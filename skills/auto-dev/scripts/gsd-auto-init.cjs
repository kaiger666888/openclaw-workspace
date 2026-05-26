#!/usr/bin/env node
/**
 * GSD Auto-Init — 无交互式初始化 GSD 项目
 *
 * 绕过 /gsd:new-project 的 AskUserQuestion 交互式提问，
 * 直接用 gsd-tools.cjs 创建所有配置文件。
 *
 * 用法: node gsd-auto-init.cjs --name "项目名" --idea "项目描述" [--cwd 目录]
 *
 * 输出:
 *   - .planning/config.json  (工作流配置)
 *   - .planning/PROJECT.md   (项目上下文)
 *   - .planning/STATE.md     (项目状态)
 *   - decisions.json         (所有问答记录，供用户审阅)
 */

const fs = require("fs");
const path = require("path");
const { execSync } = require("child_process");

// ─── 参数解析 ───
const args = process.argv.slice(2);
let projectName = "";
let projectIdea = "";
let cwd = process.cwd();

for (let i = 0; i < args.length; i++) {
  if (args[i] === "--name" && args[i + 1]) projectName = args[++i];
  else if (args[i] === "--idea" && args[i + 1]) projectIdea = args[++i];
  else if (args[i] === "--cwd" && args[i + 1]) cwd = args[++i];
}

if (!projectName || !projectIdea) {
  console.error("Usage: node gsd-auto-init.cjs --name '项目名' --idea '项目描述'");
  process.exit(1);
}

const GSD_TOOLS = path.join(
  process.env.HOME,
  ".claude/get-shit-done/bin/gsd-tools.cjs"
);

function run(cmd) {
  try {
    return execSync(cmd, { cwd, encoding: "utf-8", stdio: ["pipe", "pipe", "pipe"] }).trim();
  } catch (e) {
    return e.stdout?.trim() || e.message;
  }
}

// ─── 默认配置决策 (模拟 /gsd:new-project 的所有交互问答) ───
const decisions = {
  // Step 2: Brownfield
  Q_brownfield: {
    question: "检测到已有代码，是否先 map codebase?",
    options: ["Map codebase first (Recommended)", "Skip mapping"],
    answer: "Skip mapping",
    rationale: "自动模式假设 greenfield",
  },
  // Step 2a / Step 5: Config Round 1
  Q_mode: {
    question: "工作模式?",
    options: ["YOLO (Recommended)", "Interactive"],
    answer: "YOLO",
    rationale: "OpenClaw 自动化场景，无需人工确认",
  },
  Q_granularity: {
    question: "范围切分粒度?",
    options: ["Coarse (3-5 phases)", "Standard (5-8 phases)", "Fine (8-12 phases)"],
    answer: "Standard",
    rationale: "平衡的 phase 大小，适合大多数 MVP",
  },
  Q_execution: {
    question: "并行执行 plans?",
    options: ["Parallel (Recommended)", "Sequential"],
    answer: "Parallel",
    rationale: "独立 plans 并行执行加快速度",
  },
  Q_git_tracking: {
    question: "将 planning docs 提交到 git?",
    options: ["Yes (Recommended)", "No"],
    answer: "Yes",
    rationale: "版本控制跟踪规划文档变更",
  },
  // Step 5: Config Round 2
  Q_research: {
    question: "每个 phase 前是否研究?",
    options: ["Yes (Recommended)", "No"],
    answer: "Yes",
    rationale: "调查领域、发现模式、避免踩坑",
  },
  Q_plan_check: {
    question: "验证 plans 是否能达成目标?",
    options: ["Yes (Recommended)", "No"],
    answer: "Yes",
    rationale: "执行前发现计划缺陷",
  },
  Q_verifier: {
    question: "每个 phase 后验证交付物?",
    options: ["Yes (Recommended)", "No"],
    answer: "Yes",
    rationale: "确认交付物符合 phase 目标",
  },
  Q_ai_models: {
    question: "AI 模型配置?",
    options: ["Balanced (Recommended)", "Quality", "Budget", "Inherit"],
    answer: "Balanced",
    rationale: "质量/成本平衡，使用 Sonnet 级别",
  },
  // Step 6: Research
  Q_research_decision: {
    question: "是否在定义需求前先研究生态系统?",
    options: ["Research first (Recommended)", "Skip research"],
    answer: "Research first",
    rationale: "自动模式默认开启研究",
  },
  // Step 7: Requirements
  Q_requirements_approval: {
    question: "需求定义是否正确?",
    options: ["Approve", "Adjust"],
    answer: "Approve",
    rationale: "自动模式自动批准需求",
  },
  // Step 8: Roadmap
  Q_roadmap_approval: {
    question: "路线图结构是否合适?",
    options: ["Approve", "Adjust phases", "Review full file"],
    answer: "Approve",
    rationale: "自动模式自动批准路线图",
  },
};

// ─── Step 1: Init ───
console.log("━━━ Step 1: 检查项目状态 ━━━");
const initResult = JSON.parse(run(`node "${GSD_TOOLS}" init new-project`));
console.log("Init:", JSON.stringify(initResult, null, 2));

if (initResult.project_exists) {
  console.error("项目已存在，使用 /gsd:progress 检查进度");
  process.exit(1);
}

if (!initResult.has_git) {
  run("git init");
  console.log("Git 初始化完成");
}

// ─── Step 2a/5: 创建 config.json ───
console.log("\n━━━ Step 2: 创建配置 ━━━");
const configResult = JSON.parse(
  run(
    `node "${GSD_TOOLS}" config-new-project '${JSON.stringify({
      mode: "yolo",
      granularity: "standard",
      parallelization: true,
      commit_docs: true,
      model_profile: "balanced",
      workflow: {
        research: true,
        plan_check: true,
        verifier: true,
        nyquist_validation: true,
        auto_advance: true,
      },
    })}'`
  )
);
console.log("Config:", JSON.stringify(configResult));

// Set auto_chain_active for autonomous mode
run(`node "${GSD_TOOLS}" config-set workflow._auto_chain_active true`);

// ─── Step 4: 创建 PROJECT.md ───
console.log("\n━━━ Step 3: 创建 PROJECT.md ━━━");
const planningDir = path.join(cwd, ".planning");
fs.mkdirSync(planningDir, { recursive: true });

const today = new Date().toISOString().split("T")[0];
const projectMd = `# ${projectName}

## Core Value

${projectIdea}

## What This Is

${projectIdea}

## Context

- **Initiated**: ${today}
- **Mode**: Autonomous (OpenClaw auto-dev)
- **Type**: Greenfield MVP

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] Core functionality as described above
- [ ] Basic user interface/experience
- [ ] Data persistence
- [ ] Error handling

### Out of Scope

- Advanced features — v2
- Multi-language support — not needed for MVP
- Mobile native app — web first

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Auto-config via OpenClaw | Non-interactive setup for ACPX | — Pending |
| YOLO mode | Autonomous execution without approval gates | — Pending |
| Standard granularity | Balanced phase size for MVP | — Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

---
*Last updated: ${today} after initialization*
`;

fs.writeFileSync(path.join(planningDir, "PROJECT.md"), projectMd);
console.log("PROJECT.md 已创建");

// ─── 初始化 STATE.md ───
const stateMd = `# Project State

## Current Position
- **Phase**: Pre-planning
- **Status**: Initialized
- **Updated**: ${today}

## Decisions Log
| Date | Decision | Context |
|------|----------|---------|
| ${today} | Auto-initialized via OpenClaw | Non-interactive setup |

## Blockers
(none)

## Quick Tasks Completed
| Date | Task | Summary |
|------|------|---------|
`;
fs.writeFileSync(path.join(planningDir, "STATE.md"), stateMd);
console.log("STATE.md 已创建");

// ─── 生成 CLAUDE.md ───
run(`node "${GSD_TOOLS}" generate-claude-md`);

// ─── Git 提交 ───
run(`node "${GSD_TOOLS}" commit "chore: initialize project via OpenClaw auto-dev" --files .planning/PROJECT.md .planning/config.json .planning/STATE.md CLAUDE.md 2>/dev/null || echo "commit skipped"`);

// ─── 输出问答记录 ───
console.log("\n━━━ 交互问答记录 ━━━");
const qaLog = {
  project: projectName,
  idea: projectIdea,
  timestamp: new Date().toISOString(),
  total_questions: Object.keys(decisions).length,
  decisions: decisions,
};

const qaPath = path.join(planningDir, "Q&A-LOG.json");
fs.writeFileSync(qaPath, JSON.stringify(qaLog, null, 2));
console.log(`Q&A 记录已保存到: ${qaPath}`);

// 打印所有问答
for (const [key, d] of Object.entries(decisions)) {
  console.log(`\nQ: ${d.question}`);
  d.options.forEach((opt) => {
    console.log(`  ${opt === d.answer ? "✓" : " "} ${opt}`);
  });
  console.log(`  → ${d.answer} (${d.rationale})`);
}

console.log("\n━━━ 初始化完成 ━━━");
console.log(`\n下一步: 运行 /gsd:autonomous 或让 Claude Code 执行研究→需求→路线图流程`);
console.log(`项目目录: ${cwd}`);
