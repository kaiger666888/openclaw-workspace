#!/bin/bash
# 内容生成脚本 - 使用AI子代理生成高质量内容
# 用法: ./generate-content.sh <事件类型> <输出文件>

EVENT_TYPE="$1"
OUTPUT_FILE="$2"
DATE=$(date +"%Y年%m月%d日")

if [ -z "$EVENT_TYPE" ] || [ -z "$OUTPUT_FILE" ]; then
  echo "用法: $0 <事件类型> <输出文件>"
  exit 1
fi

# 根据事件类型生成不同的提示词
case "$EVENT_TYPE" in
  "daily-news")
    PROMPT="请生成今天的科技新闻摘要（$DATE），包括：
1. AI/大模型领域的重要进展
2. 开发工具和编程语言的更新
3. 重要的安全漏洞或技术问题
4. 其他值得关注的科技动态

请使用简洁的中文，每条新闻用1-2句话概括。使用markdown格式。"
    ;;

  "github-trending")
    PROMPT="请模拟生成今天的GitHub Trending列表（$DATE），包括：
1. JavaScript热门项目
2. Python热门项目  
3. Go热门项目
4. Rust热门项目
5. 其他值得注意的项目

每个项目包括：项目名称、简短描述。使用markdown格式。"
    ;;

  "daily-aigc")
    PROMPT="请生成AIGC前沿总结（$DATE），包括：
1. 大模型进展（GPT、Claude、开源模型等）
2. AI应用创新
3. 重要的AI工具/框架更新
4. 值得关注的AI论文或研究

请使用简洁的中文，使用markdown格式。"
    ;;

  "claude-code-insights")
    PROMPT="请生成Claude Code使用心得（$DATE），包括：
1. 今日使用的亮点功能
2. 实用的使用技巧
3. 遇到的挑战和解决方案
4. 对其他用户的建议

请使用简洁的中文，从实际使用角度出发。使用markdown格式。"
    ;;

  *)
    echo "未知的事件类型: $EVENT_TYPE"
    exit 1
    ;;
esac

# 输出提示词到文件，供后续处理
cat > "$OUTPUT_FILE" << EOF
# $EVENT_TYPE - $DATE

$PROMPT

---

*注意：此文件包含生成内容的提示词。实际内容可以通过以下方式生成：
1. 使用 sessions_spawn 调用子代理生成内容
2. 手动编辑此文件
3. 集成其他AI服务*
EOF

echo "✅ 提示词已生成: $OUTPUT_FILE"
