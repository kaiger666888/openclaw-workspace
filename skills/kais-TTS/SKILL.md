---
name: kais-TTS
version: 1.0.0
description: "ChatTTS 语音合成调研与部署指南。覆盖 RTX 3060 Ti Windows 部署、音质优化、增强版方案对比、竞品横向评测。触发词：ChatTTS, 语音合成, TTS, 文字转语音, 部署ChatTTS, 语音生成, 语音克隆, AI配音"
---

# kais-ChatTTS

ChatTTS 深度调研与部署指南，专注于 RTX 3060 Ti (8GB) Windows 环境。

## 项目概述

### 基本信息
- **仓库**: https://github.com/2noise/ChatTTS
- **许可**: AGPLv3+ (代码) + CC BY-NC 4.0 (模型)
- **语言**: 中文 + 英文（英文仍为实验性）
- **开源版**: 4万小时预训练模型（未 SFT），官方故意加入高频噪声 + MP3 压缩降质
- **官方声明**: 仅供学术研究，禁止商业用途

### 核心架构
- **训练数据**: 10万+ 小时中英文音频，开源版为 4万小时预训练
- **模型组件**: DVAE 编码器 + 自回归语言模型 + Vocos 声码器
- **输出**: 24kHz 采样率
- **特色**: 对话场景优化，支持多说话人、笑声/停顿/语气词细粒度控制

### 质量限制（重要）
官方在开源模型中**故意降质**：
1. 训练时加入高频噪声
2. 使用 MP3 格式压缩音频质量
3. 目的：防止恶意使用
4. 结论：开源版音质天花板有限，追求高音质需考虑其他方案或后处理增强

---

## RTX 3060 Ti Windows 部署指南

### 硬件需求
- **GPU**: RTX 3060 Ti 8GB VRAM（最低 4GB）
- **系统内存**: 16GB+
- **存储**: 10GB+（模型文件）
- **性能参考**: 4090 约 7 tokens/s，RTF ≈ 0.3；3060 Ti 预计 4-5 tokens/s

### 环境配置

```powershell
# 1. 创建 conda 环境
conda create -n chattts python=3.11
conda activate chattts

# 2. 安装 PyTorch（CUDA 12.1）
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu121

# 3. 克隆项目
git clone https://github.com/2noise/ChatTTS
cd ChatTTS

# 4. 安装依赖
pip install --upgrade -r requirements.txt

# 5. 可选加速（推荐）
pip install safetensors vllm==0.2.7
```

### ⚠️ 不要安装
- **TransformerEngine**: 目前无法正常运行（#672 #676）
- **FlashAttention-2**: 会反而降低生成速度

### 国内模型下载（HuggingFace 不通畅时）
```python
from modelscope import snapshot_download
model_dir = snapshot_download('zlj2546/ChatTTS')

# 使用本地模型
import ChatTTS
chat = ChatTTS.Chat()
chat.load_models('custom', custom_path=model_dir)
```

### 启动方式

```powershell
# WebUI（推荐首次使用）
python examples/web/webui.py

# 命令行
python examples/cmd/run.py "你好世界" "Hello World"
```

### 显存优化策略（8GB 关键）

1. **compile=True**: `chat.load(compile=True)` 启用 torch.compile 加速推理
2. **短文本分段**: 长文本拆分为 30 秒以内段落分别生成
3. **关闭不必要的后台程序**: 释放系统内存，减少 GPU 换页
4. **FP16 推理**: PyTorch 默认使用 FP16，无需额外配置
5. **batch_size=1**: 不要批量推理，逐条生成节省显存

---

## 音质提升指南

### 参数调优

| 参数 | 推荐值 | 说明 |
|------|--------|------|
| `temperature` | 0.0003 ~ 0.3 | 越低越稳定，太高会杂音/异常 |
| `top_P` | 0.7 | 情感相关性控制 |
| `top_K` | 20 | 情感相似性控制 |

```python
params_infer_code = ChatTTS.Chat.InferCodeParams(
    spk_emb=rand_spk,
    temperature=0.0003,
    top_P=0.7,
    top_K=20,
)
```

### 音色控制（最关键的质量因素）

**优先级**: .pt 音色文件 > 音色码字符串 > seed 值

```python
# 1. 采样并保存音色
rand_spk = chat.sample_random_speaker()
torch.save(rand_spk, "my_voice.pt")  # 保存以备复用

# 2. 加载已保存的音色
spk = torch.load("my_voice.pt", map_location=torch.device('cpu')).detach()

# 3. 使用音色码（字符串形式，更稳定）
from ChatTTS.utils import compress_and_encode
spk_emb_str = compress_and_encode(spk)
params_infer_code = ChatTTS.Chat.InferCodeParams(spk_emb=spk_emb_str)
```

**音色资源**:
- [ChatTTS_Speaker](https://github.com/6drf21e/ChatTTS_Speaker): 音色打标 + 稳定性评估
- [ttslist.aiqbh.com](http://ttslist.aiqbh.com/): 音色种子示例库

### 文本控制标记

**句子级控制**（通过 RefineText prompt）:
- `[oral_0~9]`: 口语化程度，0=正式，9=非常口语
- `[laugh_0~2]`: 笑声概率，0=无，2=频繁
- `[break_0~7]`: 停顿时长，0=最短，7=最长

**词级控制**（skip_refine_text=True 时直接插入文本）:
- `[uv_break]`: 插入停顿
- `[laugh]`: 插入笑声
- `[lbreak]`: 长停顿

```python
# 句子级
params_refine_text = ChatTTS.Chat.RefineTextParams(
    prompt='[oral_2][laugh_0][break_6]',
)

# 词级
text = '什么是[uv_break]你最喜欢的食物？[laugh][lbreak]'
wavs = chat.infer(text, skip_refine_text=True,
                  params_refine_text=params_refine_text,
                  params_infer_code=params_infer_code)
```

### 后处理增强方案

1. **Speech-AI-Forge** (最推荐): 人声增强 (ResembleEnhance) + 背景降噪
   - Windows 整合包解压即用
   - 内置 27 个 ChatTTS 音色
   - 支持速度/音调/音量调节 + 响度均衡
2. **ChatTTS-Enhanced**: 批量处理 + SRT 字幕导出
3. **ChatTTS-OpenVoice**: 配合 OpenVoice 做声音克隆

---

## 增强版项目对比

| 项目 | Star | 核心亮点 | 适合场景 |
|------|------|----------|----------|
| [Speech-AI-Forge](https://github.com/lenML/Speech-AI-Forge) | ⭐最高 | 多模型支持、人声增强、API Server、WebUI、Windows整合包 | **首选**，一站式 TTS 工作台 |
| [ChatTTS-ui](https://github.com/jianchang512/ChatTTS-ui) | 高 | API 接口、第三方集成 | 需要程序化调用 |
| [ChatTTS_colab](https://github.com/6drf21e/ChatTTS_colab) | 中 | 流式输出、长音频、分角色阅读 | Colab 免费体验 |
| [ChatTTS-Enhanced](https://github.com/CCmahua/ChatTTS-Enhanced) | 中 | 批量处理、SRT 导出 | 视频配音批量制作 |
| [ChatTTS-OpenVoice](https://github.com/HKoon/ChatTTS-OpenVoice) | 中 | 声音克隆 | 需要克隆特定人声 |
| [ChatTTS-manager](https://github.com/MaterialShadow/ChatTTS-manager) | 中 | 音色管理系统 | 需要管理大量音色 |
| [ComfyUI-ChatTTS](https://github.com/AIFSH/ComfyUI-ChatTTS) | 低 | ComfyUI 工作流节点 | ComfyUI 用户 |

### 推荐：Speech-AI-Forge

如果目标是高质量 TTS 输出，**强烈推荐直接用 Speech-AI-Forge** 而非原版 ChatTTS：

```powershell
# Windows: 直接下载整合包解压即用
# https://github.com/lenML/Speech-AI-Forge/releases

# 或从源码部署
git clone https://github.com/lenML/Speech-AI-Forge
cd Speech-AI-Forge
pip install -r requirements.txt
python -m scripts.download_models --source=modelscope --models=ChatTTS,resemble-enhance
python webui.py
```

支持的 TTS 模型（远不止 ChatTTS）：Index-TTS、Qwen3-TTS、FishSpeech、CosyVoice v2/v3、F5-TTS、GPT-SoVITS、Spark-TTS、FireRedTTS

---

## 竞品横向对比

| 模型 | 语言 | 音质 | 速度 | 显存需求 | 许可 | 特点 |
|------|------|------|------|----------|------|------|
| **ChatTTS** | 中/英 | ⭐⭐⭐ | 慢 | 4GB+ | CC BY-NC | 对话场景优化，细粒度韵律控制 |
| **CosyVoice v2/v3** | 中/英/日/粤/韩 | ⭐⭐⭐⭐⭐ | 中 | 4GB+ | Apache 2.0 | **音质最佳**，阿里出品，零样本克隆 |
| **Fish-speech 1.5** | 中/英/日/韩 | ⭐⭐⭐⭐ | 快 | 2GB+ | MIT | 质量高、速度快、多语言 |
| **GPT-SoVITS** | 中/英/日/韩/粤 | ⭐⭐⭐⭐ | 快 | 4GB+ | MIT | 声音克隆强，社区活跃 |
| **Index-TTS 2** | 中/英 | ⭐⭐⭐⭐ | 快 | 4GB+ | MIT | 参考音频克隆效果好 |
| **Qwen3-TTS** | 中/英 | ⭐⭐⭐⭐ | 中 | 4GB+ | 通义 | 通义出品，支持声音设计 |
| **F5-TTS** | 中/英 | ⭐⭐⭐ | 快 | 4GB+ | CC-BY-4.0 | 零样本克隆，E2E 架构 |
| **MeloTTS** | 中/英/日/韩 | ⭐⭐⭐ | 极快 | 1GB+ | MIT | **速度最快**，低资源友好 |
| **Bark** | 多语言 | ⭐⭐ | 慢 | 4GB+ | MIT | 非对话型，效果偏机械 |
| **XTTSv2** | 多语言 | ⭐⭐⭐ | 中 | 4GB+ | AGPL | Coqui 出品，多语言克隆 |

### RTX 3060 Ti 推荐方案

**追求最佳音质**: CosyVoice v2/v3（Apache 2.0 可商用）
**追求对话自然度**: ChatTTS + Speech-AI-Forge 人声增强
**追求速度**: MeloTTS 或 Fish-speech
**追求声音克隆**: GPT-SoVITS 或 Index-TTS 2
**一站式方案**: Speech-AI-Forge（支持上述大部分模型切换）

---

## API 集成方案

### 原版 ChatTTS API

```python
import ChatTTS
import torch
import torchaudio

chat = ChatTTS.Chat()
chat.load(compile=True)

# 单次推理
wavs = chat.infer(["要转换的文本"])
torchaudio.save("output.wav", torch.from_numpy(wavs[0]).unsqueeze(0), 24000)
```

### Speech-AI-Forge API Server

```powershell
# 启动 API 服务
python launch.py
# API 文档: http://localhost:7870/docs
```

### ChatTTS-ui API

提供 RESTful API，可直接在第三方应用中调用。

---

## 常见问题 FAQ

### Q: 生成的音频有杂音/异常？
**A**: 这是自回归模型通病。解决方案：降低 temperature（0.0003）、多次采样选最佳、使用后处理增强（ResembleEnhance）。

### Q: 中文标点报错？
**A**: 修改 `ChatTTS/utils/infer_utils.py` 第 103 行 character_map，添加缺失标点：
```python
character_map = {
    '…': '', '—': ',', '＿': ',', '？': ',',
}
```

### Q: 显存不足（8GB）？
**A**: 确保关闭其他 GPU 程序，使用短文本分段生成，compile=True 加速。

### Q: 模型下载失败？
**A**: 使用 ModelScope 替代 HuggingFace，或手动下载模型文件配置本地路径。

### Q: 音色每次不一样？
**A**: 必须保存并复用 spk_emb。用 seed 值每次效果有显著差异，优先用 .pt 文件或音色码。

### Q: 英文效果差？
**A**: 官方说明英文仍为实验性，中文效果远好于英文。

### Q: 如何商业化使用？
**A**: ChatTTS 开源模型 CC BY-NC 4.0 禁止商用。如需商用，建议使用 CosyVoice（Apache 2.0）或 Fish-speech（MIT）。

---

## 快速决策树

```
需要 TTS？
├─ 商用？
│  └─ 是 → CosyVoice / Fish-speech（宽松许可）
│  └─ 否 ↓
├─ 追求极致音质？
│  └─ CosyVoice v2/v3
├─ 对话/播客场景？
│  └─ ChatTTS + Speech-AI-Forge 增强
├─ 声音克隆？
│  └─ GPT-SoVITS / Index-TTS 2
├─ 低资源/快速？
│  └─ MeloTTS
└─ 什么都想试？
   └─ Speech-AI-Forge（一站式多模型）
```

---

## 参考资源

- 官方仓库: https://github.com/2noise/ChatTTS
- 资源汇总: https://github.com/libukai/Awesome-ChatTTS
- Speech-AI-Forge: https://github.com/lenML/Speech-AI-Forge
- 音色示例: http://ttslist.aiqbh.com/
- ModelScope 模型: https://www.modelscope.cn/models/pengzhendong/ChatTTS
- B站部署教程: https://www.bilibili.com/video/BV1Ui421v7JU/
