# CC Monitor Cron 规范

> 防止多个 CC Monitor cron 并发触发导致 event loop 阻塞、Telegram 轮询饥饿。

## 核心规则

| 规则 | 要求 | 原因 |
|------|------|------|
| **单一活跃** | 最多 1 个 enabled 的 CC Monitor cron | 多个 monitor 并发 agent run 会阻塞 event loop |
| **最低间隔** | ≥ 10 分钟（600000ms） | 短间隔增加 agent run 频率，放大阻塞风险 |
| **payload 类型** | `kind: "systemEvent"` | 避免 embedded agent run（agentTurn 会 spawn 嵌入式 agent，占 10s+ CPU） |
| **sessionTarget** | `"main"` | 复用主会话，不创建隔离 session |
| **wakeMode** | `"now"` 可接受，但结合 systemEvent 使用 | systemEvent 是轻量级系统事件，不会 spawn agent |
| **自清理** | 检测到目标完成/退出时，必须 `cron(action=update, enabled=false)` | 防止已完成的 monitor 持续运行 |

## 创建前检查清单

创建新 CC Monitor cron 前，agent **必须**执行以下步骤：

1. **`cron(action=list)`** — 查看现有 cron jobs
2. **清理同类** — 如果存在同目标的 enabled monitor（名称匹配或目标匹配），先 `cron(action=update, enabled=false)` 禁用旧的
3. **禁用所有其他 CC Monitor** — 如果已有其他 CC Monitor 在运行，评估是否需要先禁用（同一时间只保留 1 个）
4. **创建新 monitor** — 按下方模板创建

## Cron Job 模板

```json
{
  "name": "CC Monitor: <目标名称>",
  "schedule": {
    "kind": "every",
    "everyMs": 600000
  },
  "sessionTarget": "main",
  "wakeMode": "now",
  "payload": {
    "kind": "systemEvent",
    "text": "检查 <目标> Claude Code 进度：\n1. <状态检查命令>\n2. <进度判断逻辑>\n3. 有变化 → 用 message tool 发消息\n4. 无变化 → 不发消息（NO_REPLY）\n5. 目标已退出 → 发送完成通知 + cron(action=update, id=<自身ID>, enabled=false)"
  }
}
```

## 禁止事项

- **禁止** 创建 `kind: "agentTurn"` 类型的 CC Monitor（会 spawn embedded agent，阻塞 event loop）
- **禁止** 同时 enable 2 个以上 CC Monitor cron
- **禁止** 使用 < 10 分钟的间隔
- **禁止** 创建重复 monitor（同目标已有 monitor 时，更新而非新建）

## 故障场景

### 重启后所有 cron 同时触发

`wakeMode: "now"` 意味着 gateway 重启后，所有 pending cron 立即执行。如果同时有多个 CC Monitor：

1. 每个 monitor 触发一次 agent run（~10s CPU）
2. 多个 agent run 并行占满 event loop
3. Telegram getUpdates 轮询被饿死
4. 机器人停止回复

**解决方案**：确保只有 1 个 enabled CC Monitor，且使用 `systemEvent` 而非 `agentTurn`。

### Monitor 不自清理

目标 Claude Code 已完成退出，但 cron 仍在运行。每次触发都执行无意义检查。

**解决方案**：monitor 的 payload **必须**包含退出检测 + 自禁用逻辑。

## 废弃 Cron 清理

定期检查 `cron(action=list)`，清理：
- `enabled: false` 且目标已完成的 monitor → 可删除
- 同名多版本的 monitor（如 `v1.2`, `v1.3`）→ 只保留最新版，删除旧版
- 目标 workspace 已不存在的 monitor → 删除
