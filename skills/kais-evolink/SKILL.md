---
name: kais-evolink
version: 1.0.0
description: "Evolink AI 视频生成技能，接入 Seedance 1.5 Pro 等模型。支持文生视频、图生视频、首尾帧生成。触发词：evolink, 生成视频, evolink视频, seedance, 文生视频, 图生视频, 首尾帧, evolink生成"
---

# kais-evolink

通过 Evolink API 生成 AI 视频，默认使用 seedance-1.5-pro 模型。

## 配置

API Key 存储在 `~/.openclaw/.evolink.json`：
```json
{
  "apiKey": "sk-xxx",
  "baseUrl": "https://api.evolink.ai/v1"
}
```

首次使用时检查配置文件，不存在则提示用户提供 API Key。

## 核心流程

<!-- FREEDOM:low -->

### 1. 创建视频生成任务

```bash
POST https://api.evolink.ai/v1/videos/generations
Authorization: Bearer YOUR_API_KEY
Content-Type: application/json

{
  "model": "seedance-1.5-pro",
  "prompt": "<描述>",
  "image_urls": [],           // 可选：0张=文生视频, 1张=图生视频, 2张=首尾帧
  "duration": 5,              // 4-12秒
  "quality": "720p",          // 480p/720p/1080p
  "aspect_ratio": "16:9",     // 16:9/9:16/1:1/4:3/3:4/21:9/adaptive
  "generate_audio": true      // 是否生成音频
}
```

成功返回 task_id，用于轮询状态。

### 2. 轮询任务状态

```bash
GET https://api.evolink.ai/v1/tasks/{task_id}
Authorization: Bearer YOUR_API_KEY
```

状态值：pending → processing → completed / failed

completed 时 `output.video_url` 为视频下载链接（24小时有效）。

### 3. 轮询策略

- 初始等待 10 秒后开始轮询
- 每 15 秒查询一次
- 超时上限 10 分钟
- failed 时输出错误信息

<!-- /FREEDOM:low -->

## 模式说明

| 模式 | image_urls | 说明 |
|------|-----------|------|
| 文生视频 | `[]` 或不传 | 纯文本描述生成视频 |
| 图生视频 | 1 张图片 URL | 基于参考图生成视频 |
| 首尾帧 | 2 张图片 URL | 第一帧和最后一帧，模型补中间 |

## 参数参考

| 参数 | 范围 | 默认 |
|------|------|------|
| duration | 4-12 秒 | 5 |
| quality | 480p / 720p / 1080p | 720p |
| aspect_ratio | 16:9 / 9:16 / 1:1 / 4:3 / 3:4 / 21:9 / adaptive | 16:9 |
| generate_audio | true / false | true |

图片限制：单张 ≤10MB，格式 .jpg/.jpeg/.png/.webp，宽高 300-6000px，宽高比 0.4-2.5。

## 完整执行脚本

使用 `scripts/evolink.sh` 执行完整流程：

```bash
# 文生视频
bash scripts/evolink.sh --prompt "一只猫弹钢琴" --duration 8 --quality 1080p

# 图生视频
bash scripts/evolink.sh --prompt "镜头缓慢推进" --image-url "https://example.com/img.jpg" --duration 5

# 首尾帧
bash scripts/evolink.sh --prompt "过渡动画" --image-url "https://a.jpg" --last-frame "https://b.jpg" --duration 6
```

## 注意事项

- 视频 URL 24 小时后失效，需及时下载保存
- 音频生成会增加费用，可通过 `generate_audio: false` 关闭
- 建议对话内容用双引号包裹以优化音频效果
- 文件上传（本地图片）需先通过 Evolink 文件上传 API 获取 URL
