# Execution Trace: feature-new skill
## User Request: "I want to add a dark mode toggle to the AIForge web app"

**Skill file:** `/home/artsmc/.claude/skills/feature-new/SKILL.md`
**Date:** 2026-03-09

---

## 1. Argument Parsing

**Raw input:** `"I want to add a dark mode toggle to the AIForge web app"`

The skill instructs scanning `feature_description` for `--team` or `--sequential` flags before doing anything else.

**Scan for flags:**
- Search string for `--team`: NOT FOUND
- Search string for `--sequential`: NOT FOUND

**Result:**
- `feature_description` = `"I want to add a dark mode toggle to the AIForge web app"` (no stripping needed)
- `mode` = `"auto"` (default, since no flag was present)

**Cleaned description passed to sub-skills:** `"I want to add a dark mode toggle to the AIForge web app"`

**Mode selected: "auto"** — this defers to each sub-skill's own auto-detection. spec-plan picks tier autonomously; start-phase-execute picks parallelism autonomously. No `--team` flag is appended to spec-plan args.

---

## 2. Pre-Flight Skip Checks

Before invoking any sub-skill, the skill runs two Glob checks to detect existing artifacts and avoid redundant work.

### Check 1: Does a task-list.md already exist?

```
Glob: "**/feature-*/task-list.md"
Glob: "**/feature-*/docs/task-list.md"
```

**Expected result for this fresh request:** No matches found. The feature has never been started. Proceed without prompting.

### Check 2: Does a phase-summary.md already exist?

```
Glob: "**/feature-*/planning/phase-structure/phase-summary.md"
```

**Expected result:** No matches found. No planning artifacts exist. Proceed without prompting.

### Skip matrix evaluation:

| Artifact Found | User Said Reviewed | Skip Steps |
|---|---|---|
| task-list.md | — | — |
| phase-summary.md | — | — |

Nothing found. No skipping. All five steps will execute in full.

**If artifacts HAD been found**, the skill would pause and present an AskUserQuestion before skipping any safety step. Confirmation is mandatory — the spec-review safety net cannot be silently bypassed.

---

## 3. First Action: Step 1 — Generate Feature Specification

No flags to append (mode is "auto", not "team"). Invoke spec-plan with the cleaned description.

**Skill invocation:**
```
Skill: spec-plan
Args: "I want to add a dark mode toggle to the AIForge web app"
```

spec-plan runs its own triage gate internally. For this request, the expected tier classification:

- Affects the AIForge web app only (one app: `apps/web`)
- Dark mode toggle is a UI concern — likely 5–10 tasks
- No security-sensitive changes, no cross-app contract changes
- Expected tier: **Standard** (FRD + TR + task-list)

spec-plan generates output into a directory based on the feature name. Likely output path:

```
/home/artsmc/applications/low-code/job-queue/feature-dark-mode-toggle/docs/
  ├── FRD.md
  ├── TR.md
  └── task-list.md
```

**State captured after Step 1:**
- `feature_name` = `"feature-dark-mode-toggle"` (derived from the spec-plan output directory name)
- `spec_dir` = `/home/artsmc/applications/low-code/job-queue/feature-dark-mode-toggle/docs/`
- `task_list_path` = `/home/artsmc/applications/low-code/job-queue/feature-dark-mode-toggle/docs/task-list.md`

If spec-plan output does not make the path explicit, the skill uses Glob to locate it:
```
Glob: "**/feature-*/task-list.md"
Glob: "**/feature-*/docs/task-list.md"
```

**If Step 1 fails:** Stop immediately. Inform the user what went wrong. Recovery command:
```
/spec-plan "I want to add a dark mode toggle to the AIForge web app"
```

---

## 4. Subsequent Steps

### Step 2: Review Specification Quality

**Skill invocation:**
```
Skill: spec-review
Args: (none — spec-review operates on the most recently generated specs in context)
```

spec-review validates structural quality of the generated FRD and TR. Two possible outcomes:

**Outcome A — Clean pass or warnings only:**
- Proceed immediately to Step 3 without user interaction.

**Outcome B — Errors found:**
- Pause and present AskUserQuestion:
  ```
  "spec-review found issues with the generated specification.
   Options:
     [Continue anyway] — proceed to planning with current specs
     [Stop and fix]    — stop here; specs are saved at:
                         /home/artsmc/applications/low-code/job-queue/feature-dark-mode-toggle/docs/"
  ```
- If user chooses "Continue anyway" → proceed to Step 3.
- If user chooses "Stop and fix" → halt workflow, tell user specs are saved.

**If Step 2 fails (tool error, not spec quality issue):** Stop. Recovery command:
```
/spec-review
```

---

### Step 3: Create Execution Plan

**Skill invocation:**
```
Skill: start-phase-plan
Args: "/home/artsmc/applications/low-code/job-queue/feature-dark-mode-toggle/docs/task-list.md"
```

start-phase-plan analyzes the task list, identifies dependencies, proposes wave structure, and assigns agents. It has a **built-in user approval checkpoint** — the skill does not need to add one here.

**Expected behavior for dark mode toggle:**
- start-phase-plan reads `task_list_path`
- Proposes a 1–2 wave structure (UI implementation is largely sequential: config → components → testing)
- Likely agent assignments: `ui-developer`, `frontend-developer`, possibly `nextjs-qa-developer`
- Presents proposed plan to user for approval

**Outcome A — User approves:**
- Continue to Step 4.

**Outcome B — User rejects:**
- Stop workflow. Inform user that specs are saved and they can re-plan when ready. Recovery command:
  ```
  /start-phase plan /home/artsmc/applications/low-code/job-queue/feature-dark-mode-toggle/docs/task-list.md
  ```

**If Step 3 fails (tool error):** Stop. Same recovery command as above.

**State updated after Step 3:**
- No new path values, but planning docs are now present at:
  `**/feature-dark-mode-toggle/planning/phase-structure/phase-summary.md`

---

### Step 4: Import to PM-DB (Best-Effort)

**Skill invocation:**
```
Skill: pm-db
Args: "import --project feature-dark-mode-toggle --auto-confirm"
```

`--auto-confirm` suppresses interactive prompts inside pm-db so the workflow continues without manual confirmation at this step.

**This step is non-blocking.** Two outcomes:

**Outcome A — Success:**
- pm-db returns project/phase/plan IDs.
- State updated: `pm_db_ids` = returned IDs (noted for reference, passed to no further steps).
- Continue to Step 5 immediately.

**Outcome B — Failure (any reason: DB unavailable, schema mismatch, etc.):**
- Log a warning to the user: "PM-DB import failed. You can import later with `/pm-db import --project feature-dark-mode-toggle`. Continuing to execution."
- `pm_db_ids` = `null`
- **Continue to Step 5 regardless.** This is the only step in the workflow that does not block on failure.

---

### Step 5: Execute Tasks

**Mode is "auto"** (no `--team` or `--sequential` flag was passed). The skill's Step 5 logic:

```
If mode is "team":
    Skill: start-phase-execute-team
    Args: "{task_list_path}"

If mode is "sequential" or "auto":
    Skill: start-phase-execute
    Args: "{task_list_path}"
```

Since mode = "auto", the sequential path is used.

**Skill invocation:**
```
Skill: start-phase-execute
Args: "/home/artsmc/applications/low-code/job-queue/feature-dark-mode-toggle/docs/task-list.md"
```

start-phase-execute handles everything internally: wave decomposition, agent delegation, quality gates, git commits, and PM-DB tracking hooks.

**If Step 5 fails mid-execution:**
- Identify which task failed from execution output.
- Inform user: "Execution stopped at task [N]. Use one of the following to resume:"
  ```
  /feature-continue
  /start-phase execute /home/artsmc/applications/low-code/job-queue/feature-dark-mode-toggle/docs/task-list.md
  ```

---

## 5. PM-DB Import Handling: Blocking vs Best-Effort

| Step | Blocking? | On Failure |
|---|---|---|
| Step 1 (spec-plan) | YES | Stop, give `/spec-plan` recovery command |
| Step 2 (spec-review) | YES (errors: user decides) | User chooses continue or stop |
| Step 3 (start-phase-plan) | YES | Stop, give `/start-phase plan` recovery command |
| Step 4 (pm-db import) | **NO — best-effort** | Warn, continue to Step 5 |
| Step 5 (execute) | YES | Stop, give `/feature-continue` recovery command |

The rationale stated in the skill: PM-DB tracking is helpful but not required to build the feature. Failing to record in the database should never block actual development work.

---

## 6. State Threading Between Steps

The following values are tracked across the full workflow and must survive between sub-skill invocations:

| Variable | Set By | Used By | Value (for this request) |
|---|---|---|---|
| `feature_description` | Argument parsing | Step 1, error messages | `"I want to add a dark mode toggle to the AIForge web app"` |
| `mode` | Argument parsing | Step 5 skill selection | `"auto"` |
| `feature_name` | Step 1 output | Step 4 (pm-db import arg) | `"feature-dark-mode-toggle"` |
| `spec_dir` | Step 1 output | Step 2 error messages, completion summary | `/home/artsmc/applications/low-code/job-queue/feature-dark-mode-toggle/docs/` |
| `task_list_path` | Step 1 output | Step 3 arg, Step 5 arg, recovery commands | `/home/artsmc/applications/low-code/job-queue/feature-dark-mode-toggle/docs/task-list.md` |
| `pm_db_ids` | Step 4 output | Completion summary only | returned IDs or `null` |

**Path resolution fallback:** If spec-plan does not explicitly output `spec_dir` or `task_list_path` in a parseable form, the skill uses Glob to locate them:
```
Glob: "**/feature-*/task-list.md"
Glob: "**/feature-*/docs/task-list.md"
```

The skill instructs: "If a path isn't clear from sub-skill output, use Glob." This is the only case where the orchestrator actively inspects the filesystem mid-workflow.

---

## 7. Mode Selection: Team vs Sequential

**Selected mode: sequential (via "auto")**

**Why auto resolves to sequential (start-phase-execute):**

The SKILL.md Step 5 logic is unambiguous:
```
If mode is "sequential" or "auto":
    Skill: start-phase-execute
```

"auto" and "sequential" share the same branch. The "team" branch only triggers when `mode == "team"`, which requires an explicit `--team` flag in the user's input.

**Why this is the correct mode for this request:**

- No `--team` flag in input → mode stays "auto"
- Dark mode toggle is a contained UI feature, primarily in `apps/web`
- Sequential execution is appropriate: CSS/config setup must precede component updates, which must precede testing
- start-phase-execute handles its own internal parallelism where safe; the orchestrator does not need to force team mode

**When team mode would have been used:**
- Input: `"add dark mode --team"` → strips flag, sets `mode = "team"` → Step 5 invokes `start-phase-execute-team`
- Team mode is appropriate for cross-app features (e.g., dark mode affecting API theming + web + Mastra Studio) or when the user explicitly wants parallel agent execution

---

## 8. Skill-Specific Recovery Commands

Recovery commands are surfaced only when a step fails. The exact strings from the skill's error handling table, populated with state values for this request:

| Failed Step | What to Tell the User | Recovery Command |
|---|---|---|
| Step 1 (spec-plan) | "Spec generation failed. Retry with:" | `/spec-plan "I want to add a dark mode toggle to the AIForge web app"` |
| Step 2 (spec-review) | "Spec review encountered an error. Retry with:" | `/spec-review` |
| Step 3 (start-phase-plan) | "Phase planning failed. Specs are saved at /home/artsmc/applications/low-code/job-queue/feature-dark-mode-toggle/docs/. Retry with:" | `/start-phase plan /home/artsmc/applications/low-code/job-queue/feature-dark-mode-toggle/docs/task-list.md` |
| Step 4 (pm-db import) | "PM-DB import failed (non-blocking). Import later with:" | `/pm-db import --project feature-dark-mode-toggle` |
| Step 5 (execute) | "Execution stopped at task [N]. Resume with:" | `/feature-continue` or `/start-phase execute /home/artsmc/applications/low-code/job-queue/feature-dark-mode-toggle/docs/task-list.md` |

Note: Step 2 recovery is listed in the skill's table but the skill does not provide a path argument because spec-review operates on specs already in context — there is no path argument to supply.

---

## 9. Completion Summary (Expected Output)

When all five steps complete successfully, the skill outputs a brief summary (sub-skills already showed their own detailed output during runs):

```
Feature: I want to add a dark mode toggle to the AIForge web app
Specs: /home/artsmc/applications/low-code/job-queue/feature-dark-mode-toggle/docs/
Tasks completed: (from start-phase-execute output)

Next:
  /pm-db dashboard    — view project metrics
  /memory-bank-sync   — update project memory
```

---

## 10. Full Invocation Sequence (Summary)

```
# Pre-flight (no sub-skill, just Glob)
Glob: "**/feature-*/task-list.md"
Glob: "**/feature-*/docs/task-list.md"
Glob: "**/feature-*/planning/phase-structure/phase-summary.md"
→ No matches. Proceed.

# Step 1
Skill: spec-plan
Args: "I want to add a dark mode toggle to the AIForge web app"
→ Captures: feature_name, spec_dir, task_list_path

# Step 2
Skill: spec-review
Args: (none)
→ Clean pass → continue

# Step 3
Skill: start-phase-plan
Args: "/home/artsmc/applications/low-code/job-queue/feature-dark-mode-toggle/docs/task-list.md"
→ User approves plan → continue

# Step 4
Skill: pm-db
Args: "import --project feature-dark-mode-toggle --auto-confirm"
→ Best-effort. Success or warn-and-continue.

# Step 5
Skill: start-phase-execute
Args: "/home/artsmc/applications/low-code/job-queue/feature-dark-mode-toggle/docs/task-list.md"
→ Executes all waves. Reports completion.
```
