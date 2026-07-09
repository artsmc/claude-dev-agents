---
name: memorybank-update
description: Review and update Memory Bank files. Full mode reads all 6 files and proposes targeted updates; --quick mode (formerly memory-bank-sync) updates only activeContext.md + progress.md. Full mode for "update the memory bank", "refresh documentation", "sync all memory bank files", architecture changes, or major milestones. Quick for "quick save", "save my progress", "mark this as done", "update where I left off", or recording a finished task without a full review.
---

# Memory Bank: Update

Comprehensive review and update of entire Memory Bank, with a `--quick` mode (formerly /memory-bank-sync) for fast 2-file saves.

**Helper Scripts Available:**
- `scripts/validate_memorybank.py` - Pre/post validation
- `scripts/detect_stale.py` - Find outdated info
- `scripts/extract_todos.py` - Extract action items
- `scripts/sync_active.py` - Fast 2-file update (quick mode)

## Quick Mode (--quick)

Fast sync of activeContext.md + progress.md ONLY — skips the full 6-file review below. Use after individual tasks, for a quick save before ending a session, or minor progress updates. NOT for architecture changes (run full mode).

Does NOT touch: projectbrief, productContext, techContext, systemPatterns.

```bash
python3 scripts/sync_active.py /path/to/project \
  --active '{"Current Focus": "...", "Learnings": "..."}' \
  --progress '{"What'\''s Working": "- Finished task"}' \
  --append
```

Full quick-mode procedure, output format, and performance notes: `references/quick-mode.md`.

## Full Workflow

### 1. Announce
"Understood. Initiating a full Memory Bank review and update."

### 1.5. Health Check (Staleness Detection)
```bash
find /home/artsmc/.claude/memory-bank -name "*.md" -mtime +7 -printf "STALE: %f (last modified %TD)\n"
```
Flag any files older than 7 days for priority attention. Every file must have a `Last Updated: YYYY-MM-DD` line after its title.

### 2. Validate
```bash
python3 scripts/validate_memorybank.py /path/to/project
```
Fix any errors before proceeding.

### 3. Detect Staleness
```bash
python3 scripts/detect_stale.py /path/to/project
```
Identify files needing attention.

### 4. Read All Files
Read in hierarchical order:
- projectbrief.md
- productContext.md, techContext.md, systemPatterns.md
- activeContext.md
- progress.md

### 5. Extract TODOs
```bash
python3 scripts/extract_todos.py /path/to/project
```
Get current action items.

### 6. Propose Updates
Based on analysis, propose specific changes to each file.
Focus heavily on:
- **activeContext.md** - Current work, recent changes, next steps
- **progress.md** - Move completed items, update status

### 7. Wait for Confirmation
Present proposal, wait for user approval.

### 8. Apply Updates
Update files based on approved changes.

### 9. Validate Result
```bash
python3 scripts/validate_memorybank.py /path/to/project
```

## When to Use

- After implementing significant changes
- When new patterns/decisions made
- User explicitly requests update
- After multiple tasks completed

See `scripts/README.md` for complete documentation.
