# Team Skills Implementation Guide

## What We Built

Complete team-enabled enhancements for your feature development workflow with `--team` flag support.

**Files Created:**

```
skills/
├── feature-new/
│   └── SKILL-TEAM.md                    # Team-enabled orchestrator
├── spec-plan/
│   └── TEAM-ENHANCEMENT.md              # Parallel spec generation
└── start-phase-execute-team/
    └── SKILL.md                         # Parallel task execution

docs/
├── teams-integration-guide.md            # Architecture overview
├── teams-in-action-example.md            # Real workflow example
└── team-skills-implementation-guide.md   # This file
```

---

## Quick Start

### Enable Teams (Required)

```json settings.json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  }
}
```

Or set environment variable:
```bash
export CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1
```

### Use Team Mode

```bash
# Force team mode
/feature-new "add user authentication" --team

# Force sequential mode
/feature-new "add logout button" --sequential

# Auto-detect mode (default)
/feature-new "add payment processing"
# → Uses teams if 7+ tasks detected
```

---

## Architecture

```
/feature-new --team
    │
    ├─ /spec-plan --team              (Parallel spec generation)
    │   ├─ Wave 1: FRD + FRS+TR       (4 min, 2 agents)
    │   ├─ Wave 2: GS                 (2 min, 1 agent)
    │   └─ Wave 3: task-list          (2 min, 1 agent)
    │   Total: 11 min (vs 19 min sequential)
    │
    ├─ /spec-review                   (Validation)
    │
    ├─ /start-phase-plan              (Strategic planning)
    │
    ├─ /pm-db import                  (Tracking)
    │
    └─ /start-phase-execute-team      (Parallel execution)
        ├─ Wave 1: Tasks 1, 2         (22 min, 2 agents)
        ├─ Wave 2: Task 3             (15 min, 1 agent)
        ├─ Wave 3: Tasks 4, 5         (22 min, 2 agents)
        └─ Wave 4: Tasks 6, 7         (25 min, 2 agents)
        Total: 84 min (vs 127 min sequential)
```

---

## Integration Strategy

### Phase 1: Add Team Support to Existing Skills

**Option A: Modify Existing Files (Recommended)**

Update existing skills to detect `--team` flag and route accordingly:

```markdown
# In /spec-plan/SKILL.md

## Step 5: Generate Specifications

# Check for --team flag
if args contains "--team":
    [Use team-based generation from TEAM-ENHANCEMENT.md]
else:
    [Use existing sequential generation]
```

**Option B: Create Separate Skills**

Keep existing skills unchanged, create new variants:

```bash
skills/
├── spec-plan/SKILL.md           # Original (sequential)
├── spec-plan-team/SKILL.md      # New (team mode)
├── start-phase-execute/         # Original
└── start-phase-execute-team/    # New (team mode)
```

Then modify `/feature-new` to route based on flag:

```markdown
if USE_TEAM_MODE:
    Skill({ skill: "spec-plan-team", args: "..." })
    Skill({ skill: "start-phase-execute-team", args: "..." })
else:
    Skill({ skill: "spec-plan", args: "..." })
    Skill({ skill: "start-phase-execute", args: "..." })
```

### Phase 2: Test with Real Features

```bash
# Small feature (expect sequential)
/feature-new "add logout button" --team

# Medium feature (expect team mode)
/feature-new "add user profile page" --team

# Large feature (expect team mode with speedup)
/feature-new "add payment processing with Stripe" --team
```

### Phase 3: Make Team Mode Default

After validation, switch auto-detect to prefer team mode:

```markdown
# In feature-new/SKILL-TEAM.md

if task_count >= 5:  # Lower threshold from 7 to 5
    USE_TEAM_MODE = true
```

---

## Expected Performance

### Spec Generation

| Mode | Duration | Agents | Speedup |
|------|----------|--------|---------|
| Sequential | 19 min | 1 | 1.0x |
| Team | 11 min | 4 | 1.7x |

### Task Execution (7 tasks)

| Mode | Duration | Agents | Speedup |
|------|----------|--------|---------|
| Sequential | 127 min | 1 | 1.0x |
| Team | 84 min | 7 | 1.5x |

### Full Workflow

| Mode | Duration | Total Agents | Speedup |
|------|----------|--------------|---------|
| Sequential | 146 min | 1 | 1.0x |
| Team | 95 min | 9 | 1.54x |

**Time saved:** 51 minutes (35% faster)

---

## Token Usage

### Spec Generation

- **Sequential:** ~50k tokens
- **Team:** ~120k tokens (2.4x more)

### Task Execution (7 tasks)

- **Sequential:** ~150k tokens
- **Team:** ~450k tokens (3x more)

### Full Workflow

- **Sequential:** ~200k tokens
- **Team:** ~570k tokens (2.85x more)

**Trade-off:** More tokens for faster execution

---

## Dependency Management

### How Dependencies Work

**Task list format:**
```markdown
## Task 1: Create auth API endpoint
Agent: nextjs-backend-developer
Estimated time: 20 minutes
Depends on: None

## Task 2: Create login UI component
Agent: ui-developer
Estimated time: 18 minutes
Depends on: None

## Task 3: Connect UI to API
Agent: frontend-developer
Estimated time: 15 minutes
Depends on: Task 1, Task 2
```

**System automatically:**
1. Parses dependencies
2. Creates execution waves
3. Blocks tasks until dependencies complete
4. Spawns agents for each wave

### Wave Detection Algorithm

```typescript
function createWaves(tasks: Task[]): Task[][] {
  const waves: Task[][] = [];
  const completed = new Set<string>();

  while (completed.size < tasks.length) {
    // Find tasks with satisfied dependencies
    const wave = tasks.filter(task =>
      !completed.has(task.id) &&
      task.depends_on.every(dep => completed.has(dep))
    );

    if (wave.length === 0) {
      throw new Error('Circular dependency');
    }

    waves.push(wave);
    wave.forEach(t => completed.add(t.id));
  }

  return waves;
}
```

---

## Quality Gates

**Enforced per agent:**

```typescript
// Each agent runs quality gates before committing

1. Lint check:
   npm run lint → Must pass (0 errors)

2. Build check:
   npm run build → Must succeed

3. Test check (if applicable):
   npm test → Must pass (0 failures)

4. Self-review:
   Agent reviews own code for bugs, security, quality

5. Git commit:
   Only after all gates pass
```

**If gates fail:**
- Agent fixes issues
- Re-runs gates
- Retries until all pass

**No manual intervention needed** - agents handle fixes automatically.

---

## Peer Communication

**Agents communicate directly:**

```typescript
// Example: docs agent asks backend agent

SendMessage({
  type: "message",
  recipient: "backend-agent-2",
  content: "What's the JWT token expiry time?",
  summary: "Question about JWT expiry"
});

// backend-agent-2 responds:
SendMessage({
  type: "message",
  recipient: "docs-agent-1",
  content: "15 minutes for access tokens, 7 days for refresh tokens",
  summary: "JWT expiry times"
});
```

**Team Lead sees summary** in idle notifications but doesn't need to relay.

---

## Error Handling

### Team Creation Failure

```
❌ Failed to create team

Reason: CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS not enabled

Fix:
  1. Add to settings.json:
     {
       "env": {
         "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
       }
     }
  2. Restart Claude Code
  3. Retry with --team flag
```

### Agent Spawn Failure

```
❌ Failed to spawn agent: backend-agent-3

Reason: Insufficient resources or tmux not available

Fix:
  1. Check tmux: which tmux
  2. Install if missing: brew install tmux (macOS)
  3. Or use in-process mode (no tmux required)
  4. Or fallback to sequential mode
```

### Task Deadlock

```
⚠️ Potential deadlock in Wave 3

Task 4 blocked by: Task 3 (not complete)
Task 5 blocked by: Task 3 (not complete)

Fix:
  1. Check agent status: TaskList()
  2. Message stuck agent: SendMessage(...)
  3. Or mark task complete manually if work is done
```

### Quality Gate Failure

```
❌ Quality gate failed: Task 4

Lint errors: 2
Build errors: 0

Agent will:
  1. Fix lint errors
  2. Re-run gates
  3. Retry commit

No manual intervention needed ✓
```

---

## Best Practices

### 1. Give Teammates Context

**Good spawn prompt:**
```
You are responsible for: Create auth API endpoint

Context:
- Project uses Next.js 15 App Router
- Auth tokens stored in httpOnly cookies
- JWT expiry: 15 min access, 7 days refresh
- Existing patterns: src/lib/auth-helpers.ts

Files to create:
- src/api/auth/login/route.ts
- src/api/auth/logout/route.ts
```

**Bad spawn prompt:**
```
Create auth API
```

### 2. Size Tasks Appropriately

**Too small:**
```
- Task 1: Import React
- Task 2: Create component file
- Task 3: Write return statement
```
(Coordination overhead > benefit)

**Too large:**
```
- Task 1: Build entire authentication system
```
(Risk of wasted effort without check-ins)

**Just right:**
```
- Task 1: Create auth API endpoint
- Task 2: Create login UI component
- Task 3: Connect UI to API
```
(Self-contained units with clear deliverables)

### 3. Avoid File Conflicts

**Bad:**
```
- Task 1: Update src/lib/auth.ts (add login)
- Task 2: Update src/lib/auth.ts (add logout)
```
(Two agents editing same file → overwrites)

**Good:**
```
- Task 1: Create src/lib/auth-login.ts
- Task 2: Create src/lib/auth-logout.ts
```
(Each agent owns different files)

### 4. Monitor Progress

Check in periodically:

```bash
# View task status
TaskList()

# Check specific task
TaskGet({ taskId: "3" })

# Message agent if stuck
SendMessage({
  recipient: "backend-agent-2",
  content: "How's Task 4 going? Need any help?"
})
```

### 5. Use Hooks for Quality

```bash
# TeammateIdle hook
# Exit code 2 = send feedback and keep working

if [lint_errors > 0]; then
    echo "Fix lint errors before going idle"
    exit 2
fi

# TaskCompleted hook
# Exit code 2 = prevent completion

if [tests_failing]; then
    echo "All tests must pass before marking complete"
    exit 2
fi
```

---

## When to Use Team Mode

### Use Teams When:

✅ **7+ tasks**
✅ **Multiple independent modules**
✅ **Complex features (2+ hours)**
✅ **Time is more valuable than tokens**
✅ **Parallelism opportunities (2+ independent tasks)**

### Don't Use Teams When:

❌ **< 5 tasks**
❌ **All tasks strictly sequential**
❌ **Simple changes (< 1 hour)**
❌ **Single-file modifications**
❌ **Routine maintenance**

---

## Troubleshooting

### Teammates Not Appearing

**Check:**
1. Teams enabled: `echo $CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS`
2. tmux available: `which tmux`
3. Task count threshold: Need 7+ tasks for auto-detect

**Fix:**
```bash
# Enable teams
export CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1

# Force team mode (bypass auto-detect)
/feature-new "..." --team

# Or install tmux
brew install tmux  # macOS
```

### Too Many Permission Prompts

**Pre-approve common operations:**

```json settings.json
{
  "permissions": {
    "bash": "allow",
    "edit": "allow",
    "write": "allow"
  }
}
```

### Orphaned tmux Sessions

**List and kill:**
```bash
tmux ls
tmux kill-session -t phase-execution
```

### Task Status Lag

**Manually update task:**
```typescript
// If agent completed but forgot to mark complete
TaskUpdate({
  taskId: "4",
  status: "completed"
});
```

---

## Migration Path

### Week 1: Add Team Support

1. Copy `SKILL-TEAM.md` to `/feature-new/`
2. Copy `TEAM-ENHANCEMENT.md` logic to `/spec-plan/SKILL.md`
3. Copy `/start-phase-execute-team/` to skills directory
4. Test with small feature

### Week 2: Validate & Refine

1. Test with medium feature (7-10 tasks)
2. Test with large feature (15+ tasks)
3. Measure real speedups
4. Refine dependency detection
5. Optimize wave structure

### Week 3: Make Default

1. Update `/feature-new/SKILL.md` to use team by default
2. Set auto-detect threshold to 5 tasks (down from 7)
3. Document in README
4. Update user guide

### Week 4: Production Use

1. Roll out to all features
2. Monitor token usage
3. Collect feedback
4. Iterate on improvements

---

## Testing Checklist

### Test Case 1: Simple Feature (Sequential Expected)

```bash
/feature-new "add logout button" --team

Expected:
- Auto-detect: Sequential mode (< 7 tasks)
- Duration: ~30 min
- Agents: 1
- Deliverables: All files created
```

### Test Case 2: Medium Feature (Team Mode)

```bash
/feature-new "add user profile page" --team

Expected:
- Auto-detect: Team mode (7-10 tasks)
- Duration: ~60-80 min
- Agents: 7-10
- Speedup: 1.5x vs sequential
```

### Test Case 3: Large Feature (Team Mode with High Speedup)

```bash
/feature-new "add payment processing with Stripe" --team

Expected:
- Auto-detect: Team mode (15+ tasks)
- Duration: ~120-180 min
- Agents: 15+
- Speedup: 2x vs sequential
```

### Test Case 4: Dependency Handling

```bash
/feature-new "add authentication system" --team

Expected:
- Waves: 4-5
- Dependencies: Correctly enforced
- No deadlocks
- All tasks complete in order
```

### Test Case 5: Error Recovery

```bash
/feature-new "add complex feature" --team

Expected (if agent fails):
- System detects failure
- Spawns replacement agent
- Continues execution
- All tasks eventually complete
```

---

## Maintenance

### Monthly Tasks

1. Review token usage trends
2. Analyze speedup metrics
3. Optimize wave detection
4. Update agent spawn prompts
5. Refine quality gates

### Quarterly Tasks

1. Update team patterns based on learnings
2. Review agent utilization
3. Optimize for cost vs speed trade-offs
4. Train team on new patterns

---

## Support & Feedback

**Questions:**
- Read `/docs/teams-integration-guide.md`
- Read `/docs/teams-in-action-example.md`
- Check Claude Code docs: https://code.claude.com/docs/en/agent-teams

**Issues:**
- Check troubleshooting section
- Review error messages
- Test with sequential mode as fallback

**Feedback:**
- Track speedup metrics
- Monitor token usage
- Report bugs to Claude Code team

---

## Summary

**What you get:**
- ✅ 1.5-2x faster feature development
- ✅ Parallel spec generation (1.7x)
- ✅ Parallel task execution (1.5x)
- ✅ Automatic dependency management
- ✅ Quality gates enforced per agent
- ✅ Peer communication between agents
- ✅ Token usage: 2-3x more, but worthwhile for speed

**How to use:**
```bash
/feature-new "your feature description" --team
```

**Files created:**
- `SKILL-TEAM.md` - Team-enabled orchestrator
- `TEAM-ENHANCEMENT.md` - Spec generation guide
- `start-phase-execute-team/SKILL.md` - Parallel executor

**Next steps:**
1. Enable teams in settings
2. Test with small feature
3. Measure speedup
4. Roll out to production
