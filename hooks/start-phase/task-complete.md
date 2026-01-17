---
name: start-phase-task-complete
trigger: on-task-complete
description: Automatically triggers quality gate after task completion
enabled: true
silent: false
filter:
  context: start-phase-execute
---

# Start-Phase: Task Complete Hook

Automatically triggers quality gate workflow after each task completes.

## Purpose

Bridges task execution to quality gate:
- Detects task completion
- Triggers quality gate hook
- Ensures no task skips quality checks
- Maintains execution flow

## Trigger

**Event:** `on-task-complete`
**Filter:** Only during `/start-phase execute` context
**When:** Immediately after task execution finishes

## Behavior

### Step 1: Detect Task Completion

When a task completes during Mode 2 execution:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Task Execution Complete
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Task: {task-name}
Agent: {agent-persona}
Duration: {duration}
Files changed: {count}

Triggering quality gate...
```

---

### Step 2: Extract Task Information

Parse task details from context:

```
Task Information:
• Name: setup-auth-api
• Phase: prototype-build
• Agent: nextjs-backend-developer
• Start time: 10:23:45
• End time: 10:52:12
• Duration: 28 minutes, 27 seconds

Files modified:
• src/api/auth.ts (new)
• src/types/user.ts (modified)
• tests/auth.test.ts (new)

Lines changed: +124 -5
```

---

### Step 3: Check for Mid-Task Checkpoints

If task duration > 30 minutes:

```
⏰ Long Task Detected (28 min)

Checking for checkpoint commits...
```

**Look for checkpoint commits:**
```bash
git log --grep="checkpoint: {task-name}" --since="30 minutes ago"
```

**If no checkpoints:**
```
⚠️ Recommendation: Long tasks should have checkpoint commits

For future tasks >30 min, create checkpoints:
git commit -m "checkpoint: {task-name} - {milestone}"

This is a recommendation only. Continuing to quality gate...
```

**If checkpoints found:**
```
✅ Checkpoint commits found: 2

• checkpoint: setup-auth-api - routes and types wired
• checkpoint: setup-auth-api - database integration complete

Good practice for long tasks!
```

---

### Step 4: Trigger Quality Gate

Automatically invoke quality-gate hook:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚦 Triggering Quality Gate
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Quality gate will:
1. Run lint checks
2. Run build checks
3. Perform code review
4. Validate task completion
5. Create git commit

Please wait...
```

**Invoke:**
```
→ Execute quality-gate.md hook
```

(Quality gate hook takes over from here)

---

### Step 5: Monitor Quality Gate Results

Wait for quality gate to complete:

```
🚦 Quality Gate Running...

[Progress shown by quality-gate hook]

• Lint: Running...
• Build: Waiting...
• Review: Waiting...
```

---

### Step 6: Handle Quality Gate Results

#### If Quality Gate Passes ✅

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Task Complete & Quality Gate PASSED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Task: {task-name}
Status: ✅ COMPLETE & VERIFIED

Quality checks:
✅ Lint passed
✅ Build passed
✅ Code review: APPROVED
✅ Commit created: abc1234

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Ready for next task.
```

→ Allow next task to begin

---

#### If Quality Gate Fails ❌

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
❌ Task Complete BUT Quality Gate FAILED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Task: {task-name}
Status: ⚠️ NEEDS FIXES

Failed checks:
❌ Lint: 3 errors
❌ Build: 1 error

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⛔ BLOCKED: Cannot proceed to next task

Quality gate must pass before continuing.

Options:
1. Let me fix the errors
2. Review specific errors
3. I'll fix them manually
```

→ Block next task until fixed

---

### Step 7: Update Phase Progress

After successful quality gate, update phase tracking:

```
Phase Progress Update:

Total tasks: 8
Completed: 3 ✅
In progress: 0
Pending: 5

Current completion: 37.5%
```

---

### Step 8: Next Task Preview

If more tasks remain:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 Next Task Ready
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Next: Task 4 - Create UI components
Agent: ui-developer
Depends on: Task 1 ✅, Task 2 ✅
Estimated: 45 minutes

Ready to start? (y/n)
```

---

If no more tasks:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎉 All Tasks Complete!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Phase: {phase_name}
Total tasks: 8
All completed: ✅

Proceeding to final phase review...
```

→ Trigger phase-complete hook

---

## Task Completion Checklist

Before triggering quality gate, verify:

1. ✅ Task execution finished
2. ✅ Changes made to codebase
3. ✅ In start-phase execute context
4. ✅ Task not already processed

**Only then** trigger quality gate.

---

## Error Handling

### If Quality Gate Hook Not Found

```
⚠️ Quality Gate Hook Not Available

The quality-gate.md hook is not found or disabled.

Falling back to manual quality checks:
1. Run: npm run lint
2. Run: npm run build
3. Perform manual code review
4. Create task update file
5. Create git commit

Proceed with manual checks? (y/n)
```

---

### If Context Lost

```
⚠️ Task Context Lost

Cannot determine which task just completed.

Please manually specify:
Task name: _____
```

---

### If Multiple Tasks Complete Simultaneously

```
⚠️ Multiple Tasks Completed

Detected parallel task completion:
• Task 2: Create UI components
• Task 3: Write tests

Running quality gates sequentially:
1. Processing Task 2...
2. Processing Task 3...
```

---

## Integration with Mode 2 Workflow

This hook fits into the execution flow:

```
Mode 2: Execute
  ↓
Part 3: Execute task
  ↓
[Task execution completes]
  ↓
Task-Complete Hook ⭐ (THIS HOOK)
  ↓
Quality-Gate Hook
  ↓
Part 4: Task update + commit
  ↓
Next task OR Phase complete
```

---

## Configuration

### Enable/Disable Hook

```yaml
# In frontmatter
enabled: true     # Set to false to disable automatic gate
silent: false     # Set to true for quiet operation
```

### Customization

```json
{
  "task_complete": {
    "auto_trigger_gate": true,
    "checkpoint_warning": true,
    "next_task_preview": true,
    "progress_tracking": true
  }
}
```

---

## Performance

- **Detection:** < 1 second
- **Context extraction:** < 1 second
- **Checkpoint check:** < 2 seconds
- **Hook invocation:** Immediate
- **Total overhead:** ~3 seconds before quality gate

Quality gate itself takes 1-2 minutes.

---

## Benefits

### Automation

✅ **No manual trigger** - Quality gate runs automatically
✅ **No forgotten checks** - Every task goes through gate
✅ **Consistent flow** - Same process every time

### Safety

✅ **Mandatory checks** - Cannot skip quality gate
✅ **Blocked on fail** - Next task waits for fixes
✅ **Clear status** - Always know task state

### Progress Tracking

✅ **Phase progress** - Updated after each task
✅ **Next task preview** - Know what's coming
✅ **Completion detection** - Triggers phase-complete when done

---

## Example Flow

```bash
# During Mode 2 execution
Task 3: Setup authentication API
→ Implement routes, types, validation
→ Task execution completes

# Task-complete hook triggers
✅ Task Execution Complete

→ Extract task info
→ Check for checkpoints
→ Trigger quality gate hook

# Quality gate runs
🚦 Quality Gate Activated
→ Lint: ✅ PASSED
→ Build: ✅ PASSED
→ Review: ✅ APPROVED
→ Commit: ✅ CREATED

# Task marked complete
✅ Task Complete & Quality Gate PASSED

# Phase progress updated
Progress: 3/8 tasks (37.5%)

# Next task ready
📋 Next Task: Create UI components
Ready to start? (y)

# Continue execution...
```

---

## Troubleshooting

### Quality gate not triggering

- Check hook enabled: `enabled: true`
- Verify context: Must be in `/start-phase execute`
- Check filter: Context must match

### Multiple quality gates running

- Ensure only one task-complete event fires
- Check for duplicate hooks
- Verify hook priority settings

### Task skipped quality gate

- Check hook execution logs
- Verify trigger conditions met
- Manually run: `/quality-gate {task-name}`

---

**This hook ensures no task escapes quality validation.**

See `hooks/start-phase/quality-gate.md` for quality gate details.
See `skills/start-phase/README.md` for complete documentation.
