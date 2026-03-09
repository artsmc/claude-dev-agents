---
name: feature-new
description: "Complete feature workflow - from planning to execution with PM-DB tracking. Use this skill when the user wants to build a new feature end-to-end, saying things like 'build this feature', 'implement this', 'new feature', 'add this capability', or '/feature-new'. Orchestrates spec-plan → spec-review → start-phase-plan → pm-db → start-phase-execute into one workflow with human checkpoints. Even if the user doesn't explicitly mention this skill, use it whenever someone describes a new feature they want built from scratch."
args:
  feature_description:
    type: string
    description: Brief description of the feature to develop
    required: true
  mode:
    type: string
    description: "Execution mode: auto (default), team, sequential. Team mode passes --team to sub-skills for parallel execution. Auto lets each sub-skill decide."
    required: false
    default: "auto"
---

# Feature New — End-to-End Feature Orchestration

Chain five skills into one workflow: **spec → review → plan → track → execute**.

## Purpose

Building a feature from scratch involves multiple skills in sequence, with state (file paths, project names) threading between them. This orchestrator handles sequencing, state-passing, and error recovery so you focus on the feature itself.

Each sub-skill handles its own output, user interaction, and formatting. This skill only manages the flow between them.

## Flow

```
spec-plan → spec-review → start-phase-plan → pm-db import → execute
    |            |              |                  |             |
 generates    validates     user approves     best-effort    builds it
 spec docs    quality       execution plan    tracking
```

**Human checkpoints:** after spec-review (if issues), after phase-plan (always).

## Argument Parsing

The user may pass flags inline in the description string (e.g., `"add auth --team"`). Before doing anything:

1. **Scan `feature_description` for `--team` or `--sequential`** flags
2. If found, **strip the flag** from the description and set `mode` accordingly
3. Pass the **cleaned description** (without flags) to sub-skills
4. Re-append `--team` to spec-plan args only if mode is "team" (spec-plan expects it as a flag)

Example: `"add auth --team"` → `feature_description = "add auth"`, `mode = "team"`

## State Tracking

Track these values across steps — each is derived from the previous step's output:

- **feature_name** — directory name created by spec-plan (e.g., `feature-dark-mode`)
- **spec_dir** — where spec-plan saved files (e.g., `./job-queue/feature-dark-mode/docs/`)
- **task_list_path** — path to the generated task-list.md
- **pm_db_ids** — project/phase/plan IDs from pm-db (may be null if import was skipped)

If a path isn't clear from sub-skill output, use Glob:
```
Glob: "**/feature-*/task-list.md" or "**/feature-*/docs/task-list.md"
```

---

## Step 1: Generate Feature Specification

Invoke spec-plan. It auto-detects tier (quick/standard/full) and generates the right documentation depth.

```
Skill: spec-plan
Args: "{{feature_description}}"
      (append " --team" if mode is "team")
```

After completion, extract the **spec_dir** and **task_list_path** from spec-plan's output. These are needed for all remaining steps.

**If it fails:** Stop. Tell the user what went wrong and that they can retry directly with `/spec-plan "{{feature_description}}"`.

---

## Step 2: Review Specification Quality

Invoke spec-review to validate the generated specs. This catches structural issues before you commit to planning and execution.

```
Skill: spec-review
```

- **Clean pass or warnings only:** Continue.
- **Errors found:** Ask the user via AskUserQuestion:
  - "Continue anyway" → proceed to Step 3
  - "Stop and fix" → stop workflow, tell user specs are saved at spec_dir

This step prevents executing a flawed spec. It's a safety net, not a gate — the user decides whether issues are blocking.

---

## Step 3: Create Execution Plan

Invoke start-phase-plan with the task list from Step 1.

```
Skill: start-phase-plan
Args: "{task_list_path}"
```

start-phase-plan has a **built-in user approval checkpoint**. It analyzes dependencies, proposes wave structure and agent assignments, then asks the user to approve.

- **User approves:** Continue.
- **User rejects:** Stop. Tell them specs are saved and they can re-plan with `/start-phase plan {task_list_path}`.

---

## Step 4: Import to PM-DB (best-effort)

Import the feature into PM-DB for tracking. This is helpful but **not blocking** — if it fails, warn and continue.

```
Skill: pm-db
Args: "import --project {feature_name} --auto-confirm"
```

- **Success:** Note the returned IDs for reference.
- **Failure:** Warn the user, then proceed to Step 5. They can import later with `/pm-db import`.

---

## Step 5: Execute Tasks

Choose the execution skill based on mode:

**If mode is "team":**
```
Skill: start-phase-execute-team
Args: "{task_list_path}"
```

**If mode is "sequential" or "auto":**
```
Skill: start-phase-execute
Args: "{task_list_path}"
```

The execution skill handles everything: wave decomposition, agent delegation, quality gates, git commits, and PM-DB tracking hooks.

**If it fails mid-execution:** Tell the user which task failed and that they can resume with `/feature-continue` or `/start-phase execute {task_list_path}`.

---

## Completion

When all steps finish, show a brief summary:

```
Feature: {feature_description}
Specs: {spec_dir}
Tasks completed: (from execution output)

Next:
  /pm-db dashboard    — view project metrics
  /memory-bank-sync   — update project memory
```

Keep it short. The sub-skills already showed detailed output during their runs.

---

## Error Handling

**Principle: fail fast, explain clearly, give a recovery command.**

At any failure (except Step 4 which is best-effort):
1. Name the failed step
2. List what completed before it
3. Give the exact command to retry or resume

**Recovery commands by step:**

| Failed Step | Recovery Command |
|-------------|-----------------|
| Step 1 | `/spec-plan "{{feature_description}}"` |
| Step 2 | `/spec-review` |
| Step 3 | `/start-phase plan {task_list_path}` |
| Step 4 | `/pm-db import --project {feature_name}` (or skip) |
| Step 5 | `/feature-continue` or `/start-phase execute {task_list_path}` |

---

## Skip Logic

Before starting Step 1, run Glob to check for existing artifacts. If found, confirm with the user before skipping.

**Pre-flight checks:**

1. **Check for task-list.md:**
   ```
   Glob: "**/feature-*/task-list.md" or "**/feature-*/docs/task-list.md"
   ```
   If found → specs exist. Check if user also said they reviewed them.

2. **Check for phase-summary.md:**
   ```
   Glob: "**/feature-*/planning/phase-structure/phase-summary.md"
   ```
   If found → planning already done.

**Confirmation is mandatory before skipping.** Even if the user's message clearly implies steps are done, present what you found and ask:

```
AskUserQuestion:
  "I found existing specs at: {path}
   Skip spec generation and review, and go straight to planning?"
  Options: "Yes, skip to planning" / "No, regenerate from scratch"
```

This prevents silently skipping safety steps (especially spec-review) without the user's explicit awareness.

**Skip matrix:**

| Found | User said reviewed | Skip Steps |
|-------|-------------------|------------|
| task-list.md | Yes | 1 + 2 |
| task-list.md | No | 1 only (still run review) |
| phase-summary.md | N/A | 3 |
| PM-DB has feature | N/A | 4 |

---

## Notes

- Each sub-skill manages its own output — don't duplicate their displays
- The workflow is sequential because each step depends on the previous one
- Mode "auto" defers to each sub-skill's own auto-detection (spec-plan picks tier, execute picks parallelism)
- Mode "team" passes team flags through to sub-skills that support them
