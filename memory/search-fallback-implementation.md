# 搜索降级方案实现

**时间**: 2026-03-17 14:25
**目的**: 当代理不可用时，自动切换到国内可访问的搜索方式

---

## 实现方案

### 降级优先级

1. **Brave Search API** (需要代理)
   - URL: `https://api.search.brave.com/res/v1/web/search`
   - 需要: API Key + 代理
   - 优点: 高质量结果，JSON 格式
   - 缺点: 需要代理

2. **DuckDuckGo API** (可能需要代理)
   - URL: `https://api.duckduckgo.com/?format=json`
   - 需要: 无需 API Key
   - 优点: 隐私友好，简单
   - 缺点: 结果有限，可能被墙

3. **百度搜索** (国内直连)
   - URL: `https://www.baidu.com/s?wd=xxx`
   - 需要: 无
   - 优点: 国内可直接访问
   - 缺点: 需要解析 HTML，质量一般

4. **Bing 中国版** (国内直连)
   - URL: `https://cn.bing.com/search?q=xxx`
   - 需要: 无
   - 优点: 国内可直接访问，质量较好
   - 缺点: 需要解析 HTML

---

## 已创建的工具

### 1. web-search-fallback.sh

**路径**: `/home/kai/.openclaw/workspace/scripts/web-search-fallback.sh`

**用法**:
```bash
./web-search-fallback.sh "搜索关键词" [结果数量] [输出文件]

# 示例
./web-search-fallback.sh "AI trends 2026" 5 /tmp/results.txt
```

**功能**:
- 自动尝试 3 种搜索方式
- 降级到可用的方案
- 输出 JSON 或纯文本格式
- 记录搜索来源

### 2. proxy-manager.sh

**路径**: `/home/kai/.openclaw/workspace/scripts/proxy-manager.sh`

**用法**:
```bash
./proxy-manager.sh {status|test|disable|enable|restart|switch|update}
```

**功能**:
- 查看代理状态
- 测试代理连接
- 切换代理节点
- 更新订阅

---

## 测试结果

### 测试 1: Brave API
```
✗ Brave API 不可用
原因: 代理服务器 connection refused
```

### 测试 2: DuckDuckGo
```
✗ DuckDuckGo 不可用或无结果
原因: 可能被墙或网络问题
```

### 测试 3: 百度搜索
```
✓ 百度可用
状态: 成功获取搜索结果
来源: 百度搜索
```

---

## 在定时任务中使用

### 方案 A: 修改任务脚本

在需要搜索的定时任务中，使用降级脚本替代 `web_search`:

```bash
# 旧方法（依赖代理）
RESULTS=$(web_search "AI news" 5)

# 新方法（自动降级）
/home/kai/.openclaw/workspace/scripts/web-search-fallback.sh "AI news" 5 /tmp/search-results.txt
RESULTS=$(cat /tmp/search-results.txt)
```

### 方案 B: 使用 web_fetch 抓取固定网站

对于特定主题的搜索，可以直接抓取相关网站：

```bash
# 技术新闻
web_fetch "https://www.theverge.com/ai-artificial-intelligence"

# GitHub Trending
web_fetch "https://github.com/trending"

# Hacker News
web_fetch "https://news.ycombinator.com/"
```

### 方案 C: 混合方案

```bash
# 1. 尝试搜索 API
SEARCH_RESULT=$(web-search-fallback.sh "关键词" 5 /tmp/results.txt)

# 2. 如果失败，使用 web_fetch 抓取固定网站
if [ $? -ne 0 ]; then
    web_fetch "https://example.com/news" > /tmp/fallback-results.txt
fi

# 3. 合并结果或使用缓存
```

---

## 待改进

### 优先级 P1

1. **改进 HTML 解析**
   - 百度和 Bing 的 HTML 解析不够稳定
   - 考虑使用更可靠的解析方法

2. **添加缓存机制**
   - 缓存搜索结果
   - 减少对外部 API 的依赖

3. **添加更多搜索源**
   - 搜狗搜索
   - 360 搜索
   - RSS 源

### 优先级 P2

1. **智能路由**
   - 根据查询内容选择最佳搜索源
   - 技术内容优先用 Bing
   - 中文内容优先用百度

2. **结果聚合**
   - 同时查询多个源
   - 去重和排序
   - 提高结果质量

---

## 当前状态

✅ **降级方案已实现**
- 3 层降级机制
- 自动选择可用方案
- 独立的代理管理工具

⚠️ **待优化**
- HTML 解析稳定性
- 搜索结果质量
- 错误处理

📋 **待集成**
- 修改定时任务使用降级脚本
- 添加到 HEARTBEAT 检查
- 实现缓存机制

---

**创建时间**: 2026-03-17 14:25
**状态**: ✅ 基础版本可用
