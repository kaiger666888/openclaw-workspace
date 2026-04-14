# Experiment Research Skill

**实验式研究助手** - 通过设计实验、执行测试、记录结果、验证假设，得出基于证据的研究结论。

## 🎯 核心特性

- **实验驱动** - 不只是信息聚合，而是通过实际验证得出结论
- **可量化结果** - 每个结论都有数据支持
- **可重复验证** - 实验可以重新运行验证
- **结构化记录** - 标准化的实验计划和结果记录
- **可信度标记** - 每条结论都有置信度评估

## 🚀 快速开始

### 1. 性能基准测试

```bash
# 创建实验
cd /home/kai/.openclaw/workspace/skills/experiment-research

# 运行基准测试
./scripts/run-benchmark.sh \
  -n "rust-vs-go-concurrency" \
  -t benchmark \
  -r 5 \
  -c "./your-benchmark-script.sh"

# 分析结果
python scripts/analyze-results.py results/rust-vs-go-concurrency-abc123
```

### 2. 特性对比研究

```markdown
# 在对话中使用
实验主题：PostgreSQL vs MySQL 特性对比
实验类型：comparison
维度：ACID 支持、索引类型、扩展性、生态
验证策略：官方文档 + 社区讨论 + 实际案例
```

### 3. 可用性测试

```markdown
# 在对话中使用
实验主题：React vs Vue 开发体验
实验类型：usability
任务：实现 Todo List、添加状态管理、集成 API
评估指标：代码行数、复杂度、文档质量
```

## 📁 目录结构

```
experiment-research/
├── SKILL.md                   # Skill 主文件
├── README.md                  # 本文件
├── templates/                 # 模板文件
│   ├── experiment-plan.md     # 实验计划模板
│   ├── result-record.md       # 结果记录模板
│   └── analysis-report.md     # 分析报告模板
├── scripts/                   # 工具脚本
│   ├── run-benchmark.sh       # 运行基准测试
│   └── analyze-results.py     # 分析结果
└── results/                   # 实验结果（自动创建）
    └── [experiment-id]/       # 每个实验一个目录
        ├── environment.json   # 环境信息
        ├── round-1.json       # 第1轮结果
        ├── round-2.json       # 第2轮结果
        ├── ...
        └── summary.json       # 汇总报告
```

## 🔬 实验类型

### Benchmark（性能基准测试）

**适用场景**：性能对比、资源消耗分析

**使用方式**：
```bash
./scripts/run-benchmark.sh \
  -n "python-vs-nodejs" \
  -t benchmark \
  -r 5 \
  -c "python benchmark.py"
```

**输出**：
- JSON 格式的原始数据
- 性能统计（平均值、中位数、标准差）
- 成功率分析

### Comparison（特性对比）

**适用场景**：技术选型、功能覆盖分析

**使用方式**：
```markdown
实验主题：React vs Vue 2026
实验类型：comparison
维度：
  - 组件系统
  - 状态管理
  - 性能优化
  - 生态工具
验证策略：
  - 官方文档
  - 社区讨论
  - 实际项目案例
```

### Usability（可用性测试）

**适用场景**：开发体验、学习曲线分析

**使用方式**：
```markdown
实验主题：Claude Code vs Cursor
实验类型：usability
任务：
  - 实现一个简单功能
  - 调试一个 bug
  - 重构一段代码
评估指标：
  - 完成时间
  - 代码质量
  - 调试效率
```

### Hybrid（混合实验）

**适用场景**：综合评估（性能 + 易用性）

**使用方式**：
```markdown
实验主题：全面评估 Rust vs Go
实验类型：hybrid
阶段：
  1. Benchmark: 性能测试
  2. Comparison: 特性对比
  3. Usability: 开发体验
综合评分:
  - 性能: 40%
  - 易用性: 30%
  - 生态: 30%
```

## 📊 使用模板

### 创建实验计划

```bash
# 复制模板
cp templates/experiment-plan.md my-experiment-plan.md

# 填写实验计划
# 参考模板中的说明填写每个部分
```

### 记录实验结果

```bash
# 复制模板
cp templates/result-record.md my-result-record.md

# 填写结果
# 参考模板中的格式记录数据和观察
```

### 生成分析报告

```bash
# 运行分析脚本
python scripts/analyze-results.py results/[experiment-id] report.md

# 或在对话中让 AI 帮你生成报告
```

## 🔄 工作流程

```
1. 定义研究问题
   ↓
2. 设计实验计划（使用 experiment-plan.md）
   ↓
3. 准备实验环境
   ↓
4. 执行实验（run-benchmark.sh 或手动）
   ↓
5. 记录结果（使用 result-record.md）
   ↓
6. 验证结果可信度
   ↓
7. 分析数据（analyze-results.py）
   ↓
8. 生成报告（使用 analysis-report.md）
   ↓
9. 基于结果迭代（可选）
```

## 💡 最佳实践

### 实验设计

1. **明确研究问题** - 问题要具体、可测量
2. **设置对照组** - 有对比才有结论
3. **多轮实验** - 至少 3-5 轮取平均
4. **记录环境** - 环境一致性很重要
5. **预设指标** - 明确什么是"好"

### 结果验证

1. **交叉验证** - 多个来源验证同一结论
2. **重复实验** - 检查结果可重复性
3. **对照实验** - 与已知基线对比
4. **异常记录** - 不要隐瞒失败和异常

### 报告撰写

1. **数据驱动** - 每个结论都要有数据支持
2. **可信度标记** - 说明结论的置信度
3. **诚实记录限制** - 承认实验局限性
4. **行动建议** - 给出基于证据的建议

## 🆚 与其他 Skill 的区别

| 特性 | deep-research | experiment-research |
|------|---------------|---------------------|
| **方法** | 信息聚合 | 实验验证 |
| **输出** | 研究报告 | 实验报告 + 数据 |
| **可信度** | 基于来源 | 基于实际测试 |
| **适用场景** | 概念理解、趋势分析 | 性能对比、技术选型 |
| **时间成本** | 快（几分钟） | 慢（几小时到几天） |

### 组合使用

```markdown
# 第一步：信息收集
使用 deep-research 了解 Rust 并发模型

# 第二步：实验验证
使用 experiment-research 验证 Rust 并发性能

# 第三步：综合决策
结合两者得出最终结论
```

## 🔗 相关资源

- **灵感来源**: [karpathy/autoresearch](https://github.com/karpathy/autoresearch)
- **deep-research skill**: `/home/kai/.openclaw/workspace/skills/deep-research/`
- **Notion 技术研究页面**: [技术研究](notion://...)

## 📝 示例

### 示例 1: Rust vs Go 并发性能

```bash
# 1. 创建实验计划
cat > /tmp/rust-go-plan.md << 'EOF'
实验主题：Rust vs Go 并发性能
实验类型：benchmark
指标：
  - 吞吐量（请求/秒）
  - 延迟（P95）
  - 内存占用
场景：
  - 计算密集型
  - I/O 密集型
  - 高并发网络
EOF

# 2. 运行实验
./scripts/run-benchmark.sh \
  -n "rust-go-concurrency" \
  -t benchmark \
  -r 5 \
  -c "./benchmarks/rust-go-bench.sh"

# 3. 分析结果
python scripts/analyze-results.py results/rust-go-concurrency-abc123

# 4. 生成报告（在对话中让 AI 帮你）
```

### 示例 2: React vs Vue 开发体验

```markdown
# 在对话中
实验主题：React vs Vue 开发体验对比
实验类型：usability
任务：
  1. 实现 Todo List
  2. 添加状态管理
  3. 集成 API
评估指标：
  - 代码行数
  - 概念复杂度（1-10）
  - 文档查找时间
  - 调试时间
轮次：3（每个任务重复 3 次）
```

## ❓ 常见问题

### Q: 什么时候用 experiment-research，什么时候用 deep-research？

**A**:
- 需要**性能数据** → experiment-research
- 需要**功能对比** → experiment-research
- 需要**快速了解** → deep-research
- 需要**趋势分析** → deep-research
- **重要决策** → 组合使用

### Q: 实验需要多少轮次？

**A**:
- 最少：3 轮（快速验证）
- 推荐：5 轮（标准测试）
- 严格：10+ 轮（学术论文级别）

### Q: 如何提高实验可信度？

**A**:
1. 多轮实验（至少 5 轮）
2. 交叉验证（多源对比）
3. 环境一致（记录所有配置）
4. 异常记录（不要隐瞒失败）
5. 开放数据（提供原始数据）

## 📄 许可证

MIT License

---

**创建时间**: 2026-03-26
**灵感来源**: karpathy/autoresearch
**作者**: Clawd (AI Assistant)
