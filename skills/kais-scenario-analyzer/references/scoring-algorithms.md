# 评分算法详解

> 各维度评分的具体计算公式和实现细节

## 叙事结构评分（20分）

### 情节点密度（8分）

```python
def plot_point_density(scenes):
    plot_points = sum(1 for s in scenes if s['plot_point_type'] != 'none')
    density = plot_points / len(scenes)
    
    if density >= 0.4: return 8
    elif density >= 0.3: return 6
    elif density >= 0.2: return 4
    elif density >= 0.1: return 2
    else: return 1
```

### 三幕式吻合度（6分）

```python
def three_act_fit(scenes):
    n = len(scenes)
    q1 = scenes[:n//4]    # 铺垫
    q2 = scenes[n//4:3*n//4]  # 冲突
    q3 = scenes[3*n//4:]  # 高潮
    
    avg_q1 = mean(s['conflict_level'] for s in q1)
    avg_q2 = mean(s['conflict_level'] for s in q2)
    avg_q3 = mean(s['conflict_level'] for s in q3)
    
    # 理想：q1低→q2高→q3最高
    score = 0
    if avg_q2 > avg_q1: score += 2
    if avg_q3 > avg_q2: score += 2
    if avg_q1 < 4: score += 1  # 铺垫不应太激烈
    if avg_q3 >= 7: score += 1  # 高潮必须够强
    
    return min(score, 6)
```

### 节奏变化（6分）

```python
def rhythm_variation(scenes):
    conflicts = [s['conflict_level'] for s in scenes]
    std_dev = stdev(conflicts)
    
    if std_dev >= 3.0: return 6
    elif std_dev >= 2.0: return 5
    elif std_dev >= 1.5: return 4
    elif std_dev >= 1.0: return 3
    else: return 1
```

## 情感弧线评分（20分）

### 情绪波动范围（7分）

```python
def emotion_range(scenes):
    all_emotions = set()
    for s in scenes:
        all_emotions.update(s.get('emotion_words', []))
    coverage = len(all_emotions) / 8  # Plutchik 8维
    
    if coverage >= 0.5: return 7
    elif coverage >= 0.375: return 5
    elif coverage >= 0.25: return 3
    else: return 1
```

### 转场频率（7分）

```python
def transition_frequency(scenes, total_seconds):
    transitions = 0
    prev_emotions = set()
    for s in scenes:
        curr = set(s.get('emotion_words', []))
        if curr != prev_emotions and curr:
            transitions += 1
        prev_emotions = curr
    
    freq = transitions / (total_seconds / 60)
    
    if freq >= 5: return 7
    elif freq >= 3: return 5
    elif freq >= 1.5: return 3
    else: return 1
```

## Hook强度评分（20分）

### 3秒Hook（10分）

```python
def hook_3sec(opening_scene):
    conflict = opening_scene['conflict_level']
    # 检查是否有悬念元素
    has_suspense = any(w in opening_scene.get('emotion_words', []) 
                       for w in ['惊讶', '恐惧', '愤怒'])
    suspense_bonus = 2 if has_suspense else 0
    
    raw = conflict * 1.0 + suspense_bonus
    return min(round(raw), 10)
```

## 完播率预测评分（20分）

### 疲劳曲线（8分）

```python
def fatigue_curve(scenes):
    """计算全剧注意力衰减"""
    attention = 1.0
    decay_streak = 0
    min_attention = 1.0
    
    for s in scenes:
        if s['conflict_level'] < 3:
            decay_streak += 1
            attention *= (1 - 0.02 * decay_streak)  # 累积衰减
        else:
            decay_streak = 0
            attention = min(attention + 0.1, 1.0)  # 冲突恢复注意力
        
        min_attention = min(min_attention, attention)
    
    # 衰减越小越好
    decay = 1 - min_attention
    if decay <= 0.15: return 8
    elif decay <= 0.25: return 6
    elif decay <= 0.35: return 4
    elif decay <= 0.50: return 2
    else: return 1
```

## 综合完播率预测

```python
def predict_completion(total_score):
    """将总分映射到完播率预测"""
    # 基于经验公式，总分与完播率大致线性相关
    base = total_score * 0.8 + 10  # 50分→50%, 100分→90%
    return min(round(base), 99)
```
