---
name: auto-dev
description: Automated full-stack development pipeline. Orchestrates research → MVP planning → repo creation → Claude Code interactive development with /gsd skill. Use when user says "auto dev", "自动开发", "从零开始做一个", "帮我实现一个项目", or provides a project idea that needs full implementation from scratch.
---

# Auto-Dev Pipeline

OpenClaw as PM/Orchestrator, Claude Code as Developer. Fully autonomous loop until human verification.

## Pipeline Phases

### Phase 1: Research (deep-research skill)

Spawn a sub-agent with `runtime="subagent"` to run deep research on the task:

```
Task: Research "[user's task description]" for MVP implementation.
Output: Technical feasibility, tech stack options, key challenges, existing solutions.
Focus: What's the simplest path to a working MVP?
```

Synthesize research into a concise MVP route (1 paragraph + bullet points).

### Phase 2: Repo Init

1. `gh repo create <project-name> --private --description "..."`
2. `git clone` to workspace temp dir
3. Create `docs/archi/` structure:
   - `docs/archi/REQUIREMENTS.md` - Feature requirements (user stories, acceptance criteria)
   - `docs/archi/ARCHITECTURE.md` - Tech stack, component diagram, data flow
   - `docs/archi/MVP-PLAN.md` - Phased implementation plan with milestones
4. Git commit + push

### Phase 3: GSD 项目初始化 (非交互式)

**关键**: `/gsd:new-project` 使用 AskUserQuestion 进行交互式问答，ACPX 无法处理。
**解决方案**: 用 `gsd-auto-init.cjs` 脚本直接创建所有配置文件，绕过交互式提问。

#### 3a: 运行自动初始化脚本

```bash
node ~/.openclaw/workspace/skills/auto-dev/scripts/gsd-auto-init.cjs \
  --name "项目名" \
  --idea "用户描述的项目idea，越详细越好" \
  --cwd /path/to/project/repo
```

这个脚本会：
- 检查项目状态 (gsd-tools init)
- 创建 `.planning/config.json` (YOLO mode, balanced profile, standard granularity)
- 创建 `.planning/PROJECT.md` (从用户 idea 生成)
- 创建 `.planning/STATE.md` (初始状态)
- 创建 `.planning/Q&A-LOG.json` (**记录所有交互问答的问题、选项和答案**)
- Git 提交所有文件

#### 3b: 发送 Q&A 记录给用户

读取 `.planning/Q&A-LOG.json` 并格式化为飞书卡片消息发送给用户：

```
📋 GSD 项目初始化 — 交互问答记录

已自动完成 [N] 项配置决策：

Q1: 工作模式?
  □ Interactive
  ■ YOLO (自动执行，无需确认)
  → 自动选择: OpenClaw 自动化场景

Q2: 范围切分粒度?
  □ Coarse (3-5 phases)
  ■ Standard (5-8 phases)
  □ Fine (8-12 phases)
  → 自动选择: 平衡的 phase 大小

Q3: AI 模型配置?
  ■ Balanced (Sonnet 级别)
  □ Quality (Opus)
  □ Budget (Haiku)
  → 自动选择: 质量/成本平衡

... [所有问答]

如需修改任何配置，告诉我具体项和你的选择。
```

#### 3c: 运行 GSD 研究→需求→路线图 (使用 Claude Code)

用 ACPX session 启动 Claude Code，发送以下消息：

```
项目已初始化，配置文件在 .planning/ 目录下。
请执行以下步骤完成项目初始化：

1. 运行研究阶段 (不使用 AskUserQuestion):
   - 阅读 .planning/PROJECT.md 了解项目背景
   - 阅读 docs/archi/ 下的架构文档 (如果有)
   - 使用 gsd-tools.cjs 相关工具进行技术栈、功能、架构和陷阱研究
   - 将研究结果写入 .planning/research/ 目录

2. 创建需求文档:
   - 基于研究和 PROJECT.md 创建 .planning/REQUIREMENTS.md
   - 所有 table stakes 功能纳入 v1
   - 差异化功能根据 PROJECT.md 判断

3. 创建路线图:
   - 使用 gsd-tools.cjs 生成路线图
   - 将路线图写入 .planning/ROADMAP.md
   - 每个需求都映射到一个 phase

重要：不要使用 AskUserQuestion 工具！所有决策基于项目描述和最佳实践自主完成。
完成后报告路线图结构。
```

#### 3d: 通知用户路线图并继续执行

发送路线图摘要给用户（仅通知，不等待确认），然后立即继续 Phase 4 执行：

```
🗺️ 项目路线图已生成，自动开始执行

| Phase | 目标 | 需求 |
|-------|------|------|
| 1 | ... | ... |
| 2 | ... | ... |
| 3 | ... | ... |

YOLO 模式，无需确认。执行中...
```

### Phase 4: Claude Code 自动执行

通知用户路线图后（无需等待确认），立即通过 ACPX session 发送：

```
路线图已就绪，请开始自动执行：

1. 运行 /gsd:autonomous --from 1

如果 autonomous 命令因 AskUserQuestion 卡住：
- 改用 /gsd:execute-phase 1 直接执行
- 或者手动按 phase 顺序执行: discuss → plan → execute

每个 phase 完成后报告进度。
```

#### Monitor Loop

**Strategy A: /gsd:autonomous (推荐 - 最省交互)**
- Claude Code 自己跑完所有 phase
- OpenClaw 只需定期 `/gsd:progress` 检查进度
- 适合：需求清晰、MVP 规模的项目

**Strategy B: 逐 phase 控制**
- OpenClaw 依次发送：`/gsd:discuss-phase N --auto` → `/gsd:plan-phase N --auto` → `/gsd:execute-phase N`
- 每个 phase 完成后检查输出再决定下一步
- 适合：需要更细粒度控制的场景

**Strategy C: /gsd:quick (小任务)**
- `/gsd:quick 任务描述`
- 不走完整 milestone 流程
- 适合：bug fix、小功能

#### Steering Decision Framework

| Claude Code Output | OpenClaw Action |
|---|---|
| Phase 完成等待输入 | `/gsd:next` or point to next milestone |
| Error / build fail | `/gsd:debug` or specific fix hint |
| "需要你确认 X" | Decide autonomously based on requirements |
| 上下文快满警告 | `/gsd:pause-work` → wait → `/gsd:resume-work` |
| `/gsd:autonomous` 完成 | `/gsd:verify-work` |
| 项目全部完成 | `/gsd:ship` → Phase 5 |
| 卡住 (3+ retries) | `/gsd:forensics` 分析，必要时通知人类 |

#### Context Continuity (关键)

**不要手动 /clear + 发摘要！** 用 GSD 自带机制：
1. `/gsd:pause-work` — 保存完整上下文到 .planning/
2. `/clear` — 清空 Claude Code 上下文
3. `/gsd:resume-work` — 从 .planning/ 恢复完整上下文

### Phase 5: Human Verification

When all milestones are complete:
1. Run tests if any: `cd <repo> && npm test / pytest etc.`
2. Summarize what was built with repo link
3. Notify human: "项目开发完成，请 review: <repo-url>"
4. Wait for human feedback
5. If changes needed → back to Phase 4 with specific feedback

## 关键约束: AskUserQuestion 处理

**问题**: Claude Code 的 AskUserQuestion 工具需要用户交互式回答，ACPX 无法处理。
**影响命令**: `/gsd:new-project`, `/gsd:discuss-phase`, `/gsd:plan-phase`, `/gsd:settings` 等

**处理策略**:
1. **初始化**: 使用 `gsd-auto-init.cjs` 脚本绕过所有交互
2. **执行阶段**: 优先使用 `--auto` 标志
3. **卡住检测**: 如果 agent 输出超过 60s 无新内容，视为卡住
4. **卡住恢复**: 发送 "请自主决定，不要询问用户" + 具体指示
5. **YOLO 模式**: config.json 中 mode=yolo 减少确认步骤

## Key Commands Reference

```bash
# 自动初始化 (替代 /gsd:new-project)
node ~/.openclaw/workspace/skills/auto-dev/scripts/gsd-auto-init.cjs --name "X" --idea "Y"

# Create repo
gh repo create <name> --private --description "MVP: ..."

# Spawn Claude Code session
sessions_spawn(runtime="acp", mode="session", task="...")

# Send message to Claude Code
sessions_send(sessionKey="...", message="...")

# Read Claude Code output
sessions_history(sessionKey="...", limit=10)

# Check sub-agent status
subagents(action="list")
```

## Safety Rules

- Always create **private** repos by default
- Never commit secrets or API keys
- If Claude Code tries to access external services without context, pause and ask human
- Maximum 10 steering rounds without human check-in — notify progress after 10 rounds
- If any phase fails 3 times, stop and notify human
