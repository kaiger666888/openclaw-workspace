# AIGC 前沿总结生成 Prompt

## 任务目标

每日推送 AIGC 前沿资讯总结到 Notion，追踪最新 AI 产品、技术突破和行业动态。

## 内容要求

### 1. 信息来源

**主要来源**（优先级排序）：
1. The Verge AI: https://www.theverge.com/ai-artificial-intelligence
2. TechCrunch AI: https://techcrunch.com/category/artificial-intelligence/
3. MIT Technology Review: https://www.technologyreview.com/topic/artificial-intelligence/
4. OpenAI Blog: https://openai.com/blog/
5. Anthropic Blog: https://www.anthropic.com/news/
6. Google AI Blog: https://blog.google/technology/ai/
7. Meta AI Blog: https://ai.meta.com/blog/

### 2. 内容结构

```markdown
# AIGC前沿总结 - YYYY年MM月DD日

> 一句话总结今日重点

## 🔥 头条新闻
- [新闻标题](链接)
  - 关键信息
  - 影响分析

## 💡 技术突破
- [技术名称]
  - 突破点
  - 应用前景

## 🏢 产品发布
- [产品名称]
  - 核心功能
  - 目标用户

## 💰 商业动态
- 融资/收购/合作
  - 金额/条款
  - 市场影响

## 🎯 趋势观察
- 行业趋势
- 技术方向
- 市场预测

## 📊 数据快览
- 关键数字
- 增长数据
- 市场份额

---

**数据来源**: [来源列表] | **生成时间**: YYYY-MM-DD HH:MM
```

### 3. 质量标准

- ✅ **时效性**：24小时内新闻
- ✅ **准确性**：信息来源可靠
- ✅ **实用性**：对读者有价值
- ✅ **简洁性**：突出重点，- ✅ **多样性**：覆盖多个领域

### 4. 搜索策略

**优先使用 web_search（中文关键词）**：
```python
web_search(query="AI人工智能最新新闻 2026", search_lang="zh-hans", count=10)
web_search(query="AIGC大模型前沿动态", search_lang="zh-hans", count=10)
```

**如果 web_search 失败，使用 web_fetch 降级方案**：
```python
# 抓取权威网站
web_fetch("https://www.theverge.com/ai-artificial-intelligence")
web_fetch("https://techcrunch.com/category/artificial-intelligence/")
web_fetch("https://openai.com/blog/")
```

**降级优先级**：
1. web_search (首选)
2. web_fetch 抓取固定网站
3. 基于经验生成并标注来源

**搜索限制**：
- web_search: ≤ 3 次
- web_fetch: ≤ 5 次
- 如果都失败： 创建基础框架页面并标注"待补充"

### 5. 内容要求

- 每条信息必须有**来源链接**
- 使用蓝色链接格式：`[来源名称](URL)`
- 标注信息时间（如"2小时前"）
- 区分事实和观点
- 重要信息用 **粗体** 或 emoji 强调

## Notion 格式要求

使用 `markdown-to-notion.py` 转换：
```bash
/home/kai/.openclaw/workspace/scripts/lib/markdown-to-notion.py content.md > blocks.json
```

格式检查：
- [ ] 顶部有 callout 摘要
- [ ] 使用 heading_2 作为分类标题
- [ ] 链接格式：`[来源名称](URL)`
- [ ] 使用 divider 分隔各部分
- [ ] 底部有数据来源说明

## 执行流程

1. 搜索 AIGC 最新资讯（3-5 个来源）
2. 筛选最重要和最新信息（5-10 条）
3. 生成 Markdown 内容
4. 转换为 Notion 格式
5. 追加到 Notion 页面
6. 记录到 memory/YYYY-MM-DD.md

## 注意事项

- 所有内容必须用中文输出（技术术语可保留英文原名）
- 搜索优先使用中文关键词
- 关注实际价值，- 避免过度炒作的内容
- 标注每条信息的来源
- 如果无法获取足够信息，创建基础框架页面

---

**创建时间**: 2026-03-17
**适用任务**: daily-aigc
