# 输出格式模板

## 标准监控卡片

```
📊 环境监控 [HH:MM]

🤖 Subagent (N个运行中)
  ├─ [session-key] task描述... ⏱ Xm ✅
  └─ [session-key] task描述... ⏱ 35m ⚠️

🖥️ Tmux (N个活跃会话)
  ├─ session:window — 描述 ⏱ 状态 ✅
  └─ session:window — 描述 ⏱ 状态 ❌

🔧 Claude Code (N个会话)
  ├─ session:window — 🟢 active
  └─ session:window — 🟡 waiting

⚡ 本地任务 (N个后台)
  ├─ command... ⏱ Xm ✅
  └─ command... ⏱ Xm ⚠️

⏰ 定时任务 (N个启用)
  ├─ 任务名 — 上次: HH:MM / 下次: HH:MM
  └─ 任务名 — 上次: HH:MM / 下次: HH:MM
```

## 状态标记

| 标记 | 含义 |
|------|------|
| ✅ | 正常运行 |
| ⚠️ | 运行时间较长（5-30min）或需要关注 |
| ⚠️⚠️ | 运行时间过长（>30min），建议检查 |
| 🔴 | 运行超过 1h，高度关注 |
| ❌ | 异常/报错 |
| 🟢 | Claude Code 活跃中 |
| 🟡 | Claude Code 等待输入 |
| ⏸️ | Claude Code 空闲 |

## 精简模式（单场景）

当用户只查询单个场景时，省略标题头，直接输出该场景的子项：

```
🤖 Subagent (2个运行中)
  ├─ [cleanup] 清理临时文件... ⏱ 3m ✅
  └─ [research] 搜索论文... ⏱ 12m ⚠️
```

## 空状态

如果某场景无运行中的任务：

```
🤖 Subagent — 无运行中任务
```

## 异常汇总

当有异常任务时，在卡片末尾追加异常摘要：

```
⚠️ 异常 (2)
  ├─ tmux:train-gpu — 进程已退出 (code 137)
  └─ exec:build — 超时 (运行 >1h)
```
