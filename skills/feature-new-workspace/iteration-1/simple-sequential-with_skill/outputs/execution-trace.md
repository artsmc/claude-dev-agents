# Execution Trace: feature-new skill

**User request:** "I want to add a dark mode toggle to the AIForge web app"
**Skill invoked:** `feature-new`
**Trace date:** 2026-03-09

---

## Skill Invocation

```
Skill: feature-new
Args:
  feature_description: "add a dark mode toggle to the AIForge web app"
  mode: "auto"  (default, not specified by user)
```

**Mode determination:** The user said "I want to add..." which is a single-concern feature touching one app (Web). Mode defaults to `"auto"`, which lets each sub-skill decide its own parallelism. No `--team` flag is appended.

---

## Pre-Flight: Skip Detection

Before starting Step 1, run Glob to check whether specs already exist:

```
Glob: "**/feature-dark-mode*/task-list.md"
Glob: "**/job-queue/*dark-mode*/docs/task-list.md"
```

**Result:** No matches found. No existing artifacts. All five steps will run.

---

## Step 1: Generate Feature Specification

**Action:**
```
Skill: spec-plan
Args: "add a dark mode toggle to the AIForge web app"
```

No `--team` suffix because mode is `"auto"` (not `"team"`).

**What spec-plan does internally:**
- Runs its triage gate: single concern, one app (Web), estimated <5 tasks, known UI pattern
- Classifies tier as **Quick** (task-list only, no FRD/FRS)
- Confirms scope with the user before generating
- Generates a task-list.md and saves it under the job-queue directory

**Expected output from spec-plan:**
```
Tier: Quick
Feature directory: feature-dark-mode
Saved: /home/artsmc/applications/low-code/job-queue/feature-dark-mode/task-list.md
```

**State extracted after Step 1:**

| Variable | Value |
|---|---|
| `feature_name` | `feature-dark-mode` |
| `spec_dir` | `/home/artsmc/applications/low-code/job-queue/feature-dark-mode/` |
| `task_list_path` | `/home/artsmc/applications/low-code/job-queue/feature-dark-mode/task-list.md` |
| `pm_db_ids` | null (not yet set) |

If the path is not explicit in spec-plan's output, run:
```
Glob: "**/feature-dark-mode*/task-list.md"
```
to confirm the location before proceeding.

**Failure recovery (Step 1):**
If spec-plan errors or produces no output, stop the workflow and tell the user:
> "spec-plan failed during specification generation. You can retry directly with:
> `/spec-plan "add a dark mode toggle to the AIForge web app"`"

---

## Step 2: Review Specification Quality

**Action:**
```
Skill: spec-review
Args: (none — spec-review reads spec_dir from context/ambient state)
```

spec-review validates the generated docs for structural completeness, missing sections, contradictions, and coverage gaps.

**Branch A — Clean pass or warnings only:**
Continue immediately to Step 3. No user interaction required.

**Branch B — Errors found:**
Pause and ask the user via AskUserQuestion:
> "spec-review found issues in the generated specification:
> [list of errors]
>
> How do you want to proceed?
> 1. Continue anyway (proceed to planning with current specs)
> 2. Stop and fix (specs are saved at `/home/artsmc/applications/low-code/job-queue/feature-dark-mode/`)"

- If user chooses "Continue anyway" → proceed to Step 3
- If user chooses "Stop and fix" → halt workflow, direct user to spec_dir

**Expected for dark mode toggle:** spec-review is likely to pass cleanly (Quick-tier task list is simple, low error surface).

**State after Step 2:** unchanged — no new paths are produced.

**Failure recovery (Step 2):**
If spec-review itself errors (not spec errors, but tool failure):
> "spec-review failed to run. You can retry with `/spec-review` or continue to planning manually with `/start-phase plan {task_list_path}`."

---

## Step 3: Create Execution Plan

**Action:**
```
Skill: start-phase-plan
Args: "/home/artsmc/applications/low-code/job-queue/feature-dark-mode/task-list.md"
```

**What start-phase-plan does internally:**
- Reads the task list
- Analyzes task dependencies to determine wave structure
- Proposes agent assignments (e.g., Wave 1: `ui-developer` for toggle component; Wave 2: `frontend-developer` for Zustand state wiring; Wave 3: `nextjs-qa-developer` for tests)
- Presents the wave plan to the user for approval
- **Built-in human checkpoint:** user must explicitly approve before continuing

**Expected plan output (approximate):**
```
Wave 1: Add dark mode CSS variables and Tailwind config  → ui-developer
Wave 2: Create DarkModeToggle component                  → ui-developer
Wave 3: Wire Zustand store for theme state persistence   → frontend-developer
Wave 4: Integrate toggle into app layout/navbar          → frontend-developer
Wave 5: Write unit and integration tests                 → nextjs-qa-developer
```

**User checkpoint:**
- **User approves:** Continue to Step 4.
- **User rejects:** Halt workflow and tell the user:
  > "Execution plan rejected. Your specs are saved at `/home/artsmc/applications/low-code/job-queue/feature-dark-mode/`. You can re-plan anytime with:
  > `/start-phase plan /home/artsmc/applications/low-code/job-queue/feature-dark-mode/task-list.md`"

**State after Step 3:** unchanged for tracked variables. start-phase-plan may produce a `phase-summary.md` alongside the task list, but this orchestrator does not need to track that path explicitly.

**Failure recovery (Step 3):**
If start-phase-plan errors before showing the approval checkpoint:
> "start-phase-plan failed. You can retry with:
> `/start-phase plan /home/artsmc/applications/low-code/job-queue/feature-dark-mode/task-list.md`"

---

## Step 4: Import to PM-DB (best-effort)

**Action:**
```
Skill: pm-db
Args: "import --project feature-dark-mode --auto-confirm"
```

`--auto-confirm` is passed so pm-db does not block on interactive prompts. `feature_name` (`feature-dark-mode`) is substituted from state tracked in Step 1.

**Branch A — Success:**
Note the returned IDs (project_id, phase_id, plan_id) for reference. Update state:

| Variable | Value |
|---|---|
| `pm_db_ids` | `{ project_id: <X>, phase_id: <Y>, plan_id: <Z> }` |

Continue to Step 5.

**Branch B — Failure:**
This step is **best-effort** — failure does not block execution. Warn the user:
> "PM-DB import failed (non-blocking). The feature will still be executed. You can import tracking data later with:
> `/pm-db import --project feature-dark-mode`"

Then continue to Step 5 regardless.

**State after Step 4:** `pm_db_ids` set on success, null on failure.

---

## Step 5: Execute Tasks

**Mode decision:** mode is `"auto"` (not `"team"`), so the sequential executor is used.

**Action:**
```
Skill: start-phase-execute
Args: "/home/artsmc/applications/low-code/job-queue/feature-dark-mode/task-list.md"
```

**What start-phase-execute does internally:**
- Reads the task list and approved wave plan
- Executes each wave sequentially, delegating tasks to specialized agents (ui-developer, frontend-developer, nextjs-qa-developer)
- Applies quality gates between waves (lint, type-check, tests)
- Creates git commits after each completed wave
- Reports PM-DB tracking hooks if `pm_db_ids` are available

**Expected execution flow:**
```
Wave 1 → ui-developer adds Tailwind dark mode config, CSS variables
Wave 2 → ui-developer builds DarkModeToggle component (TSX + styles)
Wave 3 → frontend-developer adds Zustand store slice for theme persistence
Wave 4 → frontend-developer wires toggle into Layout/Navbar
Wave 5 → nextjs-qa-developer writes unit tests for toggle component and store
```

**Failure mid-execution:**
If a task fails during execution, tell the user:
> "Execution failed at [wave N / task name]. Completed waves: [list].
> You can resume where it left off with:
> `/feature-continue`
> or directly with:
> `/start-phase execute /home/artsmc/applications/low-code/job-queue/feature-dark-mode/task-list.md`"

---

## State Threading Summary

The table below shows every tracked variable and how it flows across steps:

| Variable | Set in Step | Used in Steps | Example Value |
|---|---|---|---|
| `feature_name` | 1 (spec-plan output) | 4 | `feature-dark-mode` |
| `spec_dir` | 1 (spec-plan output) | 2, 3 (error messages) | `/home/artsmc/applications/low-code/job-queue/feature-dark-mode/` |
| `task_list_path` | 1 (spec-plan output, confirmed via Glob) | 3, 5 | `/home/artsmc/applications/low-code/job-queue/feature-dark-mode/task-list.md` |
| `pm_db_ids` | 4 (pm-db import) | 5 (PM-DB hooks) | `{ project_id: 42, phase_id: 7, plan_id: 3 }` |

**Glob fallback for path resolution:**
If spec-plan's output does not make `task_list_path` unambiguous, run:
```
Glob: "**/feature-dark-mode*/task-list.md"
```
before Step 3 to confirm the exact path.

---

## Mode: Sequential vs Team

**For this request, mode is `"auto"` → sequential execution.**

Reasoning:
- Single app affected (Web frontend only)
- Feature is UI-focused with clear sequential dependencies (config → component → state → integration → tests)
- `"auto"` defers to spec-plan's tier detection (Quick) and start-phase-execute's own wave logic
- No `--team` flag is appended to any sub-skill invocation

**When team mode would apply instead:**
If the user had said "add dark mode to the AIForge web app with full API persistence of user preference", that would span Web + API, warranting `mode: "team"` with `start-phase-execute-team` and `--team` appended to spec-plan.

---

## Error Recovery Table (All Steps)

| Failed Step | What Was Completed | Recovery Command |
|---|---|---|
| Step 1: spec-plan | Nothing | `/spec-plan "add a dark mode toggle to the AIForge web app"` |
| Step 2: spec-review | Specs generated at `spec_dir` | `/spec-review` then manually continue |
| Step 3: start-phase-plan | Specs reviewed and saved | `/start-phase plan /home/artsmc/applications/low-code/job-queue/feature-dark-mode/task-list.md` |
| Step 4: pm-db import | Plan approved (non-blocking, continue) | `/pm-db import --project feature-dark-mode` (later, optional) |
| Step 5: start-phase-execute | All prior steps complete | `/feature-continue` or `/start-phase execute /home/artsmc/applications/low-code/job-queue/feature-dark-mode/task-list.md` |

---

## Final Output (Completion Summary)

When all five steps complete successfully, show:

```
Feature: add a dark mode toggle to the AIForge web app
Specs:   /home/artsmc/applications/low-code/job-queue/feature-dark-mode/
Tasks completed: 5 tasks across 5 waves

Next:
  /pm-db dashboard    — view project metrics
  /memory-bank-sync   — update project memory
```

No redundant detail is shown here — sub-skills already displayed their own output during execution.

---

## Notes on Skill Behavior

1. **spec-plan tier classification:** For "dark mode toggle on one app," spec-plan should consistently classify this as Quick (task-list only). If it misclassifies as Standard (FRD + TR), spec-review becomes more important as a quality gate.

2. **start-phase-plan approval is mandatory:** Even for a simple feature, the user approval checkpoint in Step 3 always fires. There is no way to bypass it from this orchestrator — this is by design.

3. **pm-db best-effort:** The skill explicitly marks Step 4 as non-blocking. If the PM-DB is not initialized or the import fails, the workflow continues rather than halting on a tracking concern.

4. **Sequential dependency chain:** Steps 1→2→3→4→5 are strictly sequential. No parallelism is introduced at the orchestrator level; parallelism is deferred to start-phase-execute-team (only used when mode is "team").

5. **Sub-skill output ownership:** This orchestrator does not reformat or summarize sub-skill output during execution. Each sub-skill owns its own display. The orchestrator only shows a brief completion summary at the end and error messages if something fails.
