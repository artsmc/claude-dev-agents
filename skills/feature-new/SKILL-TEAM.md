---
name: feature-new-team
description: Complete feature workflow with multi-agent team parallelization
args:
  feature_description:
    type: string
    description: Brief description of the feature to develop
    required: true
  team_mode:
    type: string
    description: "Team execution mode: auto, enabled, disabled"
    required: false
    default: "auto"
---

# Feature New (Team Mode)

Execute the complete end-to-end feature development workflow with **multi-agent team parallelization** for maximum speed.

---

## Team Mode Detection

**Step 0: Determine Execution Mode**

Parse args to check for `--team` flag or `team_mode` parameter:

```bash
# User can specify:
# /feature-new "add auth" --team              → Force team mode
# /feature-new "add auth" --sequential        → Force sequential mode
# /feature-new "add auth"                     → Auto-detect mode

if args contains "--team" or team_mode == "enabled":
    USE_TEAM_MODE = true
elif args contains "--sequential" or team_mode == "disabled":
    USE_TEAM_MODE = false
else:
    # Auto-detect based on feature complexity
    # (We'll make this decision after spec planning in Step 4)
    USE_TEAM_MODE = "auto"
```

Display mode selection:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚀 Feature New: {{feature_description}}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Execution mode: [Team Mode ENABLED / Sequential / Auto-detect]

Team mode benefits:
  ⚡ 1.5-2x faster execution (parallel tasks)
  🎯 Specialized agents per task
  🔄 Automatic peer communication
  ✅ Quality gates enforced per agent
```

---

## Step 1: Initialize Documentation Systems (if needed)

[Same as original - no changes needed]

---

## Step 2: Generate Feature Specification (Team-Enhanced)

**If USE_TEAM_MODE == true:**

Use team-enabled spec generation:

```typescript
// Check if team flag was passed
if (USE_TEAM_MODE === true || USE_TEAM_MODE === "auto") {
  // Try team mode first
  Skill({
    skill: "spec-plan",
    args: "{{feature_description}} --team"
  });
} else {
  // Use sequential mode
  Skill({
    skill: "spec-plan",
    args: "{{feature_description}}"
  });
}
```

**What happens in team mode:**
1. Research phase (sequential): 5 min
2. Spec generation (parallel): 4 min with 4 agents
3. Validation phase (sequential): 2 min

**Total:** 11 min vs 19 min sequential (42% faster)

**Display:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚡ Step 2/6: Parallel Spec Generation (Team Mode)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Team: spec-generation (4 agents)

Research Phase (5 min):
  ├─ Reading Memory Bank... ✓
  ├─ Reading Documentation Hub... ✓
  └─ Analyzing codebase patterns... ✓

Parallel Spec Generation (4 min):
  ├─ [frd-writer] Generating FRD.md... ✓
  ├─ [frs-tr-writer] Generating FRS.md + TR.md... ✓
  ├─ [scenario-writer] Generating GS.md... ✓
  └─ [task-writer] Generating task-list.md... ✓

Validation (2 min):
  └─ Cross-reference validation... ✓

Team shutdown ✓

✅ Step 2/6: Specification created (11 min)
   Location: ./job-queue/feature-{name}/docs/
   ⚡ Speedup: 1.7x faster than sequential
```

---

## Step 3: Review Specification Quality

[Same as original - no changes needed]

---

## Step 4: Create Strategic Execution Plan

**After getting task-list.md, analyze for team mode:**

```bash
# Read task-list.md
task_count=$(grep -c "^## Task" task-list.md)

# Auto-detect mode logic
if USE_TEAM_MODE == "auto":
    if task_count >= 7:
        USE_TEAM_MODE = true
        echo "📊 Auto-detect: $task_count tasks detected → Team mode ENABLED"
    else:
        USE_TEAM_MODE = false
        echo "📊 Auto-detect: $task_count tasks detected → Sequential mode"
```

Then run planning:

```typescript
Skill({
  skill: "start-phase-plan",
  args: "{path_to_task_list}"
});
```

**start-phase-plan will:**
1. Analyze dependencies
2. Create execution waves (if team mode)
3. Show parallel speedup estimate
4. Ask user for approval

**Display with team mode enabled:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Step 4/6: Strategic Plan (Team Mode Analysis)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Task count: 7 tasks
Dependencies analyzed: 4 execution waves identified

Execution Plan:

Wave 1 (Parallel - 2 tasks, 22 min):
  ├─ Task 1: Create auth API endpoint (backend)
  └─ Task 2: Create login UI component (ui)
     No dependencies ✓

Wave 2 (Sequential - 1 task, 15 min):
  └─ Task 3: Connect UI to API (frontend)
     Depends on: Tasks 1, 2

Wave 3 (Parallel - 2 tasks, 22 min):
  ├─ Task 4: Add JWT token generation (backend)
  └─ Task 5: Create user database schema (backend)
     Both depend on: Task 3

Wave 4 (Parallel - 2 tasks, 25 min):
  ├─ Task 6: Write integration tests (qa)
  └─ Task 7: Write documentation (docs)
     Both depend on: All previous tasks

⚡ Parallel Execution Estimate:
  Sequential: 127 minutes (2h 7min)
  Parallel:   84 minutes (1h 24min)
  Speedup:    1.5x (34% time saved)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👤 CHECKPOINT 2: Approve Team Execution Plan
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Options:
  - approve: Execute with team mode (parallel)
  - sequential: Execute without teams (sequential)
  - revise: Adjust task breakdown
  - cancel: Stop workflow
```

---

## Step 5: Import to PM-DB

```typescript
Skill({
  skill: "pm-db",
  args: `import --project feature-{name} --mode ${USE_TEAM_MODE ? 'parallel' : 'sequential'}`
});
```

**Display:**
```
✅ Step 5/6: Imported to PM-DB
   Phase Run ID: 42
   Execution mode: ${USE_TEAM_MODE ? 'parallel (team)' : 'sequential'}
   Task count: 7
   Estimated duration: ${USE_TEAM_MODE ? '84 min' : '127 min'}
```

---

## Step 6: Execute Phase (Team-Enhanced)

**If USE_TEAM_MODE == true:**

Use team-enabled execution:

```typescript
Skill({
  skill: "start-phase-execute",
  args: `${path_to_task_list} --team`
});
```

**What happens in team mode:**

### Phase Structure

```
Part 1: Create directories
Part 2: Generate planning docs
Part 3: Create team & analyze dependencies
Part 4: Execute with multi-agent team
Part 5: Quality gates & closeout
```

### Part 3: Team Setup

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚡ Part 3: Team-Based Execution Setup
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Creating team: phase-execution
Team config: ~/.claude/teams/phase-execution/config.json
Task list: ~/.claude/tasks/phase-execution/

Creating task entries with dependencies...
  ✓ Task 1: Create auth API endpoint
  ✓ Task 2: Create login UI component
  ✓ Task 3: Connect UI to API (blocked by: 1, 2)
  ✓ Task 4: Add JWT token generation (blocked by: 3)
  ✓ Task 5: Create user schema (blocked by: 3)
  ✓ Task 6: Write integration tests (blocked by: 1-5)
  ✓ Task 7: Write documentation (blocked by: 1-5)

All tasks created ✓
```

### Part 4: Wave Execution

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
━━━ Wave 1 (2 tasks) ━━━
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Spawning agents for Wave 1...
  ✓ backend-agent-1 (nextjs-backend-developer)
  ✓ ui-agent-1 (ui-developer)

[backend-agent-1] Claiming Task 1...
[backend-agent-1] Task 1: Create auth API endpoint
  ├─ Owner: backend-agent-1
  ├─ Status: in_progress
  └─ Writing src/api/auth/route.ts...

[ui-agent-1] Claiming Task 2...
[ui-agent-1] Task 2: Create login UI component
  ├─ Owner: ui-agent-1
  ├─ Status: in_progress
  └─ Writing src/components/LoginForm.tsx...

[Agents working in parallel...]

[backend-agent-1] Task 1 progress:
  ├─ Code written ✓
  ├─ Quality gate: Lint ✓ Build ✓
  ├─ Code review: ✓ Passed
  ├─ Git commit: feat: add auth API endpoint
  └─ Task 1 complete! (20 minutes)

[ui-agent-1] Task 2 progress:
  ├─ Code written ✓
  ├─ Quality gate: Lint ✓ Build ✓
  ├─ Code review: ✓ Passed
  ├─ Git commit: feat: add login UI component
  └─ Task 2 complete! (18 minutes)

✅ Wave 1 complete in 22 minutes (longest task)
   (Sequential would have taken 38 minutes)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
━━━ Wave 2 (1 task) ━━━
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Spawning agents for Wave 2...
  ✓ frontend-agent-1 (frontend-developer)

[frontend-agent-1] Claiming Task 3...
[frontend-agent-1] Checking dependencies...
  ✓ Task 1 (auth API): completed
  ✓ Task 2 (login UI): completed
  ✓ Dependencies satisfied!

[frontend-agent-1] Task 3: Connect UI to API
  ├─ Writing src/lib/auth.ts...
  ├─ Quality gate: Lint ✓ Build ✓
  ├─ Code review: ✓ Passed
  ├─ Git commit: feat: connect login UI to API
  └─ Task 3 complete! (15 minutes)

✅ Wave 2 complete in 15 minutes

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
━━━ Wave 3 (2 tasks) ━━━
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[backend-agent-2] Task 4 complete! (22 minutes)
[backend-agent-3] Task 5 complete! (12 minutes)

✅ Wave 3 complete in 22 minutes

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
━━━ Wave 4 (2 tasks) ━━━
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[qa-agent-1] Task 6: Write integration tests
  ├─ Writing tests/integration/auth.test.ts...
  └─ Tests passing (12/12) ✓

[docs-agent-1] Task 7: Write documentation
  ├─ SendMessage to backend-agent-2: "What's the JWT expiry time?" ✓
  ├─ [backend-agent-2 responds: "15 minutes access, 7 days refresh"]
  └─ Writing docs/authentication.md... ✓

✅ Wave 4 complete in 25 minutes

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔄 Shutting Down Team
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Requesting shutdown for all agents...
  ✓ backend-agent-1 ✓
  ✓ ui-agent-1 ✓
  ✓ frontend-agent-1 ✓
  ✓ backend-agent-2 ✓
  ✓ backend-agent-3 ✓
  ✓ qa-agent-1 ✓
  ✓ docs-agent-1 ✓

Team shutdown complete ✓
Cleaning up team resources ✓
```

### Part 5: Closeout with Metrics

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Phase Complete!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Tasks: 7/7 completed
Duration: 84 minutes (1h 24min)
Quality gates: 7/7 passed
Git commits: 7 commits
Test coverage: 89%

⚡ Parallel Execution Breakdown:
  Wave 1: 22 min (2 agents)
  Wave 2: 15 min (1 agent)
  Wave 3: 22 min (2 agents)
  Wave 4: 25 min (2 agents)

⚡ Speedup Analysis:
  Sequential estimate: 127 minutes
  Actual (parallel): 84 minutes
  Time saved: 43 minutes (34%)
  Speedup: 1.5x

Agent Utilization:
  backend-agent-1: 20 min (Task 1)
  backend-agent-2: 22 min (Task 4)
  backend-agent-3: 12 min (Task 5)
  ui-agent-1: 18 min (Task 2)
  frontend-agent-1: 15 min (Task 3)
  qa-agent-1: 25 min (Task 6)
  docs-agent-1: 15 min (Task 7)

Peer Communication:
  └─ docs-agent-1 → backend-agent-2 (1 message)
```

---

## Final Output

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎉 FEATURE COMPLETE (Team Mode)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Feature: {{feature_description}}
Location: ./job-queue/feature-{name}/

Completed Steps:
  ✅ [1/6] Documentation initialized
  ✅ [2/6] Specification created (⚡ 1.7x faster with teams)
  ✅ [3/6] Specification reviewed
  ✅ [4/6] Strategic plan approved
  ✅ [5/6] Imported to PM-DB
  ✅ [6/6] Phase executed (⚡ 1.5x faster with teams)

⚡ Team Mode Performance:
  Total time: 95 minutes (1h 35min)
  Sequential estimate: 146 minutes (2h 26min)
  Time saved: 51 minutes (35%)
  Overall speedup: 1.54x

Agents used: 9 total
  Spec generation: 4 agents
  Task execution: 7 agents (some reused)

Next steps:
  - View metrics: /pm-db dashboard
  - Update Memory Bank: /memory-bank-sync
  - View phase summary: ./job-queue/feature-{name}/planning/phase-structure/phase-summary.md

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Error Handling (Team-Specific)

### Team Creation Failures

```
❌ Failed to create team: phase-execution

Reason: CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS not enabled

Recovery:
  1. Enable teams in settings.json:
     {
       "env": {
         "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
       }
     }
  2. Retry with: /feature-new "{{feature_description}}" --team
  3. Or use sequential mode: /feature-new "{{feature_description}}" --sequential
```

### Agent Spawn Failures

```
❌ Failed to spawn agent: backend-agent-2

Reason: Insufficient resources or tmux not available

Recovery:
  1. Check tmux installation: which tmux
  2. Reduce agent count (use sequential mode)
  3. Retry with fewer parallel waves
```

### Task Deadlock Detection

```
⚠️ Potential deadlock detected in Wave 3

Task 4 blocked by: Task 3 (not yet complete)
Task 5 blocked by: Task 3 (not yet complete)
Task 3 blocked by: Task 2 (marked complete but verification failed)

Recovery:
  1. Manually verify Task 2 completion
  2. Update task status: TaskUpdate({ taskId: "2", status: "completed" })
  3. Or tell team lead: "Unblock Task 3"
```

---

## Usage Examples

### Force Team Mode

```bash
/feature-new "add user authentication with JWT" --team
```

### Force Sequential Mode

```bash
/feature-new "add logout button" --sequential
```

### Auto-Detect Mode (Default)

```bash
/feature-new "add payment processing"
# System will choose based on task count and complexity
```

### Per-Step Control

```bash
/feature-new "add admin dashboard" --spec-mode=team --exec-mode=sequential
```

---

## Best Practices (from Claude Code Docs)

### Give Teammates Enough Context

Teammates don't inherit conversation history. Each spawn prompt should include:
- Task-specific details
- File locations
- API contracts
- Expected deliverables

### Size Tasks Appropriately

- **Too small**: Coordination overhead exceeds benefit
- **Too large**: Risk of wasted effort without check-ins
- **Just right**: Self-contained units (function, test file, review)

### Avoid File Conflicts

Break work so each teammate owns different files. If two agents edit the same file, overwrites can occur.

### Monitor and Steer

Check on teammate progress, redirect approaches that aren't working, and synthesize findings as they come in.

### Quality Gates with Hooks

Use hooks to enforce quality:
- `TeammateIdle`: Exit code 2 sends feedback and keeps teammate working
- `TaskCompleted`: Exit code 2 prevents completion and sends feedback

---

## Token Usage Considerations

**Team mode uses significantly more tokens:**
- Each teammate has its own context window
- Token usage scales with number of active teammates
- For research, review, and new features: extra tokens are worthwhile
- For routine tasks: sequential mode is more cost-effective

**Estimated token usage for 7-task feature:**
- Sequential: ~150k tokens
- Team mode: ~350k tokens (2.3x more)
- But 1.5x faster execution time

**When to use team mode:**
- ✅ Complex features (10+ hours sequential)
- ✅ Multiple independent modules
- ✅ Time is more valuable than token cost
- ❌ Simple changes (< 2 hours sequential)
- ❌ Routine maintenance
- ❌ Single-file modifications

---

## Notes for Execution

- **Team management**: Create team at start of execution, clean up at end
- **Task tracking**: Use shared task list at `~/.claude/tasks/phase-execution/`
- **Dependency enforcement**: TaskUpdate with `addBlockedBy` prevents premature execution
- **Agent spawning**: Spawn only agents needed for current wave (not all at once)
- **Shutdown protocol**: Request shutdown for all agents, wait for confirmations, then TeamDelete
- **Failure recovery**: If agent fails, spawn replacement to continue work
- **Quality gates**: Enforced per agent, not just at phase level
