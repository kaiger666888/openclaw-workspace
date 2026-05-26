---
name: kais-monitor
version: 1.0.0
description: "多场景进度监控 skill。当需要监控 subagent、tmux、Claude Code、exec 后台任务、cron 定时任务等运行状态时使用。触发词：'监控' '进度' '状态' '查看任务' '查看运行' '监控进度' '任务进度' '运行状态' 'subagent状态' '查看subagent' 'tmux状态' '查看tmux' 'claude code进度' '后台任务' '定时任务' 'monitor' '任务跑到哪了' '有什么在运行' '全部状态' '环境监控'"
---

# kais-monitor

多场景运行进度监控工具——一个入口查看所有正在执行的任务。

## 概述

集中监控 OpenClaw 环境中各类正在运行的任务和进程，提供统一的进度视图。

支持的监控场景：
- **Subagent 任务**：通过 `subagents list` + `sessions_list` 查看子代理状态
- **Tmux 会话**：通过 SSH 连接 Worker Node 查看远程 tmux 会话
- **Claude Code 开发**：在 tmux 中检查 Claude Code 会话的当前工作状态
- **Exec 后台任务**：通过 `process list` 查看本地后台命令
- **Cron 任务**：通过 `cron list` 查看定时任务状态

## 触发场景

- 当用户说 "监控", "进度", "状态", "查看任务", "看板" 等短词
- 当用户说 "任务跑到哪了", "有什么在运行", "进度怎么样"
- 当用户说 "subagent/tmux/claude code/后台/定时任务 + 状态/进度"
- 当用户说英文 "monitor", "status", "what's running", "check progress"
- 当需要快速了解当前环境整体工作状态时

## 前置条件

- OpenClaw 正在运行（本机 subagent/exec/cron 监控）
- Worker Node 可达（远程 tmux/Claude Code 监控，需 SSH）
- Worker Node 信息：见 TOOLS.md "高配机" 条目

## 监控命令

<!-- FREEDOM:low -->

### 1. Subagent 监控

```bash
# 查看当前会话的 subagent
# 使用 subagents tool: action=list
```

通过 `subagents(action=list)` 获取正在运行的子代理，关注：
- `status`：running / completed / failed
- `task`：任务描述
- `elapsed`：运行时长
- `model`：使用的模型

如果 subagent 有具体 sessionKey，用 `sessions_history(sessionKey, limit=5)` 查看最近输出。

### 2. Tmux 会话监控（Worker Node）

```bash
ssh kai@192.168.71.38 "tmux list-sessions 2>/dev/null && echo '---' && tmux list-windows -a 2>/dev/null"
```

获取所有 tmux 会话和窗口列表。对每个活跃会话，查看最新输出：

```bash
ssh kai@192.168.71.38 "tmux capture-pane -t <session>:<window> -p | tail -30"
```

重点关注：
- Claude Code 会话：看最后几行输出判断是否在等待输入
- 训练/推理任务：看进度条或日志输出
- 异常状态：看是否有错误信息或进程退出

### 3. Claude Code 开发监控

在 tmux 中识别 Claude Code 会话（窗口名含 `claude` 或进程名含 `claude`）：

```bash
ssh kai@192.168.71.38 "tmux list-panes -a -F '#{session_name}:#{window_index}.#{pane_index} #{pane_current_command}' | grep -i claude"
```

捕获 Claude Code 会话的当前状态：

```bash
ssh kai@192.168.71.38 "tmux capture-pane -t <session:window> -p | tail -40"
```

判断 Claude Code 状态：
- **活跃中**：有工具调用输出或代码生成中
- **等待输入**：显示 `> ` 提示符或等待确认
- **已完成**：显示最终结果或回到命令行
- **报错**：有 ERROR/FAILED 等关键字

### 4. Exec 后台任务监控

通过 `process(action=list)` 查看本地后台 exec 会话。

关注：
- `sessionId`：会话标识
- `command`：正在运行的命令
- `status`：running / exited
- `elapsed`：运行时长

### 5. Cron 任务状态

通过 `cron(action=list)` 查看已配置的定时任务。

关注：
- `enabled`：是否启用
- `lastRun` / `nextRun`：上次/下次执行时间
- `status`：任务执行状态

<!-- /FREEDOM:low -->

## 输出格式

<!-- FREEDOM:high -->

监控结果以简洁的状态卡片形式呈现，按场景分组。每个场景一行标题 + 子项列表，异常 ❌、长时间 ⚠️、正常 ✅。完整模板见 [输出格式模板](references/output-format.md)。

<!-- /FREEDOM:high -->

## 快速监控模式

当用户只说 "监控" 或 "状态" 时，执行全量扫描（所有场景）。

当用户指定场景时（如 "查看 subagent"），只扫描对应场景：

| 用户说 | 扫描范围 |
|--------|---------|
| "subagent 状态" / "查看子代理" | 仅 Subagent |
| "tmux 状态" / "查看 tmux" | 仅 Tmux 会话 |
| "claude code 进度" / "CC 状态" | 仅 Claude Code |
| "后台任务" / "exec 状态" | 仅 Exec 后台 |
| "定时任务" / "cron 状态" | 仅 Cron |
| "监控" / "全部状态" / "进度" | 全量扫描 |

## 注意事项

- SSH 连接 Worker Node 可能超时，设置 `timeoutMs: 10000`
- tmux capture-pane 只返回可见区域，长输出需要 `tmux capture-pane -S -300` 增加缓冲区
- Claude Code 状态判断基于文本启发式，不保证 100% 准确
- 如果 Worker Node 不可达，跳过远程监控并标注 ⚠️

## CC Monitor Cron 管理

当需要创建定时监控 Claude Code 进度的 cron 任务时，**必须遵守**以下规范。完整规则见 [Cron Monitor 规范](references/cron-monitor-guide.md)。

### 铁律

1. **同时最多 1 个** enabled 的 CC Monitor cron
2. **间隔 ≥ 10 分钟**（禁止 3 分钟、5 分钟）
3. **必须用 `systemEvent`**，禁止 `agentTurn`（会 spawn embedded agent 阻塞 event loop）
4. **必须自清理** — 目标退出时 `cron(action=update, enabled=false)` 禁用自身

### 创建流程

1. `cron(action=list)` 查看现有 monitor
2. 禁用所有其他 CC Monitor（`cron(action=update, enabled=false)`）
3. 创建新 monitor（用 systemEvent payload）

### 反面教材

```
❌ 两个 CC Monitor 同时 enabled，间隔 5 分钟，wakeMode=now
→ 重启时两个 agent run 同时触发 → event loop 阻塞 → Telegram 不回复
```

## 参考文档

- [Worker Node 配置](references/worker-node.md)
- [状态判断规则](references/status-heuristics.md)
- [输出格式模板](references/output-format.md)
- [Cron Monitor 规范](references/cron-monitor-guide.md)
