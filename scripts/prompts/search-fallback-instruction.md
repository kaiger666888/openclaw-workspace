# 搜索降级指令

**重要**：当 web_search 工具不可用时，请使用以下降级方案：

## 降级策略

### 方案1：使用 web_fetch 抓取固定网站（推荐）

如果搜索功能不可用，直接抓取相关网站获取信息：

**AI/技术类**：
- The Verge AI: https://www.theverge.com/ai-artificial-intelligence
- TechCrunch AI: https://techcrunch.com/category/artificial-intelligence/
- MIT Technology Review: https://www.technologyreview.com/topic/artificial-intelligence/

**GitHub Trending**：
- GitHub Trending: https://github.com/trending
- GitHub Trending (Python): https://github.com/trending/python
- GitHub Explore: https://github.com/explore

**新闻类**：
- Hacker News: https://news.ycombinator.com/
- Reddit r/technology: https://www.reddit.com/r/technology/
- Product Hunt: https://www.producthunt.com/

**技术博客**：
- GitHub Blog: https://github.blog/
- OpenAI Blog: https://openai.com/blog/
- Anthropic Blog: https://www.anthropic.com/news/

### 方案2：使用本地知识库

如果网络完全不可用，使用本地知识：
```bash
# 搜索本地记忆
grep -r "关键词" ~/.openclaw/workspace/memory/*.md

# 搜索历史数据
cat ~/.openclaw/workspace/memory/YYYY-MM-DD.md
```

### 方案3：基于经验和常识生成

如果外部信息完全不可用：
- 基于已有知识和经验生成内容
- 标注"基于个人经验/常识"
- 避免编造具体数据或事实

## 执行优先级

1. **尝试 web_search** - 如果可用
2. **降级到 web_fetch** - 抓取相关网站
3. **使用本地知识库** - 如果网络完全不可用
4. **基于经验生成** - 最后手段

## 内容标注

当使用降级方案时，请在内容中标注：
```
**数据来源**: [来源说明]
- 如果是 web_fetch: "来源: [网站名称] ([日期])"
- 如果是本地知识: "来源: 本地知识库"
- 如果是个人经验: "来源: 个人经验/常识"
```

## 质量标准

即使使用降级方案，也要保证：
- ✅ 内容准确性
- ✅ 实用价值
- ✅ 逻辑清晰
- ✅ 标注来源

## 错误处理

如果所有方案都失败：
1. 创建基础框架页面
2. 添加"待补充内容"标记
3. 记录失败原因到 memory/YYYY-MM-DD.md
4. 不要生成低质量或虚构内容

---

**创建时间**: 2026-03-17
**状态**: 降级方案指令
