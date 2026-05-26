#!/usr/bin/env python3
"""
kais-soul-radar prompt eval script
Uses LLM to score a Story Kernel output on 5 dimensions (total 100).
Test data is cached to ensure fair comparison across experiments.
"""
import json
import sys
import os
import subprocess
import hashlib
import time

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EVAL_DIR = os.path.dirname(os.path.abspath(__file__))
TEST_DATA_PATH = os.path.join(EVAL_DIR, "test-data.json")
PROMPT_DIR = os.path.join(SKILL_DIR, "prompts")
SCHEMA_PATH = os.path.join(SKILL_DIR, "schemas", "story_kernel.json")

# Default test data: real search results from 2026-05-06
DEFAULT_TEST_DATA = {
    "l1_data": [
        "2.8亿灵活就业者中77%因户籍限制无法在就业地正常参保",
        "职工养老保险断缴名单新增4200万条，灵活就业群体断缴率38%",
        "每3位灵活就业年轻人中就有1人暂停缴纳社保",
        "国务院2025年12月发布灵活就业人员社保缴费新规",
        "2026年灵活就业人员社保缴费迎来3个重要新调整"
    ],
    "l2_data": [
        "23万大厂员工被AI替代，Gartner预测到2027年一半因AI裁员的公司会重新招人",
        "中国约7030万岗位面临AI直接替代风险，1.57亿岗位面临收缩",
        "2026开年7万科技人失业，第一波AI裁员潮已来",
        "MIT 2025数据：95%给AI砸钱的企业还没赚到钱",
        "花旗2026报告：中国大规模裁员几乎未在主流企业出现，但岗位重构加速"
    ],
    "l5_data": [
        "2025年轻人断层式理性消费，兴趣消费占57.1%，虚拟充值30.5%",
        "宠物经济2024年超越母婴经济，宠物数量首次超过4岁以下婴幼儿",
        "代际消费分层：70后发展型→千禧体验型→Z世代数字确权型",
        "物尽其用成为年轻人新生活哲学，从家庭代际记忆自然延伸",
        "18-22岁热衷虚拟消费，23-28岁展现断层式理性，29-35岁家庭CEO思维"
    ]
}

def ensure_test_data():
    """Load or create test data cache."""
    if os.path.exists(TEST_DATA_PATH):
        with open(TEST_DATA_PATH) as f:
            return json.load(f)
    with open(TEST_DATA_PATH, 'w') as f:
        json.dump(DEFAULT_TEST_DATA, f, ensure_ascii=False, indent=2)
    return DEFAULT_TEST_DATA

def read_prompt(prompt_file):
    """Read a prompt template."""
    path = os.path.join(PROMPT_DIR, prompt_file)
    if not os.path.exists(path):
        return None
    with open(path) as f:
        return f.read()

def build_analysis_prompt():
    """Build the full analysis prompt from templates and test data."""
    data = ensure_test_data()
    
    stratum_prompt = read_prompt("stratum-analysis.txt")
    if not stratum_prompt:
        print("ERROR: prompts/stratum-analysis.txt not found")
        return None
    
    # Build input data section
    input_data = f"""## 实际数据（2026-05-06 采集）

### L1 制度地层数据
{chr(10).join('- ' + d for d in data['l1_data'])}

### L2 技术地层数据
{chr(10).join('- ' + d for d in data['l2_data'])}

### L5 代际契约地层数据
{chr(10).join('- ' + d for d in data['l5_data'])}
"""
    
    # Replace placeholders
    prompt = stratum_prompt
    prompt = prompt.replace("{STRATUM}", "L1+L2+L5")
    prompt = prompt.replace("{STRATUM_DESCRIPTION}", "制度地层(L1): 法律政策中的权力语法; 技术地层(L2): AI替代与岗位位移; 代际契约地层(L5): 代际消费观念与生存策略冲突")
    prompt = prompt.replace("{DATA}", input_data)
    
    # Add evaluation instruction
    prompt += """

# 重要：这是评估模式
请严格按照 JSON Schema 输出一个完整的分析结果（kernels 数组中至少包含 1 个故事核）。
这是用于评估 prompt 质量的标准测试，请认真分析。
"""
    
    return prompt

def run_eval():
    """Main eval: build prompt, print it for agent to execute, parse score."""
    prompt = build_analysis_prompt()
    if not prompt:
        print("EVAL_SCORE: 0")
        return
    
    # Print the prompt for the OpenClaw agent to execute
    print("=" * 60)
    print("ANALYSIS_PROMPT_START")
    print("=" * 60)
    print(prompt)
    print("=" * 60)
    print("ANALYSIS_PROMPT_END")
    print("=" * 60)
    print()
    print("INSTRUCTIONS:")
    print("1. Execute the above prompt through LLM")
    print("2. Feed the JSON output to the eval rubric below")
    print("3. Score on 5 dimensions and print EVAL_SCORE: <total>")
    print()
    
    eval_rubric = """
# EVAL RUBRIC (score 0-100)

After getting the Story Kernel JSON output, score it:

## 1. 结构性公式深度 (25分)
- 20-25: 公式真正捕捉到"结构力量迫使个人走向必然结局"，不是个人叙事
- 15-19: 有结构性视角但不够深入，或偏向个人归因
- 10-14: 表面描述，缺乏结构性分析
- 0-9: 纯个人叙事，无结构性视角

## 2. 叙事角度质量 (25分)
- 20-25: 角度新颖、驱动性强、每个角度都能展开一个完整故事，避免套路
- 15-19: 有一定新意但部分角度偏常见
- 10-14: 角度较套路（逆袭、和解、成长等）
- 0-9: 角度空洞或不可操作

## 3. 微观裂隙真实感 (20分)
- 16-20: 人物具体可信、场景有画面感、冲突有日常质感
- 12-15: 人物和场景基本可信但缺乏细节
- 8-11: 过于抽象或过于戏剧化
- 0-7: 不可信或空洞

## 4. 数据可验证性 (15分)
- 13-15: 数据引用具体、来源可查、与输入数据一致
- 10-12: 有数据引用但不够具体
- 5-9: 数据模糊或可能编造
- 0-4: 无数据引用或明显编造

## 5. 代际语法冲突 (15分, L5分析时评分)
- 13-15: 冲突有洞察力、避免刻板印象、不可翻译核心词精准
- 10-12: 有冲突但略显表面
- 5-9: 刻板印象明显
- 0-4: 无冲突或与L5无关

Output format: EVAL_SCORE: <total>/100
"""
    print(eval_rubric)

if __name__ == "__main__":
    if "--baseline" in sys.argv:
        print("Running baseline eval...")
    run_eval()
