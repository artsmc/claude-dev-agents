---
name: feature-new
description: Complete feature workflow - from planning to execution with PM-DB tracking
args:
  feature_description:
    type: string
    description: Brief description of the feature to develop
    required: true
---

# feature-new Skill

Complete end-to-end feature development workflow with automatic PM-DB tracking.

## Usage

```bash
/feature-new "add user authentication"
/feature-new "implement payment processing"
/feature-new "build admin dashboard"
```

## What It Does

Orchestrates the complete feature development workflow:

1. **Initialize Documentation** (if needed)
2. **Create Feature Specification**
3. **Review Specification**
4. **Create Phase Plan**
5. **Import to PM-DB**
6. **Execute Phase with Quality Gates**

## Complete Workflow

### Part 1: Documentation Initialization

```
🔄 Step 1/6: Initialize documentation systems...

Calling /documentation-start...
```

Ensures Memory Bank and Document Hub are initialized.

---

### Part 2: Feature Specification

```
🔄 Step 2/6: Create feature specification...

Calling /spec-plan with:
  Feature: {feature_description}
```

**What happens:**
- Launches spec-writer agent
- Generates complete specification:
  - FRD.md (Feature Requirements Document)
  - FRS.md (Functional Requirements Specification)
  - GS.md (Gherkin Scenarios)
  - TR.md (Technical Requirements)
  - task-list.md (Development tasks)
- Outputs to: `./job-queue/feature-{name}/docs/`

---

### Part 3: Specification Review

```
🔄 Step 3/6: Review specification...

Calling /spec-review...
```

**What happens:**
- Validates all specification files
- Runs critique_plan.py
- Presents findings to user
- **Waits for user approval:**
  - ✅ Approve → Proceed to planning
  - 🔄 Request changes → Iterate specification
  - ❌ Reject → Stop workflow

**IMPORTANT: This is a human-in-the-loop checkpoint.**

User must explicitly approve before proceeding.

---

### Part 4: Phase Planning

```
🔄 Step 4/6: Create strategic plan...

Calling /start-phase plan ./job-queue/feature-{name}/tasks.md...
```

**What happens:**
- Analyzes task complexity
- Identifies parallelism opportunities
- Proposes wave structure
- **Waits for user approval:**
  - ✅ Approve → Proceed to import
  - 🔄 Revise → Suggest changes
  - ❌ Reject → Stop workflow

**IMPORTANT: Another human-in-the-loop checkpoint.**

---

### Part 5: Import to PM-DB

```
🔄 Step 5/6: Import to project database...

Calling /pm-db import --project {feature-name}...
```

**What happens:**
- Imports specification to PM-DB
- Creates project record
- Creates phase record
- Creates phase_plan record
- Links tasks to plan

**Output:**
```
✅ Imported to PM-DB
   Project ID: 12
   Phase ID: 34
   Plan ID: 56
   Tasks: 7
```

---

### Part 6: Execute Phase

```
🔄 Step 6/6: Execute phase with quality gates...

Calling /start-phase execute ./job-queue/feature-{name}/tasks.md...
```

**What happens:**
- Calls on-phase-run-start hook (gets phase_run_id)
- Executes Part 1-5 of start-phase-execute
- For each task:
  - Calls on-task-run-start hook
  - Executes task with agent
  - Calls on-task-run-complete hook
  - Runs quality gates
  - Calls on-quality-gate hook
  - Creates task update
  - Git commits
- Calls on-phase-run-complete hook
- Displays metrics

---

## Complete Output Example

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚀 Starting Feature Development Workflow
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Feature: add user authentication

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔄 Step 1/6: Initialize documentation systems...
✅ Memory Bank: Ready
✅ Document Hub: Ready

🔄 Step 2/6: Create feature specification...
✅ Specification created
   Location: ./job-queue/feature-auth/docs/
   Files: FRD.md, FRS.md, GS.md, TR.md, task-list.md

🔄 Step 3/6: Review specification...
✅ Validation passed
✅ Critique completed

⏸️ WAITING FOR USER APPROVAL

   Options:
   1. Approve → Proceed to planning
   2. Request changes → Iterate spec
   3. Reject → Stop workflow

[User selects: Approve]

✅ Specification approved

🔄 Step 4/6: Create strategic plan...
✅ Strategic plan created
   Waves: 3
   Parallel tasks: 4
   Sequential tasks: 3

⏸️ WAITING FOR USER APPROVAL

[User selects: Approve]

✅ Plan approved

🔄 Step 5/6: Import to project database...
✅ Imported to PM-DB
   Project ID: 12
   Phase ID: 34
   Plan ID: 56
   Tasks: 7

🔄 Step 6/6: Execute phase with quality gates...
✅ Phase run started (ID: 78)

   Executing tasks...
   [1/7] ████████░░░░░░░░░░░░ Task 1 complete ✅
   [2/7] ████████████░░░░░░░░ Task 2 complete ✅
   [3/7] ████████████████░░░░ Task 3 complete ✅
   ...
   [7/7] ████████████████████ Task 7 complete ✅

✅ Phase run completed (ID: 78)

📊 Phase Metrics:
   Total runs: 1
   Successful: 1
   Failed: 0
   Duration: 45.2 minutes
   Tasks: 7/7 complete

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎉 FEATURE COMPLETE: add user authentication
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Next steps:
  - View metrics: /pm-db dashboard
  - Update Memory Bank: /memory-bank-sync
  - View phase summary: ./job-queue/feature-auth/planning/phase-structure/phase-summary.md
```

---

## Human-in-the-Loop Checkpoints

This workflow has **2 required approval steps**:

1. **After spec review**: User must approve specification
2. **After phase plan**: User must approve execution plan

These checkpoints prevent:
- Executing poorly-defined specifications
- Running inefficient task plans
- Wasting tokens on flawed approaches

---

## Error Handling

If any step fails, the workflow stops and reports:

```
❌ Step {n}/6 failed: {error}

Workflow stopped. You can:
  1. Fix the issue manually
  2. Resume with /feature-continue
  3. Start over with /feature-new
```

---

## When to Use

- **Starting a new feature**: Always use this
- **First time workflow**: Great for learning the process
- **Automated pipeline**: Reduces manual orchestration

---

## When NOT to Use

- **Resuming interrupted work**: Use `/feature-continue` instead
- **Skipping specification**: Use individual skills
- **Custom workflow**: Use skills directly

---

## Implementation Details

This skill uses the Skill tool to invoke:
1. `/documentation-start`
2. `/spec-plan {feature_description}`
3. `/spec-review`
4. `/start-phase plan {task_list_path}`
5. `/pm-db import`
6. `/start-phase execute {task_list_path}`

Waits for user approval at checkpoints 3 and 4.

---

## Path Management

All artifacts stored in:
```
./job-queue/feature-{name}/
├── docs/
│   ├── FRD.md
│   ├── FRS.md
│   ├── GS.md
│   ├── TR.md
│   └── task-list.md
└── planning/
    ├── agent-delegation/
    ├── phase-structure/
    ├── task-updates/
    └── code-reviews/
```

---

## PM-DB Tracking

This workflow creates complete PM-DB records:
- **Project record**: Top-level project
- **Phase record**: Feature phase
- **Phase plan record**: Approved plan
- **Phase run record**: Execution tracking
- **Task run records**: Per-task execution
- **Quality gate records**: QA results
- **Code review records**: Review summaries

All linked together for complete traceability.
