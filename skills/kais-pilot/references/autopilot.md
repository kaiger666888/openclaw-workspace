# Autopilot Mode — 无人值守自动驾驶

## 概述

Autopilot 让 kais-pilot 在时间窗口内自动完成多个开发主题，无需人工干预。

## 架构

```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│   Config    │────→│  Scheduler   │────→│  Executor    │
│ (crew.js)   │     │ (cron one-shot)│    │ (kais-pilot) │
└─────────────┘     └──────┬───────┘     └──────┬───────┘
                           │                      │
                    ┌──────▼───────┐      ┌───────▼──────┐
                    │  Watchdog   │      │  Checkpoint  │
                    │ (cron 30min)│      │ (.json file) │
                    └──────────────┘      └──────────────┘
```

## 执行流程详解

### 1. 初始化

```js
// 读取 crew.js
const config = require(crewPath);

// 创建 checkpoint
writeCheckpoint({
  topics: config.autopilot.topics.map(t => ({ ...t, status: "pending" })),
  currentTopic: null,
  completedTopics: [],
  failedTopics: [],
  startTime: Date.now(),
});

// 启动看门狗
createWatchdogCron(config.autopilot.schedule.stallTimeout);
```

### 2. 迭代循环

每个主题作为独立的 cron session 执行（隔离上下文，避免 token 累积）：

```
检查安全条件:
  - 当前时间在 schedule.window 内？
  - 连续失败数 < maxRetries？
  - 还有 pending 主题？

选择下一个主题:
  - 有 checkpoint → 从断点继续
  - 无 checkpoint → 选择第一个 pending

生成该主题的 crew.js:
  - 有 crewTemplate → 基于模板生成
  - 无模板 → 基于主题描述自动生成（复用 Smart Mode）

执行 kais-pilot 编排:
  - 读取对应 skill 的 SKILL.md
  - 按 DAG 执行所有 step
  - 默认走 GSD 工作流

评估结果:
  - pass: 所有 output 存在且验证通过
  - needs-fix: 部分失败，可重试
  - blocked: 需要人工干预

汇报进度:
  - 更新 checkpoint
  - 发送进度通知到 notifyChannel
  - 调度下一次迭代（one-shot cron）
```

### 3. 结束

```
结束条件:
  - 所有主题完成 → 生成最终报告
  - 时间窗口结束 → 保存 checkpoint，下次恢复
  - 连续失败达上限 → 通知用户，暂停

清理:
  - 删除看门狗 cron
  - 生成最终 report.md
  - 推送到 GitHub（如配置）
```

## Checkpoint 格式

```json
{
  "version": 1,
  "topics": [
    { "id": "auth", "status": "completed", "startedAt": "...", "completedAt": "..." },
    { "id": "crud", "status": "in-progress", "startedAt": "...", "currentStep": "implement" },
    { "id": "notify", "status": "pending" }
  ],
  "stats": {
    "totalTopics": 3,
    "completed": 1,
    "failed": 0,
    "totalDuration": "15min"
  }
}
```

## Watchdog 机制

```json
{
  "name": "kais-pilot:watchdog:<project>",
  "schedule": { "kind": "every", "everyMs": 1800000 },
  "payload": {
    "kind": "agentTurn",
    "message": "检查 kais-pilot autopilot 状态：读取 .autopilot-checkpoint.json，对比上次更新时间。如果超过 stallTimeout 未更新，发送告警到 notifyChannel。",
    "timeoutSeconds": 60
  },
  "sessionTarget": "isolated",
  "delivery": { "mode": "announce" }
}
```

## 安全保护

| 保护项 | 机制 |
|--------|------|
| 时间窗口 | 只在 window 内执行 |
| 连续失败 | 达 maxRetries 后暂停 |
| 卡死检测 | watchdog 每 30min 检查 |
| 上下文隔离 | 每个主题独立 cron session |
| 回滚 | checkpoint 支持恢复到任意主题 |

## 进度通知格式

```
🚀 kais-pilot Autopilot 进度汇报

📊 总体：2/5 主题完成
✅ auth — JWT 认证模块（3min）
✅ crud — 任务 CRUD API（5min）
🔄 notify — 通知系统（执行中，step: implement）
⏳ export — 数据导出
⏳ docs — API 文档

⏱️ 已运行：12min | 预计剩余：~8min
```
