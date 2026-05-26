# OpenClaw 指挥 Claude Code 全自动化开发：深度研究报告

> 调研日期：2026-03-27 | 搜索轮次：4 | 思考深度：deep
> 来源：官方文档、GitHub 仓库、社区讨论、技术博客

---

## 一、核心概念

### 1.1 两层架构

OpenClaw 指挥 Claude Code 的自动化涉及两层：

```
┌─────────────────────────────────────────────┐
│  编排层：OpenClaw (Agent Orchestrator)        │
│  - 接收自然语言任务描述                        │
│  - 分解任务、管理会话、监控进度                 │
│  - 错误处理、重试、通知                        │
└──────────────────┬──────────────────────────┘
                   │ ACP Protocol / CLI
                   ▼
┌─────────────────────────────────────────────┐
│  执行层：Claude Code (Coding Agent)           │
│  - 代码阅读、编写、重构                       │
│  - 运行命令、测试、Git 操作                   │
│  - 多文件编辑、项目初始化                     │
└─────────────────────────────────────────────┘
```

### 1.2 两条路径

OpenClaw 与 Claude Code 交互有两条路径：

| 路径 | 方式 | 适用场景 |
|------|------|----------|
| **CLI 直接调用** | `claude -p/--print` 命令 | 一次性任务、脚本集成、CI/CD |
| **ACP 协议** | `sessions_spawn runtime:"acp"` | 持久会话、线程绑定、多轮对话 |

---

## 二、Claude Code 自动化能力详解

### 2.1 CLI 模式（`-p` / `--print`）

`-p` 标志使 Claude Code 以非交互模式运行，这是自动化的基础：

```bash
# 基础用法
claude -p "What does the auth module do?"

# 自动批准工具（关键！）
claude -p "Run the test suite and fix any failures" \
  --allowedTools "Bash,Read,Edit"

# 审查暂存更改并提交
claude -p "Look at my staged changes and create an appropriate commit" \
  --allowedTools "Bash(git diff *),Bash(git log *),Bash(git status *),Bash(git commit *)"
```

#### `--bare` 模式（推荐用于脚本）

跳过所有自动发现（hooks、skills、plugins、MCP servers），确保可复现：

```bash
claude --bare -p "Summarize this file" --allowedTools "Read"
```

#### 权限控制

```bash
# bypassPermissions - 跳过所有权限确认（最高自主性）
claude --permission-mode bypassPermissions -p "Build the entire feature"

# allowedTools - 精细控制哪些工具可用
claude -p "Fix the bug" --allowedTools "Read,Edit,Bash(npm test *)"

# Auto Mode (2026年3月新功能) - AI 分类器自动判断安全级别
claude --enable-auto-mode
# 然后按 Shift+Tab 切换到 Auto Mode
```

### 2.2 Agent SDK（Python / TypeScript）

Anthropic 提供了完整的 SDK，支持结构化输出、工具审批回调、流式响应：

**Python 示例：**

```python
import claude_code_sdk

# 基础调用
query = "Refactor all API routes to use the new error-handling middleware"
async for message in claude_code_sdk.run(query, cwd="/path/to/project"):
    if message.type == "assistant":
        print(message.content)
    elif message.type == "tool_use":
        print(f"Tool: {message.name}")

# 带权限回调
async for message in claude_code_sdk.run(
    query,
    cwd="/path/to/project",
    allowed_tools=["Read", "Edit", "Bash"],
):
    pass
```

**TypeScript 示例：**

```typescript
import { run } from "@anthropic-ai/claude-code";

for await (const message of run("Build a REST API", { cwd: "./project" })) {
  if (message.type === "assistant") {
    console.log(message.content);
  }
}
```

### 2.3 结构化输出

```bash
# JSON 输出
claude -p "Summarize this project" --output-format json

# JSON Schema 约束
claude -p "Extract function names from auth.py" \
  --output-format json \
  --json-schema '{"type":"object","properties":{"functions":{"type":"array","items":{"type":"string"}}},"required":["functions"]}' \
  | jq '.structured_output'
```

### 2.4 会话延续

```bash
# 使用 --continue 延续之前的对话
claude -p "Now add tests for the feature you just built" --continue
```

### 2.5 Hooks 系统

Hooks 是 Python/TypeScript 回调函数，在 Claude Code 代理循环的特定节点触发：

```python
HookEvent = Literal[
    "PreToolUse",           # 工具执行前
    "PostToolUse",          # 工具执行后
    "PostToolUseFailure",   # 工具执行失败
    "UserPromptSubmit",     # 用户提交提示
    "Stop",                 # 停止执行
    "SubagentStop",         # 子代理停止
    "PreCompact",           # 消息压缩前
    "Notification",         # 通知事件
    "SubagentStart",        # 子代理启动
    "PermissionRequest",    # 权限决策
]
```

**实际 Hook 示例：**

```python
# .claude/settings.json 中的 hooks 配置
# 自动格式化 Python 代码
hooks = {
    "PostToolUse": [
        {
            "matcher": "Edit",
            "hooks": [{"type": "command", "command": "black $FILE"}]
        }
    ]
}
```

---

## 三、OpenClaw 编排层详解

### 3.1 CLI 直接调用方式（coding-agent skill）

OpenClaw 通过 `exec` 工具直接调用 Claude Code CLI：

```bash
# 前台执行
bash workdir:~/project command:"claude --permission-mode bypassPermissions --print 'Your task'"

# 后台执行（推荐用于长时间任务）
bash workdir:~/project background:true command:"claude --permission-mode bypassPermissions --print 'Your task'"
# 返回 sessionId，通过 process 工具监控

# 带自动通知
bash workdir:~/project background:true command:"claude --permission-mode bypassPermissions --print 'Build REST API.

When completely finished, run: openclaw system event --text \"Done: Built REST API\" --mode now'"
```

**关键要点：**
- Claude Code **不需要 PTY**（与 Codex/Pi/OpenCode 不同）
- 使用 `--permission-mode bypassPermissions` 而非 `--dangerously-skip-permissions`
- `--print` 模式保持完整工具访问且无需交互确认

### 3.2 ACP 协议方式（acp-router skill）

通过 ACP (Agent Client Protocol) 实现更结构化的集成：

```json
// sessions_spawn 调用
{
  "task": "Build a user authentication module with JWT",
  "runtime": "acp",
  "agentId": "claude",
  "thread": true,
  "mode": "session"
}
```

**ACP 支持的 agentId 映射：**
- `claude` → Claude Code
- `codex` → Codex
- `pi` → Pi Coding Agent
- `opencode` → OpenCode
- `gemini` → Gemini CLI
- `kimi` → Kimi CLI

**acpx CLI 直接使用：**

```bash
ACPX_CMD="./extensions/acpx/node_modules/.bin/acpx"

# 持久会话
${ACPX_CMD} claude sessions show oc-claude-${conversationId} \
  || ${ACPX_CMD} claude sessions new --name oc-claude-${conversationId}

${ACPX_CMD} claude -s oc-claude-${conversationId} --cwd /path/to/project --format quiet "Your prompt"

# 一次性
${ACPX_CMD} claude exec --cwd /path/to/project --format quiet "Your prompt"

# 取消
${ACPX_CMD} claude cancel -s oc-claude-${conversationId}
```

### 3.3 线程绑定

ACP 会话可以绑定到聊天线程（Discord/Telegram），实现多轮对话：

```json5
// 配置示例
{
  agents: {
    list: [{
      id: "claude",
      runtime: {
        type: "acp",
        acp: {
          agent: "claude",
          backend: "acpx",
          mode: "persistent"
        }
      }
    }]
  }
}
```

---

## 四、全自动化工作流设计

### 4.1 从需求到代码交付的完整流程

```
1. 任务接收
   └── 用户自然语言描述 → OpenClaw 解析意图

2. 任务分解
   └── OpenClaw 将大任务拆分为子任务
   └── 确定依赖关系和执行顺序

3. 环境准备
   └── 创建临时 git worktree（并行任务）
   └── 或在目标项目目录中执行

4. 编码执行
   └── 通过 CLI 或 ACP 启动 Claude Code
   └── 提供详细的任务描述和约束

5. 进度监控
   └── process:log 检查输出
   └── process:poll 检查状态
   └── 自动通知（openclaw system event）

6. 质量保证
   └── 运行测试
   └── 代码审查（可启动第二个 Claude Code 会话）
   └── 检查 lint 和类型

7. 交付
   └── Git commit + push
   └── 创建 PR（gh pr create）
   └── 通知用户完成
```

### 4.2 并行任务编排（git worktree 模式）

```bash
# 1. 创建 worktrees
git worktree add -b fix/issue-78 /tmp/issue-78 main
git worktree add -b fix/issue-99 /tmp/issue-99 main

# 2. 并行启动 Claude Code（后台执行）
bash workdir:/tmp/issue-78 background:true \
  command:"claude --permission-mode bypassPermissions --print 'Fix issue #78: user login fails on Safari. Add test and commit.'"

bash workdir:/tmp/issue-99 background:true \
  command:"claude --permission-mode bypassPermissions --print 'Fix issue #99: API rate limiting not working. Add test and commit.'"

# 3. 监控
process action:list

# 4. 创建 PRs
cd /tmp/issue-78 && git push -u origin fix/issue-78
gh pr create --head fix/issue-78 --title "fix: Safari login issue" --body "..."

# 5. 清理
git worktree remove /tmp/issue-78
git worktree remove /tmp/issue-99
```

### 4.3 错误处理和重试

```bash
# 在任务描述中内置错误处理指令
claude --permission-mode bypassPermissions --print '
Build the feature. If you encounter errors:
1. Read the error message carefully
2. Check if dependencies need to be installed (npm install / pip install)
3. If a test fails, fix the code and re-run
4. If stuck after 3 attempts, describe what you tried and where you are stuck
5. Always commit working code before attempting risky changes
'
```

### 4.4 代码审查工作流

```bash
# 启动审查（在临时目录中安全操作）
REVIEW_DIR=$(mktemp -d)
git clone https://github.com/user/repo.git $REVIEW_DIR
cd $REVIEW_DIR && gh pr checkout 130

bash workdir:$REVIEW_DIR background:true \
  command:"claude --permission-mode bypassPermissions --print 'Review this PR. Check for bugs, security issues, and code quality. Provide a detailed review.'"

# 清理
trash $REVIEW_DIR
```

---

## 五、与其他工具的对比

### 5.1 综合对比表

| 维度 | OpenClaw + Claude Code | Claude Code 单独使用 | Cursor | Windsurf |
|------|----------------------|---------------------|--------|----------|
| **自动化程度** | ★★★★★ 全自动编排 | ★★★★ 需手动启动 | ★★★ 需人工引导 | ★★★★ Cascade 半自动 |
| **多任务并行** | ✅ git worktree + 多进程 | ❌ 单任务 | ❌ 单任务 | ❌ 单任务 |
| **远程/移动控制** | ✅ Telegram/Discord/Web | ❌ 本地终端 | ❌ 桌面 IDE | ❌ 桌面 IDE |
| **会话持久化** | ✅ ACP 线程绑定 | ⚠️ --continue 有限 | ✅ 项目级 | ✅ 项目级 |
| **错误恢复** | ✅ 自动重试 + 人工介入 | ❌ 手动处理 | ⚠️ 部分自动 | ⚠️ 部分自动 |
| **代码推理深度** | ★★★★★ Claude 原生能力 | ★★★★★ | ★★★★ | ★★★★ |
| **SWE-bench** | ~80.9% (Claude) | ~80.9% | ~72% | ~65% |
| **成本** | API 用量 + Claude Max | Claude Max $100-200/月 | $20-40/月 | $15/月 |

### 5.2 核心优势

**OpenClaw + Claude Code 的独特价值：**
1. **7×24 自动化**：从 Telegram/Discord 远程触发任务，无需打开电脑
2. **多代理编排**：同时运行多个 Claude Code 实例处理不同任务
3. **智能路由**：自然语言描述任务，OpenClaw 自动选择最佳执行方式
4. **进度监控**：后台执行 + 实时通知，不用盯着终端
5. **混合代理**：可以同时调度 Claude Code、Codex、Pi 等不同代理

**社区共识（2026年2-3月多个评测）：**
> "Cursor 用于日常内联编辑，Claude Code 用于复杂架构会话，Windsurf 用于不需要人工干预的全代理自主性。"
> "对于单独开发者想要最大 AI 杠杆：Claude Code with Max plan。没有什么能匹配它在复杂多文件变更上的自主处理能力。"

---

## 六、实际案例和最佳实践

### 6.1 案例：全功能实现（零审批）

```
Prompt: "Implement a new user analytics dashboard using React + Tailwind. Include tests, update README, and commit with conventional message."

Claude Code Auto Mode 执行：
→ 规划任务架构
→ 创建组件文件
→ 编写样式和逻辑
→ 编写测试
→ 运行测试确认通过
→ 更新 README
→ Git commit（零人工介入）
```

### 6.2 案例：大规模重构

```
Prompt: "Refactor all API routes to use our new error-handling middleware. Update tests and run full suite."

结果：Auto Mode 处理 200+ 工具调用而不中断流程。
```

### 6.3 最佳实践清单

1. **始终在 git 仓库中运行** — 便于回滚
2. **使用 `--bare` 模式用于 CI/脚本** — 确保可复现
3. **结合沙箱隔离** — 文件系统 + 网络隔离
4. **监控 token 使用** — 长任务前用 `/context` 检查
5. **不要在生产服务器上运行** — 使用隔离的 dev 环境
6. **OpenClaw 编排时添加完成通知** — `openclaw system event`
7. **使用 git worktree 并行处理** — 避免分支冲突
8. **在 Claude Code 任务描述中内置错误处理逻辑**
9. **审查任务永远在临时目录中** — 不要污染工作目录
10. **利用 Hooks 自动化格式化和测试**

---

## 七、行动建议

### 立即可做

1. **安装并配置 Claude Code CLI**
   ```bash
   npm install -g @anthropic-ai/claude-code
   claude --enable-auto-mode  # 启用 Auto Mode
   ```

2. **在 OpenClaw 中测试基础调用**
   ```
   用 Claude Code 创建一个 hello world Express 应用，放到 ~/Projects/test-app
   ```

3. **设置 acpx**
   ```bash
   cd ~/.nvm/versions/node/v24.13.0/lib/node_modules/openclaw/extensions/acpx
   npm install --omit=dev
   ./node_modules/.bin/acpx --version
   ```

### 进阶实践

4. **构建自动化流水线**：需求 → OpenClaw 分解 → Claude Code 执行 → 测试 → PR
5. **配置 ACP 线程绑定**：在 Telegram 中绑定 Claude Code 会话，实现远程开发
6. **编写自定义 Hooks**：PostToolUse 自动格式化、PreToolUse 阻止危险操作
7. **设置并行 worktree 工作流**：同时处理多个 issue

### 长期规划

8. **建立项目模板**：CLAUDE.md + Hooks + CI 配置，一键初始化新项目
9. **构建多代理团队**：OpenClaw 编排 Claude Code（编码）+ Codex（审查）+ Pi（测试）
10. **探索 Agent SDK Python/TypeScript**：更精细的控制和回调

---

## 八、关键资源

- [Claude Code 官方文档 - Headless 模式](https://code.claude.com/docs/en/headless)
- [Claude Agent SDK 概览](https://platform.claude.com/docs/en/agent-sdk/overview)
- [OpenClaw ACP 文档](https://docs.openclaw.ai/tools/acp-agents)
- [acpx GitHub](https://github.com/openclaw/acpx)
- [Claude Code Hooks 教程 (DataCamp)](https://www.datacamp.com/tutorial/claude-code-hooks)
- [Claude Code SDK Python](https://github.com/anthropics/claude-agent-sdk-python)
- [Claude Code SDK TypeScript Examples](https://github.com/anthropics/claude-code-sdk-typescript-examples)
- [Claude Code GitHub Actions](https://apidog.com/blog/a-comprehensive-guide-to-the-claude-code-sdk/)
