# Teams in Action: Real Example

## Scenario: Add User Authentication Feature

**Command:** `/feature-new "add user authentication with JWT"`

---

## Current Behavior (Sequential)

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚀 Feature New: User Authentication
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Step 1/6: Documentation initialized
✅ Step 2/6: Specification created
   Location: ./job-queue/feature-auth/docs/
   Files: FRD.md, FRS.md, GS.md, TR.md, task-list.md
✅ Step 3/6: Specification reviewed (Health: 92/100)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👤 CHECKPOINT 1: Review Specifications
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[Shows FRD, FRS, GS, TR summaries]

Options: approve / revise / cancel
> approve

✅ Step 4/6: Strategic plan approved

Task List:
  1. Create auth API endpoint (nextjs-backend) - 20 min
  2. Create login UI component (ui-developer) - 18 min
  3. Connect UI to API (frontend-developer) - 15 min
  4. Add JWT token generation (nextjs-backend) - 22 min
  5. Create user database schema (nextjs-backend) - 12 min
  6. Write integration tests (qa-engineer) - 25 min
  7. Write documentation (technical-writer) - 15 min

Estimated time: 127 minutes (2h 7min)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👤 CHECKPOINT 2: Approve Execution Plan
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Options: approve / revise / cancel
> approve

✅ Step 5/6: Imported to PM-DB
   Phase Run ID: 42

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚙️  Step 6/6: Executing Phase (Sequential Mode)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[Task 1/7] Create auth API endpoint
  Agent: nextjs-backend-developer
  ├─ Writing src/api/auth/route.ts... ✓
  ├─ Quality gate: Lint ✓ Build ✓
  ├─ Code review: ✓ Passed
  ├─ Git commit: feat: add auth API endpoint
  └─ Duration: 20 minutes

[Task 2/7] Create login UI component
  Agent: ui-developer
  ├─ Writing src/components/LoginForm.tsx... ✓
  ├─ Quality gate: Lint ✓ Build ✓
  ├─ Code review: ✓ Passed
  ├─ Git commit: feat: add login UI component
  └─ Duration: 18 minutes

[Task 3/7] Connect UI to API
  Agent: frontend-developer
  ├─ Writing src/lib/auth.ts... ✓
  ├─ Quality gate: Lint ✓ Build ✓
  ├─ Code review: ✓ Passed
  ├─ Git commit: feat: connect login UI to API
  └─ Duration: 15 minutes

[... continues for all 7 tasks ...]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Phase Complete!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Tasks: 7/7 completed
Duration: 127 minutes
Quality gates: 7/7 passed
Git commits: 7 commits

Total time: 2 hours 7 minutes
```

---

## Enhanced Behavior (with Teams)

**Command:** `/feature-new "add user authentication with JWT" --team`

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚀 Feature New: User Authentication (Parallel Mode)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Step 1/6: Documentation initialized

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚡ Step 2/6: Parallel Spec Generation
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

✅ Step 2/6: Specification created (11 min vs 19 min)
   Location: ./job-queue/feature-auth/docs/
   Speedup: 1.7x faster

✅ Step 3/6: Specification reviewed (Health: 92/100)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👤 CHECKPOINT 1: Review Specifications
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[Shows FRD, FRS, GS, TR summaries]

Options: approve / revise / cancel
> approve

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Step 4/6: Strategic Plan with Parallel Analysis
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Dependency Analysis:
  ├─ 7 tasks detected
  ├─ 4 execution waves identified
  └─ 2.5x parallelism opportunity

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

Estimated time:
  Sequential: 127 minutes (2h 7min)
  Parallel:   84 minutes (1h 24min)
  Speedup:    1.5x (34% time saved)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👤 CHECKPOINT 2: Approve Parallel Execution Plan
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Options: approve / revise / cancel / use-sequential
> approve

✅ Step 5/6: Imported to PM-DB
   Phase Run ID: 42
   Execution mode: parallel

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚡ Step 6/6: Parallel Phase Execution
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Team: phase-execution (7 agents)

━━━ Wave 1 (2 tasks) ━━━

[backend-agent-1] Task 1: Create auth API endpoint
  ├─ Claimed task (owner: backend-agent-1) ✓
  ├─ Writing src/api/auth/route.ts...

[ui-agent-1] Task 2: Create login UI component
  ├─ Claimed task (owner: ui-agent-1) ✓
  ├─ Writing src/components/LoginForm.tsx...

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

━━━ Wave 2 (1 task) ━━━

[frontend-agent-1] Task 3: Connect UI to API
  ├─ Claimed task (owner: frontend-agent-1) ✓
  ├─ Dependencies satisfied: Tasks 1, 2 ✓
  ├─ Writing src/lib/auth.ts...
  ├─ Quality gate: Lint ✓ Build ✓
  ├─ Code review: ✓ Passed
  ├─ Git commit: feat: connect login UI to API
  └─ Task 3 complete! (15 minutes)

✅ Wave 2 complete in 15 minutes

━━━ Wave 3 (2 tasks) ━━━

[backend-agent-2] Task 4: Add JWT token generation
  ├─ Claimed task (owner: backend-agent-2) ✓
  ├─ Dependencies satisfied: Task 3 ✓

[backend-agent-3] Task 5: Create user database schema
  ├─ Claimed task (owner: backend-agent-3) ✓
  ├─ Dependencies satisfied: Task 3 ✓

[Agents working in parallel...]

[backend-agent-2] Task 4 complete! (22 minutes)
[backend-agent-3] Task 5 complete! (12 minutes)

✅ Wave 3 complete in 22 minutes (longest task)
   (Sequential would have taken 34 minutes)

━━━ Wave 4 (2 tasks) ━━━

[qa-agent-1] Task 6: Write integration tests
  ├─ Claimed task (owner: qa-agent-1) ✓
  ├─ Dependencies satisfied: All previous tasks ✓
  ├─ Writing tests/integration/auth.test.ts...

[docs-agent-1] Task 7: Write documentation
  ├─ Claimed task (owner: docs-agent-1) ✓
  ├─ Dependencies satisfied: All previous tasks ✓
  ├─ SendMessage to backend-agent-2: "What's the JWT expiry time?" ✓
  ├─ [backend-agent-2 responds: "15 minutes access, 7 days refresh"]
  ├─ Writing docs/authentication.md...

[Agents working in parallel...]

[qa-agent-1] Task 6 progress:
  ├─ Tests written ✓
  ├─ All tests passing (12/12) ✓
  ├─ Quality gate: Lint ✓ Build ✓
  ├─ Git commit: test: add auth integration tests
  └─ Task 6 complete! (25 minutes)

[docs-agent-1] Task 7 progress:
  ├─ Documentation written ✓
  ├─ Quality gate: Lint ✓
  ├─ Git commit: docs: add authentication guide
  └─ Task 7 complete! (15 minutes)

✅ Wave 4 complete in 25 minutes (longest task)
   (Sequential would have taken 40 minutes)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔄 Shutting Down Team
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Requesting shutdown:
  ├─ backend-agent-1 ✓
  ├─ ui-agent-1 ✓
  ├─ frontend-agent-1 ✓
  ├─ backend-agent-2 ✓
  ├─ backend-agent-3 ✓
  ├─ qa-agent-1 ✓
  └─ docs-agent-1 ✓

Team shutdown complete ✓

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

Git History:
  7a8b9c0 docs: add authentication guide
  6a7b8c9 test: add auth integration tests
  5a6b7c8 feat: add user database schema
  4a5b6c7 feat: add JWT token generation
  3a4b5c6 feat: connect login UI to API
  2a3b4c5 feat: add login UI component
  1a2b3c4 feat: add auth API endpoint

Next steps:
  1. Review changes: git log --oneline
  2. Test locally: npm run dev
  3. Run tests: npm test
  4. Update docs: /memory-bank-sync

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Total Workflow Time
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Sequential mode: 146 minutes (2h 26min)
  ├─ Spec generation: 19 min
  └─ Task execution: 127 min

Parallel mode: 95 minutes (1h 35min)
  ├─ Spec generation: 11 min (1.7x faster)
  └─ Task execution: 84 min (1.5x faster)

Total time saved: 51 minutes (35%)
Overall speedup: 1.54x
```

---

## Key Observations

### 1. Automatic Dependency Management

Agents automatically wait for dependencies:
```
[frontend-agent-1] Checking dependencies for Task 3...
  ├─ Task 1 (auth API): completed ✓
  ├─ Task 2 (login UI): completed ✓
  └─ Dependencies satisfied, starting work...
```

### 2. Peer Communication

Agents communicate directly without Team Lead intervention:
```
[docs-agent-1 → backend-agent-2] "What's the JWT expiry time?"
[backend-agent-2 → docs-agent-1] "15 minutes access, 7 days refresh"

(Team Lead sees summary in idle notification but doesn't relay)
```

### 3. Quality Gates Still Enforced

Each agent runs quality gates independently:
```
[backend-agent-2] Running quality gates...
  ├─ Lint: 0 errors ✓
  ├─ Build: success ✓
  ├─ Tests: 4/4 passing ✓
  └─ Quality gate passed!
```

### 4. Progress Visibility

Real-time updates from all agents:
```
[11:23] backend-agent-1: Writing src/api/auth/route.ts
[11:24] ui-agent-1: Writing src/components/LoginForm.tsx
[11:35] backend-agent-1: Quality gate passed, committing...
[11:37] ui-agent-1: Quality gate passed, committing...
[11:38] backend-agent-1: Task 1 complete, going idle
[11:39] ui-agent-1: Task 2 complete, going idle
```

---

## User Experience Differences

### Sequential (Current)

**Pros:**
- ✅ Simple mental model
- ✅ Predictable execution order
- ✅ Easy to debug (linear flow)

**Cons:**
- ❌ Slower (all tasks sequential)
- ❌ No parallelization
- ❌ Single point of failure (one task blocks all)

### Parallel (with Teams)

**Pros:**
- ✅ Faster (34-50% speedup)
- ✅ Better resource utilization
- ✅ Isolated failures (one task doesn't block others)
- ✅ Quality gates still enforced per task

**Cons:**
- ❌ More complex (waves, dependencies)
- ❌ Requires dependency analysis
- ❌ Slightly higher overhead (team setup/teardown)

---

## When to Use Each Mode

### Use Sequential When:
- ❌ < 5 tasks
- ❌ All tasks strictly sequential
- ❌ Simple, quick feature
- ❌ Debugging failed execution

### Use Parallel When:
- ✅ 7+ tasks
- ✅ Graph has parallelism (2+ independent tasks)
- ✅ Feature takes 2+ hours
- ✅ Want maximum speed

---

## How to Enable

### Auto-detect (Recommended)

```bash
# System automatically chooses based on task count & dependencies
/feature-new "add authentication"

# For 7+ tasks with parallelism → uses teams
# For < 7 tasks → uses sequential
```

### Explicit Mode

```bash
# Force parallel
/feature-new "add authentication" --team

# Force sequential
/feature-new "add authentication" --sequential
```

### Per-Step Control

```bash
# Sequential spec, parallel execution
/feature-new "add authentication" --spec-mode=sequential --exec-mode=parallel

# Parallel spec, sequential execution
/feature-new "add authentication" --spec-mode=parallel --exec-mode=sequential
```

---

## Summary

**Time savings example (7 tasks):**
- Sequential: 146 min (2h 26min)
- Parallel: 95 min (1h 35min)
- Savings: 51 min (35% faster)

**For larger features (15 tasks):**
- Sequential: 360 min (6h)
- Parallel: 180 min (3h)
- Savings: 180 min (50% faster)

**Quality maintained:**
- ✅ All quality gates enforced
- ✅ All code reviews performed
- ✅ All git commits created
- ✅ All tests passing

The only difference is **speed through parallelization**!
