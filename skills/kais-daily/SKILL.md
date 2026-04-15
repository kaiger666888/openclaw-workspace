---
name: kais-daily
description: 每日定时任务执行引擎。14 个 Notion 内容任务分两批执行，每个任务 4 方向并行搜集 + 主 agent 汇总写入 + 质量验证重试。激活条件：收到 "执行每日任务"、"batch1"、"batch2" 指令，或 cron 定时触发。
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

1. **每个任务必须用 `daily-task-write.sh` 写入** — 这是唯一正确的写入方式
2. **禁止直接写入父页面 ID** — 脚本会自动创建子页面
3. **来源链接紧跟每条信息** — 禁止堆在文章底部
4. **不合格就重做** — 块数 < 50 必须重试

---

## 执行流程

### Step 1: 智能搜集（主 agent 搜索 + 2 个 sub-agent 深入）

#### 1a. 主 agent 先搜 1 次，确定搜集方向

```python
web_search(query="{topic} 2026 最新", count=5)
```

根据搜索结果，确定 2 个最有价值的搜集方向（如"AI Agent 产品发布"+"AI Agent 技术突破"），分配给 2 个 sub-agent。

#### 1b. 启动 2 个 sub-agent 交错搜集

**⚠️ Brave Search 限流：每分钟最多 1 次请求。两个 sub-agent 之间间隔 30 秒启动。**

**sub-agent A — 英文方向**：
```python
sessions_spawn(
    runtime="subagent",
    task="""你是「{task_name}」的英文搜集员。请搜索「{direction_A}」相关最新内容（2026年）。

要求：
1. web_search 搜索 2 次（英文关键词，两次之间 sleep 60 秒避免限流）
2. 对排名前 3 的结果用 web_fetch 抓取详细内容
3. 每条信息：标题、要点摘要（2-3句）、来源URL
4. 至少 5 条有价值信息
5. 只输出搜集结果，不要生成文章
6. 输出格式：
### 1. [标题]
- 摘要：...
- 来源：[来源名](URL)
- 关键数据：..."""
)
```

**等待 30 秒后启动 sub-agent B**：

**sub-agent B — 中文方向**：
```python
sessions_spawn(
    runtime="subagent",
    task="""你是「{task_name}」的中文搜集员。请搜索「{direction_B}」相关最新内容（2026年）。

要求：
1. web_search 搜索 2 次（中文关键词，search_lang="zh-hans"，两次之间 sleep 60 秒避免限流）
2. 对排名前 3 的结果用 web_fetch 抓取详细内容
3. 每条信息：标题、要点摘要（2-3句）、来源URL
4. 至少 5 条有价值信息
5. 只输出搜集结果，不要生成文章
6. 输出格式：
### 1. [标题]
- 摘要：...
- 来源：[来源名](URL)
- 关键数据：..."""
)
```

#### 搜集预算

每个任务总计：
- 主 agent：1 次搜索（定方向）
- sub-agent A：2 次搜索 + 3 次 web_fetch
- sub-agent B：2 次搜索 + 3 次 web_fetch
- **总计：5 次搜索 + 6 次抓取**（之前是 8-12 次搜索）

参考模板：`references/sub-agent-tasks.md`

### Step 2: 汇总去重

等待 4 个 sub-agent 完成后：
1. 收集所有结果
2. 去重（同一事件不同来源只保留最详细的）
3. 按重要性排序
4. 整理成写作素材

### Step 3: 生成 Markdown 内容

使用 kais-notion skill 的富格式规范。

**每个任务必须包含：**
- 页面开头 `>💡` 摘要 callout
- 每条信息紧跟 `来源：[描述](URL)`
- 关键数据颜色标注：`{red:负面}` `{green:正面}` `{blue:技术}`
- `---` 分隔各部分
- `>📋` 折叠块放补充材料

**来源链接格式（⚠️ 最重要）：**
```
✅ 正确：
### OpenAI 发布 GPT-5
- 推理能力提升 300%
- 来源：[OpenAI Blog](https://openai.com/blog/gpt5)

❌ 错误：
### OpenAI 发布 GPT-5
- 推理能力提升 300%

---
数据来源：openai.com, techcrunch.com  ← 不允许
```

**理论/心智模型等无外部来源的内容可以不写来源链接。**

### Step 4: 写入 Notion（唯一正确方式）

```bash
bash /home/kai/.openclaw/workspace/scripts/daily-task-write.sh <event> /tmp/crew-daily-tasks/<event>-content.md
```

这个脚本会自动：创建子页面 → markdown-to-notion 转换 → 写入 → 输出 PAGE_ID

**⚠️ 禁止以下写入方式：**
- ❌ `notion-cli page create --content "markdown"` （纯文本，不转换格式）
- ❌ `notion-cli block append --content "markdown"` （同上）
- ❌ 直接写入父页面 ID
- ❌ 不用脚本手动拼接 JSON

### Step 5: 验证质量

```bash
notion-cli block list <PAGE_ID>
```

| 块数 | 状态 | 处理 |
|------|------|------|
| < 20 | ❌ 严重不足 | 重做 Step 3-5 |
| 20-50 | ⚠️ 偏短 | 重做 Step 3-5 |
| ≥ 50 | ✅ 合格 | 继续下一个任务 |

**最多重试 2 次。超过则标记失败，继续下一个任务。**

参考：`references/quality-check.md`

---

## 任务配置

### 第1批（batch1）— 02:00

| # | event | 需要去重 | 特殊处理 |
|---|-------|---------|---------|
| 1 | github-review | - | 先运行 github-review.sh，有提交才继续 |
| 2 | vibecoding | - | |
| 3 | reading-notes | - | |
| 4 | failure-lessons | - | |
| 5 | tech-research | - | |
| 6 | daily-language | ✅ | 先运行 dedupe-validator.py |
| 7 | daily-aigc | - | |

### 第2批（batch2）— 02:10

| # | event | 需要去重 |
|---|-------|---------|
| 1 | daily-news | - |
| 2 | claude-code-insights | - |
| 3 | github-trending | - |
| 4 | investment-wisdom | - |
| 5 | startup-failures | - |
| 6 | knowledge-viz | - |
| 7 | mental-models | - |

完整配置：`references/events.yaml`

---

## 去重流程

需要去重的任务，在 Step 3 之前执行：

```bash
# 检查
python /home/kai/.openclaw/workspace/scripts/lib/dedupe-validator.py \
  english-german check --quote "格言内容" --author "作者"

# 生成内容后记录
python /home/kai/.openclaw/workspace/scripts/lib/dedupe-validator.py \
  english-german add --quote "格言" --author "作者" --source "来源" --page-id "PAGE_ID"
```

---

## 完成后输出

```markdown
| 任务 | PAGE_ID | 块数 | 状态 |
|------|---------|------|------|
| vibecoding | 34x... | 85 | ✅ |
| ... | ... | ... | ... |
```

---

## 工具链

| 工具 | 路径 | 用途 |
|------|------|------|
| daily-task-write.sh | `scripts/daily-task-write.sh` | 创建子页面+写入（一步完成） |
| markdown-to-notion.py | `scripts/lib/markdown-to-notion.py` | MD→Notion 块转换 |
| notion-write.sh | `scripts/lib/notion-write.sh` | 写入统一入口 |
| dedupe-validator.py | `scripts/lib/dedupe-validator.py` | 内容去重 |
| github-review.sh | `scripts/github-review.sh` | GitHub 代码审查 |

---

*创建时间: 2026-04-14*
*替代方案: 解决 GLM-5 不遵守 cron prompt 的问题，用 skill 约束执行流程*
