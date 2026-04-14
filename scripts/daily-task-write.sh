#!/bin/bash

# Daily Task Write Script - 写入Notion页面内容
# 用法: ./daily-task-write.sh <event> <content-file>

set -e

EVENT="$1"
CONTENT_FILE="$2"

if [ -z "$EVENT" ] || [ -z "$CONTENT_FILE" ]; then
    echo "用法: $0 <event> <content-file>"
    echo "示例: $0 daily-news /path/to/daily-news-content.md"
    exit 1
fi

echo "📝 开始写入 $EVENT 内容到 Notion..."

# 查找对应的页面
case "$EVENT" in
    "daily-news")
        PAGE_ID="34011082-af8e-8157-bcb7-d1a91dfe423b"
        ;;
    "claude-code-insights")
        PAGE_ID="34011082-af8e-817f-9426-c807ce8b9b63"
        ;;
    "github-trending")
        PAGE_ID="3fc11082-af8e-81c0-a440-f53168e67d10"
        ;;
    *)
        echo "未知的事件类型: $EVENT"
        exit 1
        ;;
esac

echo "📄 页面ID: $PAGE_ID"
echo "📁 内容文件: $CONTENT_FILE"

# 检查内容文件是否存在
if [ ! -f "$CONTENT_FILE" ]; then
    echo "❌ 内容文件不存在: $CONTENT_FILE"
    exit 1
fi

# 检查内容文件的行数和块数
LINE_COUNT=$(wc -l < "$CONTENT_FILE")
echo "📊 内容行数: $LINE_COUNT"

# 转换Markdown为Notion块格式
PYTHON_SCRIPT="/home/kai/.openclaw/workspace/scripts/lib/markdown-to-notion.py"
BLOCKS_FILE="/tmp/notion-blocks-$EVENT.json"

echo "🔄 正在转换Markdown为Notion块格式..."
python3 "$PYTHON_SCRIPT" --content "$(cat "$CONTENT_FILE")" "$BLOCKS_FILE"

# 检查转换是否成功
if [ ! -f "$BLOCKS_FILE" ]; then
    echo "❌ Markdown转换失败"
    exit 1
fi

BLOCK_COUNT=$(grep -c '"type"' "$BLOCKS_FILE")
echo "📊 Notion块数: $BLOCK_COUNT"

# 检查块数是否达标
if [ "$BLOCK_COUNT" -lt 50 ]; then
    echo "⚠️ 块数不足 ($BLOCK_COUNT < 50)，需要重新生成内容"
    exit 1
fi

echo "✅ 块数达标 ($BLOCK_COUNT)"

# 追加内容到Notion页面
echo "🚀 正在将内容追加到Notion页面..."
notion-cli page append "$PAGE_ID" --children-file "$BLOCKS_FILE"

if [ $? -eq 0 ]; then
    echo "✅ 内容写入成功"
    
    # 验证最终块数
    FINAL_BLOCKS=$(notion-cli block list "$PAGE_ID" --output json | grep -c '"type"' || echo "0")
    echo "📊 最终块数: $FINAL_BLOCKS"
    
    if [ "$FINAL_BLOCKS" -ge 50 ]; then
        echo "✅ 任务完成: $EVENT"
        echo "📋 状态: 成功 ($FINAL_BLOCKS 块)"
    else
        echo "❌ 块数验证失败: $FINAL_BLOCKS < 50"
        exit 1
    fi
else
    echo "❌ 内容写入失败"
    exit 1
fi

echo "🎉 $EVENT 任务完成！"