# Teams vs. Manual: Concrete Example

## The Task

**Build a remote control system for Claude Code with:**
- PTY server (Node.js + WebSocket)
- Browser client (xterm.js)
- Agent API (programmatic control)
- Integration tests
- Documentation

---

## Approach 1: Manual (Traditional)

**Time:** ~6-8 hours sequential

```bash
# You manually build each component sequentially

# Step 1: Build PTY server (2 hours)
claude code
> "Build a Node.js PTY server with WebSocket support..."
> [Write server code]
> [Test WebSocket connection]
> [Debug issues]
> [Git commit]

# Step 2: Build browser client (1.5 hours)
> "Build an xterm.js browser client that connects to the server..."
> [Write client code]
> [Test terminal rendering]
> [Debug connection issues]
> [Git commit]

# Step 3: Build agent API (1 hour)
> "Build a TypeScript API for programmatic control..."
> [Write API code]
> [Test command execution]
> [Git commit]

# Step 4: Write tests (1.5 hours)
> "Write integration tests for the complete system..."
> [Write test code]
> [Debug test failures]
> [Git commit]

# Step 5: Write documentation (1 hour)
> "Write README and deployment guide..."
> [Write docs]
> [Git commit]

# Total: 7 hours
```

**Problems:**
- ❌ Blocking: Can't start client until server is done
- ❌ Context switching: Manual git commits, manual coordination
- ❌ Single threaded: No parallelization
- ❌ Quality: No systematic code review between steps

---

## Approach 2: Claude Code Teams

**Time:** ~1.5-2 hours (with parallelization)

```bash
# Invoke the team-based skill
/remote-control-builder
```

**What happens behind the scenes:**

### Phase 1: Team Setup (2 minutes)

```
Team Lead: Creating team "remote-control-builder"
Team Lead: Creating 5 tasks (server, client, api, tests, docs)
Team Lead: Spawning 5 specialized agents...

Spawning agents:
  ✓ backend-dev (nextjs-backend-developer)
  ✓ frontend-dev (frontend-developer)
  ✓ api-dev (general-purpose)
  ✓ qa-engineer (qa-engineer)
  ✓ tech-writer (technical-writer)

All agents ready!
```

### Phase 2: Parallel Execution Wave 1 (45 minutes)

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚡ Parallel Execution (3 agents working simultaneously)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[backend-dev] Task 1: Build PTY server
  ├─ Reading task requirements...
  ├─ Claiming task (owner: backend-dev)
  ├─ Installing dependencies (node-pty, ws, express)
  ├─ Writing src/server/pty-server.ts...
  ├─ Implementing session management...
  ├─ Adding WebSocket handler...
  ├─ Running quality gates:
  │  ✓ Lint: 0 errors
  │  ✓ Build: success
  ├─ Self-review: ✓ Passed
  ├─ Git commit: "feat: add PTY server with WebSocket support"
  └─ Task complete! (45 minutes)

[frontend-dev] Task 2: Build browser client
  ├─ Reading task requirements...
  ├─ Claiming task (owner: frontend-dev)
  ├─ Installing dependencies (xterm, xterm-addon-fit)
  ├─ Writing src/client/terminal-client.ts...
  ├─ Implementing WebSocket connection...
  ├─ Adding terminal rendering...
  ├─ Running quality gates:
  │  ✓ Lint: 0 errors
  │  ✓ Build: success
  ├─ Self-review: ✓ Passed
  ├─ Git commit: "feat: add xterm.js browser client"
  └─ Task complete! (40 minutes)

[api-dev] Task 3: Build agent API
  ├─ Reading task requirements...
  ├─ Claiming task (owner: api-dev)
  ├─ SendMessage to backend-dev: "What's the session API format?"
  ├─ [backend-dev responds: "POST /api/sessions creates, GET lists..."]
  ├─ Writing src/agent/controller.ts...
  ├─ Implementing ClaudeCodeAgent class...
  ├─ Running quality gates:
  │  ✓ Lint: 0 errors
  │  ✓ Build: success
  ├─ Self-review: ✓ Passed
  ├─ Git commit: "feat: add agent control API"
  └─ Task complete! (30 minutes)

Parallel wave complete in 45 minutes (vs 4.5 hours sequential)
```

**Note the peer communication:**
```
[api-dev → backend-dev] "What's the session API format?"
[backend-dev → api-dev] "POST /api/sessions creates, GET lists,
                         POST /api/sessions/:id/command sends commands"

(Team Lead doesn't need to relay - agents communicate directly!)
```

### Phase 3: Sequential Execution Wave 2 (40 minutes)

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔄 Sequential Execution (tasks depend on Wave 1 completion)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[qa-engineer] Task 4: Write integration tests
  ├─ Checking dependencies: Tasks 1, 2, 3 must be complete
  ├─ ✓ All dependencies satisfied
  ├─ Claiming task (owner: qa-engineer)
  ├─ Reading completed code from Tasks 1-3...
  ├─ Writing tests/integration/remote-control.test.ts...
  ├─ Running tests:
  │  ✓ Server starts and accepts connections
  │  ✓ Client connects and renders terminal
  │  ✓ Agent API can send commands
  │  ✓ All tests pass (8/8)
  ├─ Git commit: "test: add integration tests"
  └─ Task complete! (25 minutes)

[tech-writer] Task 5: Write documentation
  ├─ (Can run in parallel with Task 4)
  ├─ Claiming task (owner: tech-writer)
  ├─ SendMessage to backend-dev: "What's the deployment process?"
  ├─ SendMessage to frontend-dev: "What's the browser setup?"
  ├─ Writing README.md...
  ├─ Writing docs/DEPLOYMENT.md...
  ├─ Git commit: "docs: add README and deployment guide"
  └─ Task complete! (20 minutes)

Wave 2 complete in 25 minutes (tests and docs in parallel)
```

### Phase 4: Verification & Cleanup (5 minutes)

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Verification & Team Shutdown
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Team Lead: Verifying deliverables...
  ✓ src/server/pty-server.ts exists
  ✓ src/client/terminal-client.ts exists
  ✓ src/agent/controller.ts exists
  ✓ tests/integration/remote-control.test.ts exists
  ✓ README.md exists
  ✓ All quality gates passed (5/5 tasks)
  ✓ All tests passing (8/8)
  ✓ Build successful

Team Lead: Requesting shutdown for all teammates...
  → SendMessage(backend-dev, shutdown_request)
  → SendMessage(frontend-dev, shutdown_request)
  → SendMessage(api-dev, shutdown_request)
  → SendMessage(qa-engineer, shutdown_request)
  → SendMessage(tech-writer, shutdown_request)

All teammates confirmed shutdown ✓

Team Lead: Cleaning up team resources...
  → Deleting ~/.claude/teams/remote-control-builder/
  → Deleting ~/.claude/tasks/remote-control-builder/

Team shutdown complete!
```

### Final Summary

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎉 Build Complete!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Total time: 1 hour 12 minutes

Deliverables:
  ✓ PTY server (src/server/pty-server.ts)
  ✓ Browser client (src/client/terminal-client.ts)
  ✓ Agent API (src/agent/controller.ts)
  ✓ Integration tests (tests/integration/)
  ✓ Documentation (README.md, docs/)

Git history:
  1a2b3c4 docs: add README and deployment guide
  2b3c4d5 test: add integration tests
  3c4d5e6 feat: add agent control API
  4d5e6f7 feat: add xterm.js browser client
  5e6f7g8 feat: add PTY server with WebSocket support

Quality:
  ✓ All quality gates passed
  ✓ All tests passing (8/8)
  ✓ Build successful
  ✓ Code reviewed by each agent

Speedup: 5x faster than manual (1.2h vs 7h)

Next steps:
  1. npm install
  2. npm run dev
  3. Open http://localhost:3000
```

---

## Key Differences

### Time

| Phase | Manual | Teams | Speedup |
|-------|--------|-------|---------|
| PTY Server | 2h | 45m | 2.7x |
| Browser Client | 1.5h | 40m (parallel) | - |
| Agent API | 1h | 30m (parallel) | - |
| Tests | 1.5h | 25m | 6x |
| Docs | 1h | 20m (parallel) | - |
| **Total** | **7h** | **1.2h** | **5.8x** |

### Quality

| Aspect | Manual | Teams |
|--------|--------|-------|
| Code review | Optional | Automatic (per task) |
| Quality gates | Manual | Automatic (per task) |
| Git commits | Manual | Automatic (per task) |
| Test coverage | Variable | Systematic |
| Documentation | Often skipped | Always included |

### Coordination

| Aspect | Manual | Teams |
|--------|--------|-------|
| Context switching | High (you do everything) | Low (agents specialize) |
| Communication | N/A (solo work) | Automatic (peer DMs) |
| Parallelization | None | 3 agents in parallel |
| Task tracking | Manual | Automatic (TaskList) |
| Idle time | N/A | Automatic notifications |

---

## When to Use Teams

**Use teams when:**
- ✅ Task has 3+ independent subtasks
- ✅ Parallelization would save significant time
- ✅ Different expertise needed (backend, frontend, QA, docs)
- ✅ You want systematic quality gates
- ✅ Project is complex enough to warrant coordination

**Don't use teams when:**
- ❌ Simple single-file change
- ❌ No parallelization opportunity (all sequential)
- ❌ Very quick task (< 30 minutes)
- ❌ Team overhead > task duration

---

## Real-World Example: Your Use Case

**Scenario:** You want to control Claude Code remotely from a browser, plus let an agent interact with it.

### Option A: Manual (6-8 hours)
```bash
# You manually code everything sequentially
# - Build PTY server (2h)
# - Build browser client (1.5h)
# - Build agent API (1h)
# - Write tests (1.5h)
# - Write docs (1h)
# Total: 7h
```

### Option B: Use the Team Skill (1-2 hours)
```bash
# One command, team handles everything
/remote-control-builder

# 5 agents work in parallel
# Quality gates automatic
# Tests automatic
# Docs automatic
# Git commits automatic
# Total: 1.2h
```

**Time saved:** 5.8 hours (83% reduction)

---

## How to Invoke

```bash
# In Claude Code terminal:
/remote-control-builder

# That's it! The skill handles:
# 1. Team creation
# 2. Task breakdown
# 3. Agent spawning
# 4. Parallel execution
# 5. Quality gates
# 6. Git commits
# 7. Team shutdown
# 8. Cleanup

# You just wait for the result
```

---

## Customization

If you want to customize the skill:

```bash
# Edit the skill file
vim ~/.claude/skills/remote-control-builder/SKILL.md

# Modify:
# - Number of agents
# - Task breakdown
# - Dependencies (addBlockedBy)
# - Agent types (subagent_type)
# - Extra instructions per task
```

---

## Monitoring Progress

While the team works:

```typescript
// Teams send automatic notifications when:
// - Agent claims a task
// - Agent completes a task
// - Agent goes idle
// - Agent sends peer DM
// - Quality gate passes/fails
// - Git commit created

// You see:
[backend-dev] Claimed Task 1: Build PTY server
[backend-dev] Quality gate passed ✓
[backend-dev] Git commit: feat: add PTY server
[backend-dev] Task 1 complete! Moving to next task...
[backend-dev] No more tasks available, going idle
[frontend-dev] Claimed Task 2: Build browser client
[api-dev] Claimed Task 3: Build agent API
[api-dev → backend-dev] "What's the WebSocket URL format?"
[backend-dev → api-dev] "ws://localhost:8080?session={id}"
...
```

**You don't need to manually check progress - it's streamed to you automatically.**

---

## Summary

**Claude Code Teams enable:**
- ✅ **Parallelization:** 3-5x speedup
- ✅ **Quality:** Automatic gates, reviews, tests
- ✅ **Coordination:** Agents communicate directly (peer DMs)
- ✅ **Specialization:** Each agent uses optimal expertise
- ✅ **Automation:** Git, tests, docs all automatic
- ✅ **Scalability:** Can spawn 10+ agents if needed

**For your remote control use case:** Build in 1-2 hours instead of 6-8 hours, with better quality and complete documentation.
