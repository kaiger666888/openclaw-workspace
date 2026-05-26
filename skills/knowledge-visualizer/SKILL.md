# Knowledge Visualizer

将知识文档自动转化为可视化教学资产的核心 Skill。

## 愿景

**输入**: Markdown 知识文档
**输出**: 可交互的 HTML 动画 + 教学视频
**原则**: 零人工决策，全自动化

## 工作流

```
知识文档
    ↓
[1] 解析 (knowledge-parser)
    - 提取概念、关系、流程
    - 识别适合可视化的内容
    ↓
[2] UML 生成 (uml-designer)
    - 选择合适的图表类型
    - 生成 PlantUML 代码
    ↓
[3] 动画编排 (animation-orchestrator)
    - 设计教学动画序列
    - 定义节奏和重点
    ↓
[4] 渲染 (html-renderer)
    - 生成 HTML + CSS 动画
    - 添加交互控制
    ↓
[5] 导出 (video-exporter)
    - 录制动画为视频
    - 生成教学网页
    ↓
教学资产 (网页 + 视频)
```

## 子 Skills

### 1. knowledge-parser
**职责**: 理解知识文档结构

输入: Markdown 文档
输出: JSON 结构化数据
```json
{
  "title": "文档标题",
  "concepts": [
    {"name": "概念1", "definition": "...", "importance": 0.9}
  ],
  "relationships": [
    {"from": "概念A", "to": "概念B", "type": "depends_on"}
  ],
  "processes": [
    {"name": "流程1", "steps": [...], "isLinear": true}
  ],
  "suitableForVisualization": ["flowchart", "sequence", "class"]
}
```

### 2. uml-designer
**职责**: 将结构化数据转为 PlantUML

策略:
- 线性流程 → 活动图
- 概念关系 → 类图/思维导图
- 时序交互 → 时序图
- 状态变化 → 状态图

### 3. animation-orchestrator
**职责**: 设计教学动画序列

输出:
```json
{
  "scenes": [
    {
      "elements": ["概念A", "概念B"],
      "action": "fade_in",
      "duration": 1.5,
      "narration": "首先我们看概念A..."
    }
  ],
  "totalDuration": 45
}
```

### 4. html-renderer
**职责**: 渲染可交互 HTML

技术选型:
- SVG.js 或 D3.js (轻量级动画)
- CSS Keyframes (简单动画)
- Puppeteer (预渲染复杂动画)

### 5. video-exporter
**职责**: 导出视频和网页

- HTML → Puppeteer 录制 → WebM/MP4
- 生成包含播放器的独立网页

## 使用方式

```bash
# 基础用法
knowledge-visualizer --input doc.md --output ./output

# 高级选项
knowledge-visualizer \
  --input doc.md \
  --output ./output \
  --style educational \
  --duration 60 \
  --format html,video
```

## MVP 目标

1. ✅ 支持 Markdown 输入
2. ✅ 自动识别至少 3 种图表类型
3. ✅ 生成带动画的 HTML
4. ✅ 导出 WebM 视频
5. ✅ 零人工决策

## 设计原则

1. **智能默认** - 每个决策点都有合理默认值
2. **渐进增强** - 基础功能零配置，高级功能可选
3. **教学优先** - 动画设计服务于理解，不只是炫酷
4. **模块化** - 每个子 skill 可独立使用

---

*此 Skill 正在开发中，当前版本: 0.1.0*
