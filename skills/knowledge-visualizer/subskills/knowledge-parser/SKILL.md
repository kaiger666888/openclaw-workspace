# Knowledge Parser

解析知识文档，提取可可视化的结构化数据。

## 职责

**输入**: Markdown 知识文档
**输出**: JSON 结构化数据（概念、关系、流程）

## 解析策略

### 1. 文档结构识别

```markdown
# 主标题 → 主题
## 二级标题 → 章节/概念组
### 三级标题 → 具体概念
- 列表项 → 属性/步骤
> 引用 → 重要说明
```

### 2. 概念提取

识别模式:
- **定义**: "X 是...", "X 指的是..."
- **特征**: "X 的特点是...", "X 具有..."
- **对比**: "X 与 Y 的区别...", "相比于 Y，X..."
- **例子**: "例如...", "比如..."

### 3. 关系识别

常见关系类型:
- `depends_on`: 依赖关系 ("X 需要 Y", "X 基于 Y")
- `contains`: 包含关系 ("X 包括 Y", "Y 是 X 的一部分")
- `relates_to`: 关联关系 ("X 与 Y 相关")
- `precedes`: 顺序关系 ("X 之前是 Y", "X 之后是 Y")
- `contrasts`: 对比关系 ("X 相比于 Y")

### 4. 流程识别

识别模式:
- 步骤序列 (1. 2. 3. 或 第一步、第二步)
- 条件分支 (如果...那么...)
- 循环结构 (重复...直到...)
- 并行处理 (同时...)

## 输出格式

```json
{
  "metadata": {
    "title": "文档标题",
    "summary": "一句话总结",
    "difficulty": "beginner|intermediate|advanced",
    "estimatedReadTime": 5
  },
  "concepts": [
    {
      "id": "concept-1",
      "name": "概念名称",
      "definition": "定义文本",
      "importance": 0.9,
      "keywords": ["关键词1", "关键词2"]
    }
  ],
  "relationships": [
    {
      "from": "concept-1",
      "to": "concept-2",
      "type": "depends_on",
      "label": "依赖关系描述"
    }
  ],
  "processes": [
    {
      "id": "process-1",
      "name": "流程名称",
      "type": "linear|branching|parallel|cyclic",
      "steps": [
        {
          "id": "step-1",
          "description": "步骤描述",
          "next": ["step-2"]
        }
      ]
    }
  ],
  "visualization": {
    "recommendedCharts": ["flowchart", "sequence", "mindmap"],
    "focusAreas": ["最重要的概念"],
    "suggestedPacing": "fast|medium|slow"
  }
}
```

## 实现方式

使用 Claude Code 的 LLM 能力进行智能解析:

```bash
# 调用示例
claude-code --skill knowledge-parser \
  --input doc.md \
  --output parsed.json \
  --prompt "解析此文档，提取概念、关系和流程"
```

## 提示词模板

```
你是一个知识结构化专家。请分析以下 Markdown 文档:

{document}

请提取:
1. 核心概念（名称、定义、重要性 0-1）
2. 概念间的关系（类型：depends_on/contains/relates_to/precedes/contrasts）
3. 可视化的流程（步骤、类型、流向）
4. 推荐的图表类型

输出格式: JSON
```

## 示例

**输入**:
```markdown
# RESTful API 设计

REST 是一种软件架构风格，基于 HTTP 协议。

## 核心原则

### 无状态性
每个请求包含所有必要信息，服务器不保存客户端状态。

### 统一接口
使用标准 HTTP 方法：GET、POST、PUT、DELETE。

## 设计流程

1. 识别资源
2. 定义 URI
3. 选择 HTTP 方法
4. 设计响应格式
```

**输出**:
```json
{
  "metadata": {
    "title": "RESTful API 设计",
    "summary": "REST 架构风格及其设计原则",
    "difficulty": "intermediate"
  },
  "concepts": [
    {
      "id": "rest",
      "name": "REST",
      "definition": "一种软件架构风格，基于 HTTP 协议",
      "importance": 1.0
    },
    {
      "id": "statelessness",
      "name": "无状态性",
      "definition": "每个请求包含所有必要信息",
      "importance": 0.9
    },
    {
      "id": "uniform-interface",
      "name": "统一接口",
      "definition": "使用标准 HTTP 方法",
      "importance": 0.8
    }
  ],
  "relationships": [
    {
      "from": "statelessness",
      "to": "rest",
      "type": "contains",
      "label": "是核心原则之一"
    },
    {
      "from": "uniform-interface",
      "to": "rest",
      "type": "contains",
      "label": "是核心原则之一"
    }
  ],
  "processes": [
    {
      "id": "design-process",
      "name": "RESTful API 设计流程",
      "type": "linear",
      "steps": [
        {"id": "s1", "description": "识别资源", "next": ["s2"]},
        {"id": "s2", "description": "定义 URI", "next": ["s3"]},
        {"id": "s3", "description": "选择 HTTP 方法", "next": ["s4"]},
        {"id": "s4", "description": "设计响应格式", "next": []}
      ]
    }
  ],
  "visualization": {
    "recommendedCharts": ["flowchart", "mindmap"],
    "focusAreas": ["无状态性", "统一接口"],
    "suggestedPacing": "medium"
  }
}
```

---

*版本: 0.1.0*
