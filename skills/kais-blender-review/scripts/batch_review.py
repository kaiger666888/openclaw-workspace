"""批量审查渲染结果

用法:
    python batch_review.py --renders /path/to/renders/ --blueprint scene_blueprint.json
    python batch_review.py --renders /path/to/renders/ --blueprint scene_blueprint.json --output report.json
"""

import argparse
import json
import os
import sys
from pathlib import Path


def load_blueprint(path: str) -> dict:
    with open(path) as f:
        return json.load(f)


def generate_review_prompt(blueprint: dict, shot_name: str = "") -> str:
    """生成审查 prompt"""
    scene = blueprint.get("scene", {})
    chars = blueprint.get("characters", [])
    props = blueprint.get("props", [])
    lighting = blueprint.get("lighting", {}).get("scheme", "unknown")
    camera = blueprint.get("camera", {}).get("shots", [])

    lines = [
        f"审查这张 Blender 渲染图（镜头: {shot_name}）",
        "",
        "## 场景蓝图要求",
        f"描述: {scene.get('description', 'N/A')}",
        "",
        f"角色 ({len(chars)}):",
    ]
    for c in chars:
        lines.append(f"  - {c.get('label')}: position={c.get('position')}, rotation={c.get('rotation')}")

    if props:
        lines.append(f"\n道具 ({len(props)}):")
        for p in props:
            lines.append(f"  - {p.get('label')}: position={p.get('position')}")

    lines.extend([
        f"\n灯光方案: {lighting}",
        "",
        f"机位 ({len(camera)}):",
    ])
    for s in camera:
        lines.append(f"  - {s.get('name')}: {s.get('type')}")

    relations = blueprint.get("relations", [])
    if relations:
        lines.append("\n空间关系:")
        for r in relations:
            lines.append(f"  - {r['subject']} {r['relation']} {r['object']}")

    lines.extend([
        "",
        "## 评分要求（每项 0-10）",
        "1. 画面质量（分辨率、噪点、过曝/欠曝）",
        "2. 角色正确性（数量、位置、朝向、比例）",
        "3. 构图匹配（机位类型、构图、主体位置）",
        "4. 空间关系（角色间关系、角色与道具关系）",
        "5. 氛围一致性（灯光、色调与蓝图匹配）",
        "",
        "## 输出格式（JSON）",
        '{',
        '  "scores": {"image_quality": N, "character_correctness": N, "composition_match": N, "spatial_relations": N, "atmosphere_consistency": N},',
        '  "verdict": "pass|warning|fail",',
        '  "issues": [{"severity": "critical|warning", "category": "...", "description": "...", "suggestion": "..."}],',
        '  "fix_params": null 或 具体修复参数',
        '}',
    ])

    return "\n".join(lines)


def generate_review_prompt_from_description(description: str, shot_name: str = "") -> str:
    """从自然语言描述生成审查 prompt"""
    return f"""审查这张 Blender 渲染图（镜头: {shot_name}）。

分镜描述: {description}

## 评分要求（每项 0-10）
1. 画面质量（分辨率、噪点、过曝/欠曝）
2. 角色正确性（数量、位置、朝向、比例）
3. 构图匹配（机位类型、构图、主体位置）
4. 空间关系（角色间关系、角色与道具关系）
5. 氛围一致性（灯光、色调匹配）

## 输出格式（JSON）
{{
  "scores": {{"image_quality": N, "character_correctness": N, "composition_match": N, "spatial_relations": N, "atmosphere_consistency": N}},
  "verdict": "pass|warning|fail",
  "issues": [{{"severity": "critical|warning", "category": "...", "description": "...", "suggestion": "..."}}],
  "fix_params": null
}}"""


def main():
    parser = argparse.ArgumentParser(description="Batch review renders")
    parser.add_argument("--renders", required=True, help="Directory of rendered images")
    parser.add_argument("--blueprint", help="Scene blueprint JSON")
    parser.add_argument("--description", help="Shot description (if no blueprint)")
    parser.add_argument("--output", default="review_report.json", help="Output report path")
    args = parser.parse_args()

    renders_dir = Path(args.renders)
    images = sorted(renders_dir.glob("*.png")) + sorted(renders_dir.glob("*.jpg"))

    if not images:
        print(f"No images found in {args.renders}")
        return 1

    blueprint = load_blueprint(args.blueprint) if args.blueprint else None
    report = {"shots": []}

    for img in images:
        shot_name = img.stem
        if blueprint:
            prompt = generate_review_prompt(blueprint, shot_name)
        elif args.description:
            prompt = generate_review_prompt_from_description(args.description, shot_name)
        else:
            print(f"  [SKIP] {shot_name}: no blueprint or description")
            continue

        print(f"  [REVIEW] {shot_name}")
        # Prompt 供 image() 工具使用，这里只输出
        report["shots"].append({
            "shot_id": shot_name,
            "image": str(img),
            "review_prompt": prompt,
            "status": "pending_review"
        })

    out_path = Path(args.output)
    with open(out_path, "w") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"\nReport: {out_path} ({len(report['shots'])} shots pending)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
