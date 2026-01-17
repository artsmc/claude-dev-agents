---
name: start-phase-phase-start
trigger: on-command
description: Validates phase setup when starting Mode 1 or Mode 2
enabled: true
silent: false
filter:
  command: start-phase
---

# Start-Phase: Phase Start Hook

Validates environment and setup when starting a phase (Mode 1 or Mode 2).

## Purpose

Ensures the phase has everything needed before beginning:
- Required files exist
- Directory structure valid
- Dependencies installed
- Git state clean (if Mode 2)

## Trigger

**Event:** `on-command`
**Filter:** When `/start-phase plan` or `/start-phase execute` is invoked
**When:** Before Mode 1 or Mode 2 begins

## Behavior

### Step 1: Detect Phase Start

When user invokes `/start-phase`:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚀 Start-Phase Command Detected
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Mode: {plan | execute}
Phase: {phase_name}
Task List: {task_list_file}

Running pre-flight checks...
```

---

### Step 2: Validate Task List File

Check if task list file exists:

```bash
if [ ! -f "{task_list_file}" ]; then
  echo "ERROR: Task list file not found"
fi
```

**If not found:**
```
❌ Pre-flight Check FAILED

Task list file not found: {task_list_file}

Please provide a valid path to your task list.

Example:
/start-phase plan prototype-build ./planning/tasks.md
```

**If found:**
```
✅ Task list file found: {task_list_file}
```

---

### Step 3: Determine Input Folder

Extract input folder from task list path:

```
Input folder detected: {input_folder}

This is where planning files will be created.
```

---

### Step 4: Mode-Specific Checks

#### For Mode 1 (Plan)

```
Mode: PLAN

Pre-flight checks for planning mode:
```

**Checks:**
1. ✅ Task list readable
2. ✅ Documentation Hub accessible (if exists)
3. ✅ Memory Bank accessible (if exists)

**No directory creation** - Mode 1 is planning only

---

#### For Mode 2 (Execute)

```
Mode: EXECUTE

Pre-flight checks for execution mode:
```

**Checks:**

**A. Git Status Check (Critical)**
```bash
git status --porcelain
```

**If working directory not clean:**
```
⚠️ Git Working Directory Not Clean

You have uncommitted changes:
• 3 modified files
• 2 untracked files

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Recommendation: Commit or stash changes before starting a phase.

Options:
1. Let me create a commit for you
2. I'll handle it manually
3. Proceed anyway (NOT RECOMMENDED)
```

**If clean:**
```
✅ Git working directory clean
```

---

**B. Dependencies Check**
```bash
npm list 2>/dev/null || yarn list 2>/dev/null
```

**If node_modules missing:**
```
⚠️ Dependencies Not Installed

node_modules/ not found

Run: npm install (or yarn install)

Options:
1. Let me run npm install
2. I'll run it manually
```

**If installed:**
```
✅ Dependencies installed
```

---

**C. Planning Directory Check**

Check if planning directories already exist:

```bash
ls {input_folder}/planning/ 2>/dev/null
```

**If exists with content:**
```
⚠️ Planning Directory Already Exists

Found existing planning files:
• planning/task-updates/ (3 files)
• planning/agent-delegation/ (2 files)
• planning/phase-structure/ (1 file)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

This may be from a previous phase.

Options:
1. Archive previous phase data (move to planning-archive/)
2. Continue with existing data
3. Clean and start fresh (DESTRUCTIVE)
```

**If clean:**
```
✅ Planning directory ready for creation
```

---

**D. Lint/Build Scripts Check**

Check if quality gate commands available:

```bash
npm run lint --dry-run 2>/dev/null
npm run build --dry-run 2>/dev/null
```

**If missing:**
```
⚠️ Quality Gate Commands Not Available

Missing scripts in package.json:
• npm run lint
• npm run build

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Quality gates require these scripts.

Options:
1. Add default scripts to package.json
2. Skip quality gates for this phase (NOT RECOMMENDED)
3. I'll add them manually
```

**If available:**
```
✅ Quality gate commands available
✅ npm run lint
✅ npm run build
```

---

### Step 5: Python Tools Check

Verify quality gate tools exist:

```bash
ls skills/start-phase/scripts/*.py
```

**Check for:**
- validate_phase.py
- quality_gate.py
- sloc_tracker.py
- task_validator.py

**If missing:**
```
⚠️ Quality Gate Tools Not Found

Missing Python scripts:
• skills/start-phase/scripts/quality_gate.py
• skills/start-phase/scripts/task_validator.py

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Quality gates will be unavailable.

Options:
1. Let me create the tools
2. Proceed without quality gates (NOT RECOMMENDED)
```

**If found:**
```
✅ Quality gate tools available
```

---

### Step 6: Pre-flight Summary

After all checks:

#### All Checks Passed ✅

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Pre-flight Checks PASSED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Environment ready for phase: {phase_name}

✅ Task list: {task_list_file}
✅ Input folder: {input_folder}
✅ Git: Clean working directory
✅ Dependencies: Installed
✅ Quality tools: Available

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Proceeding to {Mode 1 | Mode 2}...
```

→ Start phase normally

---

#### Warnings Present ⚠️

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️ Pre-flight Checks: WARNINGS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Warnings found:
• Git working directory has uncommitted changes
• Planning directory already exists

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

You can proceed, but it's recommended to resolve warnings first.

Proceed anyway? (y/n)
```

---

#### Critical Errors ❌

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
❌ Pre-flight Checks: FAILED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Critical errors:
• Task list file not found: {task_list_file}
• Dependencies not installed (node_modules missing)
• Quality gate scripts not found

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⛔ Cannot proceed until errors are resolved.

Recommendations:
1. Verify task list path
2. Run: npm install
3. Ensure quality gate tools are installed
```

→ Block phase start until fixed

---

## Configuration

### Enable/Disable Hook

```yaml
# In frontmatter
enabled: true     # Set to false to skip pre-flight checks
silent: false     # Set to true for quiet operation
```

### Customize Checks

Can configure which checks to run:

```json
{
  "pre_flight": {
    "git_clean": true,
    "dependencies": true,
    "quality_tools": true,
    "lint_build_scripts": true
  }
}
```

---

## Integration with Modes

### Mode 1 (Plan)

Minimal checks:
- Task list exists
- Can read docs/memory bank

**No setup required** - planning only

---

### Mode 2 (Execute)

Comprehensive checks:
- Git clean
- Dependencies installed
- Planning directories ready
- Quality tools available
- Lint/build scripts present

**Setup validated before execution**

---

## Performance

- **Pre-flight checks:** ~3-5 seconds
- **Git status:** < 1 second
- **Dependency check:** < 1 second
- **File checks:** < 1 second

**Worth it:** Prevents starting a phase in a broken environment.

---

## Error Recovery

### Auto-fix Options

Hook can auto-fix common issues:

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Create planning directories:**
   ```bash
   mkdir -p planning/{task-updates,agent-delegation,phase-structure,code-reviews}
   ```

3. **Archive previous phase:**
   ```bash
   mv planning/ planning-archive-$(date +%Y%m%d)/
   ```

4. **Add quality scripts:**
   ```json
   {
     "scripts": {
       "lint": "eslint .",
       "build": "tsc --noEmit"
     }
   }
   ```

---

## Benefits

### Prevents Common Failures

✅ **No missing files** - Task list validated upfront
✅ **No dependency issues** - Checked before starting
✅ **No git conflicts** - Clean state required
✅ **No tool failures** - Quality scripts validated

### Saves Time

✅ **Fail fast** - Issues caught before phase begins
✅ **Auto-fix** - Common issues resolved automatically
✅ **Clear feedback** - Knows exactly what's wrong

---

## Example Flow

```bash
# User starts phase
/start-phase execute prototype-build ./planning/tasks.md

# Hook triggers
🚀 Start-Phase Command Detected

# Checks run
✅ Task list found
✅ Git clean
✅ Dependencies installed
✅ Quality tools available

# Summary
✅ Pre-flight Checks PASSED

# Proceed to Mode 2
Entering Mode 2 (Execute)...
```

---

See `skills/start-phase/README.md` for complete documentation.
