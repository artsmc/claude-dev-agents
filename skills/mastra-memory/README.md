# /mastra-memory

> Mastra Memory system guide - storage backends, message history, observational memory, working memory, semantic recall, and thread management

## What it does

Loads validated patterns for the Mastra memory system: the `Memory` class with options-based config (not processor classes), storage backends (LibSQLStore, PostgresStore, UpstashStore), `options.lastMessages` history, `options.semanticRecall` (embedding-based), `options.workingMemory` (structured state), `options.observationalMemory` (auto fact extraction), thread management/cloning, and agent integration. One of the ten satellite guides routed to by `/mastra-dev`.

## When it triggers

- "Give my Mastra agent memory across conversations"
- "Set up semantic recall / working memory"
- "Which storage backend for Mastra memory?"
- "Manage or clone conversation threads"
- "Why isn't my agent remembering earlier messages?"

## Usage

```bash
/mastra-memory
```

No flags. On-demand guide pattern: `SKILL.md` is a thin stub; the full guide is printed by `bash skill.sh`.

## Context cost

Description always in context (~150 chars); SKILL.md body loads on trigger (~1k chars); full guide via `skill.sh` (~27k chars) only when executed.

## Files

| File | Purpose |
|---|---|
| `SKILL.md` | Frontmatter + stub (~1k chars) |
| `skill.sh` | Prints the full memory system guide (~27k chars) |

## Related skills

- `/mastra-dev` — CLI hub that routes here for memory concepts
- `/mastra-agents` — attaching memory to agents via the `memory` property
- `/mastra-rag` — embedding-based retrieval over documents rather than conversation history
