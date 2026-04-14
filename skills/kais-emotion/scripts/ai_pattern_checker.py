#!/usr/bin/env python3
"""AI 味检测工具 v2：多维评分 + 情感检测 + 场景感知 + 自动修复。

评分体系（总分 100）：
  - 去AI味分（0-40）：检测 AI 写作痕迹（连接词、破折号、万能句式等）
  - 人味分（0-30）：检测有人味的特征（第一人称、口语化、不完美、犹豫）
  - 情感分（0-30）：检测情感注入质量（情感波动、强度匹配、人味表达）

用法：
  python3 ai_pattern_checker.py <文件路径> [--scene SCENE] [--json] [--fix] [--diff]
  echo "文本" | python3 ai_pattern_checker.py [--scene SCENE] [--json]
  python3 ai_pattern_checker.py <文件路径> --emotion-scene comfort --emotion-intensity medium

兼容 Python 3.8+，无外部依赖。
"""

import re
import sys
import json
import random
from collections import Counter

# ============================================================
#  规则定义
# ============================================================

# 高优先级 AI 味连接词（每篇各 ≤ 1 次）
HIGH_PRIORITY_CONNECTORS = [
    "此外", "然而", "值得注意的是", "更重要的是", "总而言之",
    "综上所述", "不可否认", "毋庸置疑", "事实上", "毋庸讳言",
    "众所周知", "毋庸赘述", "诚然", "显而易见",
]

# 破折号
DASH_PATTERN = r"——"

# 否定式排比
NEGATIVE_PATTERN = r"不是[^。？\n]{1,30}，不是[^。？\n]{1,30}，而是"

# 三段式
THREE_PART_PATTERN = r"首先[^。]{2,50}其次[^。]{2,50}(?:最后|最终)[^。]{2,50}"

# 万能开头
GENERIC_OPENER = [
    "在当今快速发展的", "随着.*的发展", "在.*的背景下",
    "在这个.*的时代", "让我们", "在当今社会",
]

# 假客观
FAKE_OBJECTIVE = ["客观来说", "客观地讲", "客观来看", "理性来看", "从客观角度"]

# 过度礼貌
OVER_POLITE = ["作为一个AI", "作为一个 AI", "我只是一个语言模型", "希望对您有所帮助"]

# 宣传性用词
PROMOTIONAL = ["深刻地", "意义深远", "不可或缺", "至关重要", "具有重大意义"]

# AI 特有短语
AI_PHRASES = [
    "作为一个人工智能", "我是一个AI", "作为 AI",
    "我不能确定", "我没有个人观点", "我没有感情",
]

# 翻译腔（中国化检测）
TRANSLATION_TONE = [
    "这是一个很好的问题", "感谢你的反馈", "我理解你的感受",
    "从我的角度来看", "在这种情况下", "在一定程度上",
    "不可避免地", "基于此", "与其说", "也就是说",
    "对此", "关于这个问题", "进行了讨论", "取得了进展",
    "具有挑战性",
]

# 口语化表达（人味特征）
CASUAL_EXPRESSIONS = [
    "吧", "啊", "呢", "嘛", "哦", "嗯", "哈", "哎",
    "说实话", "其实", "反正", "说白了", "话说回来",
    "我觉得", "我感觉", "好像", "大概", "差不多",
    "有点", "挺", "蛮", "超", "巨", "贼", "绝了",
    "离谱", "上头", "种草", "踩坑", "翻车",
]

# 犹豫/不完美表达（人味特征）
HESITATION_MARKERS = [
    "可能", "也许", "大概", "不确定", "好像", "似乎",
    "说实话我也不是很确定", "这个有点复杂", "我也不太懂",
    "别问我为什么", "反正就是",
]

# 情感词汇（正面）
POSITIVE_EMOTIONS = [
    "喜欢", "开心", "高兴", "棒", "牛", "厉害", "不错", "可以",
    "赞", "好", "舒服", "满足", "欣慰", "感动", "温暖",
    "哈哈", "嘿嘿", "wow", "nice", "牛啊", "可以啊",
]

# 情感词汇（负面）
NEGATIVE_EMOTIONS = [
    "烦", "累", "难", "苦", "气", "讨厌", "无语", "崩溃",
    "郁闷", "焦虑", "担心", "害怕", "失望", "沮丧",
    "太...了", "受不了", "搞不懂", "头疼",
]

# 连续感叹号/emoji
EXCESSIVE_EXCLAIM = r"！{3,}"
EMOJI_CLUSTER = r"[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF\U00002702-\U000027B0\U0000FE00-\U0000FE0F\U0001F900-\U0001F9FF\U0001FA00-\U0001FA6F\U0001FA70-\U0001FAFF]{4,}"

# ============================================================
#  场景配置
# ============================================================

# 场景对检测标准的调整权重
SCENE_CONFIG = {
    "comfort": {
        "name": "安慰",
        "desc": "先共情再陪伴，不给鸡汤",
        # 去AI味：安慰场景更需要自然，AI味容忍度更低
        "ai_penalty_weight": 1.2,
        # 人味：第一人称和口语化更重要
        "humanity_weight": 1.3,
        # 情感：需要情感波动和温度
        "emotion_weight": 1.3,
        # 场景特有加分词
        "scene_bonus_words": ["辛苦了", "我懂", "没事", "别太往心里去", "我在"],
    },
    "debate": {
        "name": "辩论",
        "desc": "有立场，敢反驳，给论据",
        "ai_penalty_weight": 1.1,
        "humanity_weight": 1.0,
        "emotion_weight": 0.8,
        "scene_bonus_words": ["说实话", "我觉得不对", "问题是", "证据呢"],
    },
    "story": {
        "name": "故事",
        "desc": "叙事性强，允许更多修辞",
        "ai_penalty_weight": 0.8,
        "humanity_weight": 1.2,
        "emotion_weight": 1.4,
        "scene_bonus_words": [],
    },
    "daily": {
        "name": "日常",
        "desc": "随意、简洁、可以吐槽",
        "ai_penalty_weight": 1.0,
        "humanity_weight": 1.1,
        "emotion_weight": 0.9,
        "scene_bonus_words": [],
    },
    "teach": {
        "name": "教学",
        "desc": "通俗，用类比，允许不确定",
        "ai_penalty_weight": 1.0,
        "humanity_weight": 1.0,
        "emotion_weight": 0.7,
        "scene_bonus_words": ["这个有点绕", "打个比方", "简单说就是"],
    },
}

# ============================================================
#  自动修复规则
# ============================================================

FIX_RULES = [
    # (模式, 替换方案列表)
    (r"总而言之，?", ["说白了就是，", "所以，", "总之，"]),
    (r"综上所述，?", ["所以，", "总结一下，", "总之，"]),
    (r"不可否认，?", ["说实话，", "确实，", ""]),
    (r"毋庸置疑，?", ["肯定的是，", "确实，", ""]),
    (r"众所周知，?", ["大家都知道，", "都清楚，", ""]),
    (r"毋庸赘述，?", ["就不多说了，", "就不展开了，", ""]),
    (r"客观来说，?", ["说实话，", "其实，", ""]),
    (r"值得注意的是，?", ["要留意的是，", "有个细节：", "另外，"]),
    (r"更重要的是，?", ["关键是，", "更重要的是", "而且，"]),
    (r"此外，?", ["而且，", "还有就是，", "另外，"]),
    (r"然而，?", ["但是，", "不过，", "可问题是，"]),
    (r"诚然，?", ["虽然，", "确实，", ""]),
    (r"显而易见，?", ["很明显，", "看得出来，", ""]),
    (r"事实[上]?,", ["其实，", "实际上，", ""]),
    (r"在当今快速发展的", ["现在的", "当下", ""]),
    (r"深刻地", ["真的", "挺", ""]),
    (r"意义深远", ["挺重要", "有影响", ""]),
    (r"不可或缺", ["很重要", "不能少", ""]),
    (r"至关重要", ["很关键", "很重要", ""]),
    (r"这是一个很好的问题", ["问得好", "这个问题有意思", "好问题"]),
    (r"感谢你的反馈", ["谢了", "收到", "好的，知道了"]),
    (r"我理解你的感受", ["我懂", "能理解", "换我也一样"]),
    (r"从我的角度来看", ["我觉得", "在我看来", "我个人觉得"]),
    (r"具有挑战性", ["挺难的", "不简单", "有难度"]),
    (r"希望对您有所帮助", ["希望能帮到你", "希望能有用", ""]),
    (r"进行了讨论", ["聊了聊", "讨论了", "说了说"]),
    (r"取得了进展", ["有进展", "往前推了", "有成果"]),
]


# ============================================================
#  核心检测逻辑
# ============================================================

def _split_sentences(text: str) -> list:
    """将文本拆分为句子列表。"""
    parts = re.split(r"[。！？\n]+", text)
    return [s.strip() for s in parts if len(s.strip()) > 2]


def check_de_ai(text: str) -> dict:
    """去AI味检测（0-40 分）。
    
    扫描 AI 写作痕迹，基础分 40，每发现一个问题扣分。
    返回扣分明细和得分。
    """
    issues = []
    total_penalty = 0

    # 1. 破折号（超过 2 处扣 5 分/处）
    dashes = re.findall(DASH_PATTERN, text)
    dash_count = len(dashes)
    if dash_count > 2:
        penalty = (dash_count - 2) * 5
        issues.append({"type": "破折号过多", "count": dash_count, "limit": 2, "penalty": penalty})
        total_penalty += penalty

    # 2. 高优先级连接词（每个超过 1 次扣 3 分）
    for conn in HIGH_PRIORITY_CONNECTORS:
        count = len(re.findall(re.escape(conn), text))
        if count > 1:
            penalty = (count - 1) * 3
            issues.append({"type": f"连接词过多: {conn}", "count": count, "limit": 1, "penalty": penalty})
            total_penalty += penalty

    # 3. 否定式排比（超过 1 次扣 4 分）
    neg_matches = re.findall(NEGATIVE_PATTERN, text)
    if len(neg_matches) > 1:
        penalty = (len(neg_matches) - 1) * 4
        issues.append({"type": "否定式排比过多", "count": len(neg_matches), "limit": 1, "penalty": penalty})
        total_penalty += penalty

    # 4. 三段式（扣 3 分）
    three_part = re.findall(THREE_PART_PATTERN, text)
    if three_part:
        penalty = len(three_part) * 3
        issues.append({"type": "三段式论证", "count": len(three_part), "penalty": penalty})
        total_penalty += penalty

    # 5. 万能开头（扣 3 分）
    for opener in GENERIC_OPENER:
        if re.search(opener, text):
            issues.append({"type": f"万能开头: {opener[:10]}...", "penalty": 3})
            total_penalty += 3

    # 6. 假客观（扣 5 分）
    for phrase in FAKE_OBJECTIVE:
        if phrase in text:
            issues.append({"type": f"假客观: {phrase}", "penalty": 5})
            total_penalty += 5

    # 7. 宣传性用词（扣 2 分/个）
    for word in PROMOTIONAL:
        count = text.count(word)
        if count > 0:
            penalty = count * 2
            issues.append({"type": f"宣传性用词: {word}", "count": count, "penalty": penalty})
            total_penalty += penalty

    # 8. AI 身份提醒（扣 8 分）
    for phrase in OVER_POLITE + AI_PHRASES:
        if phrase in text:
            issues.append({"type": f"AI 身份提醒: {phrase}", "penalty": 8})
            total_penalty += 8

    # 9. 翻译腔（扣 2 分/个）
    for phrase in TRANSLATION_TONE:
        if phrase in text:
            issues.append({"type": f"翻译腔: {phrase}", "penalty": 2})
            total_penalty += 2

    # 10. 连续感叹号（扣 5 分）
    exclaim = re.findall(EXCESSIVE_EXCLAIM, text)
    if exclaim:
        issues.append({"type": "连续感叹号过多", "count": len(exclaim), "penalty": 5})
        total_penalty += 5

    # 11. emoji 连续（扣 3 分）
    emoji_cluster = re.findall(EMOJI_CLUSTER, text)
    if emoji_cluster:
        issues.append({"type": "emoji 连续过多", "count": len(emoji_cluster), "penalty": 3})
        total_penalty += 3

    # 12. 句子长度过于均匀（扣 3 分）
    sentences = _split_sentences(text)
    if len(sentences) >= 3:
        lengths = [len(s) for s in sentences]
        avg_len = sum(lengths) / len(lengths)
        variance = sum((l - avg_len) ** 2 for l in lengths) / len(lengths)
        std_dev = variance ** 0.5
        if std_dev < 10:
            issues.append({"type": "句子长度过于均匀", "avg": round(avg_len, 1), "std": round(std_dev, 1), "penalty": 3})
            total_penalty += 3

    score = max(0, 40 - total_penalty)
    return {"score": score, "max_score": 40, "issues": issues, "total_penalty": total_penalty}


def check_humanity(text: str) -> dict:
    """人味检测（0-30 分）。
    
    检测文本中是否具有人类写作的特征。
    基础分 0，逐项加分。
    """
    bonuses = []
    total_bonus = 0
    char_count = len(text)

    # 1. 第一人称"我"（+5 分）
    if "我" in text:
        # 频率适当加分（不是堆砌）
        i_count = text.count("我")
        if 1 <= i_count <= 10:
            bonus = 5
        elif i_count > 10:
            bonus = 3  # 太多反而有点刻意
        else:
            bonus = 0
        bonuses.append({"type": f"第一人称'我' (出现{i_count}次)", "bonus": bonus})
        total_bonus += bonus

    # 2. 口语化表达（+8 分，按比例）
    casual_count = sum(1 for expr in CASUAL_EXPRESSIONS if expr in text)
    if casual_count >= 3:
        bonus = 8
    elif casual_count >= 2:
        bonus = 6
    elif casual_count >= 1:
        bonus = 3
    else:
        bonus = 0
    bonuses.append({"type": f"口语化表达 ({casual_count}个)", "bonus": bonus})
    total_bonus += bonus

    # 3. 犹豫/不完美表达（+5 分）
    hesitation_count = sum(1 for marker in HESITATION_MARKERS if marker in text)
    if hesitation_count >= 2:
        bonus = 5
    elif hesitation_count >= 1:
        bonus = 3
    else:
        bonus = 0
    bonuses.append({"type": f"犹豫/不完美表达 ({hesitation_count}个)", "bonus": bonus})
    total_bonus += bonus

    # 4. 句子长度有变化（+5 分）
    sentences = _split_sentences(text)
    if len(sentences) >= 3:
        lengths = [len(s) for s in sentences]
        avg_len = sum(lengths) / len(lengths)
        variance = sum((l - avg_len) ** 2 for l in lengths) / len(lengths)
        std_dev = variance ** 0.5
        if std_dev >= 15:
            bonus = 5
        elif std_dev >= 10:
            bonus = 3
        else:
            bonus = 0
        bonuses.append({"type": f"句子长度变化 (标准差={std_dev:.1f})", "bonus": bonus})
        total_bonus += bonus

    # 5. 有具体数字/细节（+4 分）
    # 检测是否有阿拉伯数字或百分号
    has_numbers = bool(re.search(r'\d+', text))
    if has_numbers:
        bonuses.append({"type": "包含具体数字/细节", "bonus": 4})
        total_bonus += 4

    # 6. 短句存在（+3 分）
    short_sentences = [s for s in sentences if len(s) <= 15]
    if len(short_sentences) >= 2:
        bonuses.append({"type": f"有短句 ({len(short_sentences)}个)", "bonus": 3})
        total_bonus += 3

    score = min(30, total_bonus)
    return {"score": score, "max_score": 30, "bonuses": bonuses}


def check_emotion(text: str, scene: str = None, intensity: str = None) -> dict:
    """情感注入质量检测（0-30 分）。
    
    检测情感波动、强度匹配、情感表达自然度。
    基础分 0，逐项加分。
    """
    bonuses = []
    penalties = []
    total_bonus = 0
    total_penalty = 0

    # 1. 情感词汇存在（+8 分）
    pos_count = sum(1 for word in POSITIVE_EMOTIONS if word in text)
    neg_count = sum(1 for word in NEGATIVE_EMOTIONS if word in text)
    emotion_word_count = pos_count + neg_count
    if emotion_word_count >= 3:
        bonus = 8
    elif emotion_word_count >= 2:
        bonus = 6
    elif emotion_word_count >= 1:
        bonus = 3
    else:
        bonus = 0
    bonuses.append({"type": f"情感词汇 (正面{pos_count}+负面{neg_count}={emotion_word_count})", "bonus": bonus})
    total_bonus += bonus

    # 2. 情感波动（句子间情绪变化）（+10 分）
    sentences = _split_sentences(text)
    if len(sentences) >= 3:
        emotion_changes = 0
        prev_mood = None
        for s in sentences:
            pos = any(w in s for w in POSITIVE_EMOTIONS)
            neg = any(w in s for w in NEGATIVE_EMOTIONS)
            if pos and not neg:
                mood = "pos"
            elif neg and not pos:
                mood = "neg"
            else:
                mood = "neutral"
            if prev_mood and mood != prev_mood and mood != "neutral" and prev_mood != "neutral":
                emotion_changes += 1
            prev_mood = mood
        
        if emotion_changes >= 3:
            bonus = 10
        elif emotion_changes >= 2:
            bonus = 8
        elif emotion_changes >= 1:
            bonus = 5
        else:
            bonus = 0
        bonuses.append({"type": f"情感波动 ({emotion_changes}次变化)", "bonus": bonus})
        total_bonus += bonus
    else:
        bonuses.append({"type": "情感波动 (句子不足，无法评估)", "bonus": 0})

    # 3. 情感强度匹配（+5 分）
    # 检测感叹号数量是否适中
    exclaim_count = text.count("！") + text.count("!")
    if 1 <= exclaim_count <= 3:
        bonus = 5
    elif exclaim_count == 0:
        bonus = 2  # 没有感叹号，稍扣但不严重
    else:
        bonus = 0
        penalties.append({"type": f"感叹号过多 ({exclaim_count}个)", "penalty": 2})
        total_penalty += 2
    bonuses.append({"type": f"情感强度匹配 (感叹号{exclaim_count}个)", "bonus": bonus})
    total_bonus += bonus

    # 4. 场景加分词（+4 分）
    if scene and scene in SCENE_CONFIG:
        scene_words = SCENE_CONFIG[scene]["scene_bonus_words"]
        scene_word_count = sum(1 for w in scene_words if w in text)
        if scene_word_count >= 2:
            bonus = 4
        elif scene_word_count >= 1:
            bonus = 2
        else:
            bonus = 0
        bonuses.append({"type": f"场景匹配词 ({scene_word_count}个)", "bonus": bonus})
        total_bonus += bonus

    # 5. 不给鸡汤检测（-3 分）
    chicken_soup = [
        "一切都会好起来的", "相信自己", "加油你一定可以",
        "你是最棒的", "阳光总在风雨后", "坚持就是胜利",
    ]
    for phrase in chicken_soup:
        if phrase in text:
            penalties.append({"type": f"鸡汤表达: {phrase}", "penalty": 3})
            total_penalty += 3

    # 6. 情感真实性：检测是否"假热情"
    # 连续多个正面词+感叹号 = 假热情
    if pos_count >= 3 and exclaim_count >= 3:
        penalties.append({"type": "疑似假热情（正面词多+感叹号多）", "penalty": 3})
        total_penalty += 3

    raw_score = total_bonus - total_penalty
    score = max(0, min(30, raw_score))
    return {
        "score": score, "max_score": 30,
        "bonuses": bonuses, "penalties": penalties,
        "total_bonus": total_bonus, "total_penalty": total_penalty,
    }


def check_text(text: str, scene: str = None, intensity: str = None) -> dict:
    """综合检测：去AI味 + 人味 + 情感，返回多维评分。"""
    # 三个维度的原始分
    de_ai = check_de_ai(text)
    humanity = check_humanity(text)
    emotion = check_emotion(text, scene=scene, intensity=intensity)

    # 场景权重调整
    if scene and scene in SCENE_CONFIG:
        config = SCENE_CONFIG[scene]
        ai_weight = config["ai_penalty_weight"]
        human_weight = config["humanity_weight"]
        emo_weight = config["emotion_weight"]
    else:
        ai_weight = 1.0
        human_weight = 1.0
        emo_weight = 1.0

    # 加权分数（按比例映射到各自的满分区间）
    de_ai_score = min(40, de_ai["score"] * ai_weight)
    humanity_score = min(30, humanity["score"] * human_weight)
    emotion_score = min(30, emotion["score"] * emo_weight)

    total_score = de_ai_score + humanity_score + emotion_score

    return {
        "total_score": round(total_score, 1),
        "de_ai": {
            "label": "去AI味",
            "score": round(de_ai_score, 1),
            "max": 40,
            "weight": ai_weight,
            "issues": de_ai["issues"],
        },
        "humanity": {
            "label": "人味",
            "score": round(humanity_score, 1),
            "max": 30,
            "weight": human_weight,
            "bonuses": humanity["bonuses"],
        },
        "emotion": {
            "label": "情感",
            "score": round(emotion_score, 1),
            "max": 30,
            "weight": emo_weight,
            "bonuses": emotion["bonuses"],
            "penalties": emotion["penalties"],
        },
        "scene": scene,
        "intensity": intensity,
        "char_count": len(text),
        "line_count": len(text.split("\n")),
    }


# ============================================================
#  自动修复
# ============================================================

def fix_text(text: str) -> tuple:
    """自动修复简单 AI 味，返回 (修复后文本, 修改列表)。"""
    fixed = text
    changes = []

    for pattern, replacements in FIX_RULES:
        matches = list(re.finditer(pattern, fixed))
        for match in reversed(matches):  # 从后往前替换，避免偏移
            original = match.group()
            replacement = random.choice(replacements)
            if replacement != original:  # 确保有变化
                start, end = match.span()
                fixed = fixed[:start] + replacement + fixed[end:]
                changes.append({"original": original, "fixed": replacement})

    return fixed, changes


# ============================================================
#  输出格式化
# ============================================================

def print_report(text: str, result: dict):
    """打印人类可读的多维评分报告。"""
    total = result["total_score"]
    de_ai = result["de_ai"]
    humanity = result["humanity"]
    emotion = result["emotion"]

    # 评分等级
    if total >= 80:
        grade = "✅ 优秀"
    elif total >= 60:
        grade = "🟡 合格"
    elif total >= 40:
        grade = "🟠 需改进"
    else:
        grade = "🔴 AI味重"

    scene_info = f"  场景: {result['scene'] or '未指定'}"
    if result["intensity"]:
        scene_info += f"  强度: {result['intensity']}"

    print(f"\n{'='*55}")
    print(f"  AI 味检测报告 v2  {grade}")
    print(f"{'='*55}")
    print(f"  总分: {total}/100  |  字符: {result['char_count']}  |  行数: {result['line_count']}")
    if result["scene"]:
        print(f"  {scene_info}")
    print(f"{'='*55}")

    # 三维分数条
    print(f"\n  📊 维度评分")
    print(f"  ┌{'─'*35}┐")
    _print_bar("去AI味", de_ai["score"], de_ai["max"], de_ai["weight"])
    _print_bar("人  味", humanity["score"], humanity["max"], humanity["weight"])
    _print_bar("情  感", emotion["score"], emotion["max"], emotion["weight"])
    print(f"  ├{'─'*35}┤")
    _print_bar("总  分", total, 100, 1.0)
    print(f"  └{'─'*35}┘")

    # 去AI味问题
    if de_ai["issues"]:
        print(f"\n  🔴 去AI味问题 ({len(de_ai['issues'])}个)")
        for issue in de_ai["issues"]:
            detail = ""
            if "count" in issue:
                detail = f" (出现{issue['count']}次，扣{issue['penalty']}分)"
            elif "penalty" in issue:
                detail = f" (扣{issue['penalty']}分)"
            print(f"    • {issue['type']}{detail}")

    # 人味加分项
    if humanity["bonuses"]:
        print(f"\n  🟢 人味加分 ({len(humanity['bonuses'])}项)")
        for b in humanity["bonuses"]:
            icon = "✓" if b["bonus"] > 0 else "○"
            print(f"    {icon} {b['type']} (+{b['bonus']})")

    # 情感分析
    if emotion["bonuses"] or emotion["penalties"]:
        print(f"\n  💗 情感分析")
        for b in emotion["bonuses"]:
            print(f"    ✓ {b['type']} (+{b['bonus']})")
        for p in emotion["penalties"]:
            print(f"    ✗ {p['type']} (-{p['penalty']})")

    # 建议
    print(f"\n  {'='*55}")
    if total >= 80:
        print("  整体不错，小修即可 👍")
    elif total >= 60:
        print("  有改进空间，重点修复去AI味问题")
    else:
        print("  AI 味较重，建议大幅修改")
    print(f"{'='*55}\n")


def _print_bar(label: str, score: float, max_score: int, weight: float):
    """打印单行评分条。"""
    # 进度条
    bar_width = 20
    filled = int(bar_width * min(score, max_score) / max_score)
    bar = "█" * filled + "░" * (bar_width - filled)

    weight_str = f" ×{weight}" if weight != 1.0 else ""
    print(f"  │ {label:4s} │ {bar} {score:5.1f}/{max_score}{weight_str} │")


def print_diff(original: str, fixed: str, changes: list):
    """打印修改前后对比。"""
    print(f"\n{'='*55}")
    print(f"  📝 修改对比 ({len(changes)}处修改)")
    print(f"{'='*55}")
    for i, change in enumerate(changes, 1):
        print(f"  {i}. {change['original']}  →  {change['fixed']}")
    print(f"{'─'*55}")
    print(f"  【修改前】")
    for line in original.split("\n"):
        if line.strip():
            print(f"  - {line}")
    print(f"\n  【修改后】")
    for line in fixed.split("\n"):
        if line.strip():
            print(f"  + {line}")
    print(f"{'='*55}\n")


# ============================================================
#  CLI 入口
# ============================================================

def parse_args(argv):
    """解析命令行参数。"""
    args = {
        "file": None,
        "scene": None,
        "intensity": None,
        "json": False,
        "fix": False,
        "diff": False,
        "help": False,
    }
    i = 0
    while i < len(argv):
        arg = argv[i]
        if arg in ("--scene", "-s") and i + 1 < len(argv):
            args["scene"] = argv[i + 1]
            i += 2
        elif arg in ("--emotion-scene",) and i + 1 < len(argv):
            args["scene"] = argv[i + 1]
            i += 2
        elif arg in ("--emotion-intensity",) and i + 1 < len(argv):
            args["intensity"] = argv[i + 1]
            i += 2
        elif arg in ("--json", "-j"):
            args["json"] = True
            i += 1
        elif arg in ("--fix", "-f"):
            args["fix"] = True
            i += 1
        elif arg in ("--diff", "-d"):
            args["diff"] = True
            i += 1
        elif arg in ("--help", "-h"):
            args["help"] = True
            i += 1
        elif not arg.startswith("-"):
            args["file"] = arg
            i += 1
        else:
            i += 1
    return args


def print_help():
    """打印帮助信息。"""
    print("""AI 味检测工具 v2 — 多维评分 + 情感检测 + 场景感知

用法:
  python3 ai_pattern_checker.py <文件路径> [选项]
  echo "文本" | python3 ai_pattern_checker.py [选项]

选项:
  --scene, -s <场景>         场景类型: comfort/debate/story/daily/teach
  --emotion-scene <场景>     同 --scene
  --emotion-intensity <强度> 情感强度: light/medium/heavy
  --json, -j                 JSON 格式输出（含各维度分数）
  --fix, -f                  自动修复简单 AI 味
  --diff, -d                 显示修改前后对比（配合 --fix 使用）
  --help, -h                 显示帮助

评分体系（总分 100）:
  去AI味 (0-40)  AI写作痕迹检测
  人味   (0-30)  第一人称、口语化、犹豫、句式变化
  情感   (0-30)  情感波动、强度匹配、场景适配""")


if __name__ == "__main__":
    args = parse_args(sys.argv[1:])

    if args["help"]:
        print_help()
        sys.exit(0)

    # 验证场景参数
    if args["scene"] and args["scene"] not in SCENE_CONFIG:
        print(f"⚠️  未知场景: {args['scene']}，可选: {', '.join(SCENE_CONFIG.keys())}", file=sys.stderr)

    # 读取文本
    if args["file"]:
        with open(args["file"], "r", encoding="utf-8") as f:
            text = f.read()
    elif not sys.stdin.isatty():
        text = sys.stdin.read()
    else:
        print_help()
        sys.exit(1)

    # 检测
    result = check_text(text, scene=args["scene"], intensity=args["intensity"])

    # 输出
    if args["json"]:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print_report(text, result)

    # 自动修复
    if args["fix"]:
        fixed, changes = fix_text(text)
        if changes:
            if args["diff"]:
                print_diff(text, fixed, changes)
            else:
                print(f"\n🔧 自动修复完成，{len(changes)} 处修改")
                for c in changes:
                    print(f"  • {c['original']} → {c['fixed']}")
                print()
            # 输出修复后的文本
            if args["diff"]:
                # diff 模式已经显示了，额外输出修复后评分
                fixed_result = check_text(fixed, scene=args["scene"], intensity=args["intensity"])
                print(f"  修复前评分: {result['total_score']}/100")
                print(f"  修复后评分: {fixed_result['total_score']}/100")
            else:
                print(f"\n--- 修复后文本 ---")
                print(fixed)
        else:
            print("\n✅ 没有需要修复的 AI 味")
