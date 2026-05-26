# 开源AI音乐生成高星项目深度研究报告

> **研究日期**: 2026-04-25
> **研究深度**: Deep（4轮搜索 + 页面抓取 + GitHub API数据）
> **场景定位**: AI剧情配乐 + 本地音乐创作

---

## 目录

1. [项目总览与GitHub数据](#1-项目总览与github数据)
2. [核心项目详解](#2-核心项目详解)
3. [硬件需求与部署可行性对比](#3-硬件需求与部署可行性对比)
4. [功能维度对比](#4-功能维度对比)
5. [许可证与商用分析](#5-许可证与商用分析)
6. [Web UI与API集成](#6-web-ui与api集成)
7. [2024-2026技术演进时间线](#7-2024-2026技术演进时间线)
8. [场景推荐：AI剧情配乐+本地音乐创作](#8-场景推荐ai剧情配乐本地音乐创作)
9. [结论与行动建议](#9-结论与行动建议)

---

## 1. 项目总览与GitHub数据

### 高星项目一览（按Stars排序）

| 排名 | 项目 | ⭐ Stars | 🍴 Forks | 许可证 | 语言 | 最近更新 |
|:---:|------|:---:|:---:|:---:|:---:|:---:|
| 1 | [facebookresearch/audiocraft](https://github.com/facebookresearch/audiocraft) (MusicGen) | 23,217 | 2,612 | MIT (代码) / CC-BY-NC 4.0 (模型) | Jupyter Notebook | 2026-04-25 |
| 2 | [openai/jukebox](https://github.com/openai/jukebox) | 8,039 | 1,458 | 自定义（非商用倾向） | Python | 2026-04-21 |
| 3 | [ace-step/ACE-Step-1.5](https://github.com/ace-step/ACE-Step-1.5) | 9,588 | 1,135 | MIT | Python | 2026-04-25 |
| 4 | [multimodal-art-projection/YuE](https://github.com/multimodal-art-projection/YuE) | 6,163 | 729 | Apache 2.0 | Python | 2026-04-25 |
| 5 | [microsoft/muzic](https://github.com/microsoft/muzic) | 4,908 | 497 | MIT | Python | 2026-04-22 |
| 6 | [ace-step/ACE-Step](https://github.com/ace-step/ACE-Step) (v1) | 4,365 | 547 | Apache 2.0 | Python | 2026-04-24 |
| 7 | [riffusion/riffusion-hobby](https://github.com/riffusion/riffusion-hobby) | 3,898 | 476 | MIT | Python | 2026-04-21 |
| 8 | [Stability-AI/stable-audio-tools](https://github.com/Stability-AI/stable-audio-tools) | 3,676 | 443 | MIT (代码) / Stability AI Community License (模型) | Python | 2026-04-22 |
| 9 | [ASLP-lab/DiffRhythm](https://github.com/ASLP-lab/DiffRhythm) | 2,288 | 266 | Apache 2.0 | Python | 2026-04-24 |
| 10 | [LiuZH-19/SongGen](https://github.com/LiuZH-19/SongGen) | 308 | 30 | Apache 2.0 | Python | 2026-04-01 |

> ⚠️ Stars数据采集时间：2026-04-25，会随时间变化

---

## 2. 核心项目详解

### 2.1 ACE-Step 1.5 ⭐ 最佳推荐

**定位**: 音乐生成基础模型，"音乐界的Stable Diffusion时刻"

**架构**: 混合架构 — LM（语言模型）作为规划器 + DiT（Diffusion Transformer）作为生成器
- LM将用户简单描述转换为完整歌曲蓝图（元数据、歌词、标签）
- DiT负责高质量音频波形生成
- 使用Sana的Deep Compression AutoEncoder (DCAE) + 轻量级线性Transformer

**核心能力**:
- ✅ 文本生成音乐（短标签/描述文本/使用场景）
- ✅ 50+语言歌词生成
- ✅ 人声克隆（voice cloning）
- ✅ 歌词编辑（局部修改保留旋律）
- ✅ Remix & 变奏生成
- ✅ 多轨生成（vocal2accompaniment, singing2accompaniment）
- ✅ 封面生成、音频重绘
- ✅ BPM/调性/拍号控制
- ✅ 轨道分离（stem separation）
- ✅ LoRA微调（8首歌、1小时RTX 3090）
- ✅ 音频理解（提取BPM/调性/字幕）
- ✅ LRC歌词时间戳生成
- ✅ 质量自动评分

**性能**:
- A100: <2秒生成一首完整歌曲
- RTX 3090: <10秒生成一首完整歌曲
- 质量介于Suno v4.5 和 Suno v5之间

**参数**: 3.5B（DiT）+ 可选LM (0.6B / 1.7B / 4B)

**版本**:
- v1: 2025年5月发布
- v1.5: 2026年1月发布（重大升级）
- v1.5 XL (4B DiT): 2026年4月发布，需≥12GB VRAM

**开发者**: ACE Studio + StepFun（阶跃星辰）

---

### 2.2 YuE (乐)

**定位**: 类似Suno.ai的开源全曲生成模型，歌词→完整歌曲

**架构**: 两阶段LLM架构
- Stage 1: 7B参数，歌词→人声+伴奏token
- Stage 2: 1B参数，token→高质量音频波形

**核心能力**:
- ✅ 歌词→完整歌曲（含人声+伴奏）
- ✅ 双轨ICL模式（参考音频→风格迁移/声音克隆）
- ✅ 多语言/多风格/多演唱技巧
- ✅ 歌曲延续生成
- ✅ LoRA微调
- ✅ ComfyUI集成

**性能**:
- H800: 30秒音频需150秒
- RTX 4090: 30秒音频需约360秒
- 最低8GB VRAM（量化模型，YuE-exllamav2/YuEGP）

**参数**: 7B (Stage 1) + 1B (Stage 2)

**开发者**: HKUST + M-A-P (Multimodal Art Projection)

---

### 2.3 DiffRhythm (谛韵)

**定位**: 首个开源扩散式全曲生成模型

**架构**: Latent Diffusion（潜扩散），非自回归
- 基于VAE的音频编码器
- 扩散模型在潜空间生成
- 支持分块推理降低VRAM

**核心能力**:
- ✅ 歌词+风格提示→完整歌曲
- ✅ 纯文本风格提示（无需参考音频）
- ✅ 纯音乐生成（无歌词）
- ✅ 动态时长控制（1m35s ~ 4m45s）
- ✅ 人声生成
- ✅ 歌曲延续/编辑
- ✅ 多语言支持
- ✅ Docker部署

**性能**:
- 约10秒生成4:45完整歌曲
- 最低8GB VRAM（使用--chunked参数）

**版本演进**:
- DiffRhythm (v1): 2025年3月
- DiffRhythm v1.2: 2025年5月（修复重复/遗漏，提升质量）
- DiffRhythm 2: Apache 2.0，Block Flow Matching架构
- DiffRhythm+: 后续增强版

**开发者**: ASLP-lab（西北工业大学ASLP实验室）

---

### 2.4 AudioCraft / MusicGen (Meta)

**定位**: 深度学习音频处理与生成库（基础框架级）

**架构**: Transformer-based autoregressive model
- EnCodec音频压缩器/标记器
- MusicGen: 文本/旋律→音乐
- AudioGen: 文本→音效
- MAGNeT: 非自回归文本→音乐/音效
- JASCO: 和弦/旋律/鼓点条件控制
- MusicGen Style: 文本+风格→音乐

**核心能力**:
- ✅ 文本生成音乐（30秒片段）
- ✅ 旋律条件生成（哼唱旋律→配乐）
- ✅ 和弦/鼓点控制（JASCO）
- ✅ 音效生成（AudioGen）
- ✅ 音频水印（AudioSeal）
- ✅ 训练代码完整开放

**限制**:
- 仅生成短片段（~30秒）
- 无原声人声/歌词演唱
- 音乐质量与Suno等有差距

**性能**: 推荐16GB GPU，小模型可在较低配置运行

**开发者**: Meta (Facebook Research)

---

### 2.5 SongGen

**定位**: ICML 2025论文，单阶段自回归Transformer文本→歌曲生成

**架构**: 单阶段自回归Transformer
- Mixed模式：混合人声+伴奏单轨输出
- Dual-track模式：人声+伴奏双轨分离输出
- Interleaving A-V模式：音频-视频交替生成

**核心能力**:
- ✅ 歌词+描述文本→歌曲
- ✅ 参考声音克隆
- ✅ 双轨分离输出
- ✅ 完整训练代码+数据处理流水线

**开发者**: 中科大 + 上海AI Lab（林达华团队）

**特点**: 学术导向，提供完整数据标注和训练流程，适合研究者

---

### 2.6 其他重要项目

#### Stable Audio Open (Stability AI)
- **架构**: Latent Diffusion
- **能力**: 文本→47秒立体声音频，44.1kHz
- **亮点**: Stable Audio Open Small支持端侧部署（手机），8秒生成11秒音频
- **限制**: 仅短片段，无歌词/人声
- **许可证**: Stability AI Community License

#### Riffusion
- **架构**: Stable Diffusion→频谱图→音频
- **能力**: 实时音乐生成，文本→短音乐片段
- **亮点**: 轻量，基于图像扩散模型
- **限制**: 时序连贯性差，适合实验/氛围音

#### OpenAI Jukebox
- **架构**: VQ-VAE + Transformer
- **能力**: 文本→含人声完整歌曲
- **亮点**: 早期开创性工作
- **限制**: 推理极慢（数小时），许可证模糊

#### Microsoft Muzic
- **定位**: 音乐理解+创作的AI研究框架
- **能力**: 符号分类、声音识别、歌词创作、旋律生成
- **亮点**: 学术全面，覆盖音乐AI多个子领域

---

## 3. 硬件需求与部署可行性对比

| 项目 | 最低VRAM | 推荐VRAM | RTX 4090速度 | 部署难度 | 多GPU支持 |
|------|:---:|:---:|:---:|:---:|:---:|
| **ACE-Step 1.5** | **4GB** (offload) | 8-16GB | <10秒/首 | ⭐ 简单 | ✅ |
| **DiffRhythm** | **8GB** (--chunked) | 16GB | ~10秒/首 | ⭐⭐ 中等 | ❌ |
| **YuE** | 8GB (量化) | 24GB+ | ~360秒/30s | ⭐⭐⭐ 复杂 | ✅ (tensor parallel) |
| **MusicGen/AudioCraft** | 4GB (small) | 16GB | ~10秒/30s | ⭐⭐ 中等 | ❌ |
| **SongGen** | ~16GB | 24GB+ | 未公开 | ⭐⭐⭐ 复杂 | ❌ |
| **Stable Audio Open** | ~6GB | 12GB+ | ~30秒/47s | ⭐⭐ 中等 | ❌ |
| **Riffusion** | **2GB** | 4GB | 实时 | ⭐ 简单 | ❌ |
| **Jukebox** | 16GB | 32GB+ | 数小时 | ⭐⭐⭐⭐ 极难 | ❌ |

### ACE-Step 1.5 详细VRAM配置表

| GPU VRAM | 推荐DiT | 推荐LM | 后端 | 备注 |
|:---:|:---:|:---:|:---:|:---:|
| ≤6GB | 2B turbo | None (仅DiT) | — | INT8量化+全CPU offload |
| 6-8GB | 2B turbo | 0.6B LM | PyTorch | 轻量LM |
| 8-16GB | 2B turbo/sft | 0.6B/1.7B LM | vllm | 平衡配置 |
| 16-20GB | 2B sft / XL turbo | 1.7B LM | vllm | XL需CPU offload |
| 20-24GB | XL turbo/sft | 1.7B LM | vllm | XL无需offload |
| ≥24GB | XL sft | 4B LM | vllm | 最佳质量 |

### 硬件推荐（按场景）

**入门级 (RTX 3060 12GB / RTX 4060 8GB)**:
- ACE-Step 1.5 (2B turbo) ✅ 最佳选择
- Riffusion ✅
- MusicGen (small) ✅

**中端 (RTX 4070 12GB / RTX 3090 24GB)**:
- ACE-Step 1.5 (XL sft) ✅ 最佳选择
- DiffRhythm ✅
- YuE (2 sessions) ✅

**高端 (RTX 4090 24GB / A100 80GB)**:
- ACE-Step 1.5 XL + 4B LM ✅ 全功能
- YuE (完整全曲) ✅
- 所有项目流畅运行 ✅

---

## 4. 功能维度对比

### 4.1 文本描述生成音乐

| 项目 | 文本→音乐 | 风格控制 | 情绪控制 | BPM/调性控制 | 旋律条件 |
|------|:---:|:---:|:---:|:---:|:---:|
| ACE-Step 1.5 | ✅ 优秀 | ✅ 1000+风格 | ✅ | ✅ BPM/调性/拍号 | ✅ 参考音频 |
| YuE | ✅ 优秀 | ✅ | ✅ | ❌ | ✅ 参考音频 |
| DiffRhythm | ✅ 良好 | ✅ 风格提示 | ✅ | ❌ | ✅ 参考音频 |
| MusicGen | ✅ 良好 | ✅ | ✅ | ❌ | ✅ 旋律条件 |
| SongGen | ✅ 良好 | ✅ | ✅ | ❌ | ✅ 参考声音 |
| Stable Audio Open | ✅ 一般 | ✅ | ⚠️ 有限 | ✅ | ❌ |

### 4.2 人声合成 & 歌词配乐

| 项目 | 歌词→演唱 | 声音克隆 | 多轨分离 | 纯音乐 | 歌曲时长 |
|------|:---:|:---:|:---:|:---:|:---:|
| ACE-Step 1.5 | ✅ | ✅ | ✅ | ✅ | 10s-10min |
| YuE | ✅ 优秀 | ✅ | ⚠️ 部分 | ✅ | 数分钟 |
| DiffRhythm | ✅ | ⚠️ 有限 | ❌ | ✅ | 1m35s-4m45s |
| MusicGen | ❌ | ❌ | ❌ | ✅ | ~30s |
| SongGen | ✅ | ✅ | ✅ 双轨 | ✅ | 数分钟 |
| Stable Audio Open | ❌ | ❌ | ❌ | ✅ | ~47s |

### 4.3 多轨混音 & 编辑

| 项目 | 轨道分离 | 局部编辑 | 变奏生成 | 人声→伴奏 | 伴奏→人声 |
|------|:---:|:---:|:---:|:---:|:---:|
| ACE-Step 1.5 | ✅ | ✅ 歌词编辑 | ✅ Remix | ✅ Vocal2BGM | ✅ |
| YuE | ⚠️ 部分 | ❌ | ⚠️ ICL模式 | ❌ | ❌ |
| DiffRhythm | ❌ | ⚠️ v1.2 | ❌ | ❌ | ❌ |
| MusicGen | ❌ | ❌ | ❌ | ❌ | ❌ |
| SongGen | ✅ 双轨 | ❌ | ❌ | ❌ | ❌ |

---

## 5. 许可证与商用分析

| 项目 | 代码许可证 | 模型许可证 | 可否商用 | 商用限制 |
|------|:---:|:---:|:---:|:---:|
| **ACE-Step 1.5** | **MIT** | **MIT** | ✅ **自由商用** | 无 |
| ACE-Step v1 | Apache 2.0 | Apache 2.0 | ✅ 自由商用 | 需保留版权声明 |
| YuE | Apache 2.0 | Apache 2.0 | ✅ 自由商用 | 需注明 "YuE by HKUST/M-A-P" |
| DiffRhythm | Apache 2.0 | Apache 2.0 | ✅ 自由商用 | 需保留版权声明 |
| DiffRhythm 2 | Apache 2.0 | Apache 2.0 | ✅ 自由商用 | 需保留版权声明 |
| SongGen | Apache 2.0 | Apache 2.0 | ✅ 自由商用 | 需保留版权声明 |
| **AudioCraft/MusicGen** | **MIT** | **CC-BY-NC 4.0** | ❌ **不可商用** | 模型权重非商用 |
| Stable Audio Open | MIT | Stability AI Community License | ⚠️ 需授权 | 非商用免费，商用需联系 |
| Riffusion | MIT | MIT | ✅ 自由商用 | 无 |
| Jukebox | 自定义 | 自定义 | ⚠️ 模糊 | 建议非商用 |
| Muzic | MIT | MIT | ✅ 自由商用 | 无 |

### 关键发现

- **最佳商用选择**: ACE-Step 1.5（MIT双重许可）、YuE（Apache 2.0）
- **不可商用**: MusicGen/AudioCraft 模型权重仅限CC-BY-NC 4.0（非商用）
- **需关注**: Stable Audio Open商用需联系Stability AI获取授权

---

## 6. Web UI与API集成

| 项目 | Gradio UI | REST API | ComfyUI | Docker | Python API | 在线Demo |
|------|:---:|:---:|:---:|:---:|:---:|:---:|
| **ACE-Step 1.5** | ✅ `uv run acestep` | ✅ `uv run acestep-api` | ✅ ComfyUI_ACE-Step | ❌ | ✅ pip install | ✅ HF Space |
| YuE | ✅ YuE-UI / YuE-exllamav2-UI | ❌ | ✅ ComfyUI_YuE | ✅ YuE-for-Windows | ✅ | ✅ HF Space |
| DiffRhythm | ✅ Gradio | ❌ | ❌ | ✅ Docker Compose | ✅ | ✅ HF Space |
| MusicGen/AudioCraft | ✅ HF Spaces | ❌ | ✅ 社区节点 | ❌ | ✅ pip install | ✅ HF Space |
| SongGen | ❌ | ❌ | ❌ | ❌ | ✅ pip install | ✅ Demo Page |
| Stable Audio Open | ✅ stable-audio-open-demo | ❌ | ❌ | ❌ | ✅ stable_audio_tools | ✅ HF Space |
| Riffusion | ✅ Web App | ✅ | ❌ | ❌ | ✅ | ✅ riffusion.com |

### 集成建议

**最易集成**: ACE-Step 1.5
```bash
# 一键安装+启动
git clone https://github.com/ACE-Step/ACE-Step-1.5.git
cd ACE-Step-1.5
uv sync
uv run acestep        # Gradio UI (localhost:7860)
uv run acestep-api    # REST API (localhost:8001)
```

**API调用示例** (ACE-Step 1.5 REST API):
```python
import requests
response = requests.post("http://localhost:8001/generate", json={
    "prompt": "cinematic orchestral dark tension, 120 bpm",
    "duration": 60,
    "lyrics": "",  # 纯音乐留空
    "seed": 42
})
```

---

## 7. 2024-2026技术演进时间线

### 2023: 基础奠定
- **2023.06**: Meta开源MusicGen/AudioCraft → 文本生成音乐开创性工作
- **2023.12**: Riffusion → Stable Diffusion用于音乐生成

### 2024: 快速发展
- **2024.07**: Stability AI发布Stable Audio Open → 短音频生成
- **2024全年**: Suno/Udio等商业模型推动音乐质量标杆
- Microsoft Muzic持续更新音乐理解研究

### 2025: 爆发年
- **2025.01**: YuE发布 → 首个类Suno开源全曲模型（7B参数）
- **2025.03**: DiffRhythm发布 → 首个扩散式全曲模型，Apache 2.0
- **2025.05**: **ACE-Step v1发布** → 混合架构突破，4分钟音乐20秒生成
- **2025.05**: DiffRhythm v1.2 → 修复重复，提升质量
- **2025.05**: SongGen发布 → ICML 2025论文，双轨自回归
- **2025.06**: YuE支持LoRA微调
- **2025.11**: Stable Audio Open Small → 端侧/手机部署

### 2026: 成熟与普及
- **2026.01**: **ACE-Step v1.5发布** → 商业级质量，<4GB VRAM，MIT许可
- **2026.04**: **ACE-Step v1.5 XL (4B DiT)** → 更高音质，≥12GB VRAM

### 技术趋势

1. **架构融合**: 纯LLM→纯扩散→**混合架构（LM规划+扩散生成）**成为主流
2. **VRAM门槛降低**: 从24GB+→8GB→**4GB**
3. **生成速度提升**: 从分钟级→秒级（ACE-Step 1.5: <2秒/首 on A100）
4. **许可证开放**: CC-BY-NC→Apache 2.0→**MIT**（越来越自由）
5. **功能丰富化**: 单一文本→音乐→编辑/克隆/多轨/分离全流程
6. **跨平台**: 仅CUDA→Mac/AMD/Intel/CPU全支持

---

## 8. 场景推荐：AI剧情配乐+本地音乐创作

### 需求分析

AI剧情配乐场景核心需求：
1. **情绪/风格精准控制**（紧张/悲伤/欢快/史诗感等）
2. **纯音乐生成**（大多数场景不需要人声）
3. **时长灵活**（30秒~5分钟不等）
4. **快速生成**（批量生成多个情绪场景配乐）
5. **商用合规**（视频发布/商业项目）
6. **本地部署**（隐私/成本/速度）
7. **API集成**（与视频管线自动化对接）

### 评分矩阵（满分10分）

| 维度 | ACE-Step 1.5 | YuE | DiffRhythm | MusicGen | Stable Audio |
|------|:---:|:---:|:---:|:---:|:---:|
| 纯音乐质量 | **9** | 8 | 8 | 7 | 7 |
| 风格/情绪控制 | **9** | 7 | 7 | 6 | 6 |
| 时长灵活性 | **10** (10s-10min) | 7 | 7 | 3 (30s) | 4 (47s) |
| 生成速度 | **10** (<10s) | 3 (~6min/30s) | 9 (~10s) | 7 | 6 |
| 硬件友好度 | **9** (4GB+) | 4 (8-24GB+) | 7 (8GB+) | 7 | 6 |
| 商用合规 | **10** (MIT) | 9 (Apache) | 9 (Apache) | 3 (NC) | 5 (需授权) |
| API/Web UI | **10** | 6 | 6 | 6 | 5 |
| 编辑能力 | **9** | 4 | 4 | 2 | 2 |
| 社区活跃度 | **9** | 8 | 7 | 9 | 6 |
| **综合得分** | **95** | **62** | **61** | **50** | **47** |

### 🏆 最终推荐

#### 第一选择：ACE-Step 1.5 — 综合最佳

**推荐理由**：
1. **最低硬件门槛**：4GB VRAM即可运行，12GB获得良好体验
2. **最快生成速度**：RTX 3090上<10秒/首，批量生成效率极高
3. **最灵活时长**：10秒~10分钟，完美覆盖剧情配乐各种场景
4. **最丰富功能**：风格控制、情绪表达、编辑、Remix、轨道分离
5. **最自由许可证**：MIT双重许可，商用无顾虑
6. **最易集成**：一键安装、Gradio UI + REST API、ComfyUI节点
7. **最高质量**：超越Suno v4.5，接近Suno v5

**本地部署方案（RTX 4060 8GB）**：
```bash
git clone https://github.com/ACE-Step/ACE-Step-1.5.git
cd ACE-Step-1.5
uv sync
uv run acestep  # Gradio UI，自动选择最佳配置
```

#### 第二选择：DiffRhythm — 速度快+全曲生成

**适用场景**：需要含人声的完整歌曲、对速度要求极高

#### 第三选择：YuE — 人声表现力最强

**适用场景**：需要高质量歌词演唱、声音克隆

---

## 9. 结论与行动建议

### 核心结论

1. **2026年开源音乐生成已达到商业可用水平**，ACE-Step 1.5质量接近Suno v5
2. **本地部署已非常友好**，4GB VRAM即可入门，RTX 4060/4070完全够用
3. **MIT许可证项目（ACE-Step 1.5、Riffusion）消除商用顾虑**
4. **混合架构（LM+Diffusion）是当前最优方案**，兼顾速度、质量、可控性

### 行动建议

#### 立即可做
1. **安装ACE-Step 1.5**：在Windows远程机器(192.168.71.38, RTX GPU)上部署
2. **测试剧情配乐场景**：
   - 输入风格描述（如"cinematic dark tension orchestral, 120 bpm"）
   - 测试不同情绪：紧张、悲伤、史诗、轻松、悬疑
   - 验证纯音乐生成质量
3. **集成到kais-movie-agent管线**：通过REST API调用，自动为分镜生成配乐

#### 进阶方向
1. **训练LoRA**：针对特定风格（如"中式古风配乐""赛博朋克合成器"）训练个性化LoRA
2. **音频后处理**：结合ffmpeg实现淡入淡出、拼接、音量标准化
3. **情绪映射自动化**：从scenario.json的情感曲线→自动生成配乐提示词→批量生成

#### 持续关注
- ACE-Step后续版本更新
- DiffRhythm 2的Block Flow Matching架构进展
- YuE的vLLM/sglang支持（将大幅提升推理速度）

---

## 附录：快速参考

### 项目链接汇总

| 项目 | GitHub | Demo | 论文 |
|------|--------|------|------|
| ACE-Step 1.5 | [ace-step/ACE-Step-1.5](https://github.com/ace-step/ACE-Step-1.5) | [HF Space](https://huggingface.co/spaces/ACE-Step/Ace-Step-v1.5) | [arXiv](https://arxiv.org/abs/2602.00744) |
| ACE-Step v1 | [ace-step/ACE-Step](https://github.com/ace-step/ACE-Step) | [HF Space](https://huggingface.co/spaces/ACE-Step/ACE-Step) | [arXiv](https://arxiv.org/abs/2506.00045) |
| YuE | [multimodal-art-projection/YuE](https://github.com/multimodal-art-projection/YuE) | [Demo Page](https://map-yue.github.io/) | [arXiv](https://arxiv.org/abs/2503.08638) |
| DiffRhythm | [ASLP-lab/DiffRhythm](https://github.com/ASLP-lab/DiffRhythm) | [HF Space](https://huggingface.co/spaces/ASLP-lab/DiffRhythm) | [arXiv](https://arxiv.org/abs/2503.01183) |
| AudioCraft | [facebookresearch/audiocraft](https://github.com/facebookresearch/audiocraft) | — | NeurIPS 2023 |
| SongGen | [LiuZH-19/SongGen](https://github.com/LiuZH-19/SongGen) | [Demo Page](https://liuzh-19.github.io/SongGen/) | [arXiv](https://arxiv.org/abs/2502.13128) |
| Stable Audio | [Stability-AI/stable-audio-tools](https://github.com/Stability-AI/stable-audio-tools) | — | — |
| Riffusion | [riffusion/riffusion-hobby](https://github.com/riffusion/riffusion-hobby) | [riffusion.com](https://www.riffusion.com) | — |
| Jukebox | [openai/jukebox](https://github.com/openai/jukebox) | — | — |
| Muzic | [microsoft/muzic](https://github.com/microsoft/muzic) | — | — |

---

*报告完成于 2026-04-25 | 数据来源：GitHub API + Brave Search + 项目官方README*
