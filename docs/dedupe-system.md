# 通用去重系统使用指南

## 概述

`dedupe-validator.py` 是一个通用的去重验证框架，用于防止每日搜索归纳型任务的内容重复。

## 支持的任务类型

| 任务类型 | 数据库名称 | 主要字段 | 用途 |
|---------|-----------|---------|------|
| `english-german` | english-quotes-db.json | quote, author, source | 每日一句去重 |
| `claude-code` | claude-code-tips-db.json | tip, category | 技巧去重 |
| `github-trending` | github-projects-db.json | repo, language, description | 项目去重 |
| `investment` | investment-wisdom-db.json | quote, author, theme | 观点去重 |
| `startup-failures` | startup-cases-db.json | company, industry, failure_reason | 案例去重 |
| `tech-research` | tech-topics-db.json | topic, category, keywords | 主题去重 |
| `knowledge-viz` | knowledge-viz-topics-db.json | topic, category, tools | 主题去重 |

## 使用方法

### 1. 检查是否重复

```bash
# 检查每日一句
python /home/kai/.openclaw/workspace/scripts/lib/dedupe-validator.py \
  english-german check \
  --quote "Stay hungry, stay foolish." \
  --author "Steve Jobs"

# 检查 GitHub 项目
python /home/kai/.openclaw/workspace/scripts/lib/dedupe-validator.py \
  github-trending check \
  --repo "openai/gpt-5" \
  --language "Python"
```

**返回值：**
- `0`: 不重复，可以使用
- `1`: 重复，应跳过

### 2. 添加新内容

```bash
# 添加每日一句
python /home/kai/.openclaw/workspace/scripts/lib/dedupe-validator.py \
  english-german add \
  --quote "The only way to do great work is to love what you do." \
  --author "Steve Jobs" \
  --source "Stanford Commencement Speech, 2005"

# 添加技巧
python /home/kai/.openclaw/workspace/scripts/lib/dedupe-validator.py \
  claude-code add \
  --tip "使用 CLAUDE.md 定义项目上下文和偏好" \
  --category "效率"
```

### 3. 列出历史记录

```bash
# 列出最近 50 条
python /home/kai/.openclaw/workspace/scripts/lib/dedupe-validator.py \
  english-german list --limit 50
```

### 4. 查看统计

```bash
# 查看所有任务统计
python /home/kai/.openclaw/workspace/scripts/lib/dedupe-validator.py stats

# 查看特定任务统计
python /home/kai/.openclaw/workspace/scripts/lib/dedupe-validator.py english-german stats
```

## 在 Sub-agent 任务中使用

### Prompt 示例（每日英语德语）

```markdown
## 去重要求

生成内容前，必须检查去重：

1. **检查每日一句是否重复**：
   ```bash
   python /home/kai/.openclaw/workspace/scripts/lib/dedupe-validator.py \
     english-german check \
     --quote "你的每日一句" \
     --author "作者"
   ```

2. **如果返回 1（重复）**：
   - 重新选择一句
   - 再次检查
   - 直到找到不重复的句子

3. **内容生成成功后，添加到数据库**：
   ```bash
   python /home/kai/.openclaw/workspace/scripts/lib/dedupe-validator.py \
     english-german add \
     --quote "每日一句" \
     --author "作者" \
     --source "来源"
   ```

## 去重算法

### 相似度计算

1. **标准化文本**：去除空格、转小写、去标点
2. **完全匹配**：相似度 1.0
3. **包含关系**：相似度 0.8
4. **字符重叠**：Jaccard 相似度

### 阈值设置

- 默认阈值：`0.7`（70%）
- 可通过 `--threshold` 调整
- 建议保持默认值

## 数据库结构

每个任务的数据库文件位于：`memory/dedupe/<task>-db.json`

```json
{
  "meta": {
    "version": "1.0",
    "task_type": "english-german",
    "task_name": "每日英语德语",
    "created_at": "2026-03-19T08:00:00",
    "last_updated": "2026-03-19T08:30:00",
    "total_count": 45
  },
  "items": [
    {
      "id": "english-german_20260319_001",
      "date": "2026-03-19",
      "quote": "Stay hungry, stay foolish.",
      "author": "Steve Jobs",
      "source": "Stanford Commencement Speech, 2005",
      "page_id": "xxx-xxx-xxx"
    }
  ]
}
```

## 最佳实践

1. **生成前检查**：在选择内容时就检查去重，避免浪费时间生成重复内容
2. **批量去重**：如果生成多个项目（如 GitHub Trending），可以批量检查
3. **及时添加**：内容成功推送后立即添加到数据库
4. **定期维护**：定期查看统计，监控数据库增长

## 故障排查

### 数据库文件不存在

首次使用时会自动创建数据库文件。

### 检查命令失败

确保提供了必要字段：
```bash
# 查看任务需要的字段
python dedupe-validator.py --help
```

### 相似度计算不准确

调整阈值：
```bash
# 更严格（减少误判）
python dedupe-validator.py check --threshold 0.8 ...

# 更宽松（允许更多相似内容）
python dedupe-validator.py check --threshold 0.6 ...
```

## 更新日志

- **2026-03-19**: 初始版本，支持 7 种任务类型
