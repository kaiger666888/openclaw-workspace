---
name: kais-pilot
description: "Intelligent task orchestration and project lifecycle management. Graph is orchestration — define skills with input/output dependencies, auto-analyze DAG, pick optimal execution strategy. Supports pipeline, fan-out, map-reduce, approval gates, event loops, nested DAG, git worktree parallel development, checkpoint/resume, and evolutionary selection. Smart Mode: automatic team assembly and crew.js generation from natural language goals. Autopilot Mode: unattended multi-topic development with cron-driven iteration loop and watchdog. Use when user says 全自动模式, autopilot, 别问我了全搞定, 帮我做一个项目, 开干, 拉个团队, build this, 自动驾驶, 无人值守, 持续开发, or presents a multi-step goal without providing crew.js."
---

# Kai's Pilot — 智能任务编排与项目管理

**核心理念：图即编排。** 定义 skill 间数据依赖，编排器自动推断最优执行策略。

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

## 智能模式（Smart Mode）

用户说出目标但未提供 crew.js 时触发。触发词："全自动模式", "autopilot", "帮我做一个项目", "开干", "build this"。

### 流程

```
用户目标 → 复杂度判断(Solo/Team) → [brainstorm] → 组建团队+选策略
→ 生成 crew.js → 架构图(Mermaid→Notion) → 项目初始化 → 执行 → 优化循环 → 验证+交付 → 开发报告
```

**Solo**（<5min，单 skill）→ 直接执行，不生成 crew.js。

**Team**（多步骤）→ 进入完整流程：
1. 方向不清 → 先 brainstorm
2. 读取 `references/team-members.md` 选 skill 组合
3. **默认执行代理：`claude-code-via-openclaw`**（所有代码生成/开发 step 默认使用）
4. 按任务类型自动配置策略（见下表）
5. 生成 crew.js（含 evolve/loop/retry 配置）
6. 生成架构图（Mermaid 格式）→ 写入 Notion
7. 执行并生成 `workdir/report.md`

### 策略自动选择

| 任务类型 | 并行 | 进化 | 循环 | Git | 模板 |
|---------|------|------|------|-----|------|
| 研究/分析 | ✅ 多角度 | ✅ | ❌ | ❌ | ❌ |
| 开发/实现 | ✅ 前后端 | ✅ | ✅ 测试 | ✅ | ✅ 匹配时 |
| 内容生产 | ✅ 多平台 | ✅ | ❌ | ❌ | ❌ |
| 快速脚本 | ❌ | ❌ | ❌ | ❌ | ❌ |

### Self-Resolution

单步失败不 halt 整个项目：retry → 换 skill → 换方案 → skip（记录每次尝试到 decisions 数组）。

## 项目定义规范

### 基本结构

```js
module.exports = {
  name: "项目名称",           // 必填
  goal: "项目目标描述",       // 推荐
  workdir: "/tmp/crew-xxx",  // 可选，默认 /tmp/crew-<name>/
  env: { KEY: "value" },     // 可选
  steps: [...]               // 必填
};
```

### 扩展字段

```js
project: { lang: "node", lfs: ["*.onnx"] },  // 语言 + LFS
worktrees: 3,                                   // 并行 worktree 数
evolveStrategy: "best-output",                  // best-output / most-commits
github: true,                                   // 自动创建 GitHub repo
```

### Step 定义

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | string | 唯一标识 |
| `skill` | string | skill 名称 |
| `input` | string\|string[] | 依赖的 step output |
| `output` | string\|string[] | 产出文件 |
| `params` | object | 传给 skill 的参数 |
| `mode` | string | 强制执行模式 |
| `await` | string | `"human"` = 审批门 |
| `loop` | object | `{ max: 10, until: "quality >= 8" }` |
| `timeout` | number | 超时秒数 |
| `retry` | object\|number | `{ max: 3, delay: 5000 }` |
| `fallback` | string | 失败时替代 skill |
| `evolve` | object | `{ rounds: 2, variants: 2, survive: 1, criteria: "..." }` |
| `parallel` | number | 并行度限制（默认 4） |
| `workflow` | string | 开发工作流模式（默认 `gsd`，可选 `direct`） |

无 `input` 字段 → 起始节点。`input` 字符串 → 等价单元素数组。

## 开发工作流（GSD 集成）

当 step 的 `skill` 为 `claude-code-via-openclaw` 时，默认走 **GSD 结构化开发流程**。

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

**`workflow: "direct"`** — 自由文本 prompt，适用于简单任务/快速修复。

**params 传递规则：**

| workflow | params 内容 | 示例 |
|----------|-----------|------|
| `gsd` | 项目需求描述 | `{ requirement: "构建 REST API，支持 JWT 认证" }` |
| `direct` | 完整任务指令 | `{ task: "在 src/auth.js 中添加 OAuth2 回调处理" }` |

## 执行模式

编排器从依赖图自动推断，`mode` 字段可覆盖：

| 模式 | 图特征 | 示例 |
|------|--------|------|
| **pipeline** | 全串行链 | A → B → C |
| **fan-out** | 并行独立分支 | A → (B, C, D) |
| **map-reduce** | 多分支汇合 | (A, B) → C |
| **approval** | 有 `await:"human"` | 暂停等人工 |
| **event-loop** | 有环依赖 | 循环直到条件 |
| **dag** | 复杂图 | 通用拓扑排序 |

详见 `references/patterns.md`。

## 编排流程

```
加载 crew.js → 创建 workdir → 分析 DAG → 拓扑排序 → 按层 spawn sub-agents
→ 同层完成 → 下一层 → await 暂停 / loop 重试 → 汇总结果
```

- 失败 → retry / fallback 降级
- 每步完成后自动 checkpoint（`.checkpoint.json`）

**⚠️ 分批执行（强制）**：同层步骤数超过 `maxParallel` 时，必须分批 spawn。例如同层有 6 个步骤、`maxParallel=4`，则先 spawn 4 个，完成后再 spawn 剩余 2 个。**严禁一次性 spawn 超过 `maxParallel` 个 sub-agent。**

## 并发安全

**默认并发上限：4 个同时运行的 sub-agent。** 超过会触发 LLM provider 限流。

| 并发数 | 结果 |
|--------|------|
| ≤4 | ✅ 稳定 |
| >4 | ⚠️ 触发限流（空返回） |

额外保护：`parallel` 字段可按 step 调低。evolve `variants` 不应超过全局 `parallel`。

## Sub-Agent 监控

启动 sub-agent 后，创建 cron 监控任务：

```json
{
  "name": "kais-pilot:monitor:<task>",
  "schedule": { "kind": "every", "everyMs": 900000 },
  "sessionTarget": "current",
  "payload": {
    "kind": "systemEvent",
    "text": "检查 kais-pilot 活跃 sub-agent：subagents list + sessions_history。有进度变化就汇报，没有就 NO_REPLY。"
  }
}
```

任务完成/终止时 `cron remove`。

## 优化循环（Optimization Loop）

**项目级别的测试→评估→优化→再测试循环，自动确定迭代轮数，避免过度优化。**

> **追求足够好，而非完美。** 过度优化投入大、收益递减、引入新风险。

### 触发条件

- `optimize: true`（默认对开发型项目开启）
- `optimize: false` 可显式关闭
- 研究/内容型项目默认关闭

### 双重评估机制

**指标评估（客观）：**

| 指标 | 采集方式 | 健康阈值 |
|------|---------|---------|
| 测试通过率 | `test` step 产出 | ≥90% |
| 构建/编译 | `build` step 产出 | 零错误 |
| 代码质量 | lint/type-check | 零警告 |
| 性能基准 | benchmark output | 不退化 |
| 产出完整性 | 文件存在+非空 | 100% |

**AI 评估（主观）：**

| 维度 | 评分标准 | 权重 |
|------|---------|------|
| 功能完整度 | 目标需求覆盖率 | 30% |
| 代码质量 | 可读性、结构、错误处理 | 25% |
| 架构合理性 | 模块划分、依赖关系 | 20% |
| 可维护性 | 文档、命名、复杂度 | 15% |
| 边界处理 | 边界情况、异常路径 | 10% |

### 收敛判断（何时停止）

三个条件满足任一即停止：

1. **改进收敛**：连续 2 轮综合评分改进 < 5%
2. **已达优秀**：综合评分 ≥ 8.5 且所有关键指标通过
3. **硬性上限**：最多 5 轮

### 过度优化防护

- **改进建议去重**：跨轮次追踪已应用的改进，避免重复优化同一问题
- **回归检测**：每轮对比前一版本的指标，发现退化立即回滚
- **成本意识**：记录每轮耗时，如果单轮耗时 > 首轮的 2 倍，发出警告
- **质量倒退保护**：如果 AI 评分连续下降，立即停止并回滚到最佳版本

### crew.js 配置

```js
optimize: {
  enabled: true, maxRounds: 5,
  convergenceThreshold: 0.05, convergenceRounds: 2,
  targetScore: 8.5, metrics: ["test", "build", "lint"], rollback: true,
},
```

### 与现有机制的关系

| 机制 | 级别 | 作用 |
|------|------|------|
| `loop` | step 级 | 单步骤内部循环（如测试→修复） |
| `evolve` | step 级 | 多变体并行，优胜劣汰 |
| **`optimize`** | **项目级** | **所有 step 完成后的整体优化循环** |

执行顺序：`evolve`（step内）→ `loop`（step内）→ `optimize`（项目级）

## 架构图生成（Architecture Diagrams）

**每个项目自动生成标准 UML 架构图，输出 Mermaid 格式到 Notion 页面。**

### 图表类型（按需生成）

| 图表 | Mermaid 语法 | 何时生成 |
|------|-------------|---------|
| 系统架构图 | `graph TD` | 所有项目 |
| DAG 执行流程图 | `graph LR` | 所有项目 |
| 时序图 | `sequenceDiagram` | 多组件交互 |
| 状态图 | `stateDiagram-v2` | 状态流转 |
| 类图 | `classDiagram` | OOP 项目 |
| ER 图 | `erDiagram` | 有数据模型 |

### Mermaid 格式规范（Beautiful-Mermaid）

遵循 `Mermaid美丽核心原则`（Notion: 32811082af8e80d4a793dfb53875d948）：

**配色系统**：深色主题，五色分层
- 🔵 蓝 `#3b82f6`：接入/配置层
- 🟣 紫 `#8b5cf6`：控制/状态层
- 🟢 绿 `#10b981`：处理/核心层
- 🔷 青 `#06b6d4`：外部/网络层
- 🟠 橙 `#f97316`：完成/通知层

**视觉规范**：线条 3-5px，语义化命名，subgraph 分层

**Notion 输出**：每个 Mermaid 图作为 `code` 块（语言 `mermaid`），图前 heading_2 标题，图后 paragraph 说明。

### 配置

```js
architectureDiagrams: {
  enabled: true,              // 默认 true
  notionPageId: "xxx",        // 输出 Notion 页面
  diagrams: ["system", "dag"], // 指定图表类型（可选，默认自动判断）
},
```

## Autopilot Mode（无人值守自动驾驶）

提供一次配置，系统在时间窗口内自动完成多个开发主题，持续汇报进度。

**触发词**: "自动驾驶", "autopilot on", "无人值守模式", "帮我持续开发"

### 用户需要提供

- **开发主题列表**（topics）
- **GitHub 仓库**
- **时间窗口**（何时开发）
- **汇报通道**（telegram/feishu，可选）

### 配置示例

```js
module.exports = {
  name: "my-autopilot-project",
  goal: "构建一个任务管理系统",
  github: "kai/task-system",
  autopilot: {
    topics: [
      { id: "auth", name: "用户认证", description: "JWT + OAuth2.0" },
      { id: "crud", name: "任务CRUD", description: "RESTful API + 权限控制" },
    ],
    schedule: { window: "02:00-06:00", stallTimeout: "30min" },
    parallelAgents: 3,
    report: { notifyChannel: "telegram" },
    maxRetries: 3,
  },
  project: { lang: "node" },
  workdir: "/tmp/crew-myproject",
};
```

### 执行流程

1. **初始化** — 生成 crew.js（如未提供），创建 checkpoint，启动看门狗 cron
2. **迭代循环**（每次为隔离 cron session）：
   - 检查安全（时间窗口、连续失败数）
   - 选择下一个主题（断点续传 → 下一个 pending）
   - 生成/加载该主题的 crew.js，复用 kais-pilot 编排执行
   - AI 评估结果（pass / needs-fix / blocked）
   - 汇报进度，保存 checkpoint
   - 调度下一次 one-shot cron（完成驱动）
3. **结束** — 窗口到 / 全部完成 → 生成最终报告，清理 cron

### 关键字段

| 字段 | 说明 |
|------|------|
| `topics` | 开发主题队列，按顺序执行 |
| `schedule.window` | 活跃时间窗口 `HH:MM-HH:MM` |
| `schedule.stallTimeout` | 卡死检测阈值 |
| `parallelAgents` | 单主题并行 sub-agent 数（默认 3） |
| `report.notifyChannel` | 进度汇报通道 |
| `maxRetries` | 单主题最大重试（默认 3） |
| `crewTemplate` | 主题开发步骤模板（可选，自动生成） |

### 调度机制

- **完成驱动**: 当前迭代完成后立即调度下一次（one-shot cron）
- **看门狗兜底**: 每 30min 检查是否卡死，异常时通知用户
- **Checkpoint 持久化**: `workdir/.autopilot-checkpoint.json`，支持断点续传

> 📖 完整文档见 [`references/autopilot.md`](references/autopilot.md)

## 高级模式执行指南（AI 必须遵循）

### Approval Gate（人工审批）

```
1. 执行到该 step 时，先完成所有前置 step
2. 收集 await.reviewFiles 列出的文件内容
3. 向用户发送审批请求，包含进度、待审批内容、审批问题
4. 等待用户回复（✅ 继续 / ❌ 终止 / ✏️ 修改意见）
```

**Cron 模式下**：`await.cronSkip: true` 的 step 自动跳过。

### Event Loop（事件循环）

```
执行 step → 检查产出 → 评估 loop.until 条件
→ 达标 → 继续 / 未达标且 < loop.max → 重试 / 达上限 → 记录状态
```

### Nested DAG（嵌套编排）

```js
{
  id: "sub-project",
  crew: "./sub-crew.js",
  input: "shared-data.md",
  output: "final-result.md"
}
```

### Retry / Fallback

step 失败 → retry → 达上限 → fallback → 无 fallback → 标记失败

### 进化式开发（Evolve）

`coding-agent`、`deep-research`、`claude-code-via-openclaw` 自动开启进化。用户可通过 `evolve: false` 关闭。

```
创建 N 变体 → 并行执行 → 评估质量 → 保留 top K → 下一轮（如 rounds > 1）
```

## Cron 集成

crew.js 可通过 cron 定时执行。`await:"human"` 的 step 自动跳过（cron 无人值守），除非 `cronAwait: true`。

## 数据传递

所有 step 通过 `workdir` 文件系统传递数据。文件格式由 skill 自行决定。

## 错误处理

- 单个 step 失败 → 标记该分支失败，不影响并行其他分支
- 关键路径失败 → 汇报错误，等待用户决策
- 超时 → 终止对应 sub-agent，标记超时

## 项目生命周期管理

```
1. Bootstrap → 创建 Git 仓库、.gitignore、LFS、目录结构
2. Worktrees → 创建 N 个并行开发副本
3. Execute   → 每个 worktree 独立执行 DAG，每步自动 commit
4. Checkpoint → 关键节点自动保存快照
5. Evolve    → 对比各 worktree 产出，优胜劣汰
6. Merge     → 合并最佳分支到 main
```

### 项目模板

| 模板 | 语言 | 步骤 |
|------|------|------|
| `node-lib` | Node.js | 5（research → design → implement → test → docs） |
| `python-api` | Python | 4（research → implement → test → docs） |
| `fullstack` | Node.js | 6（+ 前后端并行开发） |
| `cli-tool` | Node.js | 4 |
| `rust-lib` | Rust | 4 |

## 编排器 CLI

```bash
# 输出结构化执行指令
node scripts/orchestrator.js --execute /path/to/crew.js

# 项目管理
node scripts/project-manager.js --bootstrap <crew.js>
node scripts/project-manager.js --worktrees <crew.js>
node scripts/project-manager.js --checkpoint <crew.js>
node scripts/project-manager.js --status <crew.js>
node scripts/project-manager.js --evolve <crew.js>
node scripts/project-manager.js --merge <crew.js>
node scripts/project-manager.js --push <crew.js>
node scripts/project-manager.js --template [name]
```

## 执行日志

```
[CREW] search | running | 0ms
[CREW] search | success | 42000ms
[CREW] notion | retrying | 15000ms
[CREW] notion | success | 28000ms
```

## 详细文档

- `references/orchestrator.md` — DAG 构建与模式推断算法
- `references/patterns.md` — 执行模式详解与示例
- `references/team-members.md` — Skill 能力矩阵与调度规则
- `references/skill-registry.md` — 常用 skill 参数格式
- `references/autopilot.md` — Autopilot 无人值守模式

### CLI 参考

```bash
# 编排器
node scripts/orchestrator.js <crew.js>           # 分析 DAG
node scripts/orchestrator.js --execute <crew.js>  # 输出执行指令

# 项目管理
node scripts/project-manager.js --bootstrap|--worktrees|--checkpoint|--status|--evolve|--merge|--push|--cleanup <crew.js>
node scripts/project-manager.js --template [name] # 列出/生成模板
```

### 进化式开发参考

`evolve` 字段控制 step 级别的多变体并行开发：

| 配置 | 默认值 | 说明 |
|------|--------|------|
| `enabled` | 创意型 skill 自动开启 | 手动控制 |
| `rounds` | 1 | 进化轮次 |
| `variants` | 2 | 每轮变体数（不超过 `parallel`） |
| `survive` | 1 | 每轮保留数 |
| `criteria` | 文件大小+完整性 | 评估标准 |
| `mutate` | "" | 变异提示词 |

项目级进化（worktree）详见上方"项目生命周期管理"章节。
