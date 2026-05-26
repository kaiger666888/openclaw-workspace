#!/bin/bash
# 智能搜索封装 - 自动选择最佳搜索方式
# 优先级: Brave API > Bing CN > 百度 > 本地知识库

QUERY="$1"
COUNT="${2:-5}"
OUTPUT_FORMAT="${3:-text}"  # text/json

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 临时文件
TEMP_RESULT="/tmp/search-result-$$"

# 执行搜索
"$SCRIPT_DIR/web-search-fallback.sh" "$QUERY" "$COUNT" > "$TEMP_RESULT" 2>&1
SEARCH_STATUS=$?

if [ $SEARCH_STATUS -eq 0 ]; then
    # 搜索成功
    if [ "$OUTPUT_FORMAT" = "json" ]; then
        # 转换为 JSON 格式（简化版）
        echo '{"status": "success", "results": []}'
    else
        cat "$TEMP_RESULT"
    fi
else
    # 搜索失败，尝试本地知识库
    echo "⚠️  外部搜索失败，尝试本地知识库..." >&2
    echo "" >&2
    
    # 使用 memory_search 搜索本地知识
    if [ -f "$SCRIPT_DIR/../memory/memory-search.sh" ]; then
        "$SCRIPT_DIR/../memory/memory-search.sh" "$QUERY" 2>/dev/null
    else
        echo "📚 本地知识库搜索：" >&2
        grep -r -i "$QUERY" ~/.openclaw/workspace/memory/*.md 2>/dev/null | head -$COUNT
    fi
fi

# 清理
rm -f "$TEMP_RESULT"
