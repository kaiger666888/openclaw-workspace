#!/bin/bash
# Daily Tasks Script v3
# 统一入口：先尝试 tasks/ 目录下的独立脚本，找不到则回退到 daily-tasks.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TASKS_DIR="$SCRIPT_DIR/../tasks"
LEGACY_SCRIPT="$SCRIPT_DIR/daily-tasks.sh"
TASK_NAME="${1:?用法: $0 <task-name>}"

# 1. 尝试 tasks/ 目录下的独立脚本
TASK_FILE="$TASKS_DIR/${TASK_NAME}.sh"
if [ -f "$TASK_FILE" ]; then
    echo "执行独立任务脚本: $TASK_FILE"
    chmod +x "$TASK_FILE"
    "$TASK_FILE"
    exit $?
fi

# 2. 回退到 daily-tasks.sh（有完整的 case 分支）
if [ -f "$LEGACY_SCRIPT" ]; then
    echo "回退到 legacy 脚本: $LEGACY_SCRIPT"
    chmod +x "$LEGACY_SCRIPT"
    "$LEGACY_SCRIPT" "$TASK_NAME"
    exit $?
fi

# 3. 都找不到
echo "❌ 错误: 未找到任务 '$TASK_NAME'"
echo "查找路径:"
echo "  1. $TASK_FILE (不存在)"
echo "  2. $LEGACY_SCRIPT (不存在)"
exit 1
