import json
import re
import shutil
import subprocess
import threading
import time
import uuid
import zipfile
from pathlib import Path
from typing import Dict, Optional

import requests as http_requests
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from config import (
    AI_GENERATED_DIR, ANIMATION_INDEX_PATH, ANIMATIONS_DIR, ASSET_INDEX_PATH,
    BLENDER_EXE, CACHE_DIR, CHARACTERS_DIR, MOTIONS_DIR,
    OUTPUT_DIR, RENDER_TIMEOUT, TRIPO_API_KEY, TRIPOSR_DIR,
)

app = FastAPI(title="Blender Execution Engine")


# ── 异步任务存储 ──────────────────────────────────────────

_jobs: Dict[str, dict] = {}
_jobs_lock = threading.Lock()


def _run_job(job_id: str, script: str, timeout: int):
    """后台线程执行 Blender 脚本"""
    script_file = CACHE_DIR / f"job_{job_id}.py"
    script_file.write_text(script, encoding="utf-8")
    try:
        result = subprocess.run(
            [str(BLENDER_EXE), "-b", "--python", str(script_file)],
            capture_output=True, text=True, timeout=timeout,
        )
        with _jobs_lock:
            _jobs[job_id]["status"] = "completed"
            _jobs[job_id]["returncode"] = result.returncode
            _jobs[job_id]["stdout"] = result.stdout
            _jobs[job_id]["stderr"] = result.stderr
    except subprocess.TimeoutExpired:
        with _jobs_lock:
            _jobs[job_id]["status"] = "timeout"
    except Exception as e:
        with _jobs_lock:
            _jobs[job_id]["status"] = "error"
            _jobs[job_id]["error"] = str(e)
    finally:
        if script_file.exists():
            script_file.unlink()


# ── 健康检查 ──────────────────────────────────────────────

@app.get("/health")
def health_check():
    """健康检查"""
    return {"status": "ok", "blender": str(BLENDER_EXE), "output_dir": str(OUTPUT_DIR)}


# ── 环境查询 ──────────────────────────────────────────────

@app.get("/capabilities")
def capabilities():
    """查询 Blender 版本、GPU、已安装插件"""
    blender_version = ""
    try:
        r = subprocess.run(
            [str(BLENDER_EXE), "--version"],
            capture_output=True, text=True, timeout=10,
        )
        m = re.search(r"Blender (\S+)", r.stdout)
        if m:
            blender_version = m.group(1)
    except Exception:
        pass

    gpu_info = []
    gpu_script = (
        "import bpy\n"
        "try:\n"
        "    prefs = bpy.context.preferences.addons['cycles'].preferences\n"
        "    prefs.get_devices()\n"
        "    for d in prefs.devices:\n"
        '        print("GPU:" + d.name + ":" + str(d.use))\n'
        "except Exception:\n"
        "    pass\n"
    )
    script_file = CACHE_DIR / "gpu_detect.py"
    script_file.write_text(gpu_script, encoding="utf-8")
    try:
        r = subprocess.run(
            [str(BLENDER_EXE), "-b", "--python", str(script_file)],
            capture_output=True, text=True, timeout=30,
        )
        for line in r.stdout.splitlines():
            if line.startswith("GPU:"):
                parts = line.split(":", 2)
                gpu_info.append({"name": parts[1] if len(parts) > 1 else "", "enabled": parts[2] == "True" if len(parts) > 2 else False})
    except Exception:
        pass
    finally:
        if script_file.exists():
            script_file.unlink()

    addons = []
    addons_dir = _get_addons_dir()
    if addons_dir.exists():
        for item in addons_dir.iterdir():
            if item.is_dir() and (item / "__init__.py").exists():
                addons.append(item.name)

    return {
        "blender_version": blender_version,
        "gpu": gpu_info,
        "addons": sorted(addons),
        "output_dir": str(OUTPUT_DIR),
        "characters_dir": str(CHARACTERS_DIR),
        "motions_dir": str(MOTIONS_DIR),
        "cache_dir": str(CACHE_DIR),
        "assets_dir": str(WORK_DIR / "assets"),
    }


# ── 脚本执行（同步） ────────────────────────────────────

class RunScriptParams(BaseModel):
    script: str = Field(..., description="要执行的 Blender Python 脚本")
    timeout: int = Field(RENDER_TIMEOUT, description="超时秒数")


@app.post("/run/script")
async def run_script(params: RunScriptParams):
    """同步执行 Blender Python 脚本"""
    script_file = CACHE_DIR / f"job_{int(time.time())}.py"
    script_file.write_text(params.script, encoding="utf-8")
    try:
        result = subprocess.run(
            [str(BLENDER_EXE), "-b", "--python", str(script_file)],
            capture_output=True, text=True, timeout=params.timeout,
        )
        return {
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
        }
    except subprocess.TimeoutExpired:
        raise HTTPException(504, f"脚本执行超时（{params.timeout}s）")
    finally:
        if script_file.exists():
            script_file.unlink()


# ── 脚本执行（异步） ────────────────────────────────────

class AsyncScriptParams(BaseModel):
    script: str = Field(..., description="要执行的 Blender Python 脚本")
    timeout: int = Field(RENDER_TIMEOUT, description="超时秒数")


@app.post("/run/async")
async def run_async(params: AsyncScriptParams):
    """异步执行脚本，立即返回 job_id，通过 /jobs/{job_id} 轮询结果"""
    job_id = uuid.uuid4().hex[:12]
    with _jobs_lock:
        _jobs[job_id] = {"status": "running", "created_at": time.time()}
    t = threading.Thread(target=_run_job, args=(job_id, params.script, params.timeout), daemon=True)
    t.start()
    return {"job_id": job_id, "status": "running"}


@app.get("/jobs/{job_id}")
def get_job(job_id: str):
    """查询异步任务状态"""
    with _jobs_lock:
        job = _jobs.get(job_id)
    if not job:
        raise HTTPException(404, "任务不存在")
    return dict(job)


@app.delete("/jobs/{job_id}")
def delete_job(job_id: str):
    """删除已完成任务记录"""
    with _jobs_lock:
        if job_id not in _jobs:
            raise HTTPException(404, "任务不存在")
        if _jobs[job_id]["status"] == "running":
            raise HTTPException(409, "任务正在运行，无法删除")
        del _jobs[job_id]
    return {"status": "deleted"}


# ── 文件管理 ──────────────────────────────────────────────

@app.get("/outputs")
def list_outputs(prefix: str = ""):
    """列出输出目录中的文件"""
    pattern = f"{prefix}*" if prefix else "*"
    files = []
    for f in sorted(OUTPUT_DIR.glob(pattern)):
        if f.is_file():
            files.append({
                "name": f.name,
                "size": f.stat().st_size,
                "modified": f.stat().st_mtime,
            })
    return {"count": len(files), "files": files}


@app.get("/outputs/{filename}")
def get_output(filename: str):
    """下载渲染结果文件"""
    file_path = OUTPUT_DIR / filename
    if not file_path.exists():
        raise HTTPException(404, "文件不存在")
    return FileResponse(file_path)


@app.delete("/outputs/{filename}")
def delete_output(filename: str):
    """删除输出文件"""
    file_path = OUTPUT_DIR / filename
    if not file_path.exists():
        raise HTTPException(404, "文件不存在")
    file_path.unlink()
    return {"status": "deleted"}


# ── 插件管理 ──────────────────────────────────────────────

def _get_addons_dir() -> Path:
    """获取 Blender 用户 addons 目录，自动检测版本"""
    version = None
    try:
        result = subprocess.run(
            [str(BLENDER_EXE), "--version"],
            capture_output=True, text=True, timeout=10,
        )
        m = re.search(r"Blender (\d+\.\d+)", result.stdout)
        if m:
            version = m.group(1)
    except Exception:
        pass

    if not version:
        m = re.search(r"(\d+\.\d+)", str(BLENDER_EXE))
        version = m.group(1) if m else "4.0"

    bf_dir = Path.home() / "AppData" / "Roaming" / "Blender Foundation" / "Blender"
    if bf_dir.exists():
        for d in sorted(bf_dir.iterdir(), reverse=True):
            if d.is_dir() and re.match(r"\d+\.\d+", d.name):
                addons = d / "scripts" / "addons"
                if addons.exists():
                    return addons

    user_dir = bf_dir / version / "scripts" / "addons"
    user_dir.mkdir(parents=True, exist_ok=True)
    return user_dir


class AddonInstallParams(BaseModel):
    url: str = Field(..., description="插件 zip 下载地址")
    name: Optional[str] = Field(None, description="插件目录名（不填则自动推断）")
    enable: bool = Field(True, description="是否安装后自动启用")


@app.post("/install/addon")
async def install_addon(params: AddonInstallParams):
    """安装 Blender 插件（zip 直链）"""
    try:
        addons_dir = _get_addons_dir()
        download_dir = CACHE_DIR / "addon_downloads"
        download_dir.mkdir(parents=True, exist_ok=True)

        filename = params.url.split("/")[-1].split("?")[0]
        if not filename.endswith(".zip"):
            filename += ".zip"
        zip_path = download_dir / filename

        r = http_requests.get(params.url, timeout=120, stream=True)
        r.raise_for_status()
        with open(zip_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

        extract_dir = CACHE_DIR / "addon_extract"
        if extract_dir.exists():
            shutil.rmtree(extract_dir)
        extract_dir.mkdir(parents=True)

        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(extract_dir)

        extracted_items = list(extract_dir.iterdir())
        if params.name:
            addon_name = params.name
        elif len(extracted_items) == 1 and extracted_items[0].is_dir():
            addon_name = extracted_items[0].name
        else:
            addon_name = filename.replace(".zip", "")

        if (extract_dir / addon_name).is_dir():
            source_dir = extract_dir / addon_name
        elif len(extracted_items) == 1 and extracted_items[0].is_dir():
            source_dir = extracted_items[0]
        else:
            source_dir = extract_dir

        src_subdir = source_dir / "src"
        if src_subdir.is_dir():
            for item in src_subdir.iterdir():
                if item.is_dir() and (item / "__init__.py").exists():
                    addon_name = item.name
                    source_dir = item
                    break

        dest = addons_dir / addon_name
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(source_dir, dest)
        shutil.rmtree(extract_dir, ignore_errors=True)

        if params.enable:
            enable_script = (
                "import bpy\n"
                "try:\n"
                f'    bpy.ops.preferences.addon_enable(module="{addon_name}")\n'
                "    bpy.ops.wm.save_userpref()\n"
                f'    print("OK: {addon_name} enabled")\n'
                "except Exception as e:\n"
                f'    print("WARN: {addon_name} " + str(e))\n'
            )
            script_file = CACHE_DIR / f"enable_{addon_name}.py"
            script_file.write_text(enable_script, encoding="utf-8")
            subprocess.run(
                [str(BLENDER_EXE), "-b", "--python", str(script_file)],
                capture_output=True, text=True, timeout=30,
            )

        return {
            "status": "success",
            "addon_name": addon_name,
            "installed_to": str(dest),
        }

    except http_requests.RequestException as e:
        raise HTTPException(502, f"下载失败: {e}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))


class AddonEnableParams(BaseModel):
    module: str = Field(..., description="插件模块名")
    enable: bool = Field(True, description="True=启用, False=禁用")


@app.post("/addon/enable")
async def enable_addon(params: AddonEnableParams):
    """启用或禁用已安装的插件"""
    action = "addon_enable" if params.enable else "addon_disable"
    script = (
        "import bpy\n"
        "try:\n"
        f'    bpy.ops.preferences.{action}(module="{params.module}")\n'
        "    bpy.ops.wm.save_userpref()\n"
        '    print("OK")\n'
        "except Exception as e:\n"
        '    print("ERROR: " + str(e))\n'
    )
    script_file = CACHE_DIR / f"toggle_{params.module}.py"
    script_file.write_text(script, encoding="utf-8")
    try:
        result = subprocess.run(
            [str(BLENDER_EXE), "-b", "--python", str(script_file)],
            capture_output=True, text=True, timeout=30,
        )
        if "OK" in result.stdout:
            return {"status": "success", "module": params.module, "enabled": params.enable}
        raise HTTPException(500, result.stdout[-500:])
    finally:
        if script_file.exists():
            script_file.unlink()


# ── 素材索引 ──────────────────────────────────────────────

_asset_index_cache: Optional[dict] = None


def _load_asset_index() -> dict:
    """加载素材索引（带缓存）"""
    global _asset_index_cache
    if _asset_index_cache is not None:
        return _asset_index_cache
    if not ASSET_INDEX_PATH.exists():
        raise HTTPException(503, "素材索引未生成，请先调用 GET /assets/rebuild")
    with open(ASSET_INDEX_PATH, "r", encoding="utf-8") as f:
        _asset_index_cache = json.load(f)
    return _asset_index_cache


@app.get("/assets")
def query_assets(
    type: Optional[str] = Query(None, description="素材类型: skins, hair, clothes, eyes, eyebrows, eyelashes, teeth, poses, proxymeshes"),
    tags: Optional[str] = Query(None, description="逗号分隔标签过滤，如: young,female"),
    q: Optional[str] = Query(None, description="在 name/description 中搜索"),
):
    """查询可用素材"""
    index = _load_asset_index()

    # 确定要搜索的类型列表
    all_types = list(index.get("assets", {}).keys())
    if type:
        requested = [t.strip() for t in type.split(",")]
        search_types = [t for t in requested if t in all_types]
        if not search_types:
            raise HTTPException(400, f"未知类型: {type}，可用: {', '.join(all_types)}")
    else:
        search_types = all_types

    # 收集候选素材
    results = []
    for t in search_types:
        for asset in index["assets"].get(t, []):
            results.append({**asset, "type": t})

    # 标签过滤
    if tags:
        required = set(t.strip().lower() for t in tags.split(","))
        results = [a for a in results if required.issubset(set(t.lower() for t in a.get("tags", [])))]

    # 关键词搜索
    if q:
        ql = q.lower()
        results = [
            a for a in results
            if ql in a["name"].lower() or ql in a.get("description", "").lower()
        ]

    return {"total": len(results), "assets": results}


@app.get("/assets/stats")
def asset_stats():
    """素材索引统计信息（含场景素材）"""
    index = _load_asset_index()
    scene_stats = index.get("scene_assets", {}).get("stats", {})
    return {
        "generated_at": index.get("generated_at"),
        "scene": scene_stats,
    }


@app.get("/assets/rebuild")
def rebuild_asset_index():
    """重新生成素材索引（含场景素材）"""
    import subprocess as sp
    script = Path(__file__).parent / "build_asset_index.py"
    if not script.exists():
        raise HTTPException(500, f"索引生成器不存在: {script}")

    result = sp.run(
        ["python", str(script)],
        capture_output=True, text=True, timeout=60,
    )
    if result.returncode != 0:
        raise HTTPException(500, f"索引生成失败: {result.stderr[:500]}")

    # 清除缓存以强制重新加载
    global _asset_index_cache
    _asset_index_cache = None

    index = _load_asset_index()
    scene_stats = index.get("scene_assets", {}).get("stats", {})
    return {
        "status": "rebuilt",
        "scene": scene_stats,
    }


# ── 场景素材 ──────────────────────────────────────────────

@app.get("/scene-assets")
def query_scene_assets(
    source: Optional[str] = Query(None, description="来源过滤: polyhaven, ambientcg"),
    category: Optional[str] = Query(None, description="类别过滤: hdris, models, textures"),
    q: Optional[str] = Query(None, description="名称关键词搜索"),
):
    """查询场景素材（HDRI / 3D模型 / PBR纹理），客户端自由组合使用"""
    index = _load_asset_index()
    scene = index.get("scene_assets", {})

    # 确定要返回的来源
    sources = [source] if source else ["polyhaven", "ambientcg"]
    invalid = [s for s in sources if s not in scene]
    if invalid:
        valid = [s for s in scene.keys() if s != "stats"]
        raise HTTPException(400, f"未知来源: {invalid}，可用: {valid}")

    results = []
    for src in sources:
        src_data = scene.get(src, {})
        cats = [category] if category else list(src_data.keys())
        for cat in cats:
            for item in src_data.get(cat, []):
                results.append({**item, "source": src, "category": cat})

    if q:
        ql = q.lower()
        results = [r for r in results if ql in r["name"].lower()]

    return {"total": len(results), "assets": results}


# ── 动画资源管理 ──────────────────────────────────────────

_animation_index_cache: Optional[dict] = None


def _load_animation_index() -> dict:
    """加载动画索引（带缓存）"""
    global _animation_index_cache
    if _animation_index_cache is not None:
        return _animation_index_cache
    if not ANIMATION_INDEX_PATH.exists():
        raise HTTPException(503, "动画索引未生成，请先调用 GET /animations/rebuild")
    with open(ANIMATION_INDEX_PATH, "r", encoding="utf-8") as f:
        _animation_index_cache = json.load(f)
    return _animation_index_cache


@app.get("/animations")
def list_animations():
    """列出可用的 Mixamo 角色和动画"""
    index = _load_animation_index()
    return {
        "characters": index.get("characters", []),
        "motions": index.get("motions", []),
        "stats": index.get("stats", {}),
    }


@app.get("/animations/rebuild")
def rebuild_animation_index():
    """重新扫描动画目录并生成索引"""
    global _animation_index_cache
    _animation_index_cache = None

    from build_animation_index import build_index
    index = build_index()
    return {
        "status": "rebuilt",
        "stats": index.get("stats", {}),
    }


# ── AI 3D 模型生成 ──────────────────────────────────────────

from ai_generator import (
    TripoClient,
    _generate_jobs,
    _create_job,
    get_job as get_generate_job,
    get_triposr_runner,
    list_jobs as list_generate_jobs,
    run_tripo_image23d,
    run_tripo_text23d,
    run_triposr_image23d,
)


@app.get("/generate/providers")
def list_generate_providers():
    """列出可用的 AI 3D 生成服务"""
    providers = []

    # Tripo
    tripo_available = bool(TRIPO_API_KEY)
    tripo_balance = None
    if tripo_available:
        try:
            client = TripoClient()
            r = client.check_balance()
            if r.get("code") == 0:
                tripo_balance = r["data"]["balance"]
        except Exception:
            pass
    providers.append({
        "id": "tripo",
        "name": "Tripo AI",
        "available": tripo_available,
        "balance": tripo_balance,
        "capabilities": ["text_to_3d", "image_to_3d"],
        "output_types": ["base_model", "model", "pbr_model"],
    })

    # TripoSR (Local)
    triposr_runner = get_triposr_runner()
    providers.append({
        "id": "triposr",
        "name": "TripoSR (Local)",
        "available": triposr_runner.is_available(),
        "capabilities": ["image_to_3d"],
        "output_types": ["model"],
    })

    return {"providers": providers}


class Text23DParams(BaseModel):
    prompt: str = Field(..., description="文字描述要生成的3D模型")
    model_version: str = Field("v2.5-20250123", description="Tripo 模型版本")
    output_type: str = Field("model", description="输出类型: base_model, model, pbr_model")


@app.post("/generate/text23d")
async def generate_text23d(params: Text23DParams):
    """使用 Tripo API 从文字生成 3D 模型"""
    if not TRIPO_API_KEY:
        raise HTTPException(503, "Tripo API Key 未配置，请设置环境变量 TRIPO_API_KEY")

    job = _create_job("tripo", {
        "type": "text_to_3d",
        "prompt": params.prompt,
        "model_version": params.model_version,
        "output_type": params.output_type,
    })

    t = threading.Thread(
        target=run_tripo_text23d,
        args=(job["job_id"], params.prompt, params.model_version, params.output_type),
        daemon=True,
    )
    t.start()
    return {"job_id": job["job_id"], "status": "pending", "provider": "tripo"}


class Image23DParams(BaseModel):
    image_path: str = Field(..., description="输入图片的本地文件路径")
    provider: str = Field("tripo", description="生成服务: tripo 或 triposr")
    model_version: str = Field("v2.5-20250123", description="Tripo 模型版本（仅 tripo）")
    output_type: str = Field("model", description="输出类型: base_model, model, pbr_model")


@app.post("/generate/image23d")
async def generate_image23d(params: Image23DParams):
    """使用 AI 从图片生成 3D 模型（Tripo 或 TripoSR）"""
    if not Path(params.image_path).exists():
        raise HTTPException(400, f"图片文件不存在: {params.image_path}")

    if params.provider == "tripo":
        if not TRIPO_API_KEY:
            raise HTTPException(503, "Tripo API Key 未配置，请设置环境变量 TRIPO_API_KEY")
        job = _create_job("tripo", {
            "type": "image_to_3d",
            "image_path": params.image_path,
            "model_version": params.model_version,
            "output_type": params.output_type,
        })
        t = threading.Thread(
            target=run_tripo_image23d,
            args=(job["job_id"], params.image_path, params.model_version, params.output_type),
            daemon=True,
        )
    elif params.provider == "triposr":
        runner = get_triposr_runner()
        if not runner.is_available():
            raise HTTPException(503, "TripoSR 不可用，请确认 TripoSR 已安装且 torch 可用")
        job = _create_job("triposr", {
            "type": "image_to_3d",
            "image_path": params.image_path,
        })
        t = threading.Thread(
            target=run_triposr_image23d,
            args=(job["job_id"], params.image_path),
            daemon=True,
        )
    else:
        raise HTTPException(400, f"不支持的 provider: {params.provider}，可用: tripo, triposr")

    t.start()
    return {"job_id": job["job_id"], "status": "pending", "provider": params.provider}


@app.get("/generate/jobs")
def list_gen_jobs(provider: Optional[str] = Query(None, description="按 provider 过滤")):
    """列出 AI 生成任务"""
    jobs = list_generate_jobs(provider)
    return {"count": len(jobs), "jobs": jobs}


@app.get("/generate/jobs/{job_id}")
def get_gen_job(job_id: str):
    """查询 AI 生成任务状态"""
    job = get_generate_job(job_id)
    if not job:
        raise HTTPException(404, "任务不存在")
    return dict(job)


@app.get("/generate/download/{job_id}")
def download_generated_model(job_id: str):
    """下载 AI 生成的 3D 模型"""
    job = get_generate_job(job_id)
    if not job:
        raise HTTPException(404, "任务不存在")
    if job["status"] != "completed":
        raise HTTPException(409, f"任务状态: {job['status']}，尚未完成")
    model_path = Path(job["result"]["model_path"])
    if not model_path.exists():
        raise HTTPException(404, "模型文件已被删除")
    return FileResponse(model_path, filename=model_path.name)


@app.post("/generate/import/{job_id}")
async def import_generated_model(job_id: str):
    """将 AI 生成的模型导入 Blender 场景"""
    job = get_generate_job(job_id)
    if not job:
        raise HTTPException(404, "任务不存在")
    if job["status"] != "completed":
        raise HTTPException(409, f"任务状态: {job['status']}，尚未完成")

    model_path = job["result"]["model_path"]
    if not Path(model_path).exists():
        raise HTTPException(404, "模型文件已被删除")

    script = (
        "import bpy\n"
        "try:\n"
        f"    bpy.ops.import_scene.gltf(filepath=r'{model_path}')\n"
        "    imported = bpy.context.selected_objects\n"
        f"    print(f'OK: imported {{len(imported)}} objects')\n"
        "    for obj in imported:\n"
        "        obj.location = (0, 0, 0)\n"
        "except Exception as e:\n"
        "    print(f'ERROR: {{e}}')\n"
    )
    script_file = CACHE_DIR / f"import_ai_{job_id}.py"
    script_file.write_text(script, encoding="utf-8")
    try:
        result = subprocess.run(
            [str(BLENDER_EXE), "-b", "--python", str(script_file)],
            capture_output=True, text=True, timeout=60,
        )
        return {
            "returncode": result.returncode,
            "stdout": result.stdout[-1000:],
            "stderr": result.stderr[-1000:],
        }
    except subprocess.TimeoutExpired:
        raise HTTPException(504, "导入超时")
    finally:
        if script_file.exists():
            script_file.unlink()


if __name__ == "__main__":
    import uvicorn
    from config import HOST, PORT

    uvicorn.run(app, host=HOST, port=PORT)
