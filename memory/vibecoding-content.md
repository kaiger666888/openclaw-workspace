## 🎯 今日编码

### 项目：Prompt 工程标准化系统
- **类型**: 基础设施 / 文档工程
- **技术栈**: Markdown, Notion API, Shell scripting
- **目标**: 为所有定时任务建立统一的prompt规范

---

## 💻 代码片段

### Prompt 文件模板结构

```markdown
# [任务名称] 生成 Prompt

## 任务目标
[描述任务的核心目标]

## 内容方向
### [分类1]
### [分类2]

## 搜索任务
### P0 - 必须搜索
### P1 - 至少搜索2个
### P2 - 可选搜索

## 输出格式
[页面标题 + 内容结构模板]

## 质量标准
### ✅ 必须包含
### ❌ 不要包含
### 📊 数量控制
```

**用途**: 统一所有定时任务的输出质量和格式

**亮点**: 分级搜索关键词（P0/P1/P2）确保内容深度，模板化输出降低维护成本

---

### Notion 内容追加脚本

```bash
# 解决 Notion API 2000 字符限制
cat > /tmp/content.md << 'EOF'
长内容...
EOF

python3 /home/kai/.openclaw/workspace/scripts/lib/notion-append.py PAGE_ID /tmp/content.md
```

**用途**: 自动分段追加长内容到 Notion 页面

**亮点**: 通过文件中转 + Python 自动分段，突破 API 限制

---

## 🔧 技术探索

### Prompt 工程模式

#### 问题
多个定时任务的输出格式不统一，质量参差不齐，难以维护

#### 发现
采用标准化 prompt 模板可以：
1. **一致性**: 所有任务遵循相同结构
2. **可控性**: 通过质量标准约束输出
3. **可扩展**: 新任务直接复制模板

#### 设计原则

```
1. 搜索关键词分级
   - P0: 必须搜索（核心信息源）
   - P1: 至少选2个（补充视角）
   - P2: 可选（深度扩展）

2. 输出格式模板化
   - 页面标题规范
   - Markdown 结构一致
   - 区块清晰分隔

3. 质量标准明确
   - ✅ 必须包含
   - ❌ 禁止内容
   - 📊 数量控制
```

---

## 📊 Prompt 文件清单

| 任务 | 文件名 | 状态 |
|------|--------|------|
| AIGC前沿总结 | `aigc-summary-prompt.md` | ✅ |
| 每日新闻 | `daily-news-prompt.md` | ✅ |
| Claude Code心得 | `claude-code-insights-prompt.md` | ✅ |
| GitHub Trending | `github-trending-prompt.md` | ✅ |
| 投资大师思想精华 | `investment-wisdom-prompt.md` | ✅ |
| 创业失败经验教训 | `startup-failure-lessons-prompt.md` | ✅ |
| 技术研究 | `tech-research-prompt.md` | ✅ |
| 每日英语德语 | `daily-language-prompt.md` | ✅ |
| VibeCoding | `vibecoding-prompt.md` | ✅ |
| 读书笔记 | `reading-notes-prompt.md` | ✅ |
| 失败经验 | `failure-lessons-prompt.md` | ✅ |
| 知识可视化研究 | `knowledge-viz-prompt.md` | ✅ |
| umlVisionAgent技术雷达 | `uml-tech-radar-prompt.md` | ✅ |

**总计**: 13 个 prompt 文件，覆盖所有定时任务

---

## 💡 今日心得

Prompt 工程不仅是 AI 对话的技巧，更是**系统化知识生产**的基础设施。通过标准化模板：

1. **降低认知负担** - 不用每次从头设计结构
2. **保证输出质量** - 明确的质量标准作为检查清单
3. **便于迭代优化** - 修改模板即可影响所有任务

这次实践验证了"慢思考 + 快执行"的方法论：花时间设计好模板，后续执行就变得高效且可靠。

---

## 🔜 明日计划

- [ ] 测试新 prompt 模板在实际任务中的效果
- [ ] 根据执行结果调整搜索关键词
- [ ] 探索 prompt 版本管理方案

---

_编码理念: 标准化是规模化的前提_
