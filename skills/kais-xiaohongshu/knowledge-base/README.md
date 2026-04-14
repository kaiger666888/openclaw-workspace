# XHS Knowledge Base（kais-xiaohongshu v2）

这个目录是小红书运营知识库的总览入口。

目标：让 agent 在开始任务前先看一眼"我们已经知道什么"，结束任务后把新的分析结果和动作沉淀到固定位置，方便后续检索和复用。

## 1. 目录结构

```text
knowledge-base/
  README.md              # 总览入口，保留当前重点和搜索指引
  accounts/              # 账号定位、账号体检、竞品账号分析
  topics/                # 选题灵感、搜索关键词、对标博主分析、选题评分
  patterns/              # 爆款结构、标题句式模板、封面模板、互动钩子
  actions/               # 发布、回复、抓取、下载、复刻等动作记录
  reviews/               # 复盘、有效/无效原因、爆款模型验证结果
  monetization/          # v2 新增：变现记录、虚拟产品数据、商单价格
```

## 2. 使用规则

- 开始任务前：先读本文件，再按目录搜索最相关的记录。
- 选题任务前：优先查 `topics/` 和 `patterns/`，已有选题库的不重复采集。
- 变现任务前：查 `monetization/` 了解历史变现数据。
- 任务进行中：遇到新的高价值结论，可以先记临时摘要，任务结束后整理成独立记录。
- 任务结束后：至少补一条结构化记录到对应目录。

## 3. v2 选题库集成

选题数据优先沉淀到 `topics/` 目录，格式示例：

```text
topics/2026-04-05-weight-loss-keywords.md
  - 核心关键词：减肥
  - 长尾词：减肥最快方法、学生党减肥、三伏天减肥...
  - 候选选题池（10-20条，含赞粉比/评论率）
  - 量化评分结果
  - 推荐创作顺序
```

## 4. 文件命名建议

日期 + brief（2-6 个高信息量词）：

- `accounts/2026-04-05-drama-watch-positioning.md`
- `topics/2026-04-05-weight-loss-keywords.md`
- `patterns/2026-04-05-listicle-title-template.md`
- `monetization/2026-04-05-template-sales-data.md`
- `reviews/2026-04-05-batch-publish-retrospective.md`

## 5. 当前重点

- 暂无固定重点，可在后续任务中持续补充。

## 6. 固定索引

- 账号分析：`knowledge-base/accounts/`
- 选题库：`knowledge-base/topics/`
- 可复用模式：`knowledge-base/patterns/`
- 动作记录：`knowledge-base/actions/`
- 结果复盘：`knowledge-base/reviews/`
- 变现数据：`knowledge-base/monetization/`（v2 新增）

## 7. 写入最小标准

每条细分记录至少包含：

- 一句话结论
- 证据或来源
- 可复用点
- 风险或边界
- 下一步动作
