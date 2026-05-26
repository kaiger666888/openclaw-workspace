# 状态判断启发式规则

## Claude Code 状态判断

基于 tmux capture-pane 输出的最后几行文本：

| 状态 | 特征 | 标记 |
|------|------|------|
| 活跃中 | 有 `⏺` `●` 工具调用指示器，或有代码块输出中 | 🟢 active |
| 等待输入 | 显示 `>` 提示符、`Do you want to`、`Accept?` | 🟡 waiting |
| 已完成 | 显示结果摘要、回到 shell 提示符 `$` | ✅ done |
| 报错 | 包含 `ERROR` `FAILED` `panic` `Segmentation fault` | ❌ error |
| 空闲 | 显示 Claude Code 欢迎界面或无新输出 | ⏸️ idle |

## Tmux 会话状态判断

| 状态 | 特征 | 标记 |
|------|------|------|
| 活跃 | 有进程在运行（非 idle） | 🟢 active |
| 空闲 | 等待输入（shell 提示符） | ⏸️ idle |
| 已退出 | 无进程运行 | ⬜ exited |
| 异常 | 有 error/kill 信号 | ❌ error |

## Subagent 状态映射

| subagents API status | 含义 | 标记 |
|---------------------|------|------|
| running | 正在执行 | 🟢 running |
| completed | 成功完成 | ✅ completed |
| failed | 执行失败 | ❌ failed |

## 时间阈值

| 时长 | 标记 | 说明 |
|------|------|------|
| < 5min | 正常 | 无特殊标记 |
| 5-30min | ⚠️ | 较长，但可接受 |
| > 30min | ⚠️⚠️ | 需关注，可能卡住 |
| > 1h | 🔴 | 高度关注，建议检查 |
