#!/bin/bash
# collect-xiaohongshu.sh - 小红书创作者数据采集
# 使用 OpenClaw browser (profile=openclaw) 自动化采集

source "$(dirname "$0")/lib/db.sh"
db_init

PLATFORM="xiaohongshu"
STATS_URL="https://creator.xiaohongshu.com/statistics"

db_log "$PLATFORM" "collect" "开始采集小红书数据"

# 注意：实际采集由 agent 通过 browser tool 执行
# 此脚本提供流程框架，agent 按 SKILL.md 中的采集流程操作 browser

echo "等待 agent 执行浏览器采集..."
echo "目标 URL: $STATS_URL"
echo "采集完成后，agent 将调用 db_insert_snapshot 存储数据"
echo ""
echo "agent 采集流程："
echo "1. browser start --profile openclaw"
echo "2. browser navigate --url $STATS_URL"
echo "3. browser snapshot → 解析粉丝数、阅读量、互动数据"
echo "4. 构造 JSON → db_insert_snapshot '$PLATFORM' '{json}'"
echo "5. browser stop"

# 如果直接传入 JSON（用于测试）
if [ -n "$1" ]; then
  db_insert_snapshot "$PLATFORM" "$1"
  db_log "$PLATFORM" "collect" "数据已存储"
fi
