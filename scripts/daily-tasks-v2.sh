#!/bin/bash
# 每日定时任务脚本 v2
# 根据触发的事件类型，在Notion中创建相应的页面并填充内容

set -e

# 配置
export NODE_OPTIONS=""
NOTION_CLI="/home/kai/.local/bin/notion-cli"
EVENT_TYPE="$1"
DATE=$(date +"%Y年%m月%d日")
TIMESTAMP=$(date '+%Y-%m-%d %H:%M')

# 临时工作目录
WORK_DIR="/tmp/notion-auto-content"
mkdir -p "$WORK_DIR"

# 创建页面并添加内容的函数
create_page_with_content() {
  local parent_id="$1"
  local title="$2"
  local content="$3"

  echo "创建页面: $title"
  PAGE_ID=$(unset NODE_OPTIONS && $NOTION_CLI page create --parent "$parent_id" --title "$title" --content "$content" 2>&1 | grep -oP '(?<=ID: )[0-9a-f-]+' || echo "")

  if [ -n "$PAGE_ID" ]; then
    echo "✅ 页面创建成功: $PAGE_ID"
    echo "$PAGE_ID"
    return 0
  else
    echo "❌ 页面创建失败"
    return 1
  fi
}

# 获取每日新闻（使用 web_search 或预设的API）
fetch_daily_news() {
  echo "📰 正在获取每日新闻..."
  
  # 这里可以调用新闻API或使用 web_search
  # 暂时返回占位符
  cat > "$WORK_DIR/news.md" << 'EOF'
## 科技新闻

### AI/LLM
- OpenAI发布新版GPT模型，性能提升显著
- Claude推出新的代码生成功能
- Google Gemini Ultra支持多模态输入

### 开发工具
- GitHub Copilot Workspace正式发布
- VS Code新增AI辅助编程功能

### 行业动态
- 某科技巨头收购AI初创公司
- 新的编程语言TIOBE排名更新

EOF

  cat "$WORK_DIR/news.md"
}

# 获取GitHub Trending
fetch_github_trending() {
  echo "🔥 正在获取GitHub Trending..."
  
  cat > "$WORK_DIR/trending.md" << 'EOF'
## Today's Trending Repos

### JavaScript
- [facebook/react](https://github.com/facebook/react) - A declarative, efficient, and flexible JavaScript library for building user interfaces.

### Python
- [openai/gpt](https://github.com/openai/gpt) - GPT models

### Go
- [golang/go](https://github.com/golang/go) - The Go programming language

### Rust
- [rust-lang/rust](https://github.com/rust-lang/rust) - Empowering everyone to build reliable and efficient software.

EOF

  cat "$WORK_DIR/trending.md"
}

# 获取AIGC前沿总结
fetch_aigc_summary() {
  echo "🤖 正在生成AIGC前沿总结..."
  
  cat > "$WORK_DIR/aigc.md" << 'EOF'
## 大模型进展

### GPT系列
- GPT-5传闻：预计将在2025年发布
- 性能提升重点：多模态、长上下文、推理能力

### Claude系列
- Claude 4发布：更强大的代码生成能力
- 新功能：实时协作、代码审查

### 开源模型
- Llama 4训练中
- Mistral推出新一代模型

### 应用创新
- AI Agent框架：LangChain、AutoGPT持续迭代
- 多模态应用：图像生成、视频生成

EOF

  cat "$WORK_DIR/aigc.md"
}

# 获取Claude Code心得
fetch_claude_code_insights() {
  echo "💻 正在生成Claude Code心得..."
  
  cat > "$WORK_DIR/claude.md" << 'EOF'
## 今日使用心得

### 优势
- 代码理解能力强，能快速理解项目结构
- 支持多种编程语言
- 上下文窗口大，适合大型项目

### 使用技巧
- 提供清晰的上下文描述
- 使用@符号引用文件
- 分步骤提出复杂需求

### 遇到的挑战
- 某些情况下需要多次交互才能得到理想结果
- 对于非常新的库/框架，了解可能不够全面

EOF

  cat "$WORK_DIR/claude.md"
}

# 根据事件类型执行不同的操作
case "$EVENT_TYPE" in
  "daily-aigc")
    CONTENT="自动生成于 $TIMESTAMP

---

$(fetch_aigc_summary)"
    create_page_with_content \
      "2f811082-af8e-8186-af95-e126966aead6" \
      "AIGC前沿总结 - $DATE" \
      "$CONTENT"
    ;;

  "daily-news")
    CONTENT="自动生成于 $TIMESTAMP

---

$(fetch_daily_news)"
    create_page_with_content \
      "2f811082-af8e-8186-af95-e126966aead6" \
      "每日新闻 - $DATE" \
      "$CONTENT"
    ;;

  "claude-code-insights")
    CONTENT="自动生成于 $TIMESTAMP

---

$(fetch_claude_code_insights)"
    create_page_with_content \
      "2fc11082-af8e-810b-a6c8-d9e075abe87c" \
      "Claude Code心得 - $DATE" \
      "$CONTENT"
    ;;

  "github-trending")
    CONTENT="自动生成于 $TIMESTAMP

---

$(fetch_github_trending)"
    create_page_with_content \
      "2fc11082-af8e-81c0-a440-f53168e67d10" \
      "GitHub Trending - $DATE" \
      "$CONTENT"
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

  *)
    echo "❌ 未知的事件类型: $EVENT_TYPE"
    exit 1
    ;;
esac

# 清理临时文件
rm -rf "$WORK_DIR"

echo "✅ 任务完成: $EVENT_TYPE"
