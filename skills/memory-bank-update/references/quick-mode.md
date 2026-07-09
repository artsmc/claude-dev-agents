# Quick Mode (--quick) — Detailed Procedure

Formerly the standalone `/memory-bank-sync` skill. Fast sync of activeContext.md and progress.md after task completion.

## Scope

Lightweight update that ONLY touches:
- **activeContext.md** - Update focus, blockers, learnings
- **progress.md** - Move completed items

**Does NOT touch:** projectbrief, productContext, techContext, systemPatterns

## When to Use

- After completing individual tasks
- Quick documentation before ending session
- Minor progress updates
- NOT for architecture changes (use full mode instead)

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
/memory-bank-update --quick

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
| **--quick** | 2 (active + progress) | ~2s | After each task |
| **full update** | All 6 files | ~5s | Major changes |

See `scripts/README.md` for complete documentation.
