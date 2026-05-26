#!/usr/bin/env bash
# tg-progress.sh — Telegram 实时进度条
# 用法:
#   1. 编程式: echo "进度文字" | tg-progress.sh [--chat-id ID] [--tag 标签]
#   2. 包装命令: tg-progress.sh --tag "构建中" -- your-command args...
#
# 进度消息会原地更新(editMessageText)，任务完成后删除最终消息。

set -euo pipefail

# ---- 配置 ----
BOT_TOKEN="8238043135:AAFqqbV2XvlvRWzZ6-Jaw-B_sY8ywMg4hVI"
PROXY="http://127.0.0.1:7890"
DEFAULT_CHAT_ID="-1003809592909"

# ---- 参数解析 ----
TAG=""
CHAT_ID="$DEFAULT_CHAT_ID"
WRAP_CMD=()
PIPE_MODE=true

while [[ $# -gt 0 ]]; do
    case "$1" in
        --chat-id) CHAT_ID="$2"; shift 2 ;;
        --tag) TAG="$2"; shift 2 ;;
        --) shift; WRAP_CMD=("$@"); PIPE_MODE=false; break ;;
        *) echo "未知参数: $1" >&2; exit 1 ;;
    esac
done

# ---- Telegram API 调用 ----
tg_call() {
    local method="$1"; shift
    curl -s --proxy "$PROXY" \
        -X POST "https://api.telegram.org/bot${BOT_TOKEN}/${method}" \
        "$@"
}

send_msg() {
    local text="$1"
    tg_call sendMessage \
        -F "chat_id=${CHAT_ID}" \
        -F "text=${text}" \
        -F "parse_mode=Markdown" \
        -F "disable_notification=true"
}

edit_msg() {
    local msg_id="$1" text="$2"
    tg_call editMessageText \
        -F "chat_id=${CHAT_ID}" \
        -F "message_id=${msg_id}" \
        -F "text=${text}" \
        -F "parse_mode=Markdown"
}

delete_msg() {
    local msg_id="$1"
    tg_call deleteMessage \
        -F "chat_id=${CHAT_ID}" \
        -F "message_id=${msg_id}" &>/dev/null || true
}

# ---- 提取 message_id ----
extract_msg_id() {
    python3 -c "import sys,json; print(json.load(sys.stdin).get('result',{}).get('message_id',''))" 2>/dev/null
}

# ---- 进度函数 ----
MSG_ID=""

progress() {
    local text="$1"
    local prefix=""
    [[ -n "$TAG" ]] && prefix="*${TAG}* | "

    if [[ -z "$MSG_ID" ]]; then
        # 首次：发送新消息
        MSG_ID=$(send_msg "${prefix}${text}" | extract_msg_id)
    else
        # 后续：编辑已有消息
        edit_msg "$MSG_ID" "${prefix}${text}" &>/dev/null || {
            # 编辑失败（消息太旧/被删），重新发送
            MSG_ID=$(send_msg "${prefix}${text}" | extract_msg_id)
        }
    fi
}

finish_progress() {
    if [[ -n "$MSG_ID" ]]; then
        delete_msg "$MSG_ID"
    fi
}

trap finish_progress EXIT

# ---- 模式1: 包装命令模式 ----
if [[ "$PIPE_MODE" == "false" && ${#WRAP_CMD[@]} -gt 0 ]]; then
    progress "⏳ 启动中..."

    # 用文件捕获输出，同时 tee 到终端
    TMP_OUT=$(mktemp)
    trap 'rm -f "$TMP_OUT"; finish_progress' EXIT

    LINE_COUNT=0
    LAST_UPDATE=0

    "${WRAP_CMD[@]}" 2>&1 | while IFS= read -r line; do
        echo "$line"  # 透传到终端

        LINE_COUNT=$((LINE_COUNT + 1))
        NOW=$(date +%s)

        # 每2秒或每10行更新一次，避免触发速率限制
        if [[ $((NOW - LAST_UPDATE)) -ge 2 ]] || [[ $((LINE_COUNT % 10)) -eq 0 ]]; then
            LAST_UPDATE=$NOW
            # 取最后3行作为进度预览
            PREVIEW=$(echo "$line" | tail -c 200)
            progress "行 ${LINE_COUNT} | \`${PREVIEW}\`"
        fi
    done

    EXIT_CODE=${PIPESTATUS[0]:-0}
    progress "✅ 完成 (exit: ${EXIT_CODE})"

    # 最终结果保留3秒后删除
    sleep 3
    exit "$EXIT_CODE"

# ---- 模式2: 管道/行输入模式 ----
else
    LINE_COUNT=0
    LAST_UPDATE=0

    while IFS= read -r line; do
        LINE_COUNT=$((LINE_COUNT + 1))
        NOW=$(date +%s)

        if [[ $((NOW - LAST_UPDATE)) -ge 2 ]] || [[ $((LINE_COUNT % 5)) -eq 0 ]]; then
            LAST_UPDATE=$NOW
            progress "[${LINE_COUNT}] ${line}"
        fi
    done

    progress "✅ 完成，共 ${LINE_COUNT} 条更新"
    sleep 2
fi
