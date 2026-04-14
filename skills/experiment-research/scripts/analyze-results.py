#!/usr/bin/env python3
"""
实验结果分析脚本
分析实验结果并生成统计报告
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import statistics


def load_experiment_results(experiment_dir: str) -> Dict[str, Any]:
    """加载实验结果"""
    exp_path = Path(experiment_dir)

    if not exp_path.exists():
        print(f"错误: 实验目录不存在: {experiment_dir}")
        sys.exit(1)

    summary_file = exp_path / "summary.json"
    if not summary_file.exists():
        print(f"错误: 找不到汇总文件: {summary_file}")
        sys.exit(1)

    with open(summary_file, 'r') as f:
        return json.load(f)


def analyze_performance(results: List[Dict]) -> Dict[str, float]:
    """分析性能数据"""
    durations = [r['duration_seconds'] for r in results]

    if not durations:
        return {}

    stats = {
        'count': len(durations),
        'mean': statistics.mean(durations),
        'median': statistics.median(durations),
        'min': min(durations),
        'max': max(durations),
        'range': max(durations) - min(durations),
    }

    if len(durations) > 1:
        stats['std_dev'] = statistics.stdev(durations)
        stats['variance'] = statistics.variance(durations)
    else:
        stats['std_dev'] = 0.0
        stats['variance'] = 0.0

    return stats


def analyze_success_rate(results: List[Dict]) -> Dict[str, Any]:
    """分析成功率"""
    total = len(results)
    success = sum(1 for r in results if r['exit_code'] == 0)
    failed = total - success

    return {
        'total': total,
        'success': success,
        'failed': failed,
        'success_rate': (success / total * 100) if total > 0 else 0.0
    }


def generate_report(experiment: Dict, perf_stats: Dict, success_stats: Dict) -> str:
    """生成分析报告"""
    report = f"""# 实验结果分析报告

## 基本信息
- **实验名称**: {experiment['experiment_name']}
- **实验类型**: {experiment['experiment_type']}
- **实验 ID**: {experiment['experiment_id']}
- **执行时间**: {experiment['timestamp']}
- **总轮次**: {experiment['total_rounds']}

## 性能统计

### 执行时间
| 指标 | 值 |
|------|-----|
| 平均时间 | {perf_stats['mean']:.3f}s |
| 中位数 | {perf_stats['median']:.3f}s |
| 最小时间 | {perf_stats['min']:.3f}s |
| 最大时间 | {perf_stats['max']:.3f}s |
| 时间范围 | {perf_stats['range']:.3f}s |
| 标准差 | {perf_stats['std_dev']:.3f}s |

### 执行成功率
| 指标 | 值 |
|------|-----|
| 总轮次 | {success_stats['total']} |
| 成功轮次 | {success_stats['success']} |
| 失败轮次 | {success_stats['failed']} |
| 成功率 | {success_stats['success_rate']:.1f}% |

## 详细结果

"""

    # 添加每轮结果
    for i, result in enumerate(experiment['results'], 1):
        status = "✅ 成功" if result['exit_code'] == 0 else "❌ 失败"
        report += f"""### 第 {i} 轮
- **状态**: {status}
- **耗时**: {result['duration_seconds']:.3f}s
- **开始时间**: {result['start_time']}
- **结束时间**: {result['end_time']}

"""

    return report


def save_report(report: str, output_path: str):
    """保存报告"""
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w') as f:
        f.write(report)

    print(f"报告已保存到: {output_file}")


def main():
    if len(sys.argv) < 2:
        print("用法: python analyze-results.py <experiment_dir> [output_file]")
        print("\n示例:")
        print("  python analyze-results.py results/rust-vs-go-abc123")
        print("  python analyze-results.py results/rust-vs-go-abc123 analysis.md")
        sys.exit(1)

    experiment_dir = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    # 加载实验结果
    print(f"加载实验结果: {experiment_dir}")
    experiment = load_experiment_results(experiment_dir)

    # 分析性能
    print("分析性能数据...")
    perf_stats = analyze_performance(experiment['results'])

    # 分析成功率
    print("分析成功率...")
    success_stats = analyze_success_rate(experiment['results'])

    # 生成报告
    print("生成分析报告...")
    report = generate_report(experiment, perf_stats, success_stats)

    # 保存或输出
    if output_file:
        save_report(report, output_file)
    else:
        print("\n" + "="*60)
        print(report)


if __name__ == "__main__":
    main()
