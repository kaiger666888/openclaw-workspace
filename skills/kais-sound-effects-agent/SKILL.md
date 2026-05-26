---
name: kais-sound-effects-agent
version: 1.1.0
description: "AI 音效创作技巧指导。基于 Sony Woosh 音效生成引擎，专注 Prompt 工程和创作方法论。触发词：音效生成, 拟声效果, sound effects, SFX创作, 生成音效, 音效prompt"
---

# kais-sound-effects-agent

AI 音效创作技巧库——基于 **Sony Woosh** 引擎，专注 Prompt 工程和创作方法论。

## 引擎：Sony Woosh

Woosh 是 Sony AI 专为**音效**设计的 foundation model，不是通用音频模型。

- **GitHub**: https://github.com/SonyResearch/Woosh
- **论文**: arXiv 2604.01929（2026.4）
- **许可**: 模型权重 CC-BY-NC，代码 MIT
- **API 封装**: https://github.com/kaiger666888/kais-gold-team

### 核心模块

| 模块 | 功能 | 适用场景 |
|------|------|---------|
| **Woosh-AE** | 高质量音频编解码器 | 48kHz 音频编解码基础 |
| **Woosh-CLAP** | 文本-音频对齐模型 | 文本 Prompt → 潜变量条件 |
| **Woosh-Flow** | 文本 → 音效（完整版） | 最高质量，推理较慢 |
| **Woosh-DFlow** | 文本 → 音效（蒸馏版） | 快速推理，质量接近 |
| **Woosh-VFlow** | 视频+文本 → 音频 | 视频配声 |

### 关键技术参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| **cfg_scale** | 4.5 | Classifier-Free Guidance，控制"遵循 Prompt 程度" |
| **seed** | 随机 | 固定种子可复现结果 |
| **solver** | dopri5 | ODE 求解器（dopri5/dopri8/bosh3/adaptive_heun） |
| **output** | ~5 秒 | 固定时长（501 latent frames @ 48kHz） |
| **sample_rate** | 48000 | 固定 48kHz |
| **batch_size** | 1-8 | 一次生成多个变体 |

> ⚠️ Woosh 是**纯音效模型**，不生成语音。语音合成请用 Qwen3-TTS。

---

## Prompt 工程核心原则

### 1. 写场景，不写技术

Woosh-CLAP 在**专业音效库描述**上微调，理解的是"什么在发生"，不是"用什么格式"。

```
❌ "explosion, 48kHz, cinematic, high quality"（技术词汇无效）
✅ "massive explosion in a warehouse with metal debris clattering and echoing"
```

**Woosh 不理解的技术指令**：48kHz、mp3、stereo、 cinematic（作为质量词）、high quality

**Woosh 理解的描述**：材质、距离、空间、动作、场景、情绪

### 2. 自然语言描写 = 最佳 Prompt

Woosh 训练数据用 Qwen3-Omni 生成的富文本描述，偏好完整的句子式描述：

```
❌ "thunder rain wind"（关键词堆砌）
✅ "thunder rumbling in the distance with heavy rain on a tin roof and strong wind gusts"
```

### 3. 两层结构法（Woosh 专用）

Woosh 的 Prompt 不需要"技术层"，核心只有两层：

| 层级 | 作用 | 示例 |
|------|------|------|
| **主体动作** | 核心声音事件 | "sportscar engine revving" |
| **场景环境** | 空间/背景/细节 | "and driving away quickly on wet asphalt" |

---

## CFG Scale 调参指南

**CFG Scale 是 Woosh 最重要的生成参数**，控制模型对 Prompt 的遵循程度。

| CFG 值 | 效果 | 适用场景 |
|--------|------|---------|
| 1.0-2.0 | 松散，更随机/创意 | 探索性生成、背景氛围 |
| **3.0-5.0** | **推荐范围** | **大多数场景，平衡准确性和多样性** |
| 5.0-7.0 | 严格遵循 Prompt | 精确匹配特定声音 |
| 7.0-10.0 | 过度遵循，可能 artifact | 不推荐，除非 Prompt 非常具体 |
| 10.0-15.0 | 极端，质量下降 | 避免 |

**调参策略**：
- 生成不满意 → 先改 Prompt，再调 CFG
- 声音太杂 → 降低 CFG（3-4）
- 声音不对 → 提高 CFG（5-6）
- 想要变化 → 固定 seed 改 CFG，或固定 CFG 改 seed

---

## 拟声词 → Woosh Prompt 映射表

Woosh-CLAP 对英文理解更好。中文拟声词需要转化为英文场景描述：

| 中文拟声 | 英文 Prompt | 关键技巧 |
|----------|-------------|---------|
| 咔嚓 | "a dry wooden branch snapping cleanly in half" | 加材质 "dry wooden" |
| 轰隆 | "deep thunder rumbling from far away, shaking the ground" | 加距离+物理感 |
| 叮咚 | "a small brass bell chiming two clear notes" | 加材质 "brass" |
| 滴答 | "a wall clock ticking steadily in a quiet room" | 加场景营造对比 |
| 呼噜 | "a person snoring heavily with rhythmic breathing" | 加 "heavily" 表力度 |
| 吧唧 | "wet footsteps squelching in thick mud" | 加介质 "thick mud" |
| 咣当 | "a heavy iron gate slamming shut with a metallic clang" | 加材质+动作 |
| 嗖嗖 | "strong wind whistling through a narrow alley" | 加空间限定 |
| 噼啪 | "a campfire crackling with popping embers" | 加场景 "campfire" |
| 咕噜 | "water bubbling steadily in a boiling pot" | 加状态 "steadily" |
| 哗啦 | "a large wave crashing against rocks with spray" | 加材质碰撞面 |
| 吱呀 | "an old wooden door slowly creaking open" | 加 "old wooden" 表材质 |
| 咚咚 | "someone knocking firmly on a heavy wooden door" | 加力度+材质 |
| 嗡嗡 | "an electrical transformer humming steadily" | 加声源身份 |
| 呲啦 | "a sharp metal tool scraping slowly across concrete" | 加速度+材质 |

**技巧**：拟声词本身对 Woosh 无效，必须描述**产生这个声音的物理事件**。

---

## 场景模板（Woosh 官方风格）

### 自然环境

```
"intense thunderstorm with heavy rain, frequent lightning strikes, and thunder echoing across mountains"
"peaceful forest ambience with birds chirping, gentle breeze through leaves, and a distant stream"
"ocean waves crashing on a rocky shore with seagulls calling and foghorn in the distance"
```

### 城市与室内

```
"busy coffee shop with espresso machine hissing, cups clinking, and quiet conversation murmur"
"rain falling on a city street with cars splashing through puddles and distant traffic"
"a quiet library with pages turning softly and a faint hum of air conditioning"
```

### 机械与交通工具

```
"sportscar engine revving and driving away quickly"  ← Woosh 官方示例
"emergency vehicle driving with siren on"             ← Woosh 官方示例
"an old diesel train slowly pulling into a station with brakes squealing"
"a helicopter flying overhead with rotor blades chopping the air"
```

### 动作与交互

```
"footsteps running on wet pavement with heavy breathing"
"swords clashing in a fast duel with metallic ringing and grunting"
"a glass shattering on a hard floor with pieces scattering"
```

### 科幻与奇幻

```
"a spaceship engine powering up with a deep low hum and energy crackling"
"magical spell casting with shimmering crystalline sounds and a deep resonant boom"
"a portal opening with a swirling vortex and deep rumbling"
```

---

## 空间感控制

Woosh 通过**场景描述**隐式控制空间感，而非技术参数：

| 想要的效果 | Prompt 技巧 |
|-----------|------------|
| 近景 | "close-up recording of..." / "right next to..." |
| 远景 | "distant..." / "far away..." / "faint..." |
| 室内混响 | "...in a large hall" / "...in a cathedral" |
| 紧闭空间 | "...inside a small metal room" |
| 开阔空间 | "...in an open field" / "...across a valley" |
| 回声 | "...echoing through..." |

---

## 质量控制

### 常见问题

| 问题 | 原因 | 修复 |
|------|------|------|
| 声音模糊 | Prompt 太笼统 | 加具体材质和动作 |
| 声音太杂 | 描述太多声源 | 减少到 1-2 个主声源 |
| 不像预期 | 用了技术词汇 | 改为自然语言场景描写 |
| 有 artifact | CFG 太高 | 降低到 3-5 |
| 每次不同 | 需要复现 | 固定 seed |
| 声音太弱 | 模型生成偏安静 | 后期增益，不改 Prompt |

### 批量生成策略

Woosh 支持 batch_size 1-8，一次生成多个变体选最好的：

```python
# 一次生成 4 个变体，挑最满意的
batch_size = 4
# 固定 CFG，不同 seed 自动产生变化
```

### 质量自检清单

- [ ] 声音主体是否清晰可辨？
- [ ] 场景空间感是否符合预期？
- [ ] 有没有不自然的 artifact？（高频杂音、金属感）
- [ ] 与画面/语境是否匹配？

---

## 进阶技巧

### 音效串联叙事

用多个 ~5s 音效片段按顺序排列，构建声音叙事：

```
场景：深夜入侵

音效 1: "a quiet house at night with a clock ticking"        → 建立宁静
音效 2: "a wooden floorboard creaking slowly"                → 异常出现
音效 3: "a door latch clicking open slowly"                   → 入侵确认
音效 4: "quick footsteps on a carpeted floor"                 → 行动开始
```

### 负空间（留白）

Woosh 固定输出 ~5s，可以利用前 1-2 秒的静默来制造冲击：

```
"silence then a sudden loud crash of metal objects falling"
```

### Seed 管理

- **固定 seed + 改 CFG**：同一个基础声音，不同强度
- **固定 CFG + 改 seed**：同一个 Prompt，不同变体
- **记录好 seed**：满意的生成务必记录 seed，方便复现和微调

### 与视频配声（Woosh-VFlow）

Woosh-VFlow 可以同时接收视频 + 文本 Prompt：

```
# 文字补充视频中不明显但需要的声音
视频：飞机飞过雪原
文本 Prompt: "a propeller plane flying over a snowy landscape, its engine roaring"
```

**技巧**：文字 Prompt 描述视频中的声音事件，VFlow 模型会自动对齐时间轴。

---

## 与 TTS 的配合

Woosh 是纯音效模型，不生成语音。完整音频制作需要配合 TTS：

```
1. 角色对话 → Qwen3-TTS（kais-gold-team Forge 容器）
2. 环境音效 → Woosh（kais-gold-team Worker Node）
3. 后期混合 → 音频编辑工具叠加
```

**关键**：TTS 和 SFX 分别生成，不要在同一个请求中混用。

---

## 工作流

```
1. 确定场景 → 列出需要的音效清单
2. 写 Prompt → 自然语言场景描写（主体动作 + 场景环境）
3. 设参数  → CFG 4.5 起步，batch_size 2-4
4. 调用 API → 通过 kais-gold-team 接口生成
5. 质量检查 → 不满意先改 Prompt，再调 CFG
6. 记录 seed → 满意的生成务必记录
7. 后期处理 → 剪辑、混合、增益（如需要）
```

---

## 相关资源

- **Sony Woosh**: https://github.com/SonyResearch/Woosh（论文 arXiv 2604.01929）
- **Woosh 官方示例页**: https://sonyresearch.github.io/Woosh/
- **Woosh ComfyUI 节点**: https://github.com/Saganaki22/ComfyUI-Woosh
- **kais-gold-team**: https://github.com/kaiger666888/kais-gold-team（引擎调用封装）
