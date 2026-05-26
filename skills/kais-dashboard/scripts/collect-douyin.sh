#!/bin/bash
# collect-douyin.sh - 抖音创作者数据采集
source "$(dirname "$0")/lib/db.sh"
db_init

PLATFORM="douyin"
STATS_URL="https://creator.douyin.com/creator-micro/data/overview"

db_log "$PLATFORM" "collect" "开始采集抖音数据"

echo "等待 agent 执行浏览器采集..."
echo "目标 URL: $STATS_URL"
echo ""
echo "agent 采集流程："
echo "1. browser start --profile openclaw"
echo "2. browser navigate --url $STATS_URL"
echo "3. browser snapshot → 解析播放量、粉丝数、互动数据"
echo "4. 构造 JSON → db_insert_snapshot '$PLATFORM' '{json}'"
echo "5. browser stop"

if [ -n "$1" ]; then
  db_insert_snapshot "$PLATFORM" "$1"
  db_log "$PLATFORM" "collect" "数据已存储"
fi
