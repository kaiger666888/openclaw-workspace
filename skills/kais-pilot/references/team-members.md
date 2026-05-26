# Team Members — Skill Capability Matrix

| Skill | Role | When to Dispatch | Available |
|-------|------|-----------------|-----------|
| brainstorm | Product/Requirements Analyst | Direction unclear, need structured ideation | ✅ |
| claude-code-via-openclaw | Lead Developer | Full projects (research→plan→develop→verify pipeline) | ✅ |
| coding-agent | Quick Developer | Small changes, scripts, one-off tasks, background execution | ✅ |
| thinking-partner | Technical Advisor | Deep problem exploration, complex trade-off analysis | ✅ |

## Default Execution Agent

**默认执行代理：`claude-code-via-openclaw`** — 所有需要代码生成/项目开发的 step 默认使用此 skill，除非用户明确指定其他 skill。

## Dispatch Rules

1. **Any coding/development task** → claude-code-via-openclaw (default)
2. **Small fix or script** → claude-code-via-openclaw (still default; can override with `coding-agent` if speed is critical)
3. **Direction unclear** → brainstorm first, then reassess
4. **Deep technical problem** → thinking-partner for analysis
5. **Multi-phase project** → brainstorm (ideation) → claude-code-via-openclaw (execution)

## Composition Examples

- **Web app from scratch**: brainstorm → claude-code-via-openclaw
- **Bug fix**: claude-code-via-openclaw (solo)
- **Explore an idea**: brainstorm (solo)
- **Complex system design**: thinking-partner → claude-code-via-openclaw
- **Prototype + iterate**: claude-code-via-openclaw (solo)
