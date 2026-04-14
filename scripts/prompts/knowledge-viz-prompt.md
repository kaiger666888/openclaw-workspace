# 知识可视化追踪 Prompt

## 任务目标

每日追踪知识可视化领域的最新可应用技术，包括工具更新、技术创新、最佳实践和实用案例，
将结果整理后推送到 Notion 技术研究页面。

## 内容要求

### 1. 追踪领域（轮换策略）

**每日重点关注**（按星期轮换）：
- **周一**：知识图谱工具（Neo4j, ArangoDB, Obsidian Graph, Roam Research 等）
- **周二**：可视化工具（Excalidraw, Mermaid, PlantUML, D3.js, ECharts 等）
- **周三**：AI 辅助可视化（Claude + Excalidraw, GitNexus, AI 生成图表等）
- **周四**：BI 和数据分析（Metabase, Superset, Looker Studio, Tableau 等）
- **周五**：交互式文档（Notion, Coda, Roam, Logseq 等的可视化功能）
- **周六**：开源项目和新工具（GitHub 新项目、Product Hunt 等）
- **周日**：综合回顾（本周热点、趋势总结、实用推荐）

### 2. 内容结构

```markdown
# 知识可视化研究 - YYYY年MM月DD日

> 一句话总结今日发现

## 🛠️ 工具更新
- [工具名称](链接)
  - 新功能/版本
  - 实用价值
  - 适用场景

## 💡 技术创新
- [技术名称]
  - 创新点
  - 应用前景
  - 学习成本

## 📊 最佳实践
- [案例名称](链接)
  - 实现方法
  - 效果展示
  - 可复用性

## 🔗 相关资源
- 文章/教程/文档链接
- GitHub 项目
- 在线演示

## 🎯 实用推荐
- 今日最值得尝试的工具/技术
- 适用人群
- 上手建议

---

**数据来源**: [来源列表] | **生成时间**: YYYY-MM-DD HH:MM
```

### 3. 质量标准

- ✅ **实用性**：必须是可立即应用的技术，不是纯理论
- ✅ **时效性**：优先追踪最近 1-7 天的更新和发现
- ✅ **可操作性**：提供具体的工具名称、链接和使用方法
- ✅ **多样性**：覆盖不同类型的可视化技术
- ✅ **真实性**：所有信息必须有来源链接

### 4. 搜索策略

**优先方案**：使用 web_search
```python
# 根据星期几选择搜索主题
web_search(
    query="knowledge visualization tools 2026",
    count=10
)

web_search(
    query="Excalidraw new features 2026",
    count=10
)

web_search(
    query="AI visualization tools latest",
    count=10
)
```

**降级方案**：如果 web_search 不可用，使用以下策略：

1. **使用 web_fetch 抓取固定网站**：
```python
# 可视化工具官网
web_fetch("https://excalidraw.com/")
web_fetch("https://mermaid.js.org/intro/")
web_fetch("https://observablehq.com/@d3")

# 知识图谱
web_fetch("https://neo4j.com/labs/)
web_fetch("https://roamresearch.com/")

# GitHub 探索
web_fetch("https://github.com/trending?since=weekly")
```

2. **使用本地知识库**：
```bash
# 搜索历史记录
cat /home/kai/.openclaw/workspace/memory/*.md | grep -i "可视化\|visualization"

# 搜索相关文档
grep -r "知识可视化\|knowledge visualization" /home/kai/.openclaw/workspace/
```

3. **基于经典工具生成**（最后手段）：
   - 列出已知的可视化工具
   - 标注"来源：经典工具"
   - 提供实用建议

**搜索限制**：
- web_search: ≤ 3 次，优先英文
- web_fetch: ≤ 5 次，选择权威网站
- 如果都失败： 基于经验生成并标注来源

### 5. 去重要求（强制执行）

**⚠️ 必须使用去重工具，禁止手动检查！**

**第一步：选择主题前，使用工具检查**
```bash
# 检查主题是否重复（返回 0=不重复，1=重复）
python3 /home/kai/.openclaw/workspace/scripts/lib/dedupe-validator.py \
  knowledge-viz check \
  --topic "主题名称" \
  --category "分类"
```

**第二步：如果返回 1（重复），必须重新选择**
- ❌ 禁止继续使用重复的主题
- ✅ 重新选择一个新主题
- ✅ 再次检查，直到返回 0

**第三步：内容生成成功后，必须添加到数据库**
```bash
# 添加到去重数据库
python3 /home/kai/.openclaw/workspace/scripts/lib/dedupe-validator.py \
  knowledge-viz add \
  --topic "主题名称" \
  --category "分类" \
  --tools "工具1,工具2" \
  --page-id "Notion页面ID"
```

**如果工具不可用**：
1. 读取历史文件：`cat /home/kai/.openclaw/workspace/memory/knowledge-viz-history.md`（如果存在）
2. 手动检查是否重复
3. 生成后手动更新历史文件

## Notion 格式要求

使用 `markdown-to-notion.py` 转换：
```bash
/home/kai/.openclaw/workspace/scripts/lib/markdown-to-notion.py content.md > blocks.json
```

格式检查：
- [ ] 顶部有 callout 摘要
- [ ] 使用 heading_2 作为分类标题
- [ ] 链接格式：`[工具名称](URL)`
- [ ] 使用 divider 分隔各部分
- [ ] 底部有数据来源说明

## Notion 页面结构

**父页面**：技术研究 (2fc11082-af8e-81de-98bb-d1741c3cee68)

**子页面命名**：知识可视化研究 - YYYY年MM月DD日

**页面位置**：技术研究页面下的子页面

## 执行流程

1. 确定今日主题（根据星期几）
2. 使用去重工具检查主题是否重复
3. 如果重复，重新选择主题
4. 搜索知识可视化相关内容（≤3次）
5. 筛选实用和最新的信息（5-10条）
6. 生成 Markdown 内容
7. 转换为 Notion 格式
8. 追加到 Notion 页面
9. 添加到去重数据库
10. 记录到 memory/YYYY-MM-DD.md

## 输出要求

### 必须包含的内容

1. **至少 3 个工具/技术更新**
   - 工具名称和链接
   - 新功能说明
   - 实用价值

2. **至少 1 个最佳实践案例**
   - 具体实现方法
   - 效果展示
   - 可复用性分析

3. **至少 2 个相关资源**
   - 文章/教程链接
   - GitHub 项目
   - 在线演示

4. **今日推荐**
   - 最值得尝试的工具/技术
   - 适用人群
   - 上手建议

### 质量检查

- [ ] 所有链接有效
- [ ] 工具名称准确
- [ ] 功能描述清晰
- [ ] 实用建议具体
- [ ] 没有重复内容

## 示例输出

### 知识可视化研究 - 2026年03月19日

> 今日发现：Excalidraw 新增 AI 流式生成功能，GitNexus 从代码生成交互式知识图谱

## 🛠️ 工具更新

### [Excalidraw](https://excalidraw.com/)
- **新功能**：AI 流式生成图表（Claude 集成）
- **实用价值**：可直接用自然语言描述需求，实时生成图表
- **适用场景**：快速原型设计、技术文档、头脑风暴

### [GitNexus](https://github.com/shareAI-lab/learn-claude-code)
- **创新点**：从 GitHub 仓库自动生成交互式知识图谱
- **技术栈**：零服务器，浏览器端运行
- **适用场景**：代码库理解、技术调研、团队知识分享

## 💡 技术创新

### AI 驱动的可视化生成
- **趋势**：Claude + MCP 集成，实时生成和编辑图表
- **代表工具**：Excalidraw, Draw.io, Mermaid
- **学习成本**：低（自然语言交互）

## 📊 最佳实践

### [Obsidian 知识图谱](https://obsidian.md/)
- **实现方法**：双向链接 + 图谱视图
- **效果**：可视化知识网络，发现隐藏关联
- **可复用性**：高，适用于个人知识管理

## 🔗 相关资源

- [Excalidraw 官方文档](https://docs.excalidraw.com/)
- [Mermaid 语法参考](https://mermaid.js.org/intro/)
- [Knowledge Graph Conference 2026](https://knowledgegraph.tech/)

## 🎯 实用推荐

**今日推荐**：Excalidraw AI 流式生成
- **适用人群**：需要快速创建图表的开发者、产品经理
- **上手建议**：
  1. 访问 Excalidraw.com
  2. 点击 AI 助手
  3. 用自然语言描述需求
  4. 实时查看生成结果

---

**数据来源**: Excalidraw 官网, GitHub Trending, Product Hunt | **生成时间**: 2026-03-19 10:00

## 注意事项

- 优先追踪**可立即使用**的技术，不是实验室项目
- 关注**学习成本**和**实用价值**的平衡
- 标注每条信息的来源和时间
- 如果无法获取足够信息，创建基础框架页面
- 使用去重工具避免重复推荐相同的工具/技术
- 优先英文搜索获取更全面结果

---

**创建时间**: 2026-03-19
**适用任务**: knowledge-viz
**父页面**: 技术研究 (2fc11082-af8e-81de-98bb-d1741c3cee68)
