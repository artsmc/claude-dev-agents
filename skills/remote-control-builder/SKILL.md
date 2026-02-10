---
title: remote-control-builder
description: Build remote control system for Claude Code using multi-agent team
skill_type: complex-task
user_invocable: true
---

# Remote Control Builder Skill

**Purpose:** Orchestrate a multi-agent team to build a complete remote control system for Claude Code sessions (PTY server + browser client + agent API).

**User invokes with:** `/remote-control-builder`

---

## System Instructions

You are the **Team Lead** for building a remote control system. Your job is to:

1. Create a team with specialized agents
2. Break down the work into parallel tasks
3. Assign tasks to appropriate agents
4. Coordinate communication between agents
5. Verify deliverables
6. Shut down the team cleanly

---

## Execution Steps

### Step 1: Initialize Team

```typescript
TeamCreate({
  team_name: "remote-control-builder",
  description: "Build remote control system for Claude Code",
  agent_type: "general-purpose"
});
```

**Creates:**
- Team config: `~/.claude/teams/remote-control-builder/config.json`
- Task list dir: `~/.claude/tasks/remote-control-builder/`

---

### Step 2: Create Task List

Use TaskCreate to define all work items:

```typescript
// Task 1: PTY Server (backend)
TaskCreate({
  subject: "Build Node.js PTY server with WebSocket support",
  description: `
Create a TypeScript server that:
- Spawns Claude Code process via node-pty
- Exposes WebSocket endpoint for terminal I/O
- Handles multiple concurrent sessions
- Implements session management (create, attach, list)
- Supports terminal resize events

Dependencies:
- node-pty
- ws (WebSocket library)
- express

Output: src/server/pty-server.ts
`,
  activeForm: "Building PTY server"
});

// Task 2: Browser Client (frontend)
TaskCreate({
  subject: "Build xterm.js browser client",
  description: `
Create a TypeScript browser client that:
- Renders terminal in browser using xterm.js
- Connects to PTY server via WebSocket
- Handles user input (keyboard, paste)
- Implements terminal resize
- Shows connection status

Dependencies:
- xterm
- xterm-addon-fit

Output: src/client/terminal-client.ts
`,
  activeForm: "Building browser client"
});

// Task 3: Agent API (automation interface)
TaskCreate({
  subject: "Build agent control API",
  description: `
Create a TypeScript API that allows agents to:
- Send commands programmatically
- Read terminal output
- Create/destroy sessions
- List active sessions
- Get session metadata

Output: src/agent/controller.ts
`,
  activeForm: "Building agent API"
});

// Task 4: Integration Tests
TaskCreate({
  subject: "Write integration tests",
  description: `
Test the complete system:
- Server starts and accepts connections
- Client connects and renders terminal
- Commands execute in Claude Code
- Agent API can control sessions

Use: Playwright for browser tests, Jest for unit tests

Output: tests/integration/
`,
  activeForm: "Writing integration tests"
});

// Task 5: Documentation
TaskCreate({
  subject: "Write README and deployment guide",
  description: `
Document:
- Architecture overview
- Setup instructions
- API reference
- Security considerations
- Deployment guide

Output: README.md, docs/
`,
  activeForm: "Writing documentation"
});
```

---

### Step 3: Spawn Specialized Teammates

```typescript
// Backend developer for PTY server
Task({
  subagent_type: "nextjs-backend-developer",  // Has Node.js expertise
  team_name: "remote-control-builder",
  name: "backend-dev",
  prompt: `
You are responsible for Task 1: Build PTY server.

Read the task details:
TaskGet({ taskId: "1" })

Claim the task:
TaskUpdate({ taskId: "1", owner: "backend-dev", status: "in_progress" })

Build the server, then mark complete:
TaskUpdate({ taskId: "1", status: "completed" })

Check for your next task:
TaskList()
`,
  description: "Build PTY server"
});

// Frontend developer for browser client
Task({
  subagent_type: "frontend-developer",
  team_name: "remote-control-builder",
  name: "frontend-dev",
  prompt: `
You are responsible for Task 2: Build browser client.

Read task details, claim it, build it, mark complete.
Then check TaskList() for Task 4 (integration tests).
`,
  description: "Build browser client"
});

// API developer for agent interface
Task({
  subagent_type: "general-purpose",
  team_name: "remote-control-builder",
  name: "api-dev",
  prompt: `
You are responsible for Task 3: Build agent API.

This API will be used by autonomous agents to control Claude Code sessions.

Coordinate with backend-dev to understand the session management interface.
`,
  description: "Build agent API"
});

// QA engineer for testing
Task({
  subagent_type: "qa-engineer",
  team_name: "remote-control-builder",
  name: "qa-engineer",
  prompt: `
You are responsible for Task 4: Integration tests.

Wait for Tasks 1, 2, 3 to complete (check TaskList periodically).

When ready, write comprehensive tests that verify:
- PTY server works
- Browser client connects
- Agent API controls sessions
`,
  description: "Write integration tests"
});

// Technical writer for docs
Task({
  subagent_type: "technical-writer",
  team_name: "remote-control-builder",
  name: "tech-writer",
  prompt: `
You are responsible for Task 5: Documentation.

Coordinate with other teammates to understand the architecture.

Use SendMessage to ask questions about implementation details.
`,
  description: "Write documentation"
});
```

---

### Step 4: Monitor Progress

As Team Lead, periodically check task status:

```typescript
// Check what's completed
TaskList();

// View specific task details
TaskGet({ taskId: "1" });

// Check if any teammate is idle or blocked
// Teammates automatically send notifications when they go idle
```

---

### Step 5: Coordinate Communication

Facilitate communication between teammates:

```typescript
// Example: frontend-dev asks backend-dev a question
// (This happens automatically via SendMessage)

// You receive a notification:
// "frontend-dev → backend-dev: What's the WebSocket URL format?"

// backend-dev responds automatically:
// "backend-dev → frontend-dev: ws://localhost:8080?session={sessionId}"

// You don't need to intervene unless there's a blocker
```

---

### Step 6: Verify Deliverables

After all tasks complete:

```typescript
// Check that all files exist
Read({ file_path: "./src/server/pty-server.ts" });
Read({ file_path: "./src/client/terminal-client.ts" });
Read({ file_path: "./src/agent/controller.ts" });
Read({ file_path: "./tests/integration/remote-control.test.ts" });
Read({ file_path: "./README.md" });

// Run integration tests
Bash({ command: "npm test" });

// Verify build passes
Bash({ command: "npm run build" });
```

---

### Step 7: Shut Down Team

```typescript
// Request shutdown for all teammates
const teammates = ["backend-dev", "frontend-dev", "api-dev", "qa-engineer", "tech-writer"];

for (const teammate of teammates) {
  SendMessage({
    type: "shutdown_request",
    recipient: teammate,
    content: "All tasks complete, shutting down team"
  });
}

// Wait for confirmations, then clean up
TeamDelete();
```

---

## Key Patterns

### 1. Task Dependencies

Use `addBlockedBy` to enforce order:

```typescript
TaskUpdate({
  taskId: "4",  // Integration tests
  addBlockedBy: ["1", "2", "3"]  // Must wait for server, client, API
});
```

### 2. Parallel Work

Tasks 1, 2, 3 can run in parallel (no dependencies).
Task 4 must wait for all three.
Task 5 can run in parallel with 4.

### 3. Peer Communication

Teammates communicate directly via SendMessage:

```typescript
// frontend-dev asks backend-dev
SendMessage({
  type: "message",
  recipient: "backend-dev",
  content: "What's the session ID format?",
  summary: "Question about session IDs"
});

// You (team lead) see a summary in idle notification
// but don't need to relay the message
```

### 4. Idle Notifications

**IMPORTANT:** Teammates go idle after every turn. This is NORMAL.

- ✅ Idle = waiting for work or input
- ❌ Don't treat idle as an error
- ✅ Idle notifications include peer DM summaries

### 5. Automatic Message Delivery

**You don't need to check for messages manually.**

- Messages from teammates appear automatically
- When you're busy, they're queued
- System delivers them when your turn ends

---

## Success Criteria

✅ All 5 tasks completed
✅ Integration tests pass
✅ Build succeeds
✅ README.md exists and is comprehensive
✅ All teammates shut down cleanly
✅ Team directory cleaned up

---

## Output to User

After completion, provide:

1. **Summary:** "Built complete remote control system with 5-agent team"
2. **Deliverables:**
   - PTY server at `src/server/pty-server.ts`
   - Browser client at `src/client/terminal-client.ts`
   - Agent API at `src/agent/controller.ts`
   - Tests at `tests/integration/`
   - Documentation at `README.md`
3. **Next Steps:**
   - Run `npm install` to install dependencies
   - Run `npm run dev` to start server
   - Open `http://localhost:3000` in browser
   - Use `ClaudeCodeAgent` class for programmatic control

---

## Notes

- **Team coordination overhead:** ~5-10 minutes for setup/teardown
- **Parallel speedup:** 3x faster than sequential (tasks 1, 2, 3 run concurrently)
- **Communication:** Teammates communicate directly (DMs), team lead only intervenes for blockers
- **Quality:** Each teammate runs their own quality checks before marking tasks complete
