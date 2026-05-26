# 去重工具强制使用规范

## ⚠️ 问题背景

**2026-03-19 发现问题**：
- 每日心智模型重复
- 每日一句重复
- 历史文件只有 2 条记录（最近一周的模型都没有被记录）

**根本原因**：
- Prompt 只要求"读取历史文件"，依赖 sub-agent 手动检查
- **没有强制使用去重工具**
- **没有调用 check 和 add 命令**

---

## ✅ 强制执行规范

### 所有每日搜索归纳型任务必须：

1. **生成前检查**：使用去重工具检查
2. **如果重复**：重新选择内容
3. **生成后添加**：添加到数据库
4. **更新历史**：更新历史文件（手动）

---

## 工具使用指南

### 1. 每日英语德语（english-german）

```bash
# 检查每日一句
python3 /home/kai/.openclaw/workspace/scripts/lib/dedupe-validator.py \
  english-german check \
  --quote "每日一句内容" \
  --author "作者"

# 添加到数据库
python3 /home/kai/.openclaw/workspace/scripts/lib/dedupe-validator.py \
  english-german add \
  --quote "每日一句内容" \
  --author "作者" \
  --source "来源" \
  --page-id "Notion页面ID"
```

### 2. 心智模型（mental-models）

```bash
# 使用专用工具（推荐）
python3 /home/kai/.openclaw/workspace/scripts/lib/mental-models-validator.py \
  check --name "模型名称"

python3 /home/kai/.openclaw/workspace/scripts/lib/mental-models-validator.py \
  add --name "模型名称" --category "类别" --page-id "页面ID"

# 或使用通用工具
python3 /home/kai/.openclaw/workspace/scripts/lib/dedupe-validator.py \
  mental-models check \
  --name "模型名称" \
  --category "类别"
```

### 3. Claude Code 心得（claude-code）

```bash
# 检查技巧
python3 /home/kai/.openclaw/workspace/scripts/lib/dedupe-validator.py \
  claude-code check \
  --tip "技巧内容" \
  --category "分类"

# 添加到数据库
python3 /home/kai/.openclaw/workspace/scripts/lib/dedupe-validator.py \
  claude-code add \
  --tip "技巧内容" \
  --category "分类" \
  --page-id "Notion页面ID"
```

### 4. GitHub Trending（github-trending）

```bash
# 检查项目
python3 /home/kai/.openclaw/workspace/scripts/lib/dedupe-validator.py \
  github-trending check \
  --repo "owner/repo" \
  --language "Python"

# 批量添加（推荐）
python3 /home/kai/.openclaw/workspace/scripts/lib/dedupe-validator.py \
  github-trending batch --file projects.json --page-id "页面ID"
```

### 5. 投资大师思想（investment）

```bash
# 检查观点
python3 /home/kai/.openclaw/workspace/scripts/lib/dedupe-validator.py \
  investment check \
  --quote "观点内容" \
  --author "巴菲特" \
  --theme "投资理念"

# 添加到数据库
python3 /home/kai/.openclaw/workspace/scripts/lib/dedupe-validator.py \
  investment add \
  --quote "观点内容" \
  --author "作者" \
  --theme "主题" \
  --page-id "Notion页面ID"
```

### 6. 创业失败经验（startup-failures）

```bash
# 检查案例
python3 /home/kai/.openclaw/workspace/scripts/lib/dedupe-validator.py \
  startup-failures check \
  --company "公司名称" \
  --industry "行业"

# 添加到数据库
python3 /home/kai/.openclaw/workspace/scripts/lib/dedupe-validator.py \
  startup-failures add \
  --company "公司名称" \
  --industry "行业" \
  --failure-reason "失败原因" \
  --page-id "Notion页面ID"
```

### 7. 技术研究（tech-research）

```bash
# 检查主题
python3 /home/kai/.openclaw/workspace/scripts/lib/dedupe-validator.py \
  tech-research check \
  --topic "研究主题" \
  --category "分类"

# 添加到数据库
python3 /home/kai/.openclaw/workspace/scripts/lib/dedupe-validator.py \
  tech-research add \
  --topic "研究主题" \
  --category "分类" \
  --keywords "关键词1,关键词2" \
  --page-id "Notion页面ID"
```

---

## Prompt 模板

在所有每日任务的 prompt 中添加以下内容：

```markdown
## ⚠️ 去重要求（强制执行）

### 第一步：生成前检查

**必须使用去重工具检查内容是否重复！**

```bash
# 检查是否重复（返回 0=不重复，1=重复）
python3 /home/kai/.openclaw/workspace/scripts/lib/dedupe-validator.py \
  <task-type> check \
  --<field> "内容"
```

### 第二步：如果重复

- ❌ **禁止继续使用重复内容**
- ✅ **重新选择新内容**
- ✅ **再次检查，直到返回 0**

### 第三步：生成成功后

**必须添加到去重数据库！**

```bash
# 添加到数据库
python3 /home/kai/.openclaw/workspace/scripts/lib/dedupe-validator.py \
  <task-type> add \
  --<field> "内容" \
  --page-id "Notion页面ID"
```

### 第四步：更新历史文件（可选）

追加到 `memory/YYYY-MM-DD.md` 或相应的历史文件。

---

**如果工具不可用**：
1. 读取历史文件
2. 手动检查
3. 生成后手动更新
```

---

## 检查清单

### Sub-agent 执行前检查

- [ ] 是否使用了去重工具检查？
- [ ] 如果重复，是否重新选择？
- [ ] 生成后是否添加到数据库？
- [ ] 是否更新了历史文件？

### 管理员检查（每日）

```bash
# 查看所有任务统计
python3 /home/kai/.openclaw/workspace/scripts/lib/dedupe-validator.py stats

# 查看特定任务历史
python3 /home/kai/.openclaw/workspace/scripts/lib/dedupe-validator.py \
  english-german list --limit 50

# 检查数据库文件
ls -la /home/kai/.openclaw/workspace/memory/dedupe/
```

---

## 故障排查

### 问题：工具命令失败

**检查 Python 环境**：
```bash
which python3
python3 --version
```

**检查文件权限**：
```bash
ls -la /home/kai/.openclaw/workspace/scripts/lib/dedupe-validator.py
chmod +x /home/kai/.openclaw/workspace/scripts/lib/dedupe-validator.py
```

### 问题：数据库文件不存在

**首次使用会自动创建**，如果失败：
```bash
mkdir -p /home/kai/.openclaw/workspace/memory/dedupe
python3 /home/kai/.openclaw/workspace/scripts/lib/dedupe-validator.py stats
```

### 问题：重复内容仍然出现

**检查 Prompt**：
- 确认包含去重要求
- 确认强制使用工具
- 确认检查返回值

**检查 Sub-agent 执行日志**：
- 是否调用了 check 命令？
- 是否处理了返回值 1？
- 是否调用了 add 命令？

---

## 更新记录

- **2026-03-19**: 创建文档，响应心智模型和每日一句重复问题
- **2026-03-19**: 更新 mental-models-prompt.md，强制使用去重工具
