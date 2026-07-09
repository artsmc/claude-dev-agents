# /document-hub-update

> Comprehensive review and update of the documentation hub (`cline-docs/`). Analyzes recent code changes, detects drift, validates structure, and proposes specific updates to keep documentation synchronized with the codebase.

## What it does

The write counterpart to `/document-hub-analyze`. It validates the hub, analyzes git history since the last doc update (or runs full drift analysis in non-git projects), scopes the update by drift severity, proposes specific prioritized edits to the four core files, applies them after your approval, and re-validates the result.

## When it triggers

- "Update the docs" / "sync documentation with code"
- "Docs are outdated"
- After completing a major feature or refactor
- After dependency changes
- Monthly documentation maintenance

## Usage

```
/document-hub-update
```

No modes or flags. Proposed edits are presented for approval before anything is written. Drift thresholds scope the work: <0.15 minor updates, 0.15-0.35 focused updates, >0.35 comprehensive review.

Helper scripts (`analyze_changes.py`, `detect_drift.py`, `validate_hub.py`, `extract_glossary.py`) are invoked from the canonical copy in `document-hub-initialize/scripts/` (2026-07 dedup) — this skill ships no scripts or references of its own.

## Context cost

Description always in context (~0.45k chars); SKILL.md body loads on trigger (~2.9k chars); no `references/` in this skill.

## Files

| File | Purpose |
|------|---------|
| `SKILL.md` | Update strategy decision tree + apply/validate workflow |

## Related skills

- `/document-hub-analyze` — read-only audit; run it first when you only want a diagnosis
- `/document-hub-read` — quick summary of current docs
- `/document-hub-initialize` — bootstrap the hub (and canonical home of the shared scripts)
- `/memory-bank-update` — the other Brain system: updates session/progress state, not architecture docs
