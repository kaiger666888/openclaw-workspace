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

### Playwright
- **已安装**: workspace 依赖 (`npm install playwright`)
- **浏览器**: Chromium (headless, `--no-sandbox`)
- **用途**: Mermaid/UML/HTML → PNG 截图
- **偏好**: 始终用 Playwright，不用 Puppeteer (2026-03-31)

### GitHub 账户

- **工作账户**: `kaiger666888` — 默认活跃账户，创建新 repo、上传代码/文件等使用此账户
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
