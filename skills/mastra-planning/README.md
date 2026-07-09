# /mastra-planning

> Strategic planning and team orchestration for Mastra development - analyzes tasks, designs team compositions, creates execution plans, and coordinates agent splits

## What it does

Meta-skill for planning Mastra work rather than writing Mastra code: detects which domains a task touches (agents, workflows, RAG, memory, evals, streaming, deploy, MCP, workspace), classifies complexity (Level 1-3), picks from seven pre-built team composition templates, breaks work into parallel task groups, and injects the right `mastra-*` satellite skills into agent prompts. One of the ten satellites around `/mastra-dev`.

## When it triggers

- "Plan this Mastra feature before we build"
- "How should we split this Mastra work across agents?"
- "What team composition for a RAG + workflow build?"
- "Which mastra skills does this task need?"

## Usage

```bash
/mastra-planning
```

No flags. On-demand guide pattern: `SKILL.md` is a thin stub; the full guide is printed by `bash skill.sh`.

## Context cost

Description always in context (~180 chars); SKILL.md body loads on trigger (~0.9k chars); full guide via `skill.sh` (~13k chars) only when executed.

## Files

| File | Purpose |
|---|---|
| `SKILL.md` | Frontmatter + stub (~0.9k chars) |
| `skill.sh` | Prints the full planning/orchestration guide (~13k chars) |

## Related skills

- `/mastra-dev` — CLI hub; this skill decides which of its satellites a team needs
- `/start-phase-plan` and `/start-phase-execute` — the general-purpose planning/execution pipeline this feeds into
- `/spec-plan` — upstream feature spec work before Mastra-specific planning
