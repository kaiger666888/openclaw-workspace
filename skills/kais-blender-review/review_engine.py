"""
Blender 渲染质量审查引擎

使用 zai-vision MCP 进行视觉分析，替代内置 image tool。
支持元素完整性检查、蓝图对比、评分判定。

用法:
    from review_engine import check_elements, review_render, mcp_analyze
"""

import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


# ─── MCP 视觉分析 ───────────────────────────────────────────────

def mcp_analyze(image_path: str, prompt: str, timeout: int = 60) -> dict:
    """调用 zai-vision MCP 进行图像分析。

    Returns:
        {"success": bool, "text": str, "error": str|None}
    """
    image_path = str(Path(image_path).resolve())
    if not os.path.exists(image_path):
        return {"success": False, "text": "", "error": f"文件不存在: {image_path}"}

    cmd = [
        "mcporter", "call", "zai-vision.analyze_image",
        f"image_source={image_path}",
        f"prompt={prompt}",
        f"--timeout={timeout * 1000}",
    ]
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout + 10
        )
        if result.returncode != 0:
            return {"success": False, "text": result.stdout, "error": result.stderr.strip() or f"exit code {result.returncode}"}
        return {"success": True, "text": result.stdout.strip(), "error": None}
    except subprocess.TimeoutExpired:
        return {"success": False, "text": "", "error": f"MCP 超时 ({timeout}s)"}
    except FileNotFoundError:
        return {"success": False, "text": "", "error": "mcporter 未安装或不在 PATH 中"}


# ─── 元素完整性检查（核心功能） ─────────────────────────────────

# 严重性映射：character > furniture > prop > decoration > environment
_SEVERITY_MAP = {
    "character": "critical",
    "furniture": "warning",
    "prop": "warning",
    "decoration": "info",
    "environment": "info",
}

_BATCH_SIZE = 5  # 每批检查的元素数量，避免 MCP 超时


def _parse_batch_response(text: str, batch: list) -> list:
    """解析 MCP 返回的元素检查结果。

    Returns:
        [{"label": "...", "visible": bool|None, "detail": "..."}]
    """
    results = []
    text_lower = text.lower()

    for item in batch:
        label = item["label"]
        visible = None
        detail = ""

        # 尝试在文本中找到该元素的状态描述
        # 匹配模式："沙发": "可见" / "不可见" / "不确定"
        patterns = [
            rf'{re.escape(label)}["\s：:]*\s*(可见|存在|有|找到|明确|出现)',
            rf'(可见|存在|有|找到|明确|出现)[^\n]*{re.escape(label)}',
        ]
        not_patterns = [
            rf'{re.escape(label)}["\s：:]*\s*(不可见|不存在|没有|未找到|缺失|看不到)',
            rf'(不可见|不存在|没有|未找到|缺失|看不到)[^\n]*{re.escape(label)}',
        ]
        unsure_patterns = [
            rf'{re.escape(label)}["\s：:]*\s*(不确定|模糊|部分|无法判断|被遮挡)',
        ]

        for p in not_patterns:
            if re.search(p, text_lower):
                visible = False
                detail = "不可见"
                break
        if visible is None:
            for p in patterns:
                if re.search(p, text_lower):
                    visible = True
                    detail = "可见"
                    break
        if visible is None:
            for p in unsure_patterns:
                if re.search(p, text_lower):
                    visible = None  # unsure
                    detail = "不确定"
                    break

        # 如果精确匹配失败，尝试更宽松的匹配
        if visible is None and detail == "":
            # 检查 label 是否在文本中出现
            if label in text or label.lower() in text_lower:
                # 找到了 label 但没有明确状态，标记不确定
                visible = None
                detail = "提及但状态不明确"
            else:
                visible = False
                detail = "未在分析结果中提及"

        results.append({
            "label": label,
            "type": item.get("type", "unknown"),
            "visible": visible,
            "detail": detail,
        })

    return results


def check_elements(
    image_path: str,
    expected_elements: list,
    batch_size: int = _BATCH_SIZE,
    timeout: int = 45,
) -> dict:
    """检查渲染图中是否包含所有预期元素。

    Args:
        image_path: 渲染图路径
        expected_elements: [{"label": "沙发", "type": "furniture"}, ...]
        batch_size: 每批检查的元素数量（默认 5，避免 MCP 超时）
        timeout: 单次 MCP 调用超时秒数

    Returns:
        {
            "total": 10, "found": 8, "missing": [...],
            "score": 8.0, "max_score": 10,
            "details": [...]
        }
    """
    total = len(expected_elements)
    if total == 0:
        return {"total": 0, "found": 0, "missing": [], "score": 0, "max_score": 0, "details": []}

    all_results = []

    # 分批检查
    for i in range(0, total, batch_size):
        batch = expected_elements[i : i + batch_size]
        elements_text = "\n".join(
            f"{j+1}. {e['label']}（类型: {e.get('type', 'unknown')}）"
            for j, e in enumerate(batch)
        )

        prompt = (
            f"请仔细检查这张渲染图，确认以下元素是否在图中可见：\n\n"
            f"{elements_text}\n\n"
            f"对每个元素逐一回答，格式：\n"
            f"元素名: 可见/不可见/不确定（简述原因）\n"
            f"请务必覆盖所有 {len(batch)} 个元素。"
        )

        resp = mcp_analyze(image_path, prompt, timeout=timeout)

        if resp["success"] and resp["text"]:
            batch_results = _parse_batch_response(resp["text"], batch)
        else:
            # MCP 失败，所有元素标记为未知
            batch_results = [
                {"label": e["label"], "type": e.get("type"), "visible": None, "detail": f"MCP 失败: {resp['error']}"}
                for e in batch
            ]

        all_results.extend(batch_results)

    # 汇总
    found = 0
    missing = []
    for r in all_results:
        if r["visible"] is True:
            found += 1
        elif r["visible"] is False:
            severity = _SEVERITY_MAP.get(r["type"], "warning")
            missing.append({
                "label": r["label"],
                "type": r["type"],
                "severity": severity,
                "detail": r["detail"],
            })
        # visible is None → 不计入 missing 也不计入 found

    score = found  # 每个元素 1 分
    return {
        "total": total,
        "found": found,
        "missing": missing,
        "score": score,
        "max_score": total,
        "details": all_results,
    }


# ─── 渲染日志 Fallback ──────────────────────────────────────────

def check_from_render_log(log_path: str, expected_elements: list) -> dict:
    """Fallback：从 Blender 渲染日志中检查元素导入情况。

    当 MCP 不可用时，通过检查 stderr 中的模型导入确认来判断。
    """
    if not os.path.exists(log_path):
        return {"total": len(expected_elements), "found": 0, "missing": [{"label": e["label"], "type": e.get("type"), "severity": "critical", "detail": "无日志可用"} for e in expected_elements], "score": 0, "max_score": len(expected_elements), "details": [], "fallback": True}

    with open(log_path) as f:
        log_content = f.read()

    found = 0
    missing = []
    details = []

    for elem in expected_elements:
        label = elem["label"]
        # 在日志中搜索关键导入关键字
        keywords = [label, label.lower()]
        if elem.get("type") == "character":
            keywords.append("character")
        elif elem.get("type") == "furniture":
            keywords.append("furniture")

        matched = any(kw in log_content for kw in keywords)
        if matched:
            found += 1
            details.append({"label": label, "type": elem.get("type"), "visible": True, "detail": "日志中找到导入记录"})
        else:
            missing.append({"label": label, "type": elem.get("type"), "severity": "warning", "detail": "日志中未找到"})
            details.append({"label": label, "type": elem.get("type"), "visible": False, "detail": "日志中未找到"})

    return {
        "total": len(expected_elements),
        "found": found,
        "missing": missing,
        "score": found,
        "max_score": len(expected_elements),
        "details": details,
        "fallback": True,
    }


# ─── 完整审查（蓝图对比 + 评分） ────────────────────────────────

def review_render(
    image_path: str,
    blueprint: dict,
    shot_type: str = "wide",
    shot_id: str = "shot_001",
) -> dict:
    """审查单张渲染图，对比蓝图验证所有元素并评分。

    Args:
        image_path: 渲染图路径
        blueprint: 场景蓝图
        shot_type: 机位类型（wide/medium/closeup）
        shot_id: 镜头 ID

    Returns:
        审查报告 dict
    """
    # 1. 收集所有预期元素
    expected = []

    # characters
    for c in blueprint.get("characters", []):
        expected.append({"label": c.get("label", "未命名角色"), "type": "character"})

    # props
    for p in blueprint.get("props", []):
        expected.append({"label": p.get("label", "未命名道具"), "type": "prop"})

    # furniture (在 scene 或 scene_layout 中)
    scene = blueprint.get("scene", {})
    for f in scene.get("furniture", []):
        expected.append({"label": f.get("label", f) if isinstance(f, dict) else f, "type": "furniture"})

    # decorations
    for d in scene.get("decorations", []):
        expected.append({"label": d.get("label", d) if isinstance(d, dict) else d, "type": "decoration"})

    # 2. 元素完整性检查
    elem_result = check_elements(image_path, expected)
    elem_score = elem_result["score"] / elem_result["max_score"] if elem_result["max_score"] > 0 else 0

    # 3. 生成综合评分 prompt
    scene_desc = scene.get("description", "")
    chars = blueprint.get("characters", [])
    lighting = blueprint.get("lighting", {}).get("scheme", "unknown")
    relations = blueprint.get("relations", [])

    relations_text = ""
    if relations:
        relations_text = "\n空间关系:\n" + "\n".join(
            f"  - {r['subject']} {r['relation']} {r['object']}"
            for r in relations
        )

    chars_text = ""
    if chars:
        chars_text = "\n角色:\n" + "\n".join(
            f"  - {c.get('label')}: position={c.get('position')}, rotation={c.get('rotation')}"
            for c in chars
        )

    review_prompt = (
        f"审查这张 Blender 渲染图。\n\n"
        f"场景: {scene_desc}\n"
        f"机位: {shot_type}{chars_text}{relations_text}\n"
        f"灯光方案: {lighting}\n\n"
        f"评分（每项 0-10），严格以 JSON 格式返回：\n"
        f'{{"image_quality": N, "character_correctness": N, "composition_match": N, '
        f'"spatial_relations": N, "atmosphere_consistency": N, '
        f'"verdict": "pass|warning|fail", '
        f'"issues": [{{"severity": "critical|warning", "category": "...", "description": "...", "suggestion": "..."}}]}}'
    )

    # 4. MCP 综合评分
    mcp_resp = mcp_analyze(image_path, review_prompt, timeout=60)
    scores = {
        "image_quality": 5,
        "character_correctness": 5,
        "composition_match": 5,
        "spatial_relations": 5,
        "atmosphere_consistency": 5,
    }
    issues = []

    if mcp_resp["success"]:
        scores = _parse_scores(mcp_resp["text"], scores)
        issues = _parse_issues(mcp_resp["text"])

    # 5. 将元素缺失加入 issues
    for m in elem_result.get("missing", []):
        issues.append({
            "severity": m["severity"],
            "category": "element_check",
            "description": f"缺失元素: {m['label']}（{m['type']}）",
            "suggestion": f"在场景中添加 {m['label']}",
        })

    # 6. 计算总分（加权）
    weights = {
        "image_quality": 0.20,
        "character_correctness": 0.25,
        "composition_match": 0.20,
        "spatial_relations": 0.20,
        "atmosphere_consistency": 0.15,
    }
    total_score = sum(scores[k] * v for k, v in weights.items())

    # 元素缺失惩罚：缺失率超过 20% 额外扣分
    if elem_result["max_score"] > 0:
        miss_rate = 1 - elem_result["score"] / elem_result["max_score"]
        if miss_rate > 0.2:
            total_score -= miss_rate * 2  # 最多扣 2 分

    total_score = max(0, min(10, total_score))

    # 7. 判定
    if total_score >= 7.0:
        verdict = "pass"
    elif total_score >= 5.0:
        verdict = "warning"
    else:
        verdict = "fail"

    # 如果有 critical issue，强制降级
    if any(i["severity"] == "critical" for i in issues):
        verdict = "fail" if verdict == "pass" else verdict

    return {
        "shot_id": shot_id,
        "image": str(image_path),
        "scores": scores,
        "total_score": round(total_score, 1),
        "verdict": verdict,
        "element_check": {
            "total": elem_result["total"],
            "found": elem_result["found"],
            "missing": [m["label"] for m in elem_result.get("missing", [])],
        },
        "issues": issues,
        "fix_params": _generate_fix_params(issues, blueprint) if verdict == "fail" else None,
        "reviewed_at": datetime.now().isoformat(),
    }


def _parse_scores(text: str, defaults: dict) -> dict:
    """从 MCP 文本中解析评分 JSON。"""
    scores = dict(defaults)
    # 尝试提取 JSON 块
    json_match = re.search(r'\{[^{}]*"image_quality"[\s\S]*?\}', text)
    if json_match:
        try:
            data = json.loads(json_match.group())
            for k in scores:
                if k in data and isinstance(data[k], (int, float)):
                    scores[k] = min(10, max(0, int(data[k])))
            return scores
        except (json.JSONDecodeError, ValueError):
            pass

    # fallback：逐字段正则提取
    for k in scores:
        m = re.search(rf'"{k}"\s*:\s*(\d+)', text)
        if m:
            scores[k] = min(10, max(0, int(m.group(1))))

    return scores


def _parse_issues(text: str) -> list:
    """从 MCP 文本中解析 issues 列表。"""
    issues = []
    json_match = re.search(r'"issues"\s*:\s*(\[[\s\S]*?\])', text)
    if json_match:
        try:
            issues = json.loads(json_match.group(1))
            # 确保每个 issue 有必要字段
            for i, issue in enumerate(issues):
                issue.setdefault("severity", "warning")
                issue.setdefault("category", "general")
                issue.setdefault("description", "未知问题")
                issue.setdefault("suggestion", "")
            return issues
        except (json.JSONDecodeError, ValueError):
            pass
    return issues


def _generate_fix_params(issues: list, blueprint: dict) -> Optional[dict]:
    """从不通过的 issues 生成修复参数建议。"""
    fix = {"characters": [], "lighting": None, "hdri": None}

    for issue in issues:
        desc = issue.get("description", "").lower()
        suggestion = issue.get("suggestion", "")
        cat = issue.get("category", "")

        if cat == "element_check" and "缺失" in desc:
            # 提取缺失元素名
            label_match = re.search(r'缺失元素:\s*(.+?)[（(]', desc)
            if label_match:
                label = label_match.group(1)
                fix["characters"].append({"label": label, "action": "add"})

        if "灯光" in desc or "atmosphere" in cat:
            fix["lighting"] = suggestion or "调整灯光"

        if "hdri" in desc.lower() or "背景" in desc:
            fix["hdri"] = suggestion or "更换 HDRI"

    # 移除空字段
    fix = {k: v for k, v in fix.items() if v}

    return fix if fix else None


# ─── CLI ─────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Blender 渲染审查引擎")
    sub = parser.add_subparsers(dest="cmd")

    # check-elements
    p_check = sub.add_parser("check-elements", help="检查元素完整性")
    p_check.add_argument("image", help="渲染图路径")
    p_check.add_argument("--elements", required=True, help="JSON: 元素列表")
    p_check.add_argument("--batch-size", type=int, default=5)

    # review
    p_review = sub.add_parser("review", help="完整审查")
    p_review.add_argument("image", help="渲染图路径")
    p_review.add_argument("--blueprint", required=True, help="蓝图 JSON 路径")
    p_review.add_argument("--shot-type", default="wide")
    p_review.add_argument("--shot-id", default="shot_001")

    args = parser.parse_args()

    if args.cmd == "check-elements":
        elements = json.loads(args.elements)
        result = check_elements(args.image, elements, batch_size=args.batch_size)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.cmd == "review":
        with open(args.blueprint) as f:
            blueprint = json.load(f)
        result = review_render(args.image, blueprint, args.shot_type, args.shot_id)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    else:
        parser.print_help()
