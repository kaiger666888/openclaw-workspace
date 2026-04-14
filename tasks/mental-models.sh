#!/bin/bash

# Mental Models Daily Task
# 执行每日心智模型研究和总结

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LIB_DIR="/home/kai/.openclaw/workspace/scripts/lib"

echo "=========================================="
echo "执行每日心智模型任务"
echo "=========================================="

# 检查临时文件是否存在
TEMP_FILE="/tmp/mental-models-content.md"
if [ ! -f "$TEMP_FILE" ]; then
    echo "错误: 临时文件不存在: $TEMP_FILE"
    echo "请确保先创建了心智模型内容文件"
    exit 1
fi

echo "找到心智模型内容文件: $TEMP_FILE"

# 提取页面ID
PAGE_ID=$(grep "^PAGE_ID:" "$TEMP_FILE" | sed 's/PAGE_ID://g' | tr -d ' ')
if [ -z "$PAGE_ID" ]; then
    echo "未在文件中找到页面ID，尝试从文件内容中提取..."
    
    # 从文件中查找可能的页面ID格式
    PAGE_ID=$(grep -oE "[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}" "$TEMP_FILE" | head -1)
    
    if [ -z "$PAGE_ID" ]; then
        echo "❌ 无法从文件中提取页面ID"
        echo "请确保文件包含有效的Notion页面ID"
        exit 1
    fi
fi

echo "提取到页面ID: $PAGE_ID"

# 使用追加方式更新到Notion
echo "使用追加模式更新到Notion..."
if [ -f "$LIB_DIR/notion-append-blocks-chunked.sh" ]; then
    echo "执行分块追加脚本..."
    "$LIB_DIR/notion-append-blocks-chunked.sh" "$PAGE_ID" "$TEMP_FILE"
    
    if [ $? -eq 0 ]; then
        echo "✅ 内容已成功分块追加到Notion页面"
        
        # 记录执行状态
        echo "$(date '+%Y-%m-%d %H:%M:%S') - mental-models - success" >> /home/kai/.openclaw/workspace/task-execution.log
    else
        echo "❌ 分块追加内容到Notion失败"
        echo "$(date '+%Y-%m-%d %H:%M:%S') - mental-models - failed" >> /home/kai/.openclaw/workspace/task-execution.log
        exit 1
    fi
else
    echo "❌ 未找到分块追加脚本: $LIB_DIR/notion-append-blocks-chunked.sh"
    exit 1
fi

# 清理临时文件
# rm -f "$TEMP_FILE"  # 保留临时文件供调试

echo "每日心智模型任务完成"
echo "=========================================="

exit 0