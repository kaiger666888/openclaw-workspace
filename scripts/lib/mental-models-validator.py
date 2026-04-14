#!/usr/bin/env python3
"""
心智模型去重验证脚本
用途：在推送新模型前，检查是否已存在历史记录中
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# 配置路径
WORKSPACE_ROOT = Path(__file__).parent.parent.parent
HISTORY_JSON = WORKSPACE_ROOT / "memory" / "mental-models-db.json"
HISTORY_MD = WORKSPACE_ROOT / "memory" / "mental-models-history.md"


def load_models_db():
    """加载心智模型 JSON 数据库"""
    if not HISTORY_JSON.exists():
        print(f"⚠️  数据库文件不存在: {HISTORY_JSON}")
        print("正在从 Markdown 文件创建数据库...")
        from pathlib import Path
        import re
        
        db = {
            "meta": {
                "version": "1.0",
                "last_updated": datetime.now().isoformat(),
                "total_count": 0
            },
            "models": []
        }
        
        # 解析 Markdown 文件
        if HISTORY_MD.exists():
            content = HISTORY_MD.read_text()
            # 匹配格式: - YYYY-MM-DD: 模型名称（类别）
            pattern = r'- (\d{4}-\d{2}-\d{2}): ([^\(]+)\(([^\)]+)\)'
            matches = re.findall(pattern, content)
            
            for date, name, category in matches:
                model = {
                    "date": date,
                    "name": name.strip(),
                    "category": category.strip(),
                    "status": "published"
                }
                db["models"].append(model)
            
            db["meta"]["total_count"] = len(db["models"])
            
            # 保存数据库
            HISTORY_JSON.parent.mkdir(parents=True, exist_ok=True)
            HISTORY_JSON.write_text(json.dumps(db, ensure_ascii=False, indent=2))
            print(f"✅ 已创建数据库，包含 {db['meta']['total_count']} 个模型")
        
        return db
    
    with open(HISTORY_JSON, 'r', encoding='utf-8') as f:
        return json.load(f)


def check_duplicate(model_name: str, db: dict) -> dict:
    """
    检查模型是否已存在
    
    返回:
    {
        "is_duplicate": bool,
        "existing_model": dict or None,
        "message": str
    }
    """
    # 标准化模型名称（去除空格、转小写）
    normalized_name = model_name.strip().lower()
    
    for model in db.get("models", []):
        existing_name = model.get("name", "").strip().lower()
        
        # 完全匹配
        if normalized_name == existing_name:
            return {
                "is_duplicate": True,
                "existing_model": model,
                "message": f"❌ 模型 '{model_name}' 已存在于 {model['date']} ({model['category']})"
            }
        
        # 部分匹配（包含关系）
        if normalized_name in existing_name or existing_name in normalized_name:
            return {
                "is_duplicate": True,
                "existing_model": model,
                "message": f"⚠️  模型 '{model_name}' 与已存在的 '{model['name']}' 相似 ({model['date']})"
            }
    
    return {
        "is_duplicate": False,
        "existing_model": None,
        "message": f"✅ 模型 '{model_name}' 可以使用"
    }


def add_model_to_db(model_name: str, category: str, page_id: str = None, sources: list = None):
    """添加新模型到数据库"""
    db = load_models_db()
    
    # 检查重复
    result = check_duplicate(model_name, db)
    if result["is_duplicate"]:
        print(result["message"])
        return False
    
    # 添加新模型
    new_model = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "name": model_name.strip(),
        "category": category.strip(),
        "status": "published"
    }
    
    if page_id:
        new_model["page_id"] = page_id
    
    if sources:
        new_model["sources"] = sources
    
    db["models"].append(new_model)
    db["meta"]["total_count"] = len(db["models"])
    db["meta"]["last_updated"] = datetime.now().isoformat()
    
    # 保存
    with open(HISTORY_JSON, 'w', encoding='utf-8') as f:
        json.dump(db, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 已添加模型: {model_name} ({category})")
    return True


def list_models_by_category(db: dict = None):
    """按类别列出所有模型"""
    if db is None:
        db = load_models_db()
    
    categories = {}
    for model in db.get("models", []):
        cat = model.get("category", "未分类")
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(model)
    
    print("\n📊 心智模型统计")
    print("=" * 50)
    for cat, models in sorted(categories.items()):
        print(f"\n{cat} ({len(models)} 个):")
        for m in models:
            print(f"  - {m['date']}: {m['name']}")
    
    print(f"\n总计: {db['meta']['total_count']} 个模型")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="心智模型去重验证工具")
    parser.add_argument("action", choices=["check", "add", "list"], help="操作类型")
    parser.add_argument("--name", help="模型名称")
    parser.add_argument("--category", help="模型类别")
    parser.add_argument("--page-id", help="Notion 页面 ID")
    parser.add_argument("--sources", nargs="+", help="来源列表")
    
    args = parser.parse_args()
    
    if args.action == "check":
        if not args.name:
            print("❌ 请提供模型名称: --name '模型名称'")
            sys.exit(1)
        
        db = load_models_db()
        result = check_duplicate(args.name, db)
        print(result["message"])
        
        if result["is_duplicate"]:
            sys.exit(1)
        else:
            sys.exit(0)
    
    elif args.action == "add":
        if not args.name or not args.category:
            print("❌ 请提供模型名称和类别: --name '模型' --category '类别'")
            sys.exit(1)
        
        success = add_model_to_db(
            model_name=args.name,
            category=args.category,
            page_id=args.page_id,
            sources=args.sources
        )
        
        sys.exit(0 if success else 1)
    
    elif args.action == "list":
        list_models_by_category()


if __name__ == "__main__":
    main()
