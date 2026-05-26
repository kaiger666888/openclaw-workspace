# 定时任务 Prompt 规范

> 统一的 prompt 设计和 Notion 文本格式标准

---

## 📁 Prompt 文件列表

| 任务 | Prompt 文件 | 执行时间 |
|------|------------|----------|
| AIGC前沿总结 | `aigc-summary-prompt.md` | 04:20 |
| 每日新闻 | `daily-news-prompt.md` | 04:30 |
| Claude Code心得 | `claude-code-insights-prompt.md` | 04:40 |
| GitHub Trending | `github-trending-prompt.md` | 04:50 |
| 投资大师思想精华 | `investment-wisdom-prompt.md` | 05:00 |
| 创业失败经验教训 | `startup-failure-lessons-prompt.md` | 05:10 |
| 技术研究 | `tech-research-prompt.md` | 04:00 |
| 每日英语德语 | `daily-language-prompt.md` | 04:10 |
| VibeCoding | `vibecoding-prompt.md` | 03:30 |
| 读书笔记 | `reading-notes-prompt.md` | 03:40 |
| 失败经验 | `failure-lessons-prompt.md` | 03:50 |
| 知识可视化研究 | `knowledge-viz-prompt.md` | 05:15 |
| umlVisionAgent技术雷达 | `uml-tech-radar-prompt.md` | 周六 05:20 |

---

## 🎯 统一设计原则

### 1. 结构化搜索关键词
每个 prompt 都包含 P0/P1/P2 优先级的搜索关键词：
- **P0** - 必须搜索
- **P1** - 至少搜索 2 个
- **P2** - 可选

### 2. 标准化输出格式
每个 prompt 都定义了：
- 页面标题格式
- 内容结构模板
- Markdown 格式要求

### 3. 明确质量标准
每个 prompt 都包含：
- ✅ 必须包含
- ❌ 不要包含
- 📊 数量控制

### 4. 评估标准
- 时效性
- 可靠性
- 实用性
- 相关性

---

## 📝 Notion 文本规范

### ⚠️ 重要：必须使用 JSON 块格式

**所有向 Notion 输出的内容必须：**
1. 使用 JSON 块格式（不是 Markdown）
2. 输出到文件，用 `notion-cli block append --children-file <json-file> <page-id>` 追加
3. 遵循格式检查清单

**详细规范：** 参见 `NOTION_FORMAT_STANDARDS.md`

### 格式检查清单
| 检查项 | 要求 |
|-------|------|
| 顶部 callout | ✅ 必须有摘要 |
| heading_2 | ✅ 分类标题 |
| 链接格式 | ✅ `🔗 名称URL` |
| 重复内容 | ❌ 禁止重复追加 |

### 标题层级
```markdown
## 🎯 一级标题（带 emoji）
### 二级标题
#### 三级标题
```

### 列表格式
```markdown
- **加粗字段**: 内容描述
```

### 表格格式
```markdown
| 列1 | 列2 | 列3 |
|-----|-----|-----|
| 内容 | 内容 | 内容 |
```

### 引用格式
```markdown
> "引用内容" — 来源
```

### 代码块
```markdown
```[语言]
// 代码
```
```

### 链接格式
```markdown
[显示文本](URL)
```

---

## 🔄 轮换计划

部分任务有主题轮换，确保内容多样性：

| 任务 | 轮换维度 |
|------|---------|
| 投资大师 | 每天一位大师（巴菲特→芒格→段永平→林奇→达利欧→格雷厄姆） |
| 创业失败 | 每天一种类型（独角兽→知名→中国→近期） |
| 技术研究 | 每天一个领域（AI→语言→架构→工具→前沿） |
| 每日语言 | 每天一个语法点（英语+德语） |
| 读书笔记 | 每天一种类型（技术→商业→方法→人文） |
| VibeCoding | 每天一个方向（AI→Web→系统→自动化→开源） |

---

## 📊 数量控制标准

| 任务 | 条目数量 | 字符控制 |
|------|---------|---------|
| AIGC前沿 | 5-12 条 | 3000-5000 |
| 每日新闻 | 5-10 条 | 2000-4000 |
| Claude Code | 4-8 条 | 2000-4000 |
| GitHub Trending | 6-10 个 | 2000-4000 |
| 投资大师 | 核心理念 2-4 个 | 3000-5000 |
| 创业失败 | 1 个案例深挖 | 3000-5000 |
| 技术研究 | 1 个主题深挖 | 5000-8000 |
| 每日语言 | 语法+词汇+名言 | 3000-4000 |
| VibeCoding | 1-3 个代码片段 | 2000-4000 |
| 读书笔记 | 3-5 条摘抄 | 2000-4000 |
| 失败经验 | 1 个失败分析 | 1500-3000 |

---

## 🛠️ 使用方法

### Sub-agent 调用
```bash
# 在 daily-tasks.sh 中触发 sub-agent 时传递 prompt 文件路径
PROMPT_FILE="/home/kai/.openclaw/workspace/prompts/aigc-summary-prompt.md"
```

### 内容生成
Sub-agent 会：
1. 读取对应的 prompt 文件
2. 按照搜索关键词执行 web_search
3. 按照输出格式生成内容
4. 符合质量标准后输出

---

## 📅 更新日志

- **2026-03-01**: 创建所有 13 个 prompt 文件，统一规范

---

*维护者: Clawd*
*最后更新: 2026-03-01*
