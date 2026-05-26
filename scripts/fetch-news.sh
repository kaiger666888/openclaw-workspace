#!/bin/bash
# 从RSS源获取每日新闻 v2
# 支持多个中文科技新闻源

set -e

# 配置
DATE=$(date +"%Y年%m月%d日")
TIMESTAMP=$(date '+%Y-%m-%d %H:%M')
TEMP_DIR="/tmp/news-fetcher-$$"
NEWS_FILE="$TEMP_DIR/all-news.txt"

# 创建临时目录
mkdir -p "$TEMP_DIR"

# 清理函数
cleanup() {
  rm -rf "$TEMP_DIR"
}
trap cleanup EXIT

# RSS源列表（中文科技新闻）
declare -A RSS_SOURCES
RSS_SOURCES["36氪"]="https://36kr.com/feed"
RSS_SOURCES["少数派"]="https://sspai.com/feed"
RSS_SOURCES["虎嗅"]="https://www.huxiu.com/rss/0.xml"
# 这些源可能不稳定，暂时注释
# RSS_SOURCES["InfoQ"]="https://www.infoq.cn/feed"
# RSS_SOURCES["雷锋网"]="https://www.leiphone.com/feed"
# RSS_SOURCES["极客公园"]="https://www.geekpark.net/rss"

# 解析单个RSS源
parse_rss() {
  local name="$1"
  local url="$2"
  local output="$3"

  echo "📡 获取 $name..." >&2

  local temp_xml="$TEMP_DIR/${name}.xml"

  if ! curl -s --connect-timeout 10 --max-time 30 "$url" -o "$temp_xml" 2>/dev/null; then
    echo "⚠️  $name 获取失败" >&2
    return 1
  fi

  # 使用Python解析RSS
  python3 -c "
import xml.etree.ElementTree as ET
import sys
from html.parser import HTMLParser
import re

class HTMLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.text = []
    def handle_data(self, d):
        self.text.append(d)
    def get_data(self):
        return ''.join(self.text)

def strip_html(html):
    if not html:
        return ''
    s = HTMLStripper()
    try:
        s.feed(html)
        return s.get_data()
    except:
        return html

try:
    tree = ET.parse('$temp_xml')
    root = tree.getroot()

    # 处理RSS格式
    items = []
    
    # 尝试RSS 2.0
    if root.tag == 'rss':
        channel = root.find('.//channel')
        if channel is not None:
            items = channel.findall('.//item')
    # 尝试Atom
    elif '{http://www.w3.org/2005/Atom}' in root.tag or 'feed' in root.tag:
        items = root.findall('.//{http://www.w3.org/2005/Atom}entry') or root.findall('.//entry')
    
    # 提取新闻（最多10条）
    count = 0
    for item in items[:10]:
        try:
            # 获取标题
            title_elem = item.find('title') or item.find('{http://www.w3.org/2005/Atom}title')
            title = ''
            if title_elem is not None and title_elem.text:
                title = title_elem.text
                # 清理CDATA和HTML
                title = re.sub(r'<!\[CDATA\[(.*?)\]\]>', r'\1', title)
                title = strip_html(title)
                title = title.strip()
            
            # 获取链接
            link_elem = item.find('link') or item.find('{http://www.w3.org/2005/Atom}link')
            link = ''
            if link_elem is not None:
                if link_elem.text:
                    link = link_elem.text
                elif link_elem.get('href'):
                    link = link_elem.get('href')
                elif link_elem.get('{http://www.w3.org/2005/Atom}href'):
                    link = link_elem.get('{http://www.w3.org/2005/Atom}href')
            
            if title and link and len(title) > 5:
                print(f'{title}|{link}')
                count += 1
        except Exception as e:
            continue
    
    sys.stderr.write(f'✅ $name: {count} 条新闻\\n')

except Exception as e:
    sys.stderr.write(f'❌ 解析 $name 失败: {e}\\n')
    sys.exit(1)
" >> "$output" 2>&1

  rm -f "$temp_xml"
  return 0
}

# 主逻辑
echo "📰 开始获取每日新闻..."
echo ""

# 获取所有新闻
> "$NEWS_FILE"

for name in "${!RSS_SOURCES[@]}"; do
  url="${RSS_SOURCES[$name]}"
  parse_rss "$name" "$url" "$NEWS_FILE"
done

# 提取唯一新闻
TEMP_OUTPUT="$TEMP_DIR/categorized.md"
> "$TEMP_OUTPUT"

# 分类新闻
AI_NEWS=""
DEV_NEWS=""
TECH_NEWS=""
FINANCE_NEWS=""

while IFS='|' read -r title link; do
  [ -z "$title" ] && continue
  
  # 去重
  if grep -qF "$title" "$TEMP_OUTPUT" 2>/dev/null; then
    continue
  fi
  
  # 分类
  category="TECH"
  if echo "$title" | grep -qiE "AI|人工智能|大模型|GPT|Claude|ChatGPT|机器学习|深度学习|算法|神经网络|智能|自动化|OpenAI|百度文心|阿里通义"; then
    category="AI"
  elif echo "$title" | grep -qiE "开发|编程|代码|框架|API|SDK|开源|GitHub|程序员|前端|后端|数据库|云原生|Docker|Kubernetes|React|Vue|Python|Java"; then
    category="DEV"
  elif echo "$title" | grep -qiE "融资|投资|创业|公司|上市|财报|估值|独角兽|IPO|并购|基金|创投|天使|A轮|B轮"; then
    category="FINANCE"
  fi
  
  # 格式化
  case "$category" in
    AI)
      AI_NEWS="$AI_NEWS- $title\n"
      ;;
    DEV)
      DEV_NEWS="$DEV_NEWS- $title\n"
      ;;
    FINANCE)
      FINANCE_NEWS="$FINANCE_NEWS- $title\n"
      ;;
    *)
      TECH_NEWS="$TECH_NEWS- $title\n"
      ;;
  esac
  
  # 记录已处理
  echo "$title" >> "$TEMP_OUTPUT"
done < "$NEWS_FILE"

# 输出markdown格式的新闻
cat << EOF
# 每日科技新闻 - $DATE

> 自动生成于 $TIMESTAMP

---

## 🔥 AI & 人工智能

${AI_NEWS:-*暂无相关新闻*}

## 🛠️ 开发工具 & 技术

${DEV_NEWS:-*暂无相关新闻*}

## 💰 创业 & 投资

${FINANCE_NEWS:-*暂无相关新闻*}

## 🚀 科技动态

${TECH_NEWS:-*暂无相关新闻*}

---

_数据来源: 36氪、少数派、InfoQ、雷锋网、虎嗅_
EOF

echo ""
echo "✅ 新闻获取完成！"
