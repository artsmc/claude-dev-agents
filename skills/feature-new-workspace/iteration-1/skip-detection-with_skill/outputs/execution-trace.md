# Execution Trace: feature-new Skip Detection

**User Request:** "I want to execute the file upload feature. Specs are already at /home/artsmc/applications/low-code/job-queue/feature-file-upload/docs/ and I've already reviewed them."

**Skill:** `/home/artsmc/.claude/skills/feature-new/SKILL.md`

**Mode:** auto (default — user did not specify)

---

## Phase 0: Argument Extraction

Before any step runs, the skill extracts its declared arguments:

```
feature_description = "file upload feature"
mode                = "auto"  (default)
```

The user also volunteered two facts out-of-band:
- Specs exist at `/home/artsmc/applications/low-code/job-queue/feature-file-upload/docs/`
- The user has already reviewed those specs

These are not formal skill arguments, but they are critical signals for the Skip Logic section.

---

## Phase 1: Pre-Flight — Checking for Existing Artifacts

The skill's **Skip Logic** section (near the bottom of SKILL.md) instructs:

> Use Glob to check for existing artifacts before each step. Don't re-run work that's already done.

The three things to check, in order, are:

| Artifact | Glob Pattern | Indicates |
|----------|-------------|-----------|
| task-list.md | `**/feature-*/task-list.md` or `**/feature-*/docs/task-list.md` | Specs exist → skip Steps 1-2 |
| phase-summary.md | `**/feature-*/phase-summary.md` | Planning done → skip Step 3 |
| PM-DB project record | (query pm-db, not a file) | Tracking exists → skip Step 4 |

### 1a. Check for task-list.md (specs)

The user explicitly stated specs are at:
```
/home/artsmc/applications/low-code/job-queue/feature-file-upload/docs/
```

Glob check executed:
```
Glob: "/home/artsmc/applications/low-code/job-queue/feature-file-upload/docs/task-list.md"
```

Fallback if not found at that exact path:
```
Glob: "**/feature-file-upload/**/task-list.md"
```

**Expected outcome:** task-list.md is found. The skill now knows:

```
spec_dir       = /home/artsmc/applications/low-code/job-queue/feature-file-upload/docs/
feature_name   = feature-file-upload   (derived from directory name)
task_list_path = /home/artsmc/applications/low-code/job-queue/feature-file-upload/docs/task-list.md
```

### 1b. Check for phase-summary.md (planning)

```
Glob: "/home/artsmc/applications/low-code/job-queue/feature-file-upload/phase-summary.md"
```

Fallback:
```
Glob: "**/feature-file-upload/**/phase-summary.md"
```

**Expected outcome:** NOT found (user only said specs exist and are reviewed — they did not say planning is done).

### 1c. Check PM-DB for existing project

PM-DB is best-effort and the user gave no signal that it already has this feature. No check is performed proactively; this is deferred to Step 4.

---

## Phase 2: Skip Detection Decision

### What the skill detected

- task-list.md: FOUND
- phase-summary.md: NOT FOUND

### What the skill's Skip Logic says

> **Specs exist** (task-list.md found in job-queue): Skip Steps 1-2, confirm with user before proceeding

The key phrase here is **"confirm with user before proceeding"**. The skill does NOT silently skip. It must ask the user first.

### Confirmation required before skipping

**YES — the skill must confirm with the user before skipping Steps 1-2.**

The skip logic explicitly requires confirmation. The user's statement ("Specs are already at ... and I've already reviewed them") is strong evidence, but the skill still confirms because:

1. The user may have stated the wrong path.
2. task-list.md may be incomplete or from a different iteration.
3. The spec-review step (Step 2) has safety implications — silently skipping it without user awareness would remove the safety net.

The confirmation prompt to the user would look like:

```
I found existing specs at:
  /home/artsmc/applications/low-code/job-queue/feature-file-upload/docs/

You mentioned you've already reviewed them.

Would you like me to:
  (a) Skip spec generation and review, and go straight to execution planning
  (b) Re-run spec-plan and spec-review from scratch
```

The user's request ("I want to execute the feature") plus their explicit statement ("I've already reviewed them") makes option (a) the obvious answer, but the skill asks rather than assumes.

---

## Phase 3: Steps Skipped and Why

| Step | Action | Reason |
|------|--------|--------|
| Step 1 — spec-plan | SKIPPED | task-list.md found at user-provided path; user confirmed no re-generation needed |
| Step 2 — spec-review | SKIPPED | User explicitly stated "I've already reviewed them"; skip confirmed by user in confirmation prompt above |
| Step 3 — start-phase-plan | RUNS | phase-summary.md not found; no planning has been done |
| Step 4 — pm-db import | RUNS (best-effort) | No evidence this feature is already in PM-DB |
| Step 5 — start-phase-execute | RUNS | This is the user's stated goal ("I want to execute") |

---

## Phase 4: Starting Step After Skip Confirmation

**Starting step: Step 3 — Create Execution Plan**

The skill proceeds with:

```
State before Step 3:
  feature_name   = feature-file-upload
  spec_dir       = /home/artsmc/applications/low-code/job-queue/feature-file-upload/docs/
  task_list_path = /home/artsmc/applications/low-code/job-queue/feature-file-upload/docs/task-list.md
  pm_db_ids      = null (not yet imported)
```

---

## Phase 5: Execution from Step 3 Forward

### Step 3: Create Execution Plan

```
Skill: start-phase-plan
Args:  "/home/artsmc/applications/low-code/job-queue/feature-file-upload/docs/task-list.md"
```

start-phase-plan reads the task list, analyzes task dependencies, proposes wave structure and agent assignments, then presents a plan to the user for approval.

**Branch A — User approves the plan:**
- Continue to Step 4.

**Branch B — User rejects the plan:**
- STOP workflow.
- Tell user:
  ```
  Execution plan was not approved. Your specs are saved at:
    /home/artsmc/applications/low-code/job-queue/feature-file-upload/docs/

  You can re-plan at any time with:
    /start-phase plan /home/artsmc/applications/low-code/job-queue/feature-file-upload/docs/task-list.md
  ```

### Step 4: Import to PM-DB (best-effort)

```
Skill: pm-db
Args:  "import --project feature-file-upload --auto-confirm"
```

**Branch A — Success:**
- Capture returned IDs (project ID, phase ID, plan ID) into `pm_db_ids`.
- Continue to Step 5.

**Branch B — Failure:**
- Warn the user:
  ```
  PM-DB import failed — this is non-blocking. Continuing to execution.
  You can import manually later with: /pm-db import --project feature-file-upload
  ```
- Continue to Step 5 regardless.

### Step 5: Execute Tasks

Mode is "auto" (default), so the skill selects:

```
Skill: start-phase-execute
Args:  "/home/artsmc/applications/low-code/job-queue/feature-file-upload/docs/task-list.md"
```

(Mode "team" is not active, so start-phase-execute-team is NOT used.)

start-phase-execute handles:
- Wave decomposition
- Agent delegation per task
- Quality gates between waves
- Git commits after each completed wave
- PM-DB tracking hooks (using pm_db_ids if available)

**Branch A — Execution completes successfully:**
- Continue to Completion summary.

**Branch B — Execution fails mid-run:**
- The skill identifies which task failed.
- Tell the user:
  ```
  Execution failed at task: [task name from execute output]

  Completed before failure:
    - Waves 1..N (list from execute output)

  Resume with:
    /feature-continue
  or:
    /start-phase execute /home/artsmc/applications/low-code/job-queue/feature-file-upload/docs/task-list.md
  ```

---

## Phase 6: Completion Summary

After all steps finish, the skill shows:

```
Feature: file upload feature
Specs:   /home/artsmc/applications/low-code/job-queue/feature-file-upload/docs/
Tasks completed: (from start-phase-execute output)

Next:
  /pm-db dashboard    — view project metrics
  /memory-bank-sync   — update project memory
```

The skill keeps this brief because sub-skills already displayed detailed output during their runs.

---

## Phase 7: Recovery Commands Reference

The skill's error handling table maps each step to an exact recovery command. With the resolved state for this request:

| Failed Step | Recovery Command |
|-------------|-----------------|
| Step 1 (skipped) | N/A — was skipped |
| Step 2 (skipped) | N/A — was skipped |
| Step 3 — start-phase-plan | `/start-phase plan /home/artsmc/applications/low-code/job-queue/feature-file-upload/docs/task-list.md` |
| Step 4 — pm-db import | `/pm-db import --project feature-file-upload` (or skip entirely) |
| Step 5 — start-phase-execute | `/feature-continue` or `/start-phase execute /home/artsmc/applications/low-code/job-queue/feature-file-upload/docs/task-list.md` |

---

## Summary: Key Observations About the Skill

### 1. Skip detection mechanism
The skill uses Glob to check for existing artifacts before each step. The primary signal is the presence of `task-list.md` anywhere under `job-queue/feature-*/`. The user-provided path is used directly as the starting Glob target, with a wildcard fallback.

### 2. Confirmation is required before skipping
The skip logic explicitly says "confirm with user before proceeding." Even though the user's message is unambiguous, the skill does not skip silently. It presents a confirm prompt naming the found path and asking for explicit approval to skip Steps 1-2.

### 3. task-list.md location resolution
The skill looks for `task-list.md` at the user-provided path:
```
/home/artsmc/applications/low-code/job-queue/feature-file-upload/docs/task-list.md
```
If not found there, it falls back to Glob:
```
**/feature-file-upload/**/task-list.md
```
The resolved path becomes `task_list_path` and is passed as the argument to every subsequent sub-skill.

### 4. Starting step
After skipping Steps 1-2 and receiving user confirmation: **Step 3 (start-phase-plan)**.

### 5. Mode "auto" behavior
Because the user did not pass `--team`, mode defaults to "auto". In Step 5 this resolves to `start-phase-execute` (not `start-phase-execute-team`). Mode "auto" defers to each sub-skill's own parallelism detection.

### 6. PM-DB is best-effort, never blocking
Even if PM-DB import fails, the skill warns and continues. The user will not be blocked from execution by a tracking failure.

### 7. The spec-review skip is sound
Skipping Step 2 (spec-review) is safe here because the user explicitly stated they reviewed the specs. The confirmation prompt makes this explicit, so the user is not accidentally bypassing the safety net without awareness.
