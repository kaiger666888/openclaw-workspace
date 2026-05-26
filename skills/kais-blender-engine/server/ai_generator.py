"""AI 3D 模型生成器 — 封装 Tripo API 和 TripoSR 本地推理"""

import asyncio
import json
import logging
import os
import sys
import time
import uuid
from pathlib import Path
from typing import Dict, Optional

import requests as http_requests

from config import AI_GENERATED_DIR, TRIPO_API_BASE_URL, TRIPO_API_KEY, TRIPO_WS_BASE_URL, TRIPOSR_DIR

logger = logging.getLogger("ai_generator")


# ── 任务存储 ──────────────────────────────────────────────

_generate_jobs: Dict[str, dict] = {}


def _create_job(provider: str, params: dict) -> dict:
    job_id = uuid.uuid4().hex[:16]
    job = {
        "job_id": job_id,
        "provider": provider,
        "status": "pending",
        "created_at": time.time(),
        "params": params,
        "result": None,
        "error": None,
    }
    _generate_jobs[job_id] = job
    return job


def get_job(job_id: str) -> Optional[dict]:
    return _generate_jobs.get(job_id)


def list_jobs(provider: Optional[str] = None) -> list:
    jobs = list(_generate_jobs.values())
    if provider:
        jobs = [j for j in jobs if j["provider"] == provider]
    return sorted(jobs, key=lambda j: j["created_at"], reverse=True)


# ── Tripo API 客户端 ──────────────────────────────────────

class TripoClient:
    """Tripo 3D AI API 客户端"""

    OUTPUT_TYPE_MAP = {
        "base_model": {"texture": False, "pbr": False},
        "model": {"texture": True, "pbr": False},
        "pbr_model": {"texture": True, "pbr": True},
    }

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or TRIPO_API_KEY
        self.base_url = TRIPO_API_BASE_URL
        self.ws_base_url = TRIPO_WS_BASE_URL

    @property
    def _headers(self) -> dict:
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

    def check_balance(self) -> dict:
        r = http_requests.get(f"{self.base_url}/user/balance", headers=self._headers, timeout=15)
        r.raise_for_status()
        return r.json()

    def text_to_3d(self, prompt: str, model_version: str = "v2.5-20250123",
                   output_type: str = "model") -> dict:
        data = {
            "type": "text_to_model",
            "model_version": model_version,
            "prompt": prompt,
            **self.OUTPUT_TYPE_MAP.get(output_type, self.OUTPUT_TYPE_MAP["model"]),
        }
        r = http_requests.post(f"{self.base_url}/task", headers=self._headers, json=data, timeout=30)
        r.raise_for_status()
        return r.json()

    def upload_image(self, image_path: str) -> dict:
        with open(image_path, "rb") as f:
            files = {"file": (Path(image_path).name, f)}
            r = http_requests.post(
                f"{self.base_url}/upload",
                headers={"Authorization": f"Bearer {self.api_key}"},
                files=files, timeout=60,
            )
        r.raise_for_status()
        return r.json()

    def image_to_3d(self, image_token: str, model_version: str = "v2.5-20250123",
                    output_type: str = "model", image_type: str = "png") -> dict:
        data = {
            "type": "image_to_model",
            "model_version": model_version,
            "file": {"type": image_type, "file_token": image_token},
            **self.OUTPUT_TYPE_MAP.get(output_type, self.OUTPUT_TYPE_MAP["model"]),
        }
        r = http_requests.post(f"{self.base_url}/task", headers=self._headers, json=data, timeout=30)
        r.raise_for_status()
        return r.json()

    def get_task(self, task_id: str) -> dict:
        r = http_requests.get(f"{self.base_url}/task/{task_id}", headers=self._headers, timeout=15)
        r.raise_for_status()
        return r.json()

    def download_model(self, task_id: str, output_type: str = "model",
                       save_dir: Optional[Path] = None) -> Path:
        result = self.get_task(task_id)
        if result["code"] != 0:
            raise RuntimeError(f"Task not ready: {result}")

        output_url = result["data"]["output"][output_type]
        file_ext = result["data"]["result"][output_type]["type"]
        save_dir = save_dir or AI_GENERATED_DIR
        local_path = save_dir / f"tripo_{task_id}_{output_type}.{file_ext}"

        with http_requests.get(output_url, headers=self._headers, stream=True, timeout=120) as r:
            r.raise_for_status()
            with open(local_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

        return local_path

    async def watch_task(self, task_id: str, job_id: str):
        """通过 WebSocket 监听任务进度，完成后下载模型"""
        import websockets

        url = f"{self.ws_base_url}/task/watch/{task_id}"
        try:
            async with websockets.connect(url, extra_headers=self._headers) as ws:
                while True:
                    message = await ws.recv()
                    data = json.loads(message)
                    result = data["data"]
                    _generate_jobs[job_id]["progress"] = f'{result["status"]}: {result["progress"]}%'
                    logger.info(f"Tripo task {task_id}: {result['status']} {result['progress']}%")

                    if data["event"] == "finalized":
                        if result["status"] != "success":
                            _generate_jobs[job_id]["status"] = "failed"
                            _generate_jobs[job_id]["error"] = f"Task failed: {result['status']}"
                            return
                        break
        except Exception as e:
            _generate_jobs[job_id]["status"] = "failed"
            _generate_jobs[job_id]["error"] = f"WebSocket error: {e}"
            return

        # 下载模型
        try:
            output_type = _generate_jobs[job_id]["params"].get("output_type", "model")
            local_path = self.download_model(task_id, output_type)
            _generate_jobs[job_id]["status"] = "completed"
            _generate_jobs[job_id]["result"] = {
                "model_path": str(local_path),
                "model_name": local_path.name,
                "task_id": task_id,
            }
            logger.info(f"Tripo task {task_id} completed, saved to {local_path}")
        except Exception as e:
            _generate_jobs[job_id]["status"] = "failed"
            _generate_jobs[job_id]["error"] = f"Download error: {e}"


# ── TripoSR 本地推理 ──────────────────────────────────────

class TripoSRRunner:
    """TripoSR 本地推理（进程内懒加载，首次调用加载模型）"""

    def __init__(self):
        self._model = None
        self._device = None

    def _ensure_model(self):
        """懒加载 TripoSR 模型"""
        if self._model is not None:
            return

        import torch
        self._device = "cuda:0" if torch.cuda.is_available() else "cpu"
        logger.info(f"Loading TripoSR model on {self._device}...")

        # 将 TripoSR 目录加入 sys.path
        tsr_path = str(TRIPOSR_DIR)
        if tsr_path not in sys.path:
            sys.path.insert(0, tsr_path)

        from tsr.system import TSR
        from tsr.utils import remove_background

        self._model = TSR.from_pretrained(
            pretrained_model_name_or_path="stabilityai/TripoSR",
            config_name="config.yaml",
            weight_name="model.ckpt",
        )
        self._model.to(self._device)
        self._model.renderer.set_chunk_size(8192)
        logger.info("TripoSR model loaded successfully")

    def is_available(self) -> bool:
        """检查 TripoSR 是否可用（目录存在 + torch 可导入）"""
        if not TRIPOSR_DIR.exists():
            return False
        try:
            import torch  # noqa: F401
            return True
        except ImportError:
            return False

    def run(self, image_path: str, output_format: str = "glb") -> Path:
        """
        执行图片 → 3D 推理，返回 GLB 文件路径。
        推理后自动释放 GPU 显存。
        """
        import torch
        import numpy as np
        from PIL import Image

        self._ensure_model()

        # 1. 去背景 + 预处理（参照官方 run.py 流程）
        logger.info(f"Processing image: {image_path}")
        from tsr.utils import remove_background, resize_foreground

        rembg_session = None
        try:
            import rembg
            rembg_session = rembg.new_session()
        except ImportError:
            logger.warning("rembg not installed, skipping background removal")

        img = Image.open(image_path).convert("RGBA")
        if rembg_session is not None:
            img = remove_background(img, rembg_session)
            rembg_session = None

        img = resize_foreground(img, 0.85)
        # 合成到灰色背景（与官方 run.py 一致）
        img_np = np.array(img).astype(np.float32) / 255.0
        img_np = img_np[:, :, :3] * img_np[:, :, 3:4] + (1 - img_np[:, :, 3:4]) * 0.5
        img = Image.fromarray((img_np * 255.0).astype(np.uint8))

        # 2. 推理
        logger.info("Running TripoSR inference...")
        with torch.no_grad():
            scene_codes = self._model([img], device=self._device)

        # 3. 提取 mesh
        meshes = self._model.extract_mesh(scene_codes, has_vertex_color=False)
        mesh = meshes[0]

        # 5. 保存 GLB
        job_id = uuid.uuid4().hex[:12]
        output_path = AI_GENERATED_DIR / f"triposr_{job_id}.{output_format}"
        mesh.export(str(output_path))
        logger.info(f"TripoSR output saved to {output_path}")

        # 6. 释放显存
        del scene_codes, meshes, mesh
        torch.cuda.empty_cache()

        return output_path


_triposr_runner = TripoSRRunner()


def get_triposr_runner() -> TripoSRRunner:
    return _triposr_runner


# ── 生成入口函数（供后台线程调用） ──────────────────────────────

def run_tripo_text23d(job_id: str, prompt: str, model_version: str, output_type: str):
    """后台线程：Tripo 文字生成3D"""
    try:
        client = TripoClient()
        _generate_jobs[job_id]["status"] = "creating"

        create_result = client.text_to_3d(prompt, model_version, output_type)
        if create_result["code"] != 0:
            _generate_jobs[job_id]["status"] = "failed"
            _generate_jobs[job_id]["error"] = create_result.get("message", "Unknown error")
            return

        tripo_task_id = create_result["data"]["task_id"]
        _generate_jobs[job_id]["tripo_task_id"] = tripo_task_id
        _generate_jobs[job_id]["status"] = "processing"

        asyncio.run(client.watch_task(tripo_task_id, job_id))
    except Exception as e:
        _generate_jobs[job_id]["status"] = "failed"
        _generate_jobs[job_id]["error"] = str(e)


def run_tripo_image23d(job_id: str, image_path: str, model_version: str, output_type: str):
    """后台线程：Tripo 图片生成3D"""
    try:
        client = TripoClient()
        _generate_jobs[job_id]["status"] = "uploading"

        upload_result = client.upload_image(image_path)
        if upload_result["code"] != 0:
            _generate_jobs[job_id]["status"] = "failed"
            _generate_jobs[job_id]["error"] = upload_result.get("message", "Upload failed")
            return

        image_token = upload_result["data"]["image_token"]
        _generate_jobs[job_id]["status"] = "creating"

        ext = Path(image_path).suffix.lstrip(".") or "png"
        create_result = client.image_to_3d(image_token, model_version, output_type, ext)
        if create_result["code"] != 0:
            _generate_jobs[job_id]["status"] = "failed"
            _generate_jobs[job_id]["error"] = create_result.get("message", "Unknown error")
            return

        tripo_task_id = create_result["data"]["task_id"]
        _generate_jobs[job_id]["tripo_task_id"] = tripo_task_id
        _generate_jobs[job_id]["status"] = "processing"

        asyncio.run(client.watch_task(tripo_task_id, job_id))
    except Exception as e:
        _generate_jobs[job_id]["status"] = "failed"
        _generate_jobs[job_id]["error"] = str(e)


def run_triposr_image23d(job_id: str, image_path: str):
    """后台线程：TripoSR 本地图片生成3D"""
    try:
        runner = get_triposr_runner()
        _generate_jobs[job_id]["status"] = "loading_model"

        output_path = runner.run(image_path)

        _generate_jobs[job_id]["status"] = "completed"
        _generate_jobs[job_id]["result"] = {
            "model_path": str(output_path),
            "model_name": output_path.name,
        }
        logger.info(f"TripoSR job {job_id} completed, saved to {output_path}")
    except Exception as e:
        _generate_jobs[job_id]["status"] = "failed"
        _generate_jobs[job_id]["error"] = str(e)
        logger.error(f"TripoSR job {job_id} failed: {e}", exc_info=True)
