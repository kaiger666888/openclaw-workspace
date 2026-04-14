# GitHub Trending 生成 Prompt

## 任务目标

每日推送 GitHub Trending 项目总结到 Notion，
追踪最热门的开源项目和技术趋势。

## 内容要求

### 1. 信息来源

**主要来源**：
1. GitHub Trending: https://github.com/trending
2. GitHub Trending (Python): https://github.com/trending/python
3. GitHub Trending (JavaScript): https://github.com/trending/javascript
4. GitHub Explore: https://github.com/explore
5. Hacker News: https://news.ycombinator.com/

### 2. 内容结构

```markdown
# GitHub Trending - YYYY年MM月DD日

> 今日最热门的开源项目

## 🔥 最热项目

### 1. [项目名称](GitHub链接)
- **语言**: Python
- **今日增长**: +1,234 ⭐
- **简介**: 项目简介
- **亮点**: 核心功能
- **适合人群**: 谁会感兴趣

## 💡 技术栈分布

### Python
- 项目1: [名称](链接) - 简介
- 项目2: [名称](链接) - 简介

### JavaScript/TypeScript
- 项目1: [名称](链接) - 简介
- 项目2: [名称](链接) - 简介

### Rust/Go
- 项目1: [名称](链接) - 简介
- 项目2: [名称](链接) - 简介

## 🎯 趋势观察

- **热门领域**: AI/ML、Web3、DevOps
- **新兴技术**: [技术名称]
- **语言趋势**: Python 稳居第一
- **应用方向**: [趋势]

## 📊 数据统计

- 总项目数: X 个
- 新项目: Y 个
- 持续热门: Z 个

---

**数据来源**: GitHub Trending | **生成时间**: YYYY-MM-DD HH:MM
```

### 3. 搜索策略

**优先使用 web_search**：
```python
web_search(query="GitHub trending today", count=5)
web_search(query="popular open source projects", count=5)
```

**如果 web_search 失败，使用 web_fetch 降级方案**：
```python
# 直接抓取 GitHub Trending
web_fetch("https://github.com/trending")
web_fetch("https://github.com/trending/python")
web_fetch("https://github.com/trending/javascript")
```

**降级优先级**：
1. web_search (首选)
2. web_fetch 抓取 GitHub Trending
3. 基于历史数据或经验生成

**搜索限制**：
- web_search: ≤ 2 次
- web_fetch: ≤ 3 次
- 如果都失败: 基于经验生成

### 4. 项目筛选标准

- ✅ 今日 star 增长 > 500
- ✅ 有实际价值（非纯娱乐）
- ✅ 活跃维护（最近提交 < 7天）
- ✅ 文档完善
- ❌ 避免重复项目
- ❌ 避免过于简单的项目

## Notion 格式要求

使用 `markdown-to-notion.py` 转换：
```bash
/home/kai/.openclaw/workspace/scripts/lib/markdown-to-notion.py content.md > blocks.json
```

格式检查：
- [ ] 顶部有 callout 摘要
- [ ] 使用 heading_2 作为分类标题
- [ ] GitHub 链接格式正确
- [ ] 使用 divider 分隔各部分
- [ ] 底部有数据来源说明

## 执行流程

1. 获取 GitHub Trending 数据
2. 筛选有价值项目（5-10 个）
3. 按语言分类
4. 生成 Markdown 内容
5. 转换为 Notion 格式
6. 追加到 Notion 页面
7. 记录到 memory/YYYY-MM-DD.md

## 注意事项

- 直接抓取 GitHub Trending 最可靠
- 关注项目的实际价值
- 标注每个项目的语言和增长数据
- 避免低质量或重复项目
- 如果网络问题，基于经验生成并标注来源

---

**创建时间**: 2026-03-17
**适用任务**: github-trending
