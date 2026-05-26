"""
自动审查：加载模板/蓝图 → 提取元素 → MCP 分析 → 生成报告

集成到 kais-blender-layout 的 build_scene 流程中。
"""

import json
import os
import sys
from pathlib import Path
from typing import Optional

# 同目录导入
sys.path.insert(0, str(Path(__file__).parent))
from review_engine import check_elements, review_render, mcp_analyze, check_from_render_log


def _find_template(template_name: str, search_dirs: list = None) -> Optional[str]:
    """在常见路径中搜索场景模板 JSON。"""
    if search_dirs is None:
        search_dirs = [
            Path(__file__).parent / "templates",
            Path.home() / ".openclaw" / "workspace" / "skills" / "kais-blender-layout" / "templates",
            Path("/tmp/blender_e2e"),
        ]

    for d in search_dirs:
        d = Path(d)
        if not d.exists():
            continue
        # 精确匹配
        for ext in [".json", ""]:
            candidate = d / f"{template_name}{ext}"
            if candidate.exists():
                return str(candidate)
        # 模糊匹配
        for f in d.glob("*.json"):
            if template_name.lower() in f.stem.lower():
                return str(f)

    return None


def auto_review_and_report(
    image_path: str,
    template_name: str,
    expected_characters: int = 2,
    render_log_path: Optional[str] = None,
) -> dict:
    """自动审查：加载模板 → 提取元素列表 → MCP 分析 → 生成报告。

    Args:
        image_path: 渲染图路径
        template_name: 场景模板名称（会在 templates 目录中搜索）
        expected_characters: 预期角色数量（用于验证）
        render_log_path: 渲染日志路径（MCP fallback 时使用）

    Returns:
        审查报告 dict
    """
    # 1. 加载模板
    template_path = _find_template(template_name)
    if template_path:
        with open(template_path) as f:
            template = json.load(f)
    else:
        template = {}

    # 2. 提取所有元素
    expected = []

    # 从模板中提取
    for c in template.get("characters", []):
        expected.append({"label": c.get("label", "角色"), "type": "character"})

    for p in template.get("props", []):
        expected.append({"label": p.get("label", "道具"), "type": "prop"})

    scene = template.get("scene", {})
    for f_item in scene.get("furniture", []):
        label = f_item.get("label", f_item) if isinstance(f_item, dict) else f_item
        expected.append({"label": str(label), "type": "furniture"})

    for d_item in scene.get("decorations", []):
        label = d_item.get("label", d_item) if isinstance(d_item, dict) else d_item
        expected.append({"label": str(label), "type": "decoration"})

    # 3. 如果没有模板数据，用默认元素
    if not expected:
        expected.append({"label": "角色", "type": "character"})
        if expected_characters > 1:
            for i in range(2, expected_characters + 1):
                expected.append({"label": f"角色{i}", "type": "character"})
        expected.extend([
            {"label": "地板", "type": "environment"},
            {"label": "墙壁", "type": "environment"},
        ])

    # 4. MCP 元素检查
    try:
        elem_result = check_elements(image_path, expected)
    except Exception as e:
        # MCP 完全失败，尝试日志 fallback
        if render_log_path and os.path.exists(render_log_path):
            elem_result = check_from_render_log(render_log_path, expected)
        else:
            elem_result = {
                "total": len(expected),
                "found": 0,
                "missing": [{"label": e["label"], "type": e.get("type"), "severity": "critical", "detail": str(e)} for e in expected],
                "score": 0,
                "max_score": len(expected),
                "details": [],
                "error": str(e),
            }

    # 5. 构建报告
    total = elem_result["total"]
    found = elem_result["found"]
    missing = elem_result.get("missing", [])

    # 评分
    if total > 0:
        completeness = found / total
    else:
        completeness = 0

    # 角色数量检查
    char_expected = sum(1 for e in expected if e["type"] == "character")
    char_found = sum(1 for d in elem_result.get("details", []) if d.get("type") == "character" and d.get("visible") is True)

    issues = []
    if char_found < char_expected:
        issues.append({
            "severity": "critical",
            "category": "character_count",
            "description": f"角色数量不足: 找到 {char_found}/{char_expected}",
            "suggestion": f"添加缺失的 {char_expected - char_found} 个角色",
        })

    for m in missing:
        issues.append({
            "severity": m.get("severity", "warning"),
            "category": "missing_element",
            "description": f"缺失: {m['label']}（{m.get('type', 'unknown')}）",
            "suggestion": f"在场景中添加 {m['label']}",
        })

    # 判定
    critical_count = sum(1 for i in issues if i["severity"] == "critical")
    if critical_count > 0 or completeness < 0.6:
        verdict = "fail"
    elif completeness < 0.8 or len(issues) > 0:
        verdict = "warning"
    else:
        verdict = "pass"

    return {
        "image": str(image_path),
        "template": template_name,
        "template_path": template_path,
        "element_check": {
            "total": total,
            "found": found,
            "missing": [m["label"] for m in missing],
            "completeness": round(completeness * 100, 1),
        },
        "character_check": {
            "expected": char_expected,
            "found": char_found,
            "ok": char_found >= char_expected,
        },
        "verdict": verdict,
        "issues": issues,
        "details": elem_result.get("details", []),
    }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="自动审查渲染图")
    parser.add_argument("image", help="渲染图路径")
    parser.add_argument("--template", required=True, help="场景模板名称")
    parser.add_argument("--characters", type=int, default=2, help="预期角色数")
    parser.add_argument("--render-log", help="渲染日志路径（fallback）")
    parser.add_argument("--output", "-o", help="输出报告路径")
    args = parser.parse_args()

    report = auto_review_and_report(
        args.image, args.template,
        expected_characters=args.characters,
        render_log_path=args.render_log,
    )

    print(json.dumps(report, ensure_ascii=False, indent=2))

    if args.output:
        Path(args.output).write_text(json.dumps(report, ensure_ascii=False, indent=2))
        print(f"\nReport saved to {args.output}")
