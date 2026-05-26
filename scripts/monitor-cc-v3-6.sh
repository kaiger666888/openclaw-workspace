#!/bin/bash

SESSION_NAME="oc-gold-team"
LOG_FILE="/tmp/oc-logs/${SESSION_NAME}.log"

# Check if tmux session exists and is running
if ! tmux has-session -t "$SESSION_NAME" 2>/dev/null; then
    echo "⚠️  Tmux session $SESSION_NAME not running"
    exit 0
fi

# Check current command in the session
CURRENT_CMD=$(tmux list-panes -t "$SESSION_NAME" -F '#{pane_current_command}' 2>/dev/null)

if [ "$CURRENT_CMD" != "claude" ]; then
    echo "✅ 已结束：$CURRENT_CMD"
    tail -10 "$LOG_FILE"
    exit 0
fi

# Claude is running, capture recent output
OUTPUT=$(tmux capture-pane -t "$SESSION_NAME" -p -S -20 | tail -15)

if [ -z "$OUTPUT" ]; then
    echo "🔄 Claude Code 运行中，但暂无输出"
else
    echo "🔄 Claude Code 运行中："
    echo "$OUTPUT" | head -10
fi