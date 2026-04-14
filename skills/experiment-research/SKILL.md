---
name: experiment-research
description: Experimental research with hypothesis-driven testing, automated validation loops, and structured result recording. Inspired by karpathy/autoresearch but adapted for general technical research (performance benchmarks, technology comparisons, feature evaluations).
metadata:
  clawdbot:
    always: false
    skillKey: experiment-research
---

# Experiment Research Skill

实验式研究助手 - 通过设计实验、执行测试、记录结果、验证假设，得出基于证据的研究结论。

## 核心理念

借鉴 karpathy/autoresearch 的**实验驱动研究**思想：

```
传统研究：搜索 → 整理 → 报告（信息聚合）
实验研究：假设 → 实验 → 验证 → 结论（证据驱动）
```

**关键差异**：
- ✅ **可量化** - 每个结论都有数据支持
- ✅ **可重复** - 实验可以重新运行验证
- ✅ **可迭代** - 基于结果优化实验设计
- ✅ **可信度标记** - 每条结论都有置信度

---

## 快速使用

```markdown
实验主题：[你的研究问题]
实验类型：benchmark/comparison/usability/hybrid
指标：[关键指标列表]
轮次：[实验轮次，默认 5]
```

**示例**：
```markdown
实验主题：Rust vs Go 并发性能
实验类型：benchmark
指标：吞吐量、延迟、内存占用
轮次：5
```

---

## 实验类型

### 1. Benchmark（性能基准测试）

**适用场景**：性能对比、资源消耗分析

**执行方式**：
- 编写基准测试代码
- 多次运行取平均
- 记录性能指标

**示例**：
```markdown
实验主题：Python asyncio vs Node.js 并发性能
实验类型：benchmark
指标：
  - 吞吐量（请求/秒）
  - 延迟（P50/P95/P99）
  - CPU 使用率
  - 内存占用
场景：
  - 单线程计算密集型
  - 多线程 I/O 密集型
  - 高并发网络请求
```

### 2. Comparison（特性对比）

**适用场景**：技术选型、功能覆盖分析

**执行方式**：
- 定义对比维度
- 收集多方信息
- 交叉验证结论

**示例**：
```markdown
实验主题：PostgreSQL vs MySQL 特性对比
实验类型：comparison
维度：
  - ACID 特性支持
  - 索引类型
  - 扩展性
  - 生态工具
验证策略：
  - 官方文档
  - 社区讨论
  - 实际案例
```

### 3. Usability（可用性测试）

**适用场景**：开发体验、学习曲线分析

**执行方式**：
- 编写示例代码
- 评估代码复杂度
- 记录开发效率

**示例**：
```markdown
实验主题：React vs Vue 开发体验
实验类型：usability
任务：
  - 实现一个 Todo List
  - 添加状态管理
  - 集成 API 调用
评估指标：
  - 代码行数
  - 概念复杂度
  - 文档质量
  - 调试难度
```

### 4. Hybrid（混合实验）

**适用场景**：综合评估（性能 + 易用性）

**执行方式**：
- 结合多种实验类型
- 多维度评分
- 加权综合结论

**示例**：
```markdown
实验主题：Claude Code vs Cursor 综合评估
实验类型：hybrid
维度：
  - 性能（响应速度、准确率）- 权重 40%
  - 易用性（学习曲线、文档）- 权重 30%
  - 生态（插件、集成）- 权重 30%
```

---

## 工作流程

```
输入研究问题
    ↓
[设计阶段] 生成实验计划
    ↓
[准备阶段] 设置实验环境
    ↓
[执行阶段] 运行实验 → 记录结果
    ↓
[验证阶段] 检查结果可信度
    ↓
[分析阶段] 生成结论报告
    ↓
[迭代阶段] 基于结果优化实验（可选）
```

### 验证循环

```python
# 伪代码
while confidence < threshold and iterations < max_iterations:
    results = run_experiment()
    confidence = validate_results(results)
    
    if confidence < threshold:
        adjust_experiment_design()
        iterations += 1
```

---

## 输出格式

### 实验计划

```markdown
# 实验计划：[主题]

## 研究问题
[明确的问题陈述]

## 假设
- 假设 1: [描述]
- 假设 2: [描述]

## 实验设计
### 指标
- 指标 1: [描述] - 测量方法
- 指标 2: [描述] - 测量方法

### 对照组
- 实验组: [描述]
- 对照组: [描述]

### 样本量
- 每组实验运行次数: N
- 预期置信度: X%

### 实验场景
1. 场景 1: [描述]
2. 场景 2: [描述]

## 验证策略
- [ ] 交叉验证（多源对比）
- [ ] 重复实验（多次运行）
- [ ] 对照实验（基线对比）
```

### 结果记录

```markdown
## 实验结果 #N

### 环境信息
- 系统: [OS]
- 硬件: [CPU/Memory]
- 时间: [timestamp]
- 工具版本: [version]

### 实验配置
- 实验类型: [type]
- 轮次: [round]
- 参数: [parameters]

### 结果数据
| 指标 | 实验组 | 对照组 | 差异 |
|------|--------|--------|------|
| 指标 1 | X | Y | +Z% |
| 指标 2 | X | Y | -Z% |

### 观察
- 观察 1: [描述]
- 观察 2: [描述]

### 异常情况
- [记录任何异常或意外结果]

### 可信度: 高/中/低
- 原因: [为什么是这个可信度]
```

### 分析报告

```markdown
# 实验研究报告：[主题]

## 执行摘要
- **核心结论**: [1-2 句话]
- **置信度**: X%（基于 Y 轮实验）
- **建议**: [行动建议]

## 研究问题
[问题陈述]

## 实验设计
[实验计划摘要]

## 结果分析

### 主要发现
#### 发现 1: [标题]
- 证据: [数据支持]
- 可信度: 高/中/低
- 来源: [实验结果链接]

#### 发现 2: [标题]
...

### 多维度分析

#### 维度 A
- 实验组: X
- 对照组: Y
- 差异: +Z%
- 结论: [描述]

#### 维度 B
...

### 综合评分
| 维度 | 实验组 | 对照组 | 权重 |
|------|--------|--------|------|
| 维度 1 | X/10 | Y/10 | W% |
| 维度 2 | X/10 | Y/10 | W% |
| **总分** | **X** | **Y** | 100% |

## 验证过程
- 交叉验证: ✅/❌
- 重复实验: ✅/❌
- 对照实验: ✅/❌
- 总置信度: X%

## 建议与限制
### 建议
- [基于证据的建议]

### 限制
- [实验局限性]
- [未覆盖场景]

## 未来改进
- [可以改进的实验设计]
- [可以增加的指标]

## 完整数据
1. [实验结果 1](link)
2. [实验结果 2](link)
```

---

## 使用场景

| 场景 | 推荐配置 | 示例 |
|------|----------|------|
| 技术选型（性能） | benchmark, 轮次 5+ | "Rust vs Go 并发性能" |
| 框架对比（功能） | comparison, 多源验证 | "React vs Vue 特性覆盖" |
| 工具评估（易用性） | usability, 示例代码 | "VSCode vs Cursor 开发体验" |
| 综合决策 | hybrid, 加权评分 | "Claude Code vs Cursor" |
| 性能优化验证 | benchmark, 前后对比 | "优化后性能提升验证" |

---

## 高级用法

### 1. 多阶段实验

```markdown
实验主题：AI 编程助手综合评估
阶段：
  1. Benchmark: 响应速度、准确率
  2. Usability: 学习曲线、文档质量
  3. Comparison: 功能覆盖、生态集成
  4. Survey: 社区反馈、用户满意度
```

### 2. A/B 测试

```markdown
实验主题：新功能用户接受度
实验类型：comparison
方法：A/B 测试
- A 组: 现有功能
- B 组: 新功能
指标: 使用率、满意度、错误率
```

### 3. 长期监控

```markdown
实验主题：系统性能退化分析
实验类型：benchmark
时间跨度：30 天
频率：每天 1 次
指标：响应时间、错误率、资源使用
```

---

## 与 deep-research 的协作

两个 skill 可以组合使用：

```markdown
# 第一阶段：信息收集（deep-research）
研究主题：Rust 并发模型
模式：quick
输出：基础理解 + 待验证问题

# 第二阶段：实验验证（experiment-research）
实验主题：Rust 并发性能验证
类型：benchmark
输入：deep-research 的待验证问题
输出：基于证据的结论
```

---

## 注意事项

1. **实验环境一致性** - 确保每次实验环境相同
2. **样本量充足** - 至少 3-5 次实验取平均
3. **记录完整** - 记录所有配置和环境信息
4. **验证可信度** - 不要只信一次实验结果
5. **诚实记录** - 记录失败和异常，不要隐瞒

---

## 触发词

- "实验对比 [A] 和 [B]"
- "性能测试 [主题]"
- "验证 [假设]"
- "A/B 测试 [功能]"
- "基准测试 [工具]"

---

## 搜索降级策略（必须遵守）

**当 `web_search` 返回错误或空结果时，必须按以下顺序尝试替代方案：**
1. `web_fetch("https://html.duckduckgo.com/html/?q=关键词")` — DuckDuckGo
2. `web_fetch("https://www.bing.com/search?q=关键词")` — Bing
3. `web_fetch` 直接抓取已知来源页面
4. 所有搜索失败则标注"⚠️ 搜索不可用，基于模型知识"

## 实现说明

此 Skill 使用：
- `exec` - 运行基准测试脚本
- `web_search` - 多源验证（失败时按降级策略处理）
- `web_fetch` - 网页抓取 + 降级搜索
- `write/read` - 记录实验结果
- LLM - 实验设计和结果分析

模板文件位于 `templates/` 目录。
脚本工具位于 `scripts/` 目录。
