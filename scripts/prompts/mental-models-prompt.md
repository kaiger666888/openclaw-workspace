# 每日心智模型生成 Prompt

## 任务目标

每日推送一个高质量心智模型到 Notion，帮助构建跨学科思维格栅。

## 内容要求

### 1. 多样化来源（轮换）
- **周一**：经济学/商学模型（机会成本、边际效应、比较优势等）
- **周二**：心理学/认知科学（认知偏差、启发式、系统1/2思维等）
- **周三**：物理学/数学模型（临界点、幂律分布、网络效应等）
- **周四**：生物学/进化论（自然选择、适应性、红皇后效应等）
- **周五**：哲学/逻辑学（第一性原理、奥卡姆剃刀、证伪主义等）
- **周六**：伟人思想（芒格、巴菲特、纳瓦尔、塔勒布等）
- **周日**：综合应用（多模型交叉、实践案例等）

### 2. 内容结构

```markdown
# [心智模型名称]

> 一句话核心定义

## 📚 核心概念
- 模型的本质是什么
- 关键要素和原理
- 为什么有效

## 🌍 来源/背景
- 起源学科
- 提出者/发展历程
- 相关理论

## 💡 应用场景
- 商业决策
- 个人成长
- 投资判断
- 日常选择

## 🔗 相关模型
- 模型A：[链接]
- 模型B：[链接]
- 模型C：[链接]

## ⚡ 实践建议
- 如何开始使用
- 常见误区
- 进阶应用

## 📖 推荐阅读
- 书籍/文章链接
- 案例研究
```

### 3. 质量标准

- ✅ **准确性**：概念解释准确，不误导
- ✅ **实用性**：提供具体应用场景和行动建议
- ✅ **连接性**：关联其他模型，构建思维网络
- ✅ **简洁性**：核心概念清晰，避免冗余
- ✅ **来源可靠**：引用权威来源，标注出处

### 4. 避免重复（强制执行 - 使用工具）

**⚠️ 必须使用去重工具，禁止手动检查！**

**第一步：选择模型前，使用工具检查**
```bash
# 检查模型是否重复（返回 0=不重复，1=重复）
python3 /home/kai/.openclaw/workspace/scripts/lib/dedupe-validator.py \
  mental-models check \
  --name "模型名称" \
  --category "类别"
```

**第二步：如果返回 1（重复），必须重新选择**
- ❌ 禁止继续使用重复的模型
- ✅ 重新选择一个新模型
- ✅ 再次检查，直到返回 0

**第三步：内容生成成功后，必须添加到数据库**
```bash
# 添加到去重数据库
python3 /home/kai/.openclaw/workspace/scripts/lib/dedupe-validator.py \
  mental-models add \
  --name "模型名称" \
  --category "类别" \
  --page-id "Notion页面ID" \
  --sources "来源1" "来源2"
```

**第四步：更新历史文件（手动）**
追加到 `mental-models-history.md`：
```markdown
- YYYY-MM-DD: 模型名称（类别）
  - 来源：[搜索来源]
  - 页面ID: [Notion页面ID]
```

**工具位置**：
- **心智模型专用**：`/home/kai/.openclaw/workspace/scripts/lib/mental-models-validator.py`
- 通用去重：`/home/kai/.openclaw/workspace/scripts/lib/dedupe-validator.py`

**使用心智模型专用工具（推荐）**：
```bash
# 检查重复
python3 /home/kai/.openclaw/workspace/scripts/lib/mental-models-validator.py \
  check --name "模型名称"

# 添加到数据库
python3 /home/kai/.openclaw/workspace/scripts/lib/mental-models-validator.py \
  add --name "模型名称" --category "类别" --page-id "页面ID"
```

**如果工具不可用**：
1. 读取历史文件：`cat /home/kai/.openclaw/workspace/memory/mental-models-history.md`
2. 手动检查是否重复
3. 生成后手动更新历史文件和数据库

### 5. 搜索策略

**优先方案**：使用 web_search
```python
# 搜索心智模型相关内容
web_search(
    query="mental model [主题] examples applications",
    count=10
)

# 搜索伟人思想
web_search(
    query="[人物名] key ideas mental models",
    count=10
)
```

**降级方案**：如果 web_search 不可用（代理故障或网络问题），使用以下策略：

1. **使用 web_fetch 抓取固定网站**：
```python
# 心智模型相关网站
web_fetch("https://fs.blog/mental-models/")  # Farnam Street
web_fetch("https://www.modelthinkers.com/")  # Model Thinkers
web_fetch("https://en.wikipedia.org/wiki/Mental_model")

# 伟人思想
web_fetch("https://www.berkshirehathaway.com/letters/letters.html")  # 巴菲特致股东信
web_fetch("https://fs.blog/tag/charlie-munger/")  # 芒格相关
```

2. **使用本地知识库**：
```bash
# 搜索历史记录
cat /home/kai/.openclaw/workspace/memory/mental-models-history.md

# 搜索相关记忆
grep -r "心智模型\|mental model" /home/kai/.openclaw/workspace/memory/*.md
```

3. **基于经典模型生成**（最后手段）：
   - 使用已知的心智模型知识
   - 标注"来源：经典理论"
   - 确保准确性

**搜索限制**：
- web_search: ≤ 3 次，优先英文
- web_fetch: ≤ 5 次，选择权威网站
- 如果都失败：基于经验生成并标注来源

## Notion 格式要求

使用 `markdown-to-notion.py` 转换：
```bash
/home/kai/.openclaw/workspace/scripts/lib/markdown-to-notion.py content.md > blocks.json
```

格式检查：
- [ ] 顶部有 callout 摘要
- [ ] 使用 heading_2 作为分类标题
- [ ] 链接格式：`[来源名称](URL)`
- [ ] 使用 divider 分隔各部分
- [ ] 底部有参考来源

## 示例输出

### 机会成本（经济学）

```markdown
# 机会成本

> 每个选择的真实成本是你放弃的次优选择

## 📚 核心概念
- 定义：做出一个选择时放弃的其他选择中价值最高的那个
- 关键要素：稀缺性、选择、价值评估
- 为什么有效：揭示隐藏成本，优化资源配置

## 🌍 来源/背景
- 起源：经济学，19世纪
- 提出者：弗里德里希·冯·维塞尔
- 相关理论：边际分析、比较优势

## 💡 应用场景
- 商业：投资决策（选择A项目意味着放弃B项目）
- 个人：时间管理（看电影 vs 学习新技能）
- 投资：资产配置（股票 vs 债券）
- 日常：消费选择（买咖啡 vs 存钱）

## 🔗 相关模型
- 沉没成本谬误：已发生成本不应影响未来决策
- 边际效应：额外一单位的收益递减
- 比较优势：专注相对优势领域

## ⚡ 实践建议
1. **显式列出选项**：写下所有可能的选择
2. **评估每个选项的价值**：量化或排序
3. **识别次优选择**：明确你放弃了什么
4. **考虑长期影响**：不只看短期得失

常见误区：
- ❌ 忽略隐形成本（时间、精力、机会）
- ❌ 过度分析导致决策瘫痪
- ❌ 只考虑金钱成本

## 📖 推荐阅读
- [Thinking, Fast and Slow](https://example.com) - Daniel Kahneman
- [The Art of Thinking Clearly](https://example.com) - Rolf Dobelli
- [Farnam Street Blog](https://fs.blog) - Shane Parrish

---

**来源**：经济学基础理论 | **推送日期**：2026-03-09
```

## 执行流程

1. 确定今日主题（根据星期几）
2. 搜索高质量内容（≤3次）
3. 提取核心概念和应用场景
4. 检查历史记录避免重复
5. 生成 Markdown 内容
6. 转换为 Notion 格式
7. 追加到 Notion 页面
8. 记录到 memory/YYYY-MM-DD.md

## 注意事项

- 搜索使用 `search_lang="zh-hans"` 进行中文搜索
- 优先使用英文搜索获取更全面结果
- 遇到速率限制时可重试
- 每个模型都要有实用价值，避免纯理论
- 链接必须有效且来源可靠
