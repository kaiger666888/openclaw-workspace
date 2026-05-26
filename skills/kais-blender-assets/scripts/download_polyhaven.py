"""批量下载 Poly Haven 资产

用法:
    python download_polyhaven.py --type hdri --names kloppenheim_06,studio_small_03
    python download_polyhaven.py --type model --names sofa_02,desk_01
    python download_polyhaven.py --type texture --names wood_floor_01
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path


# Poly Haven 下载 URL 模板
BASE_URL = "https://dl.polyhaven.org/file/ph-assets/Downloads"

# Windows 端资产根目录（通过 SMB/共享目录访问）
ASSET_BASE = Path(os.environ.get("BLENDER_ASSET_DIR", "/mnt/blender/assets"))
POLYHAVEN_BASE = ASSET_BASE / "polyhaven"


def download_hdri(name: str) -> bool:
    """下载 HDRI 文件（4K HDR 格式）"""
    url = f"{BASE_URL}/HDRI/hdr/1k/{name}.hdr"
    # Poly Haven 实际重定向到 4K
    out_dir = POLYHAVEN_BASE / "hdris"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f"{name}.hdr"

    if out_file.exists():
        print(f"  [SKIP] {name} already exists")
        return True

    try:
        result = subprocess.run(
            ["curl", "-L", "-o", str(out_file), url],
            capture_output=True, text=True, timeout=300,
        )
        if result.returncode == 0 and out_file.stat().st_size > 1024:
            print(f"  [OK] {name}.hdr ({out_file.stat().st_size // 1024}KB)")
            return True
        else:
            print(f"  [FAIL] {name}: download error or empty file")
            out_file.unlink(missing_ok=True)
            return False
    except Exception as e:
        print(f"  [ERROR] {name}: {e}")
        return False


def download_model(name: str) -> bool:
    """下载 3D 模型（2K .blend 格式，直接下载无需解压）"""
    url = f"{BASE_URL}/Models/blend/2k/{name}/{name}_2k.blend"
    out_dir = POLYHAVEN_BASE / "models" / name
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f"{name}_2k.blend"

    if out_file.exists() and out_file.stat().st_size > 1024:
        print(f"  [SKIP] {name} already exists")
        return True

    try:
        result = subprocess.run(
            ["curl", "-L", "-o", str(out_file), url],
            capture_output=True, text=True, timeout=600,
        )
        if result.returncode == 0 and out_file.stat().st_size > 1024:
            print(f"  [OK] {name}_2k.blend ({out_file.stat().st_size // 1024}KB)")
            return True
        else:
            print(f"  [FAIL] {name}: download error or empty file")
            out_file.unlink(missing_ok=True)
            return False
    except Exception as e:
        print(f"  [ERROR] {name}: {e}")
        return False


def download_texture(name: str) -> bool:
    """下载 PBR 纹理（ZIP 格式，需解压）"""
    url = f"{BASE_URL}/Textures/{name}/{name}_2K-jpg.zip"
    out_dir = POLYHAVEN_BASE / "textures"
    out_dir.mkdir(parents=True, exist_ok=True)
    zip_file = out_dir / f"{name}.zip"
    target_dir = out_dir / name

    if target_dir.exists() and any(target_dir.iterdir()):
        print(f"  [SKIP] {name} already extracted")
        return True

    try:
        subprocess.run(["curl", "-L", "-o", str(zip_file), url],
                       capture_output=True, text=True, timeout=300)
        if not zip_file.exists() or zip_file.stat().st_size < 1024:
            print(f"  [FAIL] {name}: download error")
            zip_file.unlink(missing_ok=True)
            return False

        target_dir.mkdir(parents=True, exist_ok=True)
        subprocess.run(["unzip", "-o", str(zip_file), "-d", str(target_dir)],
                       capture_output=True, text=True)
        zip_file.unlink()
        print(f"  [OK] {name} extracted to {target_dir}")
        return True
    except Exception as e:
        print(f"  [ERROR] {name}: {e}")
        return False


DOWNLOADERS = {
    "hdri": download_hdri,
    "model": download_model,
    "texture": download_texture,
}


def main():
    parser = argparse.ArgumentParser(description="Download Poly Haven assets")
    parser.add_argument("--type", required=True, choices=["hdri", "model", "texture"])
    parser.add_argument("--names", required=True, help="Comma-separated asset names")
    parser.add_argument("--server", default=os.environ.get("BLENDER_SERVER", "http://localhost:8080"),
                        help="Blender Agent Server URL for index rebuild")
    args = parser.parse_args()

    names = [n.strip() for n in args.names.split(",")]
    downloader = DOWNLOADERS[args.type]

    print(f"Downloading {len(names)} {args.type}(s)...")
    ok = sum(1 for n in names if downloader(n))
    print(f"\nDone: {ok}/{len(names)} succeeded")

    # 刷新索引
    if ok > 0 and args.server:
        import requests
        try:
            requests.get(f"{args.server}/assets/rebuild", timeout=10)
            print(f"Asset index rebuilt on {args.server}")
        except Exception:
            print("Warning: could not rebuild asset index")

    return 0 if ok == len(names) else 1


if __name__ == "__main__":
    raise SystemExit(main())
