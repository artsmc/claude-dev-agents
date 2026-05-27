---
name: memorybank-sync
description: Fast synchronization of activeContext.md and progress.md only. Lightweight alternative to full update for quick post-task documentation. Use this skill whenever the user says things like "quick save", "save my progress", "update where I left off", "just update progress", "mark this as done", or finishes a task and wants to record it without a full memory bank review. If the user only wants to update 1-2 files (not all 6), use this instead of memory-bank-update.
---

# Memory Bank: Sync

Fast sync of activeContext.md and progress.md after task completion.

**Helper Scripts Available:**
- `scripts/sync_active.py` - Fast update tool
- `scripts/extract_todos.py` - Get next steps

## What It Does

Lightweight update that ONLY touches:
- **activeContext.md** - Update focus, blockers, learnings
- **progress.md** - Move completed items

**Does NOT touch:** projectbrief, productContext, techContext, systemPatterns

## When to Use

- After completing individual tasks
- Quick documentation before ending session
- Minor progress updates
- NOT for architecture changes (use `/memory-bank-update` instead)

## Workflow

### 1. Gather Information

What changed:
- Completed tasks?
- New focus area?
- Learnings/insights?
- Blockers encountered?

### 2. Run Sync Tool

```bash
# Update activeContext.md sections
python3 scripts/sync_active.py /path/to/project \
  --active '{"Current Focus": "What working on now", "Learnings": "New pattern discovered"}' \
  --progress '{"What'\''s Working": "- Task that was finished"}' \
  --append
```

Use `--append` to add to existing section content rather than replacing it.

Or extract current TODOs first to understand what to update:
```bash
python3 scripts/extract_todos.py /path/to/project
```

### 3. Verify Updates

Tool returns what changed:
```json
{
  "activeContext": {
    "updated_sections": ["Current Focus", "Learnings"],
    "success": true
  },
  "progress": {
    "updated_sections": ["What's Working"],
    "success": true
  }
}
```

## Performance

- **Speed:** ~2 seconds (vs 5+ for full update)
- **Scope:** 2 files only
- **Use Case:** Frequent updates after tasks

## Example Usage

```bash
# After completing authentication feature
/memory-bank-sync

# Claude runs:
python3 scripts/sync_active.py /path/to/project \
  --active '{"Current Focus": "Adding password reset flow", "Learnings": "- JWT tokens work well with our session management"}' \
  --progress '{"What'\''s Working": "- Implemented user authentication API"}' \
  --append

# Result:
# ✓ activeContext.md updated with new focus and learnings
# ✓ progress.md updated with completed task
```

## Comparison

| Operation | Files Updated | Time | When to Use |
|-----------|---------------|------|-------------|
| **sync** | 2 (active + progress) | ~2s | After each task |
| **update** | All 6 files | ~5s | Major changes |

See `scripts/README.md` for complete documentation.
