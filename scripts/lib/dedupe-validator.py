#!/usr/bin/env python3
"""
通用去重验证框架
用途：为所有每日搜索归纳型任务提供去重支持
支持：每日一句、技巧、案例、项目、观点等
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

# 配置路径
WORKSPACE_ROOT = Path(__file__).parent.parent.parent
MEMORY_DIR = WORKSPACE_ROOT / "memory"
DEDUPE_DIR = MEMORY_DIR / "dedupe"

# 支持的任务类型
TASK_TYPES = {
    "english-german": {
        "db_file": "english-quotes-db.json",
        "name": "每日英语德语",
        "fields": ["quote", "author", "source"],
        "display": "每日一句"
    },
    "claude-code": {
        "db_file": "claude-code-tips-db.json",
        "name": "Claude Code 心得",
        "fields": ["tip", "category"],
        "display": "技巧"
    },
    "github-trending": {
        "db_file": "github-projects-db.json",
        "name": "GitHub Trending",
        "fields": ["repo", "language", "description"],
        "display": "项目"
    },
    "investment": {
        "db_file": "investment-wisdom-db.json",
        "name": "投资大师思想",
        "fields": ["quote", "author", "theme"],
        "display": "观点"
    },
    "startup-failures": {
        "db_file": "startup-cases-db.json",
        "name": "创业失败经验",
        "fields": ["company", "industry", "failure_reason"],
        "display": "案例"
    },
    "tech-research": {
        "db_file": "tech-topics-db.json",
        "name": "技术研究",
        "fields": ["topic", "category", "keywords"],
        "display": "主题"
    },
    "knowledge-viz": {
        "db_file": "knowledge-viz-topics-db.json",
        "name": "知识可视化研究",
        "fields": ["topic", "category", "tools"],
        "display": "主题"
    }
}


def ensure_db_dir():
    """确保数据库目录存在"""
    DEDUPE_DIR.mkdir(parents=True, exist_ok=True)


def get_db_path(task_type: str) -> Path:
    """获取任务对应的数据库文件路径"""
    if task_type not in TASK_TYPES:
        raise ValueError(f"未知任务类型: {task_type}")
    
    return DEDUPE_DIR / TASK_TYPES[task_type]["db_file"]


def load_db(task_type: str) -> dict:
    """加载任务数据库"""
    db_path = get_db_path(task_type)
    
    if not db_path.exists():
        # 创建新数据库
        db = {
            "meta": {
                "version": "1.0",
                "task_type": task_type,
                "task_name": TASK_TYPES[task_type]["name"],
                "created_at": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "total_count": 0
            },
            "items": []
        }
        save_db(task_type, db)
        return db
    
    with open(db_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_db(task_type: str, db: dict):
    """保存数据库"""
    ensure_db_dir()
    db_path = get_db_path(task_type)
    
    db["meta"]["last_updated"] = datetime.now().isoformat()
    db["meta"]["total_count"] = len(db.get("items", []))
    
    with open(db_path, 'w', encoding='utf-8') as f:
        json.dump(db, f, ensure_ascii=False, indent=2)


def normalize_text(text: str) -> str:
    """标准化文本（去空格、转小写、去标点）"""
    import re
    text = text.strip().lower()
    # 保留中英文、数字，去除其他标点
    text = re.sub(r'[^\w\u4e00-\u9fff]+', '', text)
    return text


def calculate_similarity(text1: str, text2: str) -> float:
    """计算文本相似度（简单版：基于字符重叠）"""
    if not text1 or not text2:
        return 0.0
    
    n1 = normalize_text(text1)
    n2 = normalize_text(text2)
    
    # 完全相同
    if n1 == n2:
        return 1.0
    
    # 包含关系
    if n1 in n2 or n2 in n1:
        return 0.8
    
    # 字符重叠率
    set1 = set(n1)
    set2 = set(n2)
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    
    return intersection / union if union > 0 else 0.0


def check_duplicate(task_type: str, item_data: dict, threshold: float = 0.7) -> dict:
    """
    检查是否重复
    
    参数:
    - task_type: 任务类型
    - item_data: 待检查的数据（如 {"quote": "...", "author": "..."}）
    - threshold: 相似度阈值（0-1）
    
    返回:
    {
        "is_duplicate": bool,
        "similarity": float,
        "existing_item": dict or None,
        "message": str
    }
    """
    db = load_db(task_type)
    task_config = TASK_TYPES[task_type]
    
    # 获取主要字段（第一个字段用于比较）
    primary_field = task_config["fields"][0]
    if primary_field not in item_data:
        return {
            "is_duplicate": False,
            "similarity": 0.0,
            "existing_item": None,
            "message": f"⚠️  缺少主字段 '{primary_field}'，跳过去重检查"
        }
    
    new_text = item_data[primary_field]
    max_similarity = 0.0
    most_similar_item = None
    
    for item in db.get("items", []):
        existing_text = item.get(primary_field, "")
        
        # 计算相似度
        similarity = calculate_similarity(new_text, existing_text)
        
        # 如果相似度高且其他字段也匹配，则认为重复
        if similarity >= threshold:
            # 检查次要字段
            if len(task_config["fields"]) > 1:
                secondary_field = task_config["fields"][1]
                if secondary_field in item_data and secondary_field in item:
                    sec_sim = calculate_similarity(
                        str(item_data.get(secondary_field, "")),
                        str(item.get(secondary_field, ""))
                    )
                    similarity = (similarity + sec_sim) / 2
            
            if similarity > max_similarity:
                max_similarity = similarity
                most_similar_item = item
    
    if max_similarity >= threshold and most_similar_item:
        display_name = task_config["display"]
        return {
            "is_duplicate": True,
            "similarity": max_similarity,
            "existing_item": most_similar_item,
            "message": f"❌ {display_name}已存在于 {most_similar_item.get('date', '未知日期')} (相似度: {max_similarity:.1%})"
        }
    
    return {
        "is_duplicate": False,
        "similarity": max_similarity,
        "existing_item": None,
        "message": f"✅ {task_config['display']}可以使用 (最高相似度: {max_similarity:.1%})"
    }


def add_item(task_type: str, item_data: dict, page_id: str = None, check_dup: bool = True) -> bool:
    """
    添加新项目到数据库
    
    参数:
    - task_type: 任务类型
    - item_data: 项目数据
    - page_id: Notion 页面 ID（可选）
    - check_dup: 是否检查重复（默认 True）
    
    返回:
    - True: 添加成功
    - False: 重复或失败
    """
    db = load_db(task_type)
    task_config = TASK_TYPES[task_type]
    
    # 检查重复
    if check_dup:
        result = check_duplicate(task_type, item_data)
        if result["is_duplicate"]:
            print(result["message"])
            return False
    
    # 生成 ID
    date_str = datetime.now().strftime("%Y%m%d")
    existing_ids = [i.get("id", "") for i in db["items"]]
    seq = 1
    while f"{task_type}_{date_str}_{seq:03d}" in existing_ids:
        seq += 1
    
    # 构建新项目
    new_item = {
        "id": f"{task_type}_{date_str}_{seq:03d}",
        "date": datetime.now().strftime("%Y-%m-%d"),
        **item_data
    }
    
    if page_id:
        new_item["page_id"] = page_id
    
    # 添加到数据库
    db["items"].append(new_item)
    save_db(task_type, db)
    
    print(f"✅ 已添加{task_config['display']}: {item_data.get(task_config['fields'][0], '')[:50]}...")
    return True


def batch_add(task_type: str, items: List[dict], page_id: str = None) -> dict:
    """
    批量添加项目
    
    返回:
    {
        "total": int,
        "added": int,
        "skipped": int,
        "details": list
    }
    """
    result = {
        "total": len(items),
        "added": 0,
        "skipped": 0,
        "details": []
    }
    
    for item in items:
        success = add_item(task_type, item, page_id=page_id, check_dup=True)
        if success:
            result["added"] += 1
            result["details"].append({"item": item, "status": "added"})
        else:
            result["skipped"] += 1
            result["details"].append({"item": item, "status": "skipped"})
    
    print(f"\n📊 批量添加完成:")
    print(f"  总数: {result['total']}")
    print(f"  新增: {result['added']}")
    print(f"  跳过: {result['skipped']}")
    
    return result


def list_items(task_type: str, limit: int = 20):
    """列出任务数据库中的项目"""
    db = load_db(task_type)
    task_config = TASK_TYPES[task_type]
    
    items = db.get("items", [])
    total = len(items)
    
    print(f"\n📋 {task_config['name']} - 历史记录")
    print("=" * 60)
    print(f"总数: {total}")
    
    if total == 0:
        print("暂无记录")
        return
    
    # 显示最近的项目
    recent = items[-limit:] if limit else items
    for item in reversed(recent):
        primary = item.get(task_config["fields"][0], "未知")
        date = item.get("date", "未知日期")
        print(f"  - {date}: {primary[:60]}{'...' if len(primary) > 60 else ''}")
    
    if total > limit:
        print(f"\n... 显示最近 {limit} 条，共 {total} 条")


def stats(task_type: str = None):
    """显示统计信息"""
    if task_type:
        db = load_db(task_type)
        print(f"\n📊 {TASK_TYPES[task_type]['name']}")
        print(f"  总数: {db['meta']['total_count']}")
        print(f"  最后更新: {db['meta']['last_updated']}")
    else:
        print("\n📊 所有任务统计")
        print("=" * 60)
        for tt in TASK_TYPES:
            db_path = get_db_path(tt)
            if db_path.exists():
                db = load_db(tt)
                print(f"{TASK_TYPES[tt]['name']}: {db['meta']['total_count']} 条")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="通用去重验证框架",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
支持的任务类型:
  {chr(10).join(f'  - {k}: {v["name"]}' for k, v in TASK_TYPES.items())}

示例:
  # 检查每日一句是否重复
  python dedupe-validator.py english-german check --quote "Stay hungry, stay foolish." --author "Steve Jobs"

  # 添加新技巧
  python dedupe-validator.py claude-code add --tip "使用 CLAUDE.md 定义项目上下文" --category "效率"

  # 列出历史记录
  python dedupe-validator.py github-trending list --limit 50

  # 批量添加
  python dedupe-validator.py investment batch --file items.json
        """
    )
    
    parser.add_argument("task_type", choices=TASK_TYPES.keys(), help="任务类型")
    parser.add_argument("action", choices=["check", "add", "batch", "list", "stats"], help="操作类型")
    
    # 通用字段参数
    parser.add_argument("--quote", help="每日一句/观点内容")
    parser.add_argument("--author", help="作者")
    parser.add_argument("--source", help="来源")
    parser.add_argument("--tip", help="技巧内容")
    parser.add_argument("--category", help="分类")
    parser.add_argument("--repo", help="仓库名称")
    parser.add_argument("--language", help="编程语言")
    parser.add_argument("--company", help="公司名称")
    parser.add_argument("--industry", help="行业")
    parser.add_argument("--topic", help="研究主题")
    parser.add_argument("--page-id", help="Notion 页面 ID")
    parser.add_argument("--file", help="批量导入 JSON 文件")
    parser.add_argument("--limit", type=int, default=20, help="显示数量限制")
    parser.add_argument("--threshold", type=float, default=0.7, help="相似度阈值")
    
    args = parser.parse_args()
    
    # 构建 item_data
    item_data = {}
    task_config = TASK_TYPES[args.task_type]
    
    for field in task_config["fields"]:
        if hasattr(args, field) and getattr(args, field):
            item_data[field] = getattr(args, field)
    
    # 执行操作
    if args.action == "check":
        if not item_data:
            print(f"❌ 请提供必要字段: {task_config['fields']}")
            sys.exit(1)
        
        result = check_duplicate(args.task_type, item_data, args.threshold)
        print(result["message"])
        sys.exit(1 if result["is_duplicate"] else 0)
    
    elif args.action == "add":
        if not item_data:
            print(f"❌ 请提供必要字段: {task_config['fields']}")
            sys.exit(1)
        
        success = add_item(args.task_type, item_data, args.page_id)
        sys.exit(0 if success else 1)
    
    elif args.action == "batch":
        if not args.file:
            print("❌ 批量添加需要 --file 参数")
            sys.exit(1)
        
        with open(args.file, 'r', encoding='utf-8') as f:
            items = json.load(f)
        
        result = batch_add(args.task_type, items, args.page_id)
        sys.exit(0 if result["added"] > 0 else 1)
    
    elif args.action == "list":
        list_items(args.task_type, args.limit)
    
    elif args.action == "stats":
        stats(args.task_type)


if __name__ == "__main__":
    main()
