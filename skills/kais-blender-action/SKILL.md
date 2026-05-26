---
name: kais-blender-action
version: 0.1.0
description: "Mixamo 动作镜头录制器。精确控制镜头角度、时长（ms级）录制 Mixamo 动画，输出快速预览视频供 kais-jimeng 图生视频参考。触发词：录制动作, action record, 动作预览, 录制动画, capture action, 动作参考视频, action preview, mixamo录制, 镜头录制, record animation, 动作视频, capture motion, 录制镜头, 动作参考"
---

# kais-blender-action — Mixamo 动作镜头录制器

> 精确控制镜头角度和时长，从 Mixamo 动画中截取/录制指定片段，
> 输出快速预览视频，供 kais-jimeng 图生视频作为动作参考。

## 前置依赖

- Windows 端已启动 Blender Agent Server（默认 `http://<IP>:8080`）
- kais-blender-engine skill 已就绪（本 skill 依赖其 client 库）
- 角色 FBX 和动画 FBX 已放入 `D:\BlenderAgent\animations\`

## 快速使用

```python
import sys
sys.path.insert(0, "/home/kai/.openclaw/workspace/skills/kais-blender-action/client")
from action_recorder import ActionRecorder

rec = ActionRecorder("http://192.168.71.38:8080")

# 录制一个动作片段
result = rec.record(
    character="hero.fbx",
    motion="walk.fbx",
    duration_ms=2000,       # 录制 2 秒
    start_ms=500,           # 从动画第 500ms 开始
    camera={
        "azimuth": 45,      # 水平旋转角度（度）
        "elevation": 15,    # 俯仰角度（度）
        "distance": 3.0,    # 到角色距离（米）
        "target_height": 0.9, # 注视点高度（米）
    },
    output_name="walk_ref_001",
)

print("状态:", result["status"])
print("视频:", result.get("video_path"))
```

## 镜头参数（CameraParams）

所有参数均可自由指定，精确控制相机位置和朝向。

| 参数 | 类型 | 默认值 | 范围 | 说明 |
|------|------|--------|------|------|
| `azimuth` | float | 0 | -180 ~ 180 | 水平旋转角度。0=正前方，90=左侧，-90=右侧，180=正后方 |
| `elevation` | float | 0 | -90 ~ 90 | 俯仰角度。0=平视，正=俯视，负=仰视 |
| `distance` | float | 3.0 | 0.5 ~ 20.0 | 相机到角色的距离（米） |
| `target_height` | float | 0.9 | 0 ~ 2.5 | 相机注视点高度（米）。角色约1.8m高，0.9=腰部，1.4=肩膀，1.7=头顶 |
| `fov` | float | 50 | 10 ~ 120 | 视场角（度）。小=长焦（压缩），大=广角（拉伸） |
| `lens_shift_x` | float | 0 | -1 ~ 1 | 水平镜头偏移。-1=左偏，1=右偏 |
| `lens_shift_y` | float | 0 | -1 ~ 1 | 垂直镜头偏移。-1=下偏，1=上偏 |
| `roll` | float | 0 | -180 ~ 180 | 相机绕视线轴旋转（荷兰角） |
| `orthographic` | bool | False | - | 正交投影模式（无透视变形，适合参考图） |

### 常用镜头预设

为方便使用，提供常用预设（可在此基础上微调）：

| 预设名 | azimuth | elevation | distance | fov | 效果 |
|--------|---------|-----------|----------|-----|------|
| `front_waist` | 0 | 0 | 3.0 | 50 | 正面平视腰部 |
| `front_chest` | 0 | 10 | 2.5 | 45 | 正面微俯视胸部 |
| `front_full` | 0 | 0 | 4.0 | 50 | 正面全身 |
| `side_waist` | 90 | 0 | 3.0 | 50 | 侧面平视腰部 |
| `three_quarter` | 45 | 10 | 3.0 | 50 | 四分之三经典角度 |
| `dutch_left` | 30 | 5 | 2.5 | 45 | 荷兰角（左倾） |
| `over_shoulder` | 160 | 10 | 2.0 | 60 | 过肩镜头 |
| `low_angle` | 0 | -15 | 2.5 | 45 | 低角度仰拍 |
| `high_angle` | 0 | 25 | 3.5 | 50 | 高角度俯拍 |
| `top_down` | 0 | 80 | 3.0 | 35 | 大俯视 |
| `close_up_face` | 0 | 5 | 1.2 | 35 | 面部特写 |
| `wide_shot` | 0 | 5 | 6.0 | 60 | 远景全身+环境 |

```python
# 使用预设
camera = rec.get_camera_preset("three_quarter")
# 微调
camera["distance"] = 2.5

result = rec.record(
    character="hero.fbx",
    motion="walk.fbx",
    duration_ms=1500,
    camera=camera,
    output_name="walk_3q_ref",
)
```

## 时间参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `start_ms` | int | 0 | 动画起始时间（毫秒）。精确到帧：实际帧 = round(start_ms * fps / 1000) |
| `duration_ms` | int | 必填 | 录制时长（毫秒）。精确到帧：实际帧数 = round(duration_ms * fps / 1000) + 1 |
| `fps` | int | 24 | 帧率。影响时间精度：24fps→~42ms/帧，30fps→~33ms/帧，60fps→~17ms/帧 |

**时间精度说明：**
- Blender 以帧为单位，毫秒会被换算为最近帧
- 24fps 时最小精度 ≈ 42ms，30fps ≈ 33ms，60fps ≈ 17ms
- 如需亚帧精度，可用 `fps=60`
- 换算公式：`frame = round(ms * fps / 1000)`

```python
# 精确截取第 1.2 秒到第 2.8 秒的片段
result = rec.record(
    character="hero.fbx",
    motion="run.fbx",
    start_ms=1200,
    duration_ms=1600,   # 1.2s → 2.8s
    fps=60,             # 高帧率提高时间精度
    camera=rec.get_camera_preset("front_waist"),
    output_name="run_mid_ref",
)
```

## 渲染参数（RenderParams）

快速预览模式，优先速度而非画质。

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `resolution` | int | 512 | 渲染分辨率。512=快速预览，1024=清晰参考 |
| `samples` | int | 32 | Cycles 采样数。32=最快，128=较清晰 |
| `engine` | str | `"eevee"` | 渲染引擎。`eevee`=极速，`cycles`=高质量 |
| `transparent_bg` | bool | True | 透明背景（方便 jimeng 合成） |
| `format` | str | `"mp4"` | 输出格式。`mp4` / `frames` |
| `lighting` | str | `"studio"` | 灯光预设。`studio` / `dramatic` / `soft` / `flat` |
| `output_dir` | str | `"outputs/actions/"` | 输出目录（Windows 端路径） |

**渲染速度参考（RTX 3060 Ti）：**
- Eevee 512p 32smp: ~1-2s/帧 → 24帧 ≈ 30s
- Eevee 1024p 32smp: ~2-3s/帧 → 24帧 ≈ 60s
- Cycles 512p 32smp: ~3-5s/帧 → 24帧 ≈ 90s

## 完整参数示例

```python
import sys
sys.path.insert(0, "/home/kai/.openclaw/workspace/skills/kais-blender-action/client")
from action_recorder import ActionRecorder

rec = ActionRecorder("http://192.168.71.38:8080")

# 场景：录制一个跑步动作的侧面中景
result = rec.record(
    # --- 角色 & 动画 ---
    character="hero.fbx",
    motion="run.fbx",
    
    # --- 时间控制（ms级）---
    start_ms=800,          # 跳过起步阶段
    duration_ms=2000,      # 录制 2 秒稳定跑步
    fps=30,                # 30fps 精度约 33ms
    
    # --- 镜头控制 ---
    camera={
        "azimuth": 85,       # 几乎纯侧面
        "elevation": 5,      # 微俯
        "distance": 3.5,     # 中景距离
        "target_height": 0.9, # 注视腰部
        "fov": 50,           # 标准视角
        "lens_shift_y": 0.1, # 微上移
    },
    
    # --- 渲染设置 ---
    resolution=768,
    samples=32,
    engine="eevee",
    transparent_bg=True,
    lighting="studio",
    
    # --- 输出 ---
    output_name="run_side_mid_001",
    output_dir="outputs/actions/",
)

print("状态:", result["status"])
print("视频路径:", result.get("video_path"))
print("实际帧范围:", result.get("frame_range"))
print("实际时长(ms):", result.get("actual_duration_ms"))
```

## 批量录制

一次指定多个镜头方案，批量输出参考视频。

```python
# 同一动作，多角度录制
shots = [
    {"camera": "front_waist", "duration_ms": 2000, "output_name": "walk_front"},
    {"camera": "side_waist", "duration_ms": 2000, "output_name": "walk_side"},
    {"camera": "three_quarter", "duration_ms": 2000, "output_name": "walk_3q"},
]

results = rec.record_batch(
    character="hero.fbx",
    motion="walk.fbx",
    shots=shots,
    resolution=512,
    engine="eevee",
)

for r in results:
    print(f"{r['output_name']}: {'✅' if r['success'] else '❌'} {r.get('video_path', r.get('error'))}")
```

## 动画信息查询

```python
# 列出可用角色和动画
assets = rec.list_assets()
print("角色:", [c["name"] for c in assets["characters"]])
print("动画:", [m["name"] for m in assets["motions"]])

# 获取动画时长信息
info = rec.get_motion_info("walk.fbx")
print(f"时长: {info['duration_frames']} 帧 = {info['duration_ms']} ms @ {info['fps']}fps")

# 预览动画帧范围（不渲染，返回关键帧信息）
preview = rec.preview_motion(
    motion="run.fbx",
    start_ms=0,
    duration_ms=3000,
    fps=24,
)
print("帧范围:", preview["frame_start"], "-", preview["frame_end"])
print("实际时长:", preview["actual_duration_ms"], "ms")
```

## 工作流程（与 kais-jimeng 协作）

```
1. kais-blender-action: 录制动作参考视频
   ↓ 输出 MP4（透明背景 + 动作细节）
2. 人工/AI: 从视频中选取关键帧截图
   ↓ 或直接用视频作为参考
3. kais-jimeng: 根据动作参考生成目标图片
   ↓ 图生视频或图生图
4. kais-evolink/kais-camera: 生成最终视频
```

## 与其他 Skill 的协作

```
kais-blender-assets (下载角色/动画 FBX)
       ↓
kais-blender-action (本skill) → 动作录制 → 预览视频
       ↓
kais-jimeng (动作参考 → 目标图)
       ↓
kais-camera / kais-evolink (最终视频)
```

## 注意事项

- 角色和动画 FBX 需提前通过 kais-blender-assets 下载放入对应目录
- 新增资产后需调用 `rec.refresh_assets()` 刷新索引
- 透明背景视频需播放器支持 alpha 通道（如 VLC、浏览器）
- 如需精确到亚帧级别的时间控制，使用 `fps=60`
- 快速预览建议 Eevee + 512p，清晰参考用 Cycles + 1024p
- 录制结果默认保存在 Windows 端 `D:\BlenderAgent\outputs\actions\`
