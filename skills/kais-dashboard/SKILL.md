---
name: kais-dashboard
version: 1.0.0
description: "多平台创作者数据看板。自动采集小红书、抖音、B站账号数据，生成网页看板，支持每日定时+实时刷新。触发词：dashboard, 数据看板, 播放数据, 播放量, 账号数据, 刷新数据, 创作者数据, 数据概览, 看板"
---

# kais-dashboard

多平台创作者数据看板——自动采集、存储、可视化。

<!-- FREEDOM:low -->

## 架构概览

```
cron/手动触发
  ├── 采集层 (scripts/collect-*.sh)
  │   ├── collect-xiaohongshu.sh  → 小红书创作者中心
  │   ├── collect-douyin.sh       → 抖音创作者中心
  │   └── collect-bilibili.sh     → B站创作中心
  ├── 存储层 (SQLite)
  │   └── data/dashboard.db
  ├── 生成层 (scripts/generate-dashboard.sh)
  │   └── data/dashboard/index.html
  └── 推送层 (可选)
      └── Telegram 摘要
```

## 触发模式

| 模式 | 触发方式 | 行为 |
|------|---------|------|
| 🔄 全量更新 | "刷新数据" / cron 每日 | 采集全部平台 + 重新生成看板 |
| 🎯 单平台 | "刷新小红书" / "刷新抖音" / "刷新B站" | 只采集指定平台 + 增量更新看板 |
| 📊 查看看板 | "打开看板" / "dashboard" | 打开浏览器展示看板 |
| 📋 数据摘要 | "数据摘要" / "账号概览" | 输出当前各平台数据概况 |

## 执行流程

### 步骤 1：初始化检查

```bash
# 确保数据目录和数据库存在
mkdir -p ~/.openclaw/workspace/data/dashboard
if [ ! -f ~/.openclaw/workspace/data/dashboard/dashboard.db ]; then
  sqlite3 ~/.openclaw/workspace/data/dashboard/dashboard.db < ~/.openclaw/workspace/skills/kais-dashboard/scripts/schema.sql
fi
```

### 步骤 2：数据采集

**所有采集使用 OpenClaw browser，profile=openclaw。** Cookie 复用，无需每次登录。

#### 小红书
- 目标页：`https://creator.xiaohongshu.com/publish/publish` 或 `https://creator.xiaohongshu.com/statistics`
- 数据：笔记数、阅读量、点赞、收藏、评论、粉丝数、互动率
- 方法：snapshot 解析创作者中心数据面板

#### 抖音
- 目标页：`https://creator.douyin.com/creator-micro/data/overview`
- 数据：视频数、播放量、点赞、评论、分享、粉丝数、新增粉丝
- 方法：snapshot 解析数据中心概览

#### B站
- 目标页：`https://member.bilibili.com/platform/upload-manager/article` 或 `https://member.bilibili.com/platform/data/overview`
- 数据：稿件数、播放量、点赞、投币、收藏、分享、粉丝数
- 方法：snapshot 解析数据中心（B站有部分 API 可用，优先尝试 API）

**采集脚本通用流程：**
```bash
# 1. browser start (profile=openclaw)
# 2. browser navigate → 平台数据页
# 3. browser snapshot → 提取数据
# 4. 解析 JSON → 插入 SQLite
# 5. browser stop
```

### 步骤 3：生成看板

```bash
bash ~/.openclaw/workspace/skills/kais-dashboard/scripts/generate-dashboard.sh
```

输出：`~/.openclaw/workspace/data/dashboard/index.html`

看板包含：
- **总览卡片**：各平台粉丝数、总播放量、总互动量
- **趋势图表**：近7天/30天播放量、互动率折线图（Chart.js）
- **平台对比**：各平台数据横向柱状图
- **最新数据表**：最近一次采集的详细数据

### 步骤 4：查看看板

```bash
# 用浏览器打开看板
browser open --url file:///home/kai/.openclaw/workspace/data/dashboard/index.html --profile openclaw
```

或用 canvas 展示截图。

## 数据存储

### SQLite Schema

```sql
-- 平台账号表
CREATE TABLE IF NOT EXISTS accounts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  platform TEXT NOT NULL,        -- xiaohongshu / douyin / bilibili
  account_name TEXT,
  account_id TEXT,
  created_at TEXT DEFAULT (datetime('now', 'localtime'))
);

-- 每日快照
CREATE TABLE IF NOT EXISTS daily_snapshots (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  account_id INTEGER REFERENCES accounts(id),
  date TEXT NOT NULL,             -- YYYY-MM-DD
  followers INTEGER DEFAULT 0,
  total_views INTEGER DEFAULT 0,
  total_likes INTEGER DEFAULT 0,
  total_comments INTEGER DEFAULT 0,
  total_favorites INTEGER DEFAULT 0,
  total_shares INTEGER DEFAULT 0,
  total_posts INTEGER DEFAULT 0,
  new_followers INTEGER DEFAULT 0,
  new_views INTEGER DEFAULT 0,
  interaction_rate REAL DEFAULT 0,
  raw_json TEXT,                  -- 原始数据备份
  collected_at TEXT DEFAULT (datetime('now', 'localtime')),
  UNIQUE(account_id, date)
);
```

完整 schema 见 `scripts/schema.sql`。

## 定时任务配置

创建每日 cron（建议凌晨 6:00）：

```
payload.kind = "agentTurn"
payload.message = "执行 kais-dashboard 每日数据采集：运行所有平台采集脚本，生成看板，如果数据有显著变化则推送摘要"
schedule.kind = "cron"
schedule.expr = "0 6 * * *"
schedule.tz = "Asia/Shanghai"
sessionTarget = "isolated"
```

## 错误处理

- **Cookie 过期**：提示用户手动登录一次（browser open + 用户操作），cookie 会自动保存
- **反爬拦截**：降级为手动截图方式，通知用户
- **页面改版**：采集脚本需要更新选择器，记录到 memory
- **数据异常**：与前一天数据对比，波动 >50% 标记为异常并提醒

## 文件结构

```
kais-dashboard/
├── SKILL.md                          # 本文件
├── scripts/
│   ├── schema.sql                    # SQLite 表结构
│   ├── collect-xiaohongshu.sh        # 小红书采集
│   ├── collect-douyin.sh             # 抖音采集
│   ├── collect-bilibili.sh           # B站采集
│   ├── generate-dashboard.sh         # 生成 HTML 看板
│   └── lib/
│       ├── db.sh                     # 数据库操作封装
│       └── parse-helpers.sh          # 数据解析工具
├── references/
│   ├── platform-selectors.md         # 各平台页面选择器（需维护）
│   └── api-notes.md                  # 平台 API 备注
└── assets/
    └── dashboard-template.html       # 看板 HTML 模板
```
