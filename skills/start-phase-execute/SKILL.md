---
name: start-phase-execute
description: "Structured task execution with quality gates, parallel waves, and pm-db tracking. Use this skill when the user wants to execute a task list, run implementation tasks, start building a feature from a plan, or says things like 'execute these tasks', 'start building', 'run the implementation', 'execute the plan', or 'start phase execute'. Also triggers on '/start-phase execute' commands."
args:
  task_list_file:
    type: string
    description: Path to task list markdown file
    required: true
  extra_instructions:
    type: string
    description: Optional extra context for execution
    required: false
---

# Start-Phase Execute

Execute a task list with parallel waves, agent delegation, and quality gates.

## Usage

```bash
/start-phase execute /path/to/task-list.md
/start-phase execute /path/to/task-list.md "Focus on type safety"
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

### 2.1 Task Delegation Plan

Create `{planning_folder}/agent-delegation/task-delegation.md`:

For each task, determine:
- **Agent type** — match to available agents at `~/.claude/agents/`
- **Priority** — HIGH/MEDIUM/LOW based on dependency position
- **Difficulty** — EASY/MEDIUM/HARD based on scope
- **Dependencies** — which tasks must complete first
- **Estimated time**

Include an agent workload summary to ensure balanced distribution.

### 2.2 Wave Decomposition (Parallel Execution Plan)

Create `{planning_folder}/agent-delegation/sub-agent-plan.md`:

This is the most important planning document. The goal is to maximize
parallelism while preventing file conflicts.

**How to decompose tasks into waves:**

1. **Build the dependency graph** — which tasks depend on which
2. **Identify independent roots** — tasks with no dependencies are Wave 1
3. **Check for file conflicts** — tasks modifying the same file CANNOT be parallel
4. **Group by readiness** — once all dependencies resolve, task enters next wave
5. **Validate each wave** — no two tasks in a wave touch the same file

**Common patterns:**
- Schema/model changes → Wave 1 (everything depends on these)
- Service/business logic → Wave 2 (depends on models)
- Controllers/routes → Wave 3 (depends on services)
- Frontend components → Can often parallel with backend waves
- Tests → Final wave (depends on everything)

**For each wave, document:**
- Which tasks run in parallel
- Which agent handles each task
- File conflict analysis proving parallel safety
- Estimated wave duration (max of parallel tasks, not sum)

**Calculate time savings:**
```
Sequential: sum of all task estimates
Parallel:   sum of wave max-durations
Savings:    (sequential - parallel) / sequential × 100%
```

### 2.3 System Changes Analysis

Create `{planning_folder}/phase-structure/system-changes.md`:

- List all files that will be created, modified, or deleted
- Group by impact level (HIGH = core logic, MEDIUM = integration, LOW = types/tests)
- Note cross-app impacts (API + Web + Mastra + Microsandbox)

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
