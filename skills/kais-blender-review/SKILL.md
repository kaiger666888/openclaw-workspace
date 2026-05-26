---
name: kais-blender-review
version: 0.1.0
description: "3D 渲染质量审查。对比渲染结果与分镜/场景蓝图，检查角色位置、朝向、比例、构图、灯光，不合格自动重渲染。触发词：渲染审查, 渲染质检, review render, 检查渲染, 渲染质量, render check, 渲染review, 合格检查, 渲染验证"
---

# kais-blender-review — 3D 渲染质量审查

> 自动审查 Blender 渲染结果，对比分镜描述/场景蓝图，判定是否合格。
> 不合格则生成修复参数，交由 layout/engine 重渲染。

## 审查流程

```
渲染图片 + 场景蓝图/分镜描述
         ↓
    阶段一：图像分析
         ↓
    阶段二：蓝图对比
         ↓
    阶段三：评分判定
         ↓
   ✅ 通过 / ❌ 不通过 + 修复建议
```

---

## 阶段一：图像分析

对渲染图片进行基础视觉检查。

### 检查项

| # | 检查项 | 方法 | 标准 |
|---|--------|------|------|
| 1 | **画面完整性** | 图像分析 | 无大面积黑色/白色区域，无渲染噪点过多 |
| 2 | **角色可见性** | 图像分析 | 角色在画面中可见且完整（无裁切） |
| 3 | **穿模检测** | 图像分析 | 角色与家具/环境无穿透重叠 |
| 4 | **光照质量** | 图像分析 | 无过曝/欠曝区域，阴影自然 |
| 5 | **构图合理性** | 图像分析 | 主体在画面合理位置，无严重偏移 |

---

## 阶段二：蓝图对比

将渲染结果与场景蓝图逐项对比。

### 对比项

| # | 对比项 | 蓝图字段 | 检查方法 |
|---|--------|---------|---------|
| 1 | **角色数量** | `characters[].label` | 画面中可见角色数 == 蓝图角色数 |
| 2 | **角色位置** | `characters[].position` | 角色相对位置与蓝图一致（左右/前后关系） |
| 3 | **角色朝向** | `characters[].rotation` | 角色面朝方向符合叙事逻辑（如 facing 关系） |
| 4 | **道具存在** | `props[].label` | 蓝图中列出的道具可见 |
| 5 | **机位匹配** | `camera.shots[].type` | 镜头类型与蓝图一致（全景/中景/近景） |
| 6 | **氛围匹配** | `lighting.scheme` | 灯光氛围与蓝图方案一致 |

### 空间关系验证

基于蓝图中的关系图，验证渲染结果：

| 关系类型 | 验证方法 |
|---------|---------|
| `facing` | 两个角色面朝方向大致相对 |
| `near` | 两个元素在画面中距离较近 |
| `opposite` | 两个元素分处画面两侧 |
| `behind` | 一个元素在另一个元素后方（透视关系） |
| `on_top` | 元素在另一个元素上方 |
| `guarding` | 守卫者面向目标，距离较近 |

---

## 阶段三：评分判定

### 评分维度（每项 0-10）

| 维度 | 权重 | 说明 |
|------|------|------|
| 画面质量 | 20% | 分辨率、噪点、过曝/欠曝 |
| 角色正确性 | 25% | 数量、位置、朝向、比例 |
| 构图匹配 | 20% | 机位类型、构图、主体位置 |
| 空间关系 | 20% | 角色间关系、角色与道具关系 |
| 氛围一致性 | 15% | 灯光、色调与蓝图匹配 |

### 判定标准

| 总分 | 判定 | 动作 |
|------|------|------|
| **≥ 7.0** | ✅ 通过 | 交付 |
| **5.0 - 6.9** | ⚠️ 勉强通过 | 标注问题，交付（如时间紧） |
| **< 5.0** | ❌ 不通过 | 生成修复参数，要求重渲染 |

---

## 审查报告格式

```json
{
  "shot_id": "shot_001",
  "image": "scene_wide.png",
  "scores": {
    "image_quality": 8,
    "character_correctness": 7,
    "composition_match": 9,
    "spatial_relations": 6,
    "atmosphere_consistency": 8
  },
  "total_score": 7.5,
  "verdict": "pass",
  "issues": [
    {
      "severity": "warning",
      "category": "spatial_relations",
      "description": "战士与龙的距离偏近，蓝图要求 distance=3m",
      "suggestion": "增大角色间距，调整战士位置 [0, -1, 0]"
    }
  ],
  "fix_params": null
}
```

### 不通过时的修复参数

```json
{
  "verdict": "fail",
  "total_score": 4.2,
  "issues": [
    {
      "severity": "critical",
      "category": "character_correctness",
      "description": "角色只有1个，蓝图要求2个（战士+龙）",
      "suggestion": "添加龙角色，position=[0, 3, 0]"
    },
    {
      "severity": "critical",
      "category": "atmosphere_consistency",
      "description": "灯光过于明亮，蓝图要求 dramatic 方案",
      "suggestion": "降低环境光，增加主光对比度"
    }
  ],
  "fix_params": {
    "characters": [
      {"animation": "...", "position": [0, 0, 0]},
      {"animation": "dragon_idle.fbx", "position": [0, 3, 0]}
    ],
    "hdri": "night_roads_02_4k",
    "lighting": "dramatic"
  }
}
```

---

## 使用方式

### 单张审查

```python
# 分析渲染图片
image("/path/to/scene_wide.png", prompt="""
审查这张 Blender 渲染图：
- 场景蓝图要求：战士在地牢中面对巨龙，中间有一个宝箱
- 空间关系：战士 facing 龙（距离3m），龙 guarding 宝箱
- 机位：全景（establishing shot）
- 灯光：dramatic

请按以下维度评分（0-10）并给出详细分析：
1. 画面质量
2. 角色正确性
3. 构图匹配
4. 空间关系
5. 氛围一致性

最后给出总分和判定（pass/warning/fail），如不通过请给出修复建议。
""")
```

### 批量审查

```bash
# 对整个镜头序列批量审查
python3 scripts/batch_review.py \
  --renders /path/to/renders/ \
  --blueprint /path/to/scene_blueprint.json \
  --output review_report.json
```

### 审查后重渲染

当审查不通过时，将 `fix_params` 传回 layout：

```python
from blender_layout import render_scene

# 使用审查建议的修复参数重新渲染
script = render_scene(
    characters=fix_params["characters"],
    hdri=fix_params["hdri"],
)
# POST to engine → 获取新渲染图 → 再次审查
```

---

## 重渲染策略

| 重试次数 | 策略 |
|---------|------|
| 第1次 | 按审查修复参数精确调整 |
| 第2次 | 放宽要求，调整相机角度 |
| 第3次 | 更换 HDRI / 灯光方案 |
| 第3次仍失败 | 标记为人工审核，记录问题 |

---

## 与其他 Skill 的协作

```
kais-blender-layout (渲染)
       ↓ 渲染图片
kais-blender-review (本skill) ← 场景蓝图
       ↓ 通过 ✅        ↓ 不通过 ❌ + fix_params
kais-camera              kais-blender-layout (重渲染)
```

**也可集成到 kais-movie-gate**，作为视频生成前的 3D 参考图质检环节。

## 注意事项

- 审查依赖图像分析能力，复杂空间关系（如 behind、between）可能判断不够精确
- 修复参数是建议性的，需要人工确认或 layout 二次验证
- 批量审查时注意 API 调用频率，避免限流
- 审查标准可根据项目需求调整权重和阈值
