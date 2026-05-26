#!/usr/bin/env bash
# kais-skill-creator 打包发布脚本
# 用法: publish.sh <skill-path> [--dry-run]

set -euo pipefail

SKILL_PATH=""
DRY_RUN=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run) DRY_RUN=true; shift ;;
    -h|--help) echo "用法: publish.sh <skill-path> [--dry-run]"; exit 0 ;;
    *) SKILL_PATH="$1"; shift ;;
  esac
done

if [[ -z "$SKILL_PATH" ]]; then echo "[错误] 请提供 skill 路径" >&2; exit 1; fi
if [[ ! -d "$SKILL_PATH" ]]; then echo "[错误] 目录不存在: $SKILL_PATH" >&2; exit 1; fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "📦 发布 skill: $(basename "$SKILL_PATH")"; echo ""

echo "🔍 步骤 1/3: 验证..."
if ! bash "$SCRIPT_DIR/validate.sh" "$SKILL_PATH"; then
  echo "❌ 验证失败"; exit 1
fi

echo ""; echo "📊 步骤 2/3: 评分..."
SCORE_OUTPUT=$(python3 "$SCRIPT_DIR/score.py" "$SKILL_PATH" 2>&1 || true)
TOTAL=$(echo "$SCORE_OUTPUT" | grep "总分:" | grep -oP '\d+' | head -1)
if [[ -z "$TOTAL" ]] || [[ "$TOTAL" -lt 75 ]]; then
  echo "❌ 评分 $TOTAL/100，低于 75 分，请先优化"; exit 1
fi
echo "✅ 评分 $TOTAL/100，达到发布标准"

echo ""; echo "🚀 步骤 3/3: 发布..."
if $DRY_RUN; then
  echo "🔍 [DRY-RUN] 跳过实际发布"; echo "✅ 验证通过"
  echo "正式发布: clawhub publish \"$SKILL_PATH\" --slug $(basename "$SKILL_PATH") --name \"Skill Name\" --version 1.0.0"
else
  if ! command -v clawhub &>/dev/null; then echo "⚠️  clawhub 未安装: npm i -g clawhub"; exit 1; fi
  if ! clawhub whoami &>/dev/null; then echo "⚠️  clawhub 未登录: clawhub login"; exit 1; fi
  SLUG=$(basename "$SKILL_PATH")
  echo "路径: $SKILL_PATH | Slug: $SLUG"; echo ""
  clawhub publish "$SKILL_PATH" --slug "$SLUG"
  echo "🎉 发布完成！"
fi
