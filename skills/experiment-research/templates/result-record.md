# 实验结果记录模板

## 基本信息
- **实验 ID**: [uuid]
- **实验主题**: [主题]
- **执行时间**: [timestamp]
- **执行轮次**: [N/M]

---

## 环境信息

### 硬件
```
CPU: [model]
Cores: [count]
Memory: [size]
Storage: [type + size]
```

### 软件
```
OS: [name + version]
Kernel: [version]
Runtime: [language + version]
Tools: [list with versions]
```

### 网络配置
```
Bandwidth: [speed]
Latency: [ms]
Packet Loss: [%]
```

---

## 实验配置

### 参数设置
```yaml
experiment_type: benchmark|comparison|usability|hybrid
group: experimental|control
scenario: [scenario_name]

parameters:
  param1: value1
  param2: value2

variables:
  - name: [var_name]
    values: [v1, v2, v3]
```

### 实验代码
```bash
# 运行命令
[command to run experiment]

# 或代码片段
[code snippet]
```

---

## 结果数据

### 定量指标

| 指标 | 实验组 | 对照组 | 差异 | 显著性 |
|------|--------|--------|------|--------|
| 指标 1 | X ± σ | Y ± σ | +Z% | p < 0.05 |
| 指标 2 | X ± σ | Y ± σ | -Z% | p < 0.01 |
| 指标 3 | X ± σ | Y ± σ | +Z% | N/A |

### 原始数据

#### 轮次 1
```json
{
  "timestamp": "2026-03-26T14:20:00Z",
  "metric1": 123.45,
  "metric2": 67.89,
  "metric3": 45.67
}
```

#### 轮次 2
```json
{
  "timestamp": "2026-03-26T14:21:00Z",
  "metric1": 124.12,
  "metric2": 68.34,
  "metric3": 46.01
}
```

#### 轮次 N
```json
{
  "timestamp": "...",
  "metric1": "...",
  "metric2": "...",
  "metric3": "..."
}
```

### 统计分析

```python
# 平均值
metric1_avg = 123.78
metric2_avg = 68.11
metric3_avg = 45.84

# 标准差
metric1_std = 0.67
metric2_std = 0.45
metric3_std = 0.34

# 中位数
metric1_median = 123.65
metric2_median = 68.20
metric3_median = 45.90

# 置信区间 (95%)
metric1_ci = [123.45, 124.11]
metric2_ci = [67.89, 68.33]
metric3_ci = [45.67, 46.01]
```

---

## 定性观察

### 正面发现
1. **发现 1**: [描述]
   - 证据: [数据/截图]
   - 影响: [高/中/低]

2. **发现 2**: [描述]
   - 证据: [数据/截图]
   - 影响: [高/中/低]

### 负面发现
1. **问题 1**: [描述]
   - 原因: [分析]
   - 影响: [高/中/低]

2. **问题 2**: [描述]
   - 原因: [分析]
   - 影响: [高/中/低]

### 意外发现
1. **意外 1**: [描述]
   - 可能原因: [推测]
   - 需要验证: [是/否]

---

## 性能数据

### 资源使用
```
CPU 峰值: [%]
内存峰值: [MB]
磁盘 I/O: [MB/s]
网络 I/O: [Mbps]
```

### 时间分解
```
总耗时: [s]
初始化: [s] ([%])
执行: [s] ([%])
清理: [s] ([%])
```

### 瓶颈分析
- **主要瓶颈**: [CPU/Memory/IO/Network]
- **次要瓶颈**: [CPU/Memory/IO/Network]

---

## 异常情况

### 错误日志
```
[timestamp] ERROR: [error message]
[timestamp] WARNING: [warning message]
```

### 异常行为
- **异常 1**: [描述]
  - 发生时间: [timestamp]
  - 持续时间: [s]
  - 影响: [描述]

### 崩溃/失败
- **是否崩溃**: 是/否
- **崩溃原因**: [if yes]
- **恢复方式**: [if yes]

---

## 可信度评估

### 评估维度

| 维度 | 状态 | 说明 |
|------|------|------|
| **数据完整性** | ✅/⚠️/❌ | [所有数据是否完整记录] |
| **环境一致性** | ✅/⚠️/❌ | [环境是否保持一致] |
| **结果可重复** | ✅/⚠️/❌ | [多次运行是否一致] |
| **无干扰因素** | ✅/⚠️/❌ | [是否有外部干扰] |

### 总体可信度
- **评级**: 高/中/低
- **原因**: [为什么是这个评级]
- **改进建议**: [如何提升可信度]

---

## 对比分析

### 与预期对比
| 指标 | 预期值 | 实际值 | 差异 |
|------|--------|--------|------|
| 指标 1 | X | Y | ±Z% |
| 指标 2 | X | Y | ±Z% |

### 与对照组对比
| 指标 | 实验组 | 对照组 | 改进 |
|------|--------|--------|------|
| 指标 1 | X | Y | +Z% |
| 指标 2 | X | Y | -Z% |

### 与历史数据对比
| 指标 | 本次 | 上次 | 变化 |
|------|------|------|------|
| 指标 1 | X | Y | ±Z% |

---

## 截图/图表

### 性能曲线
```
[插入性能曲线图]
```

### 资源使用
```
[插入资源使用图]
```

### 对比图表
```
[插入对比柱状图/折线图]
```

---

## 原始文件

### 日志文件
- 完整日志: `[path/to/log]`
- 错误日志: `[path/to/error.log]`

### 数据文件
- 原始数据: `[path/to/raw_data.json]`
- 处理数据: `[path/to/processed_data.csv]`

### 配置文件
- 实验配置: `[path/to/config.yaml]`
- 环境配置: `[path/to/env.sh]`

---

## 后续行动

### 需要重测
- [ ] [指标/场景] - 原因: [why]

### 需要调整
- [ ] [参数] - 从 X 调整到 Y

### 需要新增
- [ ] [新指标/新场景] - 原因: [why]

---

## 备注
[任何其他重要信息]

---

## 记录信息
- **记录人**: [name]
- **记录时间**: [timestamp]
- **审核状态**: [pending/approved/rejected]
- **审核人**: [name] - [timestamp]
