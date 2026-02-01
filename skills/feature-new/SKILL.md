---
name: feature-new
description: Complete feature workflow - from planning to execution with PM-DB tracking
args:
  feature_description:
    type: string
    description: Brief description of the feature to develop
    required: true
---

# Feature New - Complete Workflow Orchestration

Execute the complete end-to-end feature development workflow with automatic PM-DB tracking.

## Your Task

You are orchestrating a complete feature development workflow. Follow these steps in order, handling errors and user approvals as specified.

---

## Step 1: Initialize Documentation Systems (if needed)

First, check if Memory Bank and Document Hub are initialized by reading the memory-bank directory.

```bash
Use Read tool to check: memory-bank/systemPatterns.md
```

**If the file doesn't exist:**
- Use the Skill tool to invoke "documentation-start"
- Wait for completion
- Display: "✅ Step 1/6: Documentation initialized"

**If the file exists:**
- Display: "✅ Step 1/6: Documentation already initialized"

**If initialization fails:**
- Display error and STOP the workflow
- Show: "❌ Failed at Step 1/6: Could not initialize documentation systems"

---

## Step 2: Generate Feature Specification

Use the Skill tool to invoke "spec-plan" with the feature_description argument:

```
Skill tool:
  skill: "spec-plan"
  args: "{{feature_description}}"
```

**What to expect:**
- The spec-plan skill will:
  1. Research and gather context
  2. Launch spec-writer agent
  3. Generate FRD, FRS, GS, TR, and task-list.md files
  4. Save to: `./job-queue/feature-{name}/docs/`

**After it completes:**
- Display: "✅ Step 2/6: Specification created"
- Show the location: `./job-queue/feature-{name}/docs/`

**If it fails:**
- Display: "❌ Failed at Step 2/6: Spec planning failed"
- Show which steps were completed vs skipped
- STOP the workflow

---

## Step 3: Review Specification Quality

Use the Skill tool to invoke "spec-review":

```
Skill tool:
  skill: "spec-review"
```

**What to expect:**
- The spec-review skill will validate the generated specs
- It may find issues or pass cleanly

**After it completes:**
- Display: "✅ Step 3/6: Specification reviewed"
- If there were warnings, show them to the user

**If validation fails:**
- Ask the user: "⚠️ Spec review found issues. Continue anyway?"
- Use AskUserQuestion with options:
  - "Yes, continue" (proceed to Step 4)
  - "No, stop here" (STOP the workflow)

**If user chooses to stop:**
- Display: "ℹ️ Workflow stopped at user request"
- Show: "Specification saved at: ./job-queue/feature-{name}/"
- STOP the workflow

---

## Step 4: Create Strategic Execution Plan

Find the task-list.md file from the spec generation:

```bash
Use Glob tool: "**/feature-*/task-list.md"
```

Then use the Skill tool to invoke "start-phase-plan" with the task list path:

```
Skill tool:
  skill: "start-phase-plan"
  args: "{path_to_task_list}"
```

**What to expect:**
- The start-phase-plan skill will:
  1. Analyze task complexity
  2. Identify parallel execution opportunities
  3. Create wave structure
  4. Generate phase plan
  5. **ASK USER FOR APPROVAL** (built into start-phase-plan)

**After user approves:**
- Display: "✅ Step 4/6: Strategic plan approved"

**If user rejects the plan:**
- Display: "ℹ️ Plan rejected by user"
- Show: "Specification saved at: ./job-queue/feature-{name}/"
- Show: "You can re-plan later with: /start-phase plan {path}"
- STOP the workflow

---

## Step 5: Import to PM-DB

Use the Skill tool to invoke "pm-db" with import command:

```
Skill tool:
  skill: "pm-db"
  args: "import --project feature-{name}"
```

**What to expect:**
- Creates project record in PM-DB
- Creates phase record
- Creates phase_plan record
- Links all tasks to the plan
- Returns project ID, phase ID, plan ID

**After it completes:**
- Display: "✅ Step 5/6: Imported to PM-DB"
- Show the IDs returned
- Show task count

**If import fails:**
- Display: "⚠️ PM-DB import failed"
- Show manual import instructions
- Ask user: "Continue to execution anyway?"
  - If no: STOP
  - If yes: proceed to Step 6 (with warning)

---

## Step 6: Execute Phase with Quality Gates

Use the Skill tool to invoke "start-phase-execute" with the task list path:

```
Skill tool:
  skill: "start-phase-execute"
  args: "{path_to_task_list}"
```

**What to expect:**
- The start-phase-execute skill will:
  1. Call on-phase-run-start hook (gets phase_run_id)
  2. Execute Part 1-5 of the execution workflow
  3. For each task:
     - Call on-task-run-start hook
     - Execute task with appropriate agent
     - Call on-task-run-complete hook
     - Run quality gates
     - Create task update
     - Git commit
  4. Call on-phase-run-complete hook
  5. Display execution metrics

**After it completes:**
- Display: "✅ Step 6/6: Phase execution complete"
- Show final metrics
- Show completion message

**If execution fails:**
- Display which task failed
- Show: "Use /feature-continue to resume"

---

## Final Output

When all steps complete successfully, display:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎉 FEATURE COMPLETE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Feature: {{feature_description}}
Location: ./job-queue/feature-{name}/

Completed Steps:
  ✅ [1/6] Documentation initialized
  ✅ [2/6] Specification created
  ✅ [3/6] Specification reviewed
  ✅ [4/6] Strategic plan approved
  ✅ [5/6] Imported to PM-DB
  ✅ [6/6] Phase executed

Next steps:
  - View metrics: /pm-db dashboard
  - Update Memory Bank: /memory-bank-sync
  - View phase summary: ./job-queue/feature-{name}/planning/phase-structure/phase-summary.md

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Error Handling Guidelines

**At any step failure:**
1. Display which step failed with [X/6] notation
2. List which steps were completed (✓)
3. List which steps were skipped (⏭)
4. Provide recovery instructions
5. STOP the workflow (don't continue to next step)

**Example error output:**
```
❌ Workflow Failed at Step 3/6: Spec Review

Steps completed:
  ✓ [1/6] Documentation initialized
  ✓ [2/6] Specification created
  ✗ [3/6] Specification review FAILED

Steps skipped:
  ⏭ [4/6] Strategic plan
  ⏭ [5/6] PM-DB import
  ⏭ [6/6] Phase execution

Error: Validation found critical issues in FRD.md

Recovery options:
  1. Fix issues manually and run: /spec-review
  2. Regenerate spec: /spec-plan "{{feature_description}}"
  3. Resume with: /feature-continue
```

---

## Human-in-the-Loop Checkpoints

This workflow has **2 required approval steps** (handled by the sub-skills):

1. **After spec review** (Step 3): If validation fails, ask user to continue or stop
2. **After phase plan** (Step 4): User must approve the execution plan (built into start-phase-plan)

These checkpoints prevent:
- Executing poorly-defined specifications
- Running inefficient task plans
- Wasting tokens on flawed approaches

---

## Notes for Execution

- **Sequential execution**: Each step must complete before starting the next
- **Use Skill tool**: All sub-skills must be invoked using the Skill tool, not mentioned as text
- **Wait for completion**: Don't proceed to next step until current step finishes
- **Check exit codes**: If a sub-skill fails, handle the error and stop
- **Display progress**: Show step numbers [X/6] throughout
- **Path management**: Track the feature folder path for use in later steps
- **Error recovery**: Provide clear instructions for manual recovery if needed

---

## Total Expected Duration

- Step 1: ~1 min (or skip if exists)
- Step 2: ~3-5 min (AI generation)
- Step 3: ~1-2 min (validation)
- Step 4: ~2-4 min (planning + user approval)
- Step 5: ~5 sec (database import)
- Step 6: ~varies (depends on task complexity)

**Planning phase (Steps 1-5):** ~6-12 minutes
**Execution phase (Step 6):** Varies by feature scope
