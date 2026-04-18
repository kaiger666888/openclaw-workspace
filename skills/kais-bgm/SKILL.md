---
name: kais-bgm
version: 2.0.0
description: "智能BGM选曲+生成系统。双引擎架构：本地曲库匹配+AI音乐生成。与kais-movie-agent管线集成，从scenario.json情感曲线自动生成BGM策略。触发词：选BGM、配乐、选背景音乐、BGM推荐、给视频配乐、选音乐、挑BGM、找首BGM、背景音乐推荐、BGM策略、情感曲线配乐"
---

# kais-bgm — 智能 BGM 选曲

从本地音乐库根据场景描述和情感标签自动匹配最合适的背景音乐。

## 快速使用

用户描述场景或作品主题 → 自动推荐 BGM → 试听确认 → 复制到项目目录。

## 核心流程

### 1. 理解需求

向用户确认：
- **作品类型/主题**（如：仙侠短片、恐怖片、Vlog）
- **场景情感**（可选，如：紧张、温馨、史诗）
- **时长需求**（可选，默认不限）

### 2. 智能匹配

用 `selectBGM` 从本地音乐库匹配，返回 Top 5 候选：

```bash
node -e "
import { selectBGM } from '$SKILL_DIR/lib/bgm-selector.js';
import { readFileSync } from 'node:fs';

// 重建索引（如音乐库有更新）
const lib = JSON.parse(readFileSync('$SKILL_DIR/lib/bgm-library.json'));

const results = selectBGM(
  '<场景描述>',
  '<情感标签>',
  lib,
  { topN: 5, minDuration: 30, maxDuration: 180 }
);

for (const r of results) {
  console.log('[' + r.score + '分]', r.filename,
    '| 分类:', r.category,
    '| 时长:', r.duration.toFixed(1) + 's');
  console.log('路径:', r.path);
}
"
```

### 3. 试听推荐

通过 message tool 发送 Top 3 候选音频让用户试听：

```
message(action=send, media=<path>, message="🎵 1. 曲名 (时长) — 推荐理由")
```

### 4. 确认 & 复制

用户选定后，复制到项目目录：

```bash
cp "<选定BGM路径>" "<项目目录>/assets/bgm/"
```

## 高级功能

### 更新音乐库索引

当本地音乐库有新增时，重新扫描：

```bash
node -e "
import { scanMusicLibrary } from '$SKILL_DIR/lib/bgm-selector.js';
import { writeFileSync } from 'node:fs';

const library = await scanMusicLibrary('/home/kai/音乐/BGM_FreeCon', { probeDuration: true });
for (const item of library) {
  const rel = item.path.replace('/home/kai/音乐/BGM_FreeCon/', '');
  item.category = rel.split('/')[0];
  item.relativePath = rel;
}
writeFileSync('$SKILL_DIR/lib/bgm-library.json', JSON.stringify(library, null, 2));
console.log('已索引 ' + library.length + ' 首');
"
```

### 生成 AI 音乐提示词

如需 AI 生成原创 BGM：

```bash
node -e "
import { generateBGMPrompt } from '$SKILL_DIR/lib/bgm-selector.js';
console.log(generateBGMPrompt('<场景>', '<情感>', 30));
"
```

### 查看所有可用风格

```
tense(紧张) | warm(温馨) | sad(悲伤) | happy(欢快) | epic(史诗)
mystery(悬疑) | romantic(浪漫) | action(动作) | horror(恐怖) | peaceful(宁静)
```

## 音乐库概览

**路径**：`/home/kai/音乐/BGM_FreeCon`
**总量**：1037 首，16 个分类

| 分类 | 数量 | 对应风格 |
|------|------|---------|
| 节奏 | 158 | action |
| 复古 | 137 | mystery |
| 电子 | 128 | action |
| 混杂 | 126 | — |
| 史诗 | 67 | epic |
| 钢琴 | 65 | warm |
| 欢快 | 54 | happy |
| 世界 | 48 | peaceful |
| 浪漫伤感 | 43 | romantic/sad |
| 积极 | 34 | happy |
| 恐怖 | 33 | horror |
| 高分 | 38 | — |
| 摇滚 | 28 | action |
| 喜剧 | 17 | happy |
| 小提琴 | 3 | warm |

## 匹配算法

三级优先评分：

1. **分类映射**（权重 20）— 文件夹名 → BGM 风格
2. **文件名标签**（权重 10）— 歌名关键词匹配
3. **时长匹配**（权重 1-3）— 越接近目标时长越高

无匹配时随机推荐，确保始终有结果。

## 文件结构

```
kais-bgm/
├── SKILL.md              # 本文件
├── lib/
│   ├── bgm-selector.js   # 核心匹配引擎 + 情感曲线映射
│   └── bgm-library.json  # 音乐库索引
└── scripts/
    └── rescan.sh         # 重建索引脚本（可选）
```

## 🎬 与 kais-movie-agent 管线集成

### 集成点：Phase 2 之后

剧本（scenario.json）完成后，自动调用 `generateBGMScript()` 生成 BGM 策略，供 Phase 8 后期合成使用。

### 使用方式

```bash
node -e "
import { generateBGMScript } from '$SKILL_DIR/lib/bgm-selector.js';
import { readFileSync } from 'node:fs';

const scenario = JSON.parse(readFileSync('./project/scenario.json', 'utf8'));
const strategy = generateBGMScript(scenario, { preferLocal: true, aiThreshold: 0.8 });

// 保存 BGM 策略
import { writeFileSync } from 'node:fs';
writeFileSync('./project/bgm-strategy.json', JSON.stringify(strategy, null, 2));

console.log('🎵 BGM 策略已生成:');
console.log('  总镜头数:', strategy.total_shots);
console.log('  本地选曲:', strategy.local_select_count);
console.log('  AI 生成:', strategy.ai_generate_count);
console.log('  全局主题:', strategy.global_theme.style);
"
```

### bgm-strategy.json 输出格式

```json
{
  "version": "1.0",
  "project_title": "短片标题",
  "global_theme": {
    "style": "tense",
    "prompt": "tense cinematic soundtrack...",
    "genre": "悬疑"
  },
  "total_shots": 12,
  "ai_generate_count": 3,
  "local_select_count": 9,
  "shots": [
    {
      "id": "s1",
      "location": "废弃工厂",
      "emotion": "悬疑",
      "intensity": 0.6,
      "style": "mystery",
      "bgm_action": "select",
      "prompt": "mysterious dark ambient...",
      "needs_transition": false,
      "transition_type": "none"
    }
  ]
}
```

### 情感强度说明

| intensity | 含义 | BGM 策略 |
|-----------|------|---------|
| 0.0-0.3 | 平静/宁静 | 低音量环境音，几乎无旋律 |
| 0.3-0.5 | 温馨/日常 | 轻柔旋律，钢琴/吉他为主 |
| 0.5-0.7 | 情感波动 | 旋律增强，弦乐加入 |
| 0.7-0.8 | 悲伤/悬疑 | 完整配器，情感张力 |
| 0.8+ | 高潮/动作 | 全力输出，AI 生成更精准 |

### 转场处理规则

- `needs_transition: true` 时表示相邻镜头情感变化 >0.3
- `build_up`：情感上升（如 平静→紧张），1-2s 交叉淡入
- `fade_down`：情感下降（如 紧张→平静），1-2s 渐弱
