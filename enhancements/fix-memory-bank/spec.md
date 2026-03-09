# Fix 5: Memory Bank Refresh Protocol

## Problem

Memory Bank files reflect state as of 2026-02-10 (last explicit date found). Today is 2026-03-09 — 27 days of drift. Agents reading these files receive outdated context that leads to wrong decisions, such as believing only 17 agents exist when CLAUDE.md now describes 25+, or expecting "database-schema-specialist" and "devops-infrastructure" agents that were listed as "remaining to build" but may now exist.

Specific evidence from audit:
- `activeContext.md` lists "Remaining High-Priority Agents" (database-schema-specialist, devops-infrastructure) as uncreated — but `agents/` directory has `strategic-planner.md`, `team-lead.md`, `mastra-framework-expert.md`, `express-api-developer.md` (all untracked per git status).
- `progress.md` counts "17 agents" — git status shows at least 4 new untracked agent files.
- `techContext.md` says "Python 3.8+" and "future migration to OpenCode" as primary stack — but CLAUDE.md shows primary project is an Nx monorepo with Express/Next.js/Mastra. The Memory Bank describes the *framework itself*, not the actual development target.
- `projectbrief.md` scope says "Eventually port to OpenCode" — no mention of the AIForge low-code builder which is the active development focus.
- `systemPatterns.md` is the deepest file and contains the most durable content (architecture, design patterns). Least stale.
- `productContext.md` mentions `remote-control-builder` skill as a feature — but this conflicts with CLAUDE.md's actual agent list. Content is framework-self-referential, not AIForge-aware.
- No file contains a `Last Updated` timestamp — impossible to know age of any section.

## Current State Audit

| File | Last Updated | Status | Specific Issues |
|------|-------------|--------|-----------------|
| `projectbrief.md` | No timestamp | STALE | Describes "Claude Skills Framework" only; AIForge/Nx monorepo missing entirely. OpenCode migration listed as primary goal — superseded by CLAUDE.md. |
| `productContext.md` | No timestamp | STALE | Skills/features list accurate for framework but does not reflect AIForge platform work. `remote-control-builder` listed as key feature — not in CLAUDE.md agents. |
| `systemPatterns.md` | No timestamp | CURRENT (mostly) | Architecture patterns, design decisions, and anti-patterns are durable and correct. Agent Context Caching section valid. |
| `techContext.md` | No timestamp | PARTIALLY STALE | Python stdlib-only constraint accurate for tools; but omits Node 20+, Express 5, Next.js 16, Mastra as primary stack. PM-DB schema at Migration 006 — may be current. |
| `activeContext.md` | 2026-02-10 (implicit) | STALE | Lists database-schema-specialist and devops-infrastructure as "remaining to build" — likely already created. Agent count says 17. "Next Steps" section reflects Feb 2026 state. |
| `progress.md` | 2026-02-10 (implicit) | STALE | Agent count 17 outdated. "Next Milestone" section still references Feb 2026 work. "What's Left" checklist not updated post-Feb. |

## Refresh Checklist

### projectbrief.md
- Add section: "Active Development Context — AIForge Nx Monorepo" with path `/home/artsmc/applications/low-code`
- Revise "Core Purpose" to reflect dual scope: (1) Claude Skills Framework, (2) AIForge platform dev
- Remove or deprioritize OpenCode migration as primary goal

### productContext.md
- Verify `remote-control-builder` skill still exists in `/home/artsmc/.claude/skills/`
- Add note that Memory Bank serves two contexts: framework self-management + AIForge feature development

### systemPatterns.md
- No content changes required — review for accuracy only
- Add `Last Updated: 2026-03-09` header

### techContext.md
- Add AIForge tech stack section: Node 20+, Express 5, Next.js 16.1.6, Mastra, Prisma, Drizzle
- Verify PM-DB migration version is still 006 (check `migrations/` directory)
- Add `Last Updated: 2026-03-09` header

### activeContext.md
- Recount agents in `/home/artsmc/.claude/agents/` directory (actual count)
- Move completed "Planned Agent Additions" to a "Completed" section or remove
- Update "Next Steps" to reflect March 2026 state (enhancements round)
- Add `Last Updated: 2026-03-09` header

### progress.md
- Update agent count metric (currently 17 — verify actual count)
- Archive or move Feb 2026 milestones to a "Historical" section
- Update "Current Status" and "Next Milestone" sections
- Add `Last Updated: 2026-03-09` header

## Staleness Prevention

### Timestamp Convention
Every Memory Bank file must have this header line updated on each edit:
```
Last Updated: YYYY-MM-DD
```

### Health Check Integration
Flag stale files (older than 7 days) with this one-liner:
```bash
find /home/artsmc/.claude/memory-bank -name "*.md" -mtime +7 -printf "STALE: %f (last modified %TD)\n"
```

Run this at the start of any Memory Bank update skill invocation.

## Task List

1. Run health check one-liner to establish current file modification timestamps
2. Count actual agents in `/home/artsmc/.claude/agents/` directory
3. Verify which "planned" agents (database-schema-specialist, devops-infrastructure) now exist
4. Update `activeContext.md` — correct agent count, update Next Steps, add timestamp
5. Update `progress.md` — correct agent count, archive Feb 2026 milestones, add timestamp
6. Update `projectbrief.md` — add AIForge scope, revise OpenCode framing, add timestamp
7. Update `techContext.md` — add AIForge stack, verify PM-DB migration version, add timestamp
8. Review `productContext.md` — verify remote-control-builder exists, add AIForge context note, add timestamp
9. Review `systemPatterns.md` — confirm accuracy, add timestamp only
10. Add health check one-liner to `memory-bank-update` skill invocation instructions
