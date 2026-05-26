"""
场景素材索引生成器

扫描 Poly Haven + ambientCG 下载目录，生成统一索引。
用法: python build_asset_index.py
"""
import json
from datetime import datetime, timezone
from pathlib import Path

from config import ASSET_INDEX_PATH, WORK_DIR


def _scan_scene_assets() -> dict:
    """扫描场景资产目录（Poly Haven + ambientCG）"""
    assets_dir = WORK_DIR / "assets"
    result = {"polyhaven": {}, "ambientcg": {}}

    # Poly Haven: hdris (flat files) / models (dirs) / textures (dirs)
    ph_base = assets_dir / "polyhaven"
    if ph_base.is_dir():
        for category in ["hdris", "models", "textures"]:
            cat_dir = ph_base / category
            if not cat_dir.is_dir():
                continue
            items = []
            for entry in sorted(cat_dir.iterdir()):
                if entry.is_file():
                    items.append({
                        "name": entry.stem,
                        "path": str(entry),
                        "files": 1,
                        "size": entry.stat().st_size,
                    })
                elif entry.is_dir():
                    files = list(entry.rglob("*"))
                    items.append({
                        "name": entry.name,
                        "path": str(entry),
                        "files": len([f for f in files if f.is_file()]),
                        "size": sum(f.stat().st_size for f in files if f.is_file()),
                    })
            result["polyhaven"][category] = items

    # ambientCG: textures
    ac_base = assets_dir / "ambientcg" / "textures"
    if ac_base.is_dir():
        items = []
        for d in sorted(ac_base.iterdir()):
            if not d.is_dir():
                continue
            files = list(d.rglob("*"))
            items.append({
                "name": d.name,
                "path": str(d),
                "files": len([f for f in files if f.is_file()]),
                "size": sum(f.stat().st_size for f in files if f.is_file()),
            })
        result["ambientcg"]["textures"] = items

    # 统计
    ph_total = sum(len(items) for items in result["polyhaven"].values())
    ac_total = sum(len(items) for items in result["ambientcg"].values())
    result["stats"] = {"polyhaven": ph_total, "ambientcg": ac_total, "total": ph_total + ac_total}
    return result


def build_index() -> dict:
    """构建场景素材索引"""
    scene_assets = _scan_scene_assets()
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scene_assets": scene_assets,
    }


def main():
    print("Scanning scene assets...")
    index = build_index()

    with open(ASSET_INDEX_PATH, "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)

    print(f"Index written to: {ASSET_INDEX_PATH}")
    stats = index["scene_assets"]["stats"]
    print(f"Total scene assets: {stats['total']}")
    print(f"  Poly Haven: {stats['polyhaven']}")
    print(f"  ambientCG: {stats['ambientcg']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
