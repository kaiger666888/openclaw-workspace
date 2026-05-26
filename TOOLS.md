# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your* specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

### Telegram 论坛消息
- **forum group 用 message tool 发送时，必须同时带 replyTo + threadId**，缺一不可
- replyTo 确保消息进入正确话题，threadId 是第二层保险
- 只回 reply 不带附件时，直接正常回复即可（自动路由）

### kais-archi
- **输出方式**：启动本地 HTTP server，给局域网 URL（不要截图发图）
- **默认端口**：8090
- **局域网 IP**：`hostname -I` 获取
- **示例**：`http://192.168.71.140:8090/kais-movie-agent-arch.html`

### 视觉分析
- **按需选用**：内置 image tool（GLM-4.6V）和 zai-vision MCP 均可，根据场景选择
- **内置 image tool**：直接使用 `image` tool，传入图片路径和分析 prompt
- **zai-vision MCP**：`mcporter call zai-vision.analyze_image image_source="<path>" prompt="<描述需求>" --timeout 60000`
  - `analyze_image` — 通用图像理解
  - `ui_to_artifact` — UI 截图转代码/提示词/设计规范
  - `extract_text_from_screenshot` — OCR 文字提取
  - `diagnose_error_screenshot` — 错误截图诊断
  - `understand_technical_diagram` — 架构图/流程图/UML 分析
  - `analyze_data_visualization` — 数据可视化分析
  - `ui_diff_check` — 两张 UI 截图对比
  - `analyze_video` — 视频分析（MP4/MOV/M4V，≤8MB）
- **配置文件**：`~/.mcporter/mcporter.json`

### 高配机（本机，OpenClaw 运行机器）
- **IP**: 192.168.71.166
- **系统**: Linux Ubuntu
- **用户名**: kai
- **GPU**: RTX 3090 24GB（PCIe 4.0 x16）
- **角色**: OpenClaw 主机 + kais-aigc-platform + kais-gold-team 全部运行在此
- **Docker**: 容器可直接访问 GPU（nvidia-container-toolkit 已安装）
- **关联 Bot**: KaisGoldEngineBot（OpenClaw 实例在本机）
- **⚠️ 重要**: 低配机已不存在，所有服务都在本机运行

### Playwright
- **已安装**: workspace 依赖 (`npm install playwright`)
- **浏览器**: Chromium (headless, `--no-sandbox`)
- **用途**: Mermaid/UML/HTML → PNG 截图
- **偏好**: 始终用 Playwright，不用 Puppeteer (2026-03-31)

### Notion 读写规范
- **所有涉及 Notion 读写的任务，默认使用 `kais-notion` skill**，不要直接用 notion-cli 或手动 API 调用

### GitHub 账户

- **工作账户**: `kaiger666888` — 默认活跃账户，创建新 repo、上传代码/文件等使用此账户

### 汇报规范
- **代码推送到 GitHub 后汇报时，必须附带仓库 URL**（如 https://github.com/kaiger666888/kais-music-score）
- **个人账户**: `zhangkaidhb` — 需要时用 `gh auth switch --user zhangkaidhb` 切换

**⚠️ 查询仓库前必须先 `gh auth status` 确认活跃账户**，否则可能因 token 权限问题查不到私有仓库。查不到预期结果时，先排查认证问题，不要直接下结论。（2026-03-28 教训）

- **工作账户**: `kaiger666888` — 默认活跃账户，创建新 repo、上传代码/文件等使用此账户
- **个人账户**: `zhangkaidhb` — 需要时用 `gh auth switch --user zhangkaidhb` 切换

---

### Skill 创建规范
- **创建/改进 skill 必须使用 kais-skill-creator skill**，不要手动创建
- 评分 ≥ 90 才算通过，否则继续迭代
- 默认存到 GitHub（kaiger666888 账户），不发布到 ClawHub
- 创建新 skill 后自动初始化 git repo 并推送到 GitHub

---

Add whatever helps you do your job. This is your cheat sheet.

## Notion

### Pages (马斯克页面下的子页面)
- 马斯克(根页面): 2f811082-af8e-80e4-bd83-ce938ef34197
- 每日总结: 2f811082-af8e-8103-adba-d7e49dec89e9
- 每日新闻: 2f811082-af8e-8186-af95-e126966aead6
- 每日用餐: 2f811082-af8e-8128-a12d-f819313e0cf9
- VibeCoding: 2fc11082-af8e-817f-9542-ddf609cecc49
- GithubTrending: 2fc11082-af8e-81c0-a440-f53168e67d10
- 读书笔记: 2fc11082-af8e-8138-8fca-c70bcced3395
- 失败经验: 2fc11082-af8e-8120-b640-cf5eb9e2b134
- 技术研究: 2fc11082-af8e-81de-98bb-d1741c3cee68
- ClaudeCode: 2fc11082-af8e-810b-a6c8-d9e075abe87c
- TODO: 2b011082-af8e-8035-a849-eabd27cadac3
- 头脑风暴: 30911082-af8e-8195-a3c7-fb844e910a5e
- 心智模型: 31d11082-af8e-8116-83f3-f87f63dbafb1
- 代码审查: 32711082-af8e-8158-8e03-dc8ab98c17b5
  - umlVisionAgent: 32711082-af8e-8185-9883-fdff1f18a577

### Databases
- ToDo List: 25a11082-af8e-8146-9feb-d000f4aaefca
- 问题数据库: 2b511082-af8e-80fe-bf49-c2ddc468e502

### 调查研究报告归档
- 研究报告根页面: 32811082af8e8191aa20cc364202b1f9
- 规则：所有非每日任务的调查研究报告都放到此页面下对应主题子页面中

### 即梦 API 自维护
- **容器名**：`jimeng-free-api`
- **重启**：`docker restart jimeng-free-api`
- **彻底重建**：`docker stop jimeng-free-api && docker rm jimeng-free-api && docker run -d --name jimeng-free-api -p 8000:8000 jimeng-free-api`
- **诊断**：`docker logs --tail 20 jimeng-free-api`
- **status:45**：任务排队中阻塞新请求，等完成或重建容器
- **空响应**：session 过期或即梦限流，需重建+更新 session

### kais-story-score
- **功能**：故事五维质量评估系统（叙事弧线/情感深度/角色网络/节奏张力/文本质量）
- **位置**：~/.openclaw/workspace/skills/kais-story-score/
- **使用**：`python -m src.cli --input novel.txt --output-dir ./output --language zh/en [--characters 角色A,角色B]`
- **输出**：report.html（交互式可视化）、report.json（结构化数据）、7张CSV
- **GitHub**：https://github.com/kaiger666888/kais-story-score
