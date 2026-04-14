#!/bin/bash
# 每日定时任务脚本
# 根据触发的事件类型，在Notion中创建相应的页面

set -e

# 配置
export NODE_OPTIONS=""
NOTION_CLI="/home/kai/.local/bin/notion-cli"
EVENT_TYPE="$1"
DATE=$(date +"%Y年%m月%d日")
TIMESTAMP=$(date '+%Y-%m-%d %H:%M')

# 创建页面并添加内容的函数
create_page_with_content() {
  local parent_id="$1"
  local title="$2"
  local content="$3"
  local fill_content="$4"  # 是否填充内容

  echo "创建页面: $title"
  PAGE_ID=$($NOTION_CLI page create --parent "$parent_id" --title "$title" --content "$content" 2>&1 | grep -oP '(?<=ID: )[0-9a-f-]+' || echo "")

  if [ -n "$PAGE_ID" ]; then
    echo "✅ 页面创建成功: $PAGE_ID"

    # 如果需要填充内容且页面创建成功，触发子代理生成内容
    if [ "$fill_content" = "true" ] && [ -n "$PAGE_ID" ]; then
      echo "🔄 触发内容填充任务..."
      # 这里可以调用sub-agent来生成内容
      # 暂时跳过，等待用户确认方案
    fi

    return 0
  else
    echo "❌ 页面创建失败"
    return 1
  fi
}

# 根据事件类型执行不同的操作
case "$EVENT_TYPE" in
  "daily-aigc")
    create_page_with_content \
      "2f811082-af8e-8186-af95-e126966aead6" \
      "AIGC前沿总结 - $DATE" \
      "自动生成于 $TIMESTAMP

---

## 待补充内容

请在此处添加AIGC前沿总结内容。"
    ;;

  "daily-news")
    create_page_with_content \
      "2f811082-af8e-8186-af95-e126966aead6" \
      "每日新闻 - $DATE" \
      "自动生成于 $TIMESTAMP

---

## 待补充内容

请在此处添加每日新闻内容。"
    ;;

  "claude-code-insights")
    create_page_with_content \
      "2fc11082-af8e-810b-a6c8-d9e075abe87c" \
      "Claude Code心得 - $DATE" \
      "自动生成于 $TIMESTAMP

---

## 待补充内容

请在此处添加Claude Code心得内容。"
    ;;

  "github-trending")
    create_page_with_content \
      "2fc11082-af8e-81c0-a440-f53168e67d10" \
      "GitHub Trending - $DATE" \
      "自动生成于 $TIMESTAMP

---

## 待补充内容

请在此处添加GitHub Trending内容。"
    ;;

  "daily-summary")
    create_page_with_content \
      "2f811082-af8e-8103-adba-d7e49dec89e9" \
      "每日总结 - $DATE" \
      "自动生成于 $TIMESTAMP

---

## 今日总结

### 完成的工作



### 学到的知识



### 遇到的问题



### 明日计划



"
    ;;

  "daily-meal")
    create_page_with_content \
      "2f811082-af8e-8128-a12d-f819313e0cf9" \
      "每日用餐 - $DATE" \
      "自动生成于 $TIMESTAMP

---

## 早餐



## 午餐



## 晚餐



## 加餐



"
    ;;

  "vibecoding")
    create_page_with_content \
      "2fc11082-af8e-817f-9542-ddf609cecc49" \
      "VibeCoding - $DATE" \
      "自动生成于 $TIMESTAMP

---

## 今日编码

### 项目/功能



### 代码片段



### 技术探索



"
    ;;

  "reading-notes")
    create_page_with_content \
      "2fc11082-af8e-8138-8fca-c70bcced3395" \
      "读书笔记 - $DATE" \
      "自动生成于 $TIMESTAMP

---

## 今日阅读

### 书目/文章



### 摘抄



### 感悟



"
    ;;

  "failure-lessons")
    create_page_with_content \
      "2fc11082-af8e-8120-b640-cf5eb9e2b134" \
      "失败经验 - $DATE" \
      "自动生成于 $TIMESTAMP

---

## 今日失败/错误

### 问题描述



### 原因分析



### 解决方案



### 经验教训



"
    ;;

  "tech-research")
    create_page_with_content \
      "2fc11082-af8e-81de-98bb-d1741c3cee68" \
      "技术研究 - $DATE" \
      "自动生成于 $TIMESTAMP

---

## 研究主题



### 研究内容



### 发现/结论



### 参考资料



"
    ;;

  "github-review")
    echo "🔍 开始 GitHub 代码审查任务"
    /home/kai/.openclaw/workspace/scripts/github-review.sh
    ;;

  "nightly-review")
    echo "🌙 开始夜间回顾任务"
    # 这个任务由 sub-agent 执行，不需要 shell 脚本
    echo "夜间回顾任务应由 OpenClaw 主会话的 cron 触发 sub-agent 执行"
    ;;

  "mental-models")
    create_page_with_content \
      "31d11082-af8e-8116-83f3-f87f63dbafb1" \
      "心智模型 - $DATE" \
      "自动生成于 $TIMESTAMP

---

## 今日心智模型

### 核心概念



### 来源/背景



### 应用场景



### 相关模型



### 实践建议



"
    ;;

  "knowledge-viz")
    # 知识可视化追踪 - 每日追踪知识可视化领域的最新可应用技术
    create_page_with_content \
      "2fc11082-af8e-81de-98bb-d1741c3cee68" \
      "知识可视化研究 - $DATE" \
      "自动生成于 $TIMESTAMP

---

## 今日发现

### 工具更新

<!-- 内容将通过 sub-agent 生成 -->

### 技术创新
<!-- 内容将通过 sub-agent 生成 -->

### 最佳实践
<!-- 内容将通过 sub-agent 生成 -->

### 相关资源
<!-- 内容将通过 sub-agent 生成 -->
"
    ;;

  "uml-tech-radar")
    create_page_with_content \
      "2fc11082-af8e-81de-98bb-d1741c3cee68" \
      "UML技术雷达 - $DATE" \
      "自动生成于 $TIMESTAMP

---

## 🔥 高优先级技术

<!-- 内容将通过 sub-agent 生成 -->

## 💡 值得关注

<!-- 内容将通过 sub-agent 生成 -->

## 📚 相关资源

<!-- 内容将通过 sub-agent 生成 -->
"
    ;;

  *)
    echo "❌ 未知的事件类型: $EVENT_TYPE"
    exit 1
    ;;
esac

echo "✅ 任务完成: $EVENT_TYPE"
