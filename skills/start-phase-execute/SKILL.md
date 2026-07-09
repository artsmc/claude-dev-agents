---
name: start-phase-execute
description: "Structured task execution with quality gates, parallel waves, and pm-db tracking — solo or with multi-agent teams (--team). Use this skill when the user wants to execute a task list, run implementation tasks, start building a feature from a plan, run tasks in parallel with a team of agents, or says things like 'execute these tasks', 'start building', 'run the implementation', 'execute the plan', 'execute with a team', or 'start phase execute'. Also triggers on '/start-phase execute' and '/start-phase-execute-team' commands."
args:
  task_list_file:
    type: string
    description: Path to task list markdown file
    required: true
  extra_instructions:
    type: string
    description: Optional extra context for execution
    required: false
  team_mode:
    type: string
    description: "Team execution mode: auto, enabled (--team), disabled (--sequential)"
    required: false
    default: "auto"
---

# Start-Phase Execute

Execute a task list with parallel waves, agent delegation, and quality gates.

## Usage

```bash
/start-phase execute /path/to/task-list.md
/start-phase execute /path/to/task-list.md "Focus on type safety"
/start-phase execute /path/to/task-list.md --team        # force team mode
/start-phase execute /path/to/task-list.md --sequential  # force solo mode
```

## Workflow Overview

```
Phase 1: Setup        → Read task list, detect resume, create dirs
Phase 2: Plan         → Delegation plan, wave decomposition, impact analysis
Phase 3: Execute      → Run tasks by wave (parallel where possible)
Phase 4: Quality Gate → Lint, build, review after each task
Phase 5: Closeout     → Summary, metrics, archive
```

---

## Team Mode (--team)

*Formerly the standalone `/start-phase-execute-team` skill.*

**When to use:** auto-enables at 7+ tasks in the list; force on with `--team`, force off with `--sequential`. Worth it for complex features (2+ hours sequential) with multiple independent modules — expect ~3x tokens for 1.5-2x speed. Skip for simple changes, routine maintenance, or single-file work.

**Procedure summary:** parse the task list → group tasks into dependency waves (empty wave = circular dependency, abort) → `TeamCreate("phase-execution")` → `TaskCreate` per task, wiring blockers via `TaskUpdate({ addBlockedBy })` → per wave, spawn one agent per task (model: sonnet); each agent claims its task, executes, passes quality gates (hard blocks), self-reviews, commits, and marks complete → team lead polls `TaskList` until the wave completes → verify all tasks `completed` → `SendMessage` shutdown to members, then `TeamDelete`.

In team mode, agents handle Phase 3 execution and their own per-task commits (Phase 4 gates run inside each agent); Phases 1, 2, and 5 are unchanged.

**Lean Orchestrator (mandatory cost discipline):** 30-day mining showed workers are only ~15% of cost — the waste is the parent re-reading fat accumulated context 50–100×/turn (71% of the worst session). So:
- Workers default to **Sonnet at medium effort**; escalate per-task only for ambiguity, cross-cutting design, or security — and down-route fully-specified, self-contained, gate-verified tasks to **Haiku** (benchmarked 6/6 pass, zero escalations; routing table in the reference).
- Spawn prompts are **scoped snapshots** — goal, input *paths* (never pasted blobs; headroom-compress unavoidable large handoffs), constraints, acceptance, output contract.
- Workers return a **compact report** (status, artifact paths, verification evidence, ≤2-sentence notes); full detail goes to files in `{planning_folder}/task-updates/`.
- Parent keeps ≤~30k tokens of accumulated state, dispatches each wave in ONE message, never re-reads worker artifacts it doesn't need, and **checkpoints to task-list.md/pm-db between waves** so the session can `/clear` or resume.
- Retries get the same scoped snapshot + the specific failure evidence — never the parent's history.
- **Wave Gate:** a wave is done only when every worker's return is collected AND the verification gate ran — never end the turn/session with workers in flight (background workers: DONE-markers + bounded polling; timeout = failure with evidence).

**Before executing in team mode, read `references/lean-orchestrator.md`** (the canonical protocol above, with evidence and templates), `references/team-mode.md` (full procedure, mode detection, error recovery, best practices), and `references/team-mode-examples.md` (pseudocode, the exact agent spawn-prompt template, worked 7-task example, display formats).

---

## Phase 1: Setup

### 1.1 Extract Paths (NEVER lose these)

```
task_list_file = {the file path provided}
input_folder   = directory containing task_list_file
planning_folder = {input_folder}/planning
```

### 1.2 Read and Parse Task List

Read the task list file. Extract:
- Phase/feature name
- All tasks with descriptions
- Dependencies between tasks
- Any wave/phase groupings already defined

### 1.3 Resume Detection

Check THREE sources for prior progress (not just filesystem):

**1. Filesystem check:**
```bash
ls {planning_folder}/task-updates/*.md 2>/dev/null | wc -l
```

**2. PM-DB check:**
```python
# Query for prior phase runs on this feature
import sqlite3
conn = sqlite3.connect(str(Path.home() / '.claude/projects.db'))
rows = conn.execute("""
    SELECT pr.id, pr.status, pr.started_at,
           COUNT(tr.id) as task_runs,
           SUM(CASE WHEN tr.status='completed' THEN 1 ELSE 0 END) as completed
    FROM phase_runs pr
    LEFT JOIN task_runs tr ON tr.phase_run_id = pr.id
    JOIN phases p ON p.id = pr.phase_id
    WHERE p.name LIKE ? AND pr.status IN ('started', 'in_progress')
    GROUP BY pr.id
    ORDER BY pr.started_at DESC LIMIT 1
""", (f'%{feature_name}%',)).fetchall()
```

**3. Git check:**
```bash
git log --oneline --grep="{feature_name}" -5
```

**If prior progress found:**
```
Prior progress detected:
- Planning folder: {X} task-update files
- PM-DB: Phase run #{id}, {completed}/{total} tasks
- Git: {N} related commits

Options:
1. Resume from task {next_incomplete} (recommended)
2. Start fresh (backs up existing planning/)
3. Cancel
```

**If no progress found but user said "resume":**
```
No prior progress found for this feature.
Starting fresh execution. All tasks will run from the beginning.
```

### 1.4 Create Directory Structure

```bash
mkdir -p "{planning_folder}/task-updates"
mkdir -p "{planning_folder}/agent-delegation"
mkdir -p "{planning_folder}/phase-structure"
```

---

## Phase 2: Planning (3 Required Documents)

These documents force comprehensive analysis before any code is written.
This is the skill's primary value — don't skip this phase.

Create all three in `{planning_folder}`:

1. `agent-delegation/task-delegation.md` — per-task agent type, priority, difficulty, dependencies, estimate; plus agent workload summary
2. `agent-delegation/sub-agent-plan.md` — wave decomposition: dependency graph → parallel waves with file-conflict analysis and time-savings calculation (the most important document)
3. `phase-structure/system-changes.md` — all files created/modified/deleted, grouped by impact level, with cross-app impacts

Read `references/planning-docs.md` for the full template and instructions for each document BEFORE writing them.

---

## Phase 3: Execute Tasks by Wave

### Sequential Tasks

For each task in the current wave:

1. **Show progress:**
```
[████████░░░░░░░░░░░░] 8/20 tasks (40%)
Starting Task 9: {name}
Agent: {agent_type} | Priority: {priority}
```

2. **Spawn the agent** using the Task tool:
```
Task tool:
  subagent_type: "{agent_type}"
  prompt: "Execute Task {n}: {task_name}

  Context:
  - Working directory: {monorepo_root}
  - Task requirements: {full task description}
  - Extra instructions: {extra_instructions}
  - Files to modify: {from system-changes.md}

  Complete the task, then stop. Quality gate runs separately."
```

3. **Wait for completion**, then run quality gate (Phase 4)

### Parallel Wave Execution

For parallel waves, spawn ALL agents in a SINGLE message:

```
Starting Wave 3 (3 tasks in parallel):
  Task 7: {name} → {agent_type}
  Task 8: {name} → {agent_type}
  Task 9: {name} → {agent_type}

Launching agents...
```

Use the Task tool 3 times in one response to achieve true parallelism.
Wait for ALL to complete before proceeding to next wave.

### Extra Instructions

If `extra_instructions` provided, include them in every agent prompt:
```
ADDITIONAL REQUIREMENTS: {extra_instructions}
```

---

## Phase 4: Quality Gate (After Each Task)

After each task completes:

1. **Lint check:**
```bash
cd {monorepo_root} && npm run lint 2>&1 | tail -20
```

2. **Build check:**
```bash
cd {monorepo_root} && npm run build 2>&1 | tail -20
```

3. **If both pass:** Create task update file and commit
```bash
# Create task update
echo "# Task {n}: {name}\nStatus: Complete\nAgent: {agent}\nTime: {duration}" \
  > {planning_folder}/task-updates/task-{n}-{slug}.md

# Commit
git add -A && git commit -m "task({feature}): complete task {n} - {name}"
```

4. **If either fails:** Fix errors before proceeding
```
Quality Gate FAILED:
- Lint: {error count} errors
- Build: {error details}

Fix the errors, then re-run the quality gate.
Do NOT proceed to the next task until this passes.
```

---

## Phase 5: Closeout

After all tasks complete:

1. **Generate phase summary** at `{planning_folder}/phase-structure/phase-summary.md`:
   - Total tasks completed
   - Total duration
   - Quality gates: all passed
   - Files changed (from git diff)

2. **Update PM-DB** (if database exists):
   Read `references/tracking.md` for PM-DB integration details.

3. **Display final report:**
```
PHASE COMPLETE: {feature_name}

Tasks: {total}/{total} complete
Quality gates: {total}/{total} passed
Duration: {time}
Commits: {count}

Next steps:
1. /pm-db dashboard — view project status
2. Review phase summary at {planning_folder}/phase-structure/phase-summary.md
```

---

## PM-DB Tracking

PM-DB integration is optional but recommended. If `~/.claude/projects.db` exists,
track phase runs and task completions.

For detailed PM-DB hook commands, read `references/tracking.md`.

The key hooks (all at `~/.claude/hooks/pm-db/`):
- `on-phase-run-start.py` — call at Phase 1 start
- `on-task-run-start.py` — call before each task
- `on-task-run-complete.py` — call after each task
- `on-phase-run-complete.py` — call at Phase 5

---

## Path Management (CRITICAL)

These paths are set in Phase 1 and NEVER change:

```
task_list_file  → original file path
input_folder    → directory of task list
planning_folder → {input_folder}/planning

All artifacts go in planning_folder.
Never derive paths differently in different phases.
```

---

## Notes

- Phase 2 planning is the skill's primary value — don't skip it
- Quality gates are mandatory — don't proceed on failures
- Parallel waves need file conflict analysis — same-file = sequential
- Long tasks (>30 min): create checkpoint commits
- Extra instructions apply to ALL tasks in the phase
