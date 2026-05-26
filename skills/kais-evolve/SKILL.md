---
name: kais-evolve
description: Universal autonomous iterative research framework. Inspired by karpathy/kais-evolve. AI agent modifies code, runs experiments, keeps/discards based on metrics. Works with any project that has a measurable outcome and fast feedback loop.
metadata:
  clawdbot:
    always: false
    skillKey: kais-evolve
---

# Autoresearch — 通用自主迭代研究框架

> AI 驱动的实验进化系统：假设 → 实验 → 验证 → 迭代
> 借鉴 karpathy/kais-evolve，泛化到任何可量化、可快速验证的项目

---

## 核心原理

```
传统开发：  人类想方案 → 手动改代码 → 手动测试 → 手动判断 → 下一轮
Autoresearch：AI想方案 → 自动改代码 → 自动跑测试 → 自动判断 → 循环
```

本质上是一个**有智能引导的进化算法**：
- **变异** = AI 改代码/配置/prompt
- **选择** = 指标是否改善
- **遗传** = 好的改动保留，差的丢弃
- **智能引导** = AI 能读懂代码、理解报错、组合历史经验

---

## 快速开始

### 方式 1：AI 辅助生成（推荐）

让 AI 先分析项目，自动生成研究规则，人类只需审阅确认。

```bash
# 1. 在项目根目录初始化
python ~/.openclaw/workspace/skills/kais-evolve/scripts/init-project.py

# 2. 让 AI 分析项目并生成 project.md 草案
#    在 Claude Code 中说：
#    "Run `python ~/.openclaw/workspace/skills/kais-evolve/scripts/init-project.py --analyze-only .`
#     then read the analysis, generate kais-evolve/project.md, and present it to me for review."

# 3. 人类审阅 → 修改 → 确认 → 开始跑实验
```

### 方式 2：手动配置

```bash
# 1. 初始化
python ~/.openclaw/workspace/skills/kais-evolve/scripts/init-project.py /path/to/project --type [type]

# 2. 手动编辑 project.md

# 3. 启动实验
```

### 方式 3：全自动化（已验证的项目）

```bash
# 直接让 Claude Code 读 project.md 开始跑
claude --dangerously-skip-permissions
# → "Read kais-evolve/project.md and start the experiment loop"
```

---

## 文件结构

初始化后项目根目录会生成：

```
kais-evolve/
├── project.md          # 🎯 研究配置（你编辑这个）
├── results.tsv         # 📊 实验结果记录
└── experiments/        # 📁 实验日志目录
    └── .gitkeep
```

### 研究规则设计（两阶段流程）

### 第一阶段：AI 分析项目

运行 `--analyze-only` 获取项目结构分析：

```bash
python scripts/init-project.py --analyze-only /path/to/project
```

AI 会输出：
- 项目类型和技术栈
- 目录结构和关键文件
- 可用的构建/测试命令
- 建议的可编辑区域
- 推荐的优化指标

### 第二阶段：AI 生成 project.md

基于分析结果，AI 生成 project.md 草案，包含：

1. **优化目标** — 基于项目类型推荐合理的优化方向
2. **实验命令** — 从现有 scripts/build commands 中选择
3. **指标解析** — 定义如何从输出中提取数值
4. **可编辑范围** — 基于目录结构智能推断
5. **初始实验想法** — 3-5 个有针对性的起点
6. **时间预算** — 根据指标类型推荐（编译类短、训练类长）

### 人类审阅清单

```
✅ 目标是否明确？AI 是否理解了你想优化什么？
✅ 指标是否可量化？能从命令输出中稳定提取？
✅ 实验命令是否正确？能在你的环境跑通？
✅ 可编辑范围是否合理？有没有遗漏或过度开放？
✅ 时间预算是否合适？太长浪费，太短不稳定
✅ Guard rail 是否充分？改了代码还能正常跑测试吗？
✅ 初始想法是否有价值？还是需要自己补充方向？
```

修改确认后，AI 开始跑实验循环。

---

## project.md（核心配置）

这是你唯一需要编辑的文件。它定义了"研究什么"和"怎么研究"。

```markdown
# Autoresearch Project

## Goal
[一句话描述优化目标]

## Metric
- Primary: [主要指标名，越低/越高越好]
- Command: [运行实验的命令]
- Parse: [如何从输出中提取指标，grep 模式或 JSON path]

## Scope
- Editable: [agent 可以修改的文件/目录]
- Read-only: [agent 不能修改的文件]
- No new dependencies: [true/false]

## Constraints
- Time budget: [每次实验的最大时间，秒]
- Memory: [内存限制，可选]
- Simplicity: [简洁性偏好描述]

## Baseline
- Command: [运行基线的命令]
- Expected metric: [基线指标值]

## Ideas
- [可选] 给 agent 一些初始方向
```

### results.tsv（自动生成）

```tsv
commit	metric	memory_mb	status	description
abc1234	0.95	512	keep	baseline
def5678	0.93	520	keep	increase batch size
ghi9012	0.96	510	discard	try new activation
jkl3456	0.00	0	crash	double model size (OOM)
```

---

## 项目类型模板

init 脚本会根据项目类型生成不同的 project.md 模板。

### 1. Web 性能优化
```markdown
## Metric
- Primary: Lighthouse performance score (higher is better)
- Command: npx lighthouse http://localhost:3000 --output=json --chrome-flags="--headless"
- Parse: $.categories.performance.score

## Scope
- Editable: src/components/**, src/utils/**, next.config.*, webpack.config.*
- Read-only: public/**, tests/**
```

### 2. API 响应时间
```markdown
## Metric
- Primary: P99 latency in ms (lower is better)
- Command: k6 run --duration 30s scripts/load-test.js
- Parse: grep "p(99)" output

## Scope
- Editable: src/routes/**, src/middleware/**, config/**
```

### 3. 机器学习模型
```markdown
## Metric
- Primary: validation loss (lower is better)
- Command: python train.py --epochs 1 --fast
- Parse: grep "val_loss" output
```

### 4. CLI 工具速度
```markdown
## Metric
- Primary: execution time in ms (lower is better)
- Command: hyperfine "cargo run -- input.txt" --runs 10
- Parse: grep "Mean" output
```

### 5. Prompt 工程
```markdown
## Metric
- Primary: eval score (higher is better)
- Command: python eval.py --prompt-file prompts/current.txt
- Parse: grep "score:" output

## Scope
- Editable: prompts/**, src/pipeline.py
```

---

## Agent 指令（写入 project.md 的后半部分）

以下内容会被自动追加到 project.md，指导 AI agent 如何操作：

```markdown
## Experiment Loop

LOOP FOREVER (until human stops you):

1. Read the current git state (branch, commit)
2. Look at results.tsv for what's been tried and what worked
3. Form a hypothesis based on:
   - Previous successful experiments (keep patterns)
   - Previous near-misses (combining partial wins)
   - Code understanding (reading the editable files)
   - Domain knowledge (common optimization techniques)
4. Implement the change by editing files in the Editable scope
5. git commit with a descriptive message
6. Run the experiment command
7. Parse the metric from output
8. Record in results.tsv:
   - If improved: status=keep, advance the branch
   - If worse or equal: status=discard, git reset
   - If crash: status=crash, log error, try to fix or skip
9. Go to step 1

## Rules

- NEVER STOP. Keep going until human interrupts.
- NEVER ask "should I continue?" — the answer is always yes.
- NEVER modify files outside the Editable scope.
- NEVER install new dependencies (unless explicitly allowed).
- If crash: read the error, fix if trivial, skip if fundamental.
- If stuck: re-read code, try combining previous near-misses, try radical changes.
- Simplicity wins: removing code for equal performance > adding code for tiny gains.
- Time budget: kill experiments that exceed the time limit, treat as crash.

## Productivity Tips

- Each experiment takes [TIME_BUDGET] minutes
- You can run ~[60/TIME_BUDGET] experiments per hour
- Overnight (~8 hours) = ~[480/TIME_BUDGET] experiments
- Review results.tsv periodically to avoid repeating failed experiments
```

---

## 与 Claude Code 集成

### 方式 1：直接在项目目录启动

```bash
cd /path/to/your/project
claude --dangerously-skip-permissions

# 然后说：
# "Read kais-evolve/project.md and start the experiment loop."
```

### 方式 2：通过 OpenClaw 后台运行

```bash
# 使用 acpx 启动 Claude Code 后台任务
acpx run --cwd /path/to/project \
  --prompt "Read kais-evolve/project.md and follow the experiment loop instructions. Start with the baseline, then iterate autonomously." \
  --timeout 8h
```

### 方式 3：通过 OpenClaw session_spawn

```
让 Clawd 在后台启动一个 Claude Code session，持续跑实验
```

---

## 高级特性

### 1. 多指标评估

```markdown
## Metrics
- Primary: P99 latency (lower, weight 60%)
- Secondary: error rate (lower, weight 30%)
- Tertiary: memory usage (lower, weight 10%)
- Combined: weighted average of normalized scores
```

### 2. 回归测试门控

```markdown
## Guard Rails
- Must pass: npm test
- Must pass: python -m pytest tests/
- Failing tests = automatic discard (even if metric improved)
```

### 3. 分阶段研究

```markdown
## Phases
- Phase 1 (experiments 1-20): Explore — try diverse approaches, no idea is too crazy
- Phase 2 (experiments 21-50): Exploit — double down on what worked, fine-tune
- Phase 3 (experiments 51+): Combine — merge successful ideas, try interactions
```

### 4. 多 Agent 协作

```markdown
## Team
- Agent A: Focus on architecture changes
- Agent B: Focus on hyperparameter tuning
- Agent C: Focus on data pipeline optimization
- Each on separate git branch, periodically compare results
```

---

## 搜索降级策略

当需要搜索外部信息时：
1. `web_search` — 首选
2. `web_fetch` — 抓取具体页面
3. 基于代码理解 — 如果搜索不可用

---

## 注意事项

1. **必须有可量化的指标** — 这是选择压力的来源
2. **实验必须足够快** — 每次实验 < 10 分钟，理想 1-5 分钟
3. **搜索空间要可控** — 明确 agent 能改什么、不能改什么
4. **保留进化历史** — results.tsv 是最有价值的产出之一
5. **定期人工审查** — 即使全自动，偶尔看看 agent 在做什么
6. **简洁性偏好** — 防止 agent 用复杂 hack 换微小提升

---

## 触发词

- "帮我自动优化 [项目]"
- "启动 kais-evolve"
- "让 AI 自动迭代 [目标]"
- "kais-evolve [项目路径]"
- " overnight 实验 [项目]"
