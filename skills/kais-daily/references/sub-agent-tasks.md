# Sub-agent 搜集任务模板
# 4 个 sub-agent 从不同方向搜集，确保内容全面

## 通用模板

使用 sessions_spawn(runtime="subagent") 启动，task 内容如下（替换占位符）：

```
你是「{task_name}」的搜集员。请搜索「{topic}」相关的最新内容（2026年）。

搜索方向：{direction}

要求：
1. 使用 web_search 搜索 2-3 次（中英文各一次）
2. 对重要结果用 web_fetch 抓取详细内容
3. 每条信息必须包含：标题、要点摘要（2-3句）、来源URL
4. 至少搜集 5-8 条有价值的信息
5. 只输出搜集结果，不要生成文章
6. 输出格式：

### 1. [标题]
- 摘要：...
- 来源：[来源名](URL)
- 关键数据：...
```

## 4 个搜集方向

### A: 英文主流媒体
方向：TechCrunch, The Verge, Wired, Ars Technica, Bloomberg, Reuters
关键词：英文关键词，如 "AI agent 2026", "LLM breakthrough"

### B: 中文科技媒体
方向：36kr, 量子位, 机器之心, InfoQ, 少数派, 极客公园
关键词：中文关键词，如 "AI Agent 2026", "大模型最新进展"

### C: 开发者社区
方向：GitHub Trending, Hacker News, Reddit r/programming, Twitter/X
关键词：偏技术和开源，如 "github trending AI tools", "best AI coding assistant"

### D: 学术/深度分析
方向：ArXiv, 技术博客(Medium/Substack), 研究报告, YouTube 技术频道
关键词：偏深度，如 "AI research paper 2026", "deep dive LLM architecture"
