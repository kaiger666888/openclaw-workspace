# 质量检查标准

## Notion 块数验证

写入后必须执行：
```bash
notion-cli block list <PAGE_ID>
```

| 块数 | 状态 | 处理 |
|------|------|------|
| < 20 | ❌ 严重不足 | 重做 Step 3-5 |
| 20-50 | ⚠️ 偏短 | 重做 Step 3-5 |
| ≥ 50 | ✅ 合格 | 继续下一个任务 |

**最多重试 2 次，超过则标记失败继续下一个任务。**

## 格式验证

检查以下几点：
- [ ] 页面是子页面（不是直接写到父页面）
- [ ] 内容是 Notion 块格式（标题是 heading_2，不是段落里的 `##`）
- [ ] 有 callout 摘要（`>💡`）
- [ ] 每条信息紧跟来源链接（不是堆在底部）
- [ ] 关键数据有颜色标注

## 去重验证

需要去重的任务（events.yaml 中 dedup: true）：

```bash
# 检查
python /home/kai/.openclaw/workspace/scripts/lib/dedupe-validator.py \
  <dedup_type> check --<field> "内容"

# 记录
python /home/kai/.openclaw/workspace/scripts/lib/dedupe-validator.py \
  <dedup_type> add --<field> "内容" --source "来源" --page-id "页面ID"
```

## 常见失败模式

| 问题 | 根因 | 预防 |
|------|------|------|
| 内容写到父页面 | 没用 daily-task-write.sh | **必须**用 daily-task-write.sh |
| 纯文本格式 | 用了 --content 参数 | **必须**用 daily-task-write.sh |
| 空页面 | agent 跳过写入步骤 | 验证块数 < 20 则重做 |
| 来源堆底部 | 生成时偷懒 | Step 3 模板里写死格式 |
| 标题格式不统一 | agent 自创标题 | 标题由脚本自动生成 |
