---
name: kais-parallax-scene
version: 0.6.0
description: "AI视差场景生成器。三种模式：(1)AI三步法：即梦文生图→图生图分层→视差合成；(2)深度分层法：MiDaS GPU分层→Blender渲染；(3)DepthFlow：GLSL shader实时渲染，支持多种镜头运动+后处理。触发词：视差场景, parallax, 2.5D场景, AI视差, parallax scene, 视差动画, 景深分层, 场景分层, 即梦宽图, parallax animation, 视差生成, depthflow, 2.5D视频"
---

# kais-parallax-scene — AI视差场景生成器

> **三种管线模式**：
>
> | 模式 | 流程 | 适用场景 | 质量 | 速度 |
> |------|------|----------|------|------|
> | **AI三步法** ⭐ | 即梦文生图 → 图生图(背景+前景) → rembg抠图 → 视差合成 | 任意场景，无分割重影 | ⭐⭐⭐⭐⭐ | 慢 |
> | **DepthFlow** ⭐⭐ | 深度图估算 → GLSL shader 实时渲染 | 快速出片，效果丰富 | ⭐⭐⭐⭐ | **极快（~4s/视频）** |
> | 深度分层法 | MiDaS GPU分层 → Blender渲染 | 有明确景深的场景 | ⭐⭐⭐ | 中 |
>
> **推荐组合**：AI三步法（分层）+ DepthFlow（渲染）= 王炸
>
> **快速出片**：直接用 DepthFlow，内置 DepthAnything V2 自动估算深度图

## 前置依赖

<!-- FREEDOM:low -->

### AI三步法（推荐）
- **jimeng-free-api** Docker 容器运行中（Linux 端 `localhost:8000`）
- **即梦 session ID**（环境变量 `JIMENG_SESSION_ID` 或 Docker 容器内获取）
- **rembg** — Python 背景移除（`pip install rembg`）
- **numpy** + **Pillow** + **ffmpeg**

### 深度分层法
- **kais-blender-engine** skill 已安装，Windows 端 Blender Agent Server 运行中
- **Windows 端 Python 依赖**：`torch` 2.7+ (CUDA), `transformers`, `scipy`, `Pillow`

## 管线位置

```
即梦/SD 超宽图 ──→ [kais-parallax-scene] ──→ 动态镜头视频
                         │
                    全在Windows端
                         │
              ┌──────────┴──────────┐
         MiDaS深度分层(GPU)    Blender视差渲染(GPU)
              │                      │
         分层PNG + layers.json   generate_parallax_script()
              │                 engine.run_async()
              └──────────┬──────────┘
                         │
                    .mp4 + .blend
```

**与 kais-blender-layout 的关系**：
- layout 负责"3D资产场景"（角色+家具+HDRI建模渲染）
- parallax-scene 负责"2D超宽图→2.5D动态"（AI绘图分层+视差动画）
- 两者共享 kais-blender-engine 的 Windows GPU 渲染能力

---

## ⭐ AI三步法管线（推荐）

```
用户图/即梦文生图 ──→ 即梦图生图(背景21:9) ──→ 即梦图生图(前景16:9) ──→ rembg抠图 ──→ 视差合成 ──→ MP4
       ①                     ②a                      ②b                   ③a            ③b
```

**核心思路**：AI生成独立的背景和前景图，不依赖分割，彻底避免重影和黑块。

**步骤1支持两种输入**：
- **用户图**（`--source-image`）：直接用用户的图进入步骤2
- **文生图**（`--prompt`）：即梦AI生成场景图后进入步骤2

### 一键执行

```bash
# 方式A: 用户已有图，直接分层
python3 scripts/ai_parallax_pipeline.py \
  --source-image ./coffee_shop.png \
  --prompt "A cozy coffee shop interior" \
  -o coffee_parallax.mp4

# 方式B: 纯AI生成
python3 scripts/ai_parallax_pipeline.py \
  --prompt "A cozy coffee shop interior, warm lighting, wooden tables, photorealistic" \
  -o output.mp4

# 完整参数
python3 scripts/ai_parallax_pipeline.py \
  --prompt "咖啡店内部，暖色调，木桌" \
  -o coffee_parallax.mp4 \
  --bg-ratio 21:9 \
  --duration 4.0 \
  --fps 24 \
  --work-dir /tmp/jimeng_parallax
```

### 步骤详解

| 步骤 | 操作 | 输入 | 输出 |
|------|------|------|------|
| ① 获取原始图 | 用户图 or 即梦文生图 | `--source-image` or `--prompt` | `step1_original.png` (16:9) |
| ②a 图生图(背景) | 参考原始图→纯背景 | 步骤①的图 | `step2_background.png` (21:9超宽) |
| ②b 图生图(前景) | 参考原始图→前景 | 步骤①的图 | `step3_foreground_raw.png` (16:9) |
| ③a rembg抠图 | 去除前景白底 | 步骤②b | `step3_foreground_clean.png` |
| ③b 视差合成 | 背景+前景→MP4 | 步骤②a+③a | `output.mp4` |

### 参数说明

| 参数 | 默认 | 说明 |
|------|------|------|
| `--prompt` | 场景描述（有--source-image时可选） |
| `--source-image` | None | 用户提供的原始图路径（跳过文生图） |
| `--bg-ratio` | 21:9 | 背景图比例（21:9提供更大平移空间） |
| `--fg-ratio` | 16:9 | 前景图比例 |
| `--duration` | 3.0 | 视频时长(秒) |
| `--fps` | 24 | 帧率 |
| `--resolution` | 2k | 即梦生图分辨率 |
| `--session-id` | 自动 | 即梦session（默认从Docker容器获取） |

### 合成原理

```
每帧：
1. 背景层（超宽21:9）→ Ken Burns微动裁剪 → canvas
2. 前景层（rembg抠图）→ 更大偏移 → alpha叠加到canvas
3. 前景动得多 + 背景动得少 = 自然景深
```

- 背景是AI生成的完整图（无黑块）
- 前景是AI生成的独立图（无重影）
- 两层各自预放大一次再裁剪（无顿挫）
- alpha叠加（前景边缘自然融合）

### Prompt 技巧

- **英文**效果比中文好（即梦训练数据偏向英文）
- 背景prompt加 `background only, no people no furniture, empty interior`
- 前景prompt加 `foreground subjects only, isolated on white background, cutout style`
- 通用后缀加 `photorealistic, 8k, cinematic lighting`

---

## 深度分层法（传统）

```
步骤一：GPU深度分层              步骤二：GPU视差渲染
─────────────────────────────────────────────────────────
超宽图.png → MiDaS(CUDA)  →     engine.run_async()
           前景/中景/背景PNG  →    generate_parallax_script()
           layers.json          Blender Eevee → MP4
```

---

## 步骤一：深度分层（Windows GPU）

通过 engine 的 `run_async()` 在 Windows 端执行 MiDaS 深度估计：

```python
import sys
sys.path.insert(0, "/path/to/kais-blender-engine/client")
from blender_client import BlenderAgentClient

cli = BlenderAgentClient("http://192.168.71.38:8080")

# 读取分层脚本并发送到Windows执行
with open("scripts/depth_segment_win.py") as f:
    segment_code = f.read()

cmd = f"""
import sys
sys.argv = ["depth_segment_win.py", "D:/path/to/wide.png", "-o", "D:/BlenderAgent/cache/parallax/scene1", "-l", "3"]
{segment_code}
"""

job_id = cli.run_async(cmd, timeout=300)
status = cli.poll_job(job_id, interval=10, max_wait=300)
# 输出: D:/BlenderAgent/cache/parallax/scene1/{foreground,midground,background}.png + layers.json
```

**输出**：
- `foreground.png` / `midground.png` / `background.png` — 分层透明PNG
- `depth_map.png` — 深度灰度图
- `layers.json` — 图层配置（Z深度 + 路径）

### 分层方案

| 方案 | 说明 | 适用场景 |
|------|------|----------|
| MiDaS自动（默认） | `Intel/dpt-large`，GPU推理 ~1s | 通用场景 |
| 4层精细 | `-l 4`，增加distant层 | 复杂景深 |
| 手动蒙版 | 修改脚本跳过AI | 分割不完美时 |

---

## 步骤二：视差渲染（Windows GPU）

读取 `layers.json`，通过 engine 的 `generate_parallax_script()` 渲染：

```python
import sys, json
sys.path.insert(0, "/path/to/kais-blender-engine/client")
from blender_client import BlenderAgentClient
from generators.parallax import ParallaxParams, LayerConfig, generate_parallax_script

cli = BlenderAgentClient("http://192.168.71.38:8080")

params = ParallaxParams(
    preset_name="scene_001",
    layers=[
        LayerConfig(name="foreground", image_path="D:/.../foreground.png", z_depth=-1.5),
        LayerConfig(name="midground",  image_path="D:/.../midground.png",  z_depth=0.0),
        LayerConfig(name="background", image_path="D:/.../background.png", z_depth=7.5),
    ],
    camera_preset="scroll_left",
    duration=6.0,
    resolution=(1080, 1920),
    output_format="video",
    output_dir="D:/BlenderAgent/cache/parallax",
)

script = generate_parallax_script(params)
job_id = cli.run_async(script, timeout=600)
status = cli.poll_job(job_id, interval=10, max_wait=600)
# 输出: .mp4 + .blend + 帧序列
```

### 摄像机预设

| 预设 | 运动 | 适用场景 |
|------|------|----------|
| `scroll_left` | 横向平移←→，缓入缓出 | 场景展示、交代环境 |
| `scroll_right` | 反向平移→← | 反向展示 |
| `push_in` | 缓慢推进 | 聚焦主体 |
| `dolly_zoom` | 推近+缩小焦距 | Vertigo效果 |
| `orbit` | 环绕旋转90° | 物体展示 |
| `static` | 静态 | 仅输出分层场景图 |

### ParallaxParams 字段

| 字段 | 类型 | 默认 | 说明 |
|------|------|------|------|
| `preset_name` | str | 必填 | 输出文件名前缀 |
| `layers` | List[LayerConfig] | 必填 | 图层列表 |
| `camera_preset` | str | `scroll_left` | 摄像机预设 |
| `camera_focal_length` | float | 35.0 | 焦距(mm) |
| `camera_distance` | float | 2.0 | 摄像机Y轴距离 |
| `duration` | float | 6.0 | 动画时长(秒) |
| `fps` | int | 24 | 帧率 |
| `move_range` | float | 3.0 | 平移范围(米) |
| `output_format` | str | `video` | video / frames / both |
| `resolution` | tuple | (1080,1920) | (宽, 高) |
| `engine` | str | `BLENDER_EEVEE` | 渲染引擎 |
| `output_dir` | str | `D:/.../parallax` | Windows端输出目录 |

---

## 一键编排

```bash
# 全流程（Linux端编排，Windows端执行）
python3 scripts/parallax_pipeline.py \
  --image-path "D:/path/to/wide.png" \
  --name scene_001 \
  --camera scroll_left \
  --duration 6.0 \
  --ratio 9:16
```

---

## 硬件需求

| 步骤 | 资源 | 我们的配置 |
|------|------|-----------|
| MiDaS分层 | GPU VRAM 2-3GB, ~1s/张 | RTX 4070 ✅ |
| Blender渲染 | GPU VRAM 1-2GB, ~3s/72帧 | RTX 4070 ✅ |
| 模型存储 | ~1.3GB磁盘 | D盘充足 ✅ |

## 技术限制

| 限制 | 缓解方案 |
|------|----------|
| 无法镜头穿过前景 | 限制摄像机Z轴移动 |
| 侧面视角穿帮 | 边缘延伸10%+模糊 |
| 动态元素（水、火） | 结合视频生成工具 |
| 分割不完美 | 手动提供蒙版 |

---

## 双模式自动选择

<!-- FREEDOM:low -->

合成引擎根据**深度图方差**自动选择最佳模式：

| 模式 | 条件 | 效果 | 适用场景 |
|------|------|------|----------|
| **视差偏移** | `depth_variance > 0.12` | 各层按深度不同偏移 | 风景、户外、有纵深感 |
| **Ken Burns** | `depth_variance ≤ 0.12` | 缓慢缩放+平移 | 室内、平坦、浅景深 |

### 视差模式参数

| 参数 | 默认 | 说明 |
|------|------|------|
| `--parallax-strength` | 200 | 前景最大偏移(px) |

### Ken Burns模式参数

| 参数 | 默认 | 说明 |
|------|------|------|
| `--kenburns-zoom` | 1.15 | 缩放倍率（1.0=不缩放） |
| `--kenburns-pan` | 100 | 平移范围(px) |

### 强制指定模式

```bash
# 强制视差
python parallax_composite.py --image-dir <dir> --mode parallax --output out.mp4
# 强制Ken Burns
python parallax_composite.py --image-dir <dir> --mode kenburns --output out.mp4
# 自动选择（默认）
python parallax_composite.py --image-dir <dir> --output out.mp4
```

---

## ⭐⭐ DepthFlow 模式（推荐快速出片）

> **开源项目**：[BrokenSource/DepthFlow](https://github.com/BrokenSource/DepthFlow)
> **原理**：GLSL shader 在 GPU 上实时渲染，基于深度图做视差动画
> **核心优势**：极快（~4秒/3秒视频）、效果丰富、内置 AI 深度估算、无需手动分层

### 安装（Windows 端）

```bash
# 需要 Python 3.10+（3.9 不支持 numpy-quaternion）
C:\Python311\python.exe -m pip install depthflow

# 验证
C:\Python311\Scripts\depthflow.exe --help
```

### 硬件要求

| 配置 | 最低 | 我们的配置 |
|------|------|-----------|
| GPU | 任意 OpenGL 4.0 显卡 | ✅ RTX 3060 Ti 8GB |
| VRAM | 1GB+ | ✅ 8GB |
| Python | 3.10+ | ✅ 3.11（C:\Python311） |
| 依赖 | FFmpeg | ✅ D:\Program\ImportLib\ffmpeg-6.0 |

### 内置深度估算器

| 估算器 | 精度 | 速度 | 状态 | 说明 |
|--------|------|------|------|------|
| **DepthAnything V2** ⭐ | 高 | 中（首次~80s下载） | ✅ 可用 | 默认，推荐 |
| **DepthAnything V1** | 中 | 快（首次~195s下载） | ✅ 可用 | 备选，速度稍快 |
| DepthPro | 高 | 慢 | ❌ 缺torchvision | Apple 出品，需 `pip install torchvision` |
| ZoeDepth | 中 | 快 | ❌ abort | 轻量但有兼容问题 |
| Marigold | 最高 | 慢 | ❌ 超时 | 精度最好，模型太大（>5min） |

**首次运行自动下载模型**，之后缓存到 `C:\Users\Kai\AppData\Local\BrokenSource\DepthFlow\cache\depthmap`

### 动画预设（6种）

| 预设 | 运动方式 | 适用场景 | CLI |
|------|----------|----------|-----|
| **horizontal** | 水平左右平移 | 场景展示、交代环境 | `horizontal` |
| **vertical** | 垂直上下移动 | 建筑扫视、瀑布 | `vertical` |
| **zoom** | 缩放（可配置方向） | 聚焦主体、情绪递进 | `zoom` |
| **dolly** | 推近/远离（变焦感） | 希区柯克眩晕感 | `dolly` |
| **circle** | 圆弧运动 | 3D旋转展示 | `circle` |
| **orbital** | 轨道环绕 | 产品展示、360°感 | `orbital` |

### 后处理效果（可叠加）

| 效果 | 说明 | CLI |
|------|------|-----|
| **blur** | 深度感知景深虚化（DOF）⭐ 最佳边缘处理 | `blur` |
| **vignette** | 边缘暗角，增加电影感 | `vignette` |
| **lens** | 镜头畸变（广角/鱼眼），增加戏剧性 | `lens` |
| **colors** | 调色效果，自动调整色调 | `colors` |

> ⚠️ `inpaint` 不推荐使用：会以绿色填充深度图陡峭区域，效果不自然。用 `blur` 代替即可。

### 一键生成

```bash
# 基础用法（SSH 从 Linux 端调用）
ssh -i ~/.ssh/id_windows kai@192.168.71.38 \
  "C:\Python311\Scripts\depthflow.exe input -i C:\Users\kai\image.png horizontal h264 main -t 3 -w 1344 -h 768 -o C:\Users\kai\output.mp4"

# 带后处理（推拉+景深+暗角）
ssh -i ~/.ssh/id_windows kai@192.168.71.38 \
  "C:\Python311\Scripts\depthflow.exe input -i C:\Users\kai\image.png dolly blur vignette h264 main -t 4 -o C:\Users\kai\output.mp4"

# 自定义深度图（用 AI 三步法生成的深度图）
ssh -i ~/.ssh/id_windows kai@192.168.71.38 \
  "C:\Python311\Scripts\depthflow.exe input -i C:\Users\kai\image.png -d C:\Users\kai\depth.png circle blur h264 main -t 5 -o C:\Users\kai\output.mp4"
```

### CLI 完整参数

```
depthflow input -i IMAGE [-d DEPTHMAP] {ANIMATION} {POSTFX} {ENCODER} main -t SECONDS -w WIDTH -h HEIGHT -o OUTPUT.mp4
```

| 参数 | 默认 | 说明 |
|------|------|------|
| `-i` | 必填 | 输入图片路径 |
| `-d` | None（自动估算） | 自定义深度图 |
| `-t` | 10 | 视频时长（秒） |
| `-w` | 图片宽度 | 输出宽度 |
| `-h` | 图片高度 | 输出高度 |
| `-o` | 自动命名 | 输出路径 |
| `h264` | — | CPU H.264 编码（SSH 会话中用这个） |
| `h264-nvenc` | — | GPU NVENC 编码（需本地桌面会话） |

### 动画预设参数（可选微调）

| 参数 | 说明 | 示例 |
|------|------|------|
| `--intensity -i` | 全局强度 0-4（默认1.0） | `horizontal -i 2.0` |
| `--smooth -s` | 平滑变体（正弦波，默认开启） | `horizontal --linear` |
| `--loop -l` | 循环播放（默认开启） | `horizontal --no-loop` |
| `--steady -S` | 无位移时的深度值 -1~2（默认0.3） | `horizontal -S 0.5` |
| `--isometric -I` | 等距投影程度 0~1（默认0.6） | `horizontal -I 0.9` |

### 推荐效果组合

| # | 组合 | 效果 | 适用场景 |
|---|------|------|----------|
| 1 | `circle blur vignette` | 圆弧+景深+暗角 ⭐⭐ | 电影级场景展示 |
| 2 | `dolly blur` | 推拉+景深 | 希区柯克眩晕感 |
| 3 | `orbital blur` | 环绕+景深 | 产品展示 |
| 4 | `horizontal lens blur` | 横移+畸变+景深 | 戏剧性透视 |
| 5 | `zoom lens` | 缩放+镜头畸变 | 冲击感 |
| 6 | `horizontal vignette` | 横移+暗角 | 电影质感 |
| 7 | `realesr circle blur vignette` | 超分+圆弧+景深+暗角 ⭐⭐⭐ | 画质+电影感拉满 |
| 8 | `zoom --linear lens` | 匀速推进+镜头畸变 | 纪录片式推进 |

---

## 全量测试效果详解

> 以下为 RTX 3060 Ti 实测，1344x768@60fps，基于同一张原图

### 基础动画（6种）

| # | 效果 | CLI | 视觉感受 | 适用场景 |
|---|------|-----|----------|----------|
| 01 | 水平横移 | `horizontal` | 经典视差，左右缓慢平移 | 场景展示、交代环境、故事开场 |
| 02 | 垂直移动 | `vertical` | 上下扫视，展示垂直空间 | 建筑、瀑布、高层景观 |
| 03 | 缩放 | `zoom` | 缓入缓出推进/拉远，聚焦主体 | 情绪递进、特写过渡 |
| 04 | 推拉变焦 | `dolly` | 推近同时焦距变化，希区柯克眩晕感 | 悬疑、心理暗示、梦境 |
| 05 | 圆弧运动 | `circle` | 围绕焦点做弧线运动，3D感最强 | 3D旋转展示、全景环绕 |
| 06 | 轨道环绕 | `orbital` | 360°轨道环绕，展示主体全貌 | 产品展示、人物亮相、地标 |

### 后处理组合（6种）

| # | 效果 | CLI | 视觉感受 | 适用场景 |
|---|------|-----|----------|----------|
| 07 | 横移+暗角 | `horizontal vignette` | 边缘压暗聚焦中心 | 电影质感、怀旧氛围 |
| 08 | 推拉+景深 | `dolly blur` | 前景/背景虚化，主体清晰 | 人像、电影级叙事 |
| 09 | 缩放+镜头畸变 | `zoom lens` | 广角推进，边缘拉伸 | 冲击感、戏剧张力 |
| 10 | 圆弧+景深+暗角 | `circle blur vignette` ⭐⭐ | 三重后处理，电影感最强 | 高品质短片、宣传片 |
| 11 | 环绕+景深 | `orbital blur` | 环绕同时景深虚化 | 产品展示、角色介绍 |
| 12 | 横移+畸变+景深 | `horizontal lens blur` | 三重叠加，戏剧性最强 | 艺术短片、MV |

### 超分辨率放大（2种）

| # | 效果 | CLI | 视觉感受 | 首次耗时 | 适用场景 |
|---|------|-----|----------|----------|----------|
| 05s | RealESRGAN+圆弧 | `realesr circle` | 画质明显提升，细节更锐利 | ~52s（下载模型） | 真实照片、风景、建筑 |
| 06s | Waifu2x+圆弧 | `waifu2x circle` | 柔和降噪，适合二次元风格 | ~138s（下载模型） | 动漫、插画、二次元 |

> 后续使用模型已缓存，速度与普通效果一致（~4s）

### 高级参数效果（6种）

| # | 效果 | CLI | 视觉感受 | 与默认的区别 |
|---|------|-----|----------|-------------|
| 08s | 匀速推进 | `zoom --linear` | 匀速前进，没有缓入缓出 | 默认zoom有呼吸感加速减速，linear是稳定推进 |
| 13s | 4x超采样圆弧 | `circle -s 2` | 边缘更平滑，抗锯齿 | SSAA 2x = 4倍超采样，GPU开销增4倍 |
| 14s | 高质量推拉 | `dolly -q 90` | 质量提升，渲染更精细 | 默认q=50，90接近最高画质 |
| 16s | 超分+全效果 | `realesr circle blur vignette` ⭐⭐⭐ | 画质+电影感+景深全拉满 | 最佳画质组合 |
| 21s | 慢动作推拉 | `dolly -S 0.5` | 0.5x慢放，更有仪式感 | 默认1x速度，适合情绪渲染 |
| 22s | 不循环横移 | `horizontal --no-loop` | 单次播放，不回头 | 默认循环（来回摆动），no-loop是单向 |

### 特殊投影效果（2种）

| # | 效果 | CLI | 视觉感受 | 适用场景 |
|---|------|-----|----------|----------|
| 23s | 等距投影横移 | `horizontal -I 1.0` | 完全平面感，无透视变形 | 等距视角游戏风、信息图、地图 |
| 24s | 3倍循环圆弧 | `circle -l 3` | 同一动画循环3次 | 循环背景、无缝衔接、社交媒体 |

### 调色效果（1种）

| # | 效果 | CLI | 视觉感受 | 适用场景 |
|---|------|-----|----------|----------|
| 19s | 调色+环绕 | `orbital colors` | 自动调色，色调偏暖 | 氛围增强、情绪渲染 |

### 性能数据（RTX 3060 Ti）

| 分辨率 | 帧率 | 时长 | 生成时间 | 编码 |
|--------|------|------|----------|------|
| 1344x768 | 60fps | 3s | ~4s | h264 (CPU) |
| 1920x1080 | 60fps | 3s | ~5s | h264 (CPU) |
| 2560x1440 | 60fps | 3s | ~8s | h264 (CPU) |

### 注意事项

- **SSH 会话中不能用 NVENC**：无 GPU 访问权限，用 `h264` 代替 `h264-nvenc`
- **首次运行慢**：自动下载 DepthAnything V2 模型（~80s），之后缓存复用
- **边缘瑕疵**：AI 自动估算的深度图在物体边缘可能不完美，提供自定义深度图可改善
- **与 AI 三步法结合**：用 AI 三步法生成独立背景+前景，手动合成深度图后喂给 DepthFlow，效果最佳

---

## 文件结构

```
kais-parallax-scene/
├── SKILL.md                          # 本文件
├── scripts/
│   ├── ai_parallax_pipeline.py       # ⭐ AI三步法管线
│   ├── depth_segment_win.py          # Windows端深度分层脚本（GPU）
│   ├── parallax_composite.py         # 双模式合成引擎
│   └── parallax_pipeline.py          # 深度分层全流程编排
├── references/
│   ├── parallax-math.md              # 视差数学原理
│   └── midas-setup.md                # MiDaS安装指南
└── tools/
    └── depthflow.md                  # DepthFlow 使用笔记
```
