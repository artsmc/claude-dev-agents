# /document-hub-read

> Read and summarize the current state of the documentation hub (`cline-docs/`). Quick overview of system architecture, module responsibilities, technology stack, and glossary terms.

## What it does

Reads all four documentation hub files (`systemArchitecture.md`, `keyPairResponsibility.md`, `glossary.md`, `techStack.md`), validates the hub structure, and presents one organized summary — architecture overview, key modules, tech stack, glossary term count, plus any gaps or warnings. Read-only: it never modifies anything. If the hub doesn't exist, it points you to `/document-hub-initialize`.

## When it triggers

- "What does this project do?"
- "Show me the docs" / "summarize the documentation"
- "Explain the architecture of this project"
- Onboarding to an unfamiliar repo
- Before starting feature work, to load project context

## Usage

```
/document-hub-read
```

No modes or flags. Runs `validate_hub.py`, reads the four files, and prints a structured summary (format defined in `references/output-format.md`).

Helper scripts are invoked from the canonical copy in `document-hub-initialize/scripts/` (2026-07 dedup) — this skill ships no scripts of its own.

## Context cost

Description always in context (~0.5k chars); SKILL.md body loads on trigger (~4.4k chars); `references/output-format.md` (~2.2k chars) loads on demand.

## Files

| File | Purpose |
|------|---------|
| `SKILL.md` | Read-and-summarize workflow + decision tree |
| `references/output-format.md` | Template for the summary output |

## Related skills

- `/document-hub-initialize` — create the hub (and canonical home of the shared scripts)
- `/document-hub-analyze` — deep drift/quality audit, not just a summary
- `/document-hub-update` — actually change the docs
- `/memory-bank-read` — the other Brain system: session/task state rather than architecture docs
