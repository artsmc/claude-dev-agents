# /mastra-evals

> Mastra Evaluation and Testing guide - built-in scorers, custom scorers, datasets, experiments, and CI integration

## What it does

Loads validated patterns for measuring agent quality with Mastra: the 17 built-in scorer factories (e.g. `createAnswerRelevancyScorer()`), custom scorers with `createScorer()`, `runEvals({ target, scorers, data })`, dataset management, experiment comparison, agent-level scorer sampling, and CI pipeline integration. One of the ten satellite guides routed to by `/mastra-dev`.

## When it triggers

- "Add evals/scorers to my Mastra agent"
- "Write a custom scorer for this output"
- "Benchmark agent responses against a dataset"
- "Run Mastra evals in CI"
- "Which built-in scorer fits hallucination/relevancy checks?"

## Usage

```bash
/mastra-evals
```

No flags. On-demand guide pattern: `SKILL.md` is a thin stub; the full guide is printed by `bash skill.sh`.

## Context cost

Description always in context (~130 chars); SKILL.md body loads on trigger (~0.9k chars); full guide via `skill.sh` (~16k chars) only when executed.

## Files

| File | Purpose |
|---|---|
| `SKILL.md` | Frontmatter + stub (~0.9k chars) |
| `skill.sh` | Prints the full evals/testing guide (~16k chars) |

## Related skills

- `/mastra-dev` — CLI hub that routes here for eval concepts
- `/mastra-agents` — the agents being scored; scorer config lives on the agent
- `/skill-creator` — for evaluating Claude Code skills themselves, not Mastra agents
