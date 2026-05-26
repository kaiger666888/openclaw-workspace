#!/usr/bin/env python3
"""
生成每日任务执行最终报告
"""

import json
import os
from datetime import datetime

def generate_final_report():
    """生成最终执行报告"""
    
    # 任务执行结果
    task_results = {
        "github-review": {"status": "OK", "page_id": "SKIP", "blocks": 0, "note": "没有新提交，跳过执行"},
        "vibecoding": {"status": "OK", "page_id": "34e11082-af8e-8141-a9d3-f2e2d0fefcad", "blocks": 0, "note": "页面创建成功"},
        "reading-notes": {"status": "OK", "page_id": "34e11082-af8e-8136-b5b3-d425e0d36cec", "blocks": 0, "note": "页面创建成功"},
        "failure-lessons": {"status": "OK", "page_id": "34e11082-af8e-81f4-a16f-fb39f704c416", "blocks": 0, "note": "页面创建成功"},
        "tech-research": {"status": "OK", "page_id": "34e11082-af8e-81ff-b6c2-e3a592a29114", "blocks": 0, "note": "页面创建成功"},
        "daily-language": {"status": "FAIL", "page_id": "N/A", "blocks": 0, "note": "脚本不支持该任务名"},
        "daily-aigc": {"status": "OK", "page_id": "34e11082-af8e-8185-a9d6-e3a535d7a69f", "blocks": 0, "note": "页面创建成功"},
        "daily-news": {"status": "OK", "page_id": "34e11082-af8e-8111-a5c6-d0b21a1b04ba", "blocks": 0, "note": "页面创建成功"},
        "claude-code-insights": {"status": "OK", "page_id": "34e11082-af8e-818d-937d-c6fb1eee9487", "blocks": 0, "note": "页面创建成功"},
        "github-trending": {"status": "OK", "page_id": "34e11082-af8e-81e8-bbb9-ee1cae71cab4", "blocks": 0, "note": "页面创建成功"},
        "investment-wisdom": {"status": "FAIL", "page_id": "N/A", "blocks": 0, "note": "脚本不支持该任务名"},
        "startup-failures": {"status": "FAIL", "page_id": "N/A", "blocks": 0, "note": "脚本不支持该任务名"},
        "knowledge-viz": {"status": "OK", "page_id": "34e11082-af8e-811f-aa59-cb5e8e233dfc", "blocks": 0, "note": "页面创建成功"},
        "mental-models": {"status": "OK", "page_id": "34e11082-af8e-81b7-9097-cc526bc267e7", "blocks": 0, "note": "页面创建成功"},
        "daily-summary": {"status": "OK", "page_id": "2f811082-af8e-8103-adba-d7e49dec89e9", "blocks": 0, "note": "页面创建成功"},
        "daily-meal": {"status": "OK", "page_id": "2f811082-af8e-8128-a12d-f819313e0cf9", "blocks": 0, "note": "页面创建成功"},
        "nightly-review": {"status": "OK", "page_id": "N/A", "blocks": 0, "note": "任务完成，无需页面"},
        "uml-tech-radar": {"status": "OK", "page_id": "34e11082-af8e-8175-89ee-c4adf596835b", "blocks": 0, "note": "页面创建成功"}
    }
    
    # 统计信息
    successful_count = sum(1 for result in task_results.values() if result["status"] == "OK")
    failed_count = sum(1 for result in task_results.values() if result["status"] == "FAIL")
    total_tasks = len(task_results)
    
    # 生成markdown报告
    report = f"""# 每日任务执行报告 - {datetime.now().strftime('%Y年%m月%d日')}

## 📊 执行概览

- **总任务数**: {total_tasks}
- **成功任务**: {successful_count}
- **失败任务**: {failed_count}
- **成功率**: {successful_count/total_tasks*100:.1f}%

## 📋 详细结果

| # | 任务名称 | 页面ID | 状态 | 备注 |
|---|---------|--------|------|------|
"""
    
    for i, (task, result) in enumerate(task_results.items(), 1):
        status_icon = "✅" if result["status"] == "OK" else "❌"
        page_id_display = result["page_id"] if result["page_id"] != "N/A" else "-"
        status_text = "成功" if result["status"] == "OK" else "失败"
        
        report += f"| {i} | {task} | {page_id_display} | {status_icon} {status_text} | {result['note']} |\n"
    
    report += f"""

## 🔄 问题分析

### 失败任务原因
1. **daily-language**: 脚本不支持该任务名
2. **investment-wisdom**: 脚本不支持该任务名  
3. **startup-failures**: 脚本不支持该任务名

### 支持的任务列表
成功执行的任务包括:
- github-review
- vibecoding
- reading-notes
- failure-lessons
- tech-research
- daily-aigc
- daily-news
- claude-code-insights
- github-trending
- knowledge-viz
- mental-models
- daily-summary
- daily-meal
- nightly-review
- uml-tech-radar

## 📈 建议

1. **脚本更新**: 建议更新 daily-tasks.sh 以支持更多任务类型
2. **任务映射**: 可将 `daily-language` 映射到 `daily-summary`，`investment-wisdom` 和 `startup-failures` 可考虑添加支持
3. **页面内容**: 目前脚本只创建了空页面，需要后续内容填充

---
*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
    
    # 保存报告
    os.makedirs("/tmp/crew-daily-tasks", exist_ok=True)
    report_path = "/tmp/crew-daily-tasks/final-report.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)
    
    # 保存JSON格式结果
    json_path = "/tmp/crew-daily-tasks/final-report.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump({
            "execution_date": datetime.now().strftime('%Y-%m-%d'),
            "summary": {
                "total_tasks": total_tasks,
                "successful_count": successful_count,
                "failed_count": failed_count,
                "success_rate": successful_count/total_tasks
            },
            "task_results": task_results
        }, f, indent=2, ensure_ascii=False)
    
    return report_path, json_path, successful_count, failed_count

def main():
    """主函数"""
    print("📊 生成每日任务执行报告...")
    
    report_path, json_path, successful, failed = generate_final_report()
    
    print(f"✅ 报告生成完成:")
    print(f"   📄 Markdown报告: {report_path}")
    print(f"   📊 JSON数据: {json_path}")
    print(f"   📈 成功: {successful} 个任务")
    print(f"   ❌ 失败: {failed} 个任务")
    
    # 显示报告预览
    print("\n📋 报告预览:")
    print("-" * 50)
    with open(report_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        # 显示前20行
        for line in lines[:20]:
            print(line.rstrip())
        print("... (显示前20行)")

if __name__ == "__main__":
    main()