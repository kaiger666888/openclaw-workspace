---
name: claude-code-via-openclaw
description: >
  Parameterized Claude Code orchestration through OpenClaw via tmux.
  Supports two modes: NEW project (research → plan → develop → verify) and
  EXISTING project (assess state → plan next steps → execute).
  Uses tmux for session persistence, cron for monitoring.
  Use when: user wants to build/develop a project with Claude Code, or continue work on an existing project.
  NOT for: simple one-liner fixes (just edit), reading code (use read tool),
  thread-bound ACP harness requests (use sessions_spawn with runtime:"acp").
---

# Claude Code via OpenClaw

Parameterized orchestration: gather inputs → choose mode → execute workflow → monitor → report.

## Input Parameters

Before starting, gather these from the user (or infer from context):

| Parameter | Required | Description | Example |
|-----------|----------|-------------|---------|
| `project_idea` | NEW project | What to build | "A CLI tool for managing dotfiles" |
| `project_name` | NEW project | Repo/ directory name | "dotfiles-mgr" |
| `project_dir` | Always | Local path to project | `/home/kai/projects/dotfiles-mgr` |
| `repo_url` | Existing | GitHub repo URL | `https://github.com/user/dotfiles-mgr` |
| `workflow` | Optional | Which workflow to use (default: `gsd`) | `gsd`, `direct`, `batch` |
| `mode` | Optional | `new` or `existing` (auto-detect if omitted) | — |
| `branch` | Optional | Git branch to work on | `feature/auth` |
| `model` | Optional | Claude model override | `claude-sonnet-4-20250514` |

### Workflow Options

| Workflow | Best For | Description |
|----------|----------|-------------|
| **`gsd`** (default) | Full project development | Hierarchical phases: research → plan → execute → verify → ship |
| **`direct`** | Single task / bug fix | One-shot prompt, no project management overhead |
| **`batch`** | Large-scale refactors | Parallel agents in git worktrees via `/batch` |

### Auto-Detection Rules

If `mode` not specified:
- If `project_dir` exists and has `.git/` → **existing**
- If `project_dir` doesn't exist → **new**
- If `repo_url` provided → **existing** (clone first)

---

## Constants

```bash
SESSION_NAME="oc-<project_name>"          # tmux session name
TMUX_CMD="tmux new-session -d -s $SESSION_NAME"
```

---

## Launching Claude Code with tmux

### Why tmux

- **Persistent sessions** — survives OpenClaw restarts, won't be killed by timeout
- **Interactive access** — user can `tmux attach` anytime to interact directly
- **Output capture** — `tmux capture-pane` for monitoring
- **Send input** — `tmux send-keys` to steer Claude Code mid-execution

### Start a Session

```bash
# Create tmux session and launch Claude Code inside it
SESSION_NAME="oc-<project_name>"
PROJECT_DIR="/path/to/project"

tmux new-session -d -s "$SESSION_NAME" \
  "cd $PROJECT_DIR && claude -p --dangerously-skip-permissions '<task description>'"
```

**Key Claude Code flags:**
- `-p, --print` — Non-interactive output mode (required for tmux)
- `--dangerously-skip-permissions` — Bypass permission checks (needed for GSD/workflows)
- `--cwd <dir>` — Working directory (alternative to `cd`)
- `-s <name>` — Named Claude Code session (persists across invocations)
- `--model <model>` — Override default model

### Session Management

```bash
# List tmux sessions
tmux list-sessions

# Attach to session (for manual interaction)
tmux attach -t "$SESSION_NAME"

# Kill session when done
tmux kill-session -t "$SESSION_NAME"

# Check if session is alive
tmux has-session -t "$SESSION_NAME" 2>/dev/null && echo "running" || echo "not running"
```

### Sending Commands to Running Session

```bash
# Send a new prompt to Claude Code (after previous task completes)
tmux send-keys -t "$SESSION_NAME" "claude -p --dangerously-skip-permissions '/gsd:next'" Enter

# Send Ctrl+C to interrupt
tmux send-keys -t "$SESSION_NAME" C-c

# Send text as if typed
tmux send-keys -t "$SESSION_NAME" "/gsd:execute-phase 2" Enter
```

### Capturing Output

```bash
# Check if Claude Code is still running
tmux list-panes -t "$SESSION_NAME" -F '#{pane_current_command}'
# Returns "claude" if running, "bash" or "zsh" if exited
```

---

## Continuous Progress Logging

### pipe-pane: Real-time Output Capture

Use `tmux pipe-pane` to continuously stream Claude Code output to a log file:

```bash
SESSION_NAME="oc-<project_name>"
LOG_DIR="/tmp/oc-logs"
LOG_FILE="$LOG_DIR/${SESSION_NAME}.log"
mkdir -p "$LOG_DIR"

# Start continuous logging (runs in background, captures everything, strips ANSI)
tmux pipe-pane -t "$SESSION_NAME" "sed 's/\x1b\[[0-9;]*[a-zA-Z]//g' >> $LOG_FILE"

# Stop logging
tmux pipe-pane -t "$SESSION_NAME"
```

This captures ALL output in real-time — every token Claude Code produces goes to the log file immediately.

### Progress Tracking Script

Use the progress tracker to detect milestones and send targeted updates:

```bash
# Run progress tracker (continuous, checks log every 30s)
SESSION_NAME="oc-<project_name>"
LOG_FILE="/tmp/oc-logs/${SESSION_NAME}.log"
STATE_FILE="/tmp/oc-logs/${SESSION_NAME}.state"

# Check progress: what's new since last check?
PROGRESS=$(tail -100 "$LOG_FILE" | grep -v "^$" | tail -20)
LAST_LINE=$(tail -1 "$LOG_FILE")

# Detect completion: Claude Code exited
IS_RUNNING=$(tmux list-panes -t "$SESSION_NAME" -F '#{pane_current_command}' 2>/dev/null)
if [ "$IS_RUNNING" != "claude" ]; then
  echo "COMPLETED"
fi

# Detect GSD milestones
grep -oP '(Phase \d+|✓|✅|Error|FAIL|milestone|PR created)' "$LOG_FILE" | tail -5
```

### Smart Monitoring Cron

Instead of blind polling, use a smart cron that only reports on **changes**:

```bash
cron action=add --job '{
  "name": "CC Progress: <SESSION_NAME>",
  "schedule": {"kind": "every", "everyMs": 60000},
  "payload": {
    "kind": "agentTurn",
    "message": "检查 Claude Code 进度 <SESSION_NAME>：\n1. 读 /tmp/oc-logs/<SESSION_NAME>.state 获取上次进度位置\n2. 读 /tmp/oc-logs/<SESSION_NAME>.log 从上次位置之后的新内容（已自动过滤ANSI）\n3. 检测关键事件（Phase完成/错误/PR创建/退出）\n4. 有新进展 → 汇报关键变化（不超过5行），更新 state 文件\n5. 无新内容但仍在运行 → 不发消息\n6. Claude Code 已退出 → 发送完成通知，附最后30行输出\n\n重要：只在有实质性变化时才发消息。不要重复报告相同内容。",
    "timeoutSeconds": 30
  },
  "sessionTarget": "current",
  "delivery": {"mode": "announce", "channel": "<channel>", "to": "<target>"}
}'
```

### Progress State File Format

`/tmp/oc-logs/<SESSION_NAME>.state` tracks what's been reported:

```json
{
  "session": "oc-myproject",
  "logOffset": 12345,
  "lastReport": "2026-05-09T18:30:00+08:00",
  "lastMilestone": "Phase 2 complete",
  "reportedLines": ["Phase 1 complete", "Phase 2 started"],
  "status": "running"
}
```

### Key Patterns to Detect

| Pattern | Meaning | Action |
|---------|---------|--------|
| `Phase N complete` / `Phase N done` | Phase finished | Report + send next command |
| `Error` / `FAIL` / `failed` | Something broke | Alert user with context |
| `PR created` / `opened PR` | Work shipped | Report with PR link |
| `pane_current_command != claude` | Process exited | Final report + cleanup |
| `AskUserQuestion` | Stuck on prompt | Send autonomous decision |
| No new output for 5+ min | Possible hang | Check and report |
| Tool call patterns `[Edit]` `[Write]` | Active coding | No report needed (noise) |

### Log File Lifecycle

```bash
# Start of project
mkdir -p /tmp/oc-logs
tmux pipe-pane -t "$SESSION_NAME" "cat >> /tmp/oc-logs/${SESSION_NAME}.log"

# During project: log grows automatically, cron reads incrementally

# End of project: archive or delete
tmux pipe-pane -t "$SESSION_NAME"  # stop logging
# Optional: keep log for debugging, or delete
rm -f /tmp/oc-logs/${SESSION_NAME}.log /tmp/oc-logs/${SESSION_NAME}.state
```

---

## Mode: NEW Project

Full pipeline from idea to working code.

### Phase 1: Research

Spawn a sub-agent for deep research:

```
Task: Research "<project_idea>" for MVP implementation.
Output: Technical feasibility, tech stack options, key challenges, existing solutions.
Focus: What's the simplest path to a working MVP?
```

Synthesize into concise MVP route (1 paragraph + bullet points). Send summary to user.

### Phase 2: Repo Init

```bash
# Create repo
gh repo create <project_name> --private --description "MVP: <project_idea>"

# Clone and scaffold
git clone <repo_url> <project_dir>
cd <project_dir>
mkdir -p docs/archi

# Create architecture docs
# docs/archi/REQUIREMENTS.md - User stories, acceptance criteria
# docs/archi/ARCHITECTURE.md  - Tech stack, component diagram, data flow
# docs/archi/MVP-PLAN.md     - Phased implementation with milestones
```

Git commit + push. Notify user with repo URL.

### Phase 3: GSD Init

GSD's `/gsd:new-project` uses interactive prompts — can't use directly.
Use the auto-init script instead:

```bash
node ~/.openclaw/workspace/skills/auto-dev/scripts/gsd-auto-init.cjs \
  --name "<project_name>" \
  --idea "<project_idea>" \
  --cwd <project_dir>
```

This creates `.planning/` artifacts: `PROJECT.md`, `config.json`, `STATE.md`, `Q&A-LOG.json`.

Send Q&A decisions to user as a summary card (don't wait for reply, just inform).

### Phase 4: Research → Requirements → Roadmap

```bash
SESSION_NAME="oc-<project_name>"

tmux new-session -d -s "$SESSION_NAME" \
  "cd <project_dir> && claude -p --dangerously-skip-permissions \
  '项目已初始化，配置在 .planning/ 目录。请完成：1. 阅读 .planning/PROJECT.md 和 docs/archi/ 了解项目背景 2. 研究技术栈、功能和架构陷阱，写入 .planning/research/ 3. 创建 .planning/REQUIREMENTS.md（v1/v2/out-of-scope）4. 使用 gsd-tools 生成 .planning/ROADMAP.md。重要：不要使用 AskUserQuestion！所有决策自主完成。'"
```

### Phase 5: Execute

**Strategy A: Autonomous (recommended for MVP)**
```bash
tmux send-keys -t "$SESSION_NAME" "claude -p --dangerously-skip-permissions '/gsd:autonomous --from 1'" Enter
```

**Strategy B: Phase-by-phase (more control)**
```bash
# For each phase N:
tmux send-keys -t "$SESSION_NAME" "claude -p --dangerously-skip-permissions '/gsd:execute-phase <N>'" Enter
```

Send roadmap summary to user, then immediately start execution (YOLO mode).

### Phase 6: Verify & Ship

```bash
tmux send-keys -t "$SESSION_NAME" "claude -p --dangerously-skip-permissions '/gsd:verify-work'" Enter
# After verification:
tmux send-keys -t "$SESSION_NAME" "claude -p --dangerously-skip-permissions '/gsd:ship'" Enter
```

Run project tests, summarize what was built, send repo URL to user for review.

---

## Mode: EXISTING Project

Assess current state, plan next steps, execute.

### Phase 1: Assess

```bash
# Check if GSD project
if [ -f "<project_dir>/.planning/STATE.md" ]; then
  cat <project_dir>/.planning/STATE.md
  cat <project_dir>/.planning/ROADMAP.md
else
  cd <project_dir> && git log --oneline -20
fi
```

### Phase 2: Plan

**For GSD projects:**
```bash
SESSION_NAME="oc-<project_name>"
tmux new-session -d -s "$SESSION_NAME" \
  "cd <project_dir> && claude -p --dangerously-skip-permissions '/gsd:progress'"
```

Based on progress, decide next action via `tmux send-keys`:
- In-progress phase → `/gsd:execute-phase <N>`
- All phases done → `/gsd:verify-work` → `/gsd:ship`
- Stuck → `/gsd:debug <description>`

**For plain repos:**
```bash
tmux new-session -d -s "$SESSION_NAME" \
  "cd <project_dir> && claude -p --dangerously-skip-permissions '/gsd:map-codebase'"
```

Then plan based on user's task.

### Phase 3: Execute

| Scenario | Command |
|----------|---------|
| Continue GSD phase | `/gsd:execute-phase <N>` |
| New feature | Direct prompt with detailed task |
| Bug fix | `/gsd:do <description>` |
| Large refactor | `/batch <instruction>` |
| Quick fix | `/gsd:fast <task>` |

---

## Monitoring

### Setup Cron

Create a cron job that checks tmux session status and output:

```bash
cron action=add --job '{
  "name": "CC Monitor: <SESSION_NAME>",
  "schedule": {"kind": "every", "everyMs": 300000},
  "payload": {
    "kind": "agentTurn",
    "message": "检查 Claude Code 进度：\n1. tmux has-session -t <SESSION_NAME> 确认是否运行\n2. 运行中 → tmux capture-pane -t <SESSION_NAME> -p -S -50 | tail -30 查看最新输出，汇报进展\n3. pane_current_command 不是 claude → 报告\"任务已结束\"，附最后50行输出\n\n每次必须发消息，禁止不发消息。保持简短（3行内）。",
    "timeoutSeconds": 60
  },
  "sessionTarget": "current",
  "delivery": {"mode": "announce", "channel": "<channel>", "to": "<target>"}
}'
```

### Check Intervals by Phase

| Phase | Interval | Expected Duration |
|-------|----------|-------------------|
| Research | 5 min | 10-30 min |
| GSD Init | 5 min | 5-10 min |
| Roadmap | 5 min | 5-15 min |
| Execute phase | 3 min | 15-60 min |
| Autonomous run | 5 min | 30-120 min |
| Verify | 5 min | 5-15 min |

### Teardown

**Always disable monitoring when task completes:**
```bash
cron action=update --jobId <id> --patch '{"enabled": false}'
tmux kill-session -t "$SESSION_NAME"
```

### Steering Decision Framework

| Claude Code Output | OpenClaw Action (via tmux send-keys) |
|---|---|
| Phase complete, waiting | `/gsd:next` |
| Error / build fail | `/gsd:debug` or specific fix hint |
| "需要你确认 X" | Decide autonomously, send guidance |
| Context full warning | `/gsd:pause-work` → later `/gsd:resume-work` |
| Stuck (3+ retries) | `/gsd:forensics`, notify human if needed |
| All done | `/gsd:verify-work` → `/gsd:ship` |

---

## Context Continuity

**Never manually /clear + send summary!** Use GSD's built-in mechanism:
1. `/gsd:pause-work` — saves full context to `.planning/`
2. `/clear` — clear Claude Code context
3. `/gsd:resume-work` — restores from `.planning/`

---

## AskUserQuestion Handling

Claude Code's `AskUserQuestion` tool requires interactive input — can't use with `-p` mode.

**Prevention:**
- Init: use `gsd-auto-init.cjs` script (bypasses all interactive prompts)
- Execution: prefer `/gsd:autonomous`, `/gsd:fast`
- Config: set `mode: yolo` in `.planning/config.json`

**Recovery (if Claude Code gets stuck):**
- Send via tmux: specific guidance message
- If stuck: `tmux send-keys -t "$SESSION_NAME" C-c` to interrupt, then re-prompt

---

## Critical Lessons

- **tmux is the launch method** — persistent, monitorable, interactive
- **Always use `-p --dangerously-skip-permissions`** for automated workflows
- **One command per tmux send-keys** — wait for previous to complete before sending next
- **Check pane_current_command** to detect if Claude Code exited
- **Cron prompt must be minimal** (~50 words) and forbid NO_REPLY
- **Always disable monitoring cron** when task completes
- **Self-verify outputs** before reporting to user
- **Screenshots**: use `deviceScaleFactor: 3` + `asDocument=true`
- **Forum groups**: always specify `threadId` when using message tool

---

## Reference

- [acpx-cli.md](references/acpx-cli.md) — Legacy acpx reference (deprecated, use tmux + claude CLI)
- [troubleshooting.md](references/troubleshooting.md) — Common issues and solutions
