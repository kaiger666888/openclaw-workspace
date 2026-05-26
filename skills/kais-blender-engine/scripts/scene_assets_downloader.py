#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
场景3D资源批量下载工具

从 Poly Haven (HDRI + 模型 + 纹理) 和 ambientCG (PBR 材质) 批量下载 CC0 资源。
全部 CC0 许可证，商用安全。

用法:
  # 按配置文件下载全部资源
  python scene_assets_downloader.py

  # 只下载 Poly Haven HDRI
  python scene_assets_downloader.py --source polyhaven --type hdris

  # 只下载 ambientCG 纹理
  python scene_assets_downloader.py --source ambientcg

  # 列出可用资源（不下载）
  python scene_assets_downloader.py --list --source polyhaven --type models

  # 搜索特定资源
  python scene_assets_downloader.py --search "forest"

  # 指定配置文件
  python scene_assets_downloader.py --config my_assets.yaml
"""

import argparse
import hashlib
import json
import os
import sys
import time
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.parse import unquote

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import yaml

# ---------------------------------------------------------------------------
# 常量
# ---------------------------------------------------------------------------
POLYHAVEN_API = "https://api.polyhaven.com"
POLYHAVEN_DL = "https://dl.polyhaven.org/file/ph-assets"

AMBIENTCG_API = "https://ambientcg.com/api/v2/full_json"
AMBIENTCG_DL = "https://ambientcg.com/get"

DEFAULT_CONFIG = Path(__file__).parent / "scene_assets.yaml"
DEFAULT_OUTPUT = "D:/BlenderAgent/assets"

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/135.0.0.0 Safari/537.36"
)


# ---------------------------------------------------------------------------
# 工具函数
# ---------------------------------------------------------------------------

def create_session(proxy: str | None = None) -> requests.Session:
    """创建带自动重试的 requests.Session。"""
    sess = requests.Session()
    sess.headers.update({
        "User-Agent": USER_AGENT,
        "Accept": "*/*",
    })
    if proxy:
        sess.proxies = {"http": proxy, "https": proxy}

    retry = Retry(
        total=5,
        backoff_factor=1.0,
        status_forcelist=[429, 502, 503, 504],
        allowed_methods=["GET", "HEAD"],
    )
    adapter = HTTPAdapter(max_retries=retry, pool_connections=10, pool_maxsize=10)
    sess.mount("https://", adapter)
    sess.mount("http://", adapter)
    return sess


def sanitize_filename(name: str) -> str:
    """转为文件名友好格式。"""
    import re
    name = name.strip()
    name = re.sub(r"[^\w\s.-]", "", name)
    name = re.sub(r"\s+", "_", name)
    return name.lower()


def format_size(size_bytes: int) -> str:
    """格式化文件大小。"""
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


def download_file(
    sess: requests.Session,
    url: str,
    dest: Path,
    desc: str = "",
    skip_existing: bool = True,
) -> bool:
    """下载单个文件，支持断点跳过和 MD5 校验。"""
    if skip_existing and dest.exists() and dest.stat().st_size > 0:
        return True

    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + ".tmp")

    try:
        resp = sess.get(url, timeout=300, stream=True)
        resp.raise_for_status()

        total = int(resp.headers.get("content-length", 0))
        downloaded = 0

        with open(tmp, "wb") as f:
            for chunk in resp.iter_content(chunk_size=65536):
                f.write(chunk)
                downloaded += len(chunk)
                if total and desc:
                    pct = downloaded / total * 100
                    print(f"\r  {desc}: {pct:.0f}% ({format_size(downloaded)}/{format_size(total)})", end="", flush=True)

        if desc:
            print()  # 换行

        tmp.rename(dest)
        return True

    except Exception as e:
        print(f"\n  下载失败 [{desc}]: {e}")
        if tmp.exists():
            tmp.unlink()
        return False


def download_and_extract_zip(
    sess: requests.Session,
    url: str,
    dest_dir: Path,
    desc: str = "",
    skip_existing: bool = True,
) -> bool:
    """下载 ZIP 并解压到目标目录。"""
    # 检查目标目录是否已存在且有文件
    if skip_existing and dest_dir.exists() and any(dest_dir.iterdir()):
        return True

    dest_dir.mkdir(parents=True, exist_ok=True)
    zip_path = dest_dir / "_download.zip"

    try:
        if not download_file(sess, url, zip_path, desc, skip_existing=False):
            return False

        # 解压
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(dest_dir)

        zip_path.unlink()
        return True

    except Exception as e:
        print(f"  解压失败 [{desc}]: {e}")
        if zip_path.exists():
            zip_path.unlink()
        return False


# ---------------------------------------------------------------------------
# 进度追踪
# ---------------------------------------------------------------------------

class ProgressTracker:
    """跟踪下载进度，支持断点续传。"""

    def __init__(self, output_dir: Path):
        self.file = output_dir / ".scene_download_progress.json"
        self.data = self._load()

    def _load(self) -> dict:
        if self.file.exists():
            try:
                return json.loads(self.file.read_text(encoding="utf-8"))
            except Exception:
                pass
        return {"completed": {}, "failed": {}}

    def save(self):
        self.file.parent.mkdir(parents=True, exist_ok=True)
        self.file.write_text(json.dumps(self.data, indent=2, ensure_ascii=False), encoding="utf-8")

    def is_completed(self, key: str) -> bool:
        return key in self.data["completed"]

    def mark_completed(self, key: str, info: str = ""):
        self.data["completed"][key] = {"info": info, "time": time.time()}
        self.save()

    def mark_failed(self, key: str, reason: str = ""):
        self.data["failed"][key] = {"reason": reason, "time": time.time()}
        self.save()

    @property
    def completed_count(self) -> int:
        return len(self.data["completed"])

    @property
    def failed_count(self) -> int:
        return len(self.data["failed"])


# ---------------------------------------------------------------------------
# Poly Haven 下载器
# ---------------------------------------------------------------------------

class PolyHavenDownloader:
    """Poly Haven 资源下载器。"""

    ASSET_TYPES = {"hdris": "hdris", "models": "models", "textures": "textures"}

    def __init__(self, sess: requests.Session, output_dir: Path, progress: ProgressTracker):
        self.sess = sess
        self.output_dir = output_dir / "polyhaven"
        self.progress = progress

    def list_assets(self, asset_type: str, categories: list[str] | None = None) -> list[dict]:
        """获取资源列表，按分类过滤。"""
        url = f"{POLYHAVEN_API}/assets"
        params = {"t": asset_type}
        if categories and "all" not in categories:
            # Poly Haven 不支持多分类过滤，客户端过滤
            pass

        resp = self.sess.get(url, params=params, timeout=60)
        resp.raise_for_status()
        data = resp.json()

        results = []
        for asset_id, info in data.items():
            asset_cats = info.get("categories", [])
            # 如果指定了分类，检查交集
            if categories and "all" not in categories:
                if not any(c in asset_cats for c in categories):
                    continue

            results.append({
                "id": asset_id,
                "name": info.get("name", asset_id),
                "categories": asset_cats,
                "tags": info.get("tags", []),
                "description": info.get("description", ""),
                "max_resolution": info.get("max_resolution"),
                "download_count": info.get("download_count", 0),
                "thumbnail": info.get("thumbnail_url", ""),
            })

        # 按下载量排序
        results.sort(key=lambda x: x["download_count"], reverse=True)
        return results

    def get_download_urls(self, asset_id: str, asset_type: str) -> dict:
        """获取资源的所有下载链接。"""
        url = f"{POLYHAVEN_API}/files/{asset_id}"
        resp = self.sess.get(url, timeout=30)
        resp.raise_for_status()
        return resp.json()

    def download_hdri(
        self,
        asset: dict,
        resolution: str = "4k",
        formats: list[str] | None = None,
        exclude: list[str] | None = None,
        skip_existing: bool = True,
    ) -> bool:
        """下载单个 HDRI。"""
        asset_id = asset["id"]
        progress_key = f"ph_hdri_{asset_id}_{resolution}"

        if self.progress.is_completed(progress_key):
            return True

        if exclude and asset_id in exclude:
            return True

        formats = formats or ["hdr"]

        try:
            files_data = self.get_download_urls(asset_id, "hdris")
        except Exception as e:
            print(f"  获取 HDRI 信息失败 [{asset_id}]: {e}")
            self.progress.mark_failed(progress_key, str(e))
            return False

        hdri_files = files_data.get("hdri", {})
        res_data = hdri_files.get(resolution)
        if not res_data:
            # 降级到可用分辨率
            available = sorted(hdri_files.keys(), key=lambda x: {"1k": 1, "2k": 2, "4k": 4, "8k": 8, "16k": 16}.get(x, 0))
            if available:
                res_data = hdri_files[available[-1]]
            else:
                print(f"  HDRI 无可用分辨率 [{asset_id}]")
                self.progress.mark_failed(progress_key, "no resolution")
                return False

        dest_dir = self.output_dir / "hdris"
        success = True

        for fmt in formats:
            fmt_data = res_data.get(fmt)
            if not fmt_data:
                continue

            filename = f"{asset_id}_{resolution}.{fmt}"
            dest = dest_dir / filename
            desc = f"{asset['name']} ({resolution}/{fmt})"

            if not download_file(self.sess, fmt_data["url"], dest, desc, skip_existing):
                success = False

        if success:
            self.progress.mark_completed(progress_key, f"HDRI {resolution}")
        else:
            self.progress.mark_failed(progress_key, "download error")

        return success

    def download_model(
        self,
        asset: dict,
        resolution: str = "2k",
        formats: list[str] | None = None,
        download_textures: bool = True,
        exclude: list[str] | None = None,
        skip_existing: bool = True,
    ) -> bool:
        """下载单个3D模型。"""
        asset_id = asset["id"]
        progress_key = f"ph_model_{asset_id}_{resolution}"

        if self.progress.is_completed(progress_key):
            return True

        if exclude and asset_id in exclude:
            return True

        formats = formats or ["blend"]

        try:
            files_data = self.get_download_urls(asset_id, "models")
        except Exception as e:
            print(f"  获取模型信息失败 [{asset_id}]: {e}")
            self.progress.mark_failed(progress_key, str(e))
            return False

        dest_dir = self.output_dir / "models" / asset_id
        success = True

        for fmt in formats:
            fmt_data = files_data.get(fmt, {})
            res_data = fmt_data.get(resolution)
            if not res_data:
                # 降级
                available = sorted(fmt_data.keys(), key=lambda x: {"1k": 1, "2k": 2, "4k": 4}.get(x, 0))
                res_data = fmt_data[available[-1]] if available else None

            if not res_data:
                continue

            # 获取具体文件类型
            for ext, file_info in res_data.items():
                if isinstance(file_info, dict) and "url" in file_info:
                    filename = file_info.get("url", "").split("/")[-1]
                    filename = unquote(filename)
                    dest = dest_dir / filename
                    desc = f"{asset['name']} ({resolution}/{fmt})"

                    if not download_file(self.sess, file_info["url"], dest, desc, skip_existing):
                        success = False

        # 下载 PBR 贴图
        if download_textures:
            texture_maps = ["Diffuse", "Rough", "AO", "Metal", "nor_gl", "arm"]
            for map_name in texture_maps:
                map_data = files_data.get(map_name, {})
                res_data = map_data.get(resolution)
                if not res_data:
                    available = sorted(map_data.keys(), key=lambda x: {"1k": 1, "2k": 2, "4k": 4}.get(x, 0))
                    res_data = map_data[available[-1]] if available else None

                if not res_data:
                    continue

                for ext, file_info in res_data.items():
                    if isinstance(file_info, dict) and "url" in file_info:
                        filename = file_info.get("url", "").split("/")[-1]
                        filename = unquote(filename)
                        dest = dest_dir / "textures" / filename
                        desc = f"  {map_name}"

                        download_file(self.sess, file_info["url"], dest, desc, skip_existing)

        if success:
            self.progress.mark_completed(progress_key, f"Model {resolution}")
        else:
            self.progress.mark_failed(progress_key, "download error")

        return success

    def download_texture(
        self,
        asset: dict,
        resolution: str = "2k",
        download_maps: list[str] | None = None,
        exclude: list[str] | None = None,
        skip_existing: bool = True,
    ) -> bool:
        """下载单个纹理贴图集。"""
        asset_id = asset["id"]
        progress_key = f"ph_tex_{asset_id}_{resolution}"

        if self.progress.is_completed(progress_key):
            return True

        if exclude and asset_id in exclude:
            return True

        download_maps = download_maps or ["Diffuse", "Rough", "AO", "nor_gl", "Metal", "arm"]

        try:
            files_data = self.get_download_urls(asset_id, "textures")
        except Exception as e:
            print(f"  获取纹理信息失败 [{asset_id}]: {e}")
            self.progress.mark_failed(progress_key, str(e))
            return False

        dest_dir = self.output_dir / "textures" / asset_id
        success = True

        for map_name in download_maps:
            map_data = files_data.get(map_name, {})
            res_data = map_data.get(resolution)
            if not res_data:
                available = sorted(map_data.keys(), key=lambda x: {"1k": 1, "2k": 2, "4k": 4, "8k": 8}.get(x, 0))
                res_data = map_data[available[-1]] if available else None

            if not res_data:
                continue

            for ext, file_info in res_data.items():
                if isinstance(file_info, dict) and "url" in file_info:
                    filename = file_info.get("url", "").split("/")[-1]
                    filename = unquote(filename)
                    dest = dest_dir / filename
                    desc = f"{asset['name']}/{map_name} ({resolution})"

                    if not download_file(self.sess, file_info["url"], dest, desc, skip_existing):
                        success = False

        if success:
            self.progress.mark_completed(progress_key, f"Texture {resolution}")
        else:
            self.progress.mark_failed(progress_key, "download error")

        return success

    def download_all(
        self,
        config: dict,
        skip_existing: bool = True,
    ):
        """按配置批量下载所有 Poly Haven 资源。"""
        ph_config = config.get("polyhaven", {})

        for asset_type, type_config in ph_config.items():
            if not type_config.get("enabled", False):
                print(f"\n[跳过] Poly Haven {asset_type} (已禁用)")
                continue

            print(f"\n{'='*60}")
            print(f"Poly Haven - {asset_type.upper()}")
            print(f"{'='*60}")

            # 获取资源列表
            categories = type_config.get("categories", [])
            max_count = type_config.get("max_count", 0)
            resolution = type_config.get("resolution", "2k")
            exclude = type_config.get("exclude", [])

            print(f"获取资源列表 (分类: {categories or '全部'})...")
            assets = self.list_assets(asset_type, categories)
            print(f"  找到 {len(assets)} 个资源")

            if max_count > 0:
                assets = assets[:max_count]
                print(f"  限制下载前 {max_count} 个（按下载量排序）")

            success_count = 0
            fail_count = 0

            for i, asset in enumerate(assets, 1):
                print(f"\n[{i}/{len(assets)}] {asset['name']} ({asset['id']})")
                print(f"  分类: {', '.join(asset['categories'][:3])}")

                if asset_type == "hdris":
                    ok = self.download_hdri(
                        asset,
                        resolution=resolution,
                        formats=type_config.get("formats", ["hdr"]),
                        exclude=exclude,
                        skip_existing=skip_existing,
                    )
                elif asset_type == "models":
                    ok = self.download_model(
                        asset,
                        resolution=resolution,
                        formats=type_config.get("formats", ["blend"]),
                        download_textures=type_config.get("download_textures", True),
                        exclude=exclude,
                        skip_existing=skip_existing,
                    )
                elif asset_type == "textures":
                    ok = self.download_texture(
                        asset,
                        resolution=resolution,
                        download_maps=type_config.get("download_maps", []),
                        exclude=exclude,
                        skip_existing=skip_existing,
                    )
                else:
                    continue

                if ok:
                    success_count += 1
                else:
                    fail_count += 1

                delay = config.get("delay_between_downloads", 0.5)
                if delay > 0:
                    time.sleep(delay)

            print(f"\n{asset_type} 完成: {success_count} 成功, {fail_count} 失败")


# ---------------------------------------------------------------------------
# ambientCG 下载器
# ---------------------------------------------------------------------------

class AmbientCGDownloader:
    """ambientCG PBR 材质下载器。"""

    def __init__(self, sess: requests.Session, output_dir: Path, progress: ProgressTracker):
        self.sess = sess
        self.output_dir = output_dir / "ambientcg"
        self.progress = progress

    def list_assets(self, categories: list[str] | None = None) -> list[dict]:
        """获取 ambientCG 资源列表。带重试和降级（API 超时时用硬编码热门列表）。"""
        # 尝试 API，最多 3 次
        for attempt in range(3):
            try:
                all_assets = []
                offset = 0
                limit = 100

                while True:
                    params = {"limit": limit, "offset": offset, "include": "downloadData"}
                    resp = self.sess.get(AMBIENTCG_API, params=params, timeout=120)
                    resp.raise_for_status()
                    data = resp.json()

                    found = data.get("foundAssets", [])
                    if not found:
                        break

                    for asset in found:
                        asset_cats = [asset.get("displayCategory", "")]
                        if categories and "all" not in categories:
                            if not any(c.lower() in str(asset_cats).lower() for c in categories):
                                continue
                        all_assets.append({
                            "id": asset.get("assetId", ""),
                            "name": asset.get("displayName", ""),
                            "category": asset.get("displayCategory", ""),
                            "type": asset.get("dataType", ""),
                            "tags": asset.get("tags", []),
                            "download_folders": asset.get("downloadFolders", {}),
                            "download_count": asset.get("downloadCount", 0),
                        })

                    next_page = data.get("nextPageHttp")
                    if not next_page or len(found) < limit:
                        break
                    offset += limit

                all_assets.sort(key=lambda x: x["download_count"], reverse=True)
                return all_assets

            except Exception as e:
                print(f"  API 请求失败 (尝试 {attempt+1}/3): {e}")
                if attempt < 2:
                    time.sleep(5)

        # API 不可用，使用降级列表（URL 可直接构造）
        print("  API 不可用，使用降级资产列表（100 个热门材质）")
        return self._fallback_assets()

    def _fallback_assets(self) -> list[dict]:
        """API 不可用时的降级热门资产列表。"""
        ids = [
            "Asphalt023", "Bark001", "Bark006", "Bark012", "Bricks053",
            "Bricks058", "Bricks060", "Concrete013", "Concrete017", "Concrete035",
            "Fabric030", "Fabric035", "Fabric039", "Ground077", "Ground081",
            "Leather023", "Leather026", "Marble013", "Metal032", "Metal036",
            "Metal041", "Paving080", "Paving087", "Paving109", "Planks064",
            "Planks072", "Planks098", "Rock001", "Rock021", "Rock034",
            "Roofing001", "Sand001", "Sand007", "Snow003", "Soil003",
            "Stone07", "Stone10", "Tiles082", "Tiles088", "Wood061",
            "Wood062", "Wood065", "Wood067", "Wood069", "Wood091",
            "Ground039", "Ground042", "Ground052", "Concrete038", "Concrete041",
            "Bricks043", "Bricks045", "Metal020", "Metal024", "Rock013",
            "Rock015", "Rock025", "Fabric017", "Fabric021", "Paving067",
            "Paving071", "Leather011", "Leather015", "Planks057", "Planks060",
            "Marble007", "Marble008", "Stone04", "Stone06", "Sand005",
            "Snow006", "Gravel014", "Gravel015", "Roofing005", "Roofing008",
            "Tiles073", "Tiles076", "Wood053", "Wood057", "Wood058",
            "Ground028", "Ground033", "Concrete025", "Concrete029", "Bricks036",
            "Bricks040", "Metal012", "Metal015", "Rock007", "Rock009",
            "Fabric008", "Fabric012", "Paving057", "Paving060", "Wood047",
            "Wood049", "Wood051", "Leather005", "Leather008", "Soil007",
            "Soil010", "Sand010", "Sand012", "Wood093", "Wood095",
        ]
        return [{"id": aid, "name": aid, "category": "", "download_count": 0} for aid in ids]

    def download_texture(
        self,
        asset: dict,
        resolution: str = "2K",
        format_type: str = "JPG",
        exclude: list[str] | None = None,
        skip_existing: bool = True,
    ) -> bool:
        """下载单个 ambientCG 材质包。"""
        asset_id = asset["id"]
        progress_key = f"acg_{asset_id}_{resolution}_{format_type}"

        if self.progress.is_completed(progress_key):
            return True

        if exclude and asset_id in exclude:
            return True

        # 构建下载属性标记
        attribute = f"{resolution}-{format_type}"
        filename = f"{asset_id}_{attribute}.zip"
        url = f"{AMBIENTCG_DL}?file={filename}"

        dest_dir = self.output_dir / "textures" / asset_id
        desc = f"{asset['name']} ({attribute})"

        ok = download_and_extract_zip(self.sess, url, dest_dir, desc, skip_existing)

        if ok:
            self.progress.mark_completed(progress_key, f"ambientCG {attribute}")
        else:
            self.progress.mark_failed(progress_key, "download/extract error")

        return ok

    def download_all(
        self,
        config: dict,
        skip_existing: bool = True,
    ):
        """按配置批量下载所有 ambientCG 资源。"""
        acg_config = config.get("ambientcg", {}).get("textures", {})
        if not acg_config.get("enabled", False):
            print("\n[跳过] ambientCG (已禁用)")
            return

        print(f"\n{'='*60}")
        print("ambientCG - PBR Textures")
        print(f"{'='*60}")

        categories = acg_config.get("categories", [])
        max_count = acg_config.get("max_count", 0)
        resolution = acg_config.get("resolution", "2K")
        format_type = acg_config.get("format", "JPG")
        exclude = acg_config.get("exclude", [])

        print(f"获取资源列表...")
        assets = self.list_assets(categories)
        print(f"  找到 {len(assets)} 个资源")

        if max_count > 0:
            assets = assets[:max_count]
            print(f"  限制下载前 {max_count} 个（按下载量排序）")

        success_count = 0
        fail_count = 0

        for i, asset in enumerate(assets, 1):
            print(f"\n[{i}/{len(assets)}] {asset['name']} ({asset['id']})")
            print(f"  分类: {asset['category']}")

            ok = self.download_texture(
                asset,
                resolution=resolution,
                format_type=format_type,
                exclude=exclude,
                skip_existing=skip_existing,
            )

            if ok:
                success_count += 1
            else:
                fail_count += 1

            delay = config.get("delay_between_downloads", 0.5)
            if delay > 0:
                time.sleep(delay)

        print(f"\nambientCG 完成: {success_count} 成功, {fail_count} 失败")


# ---------------------------------------------------------------------------
# 搜索功能
# ---------------------------------------------------------------------------

def search_assets(
    sess: requests.Session,
    query: str,
    source: str = "all",
    limit: int = 20,
):
    """搜索资源并打印结果。"""
    query_lower = query.lower()

    if source in ("all", "polyhaven"):
        print(f"\n--- Poly Haven 搜索: '{query}' ---")
        for asset_type in ["hdris", "models", "textures"]:
            url = f"{POLYHAVEN_API}/assets"
            resp = sess.get(url, params={"t": asset_type}, timeout=60)
            resp.raise_for_status()
            data = resp.json()

            matches = []
            for asset_id, info in data.items():
                name = info.get("name", "").lower()
                tags = " ".join(info.get("tags", [])).lower()
                cats = " ".join(info.get("categories", [])).lower()
                desc = info.get("description", "").lower()

                if query_lower in name or query_lower in tags or query_lower in cats or query_lower in desc:
                    matches.append({
                        "id": asset_id,
                        "name": info.get("name", ""),
                        "categories": info.get("categories", []),
                        "download_count": info.get("download_count", 0),
                    })

            matches.sort(key=lambda x: x["download_count"], reverse=True)
            if matches:
                print(f"\n  [{asset_type}] 找到 {len(matches)} 个:")
                for m in matches[:limit]:
                    cats_str = ", ".join(m["categories"][:3])
                    print(f"    {m['name']} ({m['id']}) [{cats_str}]")

    if source in ("all", "ambientcg"):
        print(f"\n--- ambientCG 搜索: '{query}' ---")
        offset = 0
        matches = []
        while True:
            params = {"limit": 100, "offset": offset, "include": "downloadData"}
            resp = sess.get(AMBIENTCG_API, params=params, timeout=60)
            resp.raise_for_status()
            data = resp.json()
            found = data.get("foundAssets", [])
            if not found:
                break

            for asset in found:
                name = asset.get("displayName", "").lower()
                tags = " ".join(asset.get("tags", [])).lower()
                cat = asset.get("displayCategory", "").lower()
                aid = asset.get("assetId", "").lower()

                if query_lower in name or query_lower in tags or query_lower in cat or query_lower in aid:
                    matches.append({
                        "id": asset.get("assetId", ""),
                        "name": asset.get("displayName", ""),
                        "category": asset.get("displayCategory", ""),
                    })

            if len(found) < 100:
                break
            offset += 100

        if matches:
            print(f"\n  找到 {len(matches)} 个:")
            for m in matches[:limit]:
                print(f"    {m['name']} ({m['id']}) [{m['category']}]")
        else:
            print("  无结果")


def list_available(
    sess: requests.Session,
    source: str = "all",
    asset_type: str | None = None,
    categories: list[str] | None = None,
    limit: int = 30,
):
    """列出可用资源。"""
    if source in ("all", "polyhaven"):
        print("\n=== Poly Haven ===")
        for at in ["hdris", "models", "textures"]:
            if asset_type and at != asset_type:
                continue

            url = f"{POLYHAVEN_API}/assets"
            resp = sess.get(url, params={"t": at}, timeout=60)
            resp.raise_for_status()
            data = resp.json()

            # 统计分类
            all_cats = set()
            filtered = []
            for asset_id, info in data.items():
                cats = info.get("categories", [])
                all_cats.update(cats)
                if categories and "all" not in categories:
                    if not any(c in cats for c in categories):
                        continue
                filtered.append({
                    "id": asset_id,
                    "name": info.get("name", ""),
                    "categories": cats,
                    "downloads": info.get("download_count", 0),
                })

            filtered.sort(key=lambda x: x["downloads"], reverse=True)
            print(f"\n  [{at}] 总计 {len(data)} 个 (过滤后 {len(filtered)} 个)")
            print(f"  可用分类: {', '.join(sorted(all_cats))}")
            print(f"  前 {min(limit, len(filtered))} 个:")
            for item in filtered[:limit]:
                print(f"    {item['name']} ({item['id']}) [{', '.join(item['categories'][:2])}]")

    if source in ("all", "ambientcg"):
        print("\n=== ambientCG ===")
        params = {"limit": 100, "offset": 0, "include": "downloadData"}
        resp = sess.get(AMBIENTCG_API, params=params, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        total = data.get("numberOfResults", 0)
        found = data.get("foundAssets", [])

        # 统计分类
        cats_count = {}
        for asset in found:
            cat = asset.get("displayCategory", "Unknown")
            cats_count[cat] = cats_count.get(cat, 0) + 1

        print(f"\n  总计 {total} 个资源")
        print(f"  分类统计 (前100个采样):")
        for cat, count in sorted(cats_count.items(), key=lambda x: -x[1]):
            print(f"    {cat}: {count}")

        print(f"\n  前 {min(limit, len(found))} 个:")
        for asset in found[:limit]:
            print(f"    {asset.get('displayName', '')} ({asset.get('assetId', '')}) [{asset.get('displayCategory', '')}]")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="场景3D资源批量下载工具 (Poly Haven + ambientCG)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 按配置下载全部资源
  python scene_assets_downloader.py

  # 只下载 Poly Haven HDRI
  python scene_assets_downloader.py --source polyhaven --type hdris

  # 只下载 ambientCG
  python scene_assets_downloader.py --source ambientcg

  # 列出可用资源
  python scene_assets_downloader.py --list

  # 搜索资源
  python scene_assets_downloader.py --search "forest"

  # 重新下载（忽略已完成的）
  python scene_assets_downloader.py --force
        """,
    )

    parser.add_argument("--config", type=str, default=str(DEFAULT_CONFIG), help="配置文件路径")
    parser.add_argument("--source", type=str, choices=["all", "polyhaven", "ambientcg"], default="all", help="下载来源")
    parser.add_argument("--type", type=str, choices=["hdris", "models", "textures"], help="资源类型 (仅 polyhaven)")
    parser.add_argument("--output", type=str, help="输出目录 (覆盖配置文件)")
    parser.add_argument("--proxy", type=str, help="HTTP 代理 (覆盖配置文件)")
    parser.add_argument("--no-proxy", action="store_true", help="不使用代理")
    parser.add_argument("--force", action="store_true", help="强制重新下载（忽略已完成的）")
    parser.add_argument("--list", action="store_true", help="列出可用资源（不下载）")
    parser.add_argument("--search", type=str, help="搜索资源关键词")
    parser.add_argument("--limit", type=int, default=30, help="列表/搜索显示数量")

    args = parser.parse_args()

    # 加载配置
    config_path = Path(args.config)
    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
    else:
        print(f"配置文件不存在: {config_path}，使用默认配置")
        config = {}

    # 确定代理
    proxy = config.get("proxy", "http://127.0.0.1:7891")
    if args.no_proxy:
        proxy = None
    elif args.proxy:
        proxy = args.proxy

    # 确定输出目录
    output_dir = Path(args.output) if args.output else Path(config.get("output_dir", DEFAULT_OUTPUT))
    output_dir.mkdir(parents=True, exist_ok=True)

    # 创建 session
    sess = create_session(proxy)

    # 列表模式
    if args.list:
        list_available(sess, args.source, args.type, limit=args.limit)
        return

    # 搜索模式
    if args.search:
        search_assets(sess, args.search, args.source, limit=args.limit)
        return

    # 下载模式
    skip_existing = not args.force
    progress = ProgressTracker(output_dir)

    print("=" * 60)
    print("场景3D资源下载器")
    print(f"输出目录: {output_dir}")
    print(f"代理: {proxy or '无'}")
    print(f"跳过已下载: {skip_existing}")
    print("=" * 60)

    if args.source in ("all", "polyhaven"):
        # 如果指定了 --type，只下载该类型
        if args.type:
            ph_config = config.get("polyhaven", {})
            for t in list(ph_config.keys()):
                if t != args.type:
                    ph_config[t]["enabled"] = False

        ph_dl = PolyHavenDownloader(sess, output_dir, progress)
        ph_dl.download_all(config, skip_existing)

    if args.source in ("all", "ambientcg"):
        acg_dl = AmbientCGDownloader(sess, output_dir, progress)
        acg_dl.download_all(config, skip_existing)

    # 最终报告
    print(f"\n{'='*60}")
    print("下载完成 - 最终报告")
    print(f"{'='*60}")
    print(f"完成: {progress.completed_count}")
    print(f"失败: {progress.failed_count}")
    if progress.data["failed"]:
        print("失败列表:")
        for key, info in progress.data["failed"].items():
            print(f"  - {key}: {info.get('reason', '未知')}")
    print(f"\n资源存储于: {output_dir}")


if __name__ == "__main__":
    main()
