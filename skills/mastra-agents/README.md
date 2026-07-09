# /mastra-agents

> Mastra Agent development guide - creation, tools, memory, networks, processors, guardrails, voice, and structured output patterns

## What it does

Loads validated API patterns for building Mastra agents: the `Agent` class constructor, `'provider/model-name'` model strings, tool binding with `createTool()`, memory options, structured output, agent networks via `.network()`, input/output processors and guardrails, human-in-the-loop approval, and voice (TTS/STT). One of the ten satellite guides routed to by `/mastra-dev`.

## When it triggers

- "Create a Mastra agent with tools"
- "How do I get structured output from an agent?"
- "Set up an agent network / supervisor agent"
- "Add guardrails or processors to this agent"
- "Wire memory into my Mastra agent"

## Usage

```bash
/mastra-agents
```

No flags. The skill uses the on-demand guide pattern: `SKILL.md` is a thin stub, and the full guide is printed by running `bash skill.sh` — so the ~29k-char reference costs nothing until you actually invoke the skill.

## Context cost

Description always in context (~140 chars); SKILL.md body loads on trigger (~0.8k chars); full guide via `skill.sh` (~29k chars) only when executed.

## Files

| File | Purpose |
|---|---|
| `SKILL.md` | Frontmatter + stub (~0.8k chars) |
| `skill.sh` | Prints the full agent development guide (~29k chars) |

## Related skills

- `/mastra-dev` — CLI scaffolding hub that routes here for agent API patterns
- `/mastra-memory` — deep dive on the memory system agents attach to
- `/mastra-workflows` — when the orchestration is a DAG, not an agent network
