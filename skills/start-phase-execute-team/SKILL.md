---
name: start-phase-execute-team
description: Parallel task execution with multi-agent teams and quality gates
args:
  task_list_file:
    type: string
    description: Path to task list markdown file
    required: true
  team_mode:
    type: string
    description: "Team execution mode: auto, enabled, disabled"
    required: false
    default: "auto"
---

# Start-Phase Execute (Team Mode)

Enhanced phase execution with multi-agent teams for parallel task execution.

**Speedup:** 1.5-2x faster depending on task parallelism

---

## Mode Detection

**Step 0: Determine Execution Mode**

```bash
# Check args for --team flag
if args contains "--team":
    USE_TEAM_MODE=true
    echo "⚡ Team mode: ENABLED (forced)"
elif args contains "--sequential":
    USE_TEAM_MODE=false
    echo "📝 Team mode: DISABLED (sequential)"
else:
    # Auto-detect based on task count and dependencies
    task_count=$(grep -c "^## Task" "$task_list_file")

    if [ $task_count -ge 7 ]; then
        USE_TEAM_MODE=true
        echo "⚡ Team mode: ENABLED (auto-detected $task_count tasks)"
    else:
        USE_TEAM_MODE=false
        echo "📝 Team mode: DISABLED ($task_count tasks, threshold is 7)"
    fi
fi
```

---

## Part 1: Create Directories

[Same as original start-phase-execute]

---

## Part 2: Generate Planning Docs

[Same as original start-phase-execute]

---

## Part 3: Execute Tasks (Team-Enhanced)

### Step 3.0: Parse Task List

```bash
# Read task-list.md and extract task information
Read("$task_list_file")

# Parse tasks:
tasks = []
for each "## Task N:" section:
    extract:
        - id: N
        - subject: task title
        - agent_type: recommended agent
        - depends_on: [] (parse from "Depends on:" or "Blocked by:")
        - estimated_time: minutes

# Example parsed task:
{
  id: "1",
  subject: "Create auth API endpoint",
  agent_type: "nextjs-backend-developer",
  depends_on: [],
  estimated_time: 20
}
```

### Step 3.1: Analyze Dependencies & Create Waves

**If USE_TEAM_MODE == true:**

```typescript
interface Task {
  id: string;
  subject: string;
  agent_type: string;
  depends_on: string[];
  estimated_time: number;
}

function createWaves(tasks: Task[]): Task[][] {
  const waves: Task[][] = [];
  const completed = new Set<string>();

  while (completed.size < tasks.length) {
    // Find all tasks whose dependencies are satisfied
    const wave = tasks.filter(task =>
      !completed.has(task.id) &&
      task.depends_on.every(dep => completed.has(dep))
    );

    if (wave.length === 0) {
      throw new Error('Circular dependency detected in task list');
    }

    waves.push(wave);
    wave.forEach(t => completed.add(t.id));
  }

  return waves;
}

const waves = createWaves(tasks);
```

**Display wave analysis:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Dependency Analysis
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Total tasks: 7
Execution waves: 4

Wave 1 (Parallel - 2 tasks, ~22 min):
  ├─ Task 1: Create auth API endpoint (backend) [20 min]
  └─ Task 2: Create login UI component (ui) [18 min]
     No dependencies ✓

Wave 2 (Sequential - 1 task, ~15 min):
  └─ Task 3: Connect UI to API (frontend) [15 min]
     Depends on: Tasks 1, 2

Wave 3 (Parallel - 2 tasks, ~22 min):
  ├─ Task 4: Add JWT token generation (backend) [22 min]
  └─ Task 5: Create user schema (backend) [12 min]
     Both depend on: Task 3

Wave 4 (Parallel - 2 tasks, ~25 min):
  ├─ Task 6: Write integration tests (qa) [25 min]
  └─ Task 7: Write documentation (docs) [15 min]
     Both depend on: All previous tasks

⚡ Execution Estimate:
  Sequential: 127 minutes (2h 7min)
  Parallel:   84 minutes (1h 24min)
  Speedup:    1.5x (34% time saved)

Parallelism factor: 2.5 average agents per wave
```

### Step 3.2: Create Team

```typescript
TeamCreate({
  team_name: "phase-execution",
  description: `Phase execution for ${phase_name}`,
  agent_type: "general-purpose"  // Team lead role
});
```

**Creates:**
- Team config: `~/.claude/teams/phase-execution/config.json`
- Task list: `~/.claude/tasks/phase-execution/`

**Display:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 Team Creation
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Team: phase-execution
Config: ~/.claude/teams/phase-execution/config.json
Tasks: ~/.claude/tasks/phase-execution/

Team lead: current session
Teammates: will be spawned per wave

✓ Team created successfully
```

### Step 3.3: Create Task Entries with Dependencies

```typescript
for (const task of tasks) {
  TaskCreate({
    subject: task.subject,
    description: `
Execute: ${task.subject}

Requirements:
${task.description}

Agent: ${task.agent_type}
Estimated time: ${task.estimated_time} minutes

Steps:
1. Claim this task: TaskUpdate({ taskId: "${task.id}", owner: "your-name", status: "in_progress" })
2. Execute the work
3. Run quality gates (lint, build, tests)
4. Self-review code
5. Git commit
6. Mark complete: TaskUpdate({ taskId: "${task.id}", status: "completed" })
`,
    activeForm: `Executing ${task.subject}`,
    metadata: {
      agent_type: task.agent_type,
      wave: task.wave_number,
      estimated_time: task.estimated_time
    }
  });

  // Set up dependencies
  if (task.depends_on.length > 0) {
    TaskUpdate({
      taskId: task.id,
      addBlockedBy: task.depends_on
    });
  }
}
```

**Display:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 Task List Creation
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Creating 7 task entries...
  ✓ Task 1: Create auth API endpoint
  ✓ Task 2: Create login UI component
  ✓ Task 3: Connect UI to API (blocked by: 1, 2)
  ✓ Task 4: Add JWT token generation (blocked by: 3)
  ✓ Task 5: Create user schema (blocked by: 3)
  ✓ Task 6: Write integration tests (blocked by: 1-5)
  ✓ Task 7: Write documentation (blocked by: 1-5)

All tasks created ✓
Shared task list: ~/.claude/tasks/phase-execution/
```

### Step 3.4: Execute Waves

```typescript
for (const [waveIndex, wave] of waves.entries()) {
  console.log(`\n━━━ Wave ${waveIndex + 1} (${wave.length} tasks) ━━━\n`);

  // Spawn agents for this wave
  const agents = wave.map((task, idx) => {
    const agentName = `${task.agent_type}-wave${waveIndex + 1}-${idx}`;

    return Task({
      subagent_type: task.agent_type,
      team_name: "phase-execution",
      name: agentName,
      prompt: `
You are ${agentName}, responsible for: ${task.subject}

🎯 YOUR MISSION:

1. **Claim your task:**
   TaskUpdate({ taskId: "${task.id}", owner: "${agentName}", status: "in_progress" })

2. **Read task requirements:**
   TaskGet({ taskId: "${task.id}" })

3. **Check dependencies (if any):**
   ${task.depends_on.length > 0 ? `
   Your task is blocked by: ${task.depends_on.join(', ')}

   Verify they're complete:
   TaskList()

   If not complete, wait. Check every 30 seconds.
   ` : `
   No dependencies - you can start immediately!
   `}

4. **Execute the task:**
   - Write code as specified
   - Follow project patterns (check Memory Bank, Documentation Hub)
   - Ask teammates if you need clarification (SendMessage)

5. **Run quality gates:**
   - Lint: npm run lint (or equivalent)
   - Build: npm run build (or tsc)
   - Tests: npm test (if applicable)

   ⚠️ DO NOT proceed if quality gates fail!
   Fix issues before continuing.

6. **Self-review your code:**
   - Check for bugs, edge cases, security issues
   - Verify against requirements
   - Ensure code quality

7. **Git commit:**
   git add .
   git commit -m "feat: ${task.subject}

   Co-Authored-By: ${agentName} <noreply@anthropic.com>"

8. **Mark task complete:**
   TaskUpdate({ taskId: "${task.id}", status: "completed" })

9. **Check for next task:**
   TaskList()

   If there are more unassigned, unblocked tasks, claim one.
   Otherwise, go idle.

📚 CONTEXT AVAILABLE:
- Memory Bank: memory-bank/systemPatterns.md, activeContext.md
- Documentation Hub: docs/ directory
- PM-DB: Phase Run ID from on-phase-run-start hook

🤝 PEER COMMUNICATION:
- Send messages to teammates: SendMessage({ type: "message", recipient: "teammate-name", ... })
- Teammates: ${JSON.stringify(wave.map(t => t.agent_type))}

⚠️ IMPORTANT:
- Quality gates are HARD BLOCKS - fix all issues before committing
- Git commits must happen AFTER quality gates pass
- If blocked on dependencies, wait - DO NOT skip
- If you encounter errors, don't give up - debug and fix
`,
      description: `Execute ${task.subject}`,
      model: "sonnet"  // Use Sonnet for task execution (Haiku too weak)
    });
  });

  // Wait for all agents in this wave to complete
  console.log(`\nWave ${waveIndex + 1} agents spawned:`, agents.map(a => a.name));
  console.log(`Waiting for ${wave.length} tasks to complete...`);

  // Poll task status until all complete
  const waveTaskIds = wave.map(t => t.id);
  let allComplete = false;

  while (!allComplete) {
    await sleep(10000);  // Wait 10 seconds

    const taskList = TaskList();
    const waveTasks = taskList.filter(t => waveTaskIds.includes(t.id));

    allComplete = waveTasks.every(t => t.status === 'completed');

    // Display progress
    const completedCount = waveTasks.filter(t => t.status === 'completed').length;
    console.log(`Progress: ${completedCount}/${wave.length} tasks complete in Wave ${waveIndex + 1}`);

    // Check for errors
    const failed = waveTasks.filter(t => t.status === 'failed');
    if (failed.length > 0) {
      console.error(`❌ ${failed.length} tasks failed in Wave ${waveIndex + 1}:`);
      failed.forEach(t => console.error(`  - ${t.subject}`));
      throw new Error(`Wave ${waveIndex + 1} execution failed`);
    }
  }

  console.log(`✅ Wave ${waveIndex + 1} complete!\n`);
}
```

**Example output:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
━━━ Wave 1 (2 tasks) ━━━
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Spawning agents:
  ✓ nextjs-backend-developer-wave1-0
  ✓ ui-developer-wave1-1

[backend-wave1-0] Claiming Task 1...
[backend-wave1-0] Task 1: Create auth API endpoint
  ├─ Owner: backend-wave1-0
  ├─ Status: in_progress
  ├─ No dependencies, starting immediately
  └─ Writing src/api/auth/route.ts...

[ui-wave1-1] Claiming Task 2...
[ui-wave1-1] Task 2: Create login UI component
  ├─ Owner: ui-wave1-1
  ├─ Status: in_progress
  ├─ No dependencies, starting immediately
  └─ Writing src/components/LoginForm.tsx...

[Agents working in parallel...]

Progress: 0/2 tasks complete in Wave 1
Progress: 0/2 tasks complete in Wave 1
Progress: 1/2 tasks complete in Wave 1

[backend-wave1-0] Quality gates:
  ├─ Lint: npm run lint → 0 errors ✓
  ├─ Build: npm run build → success ✓
  └─ Tests: npm test → 4/4 passing ✓

[backend-wave1-0] Git commit:
  feat: Create auth API endpoint

  Co-Authored-By: backend-wave1-0 <noreply@anthropic.com>

[backend-wave1-0] Task 1 complete! (20 min)
[backend-wave1-0] Checking for next task...
[backend-wave1-0] No unblocked tasks available, going idle

Progress: 2/2 tasks complete in Wave 1

[ui-wave1-1] Task 2 complete! (18 min)
[ui-wave1-1] Going idle

✅ Wave 1 complete in 22 minutes (longest task)
   (Sequential would have taken 38 minutes)
```

### Step 3.5: Verify All Tasks Complete

```typescript
const taskList = TaskList();
const incomplete = taskList.filter(t => t.status !== 'completed');

if (incomplete.length > 0) {
  console.error(`❌ ${incomplete.length} tasks incomplete:`);
  incomplete.forEach(t => {
    console.error(`  - Task ${t.id}: ${t.subject}`);
    console.error(`    Status: ${t.status}`);
    console.error(`    Owner: ${t.owner || 'unassigned'}`);
  });
  throw new Error('Phase execution incomplete');
}

console.log(`\n✅ All ${tasks.length} tasks completed!\n`);
```

### Step 3.6: Shut Down Team

```typescript
// Read team config to get all members
const teamConfig = Read(`~/.claude/teams/phase-execution/config.json`);
const members = JSON.parse(teamConfig).members;

console.log(`\n━━━ Shutting Down Team (${members.length} agents) ━━━\n`);

// Request shutdown for all teammates
for (const member of members) {
  SendMessage({
    type: "shutdown_request",
    recipient: member.name,
    content: "Phase execution complete, all tasks finished. Thank you for your work!"
  });

  console.log(`  → Requested shutdown: ${member.name}`);
}

// Wait for confirmations (agents will respond with shutdown_response)
// System handles this automatically

await sleep(5000);  // Give agents time to shut down

// Clean up team resources
TeamDelete();

console.log(`\n✅ Team shutdown complete`);
console.log(`✅ Team resources cleaned up`);
```

---

## Part 4: Task Updates & Commits

**If USE_TEAM_MODE == true:**

Task updates and git commits are handled automatically by each agent during execution (Step 3.4).

**Display summary:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📝 Git History Summary
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

7 commits created by agents:
  7a8b9c0 feat: Write documentation (docs-wave4-1)
  6a7b8c9 feat: Write integration tests (qa-wave4-0)
  5a6b7c8 feat: Create user schema (backend-wave3-1)
  4a5b6c7 feat: Add JWT token generation (backend-wave3-0)
  3a4b5c6 feat: Connect UI to API (frontend-wave2-0)
  2a3b4c5 feat: Create login UI component (ui-wave1-1)
  1a2b3c4 feat: Create auth API endpoint (backend-wave1-0)

All commits co-authored by respective agents ✓
```

---

## Part 5: Phase Closeout

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Phase Complete! (Team Mode)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Tasks: 7/7 completed
Duration: 84 minutes (1h 24min)
Quality gates: 7/7 passed
Git commits: 7 commits
Test coverage: 89%

⚡ Parallel Execution Breakdown:
  Wave 1: 22 min (2 agents in parallel)
  Wave 2: 15 min (1 agent)
  Wave 3: 22 min (2 agents in parallel)
  Wave 4: 25 min (2 agents in parallel)

⚡ Speedup Analysis:
  Sequential estimate: 127 minutes
  Actual (parallel): 84 minutes
  Time saved: 43 minutes (34%)
  Speedup: 1.5x

Agent Utilization:
  backend-wave1-0: 20 min (Task 1)
  ui-wave1-1: 18 min (Task 2)
  frontend-wave2-0: 15 min (Task 3)
  backend-wave3-0: 22 min (Task 4)
  backend-wave3-1: 12 min (Task 5)
  qa-wave4-0: 25 min (Task 6)
  docs-wave4-1: 15 min (Task 7)

Peer Communication:
  ├─ docs-wave4-1 → backend-wave3-0: "JWT expiry time?" (1 message)
  └─ ui-wave1-1 → backend-wave1-0: "API endpoint path?" (1 message)

Quality Summary:
  Lint errors: 0
  Build errors: 0
  Test failures: 0
  Code review issues: 0

Next steps:
  - View metrics: /pm-db dashboard
  - Update Memory Bank: /memory-bank-sync
  - View phase summary: ./job-queue/feature-{name}/planning/phase-structure/phase-summary.md
```

---

## Fallback: Sequential Execution

**If USE_TEAM_MODE == false:**

Execute tasks sequentially using the original start-phase-execute logic:

```typescript
for (const task of tasks) {
  console.log(`\n━━━ Task ${task.id}/${tasks.length}: ${task.subject} ━━━\n`);

  // Call agent directly (no team)
  Task({
    subagent_type: task.agent_type,
    prompt: `Execute ${task.subject}...`,
    description: `Execute ${task.subject}`
  });

  // Wait for completion
  // Run quality gates
  // Git commit
  // Continue to next task
}
```

---

## Error Handling

### Team Creation Failure

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
  2. Retry with: /start-phase-execute ./tasks.md --team
  3. Or fallback: /start-phase-execute ./tasks.md --sequential
```

### Agent Spawn Failure

```
❌ Failed to spawn agent: backend-wave3-1

Reason: Insufficient resources or tmux not available

Recovery:
  1. Check tmux: which tmux
  2. Reduce parallelism (use sequential mode)
  3. Or spawn replacement agent manually
```

### Task Deadlock

```
⚠️ Potential deadlock detected in Wave 3

Task 4 blocked by: Task 3 (in_progress for 45 min)
Task 5 blocked by: Task 3 (in_progress for 45 min)

Investigation:
  - Check agent frontend-wave2-0 status
  - Review logs for errors
  - Task 3 may be stuck

Recovery:
  1. Message agent: SendMessage({ recipient: "frontend-wave2-0", ... })
  2. Or mark Task 3 complete manually if work is done
  3. Or spawn replacement agent
```

### Quality Gate Failure

```
❌ Quality gate failed for Task 4 (backend-wave3-0)

Lint errors: 2
  - src/lib/jwt.ts:15 - unused variable 'token'
  - src/lib/jwt.ts:23 - missing return type

Recovery (automatic):
  Agent will:
  1. Fix lint errors
  2. Re-run quality gates
  3. Retry commit if gates pass

No manual intervention needed ✓
```

---

## Best Practices

### From Claude Code Documentation

1. **Give teammates enough context**
   - Teammates don't inherit conversation history
   - Include task details, file locations, API contracts in spawn prompt

2. **Size tasks appropriately**
   - Too small: coordination overhead exceeds benefit
   - Too large: risk of wasted effort
   - Just right: self-contained units (function, test file, component)

3. **Avoid file conflicts**
   - Break work so each teammate owns different files
   - If two agents edit same file, overwrites can occur

4. **Monitor and steer**
   - Check on progress
   - Redirect approaches that aren't working
   - Synthesize findings

5. **Quality gates with hooks**
   - Use `TeammateIdle` hook: exit code 2 sends feedback
   - Use `TaskCompleted` hook: exit code 2 prevents completion

---

## Token Usage

**Sequential mode:**
- ~150k tokens (single agent context)
- 127 minutes execution time

**Team mode (7 tasks, 7 agents):**
- ~450k tokens (7 separate contexts)
- 84 minutes execution time
- 3x more tokens, but 1.5x faster

**When to use team mode:**
- ✅ Complex features (2+ hours sequential)
- ✅ Multiple independent modules
- ✅ Time is more valuable than cost
- ❌ Simple changes (< 1 hour sequential)
- ❌ Routine maintenance
- ❌ Single-file modifications

---

## Usage Examples

### Auto-Detect Mode (Default)

```bash
/start-phase-execute ./job-queue/feature-auth/task-list.md

# System detects 7 tasks → uses team mode
# Output: "⚡ Team mode: ENABLED (auto-detected 7 tasks)"
```

### Force Team Mode

```bash
/start-phase-execute ./job-queue/feature-profile/task-list.md --team

# Even if < 7 tasks, uses team mode
```

### Force Sequential Mode

```bash
/start-phase-execute ./job-queue/feature-logout/task-list.md --sequential

# Even if 7+ tasks, uses sequential mode
```

---

## Integration with Hooks

### on-phase-run-start Hook

```bash
# Hook gets phase_run_id from PM-DB
# Pass to team members via spawn prompt
```

### on-task-run-start Hook

```bash
# Called by each agent before starting task
# Gets task_run_id from PM-DB
```

### on-task-run-complete Hook

```bash
# Called by each agent after task complete
# Updates PM-DB with duration, exit code
```

### TeammateIdle Hook

```bash
# Called when agent goes idle
# Can send feedback to keep agent working
# Exit code 2 = send feedback and continue
```

### TaskCompleted Hook

```bash
# Called when agent marks task complete
# Can prevent completion if validation fails
# Exit code 2 = reject completion with feedback
```

---

## Next Steps

After implementing this skill:

1. **Test with simple feature** (3-5 tasks)
2. **Test with complex feature** (10+ tasks)
3. **Measure real speedups**
4. **Refine wave detection logic**
5. **Add to /feature-new as option**
6. **Document in README**
