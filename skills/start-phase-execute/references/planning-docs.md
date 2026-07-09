# Phase 2 Planning Documents — Full Templates

Full instructions for the 3 required planning documents created in Phase 2.
Read this before writing any of them.

## 2.1 Task Delegation Plan

Create `{planning_folder}/agent-delegation/task-delegation.md`:

For each task, determine:
- **Agent type** — match to available agents at `~/.claude/agents/`
- **Priority** — HIGH/MEDIUM/LOW based on dependency position
- **Difficulty** — EASY/MEDIUM/HARD based on scope
- **Dependencies** — which tasks must complete first
- **Estimated time**

Include an agent workload summary to ensure balanced distribution.

## 2.2 Wave Decomposition (Parallel Execution Plan)

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

## 2.3 System Changes Analysis

Create `{planning_folder}/phase-structure/system-changes.md`:

- List all files that will be created, modified, or deleted
- Group by impact level (HIGH = core logic, MEDIUM = integration, LOW = types/tests)
- Note cross-app impacts (API + Web + Mastra + Microsandbox)
