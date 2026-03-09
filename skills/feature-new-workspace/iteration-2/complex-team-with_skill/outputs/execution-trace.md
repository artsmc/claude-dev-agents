# Execution Trace: feature-new skill
## Input: "Build a complete notification system with real-time WebSocket events, email digests, and in-app notification center --team"

---

## 1. Argument Parsing (the `--team` flag)

Per the SKILL.md "Argument Parsing" section, before doing anything else, scan the raw
`feature_description` string for inline flags.

**Raw input received:**
```
"Build a complete notification system with real-time WebSocket events, email digests, and in-app notification center --team"
```

**Scan for `--team` or `--sequential`:**
- `--team` is present at the end of the string. Match found.
- `--sequential` is NOT present.

**Result of scan:**
- Flag found: `--team`
- `mode` is set to: `"team"`

---

## 2. Strip the Flag and Set Mode

The SKILL.md says: "strip the flag from the description and set mode accordingly" and "Pass the cleaned description (without flags) to sub-skills."

**Cleaned `feature_description` (flags removed):**
```
"Build a complete notification system with real-time WebSocket events, email digests, and in-app notification center"
```

**`mode` variable:**
```
mode = "team"
```

This cleaned description is the value used in every subsequent sub-skill invocation. The `--team` flag is NOT passed wholesale to all sub-skills — the SKILL.md specifies exactly where it is re-appended (only to spec-plan, see Step 1 below).

---

## 3. Pre-Flight Skip Checks

Before starting Step 1, the skill runs Glob checks to detect existing artifacts from a prior
run of this feature. This prevents silently re-generating work the user has already done.

### Check 1: Look for an existing task-list.md

```
Glob: "**/feature-*/task-list.md"
Glob: "**/feature-*/docs/task-list.md"
```

**What to look for:**
- Any directory matching `feature-notification-system`, `feature-notification*`, or similar
  slugs that correspond to this feature description.

**If task-list.md is found → mandatory user confirmation:**
```
AskUserQuestion:
  "I found existing specs at: ./job-queue/feature-notification-system/docs/task-list.md
   Skip spec generation and review, and go straight to planning?"
  Options: "Yes, skip to planning" / "No, regenerate from scratch"
```

Note: Even if the user's original message implies freshness, the SKILL.md is explicit:
"Confirmation is mandatory before skipping."

### Check 2: Look for an existing phase-summary.md

```
Glob: "**/feature-*/planning/phase-structure/phase-summary.md"
```

**If phase-summary.md is found:**
This means planning (Step 3) was already completed. That step would be skipped as well.

### Skip Matrix Applied

For this trace, assume no existing artifacts are found (this is a fresh run). All five steps
will execute in order. No skip prompts are issued.

---

## 4. First Action: Step 1 — Generate Feature Specification

**Skill invoked:** `spec-plan`

The SKILL.md rule for Step 1 args:
> `"{{feature_description}}"` (append `" --team"` if mode is "team")

Since `mode = "team"`, the `--team` flag is re-appended to the spec-plan invocation.

**Exact invocation:**
```
Skill: spec-plan
Args:  "Build a complete notification system with real-time WebSocket events, email digests, and in-app notification center --team"
```

The `--team` flag is passed here because spec-plan explicitly supports it (the SKILL.md documents "Re-append `--team` to spec-plan args only if mode is 'team'"). Other sub-skills in later steps do NOT receive `--team` as a CLI argument — mode is handled by the orchestrator choosing which execution skill to call (see Step 5).

**What spec-plan does internally (not traced here, per instructions):**
- Runs its triage gate to classify tier (Quick / Standard / Full)
- For a notification system spanning WebSocket infrastructure, email integration, and an
  in-app UI center across at minimum 3 apps (API, Web, Mastra), this is almost certainly a
  **Full** tier: 3+ apps affected, 15+ tasks anticipated, likely security-sensitive (auth tokens
  in WebSocket handshakes).
- Generates: FRD + FRS + GS + TR + task-list.md

**After completion — extract state:**

The skill's SKILL.md "State Tracking" section requires capturing:
- `feature_name` — the directory slug created by spec-plan (e.g., `feature-notification-system`)
- `spec_dir` — where spec-plan saved files (e.g., `./job-queue/feature-notification-system/docs/`)
- `task_list_path` — full path to the generated task-list.md

If spec-plan's output doesn't clearly state these paths, use:
```
Glob: "**/feature-notification*/task-list.md"
Glob: "**/feature-notification*/docs/task-list.md"
```

**If Step 1 fails:**
Stop the workflow immediately. Tell the user:
```
Step 1 (spec-plan) failed.
Nothing has been created yet.
Retry with: /spec-plan "Build a complete notification system with real-time WebSocket events, email digests, and in-app notification center"
```

---

## 5. PM-DB Import Handling (Step 4)

PM-DB import is the only step in the workflow that is explicitly **best-effort, non-blocking**.

The SKILL.md states: "This is helpful but not blocking — if it fails, warn and continue."

**Exact invocation (Step 4):**
```
Skill: pm-db
Args:  "import --project feature-notification-system --auto-confirm"
```

- `--project` is set to the `feature_name` extracted after Step 1 (the directory slug).
- `--auto-confirm` suppresses interactive prompts so the orchestrator can proceed without
  human intervention at this step.

**Success path:**
The pm-db skill returns project/phase/plan IDs. These are stored as `pm_db_ids` in the
orchestrator's state. They are noted for user reference but not required for Step 5.

**Failure path:**
Do NOT stop. Issue a warning to the user, then proceed directly to Step 5:
```
Warning: PM-DB import failed. Tracking will not be available for this feature.
You can import later with: /pm-db import --project feature-notification-system
Continuing to execution...
```

This is the **only step** where failure does not halt the workflow. All other steps (1, 2 pending
user choice, 3 pending user approval, 5) are treated as blocking failures.

---

## 6. Team Mode: Execution Skill Selection (Step 5)

The SKILL.md is explicit about which execution skill to call based on `mode`:

```
If mode is "team":
  Skill: start-phase-execute-team
  Args:  "{task_list_path}"

If mode is "sequential" or "auto":
  Skill: start-phase-execute
  Args:  "{task_list_path}"
```

Since `mode = "team"` (set during argument parsing), the orchestrator calls:

**Exact invocation:**
```
Skill: start-phase-execute-team
Args:  "./job-queue/feature-notification-system/docs/task-list.md"
```

Note: The `--team` flag is NOT appended here as a string argument. The mode decision is
made by the orchestrator choosing `start-phase-execute-team` over `start-phase-execute`.
The team skill itself handles all parallel execution, wave decomposition, multi-agent
delegation, quality gates, git commits, and PM-DB tracking hooks internally.

**Key distinction from `start-phase-execute`:**
`start-phase-execute-team` is designed for parallel agent execution. For a notification
system with decoupled concerns (WebSocket backend, email service, in-app UI), this means:
- Wave 1 (infrastructure): API WebSocket setup, database schema (parallel)
- Wave 2 (services): email digest worker, notification fanout logic (parallel)
- Wave 3 (frontend): in-app notification center UI (parallel, depends on API contract)
- Wave 4 (integration/QA): end-to-end tests, cross-app wiring (sequential gate)

**If Step 5 fails mid-execution:**
Tell the user which task failed, then provide recovery commands:
```
Step 5 (start-phase-execute-team) failed at task: [task name from output]
Completed before failure: [list from execution output]

Resume with:
  /feature-continue
  OR
  /start-phase execute ./job-queue/feature-notification-system/docs/task-list.md
```

---

## 7. State Threading Between Steps

The orchestrator tracks four variables across all five steps:

| Variable | Set After Step | Value (example for this feature) |
|---|---|---|
| `feature_name` | Step 1 | `feature-notification-system` |
| `spec_dir` | Step 1 | `./job-queue/feature-notification-system/docs/` |
| `task_list_path` | Step 1 | `./job-queue/feature-notification-system/docs/task-list.md` |
| `pm_db_ids` | Step 4 | `{ project: "proj_xxx", phase: "phase_yyy" }` or `null` |

**Threading rules:**

- `feature_name` → used in Step 4 as `--project feature-notification-system`
- `task_list_path` → used in Step 3 (`start-phase-plan` args) and Step 5 (`start-phase-execute-team` args)
- `spec_dir` → used in error messages (tell user where specs are saved) and the completion summary
- `pm_db_ids` → informational only; not passed to any subsequent skill as an argument

**If a path cannot be determined from sub-skill output:**

Use Glob to locate the artifact before proceeding:
```
Glob: "**/feature-*/task-list.md"
Glob: "**/feature-*/docs/task-list.md"
```

The orchestrator MUST resolve these paths before advancing. If it cannot resolve
`task_list_path` after Step 1, that is treated as a Step 1 failure.

---

## 8. Skill-Specific Recovery Commands

From the SKILL.md "Error Handling" recovery table, applied to this specific feature:

| Failed Step | Step Name | Recovery Command |
|---|---|---|
| Step 1 | spec-plan | `/spec-plan "Build a complete notification system with real-time WebSocket events, email digests, and in-app notification center"` |
| Step 2 | spec-review | `/spec-review` |
| Step 3 | start-phase-plan | `/start-phase plan ./job-queue/feature-notification-system/docs/task-list.md` |
| Step 4 | pm-db import | `/pm-db import --project feature-notification-system` (or skip — non-blocking) |
| Step 5 | start-phase-execute-team | `/feature-continue` OR `/start-phase execute ./job-queue/feature-notification-system/docs/task-list.md` |

**Step 2 special case:**
If spec-review finds errors (not just warnings), the recovery is NOT automatic. The
orchestrator presents an `AskUserQuestion`:
- "Continue anyway" → proceed to Step 3 (user accepts risk)
- "Stop and fix" → stop, tell user specs are at `./job-queue/feature-notification-system/docs/`

This means Step 2 failure does not necessarily terminate the workflow — the user decides.
Only a "Stop and fix" choice causes the workflow to halt at Step 2.

---

## Full Execution Flow Summary

```
Input: "...notification system... --team"
         |
         v
[PARSE] Strip "--team" → feature_description cleaned, mode = "team"
         |
         v
[PRE-FLIGHT] Glob for existing task-list.md and phase-summary.md
  → None found (fresh run) → No skip prompts
         |
         v
[STEP 1] spec-plan "...notification system... --team"  ← --team re-appended here only
  → Outputs: spec_dir, task_list_path, feature_name
  → Failure: STOP, give /spec-plan recovery command
         |
         v
[STEP 2] spec-review
  → Clean/warnings: CONTINUE
  → Errors: AskUserQuestion → user decides continue or stop
         |
         v
[STEP 3] start-phase-plan "./job-queue/feature-notification-system/docs/task-list.md"
  → Built-in user approval checkpoint (skill handles this)
  → User approves: CONTINUE
  → User rejects: STOP, give /start-phase plan recovery command
         |
         v
[STEP 4] pm-db "import --project feature-notification-system --auto-confirm"
  → Success: store pm_db_ids, continue
  → Failure: WARN only, continue  ← only non-blocking step
         |
         v
[STEP 5] start-phase-execute-team "./job-queue/feature-notification-system/docs/task-list.md"
         ^^^ "team" because mode = "team" → execute-TEAM, not execute
  → Failure mid-execution: STOP, give /feature-continue recovery command
         |
         v
[DONE] Completion summary:
  Feature: Build a complete notification system with real-time WebSocket events, email digests, and in-app notification center
  Specs: ./job-queue/feature-notification-system/docs/
  Tasks completed: (from execution output)

  Next:
    /pm-db dashboard    — view project metrics
    /memory-bank-sync   — update project memory
```
