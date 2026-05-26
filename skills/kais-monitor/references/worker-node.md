# Worker Node 配置参考

## SSH 连接信息

| 项目 | 值 |
|------|-----|
| IP | 192.168.71.38 |
| 用户 | kai |
| 端口 | 22 |
| 密钥 | ~/.ssh/id_rsa |
| 连接命令 | `ssh kai@192.168.71.38` |
| 超时建议 | 10000ms |

## 硬件

- GPU: RTX 3060 Ti 8GB
- 用途: kais-gold-team Worker Node

## 常用 tmux 会话命名约定

| 会话名模式 | 用途 |
|-----------|------|
| `claude-*` | Claude Code 开发会话 |
| `train-*` / `infer-*` | 训练/推理任务 |
| `engine-*` | GPU 引擎服务 |
| `dev-*` | 通用开发 |

## 连接故障排查

1. 检查 SSH 连通性: `ssh -o ConnectTimeout=5 kai@192.168.71.38 echo ok`
2. 如果超时: 标注 ⚠️ Worker Node 不可达，跳过远程监控
3. 如果认证失败: 检查密钥文件是否存在
