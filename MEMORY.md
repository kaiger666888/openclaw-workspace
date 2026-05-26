# MEMORY.md - 长期记忆库

> PARA 方法 + 渐进式总结 | 夜间回顾任务自动维护

---

## 📁 PARA 结构

### Projects
- **kais-gold-team GPU Runtime Manager** (2026-05-09)
  - **状态**: V2架构设计进行中，V1完成并重构
  - **技术升级**: Docker → Apptainer/SIF, Zero Resident模式, 三层权重存储
  - **V2架构**: 双卡拓扑(3090重型 + 3060Ti轻量Combo常驻), TopologyAwareRouter
  - **依赖审计**: 4个高风险非商用模型(inswapper, Wav2Lip, Woosh, arcface)
  - **仓库**: kaiger666888/kais-gold-team
  - **GSD流程**: 使用Claude Code并行开发，3Worker模式
- **知识管理系统** (2026-02-25)
  - **状态**: 架构设计完成，第17次夜间回顾任务执行
  - **核心架构**: Thiago Forte PARA方法 + 渐进式总结 + 自动化夜间回顾
  - **验证状态**: 系统持续稳定运行，全流程验证通过
  - **最新执行**: 2026-05-25 凌晨01:00，系统运行正常，等待实际对话内容
- **UML Vision Agent** (2026-02-25)
  - **状态**: MVP完成，PlantUML→HTML动画全流程验证通过
  - **技术实现**: PlantUML Server集成 + HTML动画渲染器 + 完整工作流
  - **完成内容**: 植物UML脚本、HTML动画渲染器、工作流测试(16K输出)
  - **阻塞**: GitHub仓库权限问题（Token缺少repo scope）
  - **仓库位置**: `/home/kai/.openclaw/workspace/skills/knowledge-visualizer/`

### Areas
- **知识管理**: PARA方法 + 渐进式总结 + 自动化夜间回顾系统架构稳定运行
- **可视化技术**: PlantUML → SVG → HTML动画全流程验证完成
- **失败经验积累**: 技术失败案例库（API超时、数据库连接池、缓存穿透）
- **系统验证**: 夜间回顾任务持续执行，知识管理系统架构成熟

### Resources
- **夜间回顾指南**: `/home/kai/.openclaw/workspace/memory/nightly-review-guide.md`
- **失败经验页面**: `31111082-af8e-81a8-9d73-faa35dacee02`
- **知识可视化仓库**: `/home/kai/.openclaw/workspace/skills/knowledge-visualizer`

### Archives
- **归档项目** (2026-04-13)
  - 知识可视化系统MVP
  - GitHub仓库权限问题代理
  - edu-video skill
  - ClawHub发布相关技能
- **技术失败案例整理** (2026-02-25)
  - API超时未设置导致雪崩
  - 数据库连接池耗尽
  - 缓存穿透导致数据库崩溃
  - 归档至 Notion 失败经验页面: `31111082-af8e-81a8-9d73-faa35dacee02`

---

## 当前优先级

### P1 - 活跃项目
- **kais-gold-team V2 架构设计** (2026-05-09)
  - **双卡拓扑**: 3090 (PCIe 4.0 x16, 重型任务) + 3060Ti (PCIe 3.0 x4, 轻量Combo常驻)
  - **3060Ti Combo Resident**: 6个轻量模型(SDXL/CosyVoice等), 30分钟最低驻留
  - **关键组件**: TopologyAwareRouter, 三层权重存储, 批处理调度器
  - **技术升级**: Zero Resident模式, Apptainer/SIF替代Docker
  - **依赖审计**: 🔴4个高风险非商用模型, 🟡2个AGPL框架, 🟢其余MIT/BSD/Apache
  - **仓库**: kaiger666888/kais-gold-team, release/rtx3060ti备份分支
  - **GSD流程**: Claude Code并行开发, 3Worker模式(v2-orchestrator/v2-combo/v2-deploy)
- **知识管理系统架构** (2026-02-25)
  - **状态**: 架构设计完成，第18次夜间回顾任务执行（今日）
  - **核心架构**: Thiago Forte PARA方法 + 渐进式总结 + 自动化夜间回顾
  - **验证状态**: 系统持续稳定运行，全流程自动化验证通过
  - **自动化机制**: MEMORY.md+memory/YYYY-MM-DD.md+夜间回顾任务完整闭环
- **UML Vision Agent** (2026-02-25)
  - **状态**: MVP完成，PlantUML→HTML动画全流程验证通过
  - **技术实现**: PlantUML Server集成 + HTML动画渲染器 + 完整工作流
  - **完成内容**: 植物UML脚本、HTML动画渲染器、工作流测试(16K输出)
  - **阻塞**: GitHub仓库权限问题（Token缺少repo scope）
- **UML Vision Agent技术雷达** (2026-05-09)
  - **最新数据更新**: 零信任架构采用率88%(持续提升), AI代理企业嵌入40%
  - **四象限更新**: ADOPT(零信任/Claude Sonnet 4.8), TRIAL(AI辅助UML工具82%准确度)
  - **工具生态**: 新增Miro AI, Draft1.ai, DiagrammingAI等架构设计工具
  - **执行周期**: 每周六05:20, 数据时效性和准确性显著提升
- **2.5D 视差效果研究** (2026-04-20 进行中)
  - 技术栈: DepthFlow GLSL shader + Jimeng 图生图 API
  - 已完成: 12个效果视频, Windows 端部署 (1344x768@60fps)
  - CLI: `depthflow input -i IMAGE {animation} h264 main -t 3 -w 1344 -h 768 -o OUTPUT.mp4`
  - 会话管理: session-manager.js 自动恢复

### 已归档 (2026-04-13)
- 知识可视化系统 MVP, GitHub仓库权限, 代理故障, ClawHub发布, edu-video skill

### 最新归档 (2026-05-15)
- **技术债务清理**: 硬件信息确认(RTX 3060 Ti 8GB/RTX 3090 24GB), API会话管理(Jimeng API自动恢复), 搜索降级方案

### 最新归档 (2026-05-23)
- **系统稳定期验证**: 夜间回顾任务第17次执行，知识管理系统架构稳定运行验证

---

## 关于 Kai

- 时区: Asia/Shanghai (GMT+8), 早起型 (05:00-07:00)
- 偏好: 质量优于数量, 结构化信息, 遇到问题立即解决
- 关注: AI & 编程, 语言学习, 知识管理, 投资

---

## 关键工具和脚本

| 路径 | 用途 |
|------|------|
| `scripts/daily-tasks-v3.sh` | 主任务脚本 |
| `scripts/lib/notion-append.py` | Notion 追加 (突破2000字符限制) |
| `scripts/lib/markdown-to-notion.py` | Markdown → Notion JSON块格式 |
| `scripts/lib/notion-append-blocks.sh` | 封装追加流程 |
| `scripts/lib/dedupe-validator.py` | 通用去重框架 |
| `scripts/github-review.sh` | GitHub 代码审查 |
| `scripts/web-search-fallback.sh` | 搜索降级 (5级) |
| `scripts/proxy-manager.sh` | 代理管理 (status/test/restart) |

---

## Notion 格式规范 (2026-03-04 修复)

- **必须用 JSON 块格式**: `notion-cli block append --children-file <json>` (不是纯文本)
- 转换工具: `markdown-to-notion.py` → `notion-append-blocks.sh PAGE_ID file.md`
- 规则: 顶部callout摘要 / heading_2分类 / 链接格式`[名](URL)` / 搜索限3次

---

## Web Search 规范

- 中文搜索必须用 `zh-hans` (不是 `zh`)
- 优先英文搜索
- 搜索降级链: Brave API → Exa AI (MCP免费) → 秘塔AI → Jina Reader → Bing CN
- Brave API 限制: 1次/分钟, 超限则降级

---

## Notion 页面 ID

| 页面 | ID |
|------|-----|
| 根页面 (马斯克) | `2f811082-af8e-80e4-bd83-ce938ef34197` |
| TODO 数据库 | `25a11082-af8e-8146-9feb-d000f4aaefca` |
| 问题数据库 | `2b511082-af8e-80fe-bf49-c2ddc468e502` |
| 每日英语德语 | `30411082-af8e-8191-9fb5-d1ca8f6d7b6f` |
| 心智模型 | `31d11082-af8e-8116-83f3-f87f63dbafb1` |
| 技术研究 | `2fc11082-af8e-81de-98bb-d1741c3cee68` |
| 研究报告 | `32811082af8e8191aa20cc364202b1f9` |

---

## Cron 任务

| 任务 | ID | 时间 |
|------|-----|------|
| 夜间回顾 | `6d8395cb` | 01:00 |
| GitHub 审查 | `cccb8921` | 02:00 |
| 知识可视化 | `7ddb57fe` | 05:15 |
| 技术雷达 | `f1ab078e` | 周六 05:20 |
| 每日心智模型 | `2ca99717` | 06:00 |
| 创业失败经验 | `fbd083d4` | 05:10 |

---

## 硬件

- **本机（高配机）**: RTX 3090 24GB, IP 192.168.71.166, OpenClaw 运行在此
  - 所有项目（kais-aigc-platform, kais-gold-team）都在本机运行
  - Docker 容器可直接使用 GPU
- ~~低配机~~: 已不存在
- Windows: RTX 3060 Ti 8GB (不是4070), DepthFlow 部署端

---

## 关键决策 (去重)

| 日期 | 决策 | 原因 |
|------|------|------|
| 2026-05-09 | kais-gold-team架构升级: Docker→Apptainer/SIF, 单卡→双卡架构 | HPC场景优化, RTX 3090+3060Ti双卡拓扑提升GPU利用率 |
| 2026-05-09 | V2架构采用3060Ti Combo Resident模式 | 轻量模型常驻30分钟, TopologyAwareRouter智能分配GPU资源 |
| 2026-05-09 | 依赖审计完成并发现4个高风险模型 | 合规性要求, 为商业部署识别风险 |
| 2026-05-23 | 夜间回顾任务第17次执行 - 系统稳定运行 | 知识管理系统第17天持续验证，全流程自动化机制确认有效 |
| 2026-05-25 | 夜间回顾任务第18次执行 - 系统稳定期持续 | 系统持续验证阶段，全流程自动化机制确认有效，第18次验证完成 |
| 2026-05-25 | 知识管理系统架构稳定运行第18天 | PARA方法+渐进式总结+夜间回顾系统持续稳定运行 |
| 2026-05-23 | 夜间回顾任务第16次执行 - 系统稳定期 | 系统持续验证阶段，等待实际对话内容执行完整回顾流程 |
| 2026-05-19 | 夜间回顾任务第15次执行 - 系统稳定期 | 系统持续验证阶段，等待实际对话内容执行完整回顾流程 |
| 2026-05-17 | 夜间回顾任务第14次验证通过 | 知识管理系统持续稳定运行, PARA方法验证有效 |
| 2026-05-02 | 夜间回顾任务首次执行成功 | Thiago Forte PARA方法 + 渐进式总结 + 自动化夜间回顾系统首次验证成功 |
| 2026-04-13 | 归档5个停滞项目 | kais-mind 分析发现大量"MVP后停滞", 减少心智负荷 |
| 2026-03-26 | 研究报告自动同步 Notion | 研究成果不丢失, 方便查阅 |
| 2026-03-19 | 强制使用去重工具 | 心智模型/每日一句重复, 根因是Prompt没强制用工具 |
| 2026-03-09 | web_search 用 zh-hans | 避免 API 参数错误 |
| 2026-03-04 | Notion 格式标准化 | 解决内容格式不一致, JSON块格式替换纯文本 |
| 2026-02-25 | PARA + 渐进式总结架构 + 夜间回顾任务 | 解决"记东西困难"问题，实现知识管理系统自动化 |
| 2026-02-25 | UML Vision Agent MVP开发完成 | PlantUML→HTML动画全流程技术方案验证 |
| 2026-02-22 | notion-append.py 工具 | 突破 Notion API 2000字符限制 |
