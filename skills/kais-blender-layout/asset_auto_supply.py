"""asset_auto_supply.py — 自动从 Poly Haven 补充缺失模型

当场景模板引用的资产在 Blender Agent Server 上不存在时，
自动搜索 Poly Haven 并下载到 Windows 端。

用法:
    from asset_auto_supply import auto_supply
    result = auto_supply(["round_table", "bookshelf"], "http://192.168.71.38:8080")
    # {"downloaded": [...], "failed": [...], "skipped": [...]}
"""

import json
import os
import subprocess
import sys
import time
import urllib.request
from typing import Dict, List, Optional

# ── Poly Haven 资产索引（缓存） ──────────────────────────────

_ph_model_cache: Optional[Dict] = None
_ph_cache_time: float = 0
_PH_CACHE_TTL: float = 3600  # 1 hour


def _fetch_polyhaven_models() -> Dict:
    """获取 Poly Haven 模型列表（带缓存）。通过 curl + proxy 调用。"""
    global _ph_model_cache, _ph_cache_time
    now = time.time()
    if _ph_model_cache and now - _ph_cache_time < _PH_CACHE_TTL:
        return _ph_model_cache

    url = "https://api.polyhaven.com/assets?type=models"
    proxy = os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy") or "http://127.0.0.1:7890"
    try:
        result = subprocess.run(
            ["curl", "-s", "--proxy", proxy, url],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode == 0 and result.stdout.strip():
            _ph_model_cache = json.loads(result.stdout)
            _ph_cache_time = now
            sys.stderr.write(f"[auto-supply] Cached {len(_ph_model_cache)} Poly Haven models\n")
            return _ph_model_cache
        sys.stderr.write(f"[auto-supply] curl returned empty (rc={result.returncode})\n")
    except Exception as e:
        sys.stderr.write(f"[auto-supply] Failed to fetch Poly Haven models: {e}\n")
    return _ph_model_cache or {}


# ── 关键词 → Poly Haven 模型 ID 映射 ─────────────────────────

KEYWORD_TO_PH = {
    # Tables
    "round_table":         "coffee_table_round_01",
    "coffee_table":        "CoffeeTable_01",
    "round_coffee_table":  "coffee_table_round_01",
    "tea_table":           "chinese_tea_table",
    "dining_table":        "WoodenTable_01",
    "wooden_table":        "WoodenTable_01",
    "side_table":          "ClassicNightstand_01",
    "console_table":       "chinese_console_table",
    # Chairs
    "dining_chair":        "dining_chair_02",
    "chair":               "WoodenChair_01",
    "wooden_chair":        "WoodenChair_01",
    "arm_chair":           "ArmChair_01",
    "armchair":            "ArmChair_01",
    "sofa":                "Sofa_01",
    "stool":               "chinese_stool",
    # Shelves / Storage
    "bookshelf":           "painted_wooden_shelves",
    "shelf":               "Shelf_01",
    "cabinet":             "GothicCabinet_01",
    "wooden_shelf":        "painted_wooden_shelves",
    # Decoration
    "picture_frame":       "hanging_picture_frame_01",
    "painting":            "hanging_picture_frame_01",
    "wall_art":            "hanging_picture_frame_01",
    "decorative_frame":    "fancy_picture_frame_01",
    "mirror":              "ornate_mirror_01",
    # Plants
    "potted_plant":        "potted_plant_01",
    "plant":               "potted_plant_01",
    "fern":                "fern_02",
    # Props
    "television":          "Television_01",
    "tv":                  "Television_01",
    "lantern":             "Lantern_01",
    "coffee_cart":         "CoffeeCart_01",
    "books":               "decorative_book_set_01",
    # Known unavailable on Poly Haven
    "curtain":             None,
    "curtains":            None,
    "rug":                 None,
    "carpet":              None,
    "lamp":                None,
    "ceiling_light":       None,
}


def _resolve_model_id(keyword: str, ph_models: Dict) -> Optional[str]:
    """将关键词解析为 Poly Haven 模型 ID。

    优先级:
    1. 预定义映射
    2. 精确名称匹配（ID 或 display name）
    3. 模糊匹配（关键词在 ID/name 中）
    """
    kw = keyword.strip().lower().replace(" ", "_")

    # 1. 预定义映射
    if kw in KEYWORD_TO_PH:
        ph_id = KEYWORD_TO_PH[kw]
        if ph_id is None:
            return None  # known unavailable
        if ph_id in ph_models:
            return ph_id

    # 2. 精确 ID 匹配
    if kw in ph_models:
        return kw

    # 3. 名称匹配
    for ph_id, info in ph_models.items():
        name = info.get("name", "").lower().replace(" ", "_")
        if name == kw or ph_id.lower() == kw:
            return ph_id

    # 4. 模糊匹配：关键词包含在 ID 或 name 中
    parts = kw.replace("_", " ").split()
    for ph_id, info in ph_models.items():
        ph_name = info.get("name", "").lower()
        ph_id_lower = ph_id.lower()
        if all(p in ph_id_lower or p in ph_name for p in parts if len(p) > 2):
            return ph_id

    return None


def _download_via_server(server_url: str, model_id: str) -> bool:
    """通过 Blender Agent Server 在 Windows 端下载 Poly Haven 模型。

    发送 Python 脚本到 Server 执行下载。
    直接下载 .blend 文件（Poly Haven 新格式，无需 zip）。
    """
    # Poly Haven 2K blend download URL (verified working)
    download_url = f"https://dl.polyhaven.org/file/ph-assets/Models/blend/2k/{model_id}/{model_id}_2k.blend"

    # Build script without f-strings to avoid escape issues
    script = (
        'import urllib.request, os, sys\n'
        'model_id = ' + repr(model_id) + '\n'
        'url = ' + repr(download_url) + '\n'
        'target = os.path.join("D:", os.sep, "BlenderAgent", "assets", "polyhaven", "models", model_id)\n'
        'blend_path = os.path.join(target, model_id + "_2k.blend")\n'
        'try:\n'
        '    os.makedirs(target, exist_ok=True)\n'
        '    sys.stderr.write("[download] Starting: " + model_id + "\\n")\n'
        '    opener = urllib.request.build_opener(urllib.request.HTTPRedirectHandler)\n'
        '    urllib.request.install_opener(opener)\n'
        '    urllib.request.urlretrieve(url, blend_path)\n'
        '    size = os.path.getsize(blend_path)\n'
        '    if size < 1024:\n'
        '        sys.stderr.write("[download] FAIL " + model_id + ": too small\\n")\n'
        '        if os.path.exists(blend_path):\n'
        '            os.unlink(blend_path)\n'
        '        print("FAIL")\n'
        '    else:\n'
        '        sys.stderr.write("[download] OK " + model_id + ": " + str(size // 1024) + "KB\\n")\n'
        '        print("OK")\n'
        'except Exception as e:\n'
        '    sys.stderr.write("[download] ERROR " + model_id + ": " + str(e) + "\\n")\n'
        '    if os.path.exists(blend_path):\n'
        '        os.unlink(blend_path)\n'
        '    print("FAIL")\n'
    )

    api_url = server_url.rstrip("/") + "/run/script"
    payload = json.dumps({"script": script, "timeout": 300}).encode()
    req = urllib.request.Request(
        api_url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=360) as resp:
            result = json.loads(resp.read().decode())
        output = result.get("stdout", "").strip()
        stderr = result.get("stderr", "")
        if stderr:
            sys.stderr.write(f"[auto-supply] Server stderr for {model_id}: {stderr[-300:]}\n")
        return "OK" in output
    except Exception as e:
        sys.stderr.write(f"[auto-supply] Server request failed for {model_id}: {e}\n")
        return False


def _rebuild_asset_index(server_url: str) -> bool:
    """通知 Blender Agent Server 重建资产索引。"""
    url = server_url.rstrip("/") + "/assets/rebuild"
    try:
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.status == 200
    except Exception as e:
        sys.stderr.write(f"[auto-supply] Failed to rebuild index: {e}\n")
        return False


def auto_supply(
    missing_items: List[str],
    server_url: str = "http://192.168.71.38:8080",
) -> Dict[str, List[str]]:
    """自动从 Poly Haven 搜索并下载缺失模型。

    Args:
        missing_items: 缺失的资产名称列表（模板中的 asset 字段）
        server_url: Blender Agent Server 地址

    Returns:
        {"downloaded": [成功下载的模型ID], "failed": [失败的名称], "skipped": [不可用的名称]}
    """
    result = {"downloaded": [], "failed": [], "skipped": []}

    if not missing_items:
        return result

    sys.stderr.write(f"[auto-supply] Resolving {len(missing_items)} missing items\n")

    # 获取 Poly Haven 模型列表
    ph_models = _fetch_polyhaven_models()
    if not ph_models:
        sys.stderr.write("[auto-supply] Cannot fetch Poly Haven index, aborting\n")
        result["failed"] = list(missing_items)
        return result

    # 解析每个缺失项
    to_download = []
    for item in missing_items:
        model_id = _resolve_model_id(item, ph_models)
        if model_id is None:
            sys.stderr.write(f"[auto-supply] SKIP (unavailable): {item}\n")
            result["skipped"].append(item)
        else:
            sys.stderr.write(f"[auto-supply] Resolved: {item} → {model_id}\n")
            to_download.append((item, model_id))

    # 下载
    downloaded_any = False
    for item, model_id in to_download:
        sys.stderr.write(f"[auto-supply] Downloading {model_id}...\n")
        ok = _download_via_server(server_url, model_id)
        if ok:
            result["downloaded"].append(model_id)
            downloaded_any = True
        else:
            result["failed"].append(item)

    # 重建索引
    if downloaded_any:
        sys.stderr.write("[auto-supply] Rebuilding asset index...\n")
        _rebuild_asset_index(server_url)
        time.sleep(2)  # 等待索引重建完成

    summary = (f"auto-supply done: "
               f"{len(result['downloaded'])} downloaded, "
               f"{len(result['failed'])} failed, "
               f"{len(result['skipped'])} skipped")
    sys.stderr.write(f"[auto-supply] {summary}\n")

    return result


# ── 测试 ──────────────────────────────────────────────────────

if __name__ == "__main__":
    ph = _fetch_polyhaven_models()
    test_items = ["round_table", "bookshelf", "dining_chair", "picture_frame", "curtain"]
    for item in test_items:
        model_id = _resolve_model_id(item, ph)
        status = "UNAVAILABLE" if model_id is None else f"→ {model_id}"
        print(f"  {item}: {status}")
