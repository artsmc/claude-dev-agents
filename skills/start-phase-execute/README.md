# /start-phase-execute

> Structured task execution with quality gates, parallel waves, and pm-db tracking — solo or with multi-agent teams (`--team`).

## What it does

Executes a task list (usually produced by `/spec-plan` and refined by `/start-phase-plan`) through a five-phase workflow: setup with resume detection (filesystem + pm-db + git), mandatory planning documents (delegation plan, wave decomposition, system-changes impact analysis), wave-based task execution via spawned agents, a hard lint/build quality gate plus commit after every task, and a closeout summary with pm-db tracking. Independent tasks run as parallel waves; same-file conflicts force sequential order.

## When it triggers

- "Execute these tasks" / "run the implementation" / "execute the plan"
- "Start building" from an approved plan or task list
- "Execute with a team" / "run tasks in parallel with agents"
- `/start-phase execute <task-list.md>` or the legacy `/start-phase-execute-team`
- "Resume the phase" / "pick up where execution left off" (resume detection in Phase 1)

## Usage

```bash
/start-phase execute /path/to/task-list.md
/start-phase execute /path/to/task-list.md "Focus on type safety"   # extra instructions for every task
/start-phase execute /path/to/task-list.md --team                    # force team mode
/start-phase execute /path/to/task-list.md --sequential              # force solo mode
```

Default mode is `auto`: team mode self-enables at 7+ tasks.

## Team mode (`--team`) — formerly /start-phase-execute-team

The standalone team skill was merged in as a mode (2026-07 refactor). It creates a `phase-execution` team (`TeamCreate`/`TaskCreate` with blocker wiring), spawns one agent per task per wave, and each agent claims, executes, passes its own quality gates, commits, and marks complete. Expect ~3x tokens for 1.5-2x wall-clock speed — worth it for multi-module features, wasteful for single-file work.

Team mode is governed by the **Lean Orchestrator protocol** (`references/lean-orchestrator.md`), a mandatory cost discipline derived from 30 days of mined session data (workers were only ~15% of cost; the waste was the parent re-reading fat context 50-100x per turn):

- Workers default to Sonnet/medium; per-task escalation only for ambiguity, cross-cutting design, or security (Rule 1 routing table)
- Spawn prompts are scoped snapshots — goal, input *paths* (never pasted blobs), constraints, acceptance, output contract (Rule 2)
- Workers return a compact report; full detail goes to files in `planning/task-updates/` (Rule 3)
- Parent keeps ≤~30k tokens of accumulated state, dispatches each wave in one message, checkpoints to task-list.md/pm-db between waves (Rule 4)
- Retries get the same scoped snapshot + specific failure evidence, never parent history (Rule 5)
- **Rule 6, the Wave Gate:** a wave is done only when every worker's return is collected AND the verification gate actually ran — the parent never ends its turn or session with workers in flight

Benchmark (naive vs lean fan-out on the same feature): **quality parity 6/6, parent tokens -67%**. The first lean run scored 1/6 purely from ending with workers in flight — hence Rule 6 is hard.

## Context cost

Description always in context (~530 chars); SKILL.md body loads on trigger (~10k chars); references/ load on demand: lean-orchestrator.md (~8.5k), team-mode.md (~7k), team-mode-examples.md (~18.5k), planning-docs.md (~2.3k), tracking.md (~2.3k).

## Files

| File | Purpose |
|---|---|
| `SKILL.md` | Five-phase workflow, team-mode summary, quality gates |
| `references/lean-orchestrator.md` | Canonical cost-discipline protocol for --team (Rules 1-6 + evidence) |
| `references/team-mode.md` | Full team procedure, mode detection, error recovery |
| `references/team-mode-examples.md` | Pseudocode, agent spawn-prompt template, worked 7-task example |
| `references/planning-docs.md` | Templates for the three Phase 2 planning documents |
| `references/tracking.md` | pm-db hook integration (`~/.claude/hooks/pm-db/`) |
| `evals/evals.json` | Execution, resume, and parallel-wave evals |
| `evals/start-phase-execute-team-routing-eval.json` | Routing eval for the merged team trigger |

## Related skills

- `/start-phase-plan` — Mode 1: strategic planning + human approval; run it first for non-trivial work
- `/feature-new` — end-to-end feature workflow that orchestrates spec-plan → start-phase-plan → this skill
- `/pm-db` — dashboard for the phase/task runs this skill records
- `/research-gated-build-plan` — decides whether/how to enter this execution pipeline at all
