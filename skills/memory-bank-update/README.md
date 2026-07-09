# /memory-bank-update

> Review and update Memory Bank files. Full mode reads all 6 files and proposes targeted updates; --quick mode (formerly memory-bank-sync) updates only activeContext.md + progress.md.

## What it does

Keeps the Memory Bank synchronized with reality. Full mode validates structure, detects stale files, reads all six files in hierarchical order, extracts TODOs, proposes specific per-file updates, and applies them after user approval. Quick mode skips the review entirely and does a fast 2-file save of `activeContext.md` + `progress.md` via `sync_active.py` — the frequent post-task path.

## When it triggers

Full mode:
- "update the memory bank" / "refresh documentation" / "sync all memory bank files"
- After architecture changes or major milestones

Quick mode:
- "quick save" / "save my progress" / "mark this as done"
- "update where I left off, I'm stopping for the day"
- "record that the migration task is finished — lightweight update only"

## Usage

```
/memory-bank-update            # full 6-file review with approval checkpoint
/memory-bank-update --quick    # 2-file save (formerly /memory-bank-sync)
```

`--quick` only touches activeContext.md and progress.md (~2s vs ~5s+ for full); it never modifies projectbrief, productContext, techContext, or systemPatterns. Architecture changes require full mode.

## Context cost

Description always in context (~460 chars); SKILL.md body loads on trigger (~2.6k chars); `references/quick-mode.md` (~2.4k chars) loads on demand for the detailed quick-mode procedure.

## Files

| Path | Purpose |
|---|---|
| `SKILL.md` | Both modes: quick-mode summary + full 9-step workflow |
| `references/quick-mode.md` | Detailed quick-mode procedure, sync_active.py usage, mode comparison |
| `scripts/` | Symlink to `../memory-bank-initialize/scripts` (validate_memorybank.py, detect_stale.py, extract_todos.py, sync_active.py, README.md) |
| `evals/memory-bank-sync-routing-eval.json` | Routing eval covering the merged /memory-bank-sync triggers |

Tool usage by mode: full mode runs validate → detect_stale → extract_todos → validate again; quick mode runs sync_active (optionally extract_todos first).

## Related skills

- `/memory-bank-read` — read-only summary; use when nothing needs changing
- `/memory-bank-initialize` — create the `memory-bank/` structure in the first place
- `/document-hub-update` — the equivalent for the other Brain system (`cline-docs/`)
- Formerly `/memory-bank-sync` — archived; its behavior is exactly `--quick` mode here
