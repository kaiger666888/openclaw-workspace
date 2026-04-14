#!/bin/bash
# Notion内容填充脚本
# 用于子代理调用，生成并填充Notion页面内容

set -e

# 配置
NOTION_CLI="/home/kai/.local/bin/notion-cli"
WORK_DIR="/tmp/notion-content-work"
mkdir -p "$WORK_DIR"

DATE=$(date +"%Y年%m月%d日")
EVENT_TYPE="$1"
PAGE_ID="$2"

if [ -z "$EVENT_TYPE" ]; then
  echo "错误: 缺少事件类型参数"
  exit 1
fi

echo "📝 开始为 $EVENT_TYPE 生成内容..."
echo "📅 日期: $DATE"
if [ -n "$PAGE_ID" ]; then
  echo "📄 页面ID: $PAGE_ID"
fi

# 根据事件类型生成内容
generate_content() {
  local event_type="$1"
  local output_file="$WORK_DIR/content.md"

  case "$event_type" in
    "daily-news")
      cat > "$output_file" << 'EOF'
## 今日科技新闻

### AI/大模型
<!-- 内容将通过web_search生成 -->

### 开发工具
<!-- 内容将通过web_search生成 -->

### 安全/漏洞
<!-- 内容将通过web_search生成 -->

### 行业动态
<!-- 内容将通过web_search生成 -->
EOF
      ;;

    "github-trending")
      cat > "$output_file" << 'EOF'
## GitHub Trending 今日热门

### JavaScript
<!-- 内容将通过API获取 -->

### Python
<!-- 内容将通过API获取 -->

### TypeScript
<!-- 内容将通过API获取 -->

### Go
<!-- 内容将通过API获取 -->

### Rust
<!-- 内容将通过API获取 -->
EOF
      ;;

    "daily-aigc")
      cat > "$output_file" << 'EOF'
## AIGC前沿总结

### 大模型进展
- GPT系列最新动态
- Claude系列更新
- 开源模型（Llama, Mistral等）

### AI应用创新
- 新的AI工具/框架
- 重要的AI应用场景

### 值得关注的论文/研究
<!-- 内容将通过web_search生成 -->
EOF
      ;;

    "claude-code-insights")
      cat > "$output_file" << 'EOF'
## Claude Code 使用心得

### 今日亮点
- 使用的核心功能
- 解决的问题

### 实用技巧
- 提示词优化建议
- 工作流程改进

### 遇到的挑战
- 问题描述
- 解决方案
EOF
      ;;

    *)
      echo "# $event_type - $DATE

## 待补充内容

请添加相关内容。" > "$output_file"
      ;;
  esac

  echo "$output_file"
}

# 生成内容模板
CONTENT_FILE=$(generate_content "$EVENT_TYPE")

echo "📄 内容文件: $CONTENT_FILE"
cat "$CONTENT_FILE"

# 如果有页面ID，尝试更新页面
if [ -n "$PAGE_ID" ]; then
  echo ""
  echo "🔄 正在更新Notion页面..."
  # 注意：这里需要实际的notion-cli调用逻辑
  # 由于页面创建和内容填充可能需要分开处理
  echo "💡 提示: 页面内容需要在子代理中使用web_search等工具生成"
  echo "📋 下一步: 使用notion-cli page append命令添加内容"
fi

echo ""
echo "✅ 内容生成完成"
