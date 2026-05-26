#!/usr/bin/env python3
"""
心智模型用户反馈管理工具
用途：收集、查询、分析用户对心智模型的反馈
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# 配置路径
WORKSPACE_ROOT = Path(__file__).parent.parent.parent
FEEDBACK_FILE = WORKSPACE_ROOT / "memory" / "mental-models-feedback.json"
DB_FILE = WORKSPACE_ROOT / "memory" / "mental-models-db.json"


def load_feedback():
    """加载反馈数据"""
    if not FEEDBACK_FILE.exists():
        return {
            "meta": {
                "version": "1.0",
                "created": datetime.now().isoformat(),
                "total_feedback": 0
            },
            "feedback": []
        }
    
    with open(FEEDBACK_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_feedback(data):
    """保存反馈数据"""
    FEEDBACK_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(FEEDBACK_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def add_feedback(model_name: str, feedback_type: str, content: str, rating: int = None):
    """
    添加用户反馈
    
    参数:
    - model_name: 模型名称
    - feedback_type: 反馈类型 (rating/suggestion/error/request/application)
    - content: 反馈内容
    - rating: 评分 (1-5，仅当 feedback_type="rating" 时需要)
    """
    data = load_feedback()
    
    feedback_entry = {
        "id": f"fb_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "timestamp": datetime.now().isoformat(),
        "model_name": model_name,
        "type": feedback_type,
        "content": content
    }
    
    if rating is not None:
        if rating < 1 or rating > 5:
            print("❌ 评分必须在 1-5 之间")
            return False
        feedback_entry["rating"] = rating
    
    data["feedback"].append(feedback_entry)
    data["meta"]["total_feedback"] = len(data["feedback"])
    data["meta"]["last_updated"] = datetime.now().isoformat()
    
    save_feedback(data)
    print(f"✅ 反馈已记录: {model_name} - {feedback_type}")
    return True


def get_model_feedback(model_name: str):
    """获取指定模型的所有反馈"""
    data = load_feedback()
    model_feedback = [f for f in data["feedback"] if f["model_name"] == model_name]
    
    if not model_feedback:
        print(f"📭 暂无 '{model_name}' 的反馈")
        return []
    
    print(f"\n📋 {model_name} 的反馈 ({len(model_feedback)} 条)")
    print("=" * 60)
    
    for fb in model_feedback:
        print(f"\n[{fb['timestamp']}] {fb['type'].upper()}")
        if 'rating' in fb:
            print(f"评分: {'⭐' * fb['rating']} ({fb['rating']}/5)")
        print(f"内容: {fb['content']}")
    
    return model_feedback


def get_feedback_stats():
    """获取反馈统计"""
    data = load_feedback()
    
    if not data["feedback"]:
        print("\n📊 暂无反馈数据")
        return
    
    print("\n📊 心智模型反馈统计")
    print("=" * 60)
    
    # 按类型统计
    type_counts = {}
    for fb in data["feedback"]:
        fb_type = fb["type"]
        type_counts[fb_type] = type_counts.get(fb_type, 0) + 1
    
    print("\n按类型统计:")
    for fb_type, count in sorted(type_counts.items()):
        print(f"  {fb_type}: {count} 条")
    
    # 按模型统计
    model_counts = {}
    for fb in data["feedback"]:
        model = fb["model_name"]
        model_counts[model] = model_counts.get(model, 0) + 1
    
    print("\n按模型统计:")
    for model, count in sorted(model_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {model}: {count} 条")
    
    # 平均评分
    ratings = [fb["rating"] for fb in data["feedback"] if "rating" in fb]
    if ratings:
        avg_rating = sum(ratings) / len(ratings)
        print(f"\n平均评分: {avg_rating:.2f}/5 (基于 {len(ratings)} 条评分)")
    
    print(f"\n总反馈数: {data['meta']['total_feedback']} 条")


def export_feedback_report():
    """导出反馈报告到 Markdown"""
    data = load_feedback()
    
    if not data["feedback"]:
        print("📭 暂无反馈数据，无法生成报告")
        return
    
    report_lines = [
        "# 心智模型反馈报告",
        "",
        f"> 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"> 总反馈数: {data['meta']['total_feedback']} 条",
        "",
        "---",
        ""
    ]
    
    # 按模型分组
    models = {}
    for fb in data["feedback"]:
        model = fb["model_name"]
        if model not in models:
            models[model] = []
        models[model].append(fb)
    
    for model, feedbacks in sorted(models.items()):
        report_lines.append(f"## {model} ({len(feedbacks)} 条)")
        report_lines.append("")
        
        for fb in feedbacks:
            report_lines.append(f"### {fb['timestamp']}")
            if 'rating' in fb:
                report_lines.append(f"**评分**: {'⭐' * fb['rating']} ({fb['rating']}/5)")
            report_lines.append(f"**类型**: {fb['type']}")
            report_lines.append(f"**内容**: {fb['content']}")
            report_lines.append("")
        
        report_lines.append("---")
        report_lines.append("")
    
    # 保存报告
    report_path = WORKSPACE_ROOT / "memory" / f"feedback-report-{datetime.now().strftime('%Y%m%d')}.md"
    report_path.write_text("\n".join(report_lines), encoding='utf-8')
    print(f"✅ 报告已导出: {report_path}")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="心智模型用户反馈管理")
    parser.add_argument("action", choices=["add", "get", "stats", "export"], help="操作类型")
    parser.add_argument("--model", help="模型名称")
    parser.add_argument("--type", help="反馈类型 (rating/suggestion/error/request/application)")
    parser.add_argument("--content", help="反馈内容")
    parser.add_argument("--rating", type=int, help="评分 (1-5)")
    
    args = parser.parse_args()
    
    if args.action == "add":
        if not args.model or not args.type or not args.content:
            print("❌ 请提供: --model '模型名' --type '类型' --content '内容'")
            sys.exit(1)
        
        success = add_feedback(
            model_name=args.model,
            feedback_type=args.type,
            content=args.content,
            rating=args.rating
        )
        sys.exit(0 if success else 1)
    
    elif args.action == "get":
        if not args.model:
            print("❌ 请提供模型名称: --model '模型名'")
            sys.exit(1)
        get_model_feedback(args.model)
    
    elif args.action == "stats":
        get_feedback_stats()
    
    elif args.action == "export":
        export_feedback_report()


if __name__ == "__main__":
    main()
