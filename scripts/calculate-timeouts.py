#!/usr/bin/env python3
"""
计算每日任务超时时间
使用公式：timeout = max(历史最大耗时, 120) × 1.1，向上取整到10秒
"""

import json
import math

# 读取历史数据
with open('/home/kai/.openclaw/workspace/memory/daily-task-timing.json', 'r', encoding='utf-8') as f:
    timing_data = json.load(f)

tasks = timing_data['tasks']
timeout_calculation = {}

# 计算每个任务的超时
for task_name, task_data in tasks.items():
    max_seconds = task_data['max_seconds']
    base_timeout = max(max_seconds, 120)
    raw_timeout = base_timeout * 1.1
    # 向上取整到10秒
    timeout = math.ceil(raw_timeout / 10) * 10
    timeout_calculation[task_name] = timeout

# 生成执行顺序
execution_order = [
    "github-review", "vibecoding", "reading-notes", "failure-lessons", 
    "tech-research", "daily-language", "daily-aigc", "daily-news",
    "claude-code-insights", "github-trending", "investment-wisdom", 
    "startup-failures", "knowledge-viz", "mental-models"
]

print("每日任务调度配置:")
print("=" * 50)
for task in execution_order:
    timeout = timeout_calculation[task]
    status = "⚠️ 历史失败" if tasks[task].get('last_failed') else "✅ 历史成功"
    print(f"{task:15} | timeout: {timeout:3}s | {status}")

print("\n" + "=" * 50)
print("即将开始执行14个每日任务...")