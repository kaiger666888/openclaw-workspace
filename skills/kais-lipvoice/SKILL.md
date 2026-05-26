---
name: kais-lipVoice
version: 1.0.0
description: "AI唇形同步视频生成。基于LatentSync（字节跳动），将音频驱动人物视频实现唇形同步。支持本地部署、推理、批量处理、质量优化、ComfyUI集成。触发词：唇形同步、lip sync、LatentSync、口型同步、音画同步、配音对口型、lipVoice、口播视频、数字人说话、嘴型对齐"
---

# kais-lipVoice

AI 唇形同步视频生成技能。基于字节跳动开源的 LatentSync，将任意音频驱动人物视频实现精准唇形同步。

## 核心能力

- **唇形同步生成**：音频驱动，生成口型与语音精确匹配的视频
- **多版本支持**：v1.5（8GB显存/256×256）和 v1.6（18GB显存/512×512 高清）
- **多语言支持**：v1.5 优化了中文效果
- **多种部署方式**：命令行推理、Gradio Web界面、ComfyUI节点、Replicate API
- **批量处理**：支持批量视频+音频对处理

## 技术原理

LatentSync 是基于音频条件驱动的潜在扩散模型（Latent Diffusion），端到端架构：

1. **Whisper** 将音频转为梅尔频谱 → 音频嵌入向量
2. 音频嵌入通过**交叉注意力**注入 U-Net
3. 参考帧 + 遮罩帧与噪声潜变量**通道拼接**作为 U-Net 输入
4. **TREPA** 时间表示对齐机制解决扩散模型的时序抖动问题
5. 训练时使用 TREPA + LPIPS + SyncNet 三重损失优化

**核心优势**：直接在潜在空间建模音视频关联，无中间运动表征，比像素空间扩散更高效。

## 硬件要求

### 推理（仅需推理）

| 版本 | 最低显存 | 推荐显存 | 分辨率 | 备注 |
|------|---------|---------|--------|------|
| v1.5 | 8 GB | 10 GB | 256×256 | RTX 3060/4060 可用 |
| v1.6 | 18 GB | 24 GB | 512×512 | RTX 3090/4090 推荐 |

- **系统内存**：≥ 16 GB
- **硬盘空间**：~5 GB（模型权重 + 依赖）
- **CPU**：无特殊要求，多核有助于预处理

### 训练（需要训练时）

| 阶段 | 显存要求 | 备注 |
|------|---------|------|
| Stage 1 | 23 GB | v1.5 配置 |
| Stage 2 | 30 GB | 最优性能 |
| Stage 2 高效 | 20 GB | RTX 3090 可跑 |
| Stage 1 512p | 30 GB | v1.6 高清 |
| Stage 2 512p | 55 GB | v1.6 高清最优 |

## 部署指南

### Linux 部署（推荐）

```bash
# 1. 克隆项目
git clone https://github.com/bytedance/LatentSync.git
cd LatentSync

# 2. 一键安装依赖 + 下载模型
source setup_env.sh

# 3. 验证模型文件
ls checkpoints/
# 应看到: latentsync_unet.pt  whisper/tiny.pt

# 4. 运行推理
python gradio_app.py
# 或
./inference.sh
```

### Windows 部署

```powershell
# 1. 克隆项目（推荐用 GitHub Desktop）
git clone https://github.com/bytedance/LatentSync.git
cd LatentSync

# 2. 创建 conda 环境
conda create -n latentsync python=3.10
conda activate latentsync

# 3. 升级构建工具
python -m pip install --upgrade pip setuptools wheel

# 4. 安装依赖（手动加 torchaudio）
# 在 requirements.txt 第2行后加: torchaudio==2.5.1
pip install -r requirements.txt

# 5. 验证 CUDA
python -c "import torch; print(torch.cuda.is_available())"

# 6. 下载模型
mkdir checkpoints
huggingface-cli download ByteDance/LatentSync-1.6 whisper/tiny.pt --local-dir ./checkpoints
huggingface-cli download ByteDance/LatentSync-1.6 latentsync_unet.pt --local-dir ./checkpoints

# 7. 运行
python gradio_app.py
```

### ComfyUI 集成

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/ShmuelRonen/ComfyUI-LatentSyncWrapper.git
cd ComfyUI-LatentSyncWrapper
pip install -r requirements.txt
# 重启 ComfyUI，刷新浏览器
```

## 推理使用

### 命令行推理

```bash
python -m scripts.inference \
    --unet_config_path "configs/unet/stage2_512.yaml" \
    --inference_ckpt_path "checkpoints/latentsync_unet.pt" \
    --inference_steps 20 \
    --guidance_scale 1.5 \
    --enable_deepcache \
    --video_path "input_video.mp4" \
    --audio_path "input_audio.wav" \
    --video_out_path "output.mp4"
```

### 关键参数调优

| 参数 | 范围 | 默认 | 效果 |
|------|------|------|------|
| `--inference_steps` | 20-50 | 20 | ↑ 提升画质，↓ 降低速度 |
| `--guidance_scale` | 1.0-3.0 | 1.5 | ↑ 提升唇形精度，过高导致抖动 |
| `--enable_deepcache` | flag | 关 | 开启后加速推理（DeepCache） |
| `--unet_config_path` | - | stage2 | v1.5用stage2.yaml，v1.6用stage2_512.yaml |

**最佳实践**：
- 日常使用：`inference_steps=20, guidance_scale=1.5`（速度与质量平衡）
- 高质量输出：`inference_steps=35, guidance_scale=2.0`
- 快速预览：`inference_steps=20, guidance_scale=1.0 + --enable_deepcache`

### 输入要求

- **视频**：MP4 格式，建议 25fps，正面人脸清晰可见
- **音频**：WAV 格式，16000Hz 采样率
- **音频长度**：应与视频长度匹配或更短

### 批量处理

创建批量处理脚本 `batch_inference.sh`：

```bash
#!/bin/bash
# 批量唇形同步：遍历 pairs/ 目录下的 (视频, 音频) 对
# 命名规则: pairs/video1.mp4 + pairs/video1.wav → output/video1.mp4

mkdir -p output

for video in pairs/*.mp4; do
    name=$(basename "$video" .mp4)
    audio="pairs/${name}.wav"
    if [ -f "$audio" ]; then
        echo "Processing: $name"
        python -m scripts.inference \
            --unet_config_path "configs/unet/stage2_512.yaml" \
            --inference_ckpt_path "checkpoints/latentsync_unet.pt" \
            --inference_steps 20 \
            --guidance_scale 1.5 \
            --enable_deepcache \
            --video_path "$video" \
            --audio_path "$audio" \
            --video_out_path "output/${name}.mp4"
    fi
done
```

## 云端 API

### Replicate API

无需本地 GPU，直接调用：

```bash
# 安装
pip install replicate

# 调用
replicate run bytedance/latentsync \
  video="https://example.com/input.mp4" \
  audio="https://example.com/audio.wav"
```

## 版本对比

| 特性 | v1.5 | v1.6 |
|------|------|------|
| 分辨率 | 256×256 | 512×512 |
| 最低显存 | 8 GB | 18 GB |
| 时间一致性 | 基础 | 改进 |
| 中文效果 | 优化 | 优化 |
| 模糊问题 | 有 | 显著缓解 |
| HF仓库 | ByteDance/LatentSync-1.5 | ByteDance/LatentSync-1.6 |

## 与其他工具对比

| 工具 | 方法 | 画质 | 时序一致性 | 显存 | 开源 |
|------|------|------|-----------|------|------|
| **LatentSync** | 潜在扩散 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 8-18GB | ✅ |
| Wav2Lip | GAN | ⭐⭐⭐ | ⭐⭐⭐ | ~2GB | ✅ |
| SyncTalk | 扩散 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ~8GB | ✅ |
| MuseTalk | 扩散+Motion | ⭐⭐⭐⭐ | ⭐⭐⭐ | ~8GB | ✅ |
| HeyGen | 商业 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 云端 | ❌ |
| D-ID | 商业 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 云端 | ❌ |

**LatentSync 优势**：画质最高、完全开源、中文优化、端到端无中间表征。

## 常见问题

### Q: 推理时 OOM（显存不足）
- 使用 v1.5 模型（8GB 可跑）
- 加 `--enable_deepcache` 减少显存占用
- 减少 `--inference_steps`

### Q: 中文唇形效果差
- 使用 v1.5 或 v1.6（都优化了中文）
- 确保音频采样率为 16000Hz

### Q: 生成视频有抖动
- 降低 `guidance_scale`（1.0-1.5）
- 使用 v1.6（改进了时间一致性）

### Q: 结果模糊
- 使用 v1.6（512×512 分辨率，专门解决模糊问题）
- 提高 `inference_steps` 到 30-40

### Q: 人脸检测失败
- 确保视频中人脸正面清晰、光线充足
- 避免侧脸、遮挡、多人场景

## 相关链接

- **GitHub**: https://github.com/bytedance/LatentSync
- **论文**: https://arxiv.org/abs/2412.09262
- **模型 v1.6**: https://huggingface.co/ByteDance/LatentSync-1.6
- **模型 v1.5**: https://huggingface.co/ByteDance/LatentSync-1.5
- **在线Demo**: https://huggingface.co/spaces/fffiloni/LatentSync
- **Replicate**: https://replicate.com/lucataco/latentsync
- **ComfyUI节点**: https://github.com/ShmuelRonen/ComfyUI-LatentSyncWrapper

## 工作流程

当用户请求唇形同步任务时：

1. **确认输入**：获取视频文件和目标音频文件路径
2. **选择版本**：根据 GPU 显存选择 v1.5 或 v1.6
3. **参数配置**：根据需求选择质量/速度平衡参数
4. **执行推理**：通过命令行或 API 调用
5. **质量检查**：检查输出视频的唇形同步效果
6. **交付结果**：返回生成的视频文件路径
