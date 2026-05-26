#!/usr/bin/env python3
"""kais-skill-creator 质量评分引擎 - 5维度评分（各20分，满分100）"""

import os, re, sys, json, subprocess
from pathlib import Path

def score_trigger_precision(skill_path):
    """🎯 触发精确度 (20分)"""
    score, issues = 20, []
    content = (skill_path / "SKILL.md").read_text(errors="ignore") if (skill_path / "SKILL.md").exists() else ""
    desc_match = re.search(r'^description:\s*["\']?(.*?)["\']?\s*$', content, re.MULTILINE)
    desc = desc_match.group(1) if desc_match else ""
    if not desc or len(desc) < 10:
        score -= 5; issues.append("description 为空或过短")
    else:
        triggers = re.findall(r'["\']([^"\']+)["\']', desc)
        if len(triggers) < 2:
            score -= 3; issues.append("触发词过少")
        if not re.search(r'[\u4e00-\u9fff]', desc):
            score -= 3; issues.append("缺少中文触发词")
        kw = ["当", "when", "use when", "使用", "触发", "场景", "处理", "需要"]
        if not any(k in desc.lower() for k in kw):
            score -= 4; issues.append("缺少具体触发场景")
    return score, issues

def score_structure(skill_path):
    """📐 结构完整性 (20分)"""
    score, issues = 20, []
    if not (skill_path / "SKILL.md").exists():
        return 0, ["SKILL.md 不存在"]
    content = (skill_path / "SKILL.md").read_text(errors="ignore")
    if not content.startswith("---"):
        score -= 5; issues.append("缺少 frontmatter")
    else:
        if not re.search(r'^name:', content, re.MULTILINE): score -= 3; issues.append("缺少 name")
        if not re.search(r'^description:', content, re.MULTILINE): score -= 3; issues.append("缺少 description")
    headings = re.findall(r'^## ', content, re.MULTILINE)
    if len(headings) < 2: score -= 5; issues.append("章节过少")
    scripts_dir = skill_path / "scripts"
    if scripts_dir.exists():
        for f in scripts_dir.iterdir():
            if f.is_file() and not os.access(f, os.X_OK):
                score -= 2; issues.append(f"脚本无执行权限: {f.name}"); break
    refs = re.findall(r'(?:references|scripts|assets)/[\w./-]+', content)
    missing = [r for r in set(refs) if not (skill_path / r).exists()]
    if missing:
        score -= min(4, len(missing)*2); issues.append(f"引用不存在: {', '.join(missing[:2])}")
    return score, issues

def score_token_efficiency(skill_path):
    """⚡ Token 效率 (20分)"""
    score, issues = 20, []
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists(): return 0, ["SKILL.md 不存在"]
    lines = skill_md.read_text(errors="ignore").count('\n')
    if lines > 800: score -= 10; issues.append(f"{lines}行，严重超标")
    elif lines > 500: score -= 5; issues.append(f"{lines}行，超过建议值")
    content = skill_md.read_text(errors="ignore")
    for block in re.findall(r'```[\s\S]*?```', content):
        if block.count('\n') > 20: score -= 3; issues.append("大段代码块(>20行)"); break
    refs_dir = skill_path / "references"
    if refs_dir.exists() and lines > 300 and not list(refs_dir.iterdir()):
        score -= 3; issues.append("references/ 为空")
    return score, issues

def score_executability(skill_path):
    """🔧 可执行性 (20分)"""
    score, issues = 20, []
    scripts_dir = skill_path / "scripts"
    if not scripts_dir.exists(): return 20, []
    for script in scripts_dir.iterdir():
        if not script.is_file(): continue
        try:
            if script.suffix == '.sh':
                r = subprocess.run(['bash', '-n', str(script)], capture_output=True, timeout=5)
                if r.returncode != 0: score -= 5; issues.append(f"Shell语法错误: {script.name}")
            elif script.suffix == '.py':
                r = subprocess.run(['python3', '-m', 'py_compile', str(script)], capture_output=True, timeout=5)
                if r.returncode != 0: score -= 5; issues.append(f"Python语法错误: {script.name}")
        except: score -= 2; issues.append(f"无法检查: {script.name}")
        if script.suffix in ('.sh', '.py') and script.stat().st_size > 0:
            first = script.read_text(errors='ignore').split('\n')[0]
            if not first.startswith('#!'): score -= 2; issues.append(f"缺少shebang: {script.name}"); break
    return max(0, score), issues

def score_localization(skill_path):
    """🌏 本地化质量 (20分)"""
    score, issues = 20, []
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists(): return 0, ["SKILL.md 不存在"]
    content = skill_md.read_text(errors="ignore")
    desc_match = re.search(r'^description:\s*["\']?(.*?)["\']?\s*$', content, re.MULTILINE)
    desc = desc_match.group(1) if desc_match else ""
    if desc and not re.search(r'[\u4e00-\u9fff]', desc):
        score -= 3; issues.append("description 缺少中文")
    body = re.sub(r'```[\s\S]*?```', '', content)
    body = re.sub(r'^---.*?^---', '', body, flags=re.MULTILINE|re.DOTALL)
    zh = len(re.findall(r'[\u4e00-\u9fff]', body))
    total = len(re.findall(r'[a-zA-Z\u4e00-\u9fff]', body))
    if total > 50:
        ratio = zh / total
        if ratio < 0.2: score -= 5; issues.append(f"中文比例过低({ratio:.0%})")
    return score, issues

def main():
    if len(sys.argv) < 2:
        print("用法: score.py <skill-path>"); sys.exit(1)
    skill_path = Path(sys.argv[1]).resolve()
    if not skill_path.is_dir():
        print(f"[错误] 目录不存在: {skill_path}"); sys.exit(1)

    dims = [
        ("🎯 触发精确度", score_trigger_precision),
        ("📐 结构完整性", score_structure),
        ("⚡ Token 效率", score_token_efficiency),
        ("🔧 可执行性", score_executability),
        ("🌏 本地化质量", score_localization),
    ]
    results, total = {}, 0
    print(f"📊 质量评分: {skill_path.name}")
    print("━" * 40)
    for name, func in dims:
        s, i = func(skill_path)
        results[name] = {"score": s, "issues": i}; total += s
        emoji = "🏆" if s >= 18 else "✅" if s >= 15 else "⚠️" if s >= 12 else "❌"
        print(f"  {name}: {s}/20 {emoji}")
        for issue in i: print(f"    - {issue}")
    print("━" * 40)
    grade = "🏆 优秀" if total >= 90 else "✅ 良好" if total >= 75 else "⚠️ 及格" if total >= 60 else "❌ 不合格"
    print(f"  总分: {total}/100 {grade}")
    output = {"skill": skill_path.name, "total": total, "grade": grade,
              "dimensions": {k: v["score"] for k, v in results.items()},
              "issues": {k: v["issues"] for k, v in results.items() if v["issues"]}}
    json_path = skill_path / ".score.json"
    json_path.write_text(json.dumps(output, ensure_ascii=False, indent=2))
    print(f"\n💾 评分已保存: {json_path}")
    sys.exit(0 if total >= 60 else 1)

if __name__ == "__main__":
    main()
