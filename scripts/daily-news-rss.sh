#!/bin/bash
# 每日新闻任务 - 使用RSS抓取
set -e

DATE=$(date +"%Y年%m月%d日")
NOTION_CLI="/home/kai/.local/bin/notion-cli"
RSS_SCRIPT="/home/kai/.openclaw/workspace/scripts/fetch-news-v3.sh"

# 1. 获取新闻内容
NEWS_CONTENT=$($RSS_SCRIPT 2>/dev/null | tail -n +3)  # 跳过前两行提示

if [ -z "$NEWS_CONTENT" ]; then
  echo "❌ 新闻获取失败"
  exit 1
fi

# 2. 创建Notion页面
PAGE_ID=$($NOTION_CLI page create \
  --parent "2f811082-af8e-8186-af95-e126966aead6" \
  --title "每日新闻 - $DATE" \
  --content "自动生成于 $(date '+%Y-%m-%d %H:%M')

$NEWS_CONTENT" 2>&1 | grep -oP '(?<=ID: )[0-9a-f-]+' || echo "")

if [ -n "$PAGE_ID" ]; then
  echo "✅ 每日新闻完成"
  echo "页面ID: $PAGE_ID"
  exit 0
else
  echo "❌ 页面创建失败"
  exit 1
fi
