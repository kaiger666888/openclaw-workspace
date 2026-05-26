#!/bin/bash

# Startup Failures Content Append Script
# 将创业失败分析内容分块追加到Notion页面

# 配置
PAGE_ID="2fc11082-af8e-8120-b640-cf5eb9e2b134"  # 失败经验页面ID
CONTENT_FILE="/home/kai/.openclaw/workspace/startup-failures-content.md"
TEMP_DIR="/tmp/startup-failures-chunks"

# 创建临时目录
mkdir -p "$TEMP_DIR"

# 将内容分割成小块（每块不超过2000字符）
split -b 1800 "$CONTENT_FILE" "$TEMP_DIR/chunk_"

echo "开始追加创业失败分析内容到Notion页面..."
echo "页面ID: $PAGE_ID"
echo "内容文件: $CONTENT_FILE"

# 检查notion-cli是否可用
if ! command -v notion-cli >/dev/null 2>&1; then
    echo "错误: notion-cli 未安装或不在PATH中"
    exit 1
fi

# 追加每个块
chunk_count=0
total_chunks=0

# 计算块数量
for chunk_file in "$TEMP_DIR"/chunk_*; do
    if [ -f "$chunk_file" ]; then
        total_chunks=$((total_chunks + 1))
    fi
done

echo "总共需要追加 $total_chunks 个块..."

# 逐块追加
for chunk_file in "$TEMP_DIR"/chunk_*; do
    if [ -f "$chunk_file" ]; then
        chunk_count=$((chunk_count + 1))
        echo "正在追加第 $chunk_count/$total_chunks 块..."
        
        # 获取当前块的内容
        chunk_content=$(cat "$chunk_file")
        
        # 追加到Notion页面
        if notion-cli block append "$PAGE_ID" --content "$chunk_content"; then
            echo "第 $chunk_count 块追加成功"
        else
            echo "警告: 第 $chunk_count 块追加失败"
        fi
        
        # 添加延迟避免API限制
        sleep 1
    fi
done

# 清理临时文件
rm -rf "$TEMP_DIR"

echo "所有内容块追加完成！"
echo "页面ID: $PAGE_ID"

exit 0