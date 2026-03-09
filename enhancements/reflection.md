# Reflection: Round 2

**Date:** 2026-03-09

## Did We Stay Grounded?

Yes. Round 1 produced 7 full spec packages (FRD + FRS + TR + task-list each) for problems we hadn't verified were real. Round 2 started by auditing the actual codebase and found concrete issues:

- `pm.db` is empty — the real database is `projects.db` (different file entirely)
- Hooks aren't wired to Claude Code events — they're manual utilities
- `security-auditor.md` is 41KB — burns half the context budget just loading
- Memory Bank is 27 days stale with template artifacts still in place
- 6/19 agents have no frontmatter, 3 have name mismatches

These are observed facts, not paper-derived hypotheses. Every spec references evidence from the codebase.

## Are the Specs Proportional?

Mostly. The agent definitions spec is 455 lines — justified because it covers 19 agents with per-agent migration plans. The other 4 specs are 86-145 lines each. Compare to Round 1 where every enhancement got 4 documents regardless of complexity.

One concern: the agent definitions spec may still over-prescribe. Some agents might be fine with lighter changes than specified. The phased approach (Group 1 through 5) allows stopping early if diminishing returns appear.

## What Changed Between Rounds

| Aspect | Round 1 | Round 2 |
|--------|---------|---------|
| Number of specs | 7 full packages (28 files) | 5 single docs (5 files) |
| Evidence basis | Paper concepts | Codebase audit findings |
| Estimated tasks | ~105 | ~59 |
| Estimated effort | 4 phases, weeks | ~5 days |
| Cuts made | None (built everything the paper suggested) | Cut 4 enhancements as redundant/unverified |

## Key Discovery: pm.db vs projects.db

The biggest surprise. The framework documentation and CLAUDE.md reference `pm.db`, but the actual working database has always been `projects.db`. This means anyone following the docs (including agents) would query an empty file. This single finding justifies the "fix foundation first" approach — you can't build on infrastructure you haven't verified.

## Remaining Concerns

1. **Tool restrictions via frontmatter**: The agent definitions spec assumes Claude Code respects a `tools:` field in agent .md frontmatter. This needs validation — if Claude Code ignores it, we fall back to instructions-based restrictions only.

2. **Module loading**: The modularization strategy assumes agents can be told "read this file when you need compliance guidance" and they'll actually do it on-demand. In practice, agents may load everything eagerly or skip modules entirely. Needs testing with one agent before committing to all three.

3. **Shadow git on large repos**: The PreToolUse hook runs `git branch` on every Write/Edit. In the `.claude` repo this is fine (~750 files). In large monorepos, the cleanup loop might be slow. Worth testing in the AIForge monorepo context.

## Process Improvement

The "paper as lens, not blueprint" approach worked. The OpenDev paper's lessons about context budgets and eager building directly informed the agent size audit and foundation-first ordering. But we didn't implement the paper's features — we used its principles to diagnose our own problems.

For next time: always audit before speccing. The 30 minutes spent checking `pm.db` tables saved days of work on the wrong database.
