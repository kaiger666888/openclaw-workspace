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

# 简单的Markdown转换
convert_markdown_to_notion() {
    local input_file="$1"
    local temp_file="/tmp/converted_markdown.txt"
    
    # 简单转换：保留大部分原始内容，移除纯标题格式
    while IFS= read -r line; do
        # 处理标题 - 转换为简单文本
        if [[ "$line" =~ ^#{1,6} (.+)$ ]]; then
            local text="${BASH_REMATCH[1]}"
            echo "$text"
        # 处理代码块
        elif [[ "$line" =~ ^``` ]]; then
            echo "```"
        else
            echo "$line"
        fi
    done < "$input_file" > "$temp_file"
    
    echo "$temp_file"
}

echo "开始转换Markdown格式..."

# 转换文件
CONVERTED_FILE=$(convert_markdown_to_notion "$MARKDOWN_FILE")

echo "开始将内容追加到Notion页面 $PAGE_ID..."

# 使用notion-cli追加内容
if notion-cli block append "$PAGE_ID" --content "$(cat "$CONVERTED_FILE")"; then
    echo "内容追加成功"
    
    # 清理临时文件
    rm -f "$CONVERTED_FILE"
    echo "PAGE_ID:$PAGE_ID"
    exit 0
else
    echo "错误: 内容追加失败"
    rm -f "$CONVERTED_FILE"
    exit 1
fi