# /memory-bank-read

> Quick overview of Memory Bank state. Validates structure, reads all 6 files in hierarchical order, and summarizes with staleness warnings.

## What it does

Read-only status check on a project's `memory-bank/`. Runs structure validation and staleness detection, reads the six files in dependency order (projectbrief → product/tech/patterns → activeContext → progress), and presents a single summary: project purpose, stack, architecture decisions, current focus, blockers, next steps, and a health check with staleness score. Makes no changes to any file.

## When it triggers

- "where did I leave off"
- "what's the project status" / "catch me up"
- "what was I working on"
- "summarize the memory bank"
- Returning to a project after time away, or checking whether the memory bank needs updating

## Usage

```
/memory-bank-read
```

No flags. This is the pure status-recall path — `/feature-new --continue` and similar resume flows defer to it when the user only wants to know where things stand.

## Context cost

Description always in context (~360 chars); SKILL.md body loads on trigger (~1.4k chars); no `references/` — scripts run as bash, not loaded as context.

## Files

| Path | Purpose |
|---|---|
| `SKILL.md` | Validate → staleness check → read in order → summary format |
| `scripts/validate_memorybank.py` | Structure validation |
| `scripts/detect_stale.py` | Staleness scoring and cross-file inconsistency checks |
| `scripts/sync_active.py`, `scripts/extract_todos.py` | Present in the shared scripts dir; used by the other memory-bank skills |
| `scripts/README.md` | Full tool documentation |

All scripts are stdlib-only Python.

## Related skills

- `/memory-bank-update` — actually change the files (full review, or `--quick` save)
- `/memory-bank-initialize` — no `memory-bank/` yet? bootstrap it first
- `/document-hub-read` — same idea for the other Brain system (`cline-docs/`, architecture-focused)
