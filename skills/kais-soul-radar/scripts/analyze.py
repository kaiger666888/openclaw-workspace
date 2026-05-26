#!/usr/bin/env python3
"""灵魂雷达分析脚本 - 分析指令生成器

用法:
  python3 analyze.py --stratum L1 [--topic "外卖骑手"]
  python3 analyze.py --stratum L2 L4 --topic "城市青年"
  python3 analyze.py --mode daily [--top 3]

脚本不直接调用 LLM，而是生成结构化的分析指令和搜索关键词，
由 OpenClaw agent 执行实际的 web_search 和 LLM 分析。
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Skill 根目录
SKILL_DIR = Path(__file__).resolve().parent.parent
PROMPTS_DIR = SKILL_DIR / "prompts"
SCHEMAS_DIR = SKILL_DIR / "schemas"
CACHE_DIR = SKILL_DIR / "cache"

# 六层地层配置
STRATA_CONFIG = {
    "L1": {
        "name": "制度地层",
        "description": "分析法律、政策、制度文本中的权力分配逻辑——谁被规训、谁被豁免。",
        "keywords": [
            "政策调整 个人权益 2026",
            "灵活就业 社保 缴纳",
            "平台经济 监管 政策",
            "劳动法 执行 判决",
            "户籍 改革 限制",
            "行业整顿 从业人员",
        ],
    },
    "L2": {
        "name": "技术地层",
        "description": "分析技术变革对人类劳动的位移效应——谁被替代、谁被增强。",
        "keywords": [
            "AI 替代 岗位 2026",
            "自动化 就业 冲击",
            "大模型 应用 职业影响",
            "机器人 替代 工厂",
            "技术失业 再就业",
            "AI 写作 原创版权",
        ],
    },
    "L3": {
        "name": "人口地层",
        "description": "分析人口结构变化如何重塑社会基本参数——谁在消失、谁在涌入。",
        "keywords": [
            "老龄化 养老 压力 2026",
            "生育率 下降 原因",
            "人口流动 城市 变化",
            "少子化 教育 影响",
            "养老金 缺口 数据",
        ],
    },
    "L4": {
        "name": "空间地层",
        "description": "分析居住空间的商品化进程——谁拥有空间、谁被挤出。",
        "keywords": [
            "房价 收入 比 数据",
            "城中村 拆迁 安置",
            "房租 上涨 城市",
            "县城 房地产 风险",
            "住房 保障 供给",
            "城市 挤压 年轻人",
        ],
    },
    "L5": {
        "name": "代际契约地层",
        "description": "分析不同代际之间的价值语法断裂——父辈的经验在子辈世界是否还有效。",
        "keywords": [
            "年轻人 消费观 变化",
            "养老负担 一代人",
            "代际 沟通 价值观",
            "储蓄率 年龄 变化",
            "消费降级 年轻人",
            "躺平 内卷 代际",
        ],
    },
    "L6": {
        "name": "心灵地层",
        "description": "分析人的内在世界中正在发生的结构性坍缩——什么情绪被压抑？什么意义叙事崩塌？孤独何时变成流行病？",
        "keywords": [
            "心理健康 报告 2026",
            "孤独 调查 年轻人",
            "意义感 人生 价值",
            "身份焦虑 职业认同",
            "信任度 调查 中国",
            "情绪经济 消费",
            "社交媒体 心理影响",
        ],
    },
}


def generate_kernel_id(stratum_code: str, index: int, stratified: bool = False) -> str:
    """生成故事核 ID"""
    date_str = datetime.now().strftime("%y%m%d")
    prefix = "M" if stratified else ""
    return f"sr-{date_str}-{prefix}{index:03d}"


def load_prompt_template(template_name: str) -> str:
    """加载 prompt 模板"""
    path = PROMPTS_DIR / template_name
    if not path.exists():
        print(f"⚠️ 模板文件不存在: {path}", file=sys.stderr)
        return ""
    return path.read_text(encoding="utf-8")


def build_analysis_instructions(strata: list[str], topic: str | None = None) -> dict:
    """生成分析指令"""
    date = datetime.now().strftime("%Y-%m-%d")

    if len(strata) == 1:
        # 单层分析
        code = strata[0]
        config = STRATA_CONFIG[code]
        keywords = list(config["keywords"])
        if topic:
            keywords.insert(0, f"{topic} {config['name']}")

        template = load_prompt_template("stratum-analysis.txt")

        return {
            "mode": "single",
            "stratum": code,
            "stratum_name": config["name"],
            "date": date,
            "search_keywords": keywords[:5],  # 每层最多 5 个关键词
            "prompt_template": "prompts/stratum-analysis.txt",
            "template_vars": {
                "STRATUM": code,
                "STRATUM_DESCRIPTION": config["description"],
                "DATA": "（请用 web_search 搜索上述关键词后填入搜索结果）",
            },
            "output_schema": "schemas/story_kernel.json",
            "instructions": f"""
## 分析指令：{config['name']} ({code}) 单层分析

### 1. 数据采集
使用 web_search 搜索以下关键词（每个搜索 1-3 条结果）：
{chr(10).join(f'- {kw}' for kw in keywords[:5])}

### 2. 填充模板
将搜索结果填入 prompts/stratum-analysis.txt 模板的 {{DATA}} 字段，
同时替换 {{STRATUM}} 为 {code}，{{STRATUM_DESCRIPTION}} 为：
  "{config['description']}"

### 3. 执行分析
使用填充后的 prompt 调用 LLM，要求严格按 JSON Schema 输出。

### 4. 验证输出
检查输出是否符合 schemas/story_kernel.json 的 Schema，
特别检查 macro_fissure.data_points 是否包含真实可查的数据来源。
""",
        }

    else:
        # 多层叠加分析
        strata_details = []
        for code in strata:
            config = STRATA_CONFIG[code]
            keywords = list(config["keywords"])
            if topic:
                keywords.insert(0, f"{topic} {config['name']}")
            strata_details.append({
                "code": code,
                "name": config["name"],
                "description": config["description"],
                "keywords": keywords[:3],
            })

        template = load_prompt_template("stratified-merge.txt")

        return {
            "mode": "stratified",
            "strata": strata,
            "strata_names": [STRATA_CONFIG[s]["name"] for s in strata],
            "date": date,
            "prompt_template": "prompts/stratified-merge.txt",
            "output_schema": "schemas/story_kernel.json",
            "instructions": f"""
## 分析指令：{' + '.join(strata)} 多层叠加分析

### 第一步：逐层采集与分析
对每个地层分别执行单层分析（参考上方单层分析流程）：

{chr(10).join(f"#### {d['name']} ({d['code']})" + chr(10) + chr(10).join("- " + kw for kw in d["keywords"]) for d in strata_details)}

### 第二步：叠加分析
将各层的分析结果填入 prompts/stratified-merge.txt 模板的
{{STRATUM_1_RESULT}}、{{STRATUM_2_RESULT}} 等字段。

### 第三步：执行合成
使用填充后的 prompt 调用 LLM，要求输出复合故事核。

### 第四步：验证
检查 composite_kernels 的 verifiability 字段，
确认各层数据来源均真实可查。
""",
        }


def build_daily_scan_instructions(top: int = 3) -> dict:
    """生成每日扫描指令"""
    date = datetime.now().strftime("%Y-%m-%d")
    template = load_prompt_template("daily-scan.txt")

    # 每层取 2-3 个关键词
    scan_keywords = {}
    for code, config in STRATA_CONFIG.items():
        scan_keywords[code] = config["keywords"][:3]

    return {
        "mode": "daily",
        "date": date,
        "top_n": top,
        "prompt_template": "prompts/daily-scan.txt",
        "output_schema": "schemas/story_kernel.json",
        "instructions": f"""
## 每日扫描指令 ({date})

### 1. 数据采集
对五层地层各搜索 2-3 个关键词：

{chr(10).join(f"#### {STRATA_CONFIG[c]['name']} ({c})" + chr(10) + chr(10).join("- " + kw for kw in kws) for c, kws in scan_keywords.items())}

### 2. 分析
读取 prompts/daily-scan.txt 模板，对搜索结果进行分析。
按模板中的优先级排序规则筛选 Top {top} 故事核。

### 3. 输出
格式化为精简报告推送到 Telegram。
""",
    }


def main():
    parser = argparse.ArgumentParser(description="灵魂雷达分析指令生成器")
    parser.add_argument("--stratum", nargs="+", choices=["L1", "L2", "L3", "L4", "L5", "L6"],
                        help="分析的地层（可指定多个进行叠加分析）")
    parser.add_argument("--topic", type=str, help="分析主题（可选，如'外卖骑手'、'AI替代'）")
    parser.add_argument("--mode", choices=["single", "daily"], default=None,
                        help="分析模式（single=单层/叠加，daily=每日扫描）")
    parser.add_argument("--top", type=int, default=3, help="每日扫描的 Top N 数量")
    parser.add_argument("--json", action="store_true", help="以 JSON 格式输出指令")

    args = parser.parse_args()

    if args.mode == "daily" or (not args.stratum and args.mode is None):
        result = build_daily_scan_instructions(args.top)
    elif args.stratum:
        result = build_analysis_instructions(args.stratum, args.topic)
    else:
        parser.print_help()
        sys.exit(1)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(result["instructions"])


if __name__ == "__main__":
    main()
