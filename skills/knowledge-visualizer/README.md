# UML Vision Agent

> 将知识文档自动转化为可视化教学资产

## 愿景

**输入**: Markdown 知识文档
**输出**: 可交互的 HTML 动画 + 教学视频
**原则**: 零人工决策，全自动化

## 架构

```
知识文档
    ↓
[1] knowledge-parser      # 解析文档结构
    ↓
[2] uml-designer          # 生成 PlantUML
    ↓
[3] animation-orchestrator # 设计动画序列
    ↓
[4] html-renderer         # 渲染 HTML 动画
    ↓
[5] video-exporter        # 导出视频
    ↓
教学资产 (网页 + 视频)
```

## 项目状态

🚧 **MVP 开发中** - 当前版本: 0.1.0

### 已完成
- ✅ 系统架构设计
- ✅ knowledge-parser skill 设计
- ✅ uml-designer skill 设计
- ✅ html-renderer skill 设计
- ✅ 核心编排脚本 (visualize.sh)
- ✅ 示例知识文档

### 进行中
- 🔄 PlantUML Server 集成
- 🔄 SVG 动画渲染
- 🔄 视频导出功能

### 计划中
- ⏳ Notion 集成
- ⏳ 多主题支持
- ⏳ Claude Code 完整集成

## 快速开始

```bash
# 基础用法
./visualize.sh --input doc.md --output ./output

# 查看帮助
./visualize.sh --help
```

## 技术栈

- **知识解析**: Claude Code + LLM
- **UML 生成**: PlantUML
- **动画渲染**: HTML5 + CSS3 + SVG.js
- **视频导出**: Puppeteer + FFmpeg
- **部署**: 静态站点 / Notion 嵌入

## 设计原则

1. **零决策** - 用户只需提供文档，系统自动完成剩余
2. **教学优先** - 动画服务于理解，不只是炫酷
3. **模块化** - 每个子 skill 可独立使用
4. **渐进增强** - 基础功能零配置，高级功能可选

## 示例

查看 `examples/` 目录中的示例知识文档和生成的教学资产。

## 许可证

MIT

---

*由 Clawd (OpenClaw) 创建和维护*
