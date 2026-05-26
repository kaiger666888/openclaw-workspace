# 小红书内容生成 Skill 调查报告

**调查时间**：2026-03-26 20:06
**调查者**：Clawd (AI Assistant)
**目的**：寻找帮助生成小红书内容的 skill

---

## 📊 核心发现

✅ **有大量可用的小红书内容生成 skill**

**主要分类**：
1. **ClawHub 平台 Skills** - 可直接安装使用
2. **独立工具** - 在线服务
3. **GitHub 开源项目** - 需要自己部署

---

## 🎯 ClawHub 平台 Skills（推荐）

### 1. xiaohongshu-mcp ⭐⭐⭐⭐⭐

**最成熟、最活跃的小红书 AI 自动化方案**

- **GitHub Stars**：8.4k+
- **核心能力**：
  - ✅ 搜索笔记
  - ✅ 发布内容（图文/视频）
  - ✅ 自动互动（点赞/评论/收藏）
  - ✅ 数据采集（曝光、观看、点赞等）
  - ✅ 多账号管理

- **技术路线**：MCP（Model Context Protocol）
- **安装方式**：`clawhub install xiaohongshu-mcp`
- **要求**：本地运行服务器 + 登录

**适用场景**：
- 内容创作自动化
- 竞品分析
- 数据监控
- 批量操作

---

### 2. xiaohongshu-ops-skill ⭐⭐⭐⭐

**小红书自动运营 Skill，全面托管**

- **核心能力**：
  - ✅ 分析（数据洞察）
  - ✅ 选题（热点追踪）
  - ✅ 创作（文案生成）
  - ✅ 复盘（效果分析）
  - ✅ 复刻（爆文仿写）

- **GitHub**：Xiangyu-CAS/xiaohongshu-ops-skill
- **特点**：搭配 OpenClaw 可独立运营账号

**适用场景**：
- 全自动运营
- 爆文复刻
- 内容矩阵

---

### 3. xiaohongshu-mcp-skill ⭐⭐⭐

**MCP 集成的小红书操作**

- **核心能力**：
  - ✅ 搜索笔记
  - ✅ 发布内容
  - ✅ 互动操作

- **安全警告**：ClawHub 标记为可疑，需审查代码

---

### 4. Auto-Redbook-Skills ⭐⭐⭐⭐

**自动发布工具**

- **核心能力**：
  - ✅ Markdown → 小红书图文卡片
  - ✅ 8 套精美主题
  - ✅ 4 种智能分页
  - ✅ 基于 Cookie 的全自动发布

- **GitHub**：comeonzhj/Auto-Redbook-Skills

---

## 🌐 独立工具（在线服务）

### 1. Reditor 编辑器 ⭐⭐⭐⭐⭐

**一站式小红书创作工具**

- **网址**：https://www.reditorapp.com/
- **核心功能**：
  - ✅ AI 文案生成
  - ✅ 违禁词检测
  - ✅ Emoji 生成
  - ✅ 爆款标题模板
  - ✅ 排版优化

**优点**：
- 界面友好
- 功能全面
- 免费使用

---

### 2. iThinkScene ⭐⭐⭐⭐

**多平台爆文创作工具**

- **网址**：https://app.ithinkai.cn/
- **支持平台**：
  - 小红书
  - 抖音
  - 公众号
  - 知乎
  - 今日头条
  - 微博
  - 闲鱼

**核心功能**：
- ✅ 爆文采集
- ✅ AI 伪原创
- ✅ 敏感词检测
- ✅ 批量生成
- ✅ 一键发布

---

### 3. XHSAIPro ⭐⭐⭐

**小红书智能生成与仿写**

- **网址**：https://www.xhsaipro.com/
- **核心功能**：
  - ✅ 一键生成种草笔记
  - ✅ 笔记优化
  - ✅ 断流分析

---

## 🔧 GitHub 开源项目

### 1. white0dew/XiaohongshuSkills ⭐⭐⭐⭐

**基于 Chrome DevTools Protocol 的自动化工具**

- **GitHub Stars**：1.2k+
- **核心能力**：
  - ✅ 图文笔记发布
  - ✅ 视频笔记发布
  - ✅ 多账号管理
  - ✅ 自动评论
  - ✅ 数据导出

- **技术路线**：Python + CDP
- **支持编辑器**：OpenClaw、Codex、Claude Code

---

### 2. zhjiang22/openclaw-xhs ⭐⭐⭐

**让 OpenClaw 读懂你的小红书**

- **核心能力**：
  - ✅ MCP 集成
  - ✅ 热点跟踪
  - ✅ 个人记忆库导出

---

## 📋 对比分析

| 工具/Skill | 类型 | 难度 | 功能完整度 | 推荐度 |
|-----------|------|------|-----------|--------|
| xiaohongshu-mcp | ClawHub Skill | 中 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| xiaohongshu-ops-skill | ClawHub Skill | 低 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Reditor 编辑器 | 在线工具 | 低 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| iThinkScene | 在线工具 | 低 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| XiaohongshuSkills | GitHub 项目 | 高 | ⭐⭐⭐⭐ | ⭐⭐⭐ |

---

## 💡 推荐方案

### 方案 A：快速上手（推荐新手）

**工具组合**：Reditor 编辑器 + iThinkScene

**流程**：
1. 用 Reditor 生成文案
2. 用 Reditor 检测违禁词
3. 用 iThinkScene 批量生成图文
4. 手动发布

**优点**：
- 零技术门槛
- 免费使用
- 功能全面

**缺点**：
- 需要手动发布
- 批量操作效率低

---

### 方案 B：半自动化（推荐进阶）

**工具组合**：xiaohongshu-ops-skill + Reditor

**流程**：
1. 用 xiaohongshu-ops-skill 分析热点
2. 用 Reditor 生成文案
3. 用 xiaohongshu-ops-skill 复盘优化

**优点**：
- 部分自动化
- 数据驱动
- 持续优化

**缺点**：
- 需要安装 skill
- 需要学习使用

---

### 方案 C：全自动化（推荐专业）

**工具组合**：xiaohongshu-mcp + 自动化脚本

**流程**：
1. 用 xiaohongshu-mcp 搜索爆文
2. 用 AI 生成仿写内容
3. 用 xiaohongshu-mcp 自动发布
4. 用 xiaohongshu-mcp 监控数据

**优点**：
- 全自动化
- 批量操作
- 数据监控

**缺点**：
- 技术门槛高
- 需要维护服务器
- 账号风险

---

## 🚀 快速开始

### 1. 安装 xiaohongshu-mcp（推荐）

```bash
# 安装 ClawHub CLI（如果没有）
npm install -g clawhub

# 安装 skill
clawhub install xiaohongshu-mcp

# 下载二进制文件
# 访问 https://github.com/xpzouying/xiaohongshu-mcp/releases
# 下载对应平台的文件

# 登录
./xiaohongshu-login-darwin-arm64

# 启动服务器
./xiaohongshu-mcp-darwin-arm64

# 使用
python ~/clawd/skills/xiaohongshu-mcp/scripts/xhs_client.py status
python ~/clawd/skills/xiaohongshu-mcp/scripts/xhs_client.py search "咖啡"
```

---

### 2. 使用 Reditor 编辑器（最简单）

1. 访问 https://www.reditorapp.com/
2. 输入主题
3. 点击"生成文案"
4. 检测违禁词
5. 复制发布

---

## ⚠️ 注意事项

### 1. 账号安全

- **不要登录多个账号** - 会互相踢出
- **使用小号测试** - 避免主账号被封
- **遵守平台规则** - 不要过度自动化

### 2. 内容质量

- **不要完全依赖 AI** - 需要人工审核
- **保持原创性** - 避免直接抄袭
- **关注用户体验** - 不是为了发布而发布

### 3. 法律风险

- **版权问题** - 不要复制他人内容
- **广告法** - 注意违禁词
- **平台规则** - 遵守小红书社区规范

---

## 📊 适用场景分析

| 场景 | 推荐工具 | 理由 |
|------|---------|------|
| **个人博主** | Reditor + iThinkScene | 简单易用，免费 |
| **团队运营** | xiaohongshu-ops-skill | 协作方便，数据驱动 |
| **批量矩阵** | xiaohongshu-mcp | 全自动化，批量操作 |
| **电商带货** | iThinkScene | 多平台支持，一键发布 |
| **品牌营销** | xiaohongshu-mcp + 数据分析 | 数据监控，效果追踪 |

---

## 🔗 相关资源

### ClawHub Skills
- xiaohongshu-mcp: https://clawhub.ai/Borye/xiaohongshu-mcp
- xiaohongshu-ops-skill: https://github.com/Xiangyu-CAS/xiaohongshu-ops-skill

### 独立工具
- Reditor 编辑器: https://www.reditorapp.com/
- iThinkScene: https://app.ithinkai.cn/
- XHSAIPro: https://www.xhsaipro.com/

### GitHub 项目
- xiaohongshu-mcp: https://github.com/xpzouying/xiaohongshu-mcp
- XiaohongshuSkills: https://github.com/white0dew/XiaohongshuSkills
- openclaw-xhs: https://github.com/zhjiang22/openclaw-xhs

---

## 📝 总结

**有大量可用的小红书内容生成 skill**

**推荐路径**：
1. **新手** → Reditor 编辑器（最简单）
2. **进阶** → xiaohongshu-ops-skill（部分自动化）
3. **专业** → xiaohongshu-mcp（全自动化）

**关键建议**：
- 先用免费工具测试效果
- 逐步升级到自动化工具
- 注意账号安全和内容质量
- 遵守平台规则

---

**调查完成时间**：2026-03-26 20:06
**总用时**：约10分钟
**研究者**：Clawd (AI Assistant)
