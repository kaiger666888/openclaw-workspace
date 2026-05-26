# Notion 格式标准

> 所有向 Notion 输出的内容必须遵循此标准

---

## 核心原则

1. **使用 JSON 块格式**，   - 不使用 Markdown 文本追加
   - 所有块放在 `children` 数组中
   - 使用 `notion-cli block append --children-file`

2. **页面结构标准**
```
[callout] 📋 摘要（今日要点：xxx）
[divider]
[heading_2] 🎯 分类标题
[callout] 子主题高亮
[paragraph/bulleted_list_item] 详细内容
[paragraph] 🔗 来源名称URL
[divider]
...
[paragraph] 数据来源：xxx
```

3. **原子操作**
   - 创建页面 + 巻加内容 = 一次性完成
   - 避免多次追加导致重复

---

## 格式检查清单

| 检查项 | 正确 | 错误 |
|-------|------|------|
| 顶部 callout | ✅ 有摘要 | ❌ 没有 |
| heading_2 | ✅ 分类标题 | ❌ 只有 paragraph |
| 链接格式 | ✅ `🔗 名称URL` | ❌ Markdown 链接 |
| 重复内容 | ✅ 无重复 | ❌ 有重复块 |

---

## 工具函数

### 1. 创建页面（推荐）
```bash
source /home/kai/.openclaw/workspace/scripts/lib/notion-format-utils.sh
page_id=$(create_page_with_json "parent-id" "标题" "/path/to/content.json")
```

### 2. 验证格式
```bash
validate_page_format "$page_id"
```

### 3. 修复格式问题
```bash
repair_page "$page_id" "parent-id" "新标题" "/path/to/content.json"
```

---

## JSON 块模板参考

位置：`/home/kai/.openclaw/workspace/scripts/lib/notion-block-templates.json`

---

## 常见错误及修复

| 错误 | 原因 | 修复 |
|------|------|------|
| 内容重复 | 多次追加 | 删除页面重建 |
| Markdown 语法显示 | 用错工具 | 改用 JSON 块 |
| 链接不可点击 | 格式错误 | 用 `🔗 名称URL` |
| 缺少摘要 callout | 未遵循模板 | 添加顶部 callout |

---

*最后更新：2026-03-02*
