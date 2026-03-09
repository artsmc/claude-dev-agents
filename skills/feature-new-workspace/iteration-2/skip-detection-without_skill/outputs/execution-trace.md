# Execution Trace: File Upload Feature (Specs Already Exist)

**Scenario:** User provides pre-existing specs at a known path and says they have already reviewed them. Task is to skip planning phases and go straight to execution.

**Generated:** 2026-03-09

---

## 1. How I Handle the Fact That Specs Already Exist

The user's message contains two explicit signals:

1. "Specs are already at `/home/artsmc/applications/low-code/job-queue/feature-file-upload/docs/`" — the spec-plan phase is complete.
2. "I've already reviewed them" — the spec-review phase is also complete.

These two signals gate the first two steps of the normal `feature-new` workflow. Because both conditions are satisfied by the user's statement, I skip both:

- **Do NOT invoke `/spec-plan`** — specs already exist.
- **Do NOT invoke `/spec-review`** — user has explicitly confirmed review is done.

Before skipping to execution I perform one verification step: I confirm the task-list file actually exists at the stated location. This guards against path typos and ensures the execution phase has a valid input.

```bash
ls /home/artsmc/applications/low-code/job-queue/feature-file-upload/docs/task-list.md
```

If the file exists, I proceed. If it is missing, I surface that finding immediately rather than proceeding blindly (see Section 5 — failure handling).

I also do a quick scan to understand what spec tier was produced (Quick/Standard/Full) by checking which doc types are present:

```bash
ls /home/artsmc/applications/low-code/job-queue/feature-file-upload/docs/
```

Expected files based on the prompt context (FRD, FRS, GS, TR, task-list.md = Full tier):

| File | Role |
|------|------|
| FRD.md | Functional Requirements Document |
| FRS.md | Functional Requirements Specification |
| GS.md | Golden Spec / acceptance criteria |
| TR.md | Technical Requirements |
| task-list.md | The execution input — authoritative list of tasks |

The TR.md is particularly important: it describes affected apps, technology choices, and integration points that directly inform agent selection and wave decomposition in the execution phase.

---

## 2. First Action

After confirming specs exist, my first action is to invoke `start-phase-plan` against the task-list.

**Why start-phase-plan before start-phase-execute?**

`start-phase-plan` is a read-only analysis phase. It reads the task list, detects parallelism, builds wave decomposition, and assigns agents — then presents the plan for human approval before a single line of code is written. This step is not skippable for non-trivial features. The file-upload feature spans multiple apps (API, Web, Mastra, Microsandbox are all plausible touch points), so the planning analysis has real value in preventing wasted execution.

**Concrete first action:**

```
/start-phase-plan /home/artsmc/applications/low-code/job-queue/feature-file-upload/docs/task-list.md
```

`start-phase-plan` will:

1. Read the task list and extract all tasks with their descriptions.
2. Read `~/.claude/memory-bank/systemPatterns.md` and `activeContext.md` for architectural context.
3. Scan the docs directory for TR.md (to understand cross-app impact) and FRD.md (to understand acceptance criteria).
4. Analyze complexity, parallelism opportunities, and agent assignments.
5. Present the proposed wave plan to the user for approval.

The user approves (or revises) the plan, and only then does execution begin. This approval checkpoint is the correct handoff point given that the specs are already reviewed — I am not adding a redundant review, I am doing the structural analysis needed to execute safely.

---

## 3. How I Organize the Execution

Execution follows the `start-phase-execute` workflow once the plan is approved.

### Step 3.1 — Setup (start-phase-execute Phase 1)

Paths are derived from the task list location and fixed for the entire session:

```
task_list_file  = /home/artsmc/applications/low-code/job-queue/feature-file-upload/docs/task-list.md
input_folder    = /home/artsmc/applications/low-code/job-queue/feature-file-upload/docs
planning_folder = /home/artsmc/applications/low-code/job-queue/feature-file-upload/docs/planning
```

Directory structure created:

```
planning/
  task-updates/         # One .md file per completed task
  agent-delegation/     # task-delegation.md, sub-agent-plan.md
  phase-structure/      # system-changes.md, phase-summary.md
```

Resume detection runs against three sources:

- Filesystem: `ls planning/task-updates/*.md` — will be empty on first run.
- PM-DB: Query `phase_runs` for any prior `in_progress` run matching `feature-file-upload`.
- Git: `git log --oneline --grep="feature-file-upload" -5`.

All three will be clean on a first execution. Fresh start is confirmed.

### Step 3.2 — Pre-Execution Planning Documents (start-phase-execute Phase 2)

Three mandatory documents are created before any code is written:

**A. Task Delegation Plan** at `planning/agent-delegation/task-delegation.md`

For each task in task-list.md, assigns:
- Agent type (matched to agents in `~/.claude/agents/`)
- Priority (HIGH/MEDIUM/LOW)
- Difficulty (EASY/MEDIUM/HARD)
- Dependencies
- Estimated duration

File upload is likely a multi-app feature. Typical task-to-agent mapping for a feature of this scope:

| Task Category | Likely Agent |
|--------------|--------------|
| Storage library / S3 integration | `express-api-developer` |
| Database schema for file metadata | `database-schema-specialist` |
| Upload API endpoints | `express-api-developer` |
| File validation / security controls | `security-auditor` |
| Frontend upload UI component | `ui-developer` |
| Frontend state / upload progress | `frontend-developer` |
| Microsandbox file access policy | `debugger-specialist` |
| Integration tests | `nextjs-qa-developer` or `qa-engineer` |

**B. Wave Decomposition Plan** at `planning/agent-delegation/sub-agent-plan.md`

The dependency graph drives wave grouping. For file upload, a typical decomposition:

```
Wave 1 (parallel — foundation, no inter-dependencies):
  - Database schema for file metadata (database-schema-specialist)
  - Storage library setup in libs/storage (express-api-developer)

Wave 2 (depends on Wave 1 — services layer):
  - Upload service using storage library (express-api-developer)
  - File validation and security controls (security-auditor)

Wave 3 (depends on Wave 2 — API surface + frontend can parallel here):
  - Upload REST endpoints in apps/api (express-api-developer)
  - Frontend upload UI component in apps/web (ui-developer) [parallel with API]
  - Frontend upload state management (frontend-developer) [parallel with API]

Wave 4 (depends on Wave 3 — integration and test):
  - Microsandbox file access policy updates (debugger-specialist)
  - End-to-end upload tests (nextjs-qa-developer)
```

File conflict analysis is performed within each wave to ensure no two parallel tasks modify the same file. Same-file edits are serialized into sequential sub-waves.

**C. System Changes Analysis** at `planning/phase-structure/system-changes.md`

All files to be created/modified/deleted, grouped by impact level and by app:

- HIGH: `apps/api/src/routes/upload.ts`, `libs/storage/src/index.ts`, Prisma schema
- MEDIUM: `apps/web/src/components/FileUpload.tsx`, `apps/api/src/services/upload.service.ts`
- LOW: type definitions, test files, environment variable documentation

Cross-app impact matrix is noted to ensure the team is aware of coordination boundaries.

### Step 3.3 — Task Execution by Wave (start-phase-execute Phase 3)

Each wave is launched after the previous wave's quality gate passes.

For parallel waves: all agents in the wave are spawned in a single message using multiple concurrent `Task` tool calls. This achieves true parallelism — agents run simultaneously.

For sequential tasks: single `Task` tool call, wait for completion, run quality gate, then proceed.

Progress is displayed after each task:

```
[████████░░░░░░░░░░░░] 4/10 tasks (40%)
Completed: Task 4 — Upload Service
Next: Wave 3 (3 parallel tasks)
```

### Step 3.4 — Quality Gate After Each Task (start-phase-execute Phase 4)

After every task completes:

1. Lint: `cd /home/artsmc/applications/low-code && npm run lint 2>&1 | tail -20`
2. Build: `cd /home/artsmc/applications/low-code && npm run build 2>&1 | tail -20`

If both pass:
- Task update file is written to `planning/task-updates/task-N-slug.md`
- Git commit: `git add -A && git commit -m "task(file-upload): complete task N — name"`

If either fails: fix errors before proceeding to the next task. The next wave does not start until the current wave's quality gate is fully clean.

### Step 3.5 — Closeout (start-phase-execute Phase 5)

After all tasks complete:

1. Phase summary written to `planning/phase-structure/phase-summary.md`.
2. PM-DB updated: `on-phase-run-complete.py` hook called to mark the phase_run as `completed`.
3. Final report displayed:

```
PHASE COMPLETE: feature-file-upload

Tasks:  10/10 complete
Quality gates: 10/10 passed
Duration: ~N minutes
Commits: 10

Next steps:
1. /pm-db dashboard — view project status
2. Review: planning/phase-structure/phase-summary.md
```

---

## 4. Tools and Skills Used

| Step | Tool / Skill | Purpose |
|------|-------------|---------|
| Spec verification | `Bash` (ls) | Confirm task-list.md exists at user-provided path |
| Spec scan | `Read` + `Glob` | Read TR.md and FRD.md for architectural context |
| Planning | `/start-phase-plan` skill | Wave decomposition, agent assignment, human approval |
| PM-DB init check | `Bash` (python3 init_db.py) | Ensure ~/.claude/projects.db exists |
| PM-DB import | `pm-db import_specs.py` | Import file-upload specs into tracking database |
| Execution | `/start-phase-execute` skill | Delegates tasks to specialized agents via Task tool |
| Agent delegation | `Task` tool | Spawns specialized sub-agents per wave |
| Quality gate | `Bash` (npm run lint, npm run build) | Validates each task before committing |
| Git tracking | `Bash` (git commit) | One commit per passing task |
| PM-DB tracking | `Bash` (pm-db hooks) | Records phase_run, task_run completions |
| Closeout | `pm-db generate_report.py` | Dashboard after completion |

**Specialized agents likely invoked during execution:**

- `database-schema-specialist` — Prisma schema migration for file metadata
- `express-api-developer` — Upload endpoints, storage service
- `security-auditor` — File validation, upload security controls, sandbox policy
- `ui-developer` — Upload component (drag-and-drop, progress bar)
- `frontend-developer` — Upload state management, TanStack Query integration
- `debugger-specialist` — Microsandbox file access policies
- `nextjs-qa-developer` — Integration tests for upload flow

**No skills invoked:**

- `/spec-plan` — NOT invoked (specs already exist)
- `/spec-review` — NOT invoked (user confirmed review is done)

---

## 5. What I Do If Something Fails

### Failure: task-list.md not found at stated path

```
Error: task-list.md not found at:
  /home/artsmc/applications/low-code/job-queue/feature-file-upload/docs/task-list.md

Searched:
  - Exact path: not found
  - Parent dir listing: {show ls output}

Options:
1. Correct the path (check spelling of feature-file-upload)
2. The docs may be at a different subdirectory — list the job-queue dir:
   ls /home/artsmc/applications/low-code/job-queue/
3. Re-run /spec-plan to regenerate specs
```

I do NOT proceed without a valid task-list.md. Execution cannot begin without a confirmed task list.

### Failure: start-phase-plan analysis reveals blockers

If the planning analysis surfaces blockers (ambiguous requirements, missing prerequisites, conflicting existing code), I present them to the user before proceeding:

```
Planning Analysis Found Issues:

1. Ambiguity: Task 3 references "storage provider" but TR.md lists both S3 and
   local storage as options. Which should be implemented first?
2. Prerequisite gap: libs/storage does not exist yet. Wave 1 must create it
   before any upload service work can begin.
3. Existing overlap: apps/api/src/routes/files.ts already exists with partial
   upload logic. Proceeding will modify this file — confirm intent.

Resolve these before proceeding? (yes/no)
```

Execution waits for user confirmation.

### Failure: Quality gate fails after a task

The failed task is NOT committed. The next wave does NOT start.

```
Quality Gate FAILED — Task 5: Upload Endpoint

Lint errors: 3
  apps/api/src/routes/upload.ts:47:5 - error TS2345: Argument of type...
  apps/api/src/routes/upload.ts:62:12 - error TS7006: Parameter 'req' implicitly...
  apps/api/src/services/upload.service.ts:23:9 - error TS2304: Cannot find name...

Build: FAILED (blocked by lint errors above)

Fixing errors now...
```

I attempt to fix the errors directly. If I can identify the root cause from the lint output, I fix it and re-run the quality gate. If the fix is non-trivial or touches another agent's scope, I spawn a `debugger-specialist` agent with the error context.

After three failed quality gate attempts on the same task, I surface the issue to the user with a summary of what was tried and ask for guidance.

### Failure: PM-DB database does not exist

```
Warning: ~/.claude/projects.db not found.

PM-DB tracking is optional. Options:
1. Initialize now: python3 ~/.claude/skills/pm-db/scripts/init_db.py
   Then import specs: python3 ~/.claude/skills/pm-db/scripts/import_specs.py
     --auto-confirm --job-queue-dir /home/artsmc/applications/low-code/job-queue
2. Proceed without PM-DB tracking (execution will continue, no run metrics)
```

Execution is not blocked by missing PM-DB. Tracking is skipped gracefully if the database does not exist.

### Failure: An agent task fails or produces unexpected output

If a sub-agent task returns with errors or produces incomplete output:

1. Read the task-update file (or agent output) to understand what went wrong.
2. Attempt to fix within the same agent context if the issue is small.
3. If the failure is architectural (wrong approach, missing context), re-read the relevant spec (TR.md or FRD.md) and re-spawn the agent with corrected context.
4. If two consecutive attempts on the same task fail, pause and surface to the user with a summary of both attempts and the current state of the codebase.

### Failure: Build breaks across apps (cross-app regression)

If a build failure shows errors in an app not targeted by the current task, I run `nx affected:graph` to understand the dependency chain:

```bash
cd /home/artsmc/applications/low-code && nx affected:graph
```

If the regression is confirmed as a side effect of the current task, I fix it before proceeding. If the regression was pre-existing (not caused by the current task), I document it in the task-update file and flag it to the user, but do not let it block the current task's commit unless the CI pipeline explicitly fails on it.

---

## Summary of Skip Logic

```
User says "specs already at X" → skip /spec-plan
User says "already reviewed"   → skip /spec-review
Verify task-list.md exists     → ALWAYS (safety check)
Run /start-phase-plan          → ALWAYS (wave decomposition, agent assignment)
Get user approval              → ALWAYS (no code without approval)
Run /start-phase-execute       → ALWAYS (the actual build)
```

The two phases skipped (spec-plan and spec-review) are the upstream research and documentation phases. The two phases that always run (start-phase-plan and start-phase-execute) are the structural planning and implementation phases. The user's statement gates the first two; the nature of non-trivial execution gates the second two as mandatory.
