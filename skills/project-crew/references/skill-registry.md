# Skill 参数注册表

常用 skill 的参数格式与执行方式，供编排器和 AI 参考。

## general

通用文本处理 skill，无需特定 SKILL.md。用于合并、格式化、摘要等轻量文本操作。

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| (无必填参数) | | | AI 根据 input 文件内容和 instruction 自行判断操作 |

**执行方式：** 读取 input 文件 → 按 instruction 处理 → 写入 output

---

## deep-research

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| topic | string | ✅ | 研究主题 |
| depth | `"quick"` \| `"medium"` \| `"deep"` | ❌ | 深度，默认 medium |
| output | string | ✅ | 输出 markdown 文件路径 |

**执行方式：** web_search → 分析整理 → 生成 markdown 到 output 路径

## notion

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| pageId | string | ✅ | Notion 页面 ID（32位 UUID） |
| parentPageId | string | ❌ | 父页面 ID（创建新页面时） |
| title | string | ❌ | 新页面标题 |

**执行方式：** `notion-write.sh <pageId> <markdown-file>`
- input 文件自动作为写入内容
- 创建页面时 pageId 可省略，需提供 parentPageId + title
- ⚠️ 禁止使用 `--content` 直接写入纯文本（格式会丢失）

## chart-image

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| type | string | ✅ | 图表类型：line, bar, area, pie, heatmap, candlestick 等 |
| data | object | ❌ | 内联数据对象 |
| output | string | ✅ | 输出图片路径（png） |

**执行方式：** 生成图表到 output 路径，纯 Node.js 无需浏览器

## xiaohongshu-ops

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| action | string | ✅ | 操作类型：search, publish, comment 等 |
| input | string | ✅ | 输入文件路径（markdown） |

**执行方式：** 通过 OpenClaw 内置浏览器执行小红书操作

## arxiv-watcher

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| query | string | ✅ | 搜索关键词 |
| output | string | ✅ | 输出 markdown 路径 |

**执行方式：** 搜索 ArXiv → 总结论文 → 写入 output
