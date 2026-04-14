---
name: project-crew
description: Intelligent task orchestration and project lifecycle management. "Graph is orchestration" — define skills with input/output dependencies, auto-analyze DAG, pick optimal execution strategy. Supports pipeline, fan-out, map-reduce, approval gates, event loops, nested DAG, git worktree parallel development, checkpoint/resume, and evolutionary selection.
---

# Project Crew — 智能任务编排与项目管理

**核心理念：图即编排。** 定义 skill 之间的数据依赖，编排器自动推断最优执行策略。

**扩展能力：项目即仓库。** 自动创建 Git 仓库，支持并行 worktree 开发、检查点回溯、优胜劣汰。

## 快速开始

1. 创建项目定义文件（JS）：
   ```js
   // /tmp/crew-myproject/crew.js
   module.exports = {
     name: "每日技术研究",
     steps: [
       { id: "research", skill: "deep-research", params: { topic: "AI 2026" }, output: "report.md" },
       { id: "chart", skill: "chart-image", input: "report.md", output: "chart.png" },
       { id: "notion", skill: "notion", input: ["report.md", "chart.png"] },
     ]
   };
   ```

2. 执行编排：
   ```
   读取项目定义 → 分析 DAG → 推断模式 → spawn sub-agents → 收集结果
   ```

## 项目定义规范

### 基本结构

```js
module.exports = {
  name: "项目名称",           // 必填
  goal: "项目目标描述",       // 推荐，用于 README 和方向判断
  workdir: "/tmp/crew-xxx",  // 可选，默认 /tmp/crew-<name>/
  env: { KEY: "value" },     // 可选，注入环境变量
  steps: [...]               // 必填，step 数组
};
```

### 项目管理字段（扩展）

```js
module.exports = {
  name: "ai-code-review",
  goal: "自动化代码审查系统",
  workdir: "/tmp/crew-ai-review",

  // ── 项目引导 ──
  project: {
    lang: "node",                    // 语言（node/python/rust/go/general）
    lfs: ["*.onnx", "*.gguf"],      // Git LFS 跟踪模式（可选）
  },

  // ── 并行开发 ──
  worktrees: 3,                      // 创建 3 个并行 worktree（默认 2）
  evolveStrategy: "best-output",     // 优胜劣汰策略（best-output/most-commits）

  steps: [...]
};
```

| 字段 | 说明 |
|------|------|
| `goal` | 项目目标，写入 README，指导方向判断 |
| `project.lang` | 编程语言，自动生成对应 .gitignore |
| `project.lfs` | LFS 文件模式列表，自动配置 git-lfs |
| `worktrees` | 并行开发副本数，每个是独立 git worktree |
| `evolveStrategy` | 评估策略：`best-output`（输出质量）或 `most-commits`（迭代次数） |

### Step 定义

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | string | 唯一标识符，用于引用 output |
| `skill` | string | 要调用的 skill 名称 |
| `input` | string\|string[] | 依赖的 step output 文件（自动建立依赖边） |
| `output` | string\|string[] | 产出文件（其他 step 通过 input 引用） |
| `params` | object | 传递给 skill 的参数 |
| `mode` | string | 强制执行模式（覆盖自动推断） |
| `await` | string | `"human"` = 审批门，执行到此处暂停等用户确认 |
| `loop` | object | `{ max: 10, until: "quality >= 8" }` 事件循环 |
| `timeout` | number | 超时秒数 |
| `retry` | object\|number | 重试配置：`{ max: 3, delay: 5000 }` 或数字（默认 delay 3s） |
| `fallback` | string | 失败时替代 skill 名称 |
| `parallel` | number | 并行度限制（默认 4） |
| `workflow` | string | 开发工作流模式（默认 `gsd`，可选 `direct`） |

### 开发工作流（GSD 集成）

当 step 的 `skill` 为 `claude-code-via-openclaw` 时，默认走 **GSD 结构化开发流程**，而非自由文本 prompt。

**`workflow: "gsd"`（默认）** — 结构化 phase 管理：
```
research → plan → execute → verify → ship
```
- `/gsd:new-project`：自动初始化（通过 gsd-auto-init.cjs 绕过交互）
- `/gsd:autonomous --from 1`：自主执行所有 phase
- `/gsd:execute-phase N`：执行指定 phase
- `/gsd:verify-work`：验证产出质量
- `/gsd:ship`：交付
- 支持断点续传：按 phase 粒度恢复

**`workflow: "direct"`** — 自由文本 prompt：
- 将 `params` 中的任务描述直接发给 Claude Code
- 适用于简单任务、快速修复、探索性开发
- 无结构化 phase 管理

**params 传递规则：**

| workflow | params 内容 | 示例 |
|----------|-----------|------|
| `gsd` | 项目需求描述 | `{ requirement: "构建 REST API，支持 JWT 认证" }` |
| `direct` | 完整任务指令 | `{ task: "在 src/auth.js 中添加 OAuth2 回调处理" }` |

**crew.js 示例：**
```js
module.exports = {
  name: "api-project",
  steps: [
    { id: "research", skill: "deep-research", params: { topic: "JWT best practices" }, output: "brief.md" },
    { id: "dev", skill: "claude-code-via-openclaw", input: "brief.md",
      params: { requirement: "构建用户认证 API" },
      workflow: "gsd"  // 默认值，可省略
    },
    { id: "fix", skill: "claude-code-via-openclaw",
      params: { task: "修复登录接口的 token 过期问题" },
      workflow: "direct"  // 简单任务，不走 GSD
    }
  ]
};
```

### 隐式 input 规则

如果 step 没有 `input` 字段，自动作为起始节点（无前置依赖）。如果 `input` 是字符串，等价于单元素数组。

## 执行模式

编排器从依赖图自动推断，用户可通过 `mode` 字段覆盖：

| 模式 | 图特征 | 描述 |
|------|--------|------|
| **pipeline** | 全串行链 | A → B → C |
| **fan-out** | 有并行独立分支 | A → (B, C, D) |
| **map-reduce** | 多分支汇合 | (A, B) → C |
| **approval** | 有 `await: "human"` | 暂停等人工确认 |
| **event-loop** | 有环依赖 | 循环直到条件满足 |
| **dag** | 复杂图 | 通用拓扑排序执行 |

### 模式推断算法

```
1. 解析所有 step，收集 id → { inputs, outputs, hasLoop }
2. 对每个 step，将 input 文件名解析为来源 step id
3. 构建邻接表：step.id → [依赖的 step.id]
4. 检测环：DFS 回溯 → 标记为 event-loop 模式
   - 注意：自环（同一文件 input+output）需通过 loop 字段辅助检测
5. 检查 await:"human" → 标记为 approval
6. 统计拓扑特征：
   - 有 step 的 outDegree > 1（单源扇出）→ fan-out
   - 有多个起始节点（入度=0）→ fan-out
   - 有 step 入度 > 1（汇合点）→ map-reduce
   - 所有 step 入度 ≤ 1 且全串行 → pipeline
   - 有 loop 字段 → event-loop
   - 其他 → dag（通用拓扑排序）
7. 用户通过 step.mode 可覆盖自动推断
8. 同一图中不同子图可独立使用不同模式
```

## 编排执行流程

```
┌─────────────────────────────────────────┐
│ 1. 加载 crew.js                         │
│ 2. 创建 workdir (/tmp/crew-<name>/)     │
│ 3. 分析 DAG，推断模式                    │
│ 4. 拓扑排序，确定并行层级                │
│ 5. 按层 spawn sub-agents               │
│ 6. 等待同层完成 → 下一层                │
│ 7. 遇到 await:"human" → 暂停汇报        │
│ 8. 遇到 loop → 执行+检查 until 条件     │
│ 9. 失败 → retry 重试 / fallback 降级    │
│ 10. 全部完成 → 汇总结果                  │
└─────────────────────────────────────────┘
```

### 重试与降级

- **retry**: step 失败后自动重试，支持 `max`（次数）和 `delay`（间隔 ms）
- **fallback**: 重试耗尽后，切换到替代 skill 执行
- 执行日志记录每次尝试的状态、耗时和 token 消耗

### Sub-Agent 调用

每个 step 作为独立 sub-agent 执行：
- 读取对应 skill 的 SKILL.md 获取指导
- `params` 中的内容作为任务描述
- `input` 文件从 workdir 中读取
- `output` 文件写入 workdir

## 完整示例

### 研究报告流水线

```js
module.exports = {
  name: "daily-research",
  steps: [
    {
      id: "search",
      skill: "deep-research",
      params: { topic: "AI agents 2026", depth: "medium" },
      output: "research.md"
    },
    {
      id: "summarize",
      skill: "notion",
      input: "research.md",
      params: { pageId: "2fc11082-af8e-81de-98bb-d1741c3cee68" }
    },
    {
      id: "chart",
      skill: "chart-image",
      input: "research.md",
      output: "trend-chart.png"
    },
    {
      id: "post",
      skill: "xiaohongshu-ops",
      input: ["research.md", "trend-chart.png"],
      await: "human"
    }
  ]
};
// 推断模式: search → (summarize, chart) [fan-out] → post [map-reduce + approval]
```

### 并行内容生产

```js
module.exports = {
  name: "content-factory",
  steps: [
    { id: "topic", skill: "deep-research", params: { topic: "Rust vs Go" }, output: "brief.md" },
    { id: "article", skill: "notion", input: "brief.md", output: "article.md" },
    { id: "xhs", skill: "xiaohongshu-ops", input: "brief.md" },
    { id: "chart1", skill: "chart-image", input: "brief.md", output: "perf.png" },
    { id: "chart2", skill: "chart-image", input: "article.md", output: "ecosystem.png" },
  ]
};
// 推断: topic → (article, xhs, chart1) [fan-out] → chart2 [dag]
```

## 高级模式执行指南（AI 必须遵循）

### Approval Gate（人工审批）

当 command 包含 `await` 字段时：

```
1. 执行到该 step 时，先完成所有前置 step
2. 收集 await.reviewFiles 列出的文件内容
3. 向用户发送审批请求，包含：
   - 当前进度（已完成的 steps）
   - 待审批内容（文件摘要或关键片段）
   - await.prompt 中定义的审批问题
   - 选项：✅ 继续 / ❌ 终止 / ✏️ 修改意见
4. 等待用户回复
5. 用户确认 → 继续执行后续 step
6. 用户拒绝 → 终止编排，报告原因
7. 用户修改 → 根据修改意见调整后重新审批
```

**Cron 模式下**：`await.cronSkip: true` 的 step 自动跳过，`cronAwait: true` 的 step 正常暂停（cron 会发送通知）。

### Event Loop（事件循环）

当 command 包含 `loop` 字段时：

```
1. 执行该 step
2. 检查产出（loop.selfLoop 时检查 output 文件内容）
3. 评估 loop.until 条件（AI 判断内容质量是否达标）
4. 如果达标 → 退出循环，继续后续 step
5. 如果未达标且迭代次数 < loop.max → 重新执行该 step
6. 达到 loop.max → 退出循环，记录最终状态
7. 每次迭代输出日志：[CREW] {step} | loop_iteration | {current}/{max}
```

**条件评估**：AI 读取产出文件，基于 `loop.until` 描述判断。如果有 `loop.condition`（JS 表达式），也可程序化检查。

### Nested DAG（嵌套编排）

当 step 定义了 `crew` 字段而非 `skill` 时：

```js
{
  id: "sub-project",
  crew: "./sub-crew.js",     // 相对路径，指向另一个 crew.js
  input: "shared-data.md",   // 传递给子 DAG 第一个 step 的输入
  output: "final-result.md"  // 子 DAG 最后一个 step 的输出映射回父 DAG
}
```

orchestrator 会自动展开嵌套 DAG，子 step 的 id 加上 `parentId.` 前缀。`--execute` 输出中标记了 `parentStep` 和 `nestedWorkdir`。

### Retry / Fallback 执行

当 command 包含 `retry` 时：

```
1. step 失败 → 检查 retry.max
2. 未达上限 → 等待 retry.delay ms → 重新 spawn sub-agent
3. 达到上限 → 如果有 fallback，切换到 fallback skill 重新执行
4. 无 fallback → 标记失败，继续/终止取决于是否有下游依赖
```

日志：`[CREW] {step} | retrying | {attempt}/{max}` / `[CREW] {step} | fallback | {fallback_skill}`

### 进化式开发（Evolve）

当 command 包含 `evolve.enabled: true` 时：

**默认行为**：`coding-agent`、`deep-research`、`general` 这类创意型 skill 自动开启进化。用户可通过 `evolve: false` 关闭。

**进化流程：**

```
Round 1:
  1. 从当前状态创建 N 个变体（git worktree 或文件副本）
  2. 每个变体独立执行 skill（可注入不同的变异提示）
  3. 评估所有变体的 output（按 criteria 判断质量）
  4. 保留 top K 个（survive），淘汰其余

Round 2（如 rounds > 1）:
  1. 从 survivors 派生新变体（基于 best 的输出 + 变异提示）
  2. 重复执行 → 评估 → 淘汰

最终: 保留最佳变体的 output，继续后续 step
```

**AI 执行流程：**

```
1. 读取 cmd.evolve 配置（variants, rounds, survive, criteria, mutate）
2. Round 1:
   a. 创建 variants 个工作副本（workdir/evolve-{step}/v{1..N}/）
   b. 并行 spawn variants 个 sub-agent
   c. 每个 sub-agent 执行 skill，变异提示: "尝试不同于常规的方法：{mutate}"
   d. 收集所有 output 文件
   e. 评估：按 criteria 比较（如有 criteria 则用 AI 判断，否则按文件大小+完整性）
   f. 保留 survive 个最佳，记录日志: [CREW] {step} | evolve_round | 1/{rounds} | survivors: {survive}/{variants}
3. Round 2+:
   a. 从 survivor 派生新变体
   b. 重复 b-f
4. 将最佳 output 复制回 workdir
```

**评估标准（criteria）示例：**

```js
// 通过测试结果评估
evolve: { criteria: "test-results.md 中测试通过率最高" }

// 通过输出完整性评估（默认）
evolve: { }  // 默认: output 文件大小 + 存在性

// 通过代码质量评估
evolve: { criteria: "代码可读性、错误处理、性能" }
```

**显式配置示例：**

```js
// 默认进化（creative skill 自动开启）
{ id: "implement", skill: "coding-agent", output: "src/index.js" }
// → evolve: { enabled: true, rounds: 1, variants: 2, survive: 1 }

// 自定义进化参数
{ id: "design", skill: "general", output: "docs/design.md",
  evolve: { rounds: 3, variants: 3, survive: 1, mutate: "尝试不同架构模式", criteria: "方案完整性+可行性" } }

// 关闭进化
{ id: "format", skill: "general", output: "docs/formatted.md", evolve: false }
```

**进化 vs 非进化的选择原则：**

| 适用进化 | 不适用进化 |
|----------|-----------|
| 设计/架构（多种方案） | 格式转换（确定性） |
| 代码实现（多种写法） | 测试执行（通过/失败） |
| 研究/搜索（不同角度） | 发布/部署（不可逆） |
| 不确定性高 + 试错成本低 | 确定性高 或 试错成本高 |

## Cron 集成

编排项目可直接通过 cron 定时执行：

```
cron: 0 8 * * *
task: 读取 /tmp/crew-daily-research/crew.js 并按 project-crew 流程编排执行
deliver: telegram -1003840246680
```

在 crew.js 中设置 `await: "human"` 的 step 会被跳过（cron 无人值守），除非 step 也标记了 `cronAwait: true`。

## 数据传递

所有 step 通过 `workdir` 下的文件系统传递数据：
- `input` / `output` 都是相对 workdir 的文件路径
- 编排器负责确保前置 step 的 output 文件就绪后才启动后续 step
- 文件格式由 skill 自行决定（md、json、png 等）

## 错误处理

- 单个 step 失败 → 标记该分支失败，不影响并行其他分支
- 关键路径失败 → 汇报错误，等待用户决策
- 超时 → 终止对应 sub-agent，标记超时
- 用户可在任意点通过审批门干预

## 详细文档

- `references/orchestrator.md` — 编排器算法详细实现
- `references/patterns.md` — 执行模式详解与示例
- `references/skill-registry.md` — 常用 skill 参数格式与执行方式

## 项目生命周期管理（✨ 高级）

### 生命周期概览

```
1. Bootstrap → 创建 Git 仓库、.gitignore、LFS、目录结构
2. Worktrees → 创建 N 个并行开发副本
3. Execute   → 每个 worktree 独立执行 DAG，每步自动 commit（checkpoint）
4. Checkpoint → 关键节点自动保存快照
5. Evolve    → 对比各 worktree 产出，优胜劣汰
6. Merge     → 合并最佳分支到 main
```

### 项目引导（Bootstrap）

```bash
node scripts/project-manager.js --bootstrap crew.js
```

自动完成：
- `git init` + main/dev 分支
- 根据语言生成 `.gitignore`（node/python/rust/go/general）
- 配置 Git LFS（如果定义了 `lfs` 模式）
- 根据 steps 的 output 字段创建目录结构
- 生成 `README.md`（含项目目标和结构说明）
- 初始 commit

### 并行开发（Worktrees）

```bash
# 创建 3 个并行 worktree
node scripts/project-manager.js --worktrees crew.js
```

每个 worktree 是一个独立的 Git worktree：
- 独立分支（`wt-01`, `wt-02`, `wt-03`）
- 独立工作目录
- 各自包含 `crew.js` 副本
- 互不干扰，可并行执行 DAG

**AI 执行流程：**
1. 运行 `--worktrees` 获取 worktree 路径
2. 对每个 worktree 并行 spawn sub-agent
3. 每个 sub-agent 在各自 worktree 中执行 `--execute` 的 commands
4. 每完成一个 step，运行 `--checkpoint` 保存进度

### 检查点（Checkpoint）

```bash
# 自动检查点（每步完成后）
node scripts/project-manager.js --checkpoint crew.js --step "research" --message "research step completed"

# 手动检查点
node scripts/project-manager.js --checkpoint crew.js
```

每个检查点 = 一个 git commit，包含：
- step id（在 commit message 中）
- 时间戳
- 当前所有文件状态

### 状态查看（Status）

```bash
node scripts/project-manager.js --status crew.js
```

输出：
- 当前分支
- 最近 20 个检查点（commit log）
- 所有 worktree 列表
- 并行开发配置

### 回溯（Rollback）

```bash
# 回到某个检查点
node scripts/project-manager.js --rollback crew.js --to abc1234
```

安全机制：
- 回溯前自动创建 `recovery-<timestamp>` 分支
- 不会丢失当前进度
- 可随时从 recovery 分支恢复

### 优胜劣汰（Evolve）

```bash
node scripts/project-manager.js --evolve crew.js
```

评估每个 worktree：
- 检查所有 output 文件是否存在
- 按文件大小/质量打分
- 保留得分 ≥ 最佳 80% 的 worktree（survive）
- 淘汰其余（prune）
- 输出排名和淘汰建议

### 合并（Merge）

```bash
node scripts/project-manager.js --merge crew.js
```

自动：
1. 运行 evolve 找到最佳 worktree
2. 切换到 main 分支
3. 合并最佳分支

### 完整示例：并行开发 AI 项目

```js
// crew.js
module.exports = {
  name: "ai-research-tool",
  goal: "构建一个 AI 驱动的研究工具",
  project: { lang: "node", lfs: ["*.gguf", "*.onnx"] },
  worktrees: 3,                    // 3 个并行开发副本
  evolveStrategy: "best-output",
  steps: [
    { id: "design", skill: "deep-research", params: { topic: "AI research tools", depth: "medium" }, output: "design.md" },
    { id: "implement", skill: "coding-agent", input: "design.md", output: "src/index.js" },
    { id: "test", skill: "coding-agent", input: "src/index.js", output: "test-results.md", loop: { max: 3, until: "所有测试通过" } },
    { id: "docs", skill: "general", input: ["design.md", "test-results.md"], output: "README.md" }
  ]
};
```

**执行流程：**
```
1. --bootstrap → 创建仓库 + .gitignore(node) + LFS(*.gguf,*.onnx) + src/ 目录
2. --worktrees 3 → 创建 wt-01, wt-02, wt-03 三个并行副本
3. 在每个 worktree 中：
   a. design → --checkpoint → implement → --checkpoint → test(loop) → --checkpoint → docs
   b. 每个 checkpoint 是一个 git commit
4. --evolve → 对比 3 个 worktree 的 src/index.js + test-results.md + README.md
5. --merge → 合并最佳分支到 main
```

### 断点续开

当某个 worktree 在 test step 失败时：
```bash
# 查看状态
node scripts/project-manager.js --status crew.js

# 回溯到 test 之前
node scripts/project-manager.js --rollback crew.js --to <implement-checkpoint-hash>

# 修改策略后继续执行 test 及后续步骤
```

## 编排器 CLI

```bash
# 输出执行计划（JSON）
node scripts/orchestrator.js /path/to/crew.js

# 输出结构化执行指令（推荐 — AI 直接按指令执行）
node scripts/orchestrator.js --execute /path/to/crew.js
```

### --execute 模式

`--execute` 输出可直接执行的指令列表，AI 无需手动分析 DAG 或猜参数：

```json
{
  "project": "tech-research-test",
  "workdir": "/tmp/crew-tech-research-test",
  "inferredMode": "pipeline",
  "totalSteps": 2,
  "commands": [
    {
      "step": "search",
      "layer": 0,
      "instruction": "使用 deep-research skill topic='AI 2026', depth='medium'，输出到 research.md",
      "skillRef": "deep-research",
      "params": { "topic": "AI 2026", "depth": "medium" },
      "input": null,
      "output": ["research.md"],
      "validation": "检查 research.md 存在且非空"
    },
    {
      "step": "notion",
      "layer": 1,
      "instruction": "使用 notion skill pageId='xxx'，读取 research.md",
      "skillRef": "notion",
      "params": { "pageId": "xxx" },
      "input": ["research.md"],
      "output": null,
      "validation": null,
      "retry": { "max": 3, "delay": 5000 },
      "fallback": "deep-research"
    }
  ],
  "logTemplate": {
    "format": "[CREW] {{step}} | {{status}} | {{duration}}ms",
    "example": "[CREW] search | success | 42000ms"
  }
}
```

**AI 执行流程：**
1. 运行 `--execute` 获取 commands 列表
2. 按 layer 顺序执行（同层可并行）
3. 每步执行前读取对应 skill 的 SKILL.md
4. 执行后按 `validation` 字段验证结果
5. 按 `logTemplate.format` 输出日志行
6. 失败时按 `retry`/`fallback` 配置处理

### 参数校验

`--execute` 模式自动检查每个 step 的必填参数是否齐全，缺失时在 `warnings` 数组中输出警告。参数定义来自 `references/skill-registry.md`。

## 项目管理 CLI

```bash
# 生命周期
node scripts/project-manager.js --bootstrap <crew.js>    # 创建仓库 + GitHub remote
node scripts/project-manager.js --worktrees <crew.js>    # 创建并行 worktree
node scripts/project-manager.js --checkpoint <crew.js>   # 保存检查点
node scripts/project-manager.js --status <crew.js>       # 查看状态
node scripts/project-manager.js --rollback <crew.js> --to <commit>  # 回溯
node scripts/project-manager.js --evolve <crew.js>       # 优胜劣汰
node scripts/project-manager.js --merge <crew.js>        # 合并最佳
node scripts/project-manager.js --cleanup <crew.js>      # 清理 worktree [--gc]
node scripts/project-manager.js --push <crew.js>         # 推送到远程 [--branch <name>]

# 模板
node scripts/project-manager.js --template              # 列出可用模板
node scripts/project-manager.js --template node-lib     # 生成 crew.js
node scripts/project-manager.js --template fullstack --topic "AI app"
```

### 项目模板

| 模板 | 语言 | 步骤 | 说明 |
|------|------|------|------|
| `node-lib` | Node.js | 5 | 库/包开发（research → design → implement → test → docs） |
| `python-api` | Python | 4 | API 服务（research → implement → test → docs） |
| `fullstack` | Node.js | 6 | 全栈 Web 应用（+ 前后端并行开发） |
| `cli-tool` | Node.js | 4 | CLI 工具（research → implement → test → docs） |
| `rust-lib` | Rust | 4 | Rust 库（research → implement → test → docs） |

模板自动生成：`.gitignore`、`.env.example`、`package.json`/`requirements.txt`/`Cargo.toml`/`Dockerfile`/`docker-compose.yml`（按语言）。

**使用流程：**
```bash
# 1. 从模板生成
node scripts/project-manager.js --template fullstack --topic "AI 代码审查" > crew.js

# 2. 引导项目（创建仓库 + GitHub）
node scripts/project-manager.js --bootstrap crew.js

# 3. 并行开发（3 个 worktree）
node scripts/project-manager.js --worktrees crew.js

# 4. 在每个 worktree 中执行 DAG + checkpoint...

# 5. 优胜劣汰 + 合并
node scripts/project-manager.js --evolve crew.js
node scripts/project-manager.js --merge crew.js

# 6. 推送
node scripts/project-manager.js --push crew.js

# 7. 清理
node scripts/project-manager.js --cleanup crew.js --gc
```

### GitHub 远程集成

在 crew.js 中添加 `github: true` 或 `github: "repo-name"`：

```js
module.exports = {
  name: "my-project",
  github: true,              // 自动创建 GitHub repo（私有）
  // 或:
  github: "my-awesome-repo", // 指定仓库名
  github: { repo: "name", private: false }, // 完整配置
  steps: [...]
};
```

Bootstrap 时自动：`gh repo create` → `git push origin dev`。需要 `gh auth login`。

### 执行日志

执行时按模板输出日志，便于解析和追踪：
```
[CREW] search | running | 0ms
[CREW] search | success | 42000ms
[CREW] notion | running | 0ms
[CREW] notion | failed | 15000ms
[CREW] notion | retrying | 15000ms
[CREW] notion | success | 28000ms
```
