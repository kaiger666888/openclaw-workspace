#!/bin/bash
# 每日定时任务脚本
# 根据触发的事件类型，在Notion中创建空页面（内容由 daily-task-write.sh 填充）

set -e

# 配置
export NODE_OPTIONS=""
NOTION_CLI="/home/kai/.local/bin/notion-cli"
EVENT_TYPE="$1"
DATE=$(date +"%Y年%m月%d日")

# 创建空页面的函数
create_page() {
  local parent_id="$1"
  local title="$2"

  echo "创建页面: $title"
  PAGE_ID=$($NOTION_CLI page create --parent "$parent_id" --title "$title" 2>&1 | grep -oP '(?<=ID: )[0-9a-f-]+' || echo "")

  if [ -n "$PAGE_ID" ]; then
    echo "✅ 页面创建成功: $PAGE_ID"
    return 0
  else
    echo "❌ 页面创建失败"
    return 1
  fi
}

# 根据事件类型执行不同的操作
case "$EVENT_TYPE" in
  "daily-aigc")
    create_page \
      "2f811082-af8e-8186-af95-e126966aead6" \
      "AIGC前沿总结 - $DATE"
    ;;

  "daily-news")
    create_page \
      "2f811082-af8e-8186-af95-e126966aead6" \
      "每日新闻 - $DATE"
    ;;

  "claude-code-insights")
    create_page \
      "2fc11082-af8e-810b-a6c8-d9e075abe87c" \
      "Claude Code心得 - $DATE"
    ;;

  "github-trending")
    create_page \
      "2fc11082-af8e-81c0-a440-f53168e67d10" \
      "GitHub Trending - $DATE"
    ;;

  "daily-summary")
    create_page \
      "2f811082-af8e-8103-adba-d7e49dec89e9" \
      "每日总结 - $DATE"
    ;;

  "daily-meal")
    create_page \
      "2f811082-af8e-8128-a12d-f819313e0cf9" \
      "每日用餐 - $DATE"
    ;;

  "vibecoding")
    create_page \
      "2fc11082-af8e-817f-9542-ddf609cecc49" \
      "VibeCoding - $DATE"
    ;;

  "reading-notes")
    create_page \
      "2fc11082-af8e-8138-8fca-c70bcced3395" \
      "读书笔记 - $DATE"
    ;;

  "failure-lessons")
    create_page \
      "2fc11082-af8e-8120-b640-cf5eb9e2b134" \
      "失败经验 - $DATE"
    ;;

  "tech-research")
    create_page \
      "2fc11082-af8e-81de-98bb-d1741c3cee68" \
      "技术研究 - $DATE"
    ;;

  "github-review")
    echo "🔍 开始 GitHub 代码审查任务"
    /home/kai/.openclaw/workspace/scripts/github-review.sh
    ;;

  "nightly-review")
    echo "🌙 开始夜间回顾任务"
    echo "夜间回顾任务应由 OpenClaw 主会话的 cron 触发 sub-agent 执行"
    ;;

  "mental-models")
    create_page \
      "31d11082-af8e-8116-83f3-f87f63dbafb1" \
      "心智模型 - $DATE"
    ;;

  "knowledge-viz")
    create_page \
      "2fc11082-af8e-81de-98bb-d1741c3cee68" \
      "知识可视化研究 - $DATE"
    ;;

  "investment-wisdom")
    create_page \
      "2b011082-af8e-8035-a849-eabd27cadac3" \
      "投资大师思想 - $DATE"
    ;;

  "startup-failures")
    create_page \
      "2fc11082-af8e-8120-b640-cf5eb9e2b134" \
      "创业失败经验教训 - $DATE"
    ;;

  "daily-language")
    create_page \
      "30411082-af8e-8191-9fb5-d1ca8f6d7b6f" \
      "每日语言学习 - $DATE"
    ;;

  "uml-tech-radar")
    create_page \
      "2fc11082-af8e-81de-98bb-d1741c3cee68" \
      "UML技术雷达 - $DATE"
    ;;

  *)
    echo "❌ 未知的事件类型: $EVENT_TYPE"
    exit 1
    ;;
esac

echo "✅ 任务完成: $EVENT_TYPE"
