---
name: kais-vocal
version: 1.0.0
description: "AI演唱会/福音音乐MV全流程制作管线。从一张图+一段音乐生成完整对口型演唱会视频。触发词：演唱会视频, vocal video, 福音MV, 对口型视频, AI演唱会, 九宫格MV, concert video, lip sync, vocal制作, 做个MV, 演唱会制作, 福音视频, 合唱视频, kais-vocal, vocal agent, 音乐MV, 歌曲视频, 舞台视频"
---

# kais-vocal — AI 演唱会 MV 全流程制作管线

从一张九宫格参考图 + 一首 AI 生成音乐，自动产出完整对口型演唱会视频。

## 核心工作流

```
用户输入（主题/台词/曲风）
  → Phase 1: 音乐生成（kais-song-agent）
  → Phase 2: 九宫格分镜图（kais-jimeng）
  → Phase 3: 音频切片
  → Phase 4: 批量视频生成（即梦 Seedance 2.0）
  → Phase 5: 后期合成
  → 交付成品 MP4
```

## Phase 1: 音乐生成

<!-- FREEDOM:high -->

**引擎**：通过 `kais-song-agent` 调用 ACE-Step 1.5

### 输入要求

用户需提供：
- **原始台词/歌词**：要对口型演唱的文本内容
- **曲风描述**：音乐风格（哥特叙事风、流行、说唱、合唱等）
- **场景氛围**：演唱会/福音活动/音乐节等

### Prompt 写作公式

```
根据下方的曲风与要求，基于原对白扩展（原对白内容要保证90%不改变），生成一首歌曲。

曲风与要求：[具体曲风描述]，带有[人声特征]，配以[乐器编排]，[节奏特征]，采用标准的音乐结构，副歌部分[合唱描述]。

原对白：
[台词内容逐行写入]
```

**关键提示**：必须加上「基于原对白扩展，保留 90% 原词不变」，锁住原版韵味。

### 交付物
- 完整 MP3/WAV 音频
- 歌词文本（带段落标记）
- 时长信息

用户确认音乐满意后进入 Phase 2。

## Phase 2: 九宫格分镜图

<!-- FREEDOM:high -->

**引擎**：通过 `kais-jimeng` 调用即梦图片生成

### 设计原则

九宫格分镜图是整支 MV 的核心视觉参考，一张图内布局多视角画面：

| 位置 | 推荐镜头 |
|------|---------|
| 1 (左上) | 舞台全景/远景 |
| 2 (中上) | 主唱特写（正面） |
| 3 (右上) | 合唱团群像 |
| 4 (左中) | 侧面特写 |
| 5 (中心) | 主视觉/封面镜头 |
| 6 (右中) | 乐器/乐队局部 |
| 7 (左下) | 观众席远景 |
| 8 (中下) | 主唱动态（走动/互动） |
| 9 (右下) | 全场氛围/灯光 |

### Prompt 模板

```
一张九宫格分镜参考图，[场景描述]，9个格子中分别展示不同视角的画面：
1. [镜头1描述]
2. [镜头2描述]
...
9. [镜头9描述]
整体风格：[美术风格]，电影级光影，[色调描述]
```

### 即梦图片生成参数
- 模型：`jimeng-5.0`
- 比例：`1:1`（九宫格正方形最佳）
- 分辨率：`2k` 或更高

### 交付物
- 九宫格参考图 PNG（本地保存到 `output/<project>/storyboard-grid.png`）

用户确认视觉风格后进入 Phase 3。

## Phase 3: 音频切片

<!-- FREEDOM:low -->

将完整音频按歌词段落切成 ≤15 秒的片段，匹配 Seedance 2.0 单次生成上限。

### 切片规则

1. **按歌词段落切**：每段切片必须包含完整的一句/一段歌词
2. **时长上限**：单段 ≤ 15 秒
3. **命名规范**：`slice_01.wav`, `slice_02.wav`, ...
4. **记录映射**：生成 `slices.json` 保存每段的歌词内容、时长、顺序

### 切片脚本

```bash
# 使用 ffmpeg 切片
# slices.json 格式：
# [
#   { "index": 1, "file": "slice_01.wav", "duration": 12.5, "lyrics": "台词内容..." },
#   { "index": 2, "file": "slice_02.wav", "duration": 14.8, "lyrics": "台词内容..." }
# ]
```

### 交付物
- `output/<project>/slices/` 目录下所有音频切片
- `output/<project>/slices.json` 切片映射文件

## Phase 4: 批量视频生成

<!-- FREEDOM:low -->

**引擎**：即梦 Seedance 2.0（通过 `kais-jimeng` 客户端）

### 核心参数

| 参数 | 值 | 说明 |
|------|-----|------|
| model | `jimeng-video-seedance-2.0` | 2.0 模型，对口型能力强 |
| ratio | `16:9` | 电影感横屏 |
| duration | 与切片时长一致 | 四舍五入匹配 |

### Prompt 结构

```
[场景描述]，多层次合唱，对口型演唱视频生成，
背景音乐百分百还原@音频，口型百分百同步音频中的歌词，
音色、语速、歌词内容完全相同不要改变。

根据参考音频 @音频 歌词和演唱顺序智能切镜匹配 @分镜图 分镜画面，
参考音频中的歌词内容以及演唱顺序如下：
主唱歌词内容：[第一段歌词]
合唱团歌词内容：[合唱部分]
观众歌词内容：[观众部分]
```

### 批量生成流程

对每个音频切片执行：

```javascript
// 使用 kais-jimeng 客户端
const jimeng = new JimengClient({ sessionId });
const videoUrl = await jimeng.submitSeedanceTask(
  prompt,        // 包含对应段歌词的 prompt
  [storyboardGridPath, slicePath],  // 九宫格图 + 当前切片音频
  {
    model: "jimeng-video-seedance-2.0",
    ratio: "16:9",
    duration: sliceDuration,  // 与当前切片时长一致
    timeoutMs: 600_000  // 10 分钟超时
  }
);
```

### QPS 限流

即梦 API 限制 QPS=1，每次请求间隔 ≥ 1.05 秒。`kais-jimeng` 客户端已内置令牌桶限流器，自动处理。

### 交付物
- `output/<project>/videos/` 目录下所有视频片段
- `output/<project>/video-map.json` 视频与切片的映射

## Phase 5: 后期合成

<!-- FREEDOM:low -->

将所有视频片段与原始音频合成最终 MV。

### 合成原则

1. **舍弃视频自带音频**：只保留原始切片音频
2. **手动对齐**：微调片段时长、卡点剪辑
3. **变速处理**：必要时通过 ffmpeg 变速微调（±5% 以内）

### 合成脚本

```bash
# 1. 拼接所有视频片段（静音）
ffmpeg -f concat -safe 0 -i concat_list.txt -c:v libx264 -an temp_video.mp4

# 2. 合并原始完整音频
ffmpeg -i temp_video.mp4 -i original_audio.mp3 -c:v copy -c:a aac -shortest output.mp4
```

### 交付物
- `output/<project>/final/<project-name>.mp4` — 最终成品
- `output/<project>/final/making-of.md` — 制作记录

## 项目目录结构

```
output/<project-name>/
├── audio/                    # Phase 1: 完整音乐
│   ├── original.mp3
│   └── lyrics.txt
├── storyboard-grid.png       # Phase 2: 九宫格分镜图
├── slices/                   # Phase 3: 音频切片
│   ├── slice_01.wav
│   ├── slice_02.wav
│   └── ...
├── slices.json               # 切片映射
├── videos/                   # Phase 4: 生成的视频片段
│   ├── clip_01.mp4
│   ├── clip_02.mp4
│   └── ...
├── video-map.json            # 视频映射
└── final/                    # Phase 5: 最终成品
    ├── <project-name>.mp4
    └── making-of.md
```

## 与 kais-aigc-platform 集成

### 依赖 skill

| Skill | 用途 | 调用方式 |
|-------|------|---------|
| `kais-song-agent` | AI 音乐创作（ACE-Step 1.5） | sessions_spawn 或直接调用 Kais Hub |
| `kais-jimeng` | 图片生成 + 视频生成（即梦 API） | JimengClient 直接调用 |
| `kais-gold-team` | GPU 加速（可选） | Kais Hub 管线 |

### 引擎能力映射

| 文章原始工具 | kais-aigc-platform 对应 |
|-------------|------------------------|
| tunee.ai / Mureka V9 | `kais-song-agent` (ACE-Step 1.5) |
| Image2（九宫格） | `kais-jimeng` 图片生成 |
| 即梦 AI 2.0（视频） | `kais-jimeng` Seedance 2.0 (`submitSeedanceTask`) |
| 剪映（后期剪辑） | `ffmpeg` 自动合成 |

### 关键优势

1. **完全自动化**：从音乐到成片全管线可自动执行
2. **QPS 限流内置**：jimeng-client 自带令牌桶，无需手动控制
3. **断点续传**：项目目录结构支持从任意 Phase 恢复
4. **审核门控**：每个 Phase 完成后可暂停等用户确认

## 限制与注意

- Seedance 2.0 单次最长 15 秒，完整歌曲必须切片处理
- 即梦 API QPS=1，批量生成需排队（8 段切片约 8-15 分钟）
- AI 视频偶有跑调/节奏偏移，后期需微调
- 口型同步质量取决于音频清晰度和歌词标注精确度
- 九宫格图的视觉质量直接影响所有片段的画面一致性
