---
name: kais-blender-world
version: 0.1.0
description: "3D 世界构建总调度。从分镜脚本/场景描述到最终渲染参考图的完整管线调度。触发词：3D世界, 世界构建, world build, 场景管线, 生成分镜渲染, storyboard render, 镜头渲染, 批量渲染, 渲染管线, 3D管线, 场景制作, build world, create scene"
---

# kais-blender-world — 3D 世界构建总调度

> 从分镜脚本到渲染参考图的完整管线调度。
> 编排 assets → layout（内部调用 engine）→ review 四个子 skill，一键生成所有镜头的 3D 参考图。

## 管线总览

```
输入：分镜脚本 / 场景描述列表
         ↓
┌─── kais-blender-world（本 skill）──────────────────────────────┐
│                                                               │
│  1. 解析分镜 → 提取每个镜头的需求                              │
│  2. 资产检查 → 调用 kais-blender-assets 补齐缺失资产           │
│  3. 场景规划 → 调用 kais-blender-layout 阶段一~三生成蓝图      │
│  4. 渲染执行 → 调用 kais-blender-layout 渲染（内部调用 engine）           │
│  5. 质量审查 → 调用 kais-blender-review 审查渲染结果            │
│  6. 修复循环 → 不合格则用修复参数重渲染（最多3轮）              │
│                                                               │
│ 输出：每个镜头的渲染参考图 + 审查报告                           │
└───────────────────────────────────────────────────────────────┘
         ↓
  kais-camera（视频生成）或 kais-movie-agent（后续流程）
```

## 子 Skill 清单

| Skill | 角色 | 触发方式 |
|-------|------|---------|
| **kais-blender-assets** | 资产获取与管理 | 下载缺失模型/HDRI/动画 |
| **kais-blender-layout** | 场景规划+布局渲染 | 生成蓝图 + 渲染执行 |
| **kais-blender-engine** | 底层渲染API | 动画/姿态渲染，资产管理 |
| **kais-blender-review** | 渲染质量审查 | 审查+修复建议 |

## 输入格式

### 从分镜脚本输入（主要方式）

来自 kais-movie-agent 的结构化分镜：

```json
{
  "title": "地下城遭遇战",
  "shots": [
    {
      "shot_id": "S01",
      "description": "战士推开地牢大门，火把照亮一条幽暗的走廊",
      "scene": "地牢走廊",
      "characters": [
        {"label": "战士", "animation": "walk_forward", "role": "protagonist"}
      ],
      "props": ["门", "火把", "石墙"],
      "camera": {"type": "跟随", "movement": "缓慢推进"},
      "lighting": {"scheme": "dark", "notes": "火把暖光为主光源"},
      "duration": "5s"
    },
    {
      "shot_id": "S02",
      "description": "战士停下脚步，发现前方有一条巨龙守卫着宝箱",
      "scene": "地牢大厅",
      "characters": [
        {"label": "战士", "animation": "idle_combat", "role": "protagonist"},
        {"label": "巨龙", "animation": "idle_aggressive", "role": "antagonist"}
      ],
      "props": ["宝箱", "石柱"],
      "camera": {"type": "全景→近景", "movement": "从全景推向战士表情"},
      "lighting": {"scheme": "dramatic", "notes": "龙身后有微弱的蓝色光芒"},
      "relations": [
        {"subject": "战士", "relation": "facing", "object": "巨龙", "distance": 5},
        {"subject": "巨龙", "relation": "guarding", "object": "宝箱"}
      ],
      "duration": "4s"
    }
  ]
}
```

### 从自然语言输入（简易方式）

```
一个科幻实验室场景：科学家站在实验台前，身后是巨大的全息屏幕，桌上有一个发光的烧瓶。
灯光：dramatic。需要3个机位（全景、中景、特写）。
```

---

## 执行流程

### 步骤 1：解析与规划

```python
def parse_storyboard(input_data) -> list[ShotTask]:
    """解析分镜输入，生成每个镜头的任务清单"""
    for shot in shots:
        task = ShotTask(
            shot_id=shot.shot_id,
            description=shot.description,
            characters=shot.characters,
            props=shot.props,
            camera=shot.camera,
            lighting=shot.lighting,
            relations=shot.relations,
            required_assets=extract_required_assets(shot),
            blueprint=None,       # 步骤3生成
            render_images=[],     # 步骤4填充
            review_result=None,   # 步骤5填充
        )
    return tasks
```

### 步骤 2：资产准备

对每个镜头检查所需资产，批量补齐：

```
对每个 shot:
    1. 收集所需资产清单
       - 角色: characters[].animation 对应的 FBX
       - 模型: props[] 对应的 3D 模型
       - HDRI: lighting.scheme 对应的环境光
    2. 查询本地已有资产（engine /animations + /assets API）
    3. 缺失资产 → 调用 kais-blender-assets 下载
    4. 刷新索引
```

**资产去重**：跨镜头共享同一场景时，只检查/下载一次。

**跨镜头资产映射**：

```json
{
  "warrior": {
    "character_fbx": "hero_knight.fbx",
    "animations": {
      "walk_forward": "walk_forward_inplace.fbx",
      "idle_combat": "fighting_idle.fbx"
    }
  },
  "dragon": {
    "character_fbx": "dragon_red.fbx",
    "animations": {
      "idle_aggressive": "roaring_inplace.fbx"
    }
  }
}
```

### 步骤 3：场景规划

对每个镜头生成场景蓝图（调用 kais-blender-layout 阶段一~三）：

```
对每个 shot:
    1. 场景理解 → 解析元素列表
    2. 空间推理 → 构建关系图（优先使用分镜提供的 relations）
    3. 布局求解 → 生成精确坐标
    4. 灯光/相机规划 → 匹配分镜要求
    5. 输出场景蓝图 JSON
```

**跨镜头连续性**：
- 同一角色在不同镜头中的外观保持一致（同一 FBX）
- 环境转换时标注过渡关系（如 "走廊尽头 → 大厅入口"）
- 时间线对齐：确保角色状态连续

### 步骤 4：渲染执行

对每个镜头执行渲染（调用 kais-blender-layout 渲染）：

```
对每个 shot:
    1. 将蓝图转换为 layout.render_scene() 参数
    2. 根据相机要求生成多机位渲染
    3. 通过 layout 调用 engine 提交渲染
    4. 收集渲染图片
```

**相机策略**：

| 分镜相机要求 | layout 参数映射 |
|-------------|----------------|
| 全景 | `camera_shots=["extreme_wide", "wide"]` |
| 中景 | `camera_shots=["medium"]` |
| 近景/特写 | `camera_shots=["closeup", "extreme_closeup"]` |
| 跟随 | `camera_shots=["otw_over_shoulder"]` |
| 多机位 | 组合以上选项 |

**HDRI 策略**：

| 灯光方案 | 推荐 HDRI |
|---------|-----------|
| studio | `studio_small_03_4k` |
| dramatic | `night_roads_02_4k` |
| dark | 自定义（低环境光 + 点光源） |
| warm | `kloppenheim_06_4k` |
| outdoor | `spruit_sunrise_4k` |

### 步骤 5：质量审查

对每个镜头的渲染结果执行审查（调用 kais-blender-review）：

```
对每个 shot 的每张渲染图:
    1. 图像分析 + 蓝图对比
    2. 评分判定
    3. 通过 → 交付
    4. 不通过 → 进入修复循环
```

### 步骤 6：修复循环

```
while retry_count < 3 and has_failed_shots:
    对每个不通过的 shot:
        1. 从 review 结果提取 fix_params
        2. 调整蓝图参数（位置/灯光/相机）
        3. 重新渲染
        4. 重新审查
    retry_count += 1

仍有失败 → 标记为人工审核，输出问题报告
```

---

## 输出格式

### 完整输出目录结构

```
outputs/
├── {project_name}/
│   ├── blueprints/                    # 场景蓝图
│   │   ├── S01_blueprint.json
│   │   └── S02_blueprint.json
│   ├── renders/                       # 渲染图片
│   │   ├── S01/
│   │   │   ├── S01_wide.png
│   │   │   ├── S01_medium.png
│   │   │   └── S01_closeup.png
│   │   └── S02/
│   │       ├── S02_extreme_wide.png
│   │       └── S02_closeup.png
│   ├── review_report.json             # 审查报告
│   └── production_report.json         # 总报告
```

### 总报告格式

```json
{
  "project": "地下城遭遇战",
  "total_shots": 2,
  "total_renders": 5,
  "passed": 5,
  "failed": 0,
  "retries": 0,
  "shots": [
    {
      "shot_id": "S01",
      "status": "passed",
      "renders": ["S01_wide.png", "S01_medium.png", "S01_closeup.png"],
      "best_score": 8.2
    },
    {
      "shot_id": "S02",
      "status": "passed",
      "renders": ["S02_extreme_wide.png", "S02_closeup.png"],
      "best_score": 7.8
    }
  ],
  "assets_used": {
    "characters": ["hero_knight.fbx", "dragon_red.fbx"],
    "animations": ["walk_forward.fbx", "fighting_idle.fbx", "roaring.fbx"],
    "models": ["door_01", "stone_wall_01", "treasure_chest_01"],
    "hdris": ["night_roads_02_4k"]
  }
}
```

---

## 使用方式

### 完整管线（从分镜到渲染图）

```
"帮我渲染分镜脚本的所有镜头"
→ 解析分镜 → 资产检查 → 场景规划 → 渲染 → 审查 → 交付
```

### 单镜头渲染

```
"渲染镜头 S02：战士面对巨龙，dramatic 灯光，全景+近景"
→ 跳过解析，直接进入步骤3
```

### 仅规划不渲染

```
"为这个场景生成蓝图：科学家在实验室..."
→ 只执行步骤1~3，输出蓝图 JSON，不渲染
```

### 仅审查已有渲染

```
"审查 renders/ 目录下的所有渲染图，对照分镜脚本"
→ 只执行步骤5
```

---

## 与 kais-movie-agent 的集成

world skill 最终会被 kais-movie-agent 调用：

```
kais-movie-agent
  ├── 剧本创作
  ├── 角色设计 → kais-character-designer
  ├── 分镜生成
  ├── 3D 渲染 → kais-blender-world（本 skill）← 融入点
  ├── 后期合成
  └── 视频生成 → kais-camera / kais-evolink
```

**集成接口**：

```python
# kais-movie-agent 调用 world 的标准接口
def render_storyboard_shots(storyboard: dict, output_dir: str) -> dict:
    """
    Args:
        storyboard: 分镜脚本（含 shots 数组）
        output_dir: 输出目录

    Returns:
        production_report: 总报告（含所有镜头的渲染图路径）
    """
```

---

## 性能考虑

| 策略 | 说明 |
|------|------|
| **资产去重** | 跨镜头共享资产只检查一次 |
| **并行渲染** | 无依赖的镜头可并行提交到 engine |
| **增量更新** | 已通过的镜头不重渲染 |
| **断点续传** | 记录进度，中断后可从失败镜头继续 |
| **缓存蓝图** | 同场景不同机位共用蓝图，只改相机参数 |

---

## 错误处理

| 错误类型 | 处理方式 |
|---------|---------|
| 资产下载失败 | 标记镜头为 pending，跳过继续处理其他镜头 |
| Blender 渲染超时 | 增大 timeout，降低 samples/分辨率重试 |
| 审查持续不通过 | 3轮后标记人工审核，输出详细问题报告 |
| engine 服务不可达 | 检查 health，提示用户确认 Windows 端服务状态 |

## 注意事项

- Windows 端 Blender Agent Server 必须运行（`http://<IP>:8080/health`）
- 大型项目注意渲染时间，建议先用低 samples 预览，确认构图后再高采样渲染
- Mixamo 动画需要手动下载（暂不支持自动），确保角色和动画 FBX 已就位
- 跨镜头连续性需要人工最终确认，AI 审查可覆盖大部分但非全部问题
