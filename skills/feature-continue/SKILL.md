---
name: feature-continue
description: Resume interrupted feature work from task-list.md with PM-DB tracking
args:
  task_list_path:
    type: string
    description: Path to task-list.md file
    required: true
---

# feature-continue Skill

Resume interrupted feature development with PM-DB tracking intact.

## Usage

```bash
/feature-continue ./job-queue/feature-auth/tasks.md
/feature-continue ./my-feature/tasks.md
```

## What It Does

Intelligently resumes feature work by:
1. Detecting where you left off
2. Checking PM-DB for existing phase_run
3. Resuming execution from the last incomplete task
4. Maintaining PM-DB tracking continuity

## Workflow

### Step 1: Detect Feature Location

```
🔍 Analyzing feature location...

Task list: ./job-queue/feature-auth/tasks.md
Input folder: ./job-queue/feature-auth
Planning folder: ./job-queue/feature-auth/planning
```

---

### Step 2: Check PM-DB Status

```
🔍 Checking PM-DB tracking...

Query: SELECT * FROM phase_runs WHERE plan_id = (
  SELECT id FROM phase_plans WHERE phase_id = (
    SELECT id FROM phases WHERE name = 'feature-auth'
  )
) ORDER BY created_at DESC LIMIT 1;
```

**Possible outcomes:**

**A) Active phase_run found:**
```
✅ Found active phase run
   Phase Run ID: 78
   Phase ID: 34
   Plan ID: 56
   Status: in_progress
   Started: 2026-01-30 14:23:15

   Resuming from phase run #78...
```

**B) Completed phase_run found:**
```
⚠️ Found completed phase run
   Phase Run ID: 78
   Status: completed
   Completed: 2026-01-30 16:45:32

   This phase is already complete.

   Options:
   1. View metrics: /pm-db dashboard
   2. Start new run: /start-phase execute {path}
   3. Cancel
```

**C) No phase_run found:**
```
⚠️ No PM-DB tracking found

   This feature hasn't been started with PM-DB tracking.

   Options:
   1. Import to PM-DB: /pm-db import
   2. Start fresh: /feature-new "{description}"
   3. Execute without PM-DB: /start-phase execute {path}
```

---

### Step 3: Detect Last Completed Task

```
🔍 Detecting progress...

Query: SELECT task_key FROM task_runs WHERE phase_run_id = 78 AND exit_code = 0;
```

**Output:**
```
✅ Found completed tasks:
   [1/7] Task 1: Setup auth routes ✅
   [2/7] Task 2: Create user model ✅
   [3/7] Task 3: Implement JWT ✅
   [4/7] Task 4: Add login endpoint ⏸️ (incomplete)
   [5/7] Task 5: Add logout endpoint ⏹️ (not started)
   [6/7] Task 6: Add protected routes ⏹️ (not started)
   [7/7] Task 7: Write tests ⏹️ (not started)

Last completed: Task 3
Next task: Task 4
```

---

### Step 4: Resume Execution

```
🚀 Resuming phase execution...

Phase Run ID: 78
Starting from: Task 4
Remaining tasks: 4

Calling /start-phase execute with:
  - Path: ./job-queue/feature-auth/tasks.md
  - PM_DB_PHASE_RUN_ID: 78
  - Resume from: Task 4
```

**Key behaviors:**
- **Reuses existing phase_run_id** (doesn't create new one)
- **Skips completed tasks** (doesn't re-execute)
- **Continues quality gates** (same standards)
- **Maintains git history** (continues commit sequence)
- **Updates same PM-DB records** (complete traceability)

---

### Step 5: Execution Continues

```
Executing remaining tasks...

[4/7] ████████████████░░░░ Task 4 complete ✅
[5/7] ████████████████████ Task 5 complete ✅
[6/7] ████████████████████ Task 6 complete ✅
[7/7] ████████████████████ Task 7 complete ✅

✅ Phase run completed (ID: 78)

📊 Updated Phase Metrics:
   Total runs: 1
   Duration: 72.4 minutes (resumed after 27.2 min)
   Tasks: 7/7 complete
```

---

## PM-DB Integration

### Existing Phase Run

If phase_run exists, resume uses:
```python
# Get existing phase_run
run = db.get_phase_run(phase_run_id)

# Don't create new phase_run!
# Reuse existing: PM_DB_PHASE_RUN_ID = run['id']

# For each remaining task:
task_run_id = db.create_task_run(
    phase_run_id=run['id'],  # Same phase_run!
    task_id=task['id'],
    assigned_agent=agent
)

# On completion:
db.complete_phase_run(run['id'], exit_code, summary)
```

### No Phase Run

If no phase_run, create one:
```python
# Import to PM-DB first
/pm-db import

# Then start new phase_run
hook_output=$(cat <<EOF | python3 ~/.claude/hooks/pm-db/on-phase-run-start.py
{
  "phase_name": "feature-auth",
  "project_name": "my-project",
  "assigned_agent": "start-phase-execute"
}
EOF
)

phase_run_id=$(echo "$hook_output" | jq -r '.phase_run_id')
```

---

## Progress Detection Logic

```python
def detect_progress(phase_run_id):
    """Detect which tasks are complete"""

    # Get all task_runs for this phase_run
    task_runs = db.list_task_runs(phase_run_id)

    completed_tasks = [
        tr for tr in task_runs
        if tr['exit_code'] == 0 and tr['completed_at'] is not None
    ]

    # Get all tasks from plan
    run = db.get_phase_run(phase_run_id)
    all_tasks = db.list_tasks(run['plan_id'])

    # Find first incomplete task
    completed_keys = {tr['task_key'] for tr in completed_tasks}

    for task in all_tasks:
        if task['task_key'] not in completed_keys:
            return {
                'next_task': task,
                'completed_count': len(completed_keys),
                'total_count': len(all_tasks),
                'completed_tasks': completed_keys
            }

    return {'next_task': None}  # All complete
```

---

## Use Cases

### Scenario 1: Session Dropped Mid-Execution

```bash
# Session 1 (interrupted at Task 4):
/feature-new "add auth"
# ... completes Tasks 1-3, then session drops

# Session 2 (resume):
/feature-continue ./job-queue/feature-auth/tasks.md
# ✅ Resumes from Task 4, PM-DB tracking intact
```

---

### Scenario 2: Intentional Pause

```bash
# Day 1: Start feature
/feature-new "payment processing"
# ... completes Tasks 1-5

# Day 2: Resume
/feature-continue ./job-queue/feature-payment/tasks.md
# ✅ Continues from Task 6
```

---

### Scenario 3: Multiple Attempts

```bash
# Attempt 1: Failed at Task 3 (quality gate failure)
/feature-new "admin dashboard"
# ... Tasks 1-2 pass, Task 3 fails quality gate

# Attempt 2: Fix and resume
# (manually fix issues)
/feature-continue ./job-queue/feature-admin/tasks.md
# ✅ Re-runs Task 3 (failed), then continues to Task 4-7
```

---

## Error Handling

### No task-list.md Found

```
❌ Error: task-list.md not found

Path: ./job-queue/feature-auth/tasks.md

Options:
  1. Check path is correct
  2. Run /feature-new to create feature
  3. Create task-list.md manually
```

---

### No Planning Folder

```
⚠️ Warning: No planning folder found

Expected: ./job-queue/feature-auth/planning/

This suggests the feature hasn't been executed yet.

Options:
  1. Run /start-phase plan first
  2. Run /feature-new for complete workflow
  3. Run /start-phase execute to start fresh
```

---

### Completed Phase

```
✅ Phase already complete

Phase Run ID: 78
Completed: 2026-01-30 16:45:32
All tasks: 7/7 complete ✅

Nothing to resume.

View results:
  - Dashboard: /pm-db dashboard
  - Summary: ./job-queue/feature-auth/planning/phase-structure/phase-summary.md
```

---

## Implementation Details

This skill:
1. Reads task-list.md to derive paths
2. Queries PM-DB for existing phase_run
3. Checks task_runs table for completed tasks
4. Passes resume context to /start-phase execute:
   - PM_DB_PHASE_RUN_ID (existing)
   - Skip tasks (list of completed task_keys)
   - Resume from (next task_key)

The /start-phase execute skill handles:
- Skipping completed tasks
- Reusing phase_run_id
- Creating task_runs for remaining tasks
- Completing the phase_run

---

## Benefits

✅ **Session resilience**: Resume after crashes/disconnects
✅ **PM-DB continuity**: Single phase_run tracks complete lifecycle
✅ **No duplicate work**: Skips completed tasks
✅ **Git history preservation**: Continues commit sequence
✅ **Metrics accuracy**: Duration includes all attempts
✅ **Quality gate consistency**: Same standards throughout

---

## Limitations

- Requires PM-DB import before first use
- Only resumes from last completed task (not mid-task)
- Doesn't handle merged branches (may re-run tasks)
- Assumes task-list.md hasn't changed significantly
