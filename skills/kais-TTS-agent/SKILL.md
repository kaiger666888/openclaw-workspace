---
name: kais-TTS-agent
version: 1.0.0
description: "TTS 拟人化语音创作技巧。引擎：Speech-AI-Forge (Qwen3-TTS 1.7B)，控制框架：kais-gold-team/kais-hub。专注情感标签、韵律控制、自然语言指令等创作方法论，让合成语音更接近真人表达。触发词：TTS生成, 语音生成, 拟人化语音, 情感TTS, AI配音, kais-tts, TTS agent, 语音合成, express speech, emotional TTS, 旁白生成, 角色配音, TTS技巧, 语音创作"
---

# kais-TTS-agent

TTS 拟人化语音创作技巧指南。让 AI 合成语音不再"机器味"，而是像真人一样有情感、有节奏、有呼吸。

## 引擎与控制框架

- **TTS 引擎**: Speech-AI-Forge（fork 版），Qwen3-TTS-12Hz-1.7B
  - 模型变体：CustomVoice（9种预设音色）、VoiceDesign（自然语言创建音色）、Base（声音克隆）
  - API 端点：`POST /v2/tts`
- **任务编排**: [kais-gold-team/kais-hub](https://github.com/kaiger666888/kais-gold-team) — 双机分布式系统
  - Control Node（低配机）→ Telegram Bot → 任务调度
  - Worker Node（高配 Ubuntu + GPU）→ Docker 容器 → Speech-AI-Forge → 音频生成
  - 数据流：Telegram 文本 → Syncthing 同步 → Forge API 推理 → SFTP 回传 → 交付

### API 调用格式

```python
payload = {
    "text": "要合成的文本",
    "tts": {"mid": "qwen3-tts-17cv"},       # CustomVoice 模型
    "spk": {"from_spk_name": "Chelsie"},     # 预设音色名
    "encoder": {"format": "mp3"},             # 输出格式
}
# VoiceDesign 模型需额外加 instruction 参数
payload["instruction"] = "用温柔缓慢的语速朗读"
```

> 引擎接口详见 kais-gold-team/kais-hub `demo_tts.py` 和 `docs/tts-integration-decision.md`

---

## 创作技巧核心：三层控制

```
Layer 1: 自然语言指令（instruction）  ← 最强，VoiceDesign 模型专属
Layer 2: 情感标签注入（文本预处理）    ← 中等，需转为指令
Layer 3: 韵律标记（ChatTTS 风格）     ← 精细，词级控制
```

---

## Layer 1：自然语言指令（推荐）

VoiceDesign 模型原生理解自然语言描述，这是拟人化最直接的方式。

### ✅ 有效指令写法

**描述具体、有画面感**：
```
✅ "用温柔缓慢的语速朗读，像在哄孩子入睡"
✅ "以激动的语气，语速稍快，像中了彩票一样"
✅ "老人回忆往事的语气，带着怀旧和淡淡的忧伤，语速缓慢"
✅ "严肃的新闻播报风格，吐字清晰，语速平稳，不夹杂个人情感"
✅ "轻声耳语，非常低的音量，像在图书馆里偷偷说话"
```

**指令要素公式**：
```
[语气/情感] + [语速描述] + [音量描述] + [类比/场景]
```

### ❌ 无效指令写法

```
❌ "happy"          → 太短，缺少上下文
❌ "快一点"         → 太模糊，缺少情感维度
❌ "用悲伤的语气但是也要开心" → 矛盾指令
❌ "像个人一样说话"  → 太抽象
```

### 指令与文本配合

指令只设定整体基调，文本本身的内容对韵律影响更大：

```
# 好的配合：文本自带情感线索
指令: "讲故事的语气"
文本: "他深吸一口气，缓缓说道：'我这一生，最后悔的事……'"
→ 模型会根据省略号、顿号自动放慢语速、增加停顿

# 差的配合：文本平淡但指令矛盾
指令: "激动万分"
文本: "今天天气不错。"
→ 指令和文本语义冲突，效果不稳定
```

---

## Layer 2：情感标签系统

灵感来自 Orpheus-TTS 的标签方案，适配到 Qwen3-TTS 的 instruction 参数。

### 标签集

```
基础: (happy) (sad) (angry) (calm) (surprised) (fearful)
扩展: (whispering) (shouting) (laughing) (crying) (sarcastic)
      (playful) (excited) (nervous) (serious) (gentle) (confident)
效果: (pause) (long_pause) (breath) (sigh)
强度: (emotion:0.3) ~ (emotion:1.0)
```

### 标签 → 指令映射

| 标签 | 转换为指令 | 语速 |
|------|-----------|------|
| `(happy)` | 愉快开朗的语气，语速适中偏快 | 1.1x |
| `(sad)` | 低沉忧伤的语气，语速缓慢 | 0.85x |
| `(angry)` | 愤怒激动的语气，语速快，音量稍大 | 1.2x |
| `(calm)` | 平静温和的语气，语速平稳 | 1.0x |
| `(whispering)` | 轻声细语，非常低的音量 | 0.8x |
| `(laughing)` | 带着笑意的语气 | 1.05x |
| `(serious)` | 严肃正式的语气，吐字清晰 | 1.0x |
| `(gentle)` | 温柔亲切的语气，语速缓慢 | 0.85x |
| `(excited)` | 兴奋激动的语气，语速快 | 1.2x |
| `(nervous)` | 紧张不安的语气，略带停顿 | 0.9x |

### 强度修饰

| 范围 | 指令后缀 |
|------|---------|
| 0.1-0.3 | "情感表达要含蓄微妙" |
| 0.4-0.6 | 不加修饰 |
| 0.7-0.8 | "情感表达要强烈明显" |
| 0.9-1.0 | "情感表达要非常强烈" |

### 标签堆叠

```
最多 3 个，顺序：效果 → 情感 → 强度
(breath)(sad:0.7)(whispering) → 先呼吸，再以低音量中等悲伤说话
```

### 标签使用示例

```
(calm) 今天天气不错，适合出门走走。
(surprised:0.8) 等一下——你刚才说什么？
(laughing)(playful) 开玩笑的啦！
(sad)(whispering) 有些事情……说不出口。
(angry:1.0) 我受够了！
```

---

## Layer 3：韵律标记（词级精细控制）

ChatTTS 风格标记，适合需要精确控制停顿和节奏的场景。

```
句子级:  [oral_0~9] [laugh_0~2] [break_0~7]
词级:    [uv_break] 短停顿 | [laugh] 笑声 | [lbreak] 长停顿
```

**使用场景**：
```python
# 模拟自然说话的停顿
text = "什么是[uv_break]你最喜欢的食物？"

# 强调效果
text = "最关键的是[uv_break]速度。"

# 笑声点缀
text = "这个问题嘛[laugh]其实不难回答。"
```

---

## 创作模式速查

### 旁白/有声书

```
指令: "讲故事的方式，语速缓慢，充满画面感，像在给孩子读睡前故事"
技巧:
  - 用省略号……制造悬念和停顿
  - 短句为主，长句拆分
  - 情感转折处换段重新生成
  - 适当用 [uv_break] 模拟思考停顿
```

### 对话/角色配音

```
指令: 每个角色单独一段，用不同指令
技巧:
  - 老人: "老人说话的语气，语速缓慢，声音沙哑"
  - 少女: "活泼少女的语气，语速偏快，语调上扬"
  - 旁白: "沉稳的旁白声音，语速平稳"
  - 注意: 每个角色需单独 API 调用，拼接处可能有韵律断裂
```

### 新闻播报

```
指令: "新闻播报风格，吐字清晰，语速平稳，不带个人情感"
技巧:
  - 标点符号规范化（逗号短停，句号中停）
  - 避免口语化标记
  - 专业术语前加 [uv_break] 做微停顿
```

### 情感表达/配音

```
指令: 根据场景选择对应情感 + 强度
技巧:
  - 情感渐变：分段生成，每段指令递增强度
    段1: "微微有些不安"
    段2: "越来越紧张"
    段3: "完全恐惧"
  - 用 [breath] [sigh] 增加真实感
  - 情感高峰前加 [long_pause] 做铺垫
```

### 播客/闲聊

```
指令: "像和朋友聊天一样，自然随意，偶尔带点犹豫和口头禅"
技巧:
  - 适度加入 [uv_break] 模拟思考
  - [oral_3~5] 增加口语感
  - 句末语调自然下落（不要刻意上扬）
```

---

## 关键注意事项

1. **文本 > 指令**：模型主要靠文本语义理解情感，指令只是辅助。写好文本比写好指令更重要
2. **分段 ≤ 200 字符**：超长文本必须分段，否则质量下降
3. **标点很重要**：省略号→停顿，感叹号→语气加强，问号→语调上扬
4. **参考音频增强**：提供匹配目标情感的参考音频（5-15秒，无噪音），效果远超纯指令
5. **CustomVoice vs VoiceDesign**：CustomVoice 有 9 种预设音色，VoiceDesign 可自由创建；VoiceDesign 的 instruction 效果远好于 Base 模型
6. **不要过度控制**：太复杂的指令反而让模型困惑。简单、具体的描述效果最好
7. **多轮迭代**：同一文本尝试 3-5 种不同指令，选最佳效果

## 限制与已知问题

1. Qwen3-TTS 不原生解析内联情感标签，需预处理转为 instruction
2. Base 模型的 instruction 效果有限，优先用 CustomVoice 或 VoiceDesign
3. 多段拼接处有韵律断裂风险，用 [uv_break] 或留 0.3-0.5s 静音缓解
4. 中英文混合时英文部分质量略低于纯中文
5. 社区提案原生标签支持：[QwenLM/Qwen3-TTS#238](https://github.com/QwenLM/Qwen3-TTS/discussions/238)
