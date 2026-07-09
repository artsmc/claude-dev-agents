# /feature-new

> Complete feature workflow — from planning to execution with PM-DB tracking. Orchestrates spec-plan → spec-review → start-phase-plan → pm-db → start-phase-execute into one workflow with human checkpoints. `--continue` resumes interrupted feature work from a task-list.md with PM-DB tracking intact.

## What it does

End-to-end feature orchestrator. Chains five skills — spec generation, spec review, execution planning, PM-DB import, and task execution — threading state (feature name, spec dir, task-list path, PM-DB IDs) between them, with human checkpoints after spec-review (if issues) and after phase-plan (always). Pre-flight skip logic detects existing artifacts (task-list.md, phase-summary.md) and asks before regenerating; every failure names the step and gives the exact recovery command.

## When it triggers

- "Build this feature" / "implement this" / "add this capability"
- "New feature: dark mode across the dashboard"
- "Continue the feature" / "pick up where we left off" / "what's left on this feature"
- Resuming a dropped session mid-build
- Pure status recall ("where did I leave off?") → `/memory-bank-read` instead

## Usage

```bash
/feature-new add user authentication            # auto mode: each sub-skill decides
/feature-new add auth --team                    # parallel: passes --team to sub-skills
/feature-new add auth --sequential              # force sequential execution
/feature-new --continue ./job-queue/feature-auth/tasks.md   # resume interrupted work
```

**`--continue` mode** *(formerly the standalone `/feature-continue` skill)*: derives the feature location from the task-list path, queries PM-DB `phase_runs`/`task_runs` for the latest run and completed tasks, then resumes `/start-phase execute` from the first incomplete task — reusing the existing `phase_run_id` (never duplicating), skipping done tasks, keeping quality gates and the git commit sequence. Requires a prior PM-DB import; resumes at task granularity, not mid-task.

## Flow

```
1. spec-plan        → generates tier-appropriate specs
2. spec-review      → validates quality (checkpoint if errors)
3. start-phase-plan → execution plan (user approval, always)
4. pm-db import     → tracking (best-effort, non-blocking)
5. start-phase-execute → builds it, with quality gates + commits
```

## Context cost

Description always in context (~730 chars); SKILL.md body loads on trigger (~10k chars); `references/continue-mode.md` (~8k chars — PM-DB queries, progress detection, per-scenario walkthroughs, error handling) loads on demand in --continue mode.

## Files

| File | Purpose |
|------|---------|
| `SKILL.md` | Orchestration: arg parsing, state tracking, 5 steps, skip logic, error recovery |
| `references/continue-mode.md` | Full --continue detail: queries, hook code, scenarios, error handling |
| `evals/evals.json` | Skill evals |
| `evals/feature-continue-routing-eval.json` | Routing eval for continue-vs-new triggering |

## Related skills

- **/spec-plan, /spec-review, /start-phase-plan, /start-phase-execute, /pm-db** — the five skills this orchestrates; each also works standalone
- **/memory-bank-read** — for status recall without resuming execution
- **/research-gated-build-plan** — run first when it's not yet clear the work should enter execution at all
