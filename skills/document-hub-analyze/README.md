# /document-hub-analyze

> Deep analysis of codebase vs documentation alignment (`cline-docs/`). Detects drift, identifies undocumented code, extracts missing glossary terms, and provides actionable recommendations without making changes.

## What it does

Runs a read-only, six-phase audit of the documentation hub against the actual codebase: structure validation, module drift (src/ vs docs), technology drift (dependencies vs `techStack.md`), glossary gaps, a 0-100 health score, and prioritized HIGH/MEDIUM/LOW recommendations. It makes no changes — if drift is found, it recommends running `/document-hub-update`.

## When it triggers

- "Are the docs up to date?"
- "Check documentation quality" / "documentation health check"
- "What's missing from the docs?"
- Monthly documentation audits
- A read-only pass before deciding what to update

## Usage

```
/document-hub-analyze
```

No modes or flags. Output follows `references/report-format.md`: health score, drift scores by category, undocumented modules/technologies, ranked glossary gaps, and next steps.

Helper scripts (`validate_hub.py`, `detect_drift.py`, `extract_glossary.py`) are invoked from the canonical copy in `document-hub-initialize/scripts/` (2026-07 dedup) — this skill ships no scripts of its own.

## Context cost

Description always in context (~0.4k chars); SKILL.md body loads on trigger (~4.6k chars); `references/report-format.md` (~3.8k chars) loads on demand.

## Files

| File | Purpose |
|------|---------|
| `SKILL.md` | Six-phase analysis workflow + script invocations |
| `references/report-format.md` | Template for the analysis report |

## Related skills

- `/document-hub-update` — the write counterpart: applies the fixes this skill recommends
- `/document-hub-read` — light summary of the docs, no drift analysis
- `/document-hub-initialize` — create the hub if it doesn't exist yet
- `/architecture-quality-assess` — scores the code's architecture itself; this skill scores docs-vs-code alignment
