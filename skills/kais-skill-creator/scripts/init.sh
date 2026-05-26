#!/usr/bin/env bash
# kais-skill-creator 脚手架生成器
# 用法: init.sh <skill-name> [--template simple|complex|pipeline] [--path <dir>]

set -euo pipefail

SKILL_NAME=""
TEMPLATE="simple"
OUTPUT_DIR=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --template) TEMPLATE="$2"; shift 2 ;;
    --path) OUTPUT_DIR="$2"; shift 2 ;;
    -h|--help)
      echo "用法: init.sh <skill-name> [--template simple|complex|pipeline] [--path <dir>]"
      echo "模板: simple(仅SKILL.md), complex(+scripts+references), pipeline(完整+assets)"
      exit 0 ;;
    *) SKILL_NAME="$1"; shift ;;
  esac
done

if [[ -z "$SKILL_NAME" ]]; then
  echo "[错误] 请提供 skill 名称" >&2
  exit 1
fi

# 规范化名称
SKILL_NAME=$(echo "$SKILL_NAME" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g' | sed 's/--*/-/g' | sed 's/^-//;s/-$//')

if [[ -z "$OUTPUT_DIR" ]]; then
  OUTPUT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)/skills"
fi

SKILL_DIR="$OUTPUT_DIR/$SKILL_NAME"

if [[ -d "$SKILL_DIR" ]]; then
  echo "[错误] 目录已存在: $SKILL_DIR" >&2
  exit 1
fi

echo "🔧 创建 skill: $SKILL_NAME"
echo "📁 模板: $TEMPLATE"
echo "📂 路径: $SKILL_DIR"
echo ""

mkdir -p "$SKILL_DIR"

# 标题
TITLE=$(echo "$SKILL_NAME" | sed 's/-/ /g' | sed 's/\b\(.\)/\u\1/g')

cat > "$SKILL_DIR/SKILL.md" << EOF
---
name: $SKILL_NAME
description: "[TODO: 描述 skill 功能。必须包含触发词：何时使用此 skill，具体场景、文件类型或任务。]"
---

# $TITLE

## 概述

[TODO: 1-2 句话说明此 skill 的功能]

## 触发场景

[TODO: 列出具体触发场景]
- 当用户说 "..."
- 当需要处理 ... 文件时

## 使用流程

<!-- FREEDOM:high -->
### 步骤 1：[主要操作]

[TODO: 描述核心操作步骤]

### 步骤 2：[次要操作]

[TODO: 描述辅助步骤]
<!-- /FREEDOM:high -->

## 注意事项

- [TODO: 重要提醒]
EOF

echo "  ✅ SKILL.md"

if [[ "$TEMPLATE" == "complex" || "$TEMPLATE" == "pipeline" ]]; then
  mkdir -p "$SKILL_DIR/scripts"
  mkdir -p "$SKILL_DIR/references"
  echo "  ✅ scripts/"
  echo "  ✅ references/"
fi

if [[ "$TEMPLATE" == "pipeline" ]]; then
  mkdir -p "$SKILL_DIR/assets"
  echo "  ✅ assets/"
fi

echo ""
echo "🎉 Skill '$SKILL_NAME' 创建完成！"
echo ""
echo "下一步："
echo "  1. 编辑 SKILL.md，完成 TODO 项"
echo "  2. 运行 validate.sh 检查质量"
echo "  3. 运行 score.py 获取评分"
