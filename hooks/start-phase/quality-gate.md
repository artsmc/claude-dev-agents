---
name: start-phase-quality-gate
trigger: on-task-complete
description: Mandatory quality gate between tasks - enforces lint/build/review before proceeding
enabled: true
silent: false
priority: high
filter:
  context: start-phase
---

# Start-Phase Quality Gate Hook

Mandatory quality enforcement between tasks. **No next task until this gate passes.**

## Purpose

Implements the **Part 3.5 Quality Gate** from Mode 2:
- Run lint + build (must pass)
- Require code review (per task)
- Validate task completion
- Create checkpoint commits
- Block next task if gate fails

## Trigger

**Event:** `on-task-complete`
**Filter:** Only during `/start-phase` context
**When:** After EVERY task completes, before next task starts

## Behavior

### Step 1: Detect Task Completion

When a task completes during `/start-phase execute`:

```
✅ Task completed: {task-name}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚦 Quality Gate Activated
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Running mandatory quality checks before proceeding...
```

---

### Step 2: Run Quality Checks (Mandatory)

Automatically execute quality checks:

```bash
python skills/start-phase/scripts/quality_gate.py $(pwd)
```

**Checks performed:**

#### A. Lint Check
```bash
npm run lint
```

**Must pass:** Zero lint errors

**If fails:**
```
❌ Lint Check FAILED

Errors:
• src/api/auth.ts:42 - 'userId' is assigned but never used
• src/lib/db.ts:15 - Missing return type annotation

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⛔ Quality Gate BLOCKED

You must fix lint errors before proceeding to the next task.

Options:
1. Let me fix these errors automatically
2. I'll fix them manually (re-run quality gate after)
3. Skip lint for this task (NOT RECOMMENDED)
```

---

#### B. Build Check
```bash
npm run build
```

**Must pass:** Build completes without errors

**If fails:**
```
❌ Build Check FAILED

Build errors:
• Type error: Property 'email' does not exist on type 'User'
• Module not found: '@/lib/auth'

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⛔ Quality Gate BLOCKED

You must fix build errors before proceeding.

Options:
1. Let me fix these errors automatically
2. I'll fix them manually (re-run quality gate after)
```

---

#### C. Test Check (Optional - Can be enabled per project)
```bash
npm test
```

**If enabled and fails:**
```
⚠️ Test Check FAILED

Failed tests:
• auth.test.ts - "should validate user credentials" FAILED

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

You can proceed, but tests are failing.

Options:
1. Fix tests now
2. Proceed anyway (mark as technical debt)
```

---

### Step 3: Quality Check Results

#### Scenario A: All Checks Passed ✅

```
✅ Lint Check PASSED
✅ Build Check PASSED
✅ Test Check PASSED (optional)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎉 Quality Checks Complete

Proceeding to code review...
```

→ Continue to Step 4 (Code Review)

---

#### Scenario B: Checks Failed ❌

```
❌ Quality Gate FAILED

Failed checks:
• Lint: 3 errors
• Build: 1 error

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⛔ BLOCKED: Cannot proceed to next task

What would you like to do?
1. Let me fix the errors automatically
2. I'll fix them manually and re-run the gate
3. Show me the specific errors
```

**Enforcement:** Hook does NOT proceed until checks pass.

---

### Step 4: Code Review (Per Task - Required)

After quality checks pass, prompt for code review:

```
✅ Quality Checks Passed

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 Code Review Required

Task: {task-name}
Files changed:
• src/api/auth.ts (+45 lines)
• src/types/user.ts (+12 lines)
• tests/auth.test.ts (+67 lines)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Switching to code_reviewer persona for task review...
```

**Perform task-specific code review:**

1. **Analyze changes:**
   - Correctness (logic + edge cases)
   - Type safety
   - Convention consistency
   - SRP/DRY violations
   - Security issues (if applicable)

2. **Create review document:**

Create `planning/code-reviews/{task-name}.md`:

```markdown
# Code Review: {task-name}

**Date:** {timestamp}
**Reviewer:** code_reviewer (AI)
**Files Reviewed:** {count} files

## Summary

{2-5 sentence summary of changes}

## Changes Analysis

### Correctness ✅
- Logic appears sound
- Edge cases handled (null checks, empty arrays)

### Type Safety ✅
- All functions properly typed
- No 'any' types used

### Convention Consistency ✅
- Follows project naming conventions
- Consistent formatting

### Code Quality ⚠️
- **Issue:** Function `validateUser()` is 45 lines (consider breaking down)
- **Suggestion:** Extract validation logic into separate functions

### Security ✅
- Input validation present
- No SQL injection risks
- Authentication checks in place

## Issues Found

1. **Medium Priority:** Long function in auth.ts:42
   - Current: 45 lines
   - Suggestion: Break into smaller functions

2. **Low Priority:** Missing JSDoc for `getUserByEmail()`
   - Add documentation for public API

## Fixes Applied

- None required (issues are recommendations)

## Verdict

✅ **APPROVED**

Code quality is good. Suggestions are minor improvements, not blockers.

## Next Steps

- None required
```

3. **Present review to user:**

```
📋 Code Review Complete

Verdict: ✅ APPROVED

Summary:
• Correctness: ✅ Good
• Type Safety: ✅ Good
• Code Quality: ⚠️ Minor suggestions
• Security: ✅ Good

Issues found: 1 medium, 1 low (non-blocking)

Full review: planning/code-reviews/{task-name}.md

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Code review approved. Proceeding to task validation...
```

---

### Step 5: Task Validation

Run task validator to ensure all artifacts exist:

```bash
python skills/start-phase/scripts/task_validator.py $(pwd) {task-name}
```

**Validates:**
- Task update file exists (`planning/task-updates/{task-name}.md`)
- Code review file exists (`planning/code-reviews/{task-name}.md`)
- Quality checks passed
- Checklist completed

**If validation fails:**
```
❌ Task Validation FAILED

Missing artifacts:
• Task update file: planning/task-updates/{task-name}.md

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Creating task update file...
```

---

### Step 6: Create Task Update File

If not exists, create `planning/task-updates/{task-name}.md`:

```markdown
# Task Update: {task-name}

**Status:** ✅ Completed
**Date:** {timestamp}
**Assigned to:** {agent-persona}

## What Changed

{Summary of changes}

## Files Touched

- src/api/auth.ts (+45 lines)
- src/types/user.ts (+12 lines)
- tests/auth.test.ts (+67 lines)

## How to Verify

1. Run: `npm run dev`
2. Test: Visit /api/auth/login
3. Verify: User can login successfully

## Decisions Made

- Used bcrypt for password hashing (security best practice)
- Stored JWT in httpOnly cookie (XSS protection)
- Added rate limiting (5 attempts per 15 min)

## Next Steps

- Integration testing with frontend
- Add password reset flow

## Quality Gate Checklist

- [x] Lint passed
- [x] Build passed
- [x] Review completed (planning/code-reviews/{task-name}.md)
- [x] Commit created
```

---

### Step 7: Git Commit (Only After Gate Passes)

After all checks pass and artifacts created:

```
✅ Quality Gate PASSED
✅ Code Review APPROVED
✅ Task Artifacts COMPLETE

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Creating git commit...
```

**Commit format:**
```bash
git add .
git commit -m "Completed task: {task-name} during phase {phase}

- Quality gate: PASSED
- Code review: APPROVED
- Files: {count} files changed, {additions} insertions, {deletions} deletions"
```

**Confirm commit:**
```
✅ Git Commit Created

Commit: abc1234
Message: "Completed task: {task-name} during phase {phase}"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎉 Task Complete & Quality Gate Passed

Ready to proceed to next task.
```

---

### Step 8: Gate Complete - Allow Next Task

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚦 Quality Gate: PASSED ✅
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Summary:
• Lint: ✅ Passed
• Build: ✅ Passed
• Review: ✅ Approved
• Commit: ✅ Created

Task {task-name} is complete and verified.

Next task can begin.
```

---

## Enforcement Rules

### Hard Blocks (Cannot Proceed)

1. **Lint fails** → Must fix before proceeding
2. **Build fails** → Must fix before proceeding
3. **Code review not created** → Must complete review
4. **Task update not created** → Must document task

### Soft Warnings (Can Proceed)

1. **Tests fail** → Warn but allow (if tests optional)
2. **Minor review issues** → Document but don't block
3. **Long files** → Flag but don't block

---

## Mid-Task Checkpoints (For Long Tasks)

For tasks taking >30 minutes:

```
⏰ Task Duration: 35 minutes

This is a long task. Creating checkpoint commit...
```

**Checkpoint rules:**
- Must compile/typecheck
- Don't need to pass full quality gate
- Labeled clearly as checkpoint

**Checkpoint commit format:**
```bash
git add .
git commit -m "checkpoint: {task-name} - {milestone}

WIP: Not ready for quality gate yet"
```

**Example:**
```
checkpoint: setup-auth-api - routes and types wired

WIP: Not ready for quality gate yet
```

---

## Configuration

### Enable/Disable Hook

```yaml
# In .claude/hooks/start-phase/quality-gate.md frontmatter
enabled: true     # Set to false to disable automatic gate
silent: false     # Set to true to suppress notifications
```

### Per-Project Settings

Can customize via project config:

```json
{
  "quality_gate": {
    "lint": true,
    "build": true,
    "test": false,
    "checkpoint_interval": 30
  }
}
```

---

## Performance

- **Quality checks:** ~10-30 seconds (lint + build)
- **Code review:** ~30-60 seconds (AI analysis)
- **Task validation:** < 2 seconds
- **Git commit:** < 1 second
- **Total overhead:** ~1-2 minutes per task

**Worth it:** Prevents broken code from accumulating.

---

## Error Handling

### If Quality Scripts Fail

```
⚠️ Quality gate script failed to run

Error: quality_gate.py not found

Falling back to manual checks. Please verify:
1. Lint passes: npm run lint
2. Build passes: npm run build
```

### If Git Operations Fail

```
⚠️ Git commit failed

Error: nothing to commit, working tree clean

This is OK - no changes were made during this task.
Proceeding to next task.
```

---

## Integration with Mode 2

This hook implements **Part 3.5** of Mode 2 (Execute):

```
Part 3: Execute tasks
  ↓
Part 3.5: Quality Gate ⭐ (THIS HOOK)
  ↓
Part 4: Task complete
```

**Automatic flow:**
1. Task completes
2. Hook triggers
3. Quality gate runs
4. Code review performed
5. Task validated
6. Commit created
7. Next task allowed

---

## Benefits

### For Code Quality

✅ **No broken code accumulates** - Lint/build must pass
✅ **Every task reviewed** - Not just end of phase
✅ **Clean history** - Commits only after quality checks
✅ **Documentation enforced** - Task updates required

### For Development Flow

✅ **Fast feedback** - Issues caught immediately
✅ **Clear checkpoints** - Always know where you are
✅ **Safe to proceed** - Confidence next task starts clean
✅ **Audit trail** - Review notes per task

### For Team Collaboration

✅ **Consistent quality** - Automated enforcement
✅ **Reviewable history** - Easy to audit changes
✅ **Clear decisions** - Documented per task
✅ **No surprises** - Quality gate prevents broken main

---

## Example Flow

```bash
# Task execution
Task 1: Setup auth API
→ Implement routes, types, logic
→ Task completes

# Hook triggers automatically
🚦 Quality Gate Activated

→ Run lint: ✅ PASSED
→ Run build: ✅ PASSED
→ Code review: ✅ APPROVED
→ Task update: ✅ CREATED
→ Git commit: ✅ CREATED

🎉 Quality Gate PASSED

# Next task can begin
Task 2: Create UI components
→ Start fresh with clean codebase
```

---

**Never skip quality gates.** They prevent technical debt from accumulating.

See `skills/start-phase/README.md` for complete documentation.
