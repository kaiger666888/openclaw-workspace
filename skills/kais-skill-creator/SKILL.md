---
name: kais-skill-creator
version: 1.0.0
description: "创建、改进、审核和发布 OpenClaw Skill 的全流程工具。中文优先，集成脚手架生成、5维质量评分、自动优化和 ClawHub 发布。触发词：创建skill, create skill, 改进skill, 审核skill, skill质量, 发布skill, 新建技能, 做一个skill, scaffold skill, skill脚手架, skill向导"
---

# kais-skill-creator

全流程 Skill 创作工具——从想法到发布，一个对话搞定。

## 首次使用向导

检测 `~/.openclaw/.kais-skill-creator.json` 是否存在。不存在则启动向导：

1. 读取 USER.md 获取默认作者名
2. 询问默认 skill 存放路径（默认 `~/.openclaw/workspace/skills/`）
3. 询问默认发布目标（ClawHub / 仅本地）
4. 写入配置文件，后续调用不再重复询问

配置文件格式：
```json
{
  "version": 1,
  "author": "作者名",
  "skillsDir": "~/.openclaw/workspace/skills/",
  "target": "clawhub",
  "createdAt": "ISO日期"
}
```

如果用户说 "setup", "configure", "reconfigure", "重新配置" → 重新运行向导。

## 模式选择

根据用户意图自动判断，或询问选择：

| 模式 | 触发词 | 操作 |
|------|--------|------|
| 🆕 创建新 skill | "创建skill", "做一个skill", "新建技能" | 需求分析 → 脚手架 → SKILL.md → 评分 → 优化 |
| 🔧 改进 skill | "改进skill", "优化skill", "提升skill" | 评分 → 定位问题 → 修复 → 复评 |
| 🔍 审核 skill | "审核skill", "检查skill", "skill质量" | 评分 → 报告 → 建议 |
| 📦 发布 skill | "发布skill", "publish skill" | 验证 → checklist → clawhub publish |

## 模式 1：创建新 Skill

### 步骤 1：需求理解

向用户询问（最多 3 轮追问）：
1. Skill 要解决什么问题？触发场景是什么？
2. 需要调用哪些外部工具/API？
3. 复杂度：简单（单脚本）/ 中等（多步骤）/ 复杂（编排 pipeline）？

分析后输出结构化摘要：建议名称、触发词、核心流程、外部依赖、复杂度。用户确认后继续。

### 步骤 2：生成脚手架

运行脚手架脚本：
```bash
bash ~/.openclaw/workspace/skills/kais-skill-creator/scripts/init.sh <skill-name> --template <simple|complex|pipeline> --path <skillsDir>
```

模板选择规则：
- 简单（单脚本/单操作）→ `simple`
- 中等（多步骤/有脚本）→ `complex`
- 复杂（多模块/编排型）→ `pipeline`

### 步骤 3：生成 SKILL.md

基于需求分析结果，编辑脚手架生成的 SKILL.md。遵循以下原则：

**Frontmatter 精确**：description 是触发器，必须包含具体触发场景和工具声明。
**行数控制**：< 500 行，超过则拆分到 references/。
**渐进式披露**：核心流程放 SKILL.md，详细参考放 references/。
**自由度分级**：
- 🟢 低脆弱度 → `<!-- FREEDOM:high -->`，文本指导
- 🔴 高脆弱度 → `<!-- FREEDOM:low -->`，精确脚本 + 确认

### 步骤 4：质量评估

运行评分脚本：
```bash
python3 ~/.openclaw/workspace/skills/kais-skill-creator/scripts/score.py <skill-path>
```

评分等级：
- 🏆 90-100：优秀，可直接发布
- ✅ 75-89：良好，小修后发布
- ⚠️ 60-74：及格，需要优化
- ❌ < 60：不合格，需要重写

### 步骤 5：全覆盖测试

对生成的 skill 执行全维度验证：

```bash
# 静态验证（结构、语法、权限）
bash ~/.openclaw/workspace/skills/kais-skill-creator/scripts/validate.sh <skill-path>

# 质量评分（5维度）
python3 ~/.openclaw/workspace/skills/kais-skill-creator/scripts/score.py <skill-path>
```

**测试检查清单：**
- [ ] `validate.sh` 全部通过（0 错误）
- [ ] `score.py` 总分 ≥ 85
- [ ] 脚本可实际运行（dry-run）
- [ ] references/ 引用路径全部有效
- [ ] 无敏感信息泄露
- [ ] 自由度标记正确（high/low 场景对应）

如果任何检查不通过，直接进入步骤 6 迭代。

### 步骤 6：自动迭代优化（收敛循环）

<!-- FREEDOM:low -->
**必须执行以下循环，直到质量收敛或达到上限。**

#### 收敛判断规则

| 条件 | 动作 |
|------|------|
| 总分 ≥ 90 且 validate 0 错误 | ✅ 收敛，进入步骤 7 |
| 连续 2 轮总分改进 < 3 分 | ✅ 收敛（边际收益递减），进入步骤 7 |
| 迭代达到 5 轮 | ⚠️ 强制停止，汇报当前状态让用户决策 |
| 总分 < 60 | ❌ 基础质量问题，考虑重新设计 |

#### 每轮迭代流程

```
Round N:
  1. 读取 score.py 输出的 .score.json（上轮评分 + 扣分项）
  2. 按优先级修复问题：
     - 🔴 致命问题（缺失字段、语法错误）→ 必须修复
     - 🟡 重要问题（触发词不足、行数超标）→ 应该修复
     - 🟢 优化项（中文比例、代码块迁移）→ 尽量修复
  3. 避免重复修复：追踪已修复项，不重复处理同一问题
  4. 重新运行 validate.sh + score.py
  5. 计算改进幅度，判断是否收敛
```

#### 回归保护

每轮迭代后，对比上轮分数。如果总分下降，立即回滚到上一版本。

#### 迭代日志格式

每轮记录到对话中：
```
🔄 Round 1/5
  修复: 补充中文触发词, 精简代码块, 添加 shebang
  结果: 72 → 83 (+11) ⬆️
  状态: 继续迭代

🔄 Round 2/5
  修复: 优化 description 触发场景描述
  结果: 83 → 87 (+4) ⬆️
  状态: 改进 < 3，收敛 ✅
```

#### 迭代完成后

输出最终评估报告：
```
📊 迭代完成（N 轮）
  最终评分: XX/100
  修复项: [列出所有修复]
  剩余问题: [如有]
  建议: [发布 / 继续手动优化 / 重新设计]
```
<!-- /FREEDOM:low -->

### 步骤 7：GitHub 仓库创建与推送

<!-- FREEDOM:low -->
**为每个 skill 单独创建 GitHub 仓库，只包含 skill 自身文件。**

1. **确认 GitHub 账户**：运行 `gh auth status`，确保活跃账户正确（默认 kaiger666888）
2. **在 skill 目录下初始化独立 git 仓库**：
```bash
cd <skill-path>
git init
echo -e "node_modules/\n__pycache__/\n.score.json\n*.pyc" > .gitignore
git add -A
git commit -m "feat: init <skill-name> skill"
```
3. **创建远程仓库并推送**：
```bash
gh repo create <skill-name> --public --description "<skill描述>" --source . --push
```
4. **验证推送结果**：确认仓库可访问，返回链接

**注意**：绝不将 skill 推入 workspace 大仓库，每个 skill 独立 repo。

如果用户偏好仅本地，跳过此步骤。
<!-- /FREEDOM:low -->

### 步骤 8：交付确认

展示最终 skill 结构、评分和 GitHub 仓库链接，询问用户：
1. 是否满意？→ 结束，或进入模式 4 发布到 ClawHub
2. 需要调整？→ 手动修改后重新走步骤 5-6
3. 不满意？→ 回到步骤 1 重新分析需求

## 模式 2：改进现有 Skill

1. 运行 `score.py` 获取当前评分
2. 展示各维度得分 + 具体扣分项
3. 询问改进方向（全部 / 结构 / 效率 / 可执行性）
4. 执行改进，展示 diff
5. 重新评分确认

## 模式 3：审核 Skill

1. 运行 `validate.sh` + `score.py`
2. 输出完整评分报告：5 维度得分 + 总分 + 扣分详情 + 优化建议
3. 不做修改，仅报告

## 模式 4：发布 Skill

<!-- FREEDOM:low -->
必须严格按以下顺序执行：

1. 运行验证：
```bash
bash ~/.openclaw/workspace/skills/kais-skill-creator/scripts/validate.sh <skill-path>
```

2. 确认评分 ≥ 75，否则先优化

3. 发布前 Checklist：
   - [ ] SKILL.md frontmatter 完整（name + description）
   - [ ] description 包含触发词，无歧义
   - [ ] 目录结构符合规范
   - [ ] scripts/ 有执行权限
   - [ ] 本地测试通过
   - [ ] 无敏感信息（token、私钥、个人路径）

4. 询问用户确认发布

5. 确认后执行：
```bash
bash ~/.openclaw/workspace/skills/kais-skill-creator/scripts/publish.sh <skill-path>
```

6. 验证发布结果，返回 ClawHub 链接
<!-- /FREEDOM:low -->

## CLI 命令

| 脚本 | 用法 | 说明 |
|------|------|------|
| `scripts/init.sh` | `init.sh <name> [--template simple\|complex\|pipeline] [--path <dir>]` | 一键脚手架 |
| `scripts/validate.sh` | `validate.sh <skill-path>` | 静态验证 + 评分 |
| `scripts/score.py` | `score.py <skill-path>` | 5维质量评分 |
| `scripts/publish.sh` | `publish.sh <skill-path> [--dry-run]` | 打包发布 |

## 质量评估 5 维度

| 维度 | 满分 | 评估内容 |
|------|------|----------|
| 🎯 触发精确度 | 20 | description 触发词、冲突检测、覆盖面 |
| 📐 结构完整性 | 20 | 目录规范、frontmatter、必要章节、脚本权限 |
| ⚡ Token 效率 | 20 | 行数 < 500、渐进式披露、无重复 |
| 🔧 可执行性 | 20 | 脚本语法、依赖声明、错误处理 |
| 🌏 本地化质量 | 20 | 中文触发词、中文注释、术语对照 |

详细评分标准见 `references/quality-rubric.md`。

## 最佳实践

详见 `references/best-practices.md`。

## 模板

- 简单 skill 模板：`references/templates/simple-skill.md`
- 复杂 skill 模板：`references/templates/complex-skill.md`
- Pipeline 模板：`references/templates/pipeline-skill.md`
