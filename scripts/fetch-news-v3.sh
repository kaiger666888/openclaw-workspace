#!/bin/bash
# 从RSS源获取每日新闻 v3 - 简化可靠版本

set -e

DATE=$(date +"%Y年%m月%d日")
TIMESTAMP=$(date '+%Y-%m-%d %H:%M')
TEMP_DIR="/tmp/news-$$"

mkdir -p "$TEMP_DIR"
trap "rm -rf $TEMP_DIR" EXIT

echo "📰 获取每日新闻..."

# 定义新闻源
fetch_36kr() {
  echo "📡 获取36氪..."
  curl -s --connect-timeout 15 "https://36kr.com/feed" -o "$TEMP_DIR/36kr.xml" 2>/dev/null || return 1

  # 简单XML解析
  grep -oP '<title>\K[^<]*(?=<\/title>)' "$TEMP_DIR/36kr.xml" | \
    grep -v '^36氪$' | \
    sed 's/<!\[CDATA\[//g' | sed 's/]]>//g' | \
    head -15 > "$TEMP_DIR/36kr-titles.txt"

  grep -oP '<link/>\K[^>]*' "$TEMP_DIR/36kr.xml" | head -15 > "$TEMP_DIR/36kr-links.txt" || \
    grep -oP '<link>\K[^<]*(?=<\/link>)' "$TEMP_DIR/36kr.xml" | head -15 > "$TEMP_DIR/36kr-links.txt"

  paste "$TEMP_DIR/36kr-titles.txt" "$TEMP_DIR/36kr-links.txt" | sed 's/^/📰 /' | sed 's/\t/ | /'
}

fetch_sspai() {
  echo "📡 获取少数派..."
  curl -s --connect-timeout 15 "https://sspai.com/feed" -o "$TEMP_DIR/sspai.xml" 2>/dev/null || return 1

  grep -oP '<title>\K[^<]*(?=<\/title>)' "$TEMP_DIR/sspai.xml" | \
    grep -v '^少数派$' | \
    sed 's/<!\[CDATA\[//g' | sed 's/]]>//g' | \
    head -10 > "$TEMP_DIR/sspai-titles.txt"

  grep -oP '<link>\K[^<]*(?=<\/link>)' "$TEMP_DIR/sspai.xml" | head -10 > "$TEMP_DIR/sspai-links.txt"

  paste "$TEMP_DIR/sspai-titles.txt" "$TEMP_DIR/sspai-links.txt" | sed 's/^/📰 /' | sed 's/\t/ | /'
}

fetch_huxiu() {
  echo "📡 获取虎嗅..."
  curl -s --connect-timeout 15 "https://www.huxiu.com/rss/0.xml" -o "$TEMP_DIR/huxiu.xml" 2>/dev/null || return 1

  grep -oP '<title>\K[^<]*(?=<\/title>)' "$TEMP_DIR/huxiu.xml" | \
    grep -v '^虎嗅网$' | \
    sed 's/<!\[CDATA\[//g' | sed 's/]]>//g' | \
    head -10 > "$TEMP_DIR/huxiu-titles.txt"

  grep -oP '<link>\K[^<]*(?=<\/link>)' "$TEMP_DIR/huxiu.xml" | head -10 > "$TEMP_DIR/huxiu-links.txt"

  paste "$TEMP_DIR/huxiu-titles.txt" "$TEMP_DIR/huxiu-links.txt" | sed 's/^/📰 /' | sed 's/\t/ | /'
}

# 获取所有新闻
ALL_NEWS=""
ALL_NEWS="$ALL_NEWS$(fetch_36kr 2>/dev/null || echo "")"$'\n\n'
ALL_NEWS="$ALL_NEWS$(fetch_sspai 2>/dev/null || echo "")"$'\n\n'
ALL_NEWS="$ALL_NEWS$(fetch_huxiu 2>/dev/null || echo "")"$'\n\n'

# 如果没有新闻，使用备用方案
if [ -z "$(echo "$ALL_NEWS" | grep '📰')" ]; then
  echo "⚠️  RSS获取失败，使用备用方案..."
  
  # 备用：从网页抓取
  curl -s --connect-timeout 15 "https://36kr.com" -o "$TEMP_DIR/36kr.html" 2>/dev/null
  
  # 简单的HTML解析
  grep -oP '<h3[^>]*>\K[^<]*(?=<\/h3>)' "$TEMP_DIR/36kr.html" 2>/dev/null | \
    grep -v '^$' | head -20 | sed 's/^/📰 /' | sed 's/$/ | https://36kr.com/'
fi

# 分类输出
cat << EOF
# 每日科技新闻 - $DATE

> 自动生成于 $TIMESTAMP

---

## 🔥 AI & 人工智能

$(echo "$ALL_NEWS" | grep -iE "AI|人工智能|大模型|GPT|Claude|ChatGPT|机器学习|深度学习|算法|神经网络|智能|自动化|百度|阿里|腾讯|字节" | head -10 || echo "*暂无相关新闻*")

## 🛠️ 开发工具 & 技术

$(echo "$ALL_NEWS" | grep -iE "开发|编程|代码|框架|API|SDK|开源|GitHub|程序员|前端|后端|数据库|云|Docker|Kubernetes|React|Vue|Python|Java|程序员|开发者" | head -10 || echo "*暂无相关新闻*")

## 💰 创业 & 投资

$(echo "$ALL_NEWS" | grep -iE "融资|投资|创业|公司|上市|财报|估值|独角兽|IPO|并购|基金|创投|天使|A轮|B轮|融资|亿元|千万|美元|人民币" | head -10 || echo "*暂无相关新闻*")

## 🚀 科技动态

$(echo "$ALL_NEWS" | grep -viE "AI|人工智能|大模型|GPT|Claude|ChatGPT|机器学习|深度学习|算法|神经网络|智能|自动化|百度|阿里|腾讯|字节|开发|编程|代码|框架|API|SDK|开源|GitHub|程序员|前端|后端|数据库|云|Docker|Kubernetes|React|Vue|Python|Java|程序员|开发者|融资|投资|创业|公司|上市|财报|估值|独角兽|IPO|并购|基金|创投|天使|A轮|B轮" | head -15 || echo "*暂无相关新闻*")

---

_数据来源: 36氪、少数派、虎嗅_
EOF

echo ""
echo "✅ 完成！"
