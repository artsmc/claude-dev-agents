# Execution Trace: feature-new Skip Logic
## User Request
"I want to execute the file upload feature. Specs are already at /home/artsmc/applications/low-code/job-queue/feature-file-upload/docs/ and I've already reviewed them."

**Skill invoked:** `feature-new`
**Effective args:**
- `feature_description`: "execute the file upload feature"
- `mode`: "auto" (default, no --team or --sequential flag found in description)

---

## Phase 0: Argument Parsing

The skill requires scanning `feature_description` for inline flags before doing anything.

**Scan result:** No `--team` or `--sequential` present in "execute the file upload feature".

**Cleaned description:** "execute the file upload feature"
**Resolved mode:** "auto"

No flag stripping needed. Proceed to pre-flight checks.

---

## Phase 1: Pre-Flight Checks (Skip Logic Section)

Before invoking Step 1 (spec-plan), the skill mandates running Glob checks for existing artifacts. The user's message contains two explicit signals:

- **Signal 1 — specs exist:** "Specs are already at /home/artsmc/applications/low-code/job-queue/feature-file-upload/docs/"
- **Signal 2 — reviewed:** "I've already reviewed them"

Despite these clear signals, the skill states: **"Confirmation is mandatory before skipping. Even if the user's message clearly implies steps are done, present what you found and ask."**

### Check 1: task-list.md

The skill's default Glob patterns are:
```
Glob: "**/feature-*/task-list.md"
Glob: "**/feature-*/docs/task-list.md"
```

However, the user provided an explicit path. The skill instructs: "If a path isn't clear from sub-skill output, use Glob." Since the user gave us a concrete path, we use it directly AND also run the Glob to confirm what exists on disk.

**Where we look (in priority order):**

1. **User-provided path, common locations:**
   - `/home/artsmc/applications/low-code/job-queue/feature-file-upload/docs/task-list.md`
   - `/home/artsmc/applications/low-code/job-queue/feature-file-upload/task-list.md`

2. **Glob fallback (catches non-standard placements):**
   ```
   Glob: "**/feature-file-upload/task-list.md"
   Glob: "**/feature-file-upload/docs/task-list.md"
   ```
   Applied under `/home/artsmc/applications/low-code/job-queue/` (the known job-queue directory).

**Assumed result:** task-list.md found at:
```
/home/artsmc/applications/low-code/job-queue/feature-file-upload/docs/task-list.md
```

This satisfies "Check for task-list.md → specs exist."

### Check 2: phase-summary.md

```
Glob: "**/feature-file-upload/planning/phase-structure/phase-summary.md"
```
Applied under `/home/artsmc/applications/low-code/job-queue/`.

**Expected result:** NOT found (user said specs exist and are reviewed, but has not mentioned planning is done — they said "I want to execute", implying planning has not yet been done).

### Skip Matrix Evaluation

| Condition | Status |
|---|---|
| task-list.md found | YES |
| User said reviewed | YES ("I've already reviewed them") |
| phase-summary.md found | NO |
| PM-DB has feature | UNKNOWN (not checked yet) |

Applying the skip matrix:

| Found | User said reviewed | Skip Steps |
|-------|-------------------|------------|
| task-list.md | Yes | **1 + 2** |

**Determination:** Steps 1 (spec-plan) and 2 (spec-review) are candidates to skip. Steps 3, 4, and 5 proceed normally.

---

## Phase 2: Mandatory Confirmation via AskUserQuestion

The skill is explicit: **"Confirmation is mandatory before skipping."** This is NOT optional even though the user's intent is unambiguous. The skill's rationale is to prevent silently skipping spec-review without explicit user awareness.

### Exact Confirmation Prompt

```
AskUserQuestion:
  "I found existing specs at: /home/artsmc/applications/low-code/job-queue/feature-file-upload/docs/task-list.md

   You also said you've already reviewed them.

   Skip spec generation and review, and go straight to planning?"

  Options:
    "Yes, skip to planning"
    "No, regenerate from scratch"
```

**Notes on the prompt construction:**
- The `{path}` placeholder in the skill template resolves to the full absolute path found by Glob/direct check: `/home/artsmc/applications/low-code/job-queue/feature-file-upload/docs/task-list.md`
- Because the user said "reviewed," both Steps 1 AND 2 are being offered for skip (not just Step 1)
- The two options map exactly to the skip matrix outcomes:
  - "Yes, skip to planning" → skip Steps 1 + 2, jump to Step 3
  - "No, regenerate from scratch" → run the full flow from Step 1

**We MUST wait for user response before proceeding. No assumptions are made.**

---

## Phase 3: After Confirmation — Starting Step

Assuming user selects **"Yes, skip to planning":**

**State at start of Step 3:**
```
feature_name     = "feature-file-upload"
spec_dir         = "/home/artsmc/applications/low-code/job-queue/feature-file-upload/docs/"
task_list_path   = "/home/artsmc/applications/low-code/job-queue/feature-file-upload/docs/task-list.md"
pm_db_ids        = null  (not yet imported)
```

**Starting step:** Step 3 — Create Execution Plan

```
Skill: start-phase-plan
Args: "/home/artsmc/applications/low-code/job-queue/feature-file-upload/docs/task-list.md"
```

start-phase-plan will:
1. Read the task-list at the provided path
2. Analyze task dependencies
3. Propose a wave structure and agent assignments
4. Present a built-in approval checkpoint to the user

The skill notes: "start-phase-plan has a built-in user approval checkpoint." This is the second human checkpoint in the workflow. We wait for user approval here as well.

- **User approves:** Continue to Step 4.
- **User rejects:** Stop. Inform the user: "Specs are saved at /home/artsmc/applications/low-code/job-queue/feature-file-upload/docs/ — you can re-plan with `/start-phase plan /home/artsmc/applications/low-code/job-queue/feature-file-upload/docs/task-list.md`"

---

## Phase 4: PM-DB Import (Step 4) — Best-Effort

```
Skill: pm-db
Args: "import --project feature-file-upload --auto-confirm"
```

**Key characteristic: this step is EXPLICITLY best-effort (not blocking).**

The skill states: "Import the feature into PM-DB for tracking. This is helpful but not blocking — if it fails, warn and continue."

- **Success:** Note returned project/phase/plan IDs in state as `pm_db_ids`. These are referenced in the completion summary.
- **Failure:** Warn the user: "PM-DB import failed for feature-file-upload. You can import later with `/pm-db import --project feature-file-upload`." Then proceed immediately to Step 5 without stopping.

This is the ONLY step in the entire workflow where failure does not halt execution.

---

## Phase 5: Execute Tasks (Step 5)

Mode is "auto" (resolved in Phase 0), so:

```
Skill: start-phase-execute
Args: "/home/artsmc/applications/low-code/job-queue/feature-file-upload/docs/task-list.md"
```

(Not `start-phase-execute-team`, because mode != "team".)

start-phase-execute handles internally: wave decomposition, agent delegation, quality gates, git commits, and PM-DB tracking hooks.

**If it fails mid-execution:**
- Name the failed task
- Tell the user they can resume with:
  - `/feature-continue`
  - `/start-phase execute /home/artsmc/applications/low-code/job-queue/feature-file-upload/docs/task-list.md`

---

## Phase 6: Completion Summary

After all steps finish:

```
Feature: execute the file upload feature
Specs: /home/artsmc/applications/low-code/job-queue/feature-file-upload/docs/
Tasks completed: (from start-phase-execute output)

Next:
  /pm-db dashboard    — view project metrics
  /memory-bank-sync   — update project memory
```

The skill instructs: "Keep it short. The sub-skills already showed detailed output during their runs." No duplication of sub-skill output.

---

## Recovery Commands with Resolved Paths

The skill's error table uses template placeholders. Here they are resolved for this specific invocation:

| Failed Step | Recovery Command (Resolved) |
|---|---|
| Step 1 (skipped) | `/spec-plan "execute the file upload feature"` |
| Step 2 (skipped) | `/spec-review` |
| Step 3 | `/start-phase plan /home/artsmc/applications/low-code/job-queue/feature-file-upload/docs/task-list.md` |
| Step 4 | `/pm-db import --project feature-file-upload` (or skip entirely) |
| Step 5 | `/feature-continue` or `/start-phase execute /home/artsmc/applications/low-code/job-queue/feature-file-upload/docs/task-list.md` |

---

## Full Step Execution Summary

| Step | Action | Sub-skill Invoked | Status |
|---|---|---|---|
| Arg parsing | Strip flags, resolve mode | — | mode="auto", description="execute the file upload feature" |
| Pre-flight check 1 | Glob for task-list.md | — | FOUND at `.../feature-file-upload/docs/task-list.md` |
| Pre-flight check 2 | Glob for phase-summary.md | — | NOT FOUND |
| Confirmation | AskUserQuestion (mandatory) | — | WAIT for user |
| Step 1 | spec-plan | SKIPPED (task-list.md found + user reviewed) | — |
| Step 2 | spec-review | SKIPPED (user confirmed reviewed) | — |
| Step 3 | start-phase-plan | `start-phase-plan "/home/artsmc/applications/low-code/job-queue/feature-file-upload/docs/task-list.md"` | Runs with built-in approval checkpoint |
| Step 4 | pm-db import | `pm-db "import --project feature-file-upload --auto-confirm"` | Best-effort only |
| Step 5 | start-phase-execute | `start-phase-execute "/home/artsmc/applications/low-code/job-queue/feature-file-upload/docs/task-list.md"` | Blocking |
| Completion | Summary output | — | Brief only |

---

## Key Skill Behaviors Observed

1. **Skip detection is Glob-first, not user-statement-first.** The skill does not take the user at their word alone — it verifies artifacts exist on disk before offering to skip.

2. **Confirmation is unconditionally mandatory.** The AskUserQuestion for skip confirmation fires even when the user has explicitly stated both conditions (specs exist, reviewed). This is a deliberate safety design to prevent silently bypassing spec-review.

3. **User-provided path resolves task-list.md lookup.** Given the explicit path `/home/artsmc/applications/low-code/job-queue/feature-file-upload/docs/`, the skill checks that directory directly (in addition to Glob) rather than using only the wildcard patterns.

4. **Skip granularity depends on "reviewed" signal.** If the user had NOT said they reviewed the specs, the skip matrix would only skip Step 1 (spec-plan) but still run Step 2 (spec-review). The "reviewed" claim unlocks the Step 2 skip.

5. **PM-DB is the only non-blocking step.** Every other step failure halts the workflow. PM-DB import failure emits a warning and execution continues.

6. **Mode determines Step 5 sub-skill.** "auto" → `start-phase-execute`. Only "team" → `start-phase-execute-team`. The feature_description contained no --team flag so auto is used.

7. **State threading.** The `task_list_path` resolved during pre-flight is passed unchanged into Step 3 (start-phase-plan) and Step 5 (start-phase-execute). No re-discovery is needed mid-workflow.
