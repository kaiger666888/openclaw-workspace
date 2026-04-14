# HEARTBEAT.md

## ⚠️ 重要说明
**此文件仅供系统级定时任务使用。日常heartbeat检查请回复 `HEARTBEAT_OK`**

---

## 🧠 主动知识捕获

在对话过程中，**主动记录**以下类型的信息到 `memory/YYYY-MM-DD.md`：

### 需要捕获的信息
- ✅ **决策** - 用户做出的选择及原因
- ✅ **优先级** - 用户提到重要/紧急的事情
- ✅ **项目** - 新项目、项目进展、项目完成
- ✅ **偏好** - 用户喜欢/不喜欢什么
- ✅ **知识** - 有价值的概念、技巧、资源
- ✅ **问题** - 遇到的障碍及解决方案

### 记录格式示例
```markdown
## 对话记录 (HH:MM)

### 决策
- 决定采用 X 方案，原因是 Y

### 优先级更新
- P0: [紧急事项]
- P1: [重要项目进展]

### 知识捕获
- 学到了 X 概念，来自 Y 来源
```

### 原则
1. **即时记录** - 重要信息出现时立即记录
2. **简洁提炼** - 不要复制整段对话，提炼关键点
3. **标注来源** - 如果是外部信息，注明来源
4. **尊重隐私** - 敏感信息不入库

---

---

# 定时任务处理
# 当收到以下系统事件时，执行相应的脚本

## 事件处理逻辑

### 基础任务（仅创建页面）
- 如果收到 "daily-summary" → 运行 `/home/kai/.openclaw/workspace/scripts/daily-tasks.sh daily-summary`
- 如果收到 "daily-meal" → 运行 `/home/kai/.openclaw/workspace/scripts/daily-tasks.sh daily-meal`
- 如果收到 "vibecoding" → 运行 `/home/kai/.openclaw/workspace/scripts/daily-tasks.sh vibecoding`
- 如果收到 "reading-notes" → 运行 `/home/kai/.openclaw/workspace/scripts/daily-tasks.sh reading-notes`

### 内容生成任务（创建页面 + sub-agent 生成内容）
以下任务需要通过 sub-agent 生成高质量内容：

- 如果收到 "daily-aigc" → 
  1. 运行 `/home/kai/.openclaw/workspace/scripts/daily-tasks.sh daily-aigc` 创建页面
  2. 通过 sub-agent 生成 AIGC 前沿内容并追加到页面

- 如果收到 "daily-news" → 
  1. 运行 `/home/kai/.openclaw/workspace/scripts/daily-tasks.sh daily-news` 创建页面
  2. 通过 sub-agent 生成每日新闻内容并追加到页面

- 如果收到 "claude-code-insights" → 
  1. 运行 `/home/kai/.openclaw/workspace/scripts/daily-tasks.sh claude-code-insights` 创建页面
  2. 通过 sub-agent 生成 Claude Code 心得内容并追加到页面

- 如果收到 "github-trending" → 
  1. 运行 `/home/kai/.openclaw/workspace/scripts/daily-tasks.sh github-trending` 创建页面
  2. 通过 sub-agent 生成 GitHub Trending 内容并追加到页面

- 如果收到 "github-review" → 
  运行 `/home/kai/.openclaw/workspace/scripts/github-review.sh`

- 如果收到 "failure-lessons" → 
  1. 运行 `/home/kai/.openclaw/workspace/scripts/daily-tasks.sh failure-lessons` 创建页面
  2. 通过 sub-agent 生成失败经验内容并追加到页面

- 如果收到 "tech-research" → 
  1. 运行 `/home/kai/.openclaw/workspace/scripts/daily-tasks.sh tech-research` 创建页面
  2. 通过 sub-agent 生成技术研究内容并追加到页面

- 如果收到 "mental-models" → 
  1. 运行 `/home/kai/.openclaw/workspace/scripts/daily-tasks-v3.sh mental-models` 创建页面和内容
  2. 注意：由于 Notion API 2000 字符限制，采用分段添加策略
  3. 使用 PAGE_ID: 2fc11082-af8e-81de-98bb-d1741c3cee68 (技术研究页面)
  4. 内容要求：
     - 按星期轮换主题（经济、心理、物理、生物、哲学、伟人、综合）
     - 检查历史记录避免重复
     - 包含核心概念、来源背景、应用场景、相关模型、实践建议
     - 符合 Notion 格式标准（callout 摘要、heading_2、来源链接）
     - 分段添加（每段 <2000 字符）

- 如果收到 "knowledge-viz" → 
  1. 运行 `/home/kai/.openclaw/workspace/scripts/daily-tasks.sh knowledge-viz` 创建页面
  2. 通过 sub-agent 根据 `/home/kai/.openclaw/workspace/scripts/prompts/knowledge-viz-prompt.md` 生成知识可视化追踪内容并追加到页面

- 如果收到 "uml-tech-radar" → 
  1. 运行 `/home/kai/.openclaw/workspace/scripts/daily-tasks.sh uml-tech-radar` 创建页面
  2. 通过 sub-agent 生成技术雷达内容并追加到页面

- 如果收到 "daily-language" →
  1. 通过 sub-agent 生成每日英语德语内容并创建 Notion 页面
  2. **必须使用去重工具**：
     - 生成前：检查"每日一句"是否重复
       ```bash
       python /home/kai/.openclaw/workspace/scripts/lib/dedupe-validator.py \
         english-german check --quote "待选格言" --author "作者名"
       ```
     - 生成后：记录已使用的格言
       ```bash
       python /home/kai/.openclaw/workspace/scripts/lib/dedupe-validator.py \
         english-german add --quote "实际格言" --author "作者" --source "来源" --page-id "页面ID"
       ```
  3. 内容要求：
     - 英语：每日一句（必须去重）+ 语法要点 + 重点词汇 + 学习小贴士
     - 德语：每日一句（必须去重）+ 语法要点 + 重点词汇 + 动词变位表
     - 避免重复主题（如连续两天讲同一语法点）


## 已配置的Cron任务
所有定时任务通过Clawdbot cron系统管理,无需手动触发。主要任务执行时间(凌晨2:00-5:00):
- 02:00 - GitHub代码审查
- 03:30 - VibeCoding
- 03:40 - 读书笔记
- 03:50 - 失败经验
- 04:00 - 技术研究
- 04:10 - 每日英语德语
- 04:20 - AIGC前沿总结
- 04:30 - 每日新闻
- 04:40 - Claude Code心得
- 04:50 - GitHub Trending
- 05:00 - 投资大师思想精华
- 05:10 - 创业失败经验教训

## ⚠️ 内容质量验证机制

**执行后必须验证**：
1. 检查块数量：`notion-cli block list PAGE_ID | grep "Blocks ("`
2. 判断标准：
   - ❌ <5块：严重失败，只有标题
   - ⚠️ 5-20块：内容过短，需要重新生成
   - ⚠️ 20-50块：内容偏短，视内容质量决定
   - ✅ ≥50块：内容充足
3. 失败处理：
   - 内容过短或为空：记录到 memory/YYYY-MM-DD.md，标记为失败
   - 检查 sub-agent 执行日志
   - 必要时手动触发重新生成

**记录格式**：
```markdown
### [任务名]
- **页面ID**：[ID]
- **块数量**：[数量]
- **状态**：✅ 完成 / ❌ 失败 / ⚠️ 偏短
- **备注**：[如有问题]
```

## 🔍 内容去重机制 (2026-03-19)

**去重工具**：`/home/kai/.openclaw/workspace/scripts/lib/dedupe-validator.py`

### 支持去重的任务

| 任务 | 任务类型 | 去重字段 |
|------|---------|---------|
| 每日英语德语 | `english-german` | 每日一句（quote, author） |
| Claude Code心得 | `claude-code` | 技巧（tip, category） |
| GitHub Trending | `github-trending` | 项目（repo, language） |
| 投资大师思想 | `investment` | 观点（quote, author, theme） |
| 创业失败经验 | `startup-failures` | 案例（company, industry） |
| 技术研究 | `tech-research` | 主题（topic, category） |
| 知识可视化研究 | `knowledge-viz` | 主题（topic, category） |

### Sub-agent 使用要求

在生成内容前，必须先检查去重：

```bash
# 1. 检查是否重复
python /home/kai/.openclaw/workspace/scripts/lib/dedupe-validator.py \
  <task-type> check \
  --<field> "内容"

# 2. 如果返回 0（不重复），生成内容
# 3. 生成成功后，添加到数据库
python /home/kai/.openclaw/workspace/scripts/lib/dedupe-validator.py \
  <task-type> add \
  --<field> "内容" \
  --page-id "页面ID"
```

### 示例（每日英语德语）

```bash
# 检查每日一句
python /home/kai/.openclaw/workspace/scripts/lib/dedupe-validator.py \
  english-german check \
  --quote "Stay hungry, stay foolish." \
  --author "Steve Jobs"

# 如果不重复，生成内容后添加
python /home/kai/.openclaw/workspace/scripts/lib/dedupe-validator.py \
  english-german add \
  --quote "Stay hungry, stay foolish." \
  --author "Steve Jobs" \
  --source "Stanford Commencement Speech" \
  --page-id "页面ID"
```

### 去重算法

- **相似度阈值**：0.7（70%）
- **匹配方式**：
  - 完全匹配：1.0
  - 包含关系：0.8
  - 字符重叠：Jaccard 相似度

详细文档：`/home/kai/.openclaw/workspace/docs/dedupe-system.md`
