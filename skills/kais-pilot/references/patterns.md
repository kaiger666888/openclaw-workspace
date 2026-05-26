# 执行模式详解与示例

## 1. Pipeline（串行流水线）

**图特征：** 所有 step 形成单条链，每个 step 最多一个输入和一个输出消费者。

```
A ──→ B ──→ C ──→ D
```

```js
module.exports = {
  name: "pipeline-example",
  steps: [
    { id: "fetch", skill: "deep-research", params: { topic: "..." }, output: "raw.md" },
    { id: "rewrite", skill: "notion", input: "raw.md", output: "clean.md" },
    { id: "publish", skill: "xiaohongshu-ops", input: "clean.md" }
  ]
};
```

## 2. Fan-out（并行分发）

**图特征：** 一个 step 的 output 被多个独立 step 消费，且这些消费者之间无互相依赖。

```
       ┌──→ B
A ────┼──→ C
       └──→ D
```

```js
module.exports = {
  name: "fanout-example",
  steps: [
    { id: "research", skill: "deep-research", params: { topic: "Rust" }, output: "brief.md" },
    { id: "notion", skill: "notion", input: "brief.md" },
    { id: "xhs", skill: "xiaohongshu-ops", input: "brief.md" },
    { id: "chart", skill: "chart-image", input: "brief.md", output: "chart.png" }
  ]
};
```

## 3. Map-Reduce（多源收集汇总）

**图特征：** 多个独立 step 的 output 汇聚到一个 step（入度 > 1）。

```
A ──┐
    ├──→ D
B ──┤
C ──┘
```

```js
module.exports = {
  name: "mapreduce-example",
  steps: [
    { id: "news", skill: "deep-research", params: { topic: "AI news" }, output: "news.md" },
    { id: "papers", skill: "arxiv-watcher", output: "papers.md" },
    { id: "trends", skill: "deep-research", params: { topic: "AI trends" }, output: "trends.md" },
    { id: "digest", skill: "notion", input: ["news.md", "papers.md", "trends.md"] }
  ]
};
```

## 4. Approval Gate（人工审批）✨ 高级

**图特征：** step 标记了 `await: "human"`。

```
A ──→ B ──⏸️ C (approval) ──→ D
```

```js
module.exports = {
  name: "approval-example",
  steps: [
    { id: "draft", skill: "deep-research", params: { topic: "..." }, output: "draft.md" },
    {
      id: "review",
      input: "draft.md",
      await: "human",
      awaitPrompt: "请审核以下研究报告，确认内容质量后继续发布。如需修改请说明具体意见。"
    },
    { id: "publish", skill: "xiaohongshu-ops", input: "draft.md" }
  ]
};
```

**`await` 扩展字段：**

| 字段 | 说明 |
|------|------|
| `await` | `"human"` = 启用审批 |
| `awaitPrompt` | 审批时展示给用户的问题/说明 |
| `awaitTimeout` | 超时分钟数，超时后自动继续或终止 |
| `cronAwait` | cron 模式下是否仍暂停（默认 false，cron 中自动跳过） |

**AI 执行流程：**
1. 完成前置 steps → 收集 `input` 文件
2. 向用户发送消息：进度摘要 + 待审批内容 + 选项（✅继续/❌终止/✏️修改）
3. 等待用户回复 → 根据决定继续或终止

## 5. Event Loop（事件循环）✨ 高级

**图特征：** step 标记了 `loop`，或 output 文件 == input 文件（自环）。

```
A ──→ B ──→ B ──→ B ──→ C
         (loop up to max)
```

```js
module.exports = {
  name: "loop-example",
  steps: [
    { id: "draft", skill: "deep-research", params: { topic: "..." }, output: "article.md" },
    {
      id: "refine",
      skill: "general",
      input: "article.md",
      output: "article.md",   // 覆写 = 自环
      loop: {
        max: 3,
        until: "文章结构完整，有数据支撑，无明显事实错误",
      }
    },
    { id: "publish", skill: "notion", input: "article.md" }
  ]
};
```

**`loop` 扩展字段：**

| 字段 | 说明 |
|------|------|
| `max` | 最大迭代次数（默认 5） |
| `until` | 退出条件描述（AI 自然语言判断） |
| `condition` | 程序化条件（JS 表达式，可选） |

**AI 执行流程：**
1. 执行 step → 产出文件
2. 读取产出，评估 `until` 条件
3. 达标 → 退出循环，继续下游
4. 未达标且 `iteration < max` → 重新执行（带入上次产出作为 input）
5. 达到 max → 退出，记录最终状态

**日志示例：**
```
[CREW] refine | running | 0ms
[CREW] refine | loop_iteration | 1/3
[CREW] refine | loop_iteration | 2/3
[CREW] refine | success | 45000ms (exited: condition met)
```

## 6. Nested DAG（嵌套编排）✨ 高级

**图特征：** step 引用另一个 crew.js 文件，形成嵌套 DAG。

```
┌─────────────────┐
│ Parent DAG      │
│                 │
│ A ──→ [Sub] ──→ C │
│       ┌───┬───┐  │
│       │ X │ Y │  │
│       └───┴───┘  │
└─────────────────┘
```

**父 crew.js:**
```js
module.exports = {
  name: "parent-project",
  steps: [
    { id: "data", skill: "deep-research", params: { topic: "..." }, output: "data.md" },
    {
      id: "sub-analysis",
      crew: "./sub-crew.js",
      input: "data.md",
      output: "analysis-result.md"
    },
    { id: "report", skill: "notion", input: "analysis-result.md" }
  ]
};
```

**sub-crew.js:**
```js
module.exports = {
  name: "sub-analysis",
  steps: [
    { id: "extract", skill: "general", output: "extracted.md" },
    { id: "visualize", skill: "chart-image", input: "extracted.md", output: "chart.png" },
    { id: "summarize", skill: "general", input: ["extracted.md", "chart.png"], output: "result.md" }
  ]
};
```

**展开后的 DAG：**
```
data → sub-analysis.extract → sub-analysis.visualize → sub-analysis.summarize → report
```

子 step 的 id 自动加上 `parentId.` 前缀（如 `sub-analysis.extract`）。

## 7. DAG（通用有向无环图）

**图特征：** 上述模式的任意嵌套组合。

```
      ┌──→ B ──┐
A ────┤        ├──→ E ──→ F
      └──→ C ──┘         │
            D ───────────┘
```

```js
module.exports = {
  name: "dag-example",
  steps: [
    { id: "a", skill: "deep-research", output: "a.md" },
    { id: "b", skill: "notion", input: "a.md", output: "b.md" },
    { id: "c", skill: "chart-image", input: "a.md", output: "c.png" },
    { id: "d", skill: "deep-research", output: "d.md" },
    { id: "e", skill: "notion", input: ["b.md", "c.png"], output: "e.md" },
    { id: "f", skill: "xiaohongshu-ops", input: ["e.md", "d.md"] }
  ]
};
```

**执行：** 拓扑排序为 [[A, D], [B, C], [E], [F]]，同层并行，层间串行。

## 8. 组合模式示例

**研究 → 循环优化 → 审批 → 发布：**

```js
module.exports = {
  name: "full-pipeline",
  steps: [
    { id: "research", skill: "deep-research", params: { topic: "...", depth: "medium" }, output: "draft.md" },
    {
      id: "refine",
      input: "draft.md",
      output: "draft.md",
      loop: { max: 2, until: "内容质量达标" }
    },
    {
      id: "approve",
      input: "draft.md",
      await: "human",
      awaitPrompt: "请审核报告质量"
    },
    { id: "publish", skill: "notion", input: "draft.md", retry: { max: 3 } }
  ]
};
// Pipeline + Event Loop + Approval + Retry — 全模式组合
```
