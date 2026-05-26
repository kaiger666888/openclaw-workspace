# 心智模型系统 - 使用指南

> 更新时间：2026-03-13
> 系统版本：2.0（新增去重验证、JSON 数据库、用户反馈）

---

## 📦 系统组成

### 1. 去重验证脚本
**文件位置**：`/home/kai/.openclaw/workspace/scripts/lib/mental-models-validator.py`

**功能**：
- 检查心智模型是否已存在
- 添加新模型到数据库
- 按类别列出所有模型

**使用方法**：

```bash
# 检查模型是否重复
python3 mental-models-validator.py check --name "模型名称"

# 添加新模型
python3 mental-models-validator.py add \
  --name "第一性原理" \
  --category "哲学/逻辑学" \
  --page-id "页面ID" \
  --sources "来源1" "来源2"

# 列出所有模型
python3 mental-models-validator.py list
```

### 2. JSON 数据库
**文件位置**：`/home/kai/.openclaw/workspace/memory/mental-models-db.json`

**数据结构**：
```json
{
  "id": "mm_20260309_001",
  "date": "2026-03-09",
  "name": "机会成本",
  "category": "经济学/商学",
  "day_of_week": "周一",
  "status": "published",
  "page_id": "Notion页面ID",
  "sources": ["来源1", "来源2"],
  "keywords": ["关键词1", "关键词2"],
  "summary": "一句话总结"
}
```

**查询示例**：
```python
import json

with open('mental-models-db.json') as f:
    db = json.load(f)

# 查询所有经济学模型
economics_models = [
    m for m in db['models']
    if m['category'] == '经济学/商学'
]

# 查询本周推送的模型
from datetime import datetime, timedelta
week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
recent_models = [
    m for m in db['models']
    if m['date'] >= week_ago
]
```

### 3. 用户反馈系统
**文件位置**：
- 反馈数据库：`/home/kai/.openclaw/workspace/memory/mental-models-feedback.json`
- 管理脚本：`/home/kai/.openclaw/workspace/scripts/lib/mental-models-feedback.py`

**功能**：
- 收集用户评分和建议
- 查询模型反馈
- 统计分析
- 导出报告

**使用方法**：

```bash
# 添加评分反馈
python3 mental-models-feedback.py add \
  --model "机会成本" \
  --type "rating" \
  --content "非常实用" \
  --rating 5

# 添加改进建议
python3 mental-models-feedback.py add \
  --model "机会成本" \
  --type "suggestion" \
  --content "希望能增加实际案例"

# 查询模型反馈
python3 mental-models-feedback.py get --model "机会成本"

# 查看统计
python3 mental-models-feedback.py stats

# 导出报告
python3 mental-models-feedback.py export
```

**反馈类型**：
- `rating` - 评分反馈 (1-5星)
- `suggestion` - 改进建议
- `error` - 内容错误报告
- `request` - 新模型请求
- `application` - 应用案例分享

---

## 🔄 工作流程

### 推送新模型的完整流程

```bash
# 1. 确定今日类别（根据星期几）
# 周一：经济学/商学
# 周二：心理学/认知科学
# 周三：物理学/数学
# 周四：生物学/进化论
# 周五：哲学/逻辑学
# 周六：伟人思想
# 周日：综合应用

# 2. 搜索内容
web_search(query="mental model [主题] examples applications", count=10)

# 3. 选择模型名称后，立即验证去重
python3 mental-models-validator.py check --name "模型名称"

# 4. 如果不重复，生成内容并推送到 Notion

# 5. 推送成功后，添加到数据库
python3 mental-models-validator.py add \
  --name "模型名称" \
  --category "类别" \
  --page-id "Notion页面ID" \
  --sources "来源1" "来源2"

# 6. 用户反馈（可选）
# 用户可以在任何时候提供反馈
python3 mental-models-feedback.py add \
  --model "模型名称" \
  --type "rating" \
  --content "反馈内容" \
  --rating 4
```

---

## 📊 数据统计

### 当前数据库状态
- 总模型数：2 个
- 类别覆盖：2 个（经济学/商学、生物学/进化论）
- 待开发类别：5 个

### 反馈系统状态
- 总反馈数：0 条
- 平均评分：暂无

---

## 🔧 集成到定时任务

在 `/home/kai/.openclaw/workspace/scripts/prompts/mental-models-prompt.md` 中已包含去重流程：

```markdown
### 4. 避免重复（强制执行）

**第一步：读取历史文件**
```bash
cat /home/kai/.openclaw/workspace/memory/mental-models-history.md
```

**第二步：提取已推送模型名称**
从历史文件中提取所有 `模型名称`

**第三步：选择新模型时检查**
- ❌ 禁止选择历史文件中已存在的模型名称
- ✅ 必须选择全新的、未推送过的模型
```

**建议增强**：在定时任务脚本中，选择模型后立即调用验证脚本：

```bash
# 在生成内容前验证
python3 /home/kai/.openclaw/workspace/scripts/lib/mental-models-validator.py \
  check --name "$MODEL_NAME"

if [ $? -ne 0 ]; then
  echo "模型重复，重新选择"
  exit 1
fi
```

---

## 🎯 未来改进方向

1. **自动化评分分析** - 定期分析用户反馈，生成改进建议
2. **智能推荐** - 根据用户偏好和反馈，推荐相关模型
3. **知识图谱** - 构建模型之间的关联网络
4. **多语言支持** - 支持英文版模型推送
5. **Notion 集成** - 将反馈系统嵌入到 Notion 页面

---

## 📝 维护日志

- **2026-03-13**：
  - ✅ 创建去重验证脚本
  - ✅ 建立 JSON 数据库
  - ✅ 实现用户反馈系统
  - ✅ 测试所有功能正常

- **2026-03-12**：
  - 重构心智模型历史记录，按类别分组
  - 优化去重算法

- **2026-03-09**：
  - 系统上线，推送第一个模型（机会成本）

---

## 🆘 故障排除

### 问题：验证脚本报错"数据库文件不存在"
**解决方案**：脚本会自动从 Markdown 文件创建数据库，无需手动操作

### 问题：反馈无法添加
**检查**：
1. 确保反馈类型正确（rating/suggestion/error/request/application）
2. 评分必须在 1-5 之间
3. 所有必需参数都已提供

### 问题：重复模型仍被推送
**检查**：
1. 确保在推送前调用了验证脚本
2. 检查数据库文件是否正确更新
3. 验证脚本返回值为 0（成功）还是 1（失败）

---

**维护者**：Clawd AI Assistant
**联系方式**：通过对话提供反馈
