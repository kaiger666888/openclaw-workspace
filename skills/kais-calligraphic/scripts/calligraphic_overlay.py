#!/usr/bin/env python3
"""
kais-calligraphic — 视频毛笔字浮现动画生成器

在视频中任意位置、任意时间点插入行书毛笔字浮现动画。
"""

import argparse
import os
import sys
import glob
import math
import numpy as np
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont, ImageFilter
except ImportError:
    print("请先安装依赖: pip install Pillow numpy moviepy")
    sys.exit(1)

try:
    from moviepy import (
        VideoFileClip, CompositeVideoClip, VideoClip,
        ImageClip, ColorClip
    )
    import moviepy
except ImportError:
    print("请先安装依赖: pip install Pillow numpy moviepy")
    sys.exit(1)


# ============================================================
# 字体搜索
# ============================================================

SKILL_DIR = Path(__file__).parent.parent
FONTS_DIR = SKILL_DIR / "scripts" / "fonts"

# 常见行书/毛笔字体关键词
CALLIGRAPHY_KEYWORDS = [
    "行书", "行楷", "毛笔", "brush", "calligraphy",
    "苏轼", "黄庭坚", "王羲之", "颜真卿", "楷体",
    "站酷", "庆科", "字魂", "dotgo", "zcool",
    "libian", "LiSu", "楷", "STKaiti", "FZKai",
    "KaiTi", "simkai", "FangSong", "STFangsong",
]

def find_calligraphy_font():
    """自动搜索系统中的毛笔/行书字体"""
    # 1. 先检查 skill 内置字体目录
    for f in FONTS_DIR.glob("*.ttf"):
        return str(f)
    for f in FONTS_DIR.glob("*.ttc"):
        return str(f)
    for f in FONTS_DIR.glob("*.otf"):
        return str(f)

    # 2. 搜索常见字体目录
    font_dirs = [
        "/usr/share/fonts",
        "/usr/local/share/fonts",
        "/System/Library/Fonts",
        "/Library/Fonts",
        os.path.expanduser("~/.fonts"),
        os.path.expanduser("~/.local/share/fonts"),
        "C:/Windows/Fonts",
    ]

    candidates = []
    for d in font_dirs:
        if not os.path.exists(d):
            continue
        for root, _, files in os.walk(d):
            for f in files:
                if f.lower().endswith(('.ttf', '.ttc', '.otf')):
                    filepath = os.path.join(root, f)
                    for kw in CALLIGRAPHY_KEYWORDS:
                        if kw.lower() in f.lower() or kw.lower() in filepath.lower():
                            candidates.append((filepath, f))

    if candidates:
        # 优先行书/毛笔
        for filepath, name in candidates:
            for kw in ["行书", "行楷", "毛笔", "brush", "calligraphy"]:
                if kw.lower() in name.lower():
                    return filepath
        return candidates[0][0]

    # 3. 最后回退：搜索任何中文字体
    for d in font_dirs:
        if not os.path.exists(d):
            continue
        for root, _, files in os.walk(d):
            for f in files:
                if f.lower().endswith(('.ttf', '.ttc', '.otf')):
                    for kw in ["Kai", "楷", "STKaiti", "FangSong", "仿宋", "Song", "宋"]:
                        if kw.lower() in f.lower():
                            return os.path.join(root, f)

    return None


# ============================================================
# 文字渲染
# ============================================================

def render_text(text, font_path, fontsize, color, max_width=None):
    """
    渲染文字到透明 PNG

    Returns:
        Image: RGBA 模式的文字图片
    """
    try:
        font = ImageFont.truetype(font_path, fontsize)
    except Exception:
        # 回退到默认字体
        font = ImageFont.load_default()

    # 计算文字尺寸（支持多行）
    lines = text.split('\n')
    line_sizes = []
    for line in lines:
        bbox = font.getbbox(line)
        line_sizes.append((bbox[2] - bbox[0], bbox[3] - bbox[1]))

    # 如果指定了最大宽度，自动缩小字号
    if max_width:
        max_line_width = max(s[0] for s in line_sizes)
        if max_line_width > max_width:
            ratio = max_width / max_line_width
            new_size = int(fontsize * ratio)
            font = ImageFont.truetype(font_path, new_size)
            line_sizes = []
            for line in lines:
                bbox = font.getbbox(line)
                line_sizes.append((bbox[2] - bbox[0], bbox[3] - bbox[1]))

    line_height = max(s[1] for s in line_sizes) if line_sizes else fontsize
    total_width = max(s[0] for s in line_sizes) if line_sizes else fontsize
    total_height = line_height * len(lines) + int(line_height * 0.3 * (len(lines) - 1))

    img = Image.new('RGBA', (total_width + 20, total_height + 20), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    y = 10
    for i, line in enumerate(lines):
        lw, lh = line_sizes[i]
        x = 10 + (total_width - lw) // 2  # 居中
        draw.text((x, y), line, font=font, fill=color)
        y += line_height + int(line_height * 0.3)

    return img


# ============================================================
# 浮现效果生成
# ============================================================

def make_mask(width, height, progress, effect):
    """
    生成单帧 mask

    Args:
        width, height: mask 尺寸
        progress: 0.0 ~ 1.0，动画进度
        effect: 效果类型

    Returns:
        numpy array (H, W), 0~255
    """
    if effect == 'horizontal_wipe':
        mask = np.zeros((height, width), dtype=np.float32)
        # 添加一点随机边缘，模拟毛笔不均匀
        edge_noise = np.random.uniform(-0.05, 0.05, height)
        for y in range(height):
            cutoff = int(progress * width + edge_noise[y] * width)
            cutoff = max(0, min(width, cutoff))
            mask[y, :cutoff] = 255
        return mask.astype(np.uint8)

    elif effect == 'vertical_wipe':
        mask = np.zeros((height, width), dtype=np.float32)
        edge_noise = np.random.uniform(-0.05, 0.05, width)
        for x in range(width):
            cutoff = int(progress * height + edge_noise[x] * height)
            cutoff = max(0, min(height, cutoff))
            mask[:cutoff, x] = 255
        return mask.astype(np.uint8)

    elif effect == 'fade_in':
        alpha = int(255 * progress)
        return np.full((height, width), alpha, dtype=np.uint8)

    elif effect == 'ink_spread':
        """泼墨散开效果：墨滴砸下→快速扩散→毛边"""
        rng = np.random.RandomState(42)
        mask = np.zeros((height, width), dtype=np.float32)
        yy, xx = np.mgrid[0:height, 0:width]

        # 主墨滴：从中心快速扩散
        center_x, center_y = width * 0.5, height * 0.5
        dist_center = np.sqrt(((xx - center_x) / width)**2 + ((yy - center_y) / height)**2)

        # 非线性扩散：前期极快（泼墨冲击），后期慢（渗透）
        if progress < 0.15:
            # 冲击阶段：小范围高浓度
            splash_p = progress / 0.15
            radius = splash_p * 0.6
            mask = np.clip((radius - dist_center) * 15, 0, 1)
        elif progress < 0.4:
            # 扩散阶段：快速展开，带毛边
            spread_p = (progress - 0.15) / 0.25
            radius = 0.6 + spread_p * 0.5
            # 添加随机毛边
            noise = rng.uniform(-0.08, 0.08, (height, width))
            effective_dist = dist_center + noise
            mask = np.clip((radius - effective_dist) * 6, 0, 1)
        else:
            # 渗透阶段：边缘缓慢渗透
            bleed_p = (progress - 0.4) / 0.6
            radius = 1.1 + bleed_p * 0.3
            noise = rng.uniform(-0.12, 0.12, (height, width))
            effective_dist = dist_center + noise
            mask = np.clip((radius - effective_dist) * 4, 0, 1)

        # 叠加飞溅墨点（泼墨飞溅粒子）
        n_splashes = 20
        sx = rng.randint(0, width, n_splashes)
        sy = rng.randint(0, height, n_splashes)
        sr = rng.uniform(0.01, 0.06, n_splashes)  # 飞溅点半径
        st = rng.uniform(0.05, 0.5, n_splashes)    # 飞溅出现时间

        for i in range(n_splashes):
            if progress < st[i]:
                continue
            sp = min(1.0, (progress - st[i]) / 0.3)
            dist_splash = np.sqrt(((xx - sx[i])**2 + (yy - sy[i])**2))
            splash_r = sr[i] * max(width, height) * sp
            contribution = np.clip(1.0 - dist_splash / (splash_r + 1), 0, 1)
            mask = np.maximum(mask, contribution)

        return (np.clip(mask, 0, 1) * 255).astype(np.uint8)

    elif effect == 'ink_bleed':
        """墨迹渗透：从多个墨点渗透扩散，纸张纤维感"""
        rng = np.random.RandomState(42)
        mask = np.zeros((height, width), dtype=np.float32)
        yy, xx = np.mgrid[0:height, 0:width]

        # 多个渗透源（模拟泼墨后多个墨点同时渗透）
        n_sources = 8
        src_x = rng.uniform(0.2, 0.8, n_sources) * width
        src_y = rng.uniform(0.2, 0.8, n_sources) * height
        src_delay = rng.uniform(0, 0.3, n_sources)
        src_speed = rng.uniform(0.8, 1.3, n_sources)

        for i in range(n_sources):
            if progress < src_delay[i]:
                continue
            t = (progress - src_delay[i]) * src_speed[i]
            dist = np.sqrt(((xx - src_x[i]) / width)**2 + ((yy - src_y[i]) / height)**2)

            # 不规则渗透：不同方向速度不同（模拟纸张纤维）
            angle = np.arctan2(yy - src_y[i], xx - src_x[i])
            fiber_effect = 1.0 + 0.3 * np.sin(angle * 3 + i)
            effective_dist = dist / fiber_effect

            # 快速渗透后减速
            radius = min(1.0, t * 2.0) * 0.8
            contribution = np.clip((radius - effective_dist) * 5, 0, 1)

            # 添加毛边噪声
            noise = rng.normal(0, 0.04, (height, width))
            contribution = np.clip(contribution + noise, 0, 1)

            mask = np.maximum(mask, contribution)

        return (np.clip(mask, 0, 1) * 255).astype(np.uint8)

    elif effect == 'splash_ink':
        """真正泼墨：墨从一侧泼上去，带飞溅和拖尾"""
        rng = np.random.RandomState(42)
        mask = np.zeros((height, width), dtype=np.float32)
        yy, xx = np.mgrid[0:height, 0:width]

        # 主墨流：从左上到右下的泼洒方向
        if progress < 0.1:
            # 初始冲击点
            mask[:] = 0
        else:
            p = (progress - 0.1) / 0.9
            # 泼洒前沿：对角线方向移动
            front_x = p * width * 1.3
            front_y = p * height * 0.8

            # 墨流宽度（泼墨越远越散）
            flow_width = 30 + p * width * 0.4

            # 每个像素到泼洒线的距离
            # 泼洒线：从(0, height*0.2) 到 (front_x, front_y)
            line_len = math.sqrt(front_x**2 + (front_y - height*0.2)**2) + 1e-6
            # 点到线段距离
            dx = front_x
            dy = front_y - height * 0.2
            t_param = ((xx * dx + (yy - height*0.2) * dy) / (line_len**2))
            t_param = np.clip(t_param, 0, 1)
            proj_x = t_param * front_x
            proj_y = height * 0.2 + t_param * (front_y - height * 0.2)
            dist_to_line = np.sqrt((xx - proj_x)**2 + (yy - proj_y)**2)

            # 只有在泼洒前沿之后的区域才有墨
            behind_front = (t_param <= p + 0.1)
            in_flow = (dist_to_line < flow_width) & behind_front

            # 墨浓度：中心浓，边缘淡
            ink_density = np.clip(1.0 - dist_to_line / flow_width, 0, 1) ** 0.7

            # 添加泼墨飞溅（随机墨点）
            n_drops = 40
            drop_x = rng.uniform(0, width, n_drops)
            drop_y = rng.uniform(0, height, n_drops)
            drop_r = rng.uniform(3, 25, n_drops)
            drop_t = rng.uniform(0.1, 0.8, n_drops)  # 飞溅出现时间

            splash_mask = np.zeros_like(mask)
            for i in range(n_drops):
                if progress < drop_t[i]:
                    continue
                sp = min(1.0, (progress - drop_t[i]) / 0.15)
                dist_d = np.sqrt((xx - drop_x[i])**2 + (yy - drop_y[i])**2)
                splash_mask = np.maximum(splash_mask,
                    np.clip(1.0 - dist_d / (drop_r[i] * sp + 1), 0, 1) * 0.8)

            mask = np.where(in_flow, ink_density, 0)
            mask = np.maximum(mask, splash_mask)

            # 添加拖尾纹理（泼墨的不规则边缘）
            noise = rng.normal(0, 0.05, (height, width))
            mask = np.clip(mask + noise, 0, 1)

        return (np.clip(mask, 0, 1) * 255).astype(np.uint8)

    else:
        # 默认 fade_in
        return make_mask(width, height, progress, 'fade_in')


# ============================================================
# 视频合成
# ============================================================

def parse_position(pos_str, video_w, video_h, text_w, text_h):
    """解析位置参数"""
    if pos_str == 'center':
        return ((video_w - text_w) // 2, (video_h - text_h) // 2)
    elif pos_str == 'left':
        return (50, (video_h - text_h) // 2)
    elif pos_str == 'right':
        return (video_w - text_w - 50, (video_h - text_h) // 2)
    elif pos_str == 'top':
        return ((video_w - text_w) // 2, 50)
    elif pos_str == 'bottom':
        return ((video_w - text_w) // 2, video_h - text_h - 50)
    elif ',' in pos_str:
        parts = pos_str.split(',')
        x = int(parts[0].strip())
        y = int(parts[1].strip())
        return (x, y)
    else:
        return ((video_w - text_w) // 2, (video_h - text_h) // 2)


def create_calligraphy_animation(text_img, effect, duration, fps):
    """
    创建毛笔字浮现动画的帧生成器

    Args:
        text_img: PIL Image (RGBA)
        effect: 效果类型
        duration: 动画时长（秒）
        fps: 帧率

    Returns:
        generator yielding PIL Image frames
    """
    w, h = text_img.size
    n_frames = int(duration * fps)

    for i in range(n_frames):
        progress = (i + 1) / n_frames
        # ease_out 缓动函数，更自然
        progress = 1 - (1 - progress) ** 2

        mask = make_mask(w, h, progress, effect)

        # 应用 mask 到文字图片
        text_array = np.array(text_img)
        alpha = text_array[:, :, 3].astype(np.float32)
        mask_f = mask.astype(np.float32) / 255.0
        new_alpha = (alpha * mask_f).astype(np.uint8)

        text_array[:, :, 3] = new_alpha
        frame = Image.fromarray(text_array)
        yield frame


def overlay_calligraphy(
    video_path, output_path, text_img,
    effect, start_time, duration, hold_time,
    x, y, fps
):
    """
    将毛笔字动画叠加到视频上

    Args:
        video_path: 输入视频路径
        output_path: 输出视频路径
        text_img: PIL Image (RGBA) 渲染好的文字
        effect: 效果类型
        start_time: 开始时间（秒）
        duration: 浮现动画时长（秒）
        hold_time: 保持时长（秒）
        x, y: 位置
        fps: 帧率
    """
    print(f"🎬 加载视频: {video_path}")
    video = VideoFileClip(video_path)

    vw, vh = video.size
    tw, th = text_img.size

    # 解析位置
    pos = parse_position(x, vw, vh, tw, th)
    if y not in ('center', 'left', 'right', 'top', 'bottom') and ',' not in str(y):
        pos = (pos[0], int(y))
    elif ',' not in str(y):
        py = parse_position(y, vw, vh, tw, th)
        pos = (pos[0], py[1])
    print(f"📍 位置: ({pos[0]}, {pos[1]})")
    print(f"🎨 效果: {effect}")
    print(f"⏱️  开始: {start_time}s, 浮现: {duration}s, 保持: {hold_time}s")

    total_anim_duration = duration + hold_time

    # 生成动画帧序列
    frames = list(create_calligraphy_animation(text_img, effect, duration, fps))
    print(f"🖼️  生成 {len(frames)} 帧动画")

    # 如果有保持时间，补充保持帧（最后一帧重复）
    if hold_time > 0:
        hold_frames = int(hold_time * fps)
        for _ in range(hold_frames):
            frames.append(frames[-1])
        print(f"🖼️  补充 {hold_frames} 帧保持画面")

    # 将帧转为 numpy 数组序列
    frame_arrays = [np.array(f) for f in frames]

    # 创建动画 clip
    def make_frame(t):
        idx = min(int(t * fps), len(frame_arrays) - 1)
        return frame_arrays[idx]

    anim_duration = len(frame_arrays) / fps
    anim_clip = VideoClip(make_frame, duration=anim_duration)
    anim_clip = anim_clip.with_start(start_time).with_position(pos)

    # 合成
    print("🔧 合成视频...")
    result = CompositeVideoClip([video, anim_clip])

    result.write_videofile(
        output_path,
        fps=fps,
        codec='libx264',
        audio_codec='aac' if video.audio else None,
        preset='medium',
        threads=4,
        logger='bar'
    )

    # 清理
    video.close()
    print(f"✅ 输出: {output_path}")


# ============================================================
# 独立生成模式（无输入视频时生成纯色背景）
# ============================================================

def generate_standalone(text, font_path, fontsize, color, effect, duration, hold_time, fps, output_path):
    """无输入视频时，生成纯色背景的毛笔字浮现视频"""
    print("🎨 渲染文字...")
    text_img = render_text(text, font_path, fontsize, color)

    # 创建纯色背景视频
    w, h = max(text_img.width + 200, 1280), max(text_img.height + 200, 720)
    frames = list(create_calligraphy_animation(text_img, effect, duration, fps))

    if hold_time > 0:
        hold_frames = int(hold_time * fps)
        for _ in range(hold_frames):
            frames.append(frames[-1])

    frame_arrays = [np.array(f) for f in frames]

    # 创建带背景的帧
    bg_color = (255, 250, 240)  # 宣纸色

    def make_frame(t):
        idx = min(int(t * fps), len(frame_arrays) - 1)
        text_frame = frame_arrays[idx]

        bg = np.full((h, w, 3), bg_color, dtype=np.uint8)
        tw, th = text_frame.shape[1], text_frame.shape[0]
        x_offset = (w - tw) // 2
        y_offset = (h - th) // 2

        alpha = text_frame[:, :, 3:4].astype(np.float32) / 255.0
        text_rgb = text_frame[:, :, :3].astype(np.float32)
        bg_region = bg[y_offset:y_offset+th, x_offset:x_offset+tw].astype(np.float32)
        blended = (text_rgb * alpha + bg_region * (1 - alpha)).astype(np.uint8)
        bg[y_offset:y_offset+th, x_offset:x_offset+tw] = blended

        return bg

    anim_duration = len(frame_arrays) / fps
    clip = VideoClip(make_frame, duration=anim_duration)

    clip.write_videofile(
        output_path,
        fps=fps,
        codec='libx264',
        preset='medium',
        threads=4,
        logger='bar'
    )
    print(f"✅ 输出: {output_path}")


# ============================================================
# CLI
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description='kais-calligraphic — 视频毛笔字浮现动画生成器',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 基础用法
  python3 calligraphic_overlay.py --text "春眠不觉晓" --video bg.mp4 --output result.mp4

  # 水墨效果，自定义位置
  python3 calligraphic_overlay.py --text "大江东去" --video bg.mp4 --output result.mp4 \\
      --x 100 --y 200 --effect ink_spread --fontsize 120 --start 5

  # 无视频，独立生成（纯色背景）
  python3 calligraphic_overlay.py --text "天下第一" --output standalone.mp4 \\
      --effect ink_bleed --duration 4

效果类型: horizontal_wipe, vertical_wipe, fade_in, ink_spread, ink_bleed
        """
    )

    parser.add_argument('--text', required=True, help='要显示的文字内容（竖排用 \\n 换行）')
    parser.add_argument('--video', default=None, help='输入视频路径（省略则生成纯色背景视频）')
    parser.add_argument('--output', default='output.mp4', help='输出视频路径')
    parser.add_argument('--font', default=None, help='行书 TTF 字体路径（省略则自动检测）')
    parser.add_argument('--x', default='center', help='X 坐标（像素数或 center/left/right）')
    parser.add_argument('--y', default='center', help='Y 坐标（像素数或 center/top/bottom）')
    parser.add_argument('--start', type=float, default=0, help='动画开始时间（秒）')
    parser.add_argument('--duration', type=float, default=3, help='浮现动画时长（秒）')
    parser.add_argument('--hold', type=float, default=2, help='浮现后保持时长（秒，0=不保持）')
    parser.add_argument('--effect', default='horizontal_wipe',
                        choices=['horizontal_wipe', 'vertical_wipe', 'fade_in', 'ink_spread', 'ink_bleed', 'splash_ink'],
                        help='浮现效果类型')
    parser.add_argument('--fontsize', type=int, default=80, help='字体大小（像素）')
    parser.add_argument('--color', default='#1a1a1a', help='文字颜色（十六进制）')
    parser.add_argument('--fps', type=int, default=24, help='输出帧率')

    args = parser.parse_args()

    # 解析颜色
    color_hex = args.color.lstrip('#')
    color = tuple(int(color_hex[i:i+2], 16) for i in (0, 2, 4)) + (255,)

    # 查找字体
    font_path = args.font or find_calligraphy_font()
    if font_path:
        print(f"🔤 字体: {font_path}")
    else:
        print("⚠️  未找到中文字体，将使用系统默认字体（可能不支持中文）")
        print("   建议下载行书字体放到 ~/.openclaw/workspace/skills/kais-calligraphic/scripts/fonts/")
        font_path = ""

    if args.video and os.path.exists(args.video):
        # 有输入视频：叠加模式
        print("🎨 渲染文字...")
        text_img = render_text(args.text, font_path, args.fontsize, color)
        overlay_calligraphy(
            args.video, args.output, text_img,
            args.effect, args.start, args.duration, args.hold,
            args.x, args.y, args.fps
        )
    elif args.video:
        print(f"❌ 视频文件不存在: {args.video}")
        sys.exit(1)
    else:
        # 无输入视频：独立生成模式
        generate_standalone(
            args.text, font_path, args.fontsize, color,
            args.effect, args.duration, args.hold, args.fps, args.output
        )


if __name__ == '__main__':
    main()
