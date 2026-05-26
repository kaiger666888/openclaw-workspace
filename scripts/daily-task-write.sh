#!/bin/bash

# Daily Task Write Script - 写入Notion页面内容
# 用法: ./daily-task-write.sh <page-id> <content-file>

set -e

PAGE_ID="$1"
CONTENT_FILE="$2"

if [ -z "$PAGE_ID" ] || [ -z "$CONTENT_FILE" ]; then
    echo "用法: $0 <page-id> <content-file>"
    echo "示例: $0 34311082-af8e-8159-aebf-c35bf5c03592 /tmp/crew-daily-tasks/github-trending-content.md"
    exit 1
fi

echo "📝 开始写入内容到 Notion..."
echo "📄 页面ID: $PAGE_ID"
echo "📁 内容文件: $CONTENT_FILE"

# 检查内容文件是否存在
if [ ! -f "$CONTENT_FILE" ]; then
    echo "❌ 内容文件不存在: $CONTENT_FILE"
    exit 1
fi

# 检查内容文件的行数
LINE_COUNT=$(wc -l < "$CONTENT_FILE")
echo "📊 内容行数: $LINE_COUNT"

# 转换Markdown为Notion块格式
PYTHON_SCRIPT="/home/kai/.openclaw/workspace/scripts/lib/markdown-to-notion.py"
BLOCKS_FILE="/tmp/notion-blocks-$(echo "$PAGE_ID" | cut -c1-8).json"

echo "🔄 正在转换Markdown为Notion块格式..."
python3 "$PYTHON_SCRIPT" --content "$(cat "$CONTENT_FILE")" "$BLOCKS_FILE"

# 检查转换是否成功
if [ ! -f "$BLOCKS_FILE" ]; then
    echo "❌ Markdown转换失败"
    exit 1
fi

BLOCK_COUNT=$(grep -c '"type"' "$BLOCKS_FILE")
echo "📊 Notion块数: $BLOCK_COUNT"

# 追加内容到Notion页面（不检查块数下限，由调用者决定是否重做）
echo "🚀 正在将内容追加到Notion页面..."
/home/kai/.local/bin/notion-cli page append "$PAGE_ID" --children-file "$BLOCKS_FILE"

if [ $? -eq 0 ]; then
    echo "✅ 内容写入成功 ($BLOCK_COUNT 块)"
else
    echo "❌ 内容写入失败"
    exit 1
fi

echo "🎉 写入完成！"
