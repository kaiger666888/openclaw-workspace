# Sub-agent 搜集任务模板
# 2 个 sub-agent 从英文/中文方向搜集，主 agent 先搜 1 次定方向

## 搜索策略

```
主 agent: web_search 1 次 → 分析结果 → 确定 2 个方向
    ↓
sub-agent A: web_search 2 次 (英文) + web_fetch 3 次 → 5-8 条信息
    ↓ (间隔 30 秒)
sub-agent B: web_search 2 次 (中文) + web_fetch 3 次 → 5-8 条信息
    ↓
主 agent: 汇总去重 → 10-16 条高质量素材
```

## 限流保护

| 规则 | 说明 |
|------|------|
| Brave Search | 每分钟最多 1 次，两次搜索之间 sleep 60 秒 |
| sub-agent 间隔 | A 和 B 之间间隔 30 秒启动 |
| web_fetch | 不限流，可连续调用 |
| 总搜索次数 | 每个任务 5 次（之前是 8-12 次） |

## 英文搜集方向参考

根据任务类型选择最匹配的方向：

| 任务 | 方向 A | 方向 B |
|------|--------|--------|
| daily-news | AI 产品发布 | 科技政策/监管 |
| daily-aigc | 模型/技术突破 | 产业/商业化 |
| github-trending | 热门开源项目 | 开发者工具 |
| vibecoding | 编程工具更新 | 开发方法论 |
| tech-research | 新技术/框架 | 最佳实践 |
| reading-notes | 深度文章 | 热门书籍 |
| failure-lessons | 创业失败案例 | 技术项目失败 |
| claude-code-insights | Claude Code 更新 | AI 编程工具对比 |
| investment-wisdom | 投资大师观点 | 市场分析 |
| startup-failures | 创业失败案例 | 商业模式失败 |
| knowledge-viz | 可视化工具 | 数据可视化 |
| mental-models | 认知科学 | 决策框架 |
| daily-language | 英语学习方法 | 德语学习方法 |

## 中文搜集方向参考

| 任务 | 方向 A | 方向 B |
|------|--------|--------|
| daily-news | AI 大模型动态 | 科技行业新闻 |
| daily-aigc | AI 应用案例 | 国产 AI 进展 |
| github-trending | GitHub 热门项目 | 国内开源动态 |
| vibecoding | 开发者社区热帖 | 技术教程 |
| tech-research | 技术趋势 | 国内技术方案 |
| reading-notes | 深度书评 | 知识类文章 |
| failure-lessons | 创业复盘 | 项目踩坑 |
| claude-code-insights | Claude Code 实践 | AI 编程对比 |
| investment-wisdom | 投资策略 | 宏观经济 |
| startup-failures | 创业教训 | 商业模式 |
| knowledge-viz | 数据可视化案例 | 信息架构 |
| mental-models | 心理学应用 | 思维模型实践 |
| daily-language | 英语语法/词汇 | 德语语法/词汇 |
