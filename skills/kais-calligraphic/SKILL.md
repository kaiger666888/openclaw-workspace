---
name: kais-calligraphic
description: "视频中自由插入行书毛笔字浮现动画。支持多种浮现效果（横向擦除、渐变浮现、水墨散开、墨迹渗透），可指定位置、时间、字体、大小。触发词：毛笔字动画、calligraphy、书法浮现、毛笔字叠加、行书动画、ink animation、书法效果、calligraphy overlay"
---

# kais-calligraphic — 视频毛笔字浮现动画

在视频中任意位置、任意时间点插入行书毛笔字浮现动画。

## 触发词

`毛笔字动画`, `calligraphy`, `书法浮现`, `毛笔字叠加`, `行书动画`, `ink animation`, `书法效果`, `calligraphy overlay`

## 输入参数

| 参数 | 必填 | 默认值 | 说明 |
|------|------|--------|------|
| `--text` | ✅ | - | 要显示的文字内容 |
| `--video` | ✅ | - | 输入视频路径 |
| `--output` | ✅ | `output.mp4` | 输出视频路径 |
| `--font` | ❌ | 自动检测行书字体 | 行书 TTF 字体路径 |
| `--x` | ❌ | `center` | X 坐标（像素或 center/left/right） |
| `--y` | ❌ | `center` | Y 坐标（像素或 center/top/bottom） |
| `--start` | ❌ | `0` | 动画开始时间（秒） |
| `--duration` | ❌ | `3` | 浮现动画时长（秒） |
| `--hold` | ❌ | `2` | 浮现后保持时长（秒，0=不保持） |
| `--effect` | ❌ | `horizontal_wipe` | 浮现效果类型 |
| `--fontsize` | ❌ | `80` | 字体大小（像素） |
| `--color` | ❌ | `#1a1a1a` | 文字颜色（十六进制） |
| `--fps` | ❌ | `24` | 输出帧率 |

### 浮现效果类型 (`--effect`)

| 效果 | 说明 | 视觉 |
|------|------|------|
| `horizontal_wipe` | 从左到右擦除浮现 | 最经典，适合横排文字 |
| `vertical_wipe` | 从上到下擦除浮现 | 适合竖排文字 |
| `fade_in` | 整体透明度渐变 | 简洁优雅 |
| `ink_spread` | 水墨散开效果 | 艺术感最强 |
| `ink_bleed` | 墨迹渗透效果 | 从笔画中心向外扩散 |

## 执行流程

```bash
# 1. 安装依赖（首次）
pip install Pillow numpy moviepy

# 2. 生成毛笔字浮现动画视频
python3 ~/.openclaw/workspace/skills/kais-calligraphic/scripts/calligraphic_overlay.py \
  --text "床前明月光" \
  --video /path/to/input.mp4 \
  --output /path/to/output.mp4 \
  --effect ink_spread \
  --start 2.5 \
  --duration 3 \
  --fontsize 100 \
  --color "#1a1a1a"
```

## 技术架构

```
用户输入(text+视频+位置+时间)
    ↓
Pillow 渲染文字 → 透明 PNG
    ↓
生成浮现效果 mask 帧序列
    ↓
MoviePy 合成：mask × 文字 + 原视频
    ↓
输出 MP4
```

### 核心原理

1. **文字渲染**：Pillow + 行书 TTF 字体，渲染到 RGBA 透明背景
2. **浮现动画**：生成与文字同尺寸的渐变 mask，逐帧从全透明过渡到全不透明
3. **视频叠加**：MoviePy CompositeVideoClip，精确控制位置和时间段

## 字体资源

脚本会自动搜索系统中的行书字体。推荐安装：

- **站酷庆科黄油体**：免费商用，zcool.com.cn
- **苏轼行书**：免费，qqxiuzi.cn
- **方正字迹-吕建德行楷**：付费
- **字魂系列**：部分免费

将 TTF 文件放入 `scripts/fonts/` 目录，或用 `--font` 指定路径。

## 使用示例

### 基础用法：视频中浮现诗句
```bash
python3 scripts/calligraphic_overlay.py \
  --text "春眠不觉晓" \
  --video background.mp4 \
  --output result.mp4
```

### 水墨效果，自定义位置
```bash
python3 scripts/calligraphic_overlay.py \
  --text "大江东去浪淘尽" \
  --video scene.mp4 \
  --output result.mp4 \
  --x 100 --y 200 \
  --effect ink_spread \
  --fontsize 120 \
  --start 5
```

### 竖排文字
```bash
python3 scripts/calligraphic_overlay.py \
  --text "天下\n风\n流" \
  --video video.mp4 \
  --output result.mp4 \
  --effect vertical_wipe \
  --fontsize 90
```

## 注意事项

- 视频编解码器需支持透明通道（如用 PNG 序列中间产物）
- 大字号 + 复杂效果会增加渲染时间
- 竖排文字用 `\n` 换行，横向宽度自动取最大行
- `ink_spread` 和 `ink_bleed` 效果需要 numpy
