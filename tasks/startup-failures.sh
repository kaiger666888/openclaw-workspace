#!/bin/bash

# Startup Failures Analysis Task
# 执行创业失败经验教训分析任务

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONTENT_FILE="/home/kai/.openclaw/workspace/startup-failures-content.md"
NOTION_SCRIPT="/home/kai/.openclaw/workspace/scripts/lib/notion-append-blocks.sh"

# 确保内容文件存在
if [ ! -f "$CONTENT_FILE" ]; then
    echo "错误: 内容文件不存在: $CONTENT_FILE"
    exit 1
fi

echo "开始执行创业失败经验教训分析任务..."

# 执行搜索和分析（如果需要）
echo "1. 搜索和分析创业失败案例..."
# 这里可以添加更多的分析逻辑

echo "2. 准备内容文件..."
# 检查内容文件格式
if [ -s "$CONTENT_FILE" ]; then
    echo "内容文件已准备就绪"
else
    echo "错误: 内容文件为空"
    exit 1
fi

echo "3. 尝试添加到Notion页面..."

# 首先检查是否已经有相关的页面ID
PAGE_ID=""

# 从TOOLS.md中获取失败经验页面ID
if [ -f "/home/kai/.openclaw/workspace/TOOLS.md" ]; then
    # 尝试从TOOLS.md中提取页面ID
    PAGE_ID=$(grep -o "失败经验:[^ ]*" "/home/kai/.openclaw/workspace/TOOLS.md" | head -1 | cut -d: -f2)
    if [ -n "$PAGE_ID" ]; then
        echo "找到现有页面ID: $PAGE_ID"
    fi
fi

# 如果没有找到页面ID，提示用户创建
if [ -z "$PAGE_ID" ]; then
    echo "警告: 未找到现有页面ID"
    echo "请创建一个新的Notion页面，然后手动指定PAGE_ID"
    echo "或者使用默认的页面ID继续"
    PAGE_ID="请手动指定PAGE_ID"
fi

# 尝试使用notion-script追加内容
if [ -x "$NOTION_SCRIPT" ]; then
    echo "使用Notion脚本追加内容..."
    
    # 创建临时文件用于调试
    TEMP_FILE="/tmp/startup-failures-output.txt"
    echo "PAGE_ID:$PAGE_ID" > "$TEMP_FILE"
    
    # 尝试执行notion脚本
    if "$NOTION_SCRIPT" "$PAGE_ID" "$CONTENT_FILE" >> "$TEMP_FILE" 2>&1; then
        echo "内容已成功追加到Notion页面"
        PAGE_ID=$(grep "PAGE_ID:" "$TEMP_FILE" | tail -1 | cut -d: -f2)
        if [ -n "$PAGE_ID" ]; then
            echo "页面ID: $PAGE_ID"
        fi
    else
        echo "Notion脚本执行失败"
        echo "详细输出:"
        cat "$TEMP_FILE"
        # 尝试其他方法
        if command -v notion >/dev/null 2>&1; notion block append "$PAGE_ID" --content "$(cat "$CONTENT_FILE")" >> "$TEMP_FILE" 2>&1; then
            echo "使用原生notion命令成功"
            PAGE_ID=$(grep "PAGE_ID:" "$TEMP_FILE" | tail -1 | cut -d: -f2)
        else
            echo "所有方法都失败了"
        fi
    fi
    
    # 输出结果
    if [ -f "$TEMP_FILE" ]; then
        echo "执行结果:"
        cat "$TEMP_FILE"
    fi
else
    echo "Notion脚本不可用，尝试直接使用notion命令"
    
    TEMP_FILE="/tmp/startup-failures-output.txt"
    echo "PAGE_ID:$PAGE_ID" > "$TEMP_FILE"
    
    if command -v notion >/dev/null 2>&1; then
        if notion block append "$PAGE_ID" --content "$(cat "$CONTENT_FILE")" >> "$TEMP_FILE" 2>&1; then
            echo "内容已成功追加到Notion页面"
            PAGE_ID=$(grep "PAGE_ID:" "$TEMP_FILE" | tail -1 | cut -d: -f2)
            if [ -n "$PAGE_ID" ]; then
                echo "页面ID: $PAGE_ID"
            fi
        else
            echo "notion命令执行失败"
            echo "详细输出:"
            cat "$TEMP_FILE"
        fi
    else
        echo "notion命令不可用，输出页面ID供手动使用"
        echo "PAGE_ID:$PAGE_ID"
    fi
fi

# 清理临时文件
rm -f "$TEMP_FILE"

echo "创业失败经验教训分析任务完成"
echo "请检查Notion页面中的内容是否正确追加"

exit 0