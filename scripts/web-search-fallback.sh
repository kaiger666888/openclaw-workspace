#!/bin/bash
# Web 搜索降级方案 - 集成 Agent-Reach
# 优先级: Brave API > Exa AI > 秘塔AI > Jina Reader > Bing CN

QUERY="$1"
COUNT="${2:-5}"
OUTPUT_FILE="${3:-/tmp/search-results.txt}"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

if [ -z "$QUERY" ]; then
    echo "用法: $0 <搜索关键词> [结果数量] [输出文件]"
    echo "示例: $0 'AI trends 2026' 5 /tmp/results.txt"
    echo ""
    echo "搜索引擎优先级:"
    echo "  1. Brave Search API (国际，需代理)"
    echo "  2. Exa AI 语义搜索 (MCP, 免费)"
    echo "  3. 秘塔AI搜索 (metaso.cn, 无广告)"
    echo "  4. Jina Reader + Kagi (网页抓取)"
    echo "  5. Bing CN (cn.bing.com, 国内直连)"
    exit 1
fi

# 清空输出文件
> "$OUTPUT_FILE"

echo -e "${BLUE}🔍 搜索: $QUERY${NC}" | tee -a "$OUTPUT_FILE"
echo "" | tee -a "$OUTPUT_FILE"

# 方案1: Brave API (首选，需代理)
echo -e "${YELLOW}[1/5] 尝试 Brave Search API...${NC}" | tee -a "$OUTPUT_FILE"
BRAVE_RESULT=$(curl -s --connect-timeout 5 \
    -H "Accept: application/json" \
    -H "X-Subscription-Token: ${BRAVE_API_KEY}" \
    "https://api.search.brave.com/res/v1/web/search?q=$(echo "$QUERY" | sed 's/ /+/g')&count=$COUNT" 2>/dev/null)

if [ $? -eq 0 ] && [ -n "$BRAVE_RESULT" ] && echo "$BRAVE_RESULT" | jq -e ".web.results" >/dev/null 2>&1; then
    echo -e "${GREEN}✓ Brave API 可用${NC}" | tee -a "$OUTPUT_FILE"
    echo "" | tee -a "$OUTPUT_FILE"
    
    echo "$BRAVE_RESULT" | jq -r ".web.results[:$COUNT][] | \"\n标题: \(.title)\n链接: \(.url)\n描述: \(.description // "无描述")\n\"" 2>/dev/null | tee -a "$OUTPUT_FILE"
    echo "来源: Brave Search API" >> "$OUTPUT_FILE"
    exit 0
fi

echo -e "${RED}✗ Brave API 不可用${NC}" | tee -a "$OUTPUT_FILE"
echo "" | tee -a "$OUTPUT_FILE"

# 方案2: Exa AI 语义搜索 (通过 mcporter)
echo -e "${YELLOW}[2/5] 尝试 Exa AI 语义搜索...${NC}" | tee -a "$OUTPUT_FILE"
EXA_RESULT=$(mcporter call exa.web_search_exa "{\"query\": \"$QUERY\", \"numResults\": $COUNT}" 2>/dev/null)

if [ $? -eq 0 ] && [ -n "$EXA_RESULT" ] && ! echo "$EXA_RESULT" | grep -q "error\|Error"; then
    echo -e "${GREEN}✓ Exa AI 可用${NC}" | tee -a "$OUTPUT_FILE"
    echo "" | tee -a "$OUTPUT_FILE"
    echo "$EXA_RESULT" | tee -a "$OUTPUT_FILE"
    echo "来源: Exa AI (via mcporter)" >> "$OUTPUT_FILE"
    exit 0
fi

echo -e "${RED}✗ Exa AI 不可用${NC}" | tee -a "$OUTPUT_FILE"
echo "" | tee -a "$OUTPUT_FILE"

# 方案3: 秘塔AI搜索 (国产 AI 搜索，无广告)
echo -e "${YELLOW}[3/5] 尝试秘塔AI搜索 (metaso.cn)...${NC}" | tee -a "$OUTPUT_FILE"
METASO_URL="https://metaso.cn/search?q=$(echo "$QUERY" | sed 's/ /%20/g')"

METASO_RESULT=$(curl -s --connect-timeout 10 --noproxy "*" \
    -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36" \
    -H "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8" \
    -H "Accept-Language: zh-CN,zh;q=0.9,en;q=0.8" \
    "$METASO_URL" 2>/dev/null)

if [ $? -eq 0 ] && [ -n "$METASO_RESULT" ] && echo "$METASO_RESULT" | grep -q "search-result\|result-item\|metaso"; then
    echo -e "${GREEN}✓ 秘塔AI可用${NC}" | tee -a "$OUTPUT_FILE"
    echo "" | tee -a "$OUTPUT_FILE"
    
    # 提取搜索结果（简化版）
    echo "$METASO_RESULT" | grep -oP '(?<=<title>).*?(?=</title>)' | head -1 | while read -r title; do
        if [ -n "$title" ] && [ "$title" != "秘塔AI搜索" ]; then
            echo "标题: $title" >> "$OUTPUT_FILE"
        fi
    done
    
    # 尝试提取 JSON 数据
    if echo "$METASO_RESULT" | grep -q "__NEXT_DATA__\|window\.__INITIAL_STATE__"; then
        echo "💡 秘塔AI返回动态内容，建议访问: $METASO_URL" >> "$OUTPUT_FILE"
    fi
    
    echo "" >> "$OUTPUT_FILE"
    echo "来源: 秘塔AI搜索" >> "$OUTPUT_FILE"
    echo "链接: $METASO_URL" >> "$OUTPUT_FILE"
    cat "$OUTPUT_FILE" | tail -n +3
    exit 0
fi

echo -e "${RED}✗ 秘塔AI不可用${NC}" | tee -a "$OUTPUT_FILE"
echo "" | tee -a "$OUTPUT_FILE"

# 方案4: Jina Reader (网页抓取，配合搜索引擎)
echo -e "${YELLOW}[4/5] 尝试 Jina Reader (r.jina.ai)...${NC}" | tee -a "$OUTPUT_FILE"
# 使用 Kagi 的搜索 API 或直接抓取搜索结果页
JINA_URL="https://r.jina.ai/https://search.brave.com/search?q=$(echo "$QUERY" | sed 's/ /+/g')"

JINA_RESULT=$(curl -s --connect-timeout 10 --noproxy "*" \
    -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" \
    "$JINA_URL" 2>/dev/null)

if [ $? -eq 0 ] && [ -n "$JINA_RESULT" ] && [ ${#JINA_RESULT} -gt 200 ]; then
    echo -e "${GREEN}✓ Jina Reader 可用${NC}" | tee -a "$OUTPUT_FILE"
    echo "" | tee -a "$OUTPUT_FILE"
    
    # 提取前 N 个结果
    echo "$JINA_RESULT" | head -$((COUNT * 5)) | tee -a "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    echo "来源: Jina Reader + Brave Search" >> "$OUTPUT_FILE"
    exit 0
fi

echo -e "${RED}✗ Jina Reader 不可用${NC}" | tee -a "$OUTPUT_FILE"
echo "" | tee -a "$OUTPUT_FILE"

# 方案5: Bing CN (国内直连)
echo -e "${YELLOW}[5/5] 尝试 Bing CN 搜索...${NC}" | tee -a "$OUTPUT_FILE"
BING_URL="https://cn.bing.com/search?q=$(echo "$QUERY" | sed 's/ /%20/g')&count=$COUNT"

BING_RESULT=$(curl -s --connect-timeout 10 --noproxy "*" \
    -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36" \
    -H "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8" \
    -H "Accept-Language: zh-CN,zh;q=0.9,en;q=0.8" \
    "$BING_URL" 2>/dev/null)

if [ $? -eq 0 ] && [ -n "$BING_RESULT" ] && echo "$BING_RESULT" | grep -q "b_algo\|results"; then
    echo -e "${GREEN}✓ Bing CN 可用${NC}" | tee -a "$OUTPUT_FILE"
    echo "" | tee -a "$OUTPUT_FILE"
    
    # 提取搜索结果
    echo "$BING_RESULT" | grep -oP '(?<=<li class="b_algo">).*?(?=</li>)' | head -$COUNT | while read -r line; do
        TITLE=$(echo "$line" | grep -oP '(?<=<h2>).*?(?=</h2>)' | sed 's/<[^>]*>//g' | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
        URL=$(echo "$line" | grep -oP '(?<=<a[^>]*href=")[^"]*' | head -1)
        DESC=$(echo "$line" | grep -oP '(?<=<p>).*?(?=</p>)' | sed 's/<[^>]*>//g' | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
        
        if [ -n "$TITLE" ]; then
            echo "" >> "$OUTPUT_FILE"
            echo "标题: $TITLE" >> "$OUTPUT_FILE"
            [ -n "$URL" ] && echo "链接: $URL" >> "$OUTPUT_FILE"
            [ -n "$DESC" ] && echo "描述: $DESC" >> "$OUTPUT_FILE"
            echo "" >> "$OUTPUT_FILE"
        fi
    done
    
    cat "$OUTPUT_FILE" | tail -n +3
    echo "来源: Bing CN" >> "$OUTPUT_FILE"
    exit 0
fi

echo -e "${RED}✗ Bing CN 不可用${NC}" | tee -a "$OUTPUT_FILE"
echo "" | tee -a "$OUTPUT_FILE"

# 所有方案都失败
echo -e "${RED}❌ 所有搜索方案都失败${NC}" | tee -a "$OUTPUT_FILE"
echo "" | tee -a "$OUTPUT_FILE"
echo "建议：" | tee -a "$OUTPUT_FILE"
echo "1. 检查网络连接" | tee -a "$OUTPUT_FILE"
echo "2. 配置代理以使用 Brave Search API" | tee -a "$OUTPUT_FILE"
echo "3. 稍后重试" | tee -a "$OUTPUT_FILE"

exit 1
