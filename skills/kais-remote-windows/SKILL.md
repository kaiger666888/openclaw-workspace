---
name: kais-remote-windows
version: 1.0.0
description: "通过 SSH 从 Linux OpenClaw 远程控制局域网 Windows 机器，在指定目录执行命令。触发词：远程Windows、远程控制Windows、SSH到Windows、连Windows、windows远程、remote windows、在Windows上执行、跑Windows命令、windows ssh、远程桌面、控制另一台电脑、局域网控制、ssh windows、远程执行"
---

# kais-remote-windows

通过 SSH 从 Linux OpenClaw 远程控制局域网 Windows 机器，在指定目录启动 bash 并执行命令。

## 前置条件

<!-- FREEDOM:low -->

### Windows 端（一次性配置）

1. **启用 OpenSSH Server**（Windows 10 1809+ 内置）：
   - `设置` → `应用` → `可选功能` → `添加功能` → 搜索 `OpenSSH 服务器` → 安装
   - 或 PowerShell（管理员）：`Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0`
   - 启动服务：`Start-Service sshd` + `Set-Service -Name sshd -StartupType Automatic`

2. **确认 SSH 端口**：默认 22，防火墙会自动放行。如需改端口，编辑 `C:\ProgramData\ssh\sshd_config`

3. **获取连接信息**：
   - IP：Windows 端 `ipconfig` 查看局域网 IP（如 `192.168.1.100`）
   - 用户名：Windows 登录用户名
   - 密码：Windows 登录密码

4. **（推荐）SSH 密钥免密登录**：
   ```bash
   # Linux 端生成密钥（如果还没有）
   ssh-keygen -t ed25519 -f ~/.ssh/id_windows
   # 将公钥复制到 Windows
   ssh-copy-id -i ~/.ssh/id_windows.pub USER@WINDOWS_IP
   ```

5. **确认 bash 可用**：
   - **Git Bash**（推荐）：安装 Git for Windows 后，bash 在 `C:\Program Files\Git\bin\bash.exe`
   - **WSL**：`wsl bash -c "command"`
   - **MSYS2**：`C:\msys64\usr\bin\bash.exe`

### Linux 端（OpenClaw 所在机器）

1. 确保可连通：`ssh -o ConnectTimeout=5 USER@WINDOWS_IP echo ok`
2. 如有密钥：`ssh -i ~/.ssh/id_windows USER@WINDOWS_IP echo ok`

<!-- /FREEDOM:low -->

## 连接配置

在 TOOLS.md 中记录 Windows 连接信息：

```markdown
### Windows 远程机器
- **主机名**: win-dev
- **IP**: 192.168.x.x
- **用户名**: kai
- **SSH 端口**: 22
- **SSH 密钥**: ~/.ssh/id_windows（或使用密码）
- **Bash 路径**: Git Bash → 通过 ssh 直接用 bash
- **默认工作目录**: /c/Users/kai/projects
```

## 使用方式

### 核心命令模板

<!-- FREEDOM:low -->

**单条命令执行：**
```bash
ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no \
  [-i ~/.ssh/id_windows] [-p PORT] \
  USER@WINDOWS_IP \
  "bash -c 'cd /目标目录 && 命令'"
```

**交互式长命令（多行脚本）：**
```bash
ssh USER@WINDOWS_IP "bash -s" << 'REMOTE_SCRIPT'
cd /c/Users/kai/projects/my-app
git status
npm test
REMOTE_SCRIPT
```

**后台长时间任务：**
```bash
ssh USER@WINDOWS_IP "bash -c 'cd /path && nohup command > output.log 2>&1 &'"
# 后续查看输出
ssh USER@WINDOWS_IP "cat /path/output.log"
```

**文件传输（替代 scp）：**
```bash
# Linux → Windows
scp -i ~/.ssh/id_windows local_file USER@WINDOWS_IP:/c/Users/kai/target/
# Windows → Linux
scp -i ~/.ssh/id_windows USER@WINDOWS_IP:/c/Users/kai/source/file ./
```

<!-- /FREEDOM:low -->

### 典型使用场景

<!-- FREEDOM:high -->

1. **在 Windows 项目目录跑命令**：用户说"在 Windows 上跑 npm build" → ssh 过去执行
2. **查看 Windows 文件/日志**：用户说"看看 Windows 上 xxx 的日志" → ssh cat
3. **Git 操作**：用户说"在 Windows 上 git pull" → ssh 执行
4. **启动/停止服务**：用户说"在 Windows 上启动 xxx" → ssh 执行
5. **文件传输**：用户说"把 xxx 传到 Windows" → scp

<!-- /FREEDOM:high -->

## 注意事项

<!-- FREEDOM:low -->

1. **路径格式**：Git Bash 中 Windows 路径用 `/c/Users/...` 而非 `C:\Users\...`
2. **超时设置**：长时间命令用 `ServerAliveInterval=60` 保持连接
3. **编码问题**：Windows 默认 GBK，如需 UTF-8 在 ssh 命令前加 `chcp 65001 >nul &&`
4. **PowerShell vs Bash**：默认连接是 PowerShell，必须显式调用 `bash -c` 来使用 bash
5. **断线处理**：用 `screen` 或 `tmux`（如果 Windows 端装了）或 `nohup` 保持后台任务

<!-- /FREEDOM:low -->

## 服务管理经验

<!-- FREEDOM:low -->

### 启动 Python HTTP 服务（局域网可访问）

**⚠️ 关键经验：`Start-Process -WindowStyle Hidden` 会静默失败，不要用它！**

**可靠方式 — SSH 前台启动（推荐）：**
```bash
ssh -i ~/.ssh/id_windows kai@192.168.71.38 "cd /d E:\KaisProject\kais-blender\server && python blender_agent_server.py 2>&1"
```
- 优点：100% 可靠，启动失败有报错
- 缺点：SSH 断开后服务会停

**后台启动（需要 Windows 终端手动执行）：**
```powershell
cd E:\KaisProject\kais-blender\server
Start-Process python -ArgumentList 'blender_agent_server.py' -WindowStyle Hidden
```
- `Start-Process -WindowStyle Hidden` 通过 SSH 调用会静默失败，必须在 Windows 本地终端执行

### 重启服务标准流程
```bash
# 1. 杀旧进程
ssh -i ~/.ssh/id_windows kai@192.168.71.38 "powershell -Command \"Get-Process python* -ErrorAction SilentlyContinue | Stop-Process -Force\""
# 2. 前台启动
ssh -i ~/.ssh/id_windows kai@192.168.71.38 "cd /d E:\KaisProject\kais-blender\server && python blender_agent_server.py 2>&1"
# 3. 验证局域网可访问
curl -s --connect-timeout 5 http://192.168.71.38:8080/health
```

### 防火墙规则

放行端口（一次性，重启后仍有效）：
```bash
ssh -i ~/.ssh/id_windows kai@192.168.71.38 "powershell -Command \"New-NetFirewallRule -DisplayName 'Blender Server 8080' -Direction Inbound -LocalPort 8080 -Protocol TCP -Action Allow -Profile Any\""
```

### 管理员账户 SSH 密钥

Windows 管理员账户的 `authorized_keys` 必须放在特殊位置：
```
C:\ProgramData\ssh\administrators_authorized_keys
```
且文件权限必须是 SYSTEM 和 Administrators 可读。普通 `~/.ssh/authorized_keys` 对管理员账户无效。

### Git Push 经验

- Windows 端 git credential helper 使用 `gh auth git-credential`，通过 SSH 无法推送（需要 tty）
- 解决方案：在 Windows 本地终端手动执行 `gh auth login -h github.com`
- 或通过 Windows 上的 Claude Code 执行 git push

<!-- /FREEDOM:low -->

## 故障排查

| 问题 | 解决方案 |
|------|---------|
| `Connection refused` | Windows 端 sshd 服务未启动：`Start-Service sshd` |
| `Permission denied` | 检查用户名密码，或重新配置密钥 |
| 超时 | 检查防火墙，确认两台机器在同一局域网 |
| `bash: command not found` | Git Bash 未安装或未加入 PATH，用完整路径 |
| 中文乱码 | 执行前加 `chcp 65001 >nul` 或 `export LANG=zh_CN.UTF-8` |
