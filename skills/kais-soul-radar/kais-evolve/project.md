# Autoresearch Project: kais-soul-radar Prompt Evolution

## Goal
迭代优化灵魂雷达的分析 prompt 模板，使生成的 Story Kernel 在叙事深度、结构化程度和实用性上达到最高水平。

## Metric
- Primary: eval score (higher is better, 0-100)
- Command: python3 kais-evolve/eval.py
- Parse: grep "EVAL_SCORE" output | tail -1

## Scope
- Editable: prompts/*.txt, references/strata-guide.md
- Read-only: SKILL.md, schemas/*, scripts/*, kais-evolve/*

## Constraints
- Time budget: 300 秒（5分钟，包含 LLM 调用）
- Simplicity: prompt 越短越好，相同分数下优先保留更短的 prompt
- No new dependencies: true

## Baseline
- Command: python3 kais-evolve/eval.py --baseline
- Expected metric: 60-70

## Eval 维度（总分 100）

eval.py 会用 LLM 对生成的 Story Kernel 进行评分，维度如下：

| 维度 | 满分 | 评估内容 |
|------|------|----------|
| 结构性公式深度 | 25 | macro_fissure 是否真正捕捉到"结构力量迫使"而非个人叙事 |
| 叙事角度质量 | 25 | narrative_angles 是否新颖、驱动性强、避免套路 |
| 微观裂隙真实感 | 20 | micro_fissure 的人物和场景是否具体、可信、有画面感 |
| 数据可验证性 | 15 | data_points 是否真实可查、非编造 |
| 代际语法冲突（L5时）| 15 | consumption_grammar_clash 是否有洞察力、避免刻板印象 |

## Ideas
1. 在 prompt 中加入"反套路指令"——要求 AI 主动避免常见的叙事模式（逆袭、和解、大团圆）
2. 增加"结构性公式模板"——提供 5-6 种公式句式让 AI 填充
3. 引入"叙事盲区检测"——要求 AI 分析哪些群体/困境被主流叙事忽略
4. 调整 unspeakability 评分标准——使其更精确地区分"不可讨论"的层次
5. 在 L5 prompt 中加入"反例搜索"指令——要求找到代际刻板印象的反例
6. 优化 micro_fissure 的具体度要求——强制要求包含感官细节（声音、气味、温度）
7. 增加"叙事张力公式"——结构性冲突 × 不可言说性 × 个人不可抗拒性 = 张力值

## Experiment Loop

LOOP FOREVER (until human stops you):

1. Read the current git state (branch, commit)
2. Look at results.tsv for what's been tried and what worked
3. Form a hypothesis based on:
   - Previous successful experiments (keep patterns)
   - Previous near-misses (combining partial wins)
   - Prompt engineering best practices
   - The eval dimensions above
4. Implement the change by editing files in the Editable scope
5. git commit with a descriptive message
6. Run: python3 kais-evolve/eval.py
7. Parse the EVAL_SCORE from output
8. Record in results.tsv:
   - If improved by >= 2 points: status=keep, advance
   - If worse or equal: status=discard, git reset
   - If crash: status=crash, log error, fix or skip
9. Go to step 1

## Rules

- NEVER STOP. Keep going until human interrupts.
- NEVER ask "should I continue?" — the answer is always yes.
- NEVER modify files outside the Editable scope.
- NEVER install new dependencies.
- Simplicity wins: shorter prompt for same score > longer prompt for same score.
- Time budget: kill experiments that exceed 300 seconds.
- Each experiment changes ONE aspect of the prompt (A/B testing principle).
- Always test with the SAME test data (cached in kais-evolve/test-data.json) for fair comparison.
- Record what changed in the description column of results.tsv.
