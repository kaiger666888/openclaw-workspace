"""查询本地已下载资产，检查缺失项

用法:
    python check_assets.py --type all
    python check_assets.py --type hdri --names kloppenheim_06,studio_small_03
    python check_assets.py --server http://192.168.71.38:8080
"""

import argparse
import os
import sys
from pathlib import Path


ASSET_BASE = Path(os.environ.get("BLENDER_ASSET_DIR", "/mnt/blender/assets"))


def check_local(type_: str, names: list = None) -> dict:
    """检查本地资产是否存在"""
    ph = ASSET_BASE / "polyhaven"
    ac = ASSET_BASE / "ambientcg"
    anim = Path(os.environ.get("BLENDER_ASSET_DIR", "/mnt/blender")) / "animations"

    result = {"found": [], "missing": []}

    if type_ in ("all", "hdri"):
        hdris = ph / "hdris"
        if names:
            for n in names:
                f = hdris / f"{n}.hdr"
                (result["found"] if f.exists() else result["missing"]).append(f"hdri:{n}")
        elif hdris.exists():
            result["found"].extend(f"hdri:{f.stem}" for f in hdris.glob("*.hdr"))

    if type_ in ("all", "model"):
        models = ph / "models"
        if names:
            for n in names:
                d = models / n
                (result["found"] if d.exists() and any(d.iterdir()) else result["missing"]).append(f"model:{n}")
        elif models.exists():
            result["found"].extend(f"model:{d.name}" for d in models.iterdir() if d.is_dir())

    if type_ in ("all", "texture"):
        textures = ph / "textures"
        if textures.exists():
            result["found"].extend(f"texture:{d.name}" for d in textures.iterdir() if d.is_dir())

    if type_ in ("all", "character"):
        chars = anim / "characters"
        if names:
            for n in names:
                f = chars / f"{n}.fbx"
                (result["found"] if f.exists() else result["missing"]).append(f"character:{n}")
        elif chars.exists():
            result["found"].extend(f"character:{f.stem}" for f in chars.glob("*.fbx"))

    if type_ in ("all", "motion"):
        motions = anim / "motions"
        if names:
            for n in names:
                f = motions / f"{n}.fbx"
                (result["found"] if f.exists() else result["missing"]).append(f"motion:{n}")
        elif motions.exists():
            result["found"].extend(f"motion:{f.stem}" for f in motions.glob("*.fbx"))

    return result


def main():
    parser = argparse.ArgumentParser(description="Check local assets")
    parser.add_argument("--type", default="all", choices=["all", "hdri", "model", "texture", "character", "motion"])
    parser.add_argument("--names", help="Comma-separated names to check")
    args = parser.parse_args()

    names = [n.strip() for n in args.names.split(",")] if args.names else None
    result = check_local(args.type, names)

    print(f"Found ({len(result['found'])}):")
    for item in sorted(result["found"]):
        print(f"  ✅ {item}")

    if result["missing"]:
        print(f"\nMissing ({len(result['missing'])}):")
        for item in sorted(result["missing"]):
            print(f"  ❌ {item}")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
