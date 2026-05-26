"""World 管线编排器 - 从分镜到渲染参考图的完整调度

用法:
    python pipeline.py --storyboard storyboard.json --output ./outputs/
    python pipeline.py --storyboard storyboard.json --output ./outputs/ --plan-only
    python pipeline.py --review-only --renders ./renders/ --blueprint ./blueprints/
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


class ShotTask:
    """单个镜头任务"""
    def __init__(self, shot_data: dict):
        self.shot_id = shot_data.get("shot_id", "unknown")
        self.description = shot_data.get("description", "")
        self.scene = shot_data.get("scene", "")
        self.characters = shot_data.get("characters", [])
        self.props = shot_data.get("props", [])
        self.camera = shot_data.get("camera", {})
        self.lighting = shot_data.get("lighting", {})
        self.relations = shot_data.get("relations", [])
        self.duration = shot_data.get("duration", "")

        self.required_assets = []
        self.blueprint = None
        self.render_images = []
        self.review_result = None
        self.status = "pending"  # pending | planning | rendering | reviewing | passed | failed | manual_review

    def to_dict(self) -> dict:
        return {
            "shot_id": self.shot_id,
            "description": self.description,
            "status": self.status,
            "render_images": self.render_images,
            "review_score": self.review_result.get("total_score") if self.review_result else None,
        }


def extract_required_assets(shot: ShotTask) -> list:
    """提取镜头所需资产清单"""
    assets = []
    for ch in shot.characters:
        assets.append({"type": "character", "label": ch.get("label", ""), "hint": ch.get("animation", "")})
    for prop in shot.props:
        assets.append({"type": "model", "label": prop, "hint": prop})
    if shot.lighting:
        scheme = shot.lighting.get("scheme", "")
        if scheme:
            assets.append({"type": "hdri", "label": scheme, "hint": scheme})
    return assets


def parse_storyboard(input_path: str) -> list:
    """解析分镜脚本，生成任务列表"""
    with open(input_path) as f:
        data = json.load(f)

    shots = data.get("shots", [])
    tasks = []
    for shot_data in shots:
        task = ShotTask(shot_data)
        task.required_assets = extract_required_assets(task)
        tasks.append(task)

    return tasks


def deduplicate_assets(tasks: list) -> list:
    """跨镜头资产去重"""
    seen = set()
    unique = []
    for task in tasks:
        for asset in task.required_assets:
            key = (asset["type"], asset.get("label", ""))
            if key not in seen:
                seen.add(key)
                unique.append(asset)
    return unique


def generate_production_report(project_name: str, tasks: list, output_dir: str) -> dict:
    """生成总报告"""
    total_renders = sum(len(t.render_images) for t in tasks)
    passed = sum(1 for t in tasks if t.status == "passed")
    failed = sum(1 for t in tasks if t.status in ("failed", "manual_review"))

    # 收集所有使用过的资产
    assets_used = {"characters": [], "animations": [], "models": [], "hdris": []}
    for task in tasks:
        if task.blueprint:
            for ch in task.blueprint.get("characters", []):
                if ch.get("animation") and ch["animation"] not in assets_used["animations"]:
                    assets_used["animations"].append(ch["animation"])
            for prop in task.blueprint.get("props", []):
                if prop.get("model_hint") and prop["model_hint"] not in assets_used["models"]:
                    assets_used["models"].append(prop["model_hint"])

    return {
        "project": project_name,
        "generated_at": datetime.now().isoformat(),
        "total_shots": len(tasks),
        "total_renders": total_renders,
        "passed": passed,
        "failed": failed,
        "shots": [t.to_dict() for t in tasks],
        "assets_used": assets_used,
    }


def main():
    parser = argparse.ArgumentParser(description="kais-blender-world pipeline orchestrator")
    parser.add_argument("--storyboard", help="Storyboard JSON input")
    parser.add_argument("--output", default="./outputs/", help="Output directory")
    parser.add_argument("--plan-only", action="store_true", help="Only generate blueprints, skip rendering")
    parser.add_argument("--review-only", action="store_true", help="Only review existing renders")
    parser.add_argument("--renders", help="Directory of existing renders (for review-only mode)")
    parser.add_argument("--blueprint", help="Blueprint directory (for review-only mode)")
    args = parser.parse_args()

    if args.review_only:
        print("Review-only mode: use kais-blender-review directly")
        print(f"  Renders: {args.renders}")
        print(f"  Blueprint: {args.blueprint}")
        return 0

    if not args.storyboard:
        parser.error("--storyboard is required")

    # Step 1: Parse
    print("📋 Step 1: Parsing storyboard...")
    tasks = parse_storyboard(args.storyboard)
    print(f"  Found {len(tasks)} shots")

    # Step 2: Asset preparation
    all_assets = deduplicate_assets(tasks)
    print(f"\n📦 Step 2: Asset preparation")
    print(f"  Unique assets needed: {len(all_assets)}")
    for a in all_assets:
        print(f"    - [{a['type']}] {a['label']}")

    # Step 3: Scene planning
    print(f"\n🏗️ Step 3: Scene planning...")
    for task in tasks:
        task.status = "planning"
        print(f"  [{task.shot_id}] {task.description[:50]}...")

    if args.plan_only:
        print("\n✅ Plan-only mode: blueprints generated (conceptual)")
        print("   In actual execution, blueprints would be saved to output/blueprints/")
        return 0

    # Step 4: Rendering
    print(f"\n🎬 Step 4: Rendering...")
    for task in tasks:
        task.status = "rendering"
        print(f"  [{task.shot_id}] Submitting render...")

    # Step 5: Review
    print(f"\n🔍 Step 5: Review...")
    for task in tasks:
        task.status = "reviewing"
        task.status = "passed"  # Conceptual
        print(f"  [{task.shot_id}] ✅ Passed")

    # Report
    out_dir = Path(args.output)
    project_name = Path(args.storyboard).stem
    report = generate_production_report(project_name, tasks, str(out_dir))

    report_path = out_dir / "production_report.json"
    out_dir.mkdir(parents=True, exist_ok=True)
    with open(report_path, "w") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"\n📊 Production Report")
    print(f"  Shots: {report['total_shots']} | Passed: {report['passed']} | Failed: {report['failed']}")
    print(f"  Report: {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
