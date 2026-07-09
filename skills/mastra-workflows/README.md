# /mastra-workflows

> Mastra Workflow development guide - DAG composition, control flow, suspend/resume, HITL, time travel, state management, and streaming

## What it does

Loads validated patterns for DAG-based workflows with Mastra: `createWorkflow()`/`createStep()`, composition with `.then()`/`.parallel()`/`.branch()`/`.foreach()`/`.map()`/loops/`.sleep()` plus `.commit()`, run management (`createRun()`, `start()`, `cancel()`, `restart()`), suspend/resume with `resumeSchema`, human-in-the-loop approval, time travel debugging, workflow state (`stateSchema`, `setState`), data mapping between steps, and error handling. One of the ten satellite guides routed to by `/mastra-dev`.

## When it triggers

- "Build a multi-step Mastra workflow"
- "Add branching / parallel steps to this workflow"
- "Pause the workflow for human approval" (suspend/resume, HITL)
- "Map output of step A into step B"
- "Debug a failed workflow run / time travel"

## Usage

```bash
/mastra-workflows
```

No flags. On-demand guide pattern: `SKILL.md` is a thin stub; the full guide is printed by `bash skill.sh`.

## Context cost

Description always in context (~150 chars); SKILL.md body loads on trigger (~0.9k chars); full guide via `skill.sh` (~34k chars) only when executed.

## Files

| File | Purpose |
|---|---|
| `SKILL.md` | Frontmatter + stub (~0.9k chars) |
| `skill.sh` | Prints the full workflow development guide (~34k chars) |

## Related skills

- `/mastra-dev` — CLI hub; its `create-workflow` / `add-step` / `show-graph` commands scaffold what this skill teaches
- `/mastra-agents` — agent networks as an alternative orchestration model
- `/mastra-streaming` — streaming workflow run events to a UI
