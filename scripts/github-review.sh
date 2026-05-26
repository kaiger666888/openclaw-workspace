#!/bin/bash
# GitHub 代码审查脚本
# 每天凌晨 2:00 运行，审查指定仓库的最新提交
# 报告使用中文，结果存入 Notion 代码审查目录

set -e

# 配置
REPO="zhangkaidhb/umlVisionAgent"
BRANCH="main"
DATE=$(date +"%Y-%m-%d")
DATE_CN=$(date +"%Y年%m月%d日")
TIMESTAMP=$(date '+%Y-%m-%d %H:%M')

# Notion 页面配置
NOTION_CODE_REVIEW_ROOT="32711082-af8e-8158-8e03-dc8ab98c17b5"  # 代码审查根目录
NOTION_PROJECT_PAGE="32711082-af8e-8185-9883-fdff1f18a577"      # umlVisionAgent 项目页面

# 读取 GitHub Token
if [ -z "$GITHUB_TOKEN" ]; then
  if [ -f "/home/kai/.openclaw/workspace/.github-token" ]; then
    GITHUB_TOKEN=$(cat /home/kai/.openclaw/workspace/.github-token)
  fi
  if [ -z "$GITHUB_TOKEN" ] && [ -f "$HOME/.config/gh/hosts.yml" ]; then
    GITHUB_TOKEN=$(grep -A1 'github.com' "$HOME/.config/gh/hosts.yml" | grep 'oauth_token' | awk '{print $2}' | head -1)
  fi
  if [ -z "$GITHUB_TOKEN" ] && [ -f "/home/kai/.config/gh/hosts.yml" ]; then
    GITHUB_TOKEN=$(grep -A1 'github.com' "/home/kai/.config/gh/hosts.yml" | grep 'oauth_token' | awk '{print $2}' | head -1)
  fi
fi

export GITHUB_TOKEN

echo "🔍 开始 GitHub 代码审查: $REPO ($BRANCH)"
echo "时间: $TIMESTAMP"

# 获取最近 24 小时的提交
SINCE=$(date -d '24 hours ago' --iso-8601=seconds)
echo "检查从 $SINCE 以来的提交..."

# 获取提交列表
if [ -n "$GITHUB_TOKEN" ]; then
  COMMITS=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
    "https://api.github.com/repos/$REPO/commits?sha=$BRANCH&since=$SINCE" | jq '.' 2>/dev/null || echo "[]")
else
  COMMITS=$(gh api repos/$REPO/commits?sha=$BRANCH&since=$SINCE --paginate 2>/dev/null || echo "[]")
fi
COMMIT_COUNT=$(echo "$COMMITS" | jq 'length' | tr -d '\n')

echo "发现 $COMMIT_COUNT 个新提交"

# 如果没有新提交，跳过
if [ "$COMMIT_COUNT" == "0" ]; then
  echo "✅ 没有新的提交需要审查"
  exit 0
fi

# 创建当天的审查页面
echo "创建今日审查页面: $DATE"
DAILY_PAGE=$(notion-cli page create --parent "$NOTION_PROJECT_PAGE" --title "$DATE" 2>/dev/null | grep "ID:" | awk '{print $2}')
echo "页面ID: $DAILY_PAGE"

# 生成中文审查报告
cat > /tmp/github-review.md << 'REPORT_EOF'
# 代码审查报告

REPORT_EOF

cat >> /tmp/github-review.md << REPORT_EOF

**仓库**: [$REPO](https://github.com/$REPO/tree/$BRANCH)
**分支**: $BRANCH
**审查时间**: $TIMESTAMP
**提交数量**: $COMMIT_COUNT

---

## 📊 提交概览

REPORT_EOF

# 添加每个提交的详细信息（中文）
echo "$COMMITS" | jq -r '.[] | [
  "### [\(.sha[:7])](https://github.com/'$REPO'/commit/\(.sha))",
  "**作者**: \(.commit.author.name)",
  "**时间**: \(.commit.author.date)",
  "**提交信息**: \(.commit.message)",
  ""
] | join("\n")' >> /tmp/github-review.md

# 获取代码变更统计
cat >> /tmp/github-review.md << REPORT_EOF

---

## 📈 代码变更统计

REPORT_EOF

FIRST_COMMIT=$(echo "$COMMITS" | jq -r '.[-1].sha')
LAST_COMMIT=$(echo "$COMMITS" | jq -r '.[0].sha')

if [ -n "$FIRST_COMMIT" ] && [ -n "$LAST_COMMIT" ] && [ "$FIRST_COMMIT" != "null" ] && [ "$LAST_COMMIT" != "null" ]; then
  echo "获取代码统计: $FIRST_COMMIT...$LAST_COMMIT"
  
  if [ -n "$GITHUB_TOKEN" ]; then
    STATS=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
      "https://api.github.com/repos/$REPO/compare/$FIRST_COMMIT...$LAST_COMMIT" | \
      jq -r '.files[] | "- **\(.filename)**: +\(.additions) -\(.deletions)"' 2>/dev/null || echo "")
  else
    STATS=$(gh api repos/$REPO/compare/$FIRST_COMMIT...$LAST_COMMIT --jq '.files[] | "- **\(.filename)**: +\(.additions) -\(.deletions)"' 2>/dev/null || echo "")
  fi
  
  if [ -n "$STATS" ]; then
    echo "$STATS" >> /tmp/github-review.md
  else
    echo "无法获取详细统计信息" >> /tmp/github-review.md
  fi
fi

# 添加 AI 分析建议（中文）
cat >> /tmp/github-review.md << 'REPORT_EOF'

---

## 💡 改进建议

基于以上提交，建议关注以下几点：

### 代码质量
- 检查新增代码的测试覆盖率
- 确保错误处理完善
- 验证代码风格一致性

### 性能优化
- 审查是否有性能瓶颈
- 检查资源使用效率
- 评估算法复杂度

### 安全性
- 验证输入验证和数据清理
- 检查敏感信息处理
- 确认权限控制合理

### 可维护性
- 评估代码复杂度
- 检查文档和注释
- 确认模块化设计

---

*本报告由 OpenClaw 自动生成*
REPORT_EOF

# 写入 Notion
echo "写入 Notion 页面..."
/home/kai/.openclaw/workspace/scripts/lib/notion-append-blocks.sh "$DAILY_PAGE" /tmp/github-review.md

# 保存本地备份
REPORT_FILE="/home/kai/.openclaw/workspace/memory/github-review-$DATE.md"
cp /tmp/github-review.md "$REPORT_FILE"

echo "✅ 审查报告已生成: $REPORT_FILE"
echo "✅ Notion 页面: https://www.notion.so/$DAILY_PAGE"

# 清理临时文件
rm -f /tmp/github-review.md

# 输出报告内容
cat "$REPORT_FILE"
