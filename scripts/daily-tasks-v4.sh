#!/bin/bash
# 每日定时任务脚本 v4
# 使用 notion-helpers.sh 解决字符限制和重试问题

set -e

# 加载辅助函数
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/lib/notion-helpers.sh"

# 配置
DATE=$(date +"%Y年%m月%d日")
TIMESTAMP=$(date '+%Y-%m-%d %H:%M')

# 页面ID映射
declare -A PAGE_MAPPING
PAGE_MAPPING["daily-aigc"]="2f811082-af8e-8186-af95-e126966aead6"
PAGE_MAPPING["daily-news"]="2f811082-af8e-8186-af95-e126966aead6"
PAGE_MAPPING["claude-code-insights"]="2fc11082-af8e-810b-a6c8-d9e075abe87c"
PAGE_MAPPING["github-trending"]="2fc11082-af8e-81c0-a440-f53168e67d10"
PAGE_MAPPING["daily-summary"]="2f811082-af8e-8103-adba-d7e49dec89e9"
PAGE_MAPPING["daily-meal"]="2f811082-af8e-8128-a12d-f819313e0cf9"
PAGE_MAPPING["vibecoding"]="2fc11082-af8e-817f-9542-ddf609cecc49"
PAGE_MAPPING["reading-notes"]="2fc11082-af8e-8138-8fca-c70bcced3395"
PAGE_MAPPING["failure-lessons"]="2fc11082-af8e-8120-b640-cf5eb9e2b134"
PAGE_MAPPING["tech-research"]="2fc11082-af8e-81de-98bb-d1741c3cee68"
PAGE_MAPPING["investment-wisdom"]="2fc11082-af8e-8138-8fca-c70bcced3395"
PAGE_MAPPING["startup-failures"]="2fc11082-af8e-8120-b640-cf5eb9e2b134"

# 标题映射
declare -A TITLE_MAPPING
TITLE_MAPPING["daily-aigc"]="AIGC前沿总结"
TITLE_MAPPING["daily-news"]="每日新闻"
TITLE_MAPPING["claude-code-insights"]="Claude Code心得"
TITLE_MAPPING["github-trending"]="GitHub Trending"
TITLE_MAPPING["daily-summary"]="每日总结"
TITLE_MAPPING["daily-meal"]="每日用餐"
TITLE_MAPPING["vibecoding"]="VibeCoding"
TITLE_MAPPING["reading-notes"]="读书笔记"
TITLE_MAPPING["failure-lessons"]="失败经验"
TITLE_MAPPING["tech-research"]="技术研究"
TITLE_MAPPING["investment-wisdom"]="投资大师思想精华"
TITLE_MAPPING["startup-failures"]="创业失败经验教训"

# 初始内容模板
get_initial_content() {
  local event_type="$1"

  case "$event_type" in
    "daily-news")
      echo "自动生成于 $TIMESTAMP

---

*正在获取最新新闻...*"
      ;;
    "github-trending")
      echo "自动生成于 $TIMESTAMP

---

*正在获取GitHub Trending...*"
      ;;
    "daily-aigc")
      echo "自动生成于 $TIMESTAMP

---

*正在生成AIGC前沿总结...*"
      ;;
    "claude-code-insights")
      echo "自动生成于 $TIMESTAMP

---

*正在生成使用心得...*"
      ;;
    "investment-wisdom")
      echo "自动生成于 $TIMESTAMP

---

*正在收集投资大师思想精华...*"
      ;;
    "startup-failures")
      echo "自动生成于 $TIMESTAMP

---

*正在收集创业失败案例...*"
      ;;
    *)
      echo "自动生成于 $TIMESTAMP

---

## 待补充内容"
      ;;
  esac
}

# 创建页面（使用辅助函数）
create_page() {
  local event_type="$1"
  local parent_id="${PAGE_MAPPING[$event_type]}"
  local title_prefix="${TITLE_MAPPING[$event_type]}"
  local title="$title_prefix - $DATE"
  local content=$(get_initial_content "$event_type")

  if [ -z "$parent_id" ]; then
    echo "❌ 错误: 未知的事件类型 '$event_type'"
    exit 1
  fi

  echo "📝 创建页面: $title"
  echo "📂 父页面: $parent_id"

  local page_id=$(safe_create_page "$parent_id" "$title" "$content")

  if [ -n "$page_id" ] && [[ "$page_id" != *"失败"* ]]; then
    echo "✅ 页面创建成功"
    echo "$page_id"
    return 0
  else
    echo "❌ 页面创建失败"
    return 1
  fi
}

# 追加内容（使用辅助函数，自动分段）
append_content() {
  local page_id="$1"
  local content="$2"

  echo "📝 追加内容到页面: $page_id"
  append_long_content "$page_id" "$content"
  return $?
}

# 主逻辑
EVENT_TYPE="$1"
MODE="$2"  # create-only 或 full

if [ -z "$EVENT_TYPE" ]; then
  echo "用法: $0 <事件类型> [create-only|full|append:CONTENT]"
  echo ""
  echo "事件类型:"
  echo "  daily-aigc, daily-news, claude-code-insights, github-trending"
  echo "  daily-summary, daily-meal, vibecoding, reading-notes"
  echo "  failure-lessons, tech-research, investment-wisdom, startup-failures"
  echo ""
  echo "模式:"
  echo "  create-only       - 仅创建页面，返回页面ID（默认）"
  echo "  full              - 创建页面并尝试填充内容"
  echo "  append:CONTENT    - 追加内容到已有页面"
  exit 1
fi

# 处理追加模式
if [[ "$MODE" == append:* ]]; then
  # 格式: append:PAGE_ID:BASE64_CONTENT
  mode_content="${MODE#append:}"

  if [[ "$mode_content" == *:* ]]; then
    page_id="${mode_content%%:*}"
    encoded_content="${mode_content#*:}"
    content=$(echo "$encoded_content" | base64 -d)

    append_content "$page_id" "$content"
    exit $?
  else
    echo "❌ 追加模式格式错误，应为 append:PAGE_ID:BASE64_CONTENT"
    exit 1
  fi
fi

# 默认模式为 create-only
if [ "$MODE" != "full" ]; then
  MODE="create-only"
fi

# 创建页面
PAGE_ID=$(create_page "$EVENT_TYPE")

if [ -n "$PAGE_ID" ] && [[ "$PAGE_ID" != *"失败"* ]]; then
  if [ "$MODE" = "full" ]; then
    echo ""
    echo "🔄 模式: full - 触发内容填充"
  fi

  # 输出页面ID供调用者使用
  echo "PAGE_ID:$PAGE_ID"
fi
