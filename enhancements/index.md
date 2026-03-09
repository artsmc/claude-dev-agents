# Claude Dev Agents: Framework Fixes

**Date:** 2026-03-09
**Source:** [research.md](./research.md) — OpenDev paper analysis applied to actual framework pain points

---

## What to Do, in What Order

### Fix 1: Foundation (PM-DB, Hooks, Health Check)
**Spec:** [fix-foundation/spec.md](./fix-foundation/spec.md) | **Effort:** Half day | **6 tasks**

Key findings from research:
- `pm.db` is a phantom file (0 bytes). Real database is `projects.db` (1.7MB, 25 tables)
- Hooks in `hooks/pm-db/` are manual utilities, NOT wired to Claude Code events
- No health check exists — failures are silent

What to do:
1. Delete phantom `pm.db`, fix all references to point at `projects.db`
2. Document hooks as explicit-call utilities (not event-driven)
3. Create `scripts/health-check.sh` — validates DB, hooks, Memory Bank

**Do this FIRST.** Everything else depends on the foundation being verified.

---

### Fix 2: Shadow Git Snapshots
**Spec:** [fix-shadow-git/spec.md](./fix-shadow-git/spec.md) | **Effort:** Half day | **7 tasks**

Safety net before we touch agent definitions. PreToolUse hook creates a git branch snapshot before every Write/Edit operation. One bash script, zero dependencies.

What to do:
1. Create `hooks/shadow-snapshot.sh` (script is ready to copy-paste from spec)
2. Add `PreToolUse` hook to `settings.json`
3. Auto-cleanup branches older than 24h

**Do this SECOND.** Gives us rollback protection for all subsequent changes.

---

### Fix 3: Working Memory for Teams
**Spec:** [fix-working-memory/spec.md](./fix-working-memory/spec.md) | **Effort:** Half day | **5 tasks**

Shared markdown file per team so agents stop starting from zero. No infrastructure — just a file convention.

What to do:
1. Create `~/.claude/working-memory/` directory
2. Update `team-lead.md` to create/delete working memory files
3. Convention: agents read on start, append decisions/discoveries as they work

---

### Fix 4: Standardize + Modularize Agent Definitions
**Spec:** [fix-agent-definitions/spec.md](./fix-agent-definitions/spec.md) | **Effort:** 3 days | **31 tasks across 7 phases**

The biggest fix. Current state:
- 7/19 agents over 20KB (security-auditor at 41KB burns ~40K tokens just loading)
- Only 11/19 have self-check patterns
- 6/19 have no YAML frontmatter
- 3/19 have name/filename mismatches
- No agent uses Haiku, 4 agents on Opus that should be Sonnet

What to do:
1. Define standard format: frontmatter (name, model, tools) + Role + Confidence Protocol + Core Expertise + Self-Verification
2. Split 3 bloated agents into core + modules (security-auditor, mastra-core-developer, technical-writer)
3. Assign models: 6 agents → Opus, 13 agents → Sonnet
4. Add tool restrictions to all 19 agents
5. Fix all name mismatches

---

### Fix 5: Memory Bank Refresh
**Spec:** [fix-memory-bank/spec.md](./fix-memory-bank/spec.md) | **Effort:** 2 hours | **10 tasks**

Memory Bank is 27 days stale. `activeContext.md` references Feb 2026 state. `productContext.md` has template artifacts. `progress.md` counts 17 agents when 19+ exist.

What to do:
1. Update each of the 6 files with current state
2. Add `Last Updated: YYYY-MM-DD` to every file
3. Add staleness check to health script

---

## Dependencies

```
Fix 1 (Foundation) ──→ Fix 2 (Shadow Git) ──→ Fix 4 (Agent Definitions)
                   ──→ Fix 3 (Working Memory)
                   ──→ Fix 5 (Memory Bank)
```

Fix 1 first (verify foundation). Fix 2 second (safety net). Fixes 3, 4, 5 can run in parallel after that.

---

## Success Criteria

| Check | Command | Expected |
|-------|---------|----------|
| No phantom pm.db | `ls ~/.claude/pm.db` | "No such file" |
| Health check passes | `~/.claude/scripts/health-check.sh` | Exit 0, all green |
| Shadow snapshots work | `git branch --list 'shadow/*'` | Branches exist after Write ops |
| Working memory created on team start | `ls ~/.claude/working-memory/` | File exists during team run |
| All agents have frontmatter | `grep -L '^---' ~/.claude/agents/*.md` | No output (all have it) |
| No agent over 20KB | `find ~/.claude/agents/ -maxdepth 1 -size +20k` | No output |
| All agents have model field | `grep -L '^model:' ~/.claude/agents/*.md` | No output |
| Memory Bank not stale | `find ~/.claude/memory-bank -mtime +7 -name "*.md"` | No output |

---

## What We're NOT Doing (and Why)

| Skipped | Reason |
|---------|--------|
| Custom context compaction | Claude Code already compresses context at platform level |
| Self-critique pre-action phase | Quality gates exist post-action; no evidence of gap |
| Event-driven anti-fade reminders | Subagents get fresh context; team lead fix is simpler |
| Complex tool restriction enforcement | Can't modify Claude Code tool schemas; instructions-based is feasible |
| PM-DB schema migrations | Database already has 25 tables; just fix the file reference |
| FedRAMP audit trails | Not relevant for the framework itself |

---

*5 fixes. ~5 days. Grounded in observed problems, not paper-inspired features.*
