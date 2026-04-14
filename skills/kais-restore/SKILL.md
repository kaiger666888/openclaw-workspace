---
name: kais-restore
description: "从 skills-manifest.json 恢复所有独立管理的 skill 仓库。触发词：恢复skill, restore skills, 克隆skill, 新机器初始化, migrate workspace"
---

# kais-restore

从 `skills-manifest.json` 恢复所有独立管理的 skill 仓库到本地。

## 触发场景

- 新机器初始化 workspace 后
- 误删了某个 skill 目录需要恢复
- 从备份恢复后补全 skill 仓库

## 使用流程

### 步骤 1：检查环境

```bash
# 确认 workspace 存在
ls ~/.openclaw/workspace/skills-manifest.json

# 确认 git 和 gh CLI 可用
git --version && gh auth status
```

如果 `skills-manifest.json` 不存在，提示用户先从 GitHub 克隆 workspace：
```bash
git clone https://github.com/kaiger666888/openclaw-workspace ~/.openclaw/workspace
```

### 步骤 2：读取清单并恢复

<!-- FREEDOM:low -->
必须按以下顺序执行：

```bash
cd ~/.openclaw/workspace

# 读取清单，逐个克隆
jq -r '.repos | to_entries[] | "\(.key)|\(.value)"' skills-manifest.json | while IFS='|' read -r path url; do
  if [ -d "$path/.git" ]; then
    echo "⏭️  已存在: $path"
  else
    echo "📥 克隆: $path ← $url"
    mkdir -p "$(dirname "$path")"
    git clone "$url" "$path" 2>&1 | sed 's/^/   /'
  fi
done
```
<!-- /FREEDOM:low -->

### 步骤 3：验证

```bash
# 检查所有 repo 状态
jq -r '.repos | keys[]' ~/.openclaw/workspace/skills-manifest.json | while read -r path; do
  if [ -d "$path/.git" ]; then
    branch=$(git -C "$path" branch --show-current 2>/dev/null)
    echo "✅ $path ($branch)"
  else
    echo "❌ $path (未恢复)"
  fi
done
```

### 步骤 4：汇报

输出恢复结果：
- 总计 N 个仓库
- ✅ 新克隆 X 个
- ⏭️ 已存在 Y 个
- ❌ 失败 Z 个（如有）

## 单个恢复

如果只需要恢复某个特定 skill：

```bash
cd ~/.openclaw/workspace
# 查看清单
jq -r '.repos | to_entries[] | "\(.key) → \(.value)"' skills-manifest.json

# 单个克隆
git clone <url> <path>
```

## 注意事项

- 需要 `jq`（`apt install jq` 或 `brew install jq`）
- SSH 格式的 repo（git@github.com:...）需要 SSH key 配置
- 克隆前会检查目录是否已存在，避免覆盖
