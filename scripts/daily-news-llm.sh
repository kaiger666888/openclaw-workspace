#!/bin/bash
# 每日新闻任务 - 使用LLM搜索能力
set -e

DATE=$(date +"%Y年%m月%d日")
NOTION_CLI="/home/kai/.local/bin/notion-cli"

# 1. 创建Notion页面
CONTENT="自动生成于 $(date '+%Y-%m-%d %H:%M')"$'\n\n$'\n"---"$'\n\n$'\n"*正在获取今日科技新闻...*"$'\n\n$'\n"_提示：此任务由子代理使用搜索能力自动生成_"

PAGE_ID=$($NOTION_CLI page create \
  --parent "2f811082-af8e-8186-af95-e126966aead6" \
  --title "每日新闻 - $DATE" \
  --content "$CONTENT" 2>&1 | grep -oP '(?<=ID: )[0-9a-f-]+' || echo "")

if [ -z "$PAGE_ID" ]; then
  echo "❌ 页面创建失败"
  exit 1
fi

echo "✅ 页面创建成功: $PAGE_ID"
echo "PAGE_ID:$PAGE_ID"

# 2. 输出指令让子代理执行
cat << 'INSTRUCTIONS'

请执行以下操作：

1. **搜索今日科技新闻**（重点关注今天，2026年2月11日的新闻）
   - AI/大模型动态
   - 开发工具更新
   - 科技公司动态
   - 创投资讯

2. **整理成markdown格式**：
   - 按主题分类（AI新闻、开发工具、创业投资、科技动态）
   - 每条新闻1-2句话概括
   - 包含来源链接

3. **追加到Notion页面**：
   使用命令：
   ```bash
   unset NODE_OPTIONS && /home/kai/.local/bin/notion-cli page append --content "你的新闻内容" $PAGE_ID
   ```

注意：
- 优先搜索今天的新闻
- 如果搜索功能不可用，可以基于已知信息整理近期科技趋势
- 使用markdown格式，条理清晰
INSTRUCTIONS
