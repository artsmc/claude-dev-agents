---
name: start-phase-plan
description: >-
  Mode 1 - Strategic planning with human approval before execution. Use this skill
  whenever a user wants to plan, review, or strategize a task list before executing it.
  Triggers on: "plan this", "review these tasks", "let's plan before building",
  "/start-phase plan", or any request to analyze a task list for parallelism,
  complexity, or agent delegation. Always use this before /start-phase-execute for
  non-trivial work.
args:
  task_list_file:
    type: string
    description: Path to task list markdown file (e.g., ./planning/tasks.md)
    required: true
---

# Start-Phase: Plan

Strategic analysis and refinement of a task list before execution. Read-only — no files created, no code written, no commits made.

## What This Does

1. Reads the task list and project context
2. Analyzes complexity, parallelism, and agent delegation opportunities
3. Proposes a refined plan with waves and agent assignments
4. Gets human approval before anything executes

## Workflow

### Step 1: Setup

Derive paths from the task list location. These are permanent for this session:

```
task_list_file → the file passed as argument
input_folder   → directory containing the task list
planning_folder → {input_folder}/planning
```

Announce:
```
Mode 1: Strategic Planning
Task list: {task_list_file}
Input folder: {input_folder}

Beginning strategic review...
```

### Step 2: Read Context

Read the task list file. Extract all tasks, their descriptions, and any existing dependencies.

If a Memory Bank exists at `~/.claude/memory-bank/`, read `systemPatterns.md` and `activeContext.md` for architectural context. Don't spend tokens reading all 6 files — those two give you what you need.

If a Documentation Hub exists at the input folder's `docs/` directory, scan it for relevant specs (FRD, FRS, TR) that inform the plan.

Display the current task list:
```
Current Tasks ({count}):
1. Task description
2. Task description
...
```

### Step 3: Analyze

Three analyses, presented concisely:

**Complexity Check**
- Is the scope realistic for a single phase? (Rule of thumb: 5-8 tasks is healthy, 10+ suggests splitting into multiple phases)
- Are there mixed concerns? (e.g., building AND deploying in one phase)
- Recommend scope reduction if needed — defer non-essential tasks to a future phase

**Parallelism**
- Which tasks have no dependencies on each other? These form parallel waves
- Map dependencies explicitly (Task N depends on Task M)
- Group into waves: Wave 1 (parallel), Wave 2 (depends on Wave 1), etc.

**Agent Delegation**
Use the framework's 19 standardized agents. Each has a model assignment and tool restrictions:

| Category | Agents (model) |
|----------|----------------|
| Backend | express-api-developer (sonnet), nextjs-backend-developer (sonnet), database-schema-specialist (sonnet) |
| Frontend | frontend-developer (sonnet), ui-developer (sonnet), accessibility-specialist (sonnet) |
| Architecture | strategic-planner (opus), api-designer (sonnet), mastra-core-developer (opus) |
| Quality | nextjs-code-reviewer (sonnet), nextjs-qa-developer (sonnet), security-auditor (opus) |
| Documentation | spec-writer (sonnet), technical-writer (sonnet) |
| Infrastructure | devops-infrastructure (sonnet), debugger-specialist (opus) |
| Coordination | team-lead (opus) |

Assign agents to tasks based on the work type. Note: Opus agents cost more — only assign them when the task genuinely needs deep reasoning.

**When to recommend teams vs single agents:**
- **3 or fewer tasks → ALWAYS single agent, never a team.** Even if tasks touch different concerns, the coordination overhead of a team exceeds the parallelism benefit at this scale. Pick the most relevant agent and let it handle all tasks sequentially.
- **4-5 tasks, single concern → single agent.** One agent can handle 4-5 related tasks efficiently.
- **4+ tasks, multiple distinct concerns (backend + frontend + tests) → team with parallel waves.** Only recommend teams when there's genuine parallelism between independent workstreams.

**Practical concerns to surface:**
Before presenting the plan, check for issues the user should resolve first:
- Existing code that overlaps with the task list (duplicate work risk)
- Ambiguous requirements that need clarification before execution
- Missing dependencies or prerequisites
- Framework/pattern choices that affect implementation (e.g., test runner, ORM, auth strategy)

### Step 4: Propose Refined Plan

Present the revised plan:

```
Proposed Plan
─────────────

Wave 1 (parallel):
  1. [task] → agent-name (model)
  2. [task] → agent-name (model)

Wave 2 (depends on Wave 1):
  3. [task] → agent-name (model)
  4. [task] → agent-name (model)

Wave 3 (sequential):
  5. [task] → agent-name (model)

Summary:
  Tasks: {count}
  Waves: {count} ({parallel_count} parallel, {sequential_count} sequential)
  Agents: {list of unique agents}
  Deferred: {any tasks moved to future phase}
```

### Step 5: Approval

Ask the user:
```
Options:
1. Approve → proceed to /start-phase-execute
2. Revise → suggest changes
3. Reject → start over
4. Question → ask about the plan
```

Handle each response:
- **Approve**: Confirm, then tell user to run `/start-phase-execute {task_list_file}`
- **Revise**: Apply changes, re-present, ask again
- **Reject**: Ask what they'd prefer instead
- **Question**: Answer, then return to options

### Step 6: Handoff

On approval, confirm the handoff:
```
Plan approved.

Next: /start-phase-execute {task_list_file}

Planning context:
  input_folder: {path}
  planning_folder: {path}/planning
  phase_name: {extracted or inferred}
```

## Rules

**Do in Mode 1:**
- Read files (task list, Memory Bank, Documentation Hub)
- Analyze, strategize, propose
- Get human approval

**Never do in Mode 1:**
- Create directories or files
- Write code
- Make git commits
- Execute tasks

## Working Memory Integration

If this plan will be executed by a team (4+ tasks, multiple agents), note in the approval output:
```
Team execution recommended.
Working memory will be created at: ~/.claude/working-memory/{team-name}.md
```

This prepares the user for the working memory file that `/start-phase-execute-team` will create.
