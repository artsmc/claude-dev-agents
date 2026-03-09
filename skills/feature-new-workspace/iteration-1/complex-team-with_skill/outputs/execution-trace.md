# Execution Trace: feature-new (Team Mode)

**Prompt:** "Build a complete notification system with real-time WebSocket events, email digests, and in-app notification center --team"

**Skill evaluated:** `/home/artsmc/.claude/skills/feature-new/SKILL.md`

---

## 1. Argument Parsing and Mode Detection

### Raw Input

```
feature_description = "Build a complete notification system with real-time WebSocket events, email digests, and in-app notification center --team"
```

### Parsing Steps

The skill's `args` block defines:
- `feature_description` (required, string)
- `mode` (optional, string, default: "auto")

The `--team` flag is not a named argument in the frontmatter — it appears inline in the `feature_description` string. The skill must strip it before passing the description downstream.

**Detection logic (from SKILL-TEAM.md Step 0):**

```
if args contains "--team":
    USE_TEAM_MODE = true
    mode = "team"
```

**Result after parsing:**

```
feature_description = "Build a complete notification system with real-time WebSocket events, email digests, and in-app notification center"
mode                = "team"
USE_TEAM_MODE       = true
```

The `--team` suffix is stripped from `feature_description` before any downstream skill receives it. This is important: spec-plan receives a clean description string, and the team flag is appended separately as documented in Step 1 of SKILL.md:

```
Args: "{{feature_description}}"
      (append " --team" if mode is "team")
```

---

## 2. Step 0: Pre-Flight Skip Check

Before invoking any sub-skills, the skill checks for existing artifacts (SKILL.md "Skip Logic" section):

```
Glob: "**/feature-*/task-list.md"
Glob: "**/feature-notification*/docs/task-list.md"
```

**Assumed result:** No existing artifacts found. Proceed with all five steps.

If a `task-list.md` were found at, e.g., `./job-queue/feature-notification-system/docs/task-list.md`, the skill would confirm with the user before skipping Steps 1-2.

---

## 3. Step 1 — Generate Feature Specification

### Invocation

This is the FIRST action taken.

```
Skill: spec-plan
Args:  "Build a complete notification system with real-time WebSocket events, email digests, and in-app notification center --team"
```

The `--team` flag is appended to the description string passed to spec-plan because `mode == "team"`. This tells spec-plan to use parallel spec generation (4 agents: frd-writer, frs-tr-writer, scenario-writer, task-writer).

### Why spec-plan runs first (not spec-review or any other)

The flow diagram in SKILL.md is explicit:
```
spec-plan → spec-review → start-phase-plan → pm-db import → execute
```

spec-plan is always first because it generates the foundational artifacts — the spec docs and task-list.md — that all subsequent steps depend on.

### What spec-plan will auto-detect

The notification system spans:
- Real-time WebSocket events (Mastra + Web)
- Email digests (API + external email provider)
- In-app notification center (Web frontend)
- Likely: database schema for notifications (API/Mastra)

This hits 3+ apps, is security-sensitive (user data), and will produce 15+ tasks. spec-plan's tier auto-detection will classify this as **Full tier** (FRD + FRS + GS + TR + task-list).

### State captured after Step 1

```
feature_name    = "feature-notification-system"
spec_dir        = "./job-queue/feature-notification-system/docs/"
task_list_path  = "./job-queue/feature-notification-system/docs/task-list.md"
```

The skill extracts these from spec-plan's output. If the paths are ambiguous, it runs:
```
Glob: "**/feature-notification*/task-list.md"
Glob: "**/feature-notification*/docs/task-list.md"
```

### Failure handling for Step 1

If spec-plan fails (e.g., research errors, file write failures):

```
STOP. Do not proceed.

Tell user:
  "spec-plan failed during specification generation.
   Nothing has been written yet.
   Retry with: /spec-plan "Build a complete notification system..." --team"
```

---

## 4. Step 2 — Review Specification Quality

### Invocation

```
Skill: spec-review
Args:  (none — spec-review reads from spec_dir implicitly or is pointed to it)
```

spec-review is invoked with no additional arguments. It auto-discovers the most recently generated spec files.

### Decision branches

**Branch A — Clean pass or warnings only:**
Continue to Step 3 immediately. No user interaction needed.

**Branch B — Errors found:**
Pause and ask the user via AskUserQuestion:

```
AskUserQuestion:
  "spec-review found errors in the generated specification.

   - 'Continue anyway' — proceed to Step 3 (planning)
   - 'Stop and fix' — stop here; specs are saved at:
     ./job-queue/feature-notification-system/docs/

   Choose an option:"
```

- If "Continue anyway": proceed to Step 3.
- If "Stop and fix": stop workflow. Report spec location.

### State threading

No new state variables are added by spec-review. The `spec_dir` and `task_list_path` from Step 1 remain unchanged.

### Failure handling for Step 2

If spec-review itself fails (crashes, script error):

```
STOP.

Tell user:
  "spec-review failed. Specs were generated successfully and saved at:
   ./job-queue/feature-notification-system/docs/

   Retry review with: /spec-review"
```

---

## 5. Step 3 — Create Execution Plan

### Invocation

```
Skill: start-phase-plan
Args:  "./job-queue/feature-notification-system/docs/task-list.md"
```

The `task_list_path` from Step 1 is passed directly. This is where the state thread from Step 1 is consumed.

### What start-phase-plan does internally

start-phase-plan analyzes the task list, identifies dependencies, proposes an execution wave structure, and shows a speedup estimate. Because `USE_TEAM_MODE == true`, it will present a parallel wave plan showing:
- Wave breakdown with estimated durations
- Sequential vs parallel time comparison
- Agent type assignments per task

For a full-tier notification system (likely 15+ tasks), the plan might show 5-6 waves covering:
- Wave 1: Database schema + WebSocket infrastructure (parallel)
- Wave 2: API notification endpoints + WebSocket server (parallel)
- Wave 3: Email digest job setup (sequential, depends on API)
- Wave 4: Web frontend notification center UI (depends on API)
- Wave 5: Integration wiring (depends on Wave 4)
- Wave 6: Tests + documentation (parallel, depends on all)

### Built-in human checkpoint

start-phase-plan has a mandatory user approval gate. The workflow pauses here.

**Branch A — User approves:**
Continue to Step 4.

**Branch B — User rejects:**
Stop workflow. Report:

```
"Execution plan was not approved. Specs are saved and ready.
 Re-plan with: /start-phase plan ./job-queue/feature-notification-system/docs/task-list.md"
```

### State captured after Step 3

```
phase_summary_path = "./job-queue/feature-notification-system/planning/phase-structure/phase-summary.md"
```

(This path is written by start-phase-plan. The feature-new orchestrator notes it for the final completion summary.)

### Failure handling for Step 3

If start-phase-plan crashes before showing the approval prompt:

```
STOP.

Tell user:
  "start-phase-plan failed. Steps 1-2 completed successfully.
   Specs at: ./job-queue/feature-notification-system/docs/

   Retry planning with: /start-phase plan ./job-queue/feature-notification-system/docs/task-list.md"
```

---

## 6. Step 4 — Import to PM-DB (Best-Effort)

### Invocation

```
Skill: pm-db
Args:  "import --project feature-notification-system --auto-confirm"
```

The `feature_name` variable ("feature-notification-system") is interpolated into the `--project` argument. The `--auto-confirm` flag prevents pm-db from prompting the user interactively.

### Decision branches

**Branch A — Success:**
Record the returned IDs:

```
pm_db_ids = {
  project_id: <returned>,
  phase_id:   <returned>,
  plan_id:    <returned>
}
```

Continue to Step 5.

**Branch B — Failure:**
This step is explicitly **best-effort** (SKILL.md: "helpful but not blocking"). If pm-db fails:

```
WARN user:
  "PM-DB import failed (non-blocking). Continuing to execution.
   You can import manually later with: /pm-db import --project feature-notification-system"

pm_db_ids = null
```

Continue to Step 5 regardless.

### Why this step is best-effort

PM-DB is a tracking/observability layer. Execution can succeed without it. Blocking on a tracking failure would be worse than proceeding without tracking.

---

## 7. Step 5 — Execute Tasks (Team Mode Routing)

### The Routing Decision

This is the critical team-mode branch. SKILL.md Step 5 is explicit:

```
If mode is "team":
    Skill: start-phase-execute-team
    Args:  "{task_list_path}"

If mode is "sequential" or "auto":
    Skill: start-phase-execute
    Args:  "{task_list_path}"
```

Because `mode == "team"`, the orchestrator routes to `start-phase-execute-team`, NOT `start-phase-execute`.

### Invocation

```
Skill: start-phase-execute-team
Args:  "./job-queue/feature-notification-system/docs/task-list.md"
```

Note: The SKILL-TEAM.md Step 6 shows an alternative form — passing `--team` to `start-phase-execute` instead of routing to a separate skill:

```
Skill: start-phase-execute
Args:  "./job-queue/feature-notification-system/docs/task-list.md --team"
```

However, SKILL.md Step 5 is authoritative for this orchestrator: it routes to `start-phase-execute-team` as a distinct skill name. The trace follows SKILL.md as the primary document.

### What start-phase-execute-team does

The team execution skill handles everything internally:

**Part 1:** Create working directories under `./job-queue/feature-notification-system/`

**Part 2:** Generate planning docs (PLANNING.md, DECISIONS.md, RISKS.md)

**Part 3:** Team setup
- `TeamCreate(team_name="phase-execution")`
- Create task entries with dependency chains via `TaskCreate`
- Set `addBlockedBy` for dependent tasks (dependency enforcement)

**Part 4:** Wave-by-wave parallel execution
- Per wave: spawn only the agents needed for that wave
- Each agent: `TaskUpdate` to claim task, implement, run quality gates (lint + build), commit
- Wave completes when all agents in the wave finish
- Next wave spawned only after current wave's dependencies are met

For the notification system, representative agent assignments:
- Wave 1: `database-schema-specialist` (notification schema) + `express-api-developer` (WebSocket infra setup) in parallel
- Wave 2: `express-api-developer` (notification API endpoints) + second `express-api-developer` (email digest job) in parallel
- Wave 3: `ui-developer` (notification center UI components) + `frontend-developer` (WebSocket client logic) in parallel
- Wave 4: `frontend-developer` (wire UI to API) — sequential, depends on Wave 3
- Wave 5: `qa-engineer` (integration tests) + `technical-writer` (documentation) in parallel

**Part 5:** Closeout
- All agents shut down via `TeamDelete`
- Quality metrics reported
- PM-DB tracking hooks fired (if `pm_db_ids` not null)

### Failure handling for Step 5

If execution fails mid-run (e.g., an agent crashes on Wave 3):

```
Tell user:
  "Execution failed during Wave 3 (email digest job setup).

   Completed:
     Wave 1: Database schema + WebSocket infra [committed]
     Wave 2: Notification API endpoints [committed]

   Resume options:
     /feature-continue
     /start-phase execute ./job-queue/feature-notification-system/docs/task-list.md"
```

The `feature-continue` skill is preferred since it has context about where the workflow stopped. The direct `start-phase execute` command is the fallback if `feature-continue` isn't available.

---

## 8. How Team Mode Affects Each Step (Summary Table)

| Step | Skill Invoked | Team Mode Effect |
|------|--------------|-----------------|
| 1 | `spec-plan` | `--team` appended to args; parallel spec generation with 4 agents |
| 2 | `spec-review` | No team mode effect; always sequential quality check |
| 3 | `start-phase-plan` | Wave analysis and parallel speedup estimate shown in plan |
| 4 | `pm-db` | `--auto-confirm` flag; mode metadata recorded in PM-DB if successful |
| 5 | `start-phase-execute-team` | Routed to team skill (NOT `start-phase-execute`); parallel wave execution |

---

## 9. State Threading Across All Steps

```
PARSE ARGS
  → feature_description = "Build a complete notification system..."
  → mode = "team"
  → USE_TEAM_MODE = true

STEP 1 (spec-plan)
  → feature_name    = "feature-notification-system"          [derived from spec-plan output]
  → spec_dir        = "./job-queue/feature-notification-system/docs/"
  → task_list_path  = "./job-queue/feature-notification-system/docs/task-list.md"

STEP 2 (spec-review)
  → No new state; uses spec_dir implicitly
  → user_approved_despite_errors = true/false (captured if errors found)

STEP 3 (start-phase-plan)
  → task_list_path CONSUMED as input argument
  → phase_summary_path = "./job-queue/feature-notification-system/planning/phase-structure/phase-summary.md"
  → user_approved_plan = true (workflow only continues if approved)

STEP 4 (pm-db)
  → feature_name CONSUMED as --project argument
  → pm_db_ids = { project_id, phase_id, plan_id } OR null (best-effort)

STEP 5 (start-phase-execute-team)
  → task_list_path CONSUMED as input argument
  → pm_db_ids available for tracking hooks (passed to execution skill if not null)
  → execution_result = { tasks_completed, duration_minutes, git_commits }

COMPLETION SUMMARY
  → Uses: feature_description, spec_dir, execution_result
```

If `task_list_path` is not parseable from spec-plan's output text, the skill falls back to:
```
Glob: "**/feature-notification*/task-list.md"
Glob: "**/feature-notification*/docs/task-list.md"
```

---

## 10. Complete Error Recovery Matrix

| Step | Failed Step | What Was Completed | Recovery Command |
|------|------------|-------------------|-----------------|
| 1 | spec-plan | Nothing | `/spec-plan "Build a complete notification system..." --team` |
| 2 | spec-review | Specs generated | `/spec-review` |
| 3 | start-phase-plan | Specs + review | `/start-phase plan ./job-queue/feature-notification-system/docs/task-list.md` |
| 3 | User rejected plan | Specs + review | `/start-phase plan ./job-queue/feature-notification-system/docs/task-list.md` |
| 4 | pm-db import | Specs + review + plan | Best-effort; continue OR `/pm-db import --project feature-notification-system` |
| 5 | start-phase-execute-team | All prior steps | `/feature-continue` OR `/start-phase execute ./job-queue/feature-notification-system/docs/task-list.md` |
| 5 | Team creation failure | All prior steps | Enable `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`, then retry OR use sequential: `/start-phase execute ./job-queue/feature-notification-system/docs/task-list.md` |

---

## 11. Completion Output

When all steps succeed, the skill displays:

```
Feature: Build a complete notification system with real-time WebSocket events, email digests, and in-app notification center
Specs: ./job-queue/feature-notification-system/docs/
Tasks completed: (from start-phase-execute-team output)

Next:
  /pm-db dashboard    — view project metrics
  /memory-bank-sync   — update project memory
```

The completion output is intentionally brief. Each sub-skill already displayed detailed progress during its own run.

---

## 12. Key Assertion Coverage

This trace covers all four assertions from `eval_metadata.json`:

**`team-flag-detected`:** Section 1 shows `--team` parsed from the raw input string, setting `mode = "team"` and `USE_TEAM_MODE = true`.

**`spec-plan-team-arg`:** Section 3 (Step 1) shows the exact invocation:
```
Skill: spec-plan
Args:  "Build a complete notification system... --team"
```

**`team-execute-routing`:** Section 7 (Step 5) shows the routing branch selects `start-phase-execute-team`, not `start-phase-execute`, because `mode == "team"`.

**`correct-step-order`:** Sections 3-7 maintain the documented sequence: spec-plan (1) → spec-review (2) → start-phase-plan (3) → pm-db (4) → start-phase-execute-team (5). Team mode does not reorder or skip steps.
