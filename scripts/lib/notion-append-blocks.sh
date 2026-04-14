#!/bin/bash

# Notion Append Blocks Script
# 将Markdown内容追加到Notion页面

# 检查参数
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <PAGE_ID> <MARKDOWN_FILE>"
    exit 1
fi

PAGE_ID="$1"
MARKDOWN_FILE="$2"

# 检查文件是否存在
if [ ! -f "$MARKDOWN_FILE" ]; then
    echo "错误: 文件不存在: $MARKDOWN_FILE"
    exit 1
fi

# 检查notion-cli是否可用
if ! command -v notion-cli >/dev/null 2>&1; then
    echo "错误: notion-cli 未安装或不在PATH中"
    exit 1
fi

echo "开始将内容追加到Notion页面 $PAGE_ID..."

# 直接使用notion-cli追加内容
if notion-cli block append "$PAGE_ID" --content "$(cat "$MARKDOWN_FILE")"; then
    echo "内容追加成功"
    echo "PAGE_ID:$PAGE_ID"
    exit 0
else
    echo "错误: 内容追加失败"
    exit 1
fi