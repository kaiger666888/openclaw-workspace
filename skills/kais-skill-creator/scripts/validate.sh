#!/usr/bin/env bash
# kais-skill-creator 静态验证脚本
# 用法: validate.sh <skill-path>

set -euo pipefail

SKILL_PATH="${1:-}"

if [[ -z "$SKILL_PATH" ]]; then
  echo "[错误] 请提供 skill 路径" >&2
  exit 1
fi

if [[ ! -d "$SKILL_PATH" ]]; then
  echo "[错误] 目录不存在: $SKILL_PATH" >&2
  exit 1
fi

echo "🔍 验证 skill: $SKILL_PATH"
echo ""

ERRORS=0
WARNINGS=0

# 检查 SKILL.md
if [[ ! -f "$SKILL_PATH/SKILL.md" ]]; then
  echo "❌ [致命] SKILL.md 不存在"
  exit 1
fi
echo "✅ SKILL.md 存在"

# 检查 frontmatter
if ! head -1 "$SKILL_PATH/SKILL.md" | grep -q "^---"; then
  echo "❌ SKILL.md 缺少 YAML frontmatter"
  ((ERRORS++))
else
  echo "✅ frontmatter 格式正确"
fi

# 检查 name
if ! grep -q "^name:" "$SKILL_PATH/SKILL.md"; then
  echo "⚠️  缺少 name 字段"
  ((WARNINGS++))
else
  echo "✅ name 字段存在"
fi

# 检查 description
if ! grep -q "^description:" "$SKILL_PATH/SKILL.md"; then
  echo "⚠️  缺少 description 字段"
  ((WARNINGS++))
else
  echo "✅ description 字段存在"
fi

# 行数
LINES=$(wc -l < "$SKILL_PATH/SKILL.md")
if [[ "$LINES" -gt 800 ]]; then
  echo "❌ SKILL.md $LINES 行，严重超标（建议 < 500）"
  ((ERRORS++))
elif [[ "$LINES" -gt 500 ]]; then
  echo "⚠️  SKILL.md $LINES 行，超过建议值"
  ((WARNINGS++))
else
  echo "✅ SKILL.md $LINES 行"
fi

# 检查 scripts
if [[ -d "$SKILL_PATH/scripts" ]]; then
  for script in "$SKILL_PATH/scripts/"*; do
    [[ -f "$script" ]] || continue
    if [[ ! -x "$script" ]]; then
      echo "⚠️  脚本缺少执行权限: $(basename "$script")"
      ((WARNINGS++))
    fi
    case "$script" in
      *.sh) bash -n "$script" 2>/dev/null || { echo "❌ Shell 语法错误: $(basename "$script")"; ((ERRORS++)); } ;;
      *.py) python3 -m py_compile "$script" 2>/dev/null || { echo "❌ Python 语法错误: $(basename "$script")"; ((ERRORS++)); } ;;
    esac
  done
  echo "✅ scripts/ 检查完成"
fi

# 引用路径
if grep -q "references/" "$SKILL_PATH/SKILL.md" && [[ -d "$SKILL_PATH/references" ]]; then
  while IFS= read -r ref; do
    [[ -n "$ref" ]] && [[ ! -f "$SKILL_PATH/$ref" ]] && { echo "⚠️  引用不存在: $ref"; ((WARNINGS++)); }
  done < <(grep -oP 'references/[\w./-]+' "$SKILL_PATH/SKILL.md" 2>/dev/null | sort -u)
fi

# 敏感信息
if grep -qiE '(password|secret|token|api_key|private_key)\s*[:=]' "$SKILL_PATH/SKILL.md" 2>/dev/null; then
  echo "⚠️  检测到可能的敏感信息"
  ((WARNINGS++))
else
  echo "✅ 未检测到敏感信息"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━"
if [[ $ERRORS -gt 0 ]]; then
  echo "❌ 验证失败: $ERRORS 错误, $WARNINGS 警告"
  exit 1
elif [[ $WARNINGS -gt 0 ]]; then
  echo "⚠️  通过（$WARNINGS 警告）"
else
  echo "✅ 全部通过"
fi

# 运行评分
echo ""
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python3 "$SCRIPT_DIR/score.py" "$SKILL_PATH"
