---
name: kais-daily
description: 每日定时任务执行引擎。14 个 Notion 内容任务分两批执行。每个任务：创建页面 → 读取专属 prompt → 搜索生成 → 写入 Notion → 验证质量。
metadata:
  openclaw:
    emoji: 📅
    requires:
      bins:
        - notion-cli
        - python3
---

# Kais Daily — 每日定时任务执行引擎

## 核心原则

1. **每个任务必须先读取专属 prompt** — `scripts/prompts/<event>-prompt.md`
2. **写入必须用 `daily-task-write.sh`** — 唯一正确的写入方式
3. **来源链接紧跟每条信息** — 禁止堆在文章底部
4. **不合格就重做** — 块数不达标必须重试
5. **故障隔离** — 一个任务失败不影响其他任务

---

## 执行流程

### Step 1: 创建 Notion 子页面

```bash
bash /home/kai/.openclaw/workspace/scripts/daily-tasks-v3.sh <event>
```

从输出中提取 PAGE_ID（格式：`PAGE_ID:xxxxxxxx`）

### Step 2: 读取任务专属 Prompt

```bash
read /home/kai/.openclaw/workspace/scripts/prompts/<event>-prompt.md
```

按 prompt 中的指引确定搜索关键词、内容结构和质量标准。

### Step 3: 搜索 + 生成 Markdown

- 按 prompt 文件中的搜索关键词执行搜索
- web_search 限流时降级到 web_fetch 抓取固定网站
- 生成 Markdown 保存到 `/tmp/crew-daily-tasks/<event>-content.md`

**内容格式要求：**
- 页面开头用 `>💡` 做摘要 callout
- 每条信息紧跟 `来源：[描述](URL)`
- 使用 `---` 分隔各部分

### Step 4: 写入 Notion

```bash
bash /home/kai/.openclaw/workspace/scripts/daily-task-write.sh <PAGE_ID> /tmp/crew-daily-tasks/<event>-content.md
```

⚠️ 第一个参数是 PAGE_ID，不是 event 名称！

### Step 5: 验证质量

```bash
notion-cli block list <PAGE_ID>
```

| 任务类型 | 合格 | 偏短 | 不合格 |
|----------|------|------|--------|
| daily-language | ≥20 块 | — | <20 块 |
| github-review | 有提交即合格 | — | — |
| 其他所有 | ≥50 块 | 20-50 块 | <20 块 |

最多重试 2 次，超过则标记失败继续下一个任务。

---

## 降级策略

当 web_search 不可用时：
1. web_fetch 抓取 prompt 中列出的固定网站
2. 基于已有知识生成，标注"来源：经验总结"
3. 所有方案失败则创建基础框架页面标注"待补充"

参考：`scripts/prompts/search-fallback-instruction.md`

---

## 任务配置

### 第1批（batch1）— 02:00

| # | event | prompt 文件 | 特殊处理 |
|---|-------|------------|---------|
| 1 | github-review | github-review-prompt.md | 先运行 github-review.sh，无提交则跳过 |
| 2 | vibecoding | vibecoding-prompt.md | |
| 3 | reading-notes | reading-notes-prompt.md | |
| 4 | failure-lessons | failure-lessons-prompt.md | |
| 5 | tech-research | tech-research-prompt.md | |
| 6 | daily-language | daily-language-prompt.md | 生成前必须去重检查 |
| 7 | daily-aigc | daily-aigc-prompt.md | |

### 第2批（batch2）— 02:10

| # | event | prompt 文件 | 特殊处理 |
|---|-------|------------|---------|
| 1 | daily-news | daily-news-prompt.md | |
| 2 | claude-code-insights | claude-code-insights-prompt.md | |
| 3 | github-trending | github-trending-prompt.md | |
| 4 | investment-wisdom | investment-wisdom-prompt.md | |
| 5 | startup-failures | startup-failures-prompt.md | |
| 6 | knowledge-viz | knowledge-viz-prompt.md | |
| 7 | mental-models | mental-models-prompt.md | 生成前必须去重检查 |

完整配置：`references/events.yaml`

---

## 去重流程

需要去重的任务（daily-language, mental-models），在 Step 3 之前执行：

```bash
python /home/kai/.openclaw/workspace/scripts/lib/dedupe-validator.py \
  <type> check --<field> "内容"

# 生成成功后记录
python /home/kai/.openclaw/workspace/scripts/lib/dedupe-validator.py \
  <type> add --<field> "内容" --page-id "PAGE_ID"
```

---

## 工具链

| 工具 | 路径 | 用途 |
|------|------|------|
| daily-tasks-v3.sh | `scripts/daily-tasks-v3.sh` | 创建子页面入口 |
| daily-tasks.sh | `scripts/daily-tasks.sh` | 创建子页面（回退） |
| daily-task-write.sh | `scripts/daily-task-write.sh` | 创建子页面+写入 |
| markdown-to-notion.py | `scripts/lib/markdown-to-notion.py` | MD→Notion 块转换 |
| dedupe-validator.py | `scripts/lib/dedupe-validator.py` | 内容去重 |
| github-review.sh | `scripts/github-review.sh` | GitHub 代码审查 |

---

*创建时间: 2026-04-14*
*最后更新: 2026-04-20 — 统一流程，删除 sub-agent 并行描述，对齐 cron 实际行为*
