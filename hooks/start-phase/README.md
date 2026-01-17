# Start-Phase Hooks

Comprehensive hook system for phase management with quality enforcement.

## Overview

Four hooks that implement the complete start-phase workflow:

1. **phase-start.md** - Pre-flight checks before phase begins
2. **task-complete.md** - Automatically triggers quality gate after tasks
3. **quality-gate.md** - Mandatory quality checks between tasks
4. **phase-complete.md** - Closeout and summary after phase ends

---

## Hook System Architecture

```mermaid
flowchart TD
    A[/start-phase command] --> B[phase-start hook]
    B --> C{Mode?}
    C -->|Mode 1| D[Plan Mode]
    C -->|Mode 2| E[Execute Mode]
    E --> F[Execute tasks]
    F --> G[task-complete hook]
    G --> H[quality-gate hook]
    H --> I{Passed?}
    I -->|Yes| J[Next task]
    I -->|No| K[Fix issues]
    K --> H
    J --> L{More tasks?}
    L -->|Yes| F
    L -->|No| M[phase-complete hook]
    M --> N[Phase done]
```

---

## Hooks (4 COMPREHENSIVE)

### 1. phase-start.md - Pre-flight Validation ✈️

**Trigger:** When `/start-phase` command runs
**Purpose:** Validate environment before starting

**Checks performed:**
- ✅ Task list file exists
- ✅ Git working directory clean (Mode 2 only)
- ✅ Dependencies installed (Mode 2 only)
- ✅ Quality gate tools available (Mode 2 only)
- ✅ Lint/build scripts present (Mode 2 only)

**Blocks if:**
- Task list not found
- Critical dependencies missing (Mode 2)
- Quality tools not found (Mode 2)

**Example:**
```bash
/start-phase execute prototype-build ./planning/tasks.md

# Hook triggers
🚀 Pre-flight Checks Running...

✅ Task list found
✅ Git clean
✅ Dependencies installed
✅ Quality tools available

Proceeding to Mode 2...
```

**See:** `hooks/start-phase/phase-start.md`

---

### 2. task-complete.md - Automatic Gate Trigger 🔔

**Trigger:** After each task completes
**Purpose:** Bridge task execution to quality gate

**Actions:**
1. Detect task completion
2. Extract task information
3. Check for mid-task checkpoints
4. Trigger quality-gate hook
5. Monitor gate results
6. Update phase progress
7. Preview next task

**Example:**
```bash
# Task completes
✅ Task Complete: setup-auth-api

# Hook triggers
🔔 Task-Complete Detected

Task: setup-auth-api
Duration: 28m
Files: 3 changed

Triggering quality gate...
```

**See:** `hooks/start-phase/task-complete.md`

---

### 3. quality-gate.md - Mandatory Quality Enforcement 🚦

**Trigger:** After task-complete hook (or manual)
**Purpose:** Enforce quality between tasks

**Workflow:**
1. **Run quality checks** (lint + build + optional test)
2. **Perform code review** (AI-powered per task)
3. **Validate task completion** (all artifacts present)
4. **Create task update file** (documentation)
5. **Git commit** (only after all pass)

**Hard blocks:**
- ❌ Lint errors
- ❌ Build errors
- ❌ Missing code review
- ❌ Missing task update

**Soft warnings:**
- ⚠️ Test failures (if optional)
- ⚠️ Minor review issues

**Example:**
```bash
# Quality gate runs
🚦 Quality Gate Activated

→ Lint: ✅ PASSED
→ Build: ✅ PASSED
→ Review: ✅ APPROVED

Creating git commit...

✅ Quality Gate PASSED

Next task can begin.
```

**See:** `hooks/start-phase/quality-gate.md`

---

### 4. phase-complete.md - Phase Closeout & Summary 🎉

**Trigger:** After all tasks complete
**Purpose:** Generate comprehensive phase documentation

**Generates:**
1. **Phase summary** (phase-summary.md)
   - What was delivered
   - What was deferred
   - Notable decisions
   - Known risks
   - Quality metrics

2. **Next phase candidates** (next-phase-candidates.md)
   - Backlog items discovered
   - Technical debt notes
   - Improvements needed
   - Follow-up tasks

3. **Final SLOC analysis** (system-changes.md update)
   - Per-file changes
   - Total SLOC delta
   - Code distribution

4. **Phase archive** (planning-archive-{phase}/)
   - All planning files backed up
   - Metadata captured

5. **Handoff documentation** (phase-handoff.md)
   - For next developer
   - Quick start guide
   - Known issues

**Example:**
```bash
# All tasks done
🎉 All Tasks Complete!

# Hook triggers
📊 Collecting metrics...
📝 Generating summary...
📦 Archiving phase data...
📋 Creating handoff docs...

✅ Phase closeout complete

Ready for Phase 2!
```

**See:** `hooks/start-phase/phase-complete.md`

---

## Hook Execution Flow

### Complete Phase Workflow

```
1. User: /start-phase execute prototype-build ./tasks.md

2. phase-start hook ✈️
   → Pre-flight checks
   → Validate environment
   → ✅ Ready to execute

3. Mode 2 Part 1-2
   → Create directories
   → Generate planning docs

4. Mode 2 Part 3 (Execute tasks)
   ↓
   Task 1: Setup API
   → Execute
   → task-complete hook 🔔
   → quality-gate hook 🚦
      → Lint ✅
      → Build ✅
      → Review ✅
      → Commit ✅
   → Next task
   ↓
   Task 2: Create UI
   → Execute
   → task-complete hook 🔔
   → quality-gate hook 🚦
   → Next task
   ↓
   [... repeat for all tasks ...]
   ↓
   Task 8: Final review
   → Execute
   → task-complete hook 🔔
   → quality-gate hook 🚦
   → ALL TASKS COMPLETE
   ↓
   phase-complete hook 🎉
   → Generate summary
   → Archive data
   → Handoff docs
   → ✅ PHASE DONE
```

---

## Integration with Mode 2 Parts

### Part 1: Finalize Plan
- phase-start hook validates setup

### Part 2: Detailed Planning
- No hooks (planning only)

### Part 3: Execute Tasks
- task-complete hook triggers after each task

### Part 3.5: Quality Gate
- quality-gate hook enforces quality

### Part 4: Task Updates
- Handled by quality-gate hook

### Part 5: Phase Closeout
- phase-complete hook generates artifacts

---

## Configuration

### Enable/Disable Hooks

All hooks can be individually enabled/disabled:

```yaml
# In each hook's frontmatter
enabled: true     # Set to false to disable
silent: false     # Set to true for quiet operation
```

### Global Hook Settings

Can configure via project settings:

```json
{
  "start_phase_hooks": {
    "phase_start": {
      "enabled": true,
      "strict_git_check": true,
      "require_dependencies": true
    },
    "task_complete": {
      "enabled": true,
      "auto_trigger_gate": true,
      "checkpoint_warning": true
    },
    "quality_gate": {
      "enabled": true,
      "lint": true,
      "build": true,
      "test": false,
      "checkpoint_interval": 30
    },
    "phase_complete": {
      "enabled": true,
      "generate_summary": true,
      "archive_data": true,
      "update_memory_bank_prompt": true
    }
  }
}
```

---

## Hook Priorities

Hooks execute in priority order:

1. **phase-start** - HIGH (must run first)
2. **task-complete** - MEDIUM (per task)
3. **quality-gate** - HIGH (critical checks)
4. **phase-complete** - MEDIUM (final step)

---

## Performance Impact

### Per-Hook Overhead

| Hook | Time | When | Impact |
|------|------|------|--------|
| **phase-start** | 3-5s | Once per phase | Minimal |
| **task-complete** | 3s | Per task | Low |
| **quality-gate** | 1-2m | Per task | Moderate |
| **phase-complete** | 25s | Once per phase | Minimal |

### Total Phase Overhead

For a phase with 8 tasks:
- phase-start: ~5s (once)
- task-complete: ~24s (8 × 3s)
- quality-gate: ~12m (8 × 1.5m)
- phase-complete: ~25s (once)

**Total overhead:** ~13 minutes for 8 tasks
**Execution time:** ~3 hours (example)
**Overhead percentage:** ~7%

**Worth it:** Prevents issues that would cost much more time to fix later.

---

## Benefits of Hook System

### For Quality

✅ **Automated enforcement** - No manual checks needed
✅ **Consistent standards** - Same process every task
✅ **Early detection** - Issues caught immediately
✅ **Clean checkpoints** - Always green between tasks

### For Documentation

✅ **Automatic documentation** - Task updates, reviews, summaries
✅ **Complete record** - Nothing forgotten
✅ **Easy audit** - Clear history
✅ **Knowledge retention** - Decisions captured

### For Development

✅ **Fast feedback** - Know immediately if something's wrong
✅ **Clear progress** - Always know phase status
✅ **Safe to proceed** - Confidence in code quality
✅ **Easy handoff** - Next phase starts with context

---

## Troubleshooting

### Hook not triggering

**Check:**
1. Hook enabled in frontmatter?
2. Trigger condition met?
3. Filter matches context?
4. Hook file in correct location?

**Debug:**
```bash
# Check hook status
ls -la hooks/start-phase/*.md

# Verify frontmatter
head -20 hooks/start-phase/quality-gate.md
```

---

### Quality gate blocking incorrectly

**Check:**
1. Are lint/build commands correct?
2. Is codebase actually clean?
3. Are quality scripts available?

**Fix:**
```bash
# Manually run checks
npm run lint
npm run build

# If passing, check quality gate script
python skills/start-phase/scripts/quality_gate.py $(pwd)
```

---

### Hook execution order wrong

**Check:**
1. Hook priorities set correctly?
2. Multiple hooks with same trigger?
3. Hook dependencies clear?

**Fix:**
Verify priority in frontmatter:
```yaml
priority: high  # or medium, low
```

---

### Phase not completing

**Check:**
1. All tasks marked complete?
2. Final quality gate passed?
3. phase-complete hook enabled?

**Manually trigger:**
```bash
/phase-complete {phase_name}
```

---

## Manual Hook Invocation

Can manually trigger hooks when needed:

```bash
# Manually run quality gate
/quality-gate {task-name}

# Manually complete phase
/phase-complete {phase_name}

# Re-run pre-flight checks
/pre-flight-check
```

---

## Hook Development

### Adding New Hooks

To add a new hook:

1. Create hook file: `hooks/start-phase/new-hook.md`
2. Add frontmatter:
   ```yaml
   ---
   name: start-phase-new-hook
   trigger: on-event-name
   description: What this hook does
   enabled: true
   silent: false
   filter:
     context: start-phase
   ---
   ```
3. Implement workflow
4. Document in this README
5. Test thoroughly

---

### Hook Testing

Test hooks before enabling:

1. **Dry run:** Set `enabled: false`, manually trigger
2. **Single task:** Test on one task first
3. **Full phase:** Test complete workflow
4. **Edge cases:** Test failures, warnings, edge cases

---

## Examples

### Successful Phase with All Hooks

```bash
# Start phase
/start-phase execute prototype-build ./tasks.md

# phase-start hook
✈️ Pre-flight checks: ✅ PASSED

# Execute Task 1
Task 1: Setup API
→ Execute code
→ task-complete hook 🔔
→ quality-gate hook 🚦
   → Lint: ✅
   → Build: ✅
   → Review: ✅
   → Commit: ✅
→ Next task

# Execute Task 2
Task 2: Create UI
→ Execute code
→ task-complete hook 🔔
→ quality-gate hook 🚦
   → Lint: ✅
   → Build: ✅
   → Review: ✅
   → Commit: ✅
→ Next task

# [... 6 more tasks ...]

# All tasks complete
🎉 All Tasks Complete!

# phase-complete hook
→ Generate summary ✅
→ Archive data ✅
→ Handoff docs ✅

✅ PHASE COMPLETE
```

---

### Phase with Quality Gate Failure

```bash
# Task executes
Task 3: Add validation
→ Execute code
→ task-complete hook 🔔
→ quality-gate hook 🚦
   → Lint: ❌ FAILED (3 errors)

⛔ Quality gate BLOCKED

Fix lint errors:
• src/api/auth.ts:42 - unused variable
• src/lib/db.ts:15 - missing type

Options:
1. Let me fix
2. Fix manually

# User chooses: Fix manually
# Fixes errors

# Re-run quality gate
/quality-gate add-validation

# quality-gate hook (retry)
→ Lint: ✅ PASSED
→ Build: ✅ PASSED
→ Review: ✅ APPROVED
→ Commit: ✅ CREATED

✅ Quality gate PASSED
→ Next task
```

---

## Summary

The start-phase hook system provides:
- ✈️ **Pre-flight validation** (phase-start)
- 🔔 **Automatic gate triggering** (task-complete)
- 🚦 **Quality enforcement** (quality-gate)
- 🎉 **Comprehensive closeout** (phase-complete)

**Result:** Structured, quality-focused phase management with automated checks and complete documentation.

---

See individual hook files for detailed documentation:
- `phase-start.md` - Pre-flight checks
- `task-complete.md` - Gate trigger
- `quality-gate.md` - Quality enforcement
- `phase-complete.md` - Closeout summary

See `skills/start-phase/README.md` for complete start-phase system documentation.
