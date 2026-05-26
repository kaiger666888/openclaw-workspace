# ACE-Step 参数映射参考

## 完整参数列表

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `prompt` | string | "" | 音乐风格描述（英文） |
| `lyrics` | string | "" | 带 `[Section]` 标签的歌词 |
| `vocal_language` | string | `en` | 人声语言：`en`/`zh`/`ja`/`ko` |
| `bpm` | int | null | 节拍 30-300，null=自动 |
| `key_scale` | string | "" | 调式如 "C Major"，空=自动 |
| `time_signature` | string | "" | 拍号："2"/"3"/"4"/"6" |
| `duration` | float | 30.0 | 时长（秒）10-600 |
| `model` | string | `acestep-v15-turbo` | 模型选择 |
| `inference_steps` | int | 8 | 推理步数（turbo:8, sft:50） |
| `guidance_scale` | float | 7.0 | CFG scale |
| `seed` | int | -1 | 随机种子，-1=随机 |
| `audio_format` | string | `mp3` | 输出格式 |
| `thinking` | bool | true | 启用 LM 增强质量 |
| `sample_mode` | bool | false | Simple 模式（自然语言→歌曲） |
| `sample_query` | string | "" | Simple 模式描述 |

## Prompt 示例库

### 按风格分类

| 风格 | Prompt |
|------|--------|
| 中文流行 | `chinese pop ballad, emotional female vocal, piano and strings arrangement, warm and melancholic atmosphere, soft drum beats` |
| 英文摇滚 | `alternative rock, powerful male vocal, electric guitar distortion, heavy drums, energetic and rebellious mood` |
| 电子舞曲 | `EDM, synth lead melody, deep bass drops, four on the floor beats, euphoric and uplifting` |
| 国风民谣 | `chinese traditional folk, gentle female vocal, guzheng and bamboo flute, nature sounds, peaceful and nostalgic` |
| R&B | `smooth R&B, soulful male vocal, warm bass line, soft keyboard chords, intimate and romantic` |
| 说唱 | `hip-hop trap, fast rap flow, 808 bass, hi-hat rolls, confident and aggressive attitude` |
| 爵士 | `jazz bossa nova, gentle female vocal, nylon guitar, soft brushes, relaxed and sophisticated` |
| 史诗 | `epic orchestral, powerful choir, brass and timpani, dramatic and grandiose, cinematic` |
| Lo-fi | `lo-fi hip hop, chill beats, vinyl crackle, soft piano chords, relaxed and dreamy` |
| 金属 | `heavy metal, aggressive male vocal, distorted guitars, double bass drums, intense and dark` |

### 按情感分类

| 情感 | Prompt 关键词 |
|------|-------------|
| 浪漫 | `romantic, tender, gentle, warm, intimate` |
| 激昂 | `energetic, powerful, intense, driving, anthemic` |
| 忧伤 | `melancholic, sad, nostalgic, longing, gentle piano` |
| 欢快 | `upbeat, cheerful, bright, lively, catchy` |
| 神秘 | `mysterious, ambient, ethereal, atmospheric, dark` |
| 温暖 | `warm, cozy, soft, comforting, acoustic` |

### Prompt 写作公式

```
[音乐风格], [人声描述], [主要乐器], [氛围/情感], [节奏特征]
```

示例：
```
indie folk, soft female vocal, acoustic guitar and light percussion, 
bittersweet and introspective, gentle fingerpicking rhythm
```

## 歌词格式完整示例

```
[Intro]
(soft piano melody)

[Verse 1]
月光洒在窗台
咖啡凉了第二杯
城市灯火依然亮着
只有影子陪我入睡

[Pre-Chorus]
也许该学会放手
让风吹走那些以后

[Chorus]
如果思念有声音
是不是像海浪一样不停
如果回忆有颜色
一定是薄荷味的透明

[Verse 2]
清晨阳光穿过窗帘
手机里没有你的消息
习惯性翻开旧照片
才发现微笑还是你

[Bridge]
时间走得太快
来不及说一句再见

[Chorus]
如果思念有声音
是不是像海浪一样不停
如果回忆有颜色
一定是薄荷味的透明

[Outro]
薄荷味的透明...
(piano fade out)
```
