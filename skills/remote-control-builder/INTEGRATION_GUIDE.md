# Remote Control Integration Guide

## Problem: Controlling Claude Code Remotely

You want to:
1. **Watch** a Claude Code session (read-only stream)
2. **Control** it remotely (send commands, manage files)
3. Let an **agent** interact with Claude Code programmatically

---

## Solution Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     YOUR SETUP                               │
└─────────────────────────────────────────────────────────────┘

┌──────────────┐         ┌──────────────┐         ┌──────────────┐
│   Browser    │◄────────│  PTY Server  │◄────────│ Claude Code  │
│  (Human UI)  │  WS     │  (Node.js)   │  PTY    │  (Process)   │
└──────────────┘         └──────────────┘         └──────────────┘
                                 ▲
                                 │ WS
                         ┌───────┴────────┐
                         │                 │
                    ┌────┴─────┐    ┌─────┴─────┐
                    │  Agent   │    │  matchlock │
                    │  (API)   │    │  (SSH)     │
                    └──────────┘    └───────────┘
```

---

## Part 1: PTY Server (Core Infrastructure)

**File:** `src/server/pty-server.ts`

```typescript
import * as pty from 'node-pty';
import { WebSocketServer, WebSocket } from 'ws';
import express from 'express';
import crypto from 'crypto';
import fs from 'fs';
import path from 'path';

interface Session {
  id: string;
  ptyProcess: pty.IPty;
  clients: Set<WebSocket>;
  metadata: {
    cwd: string;
    createdAt: Date;
    lastActivity: Date;
    historyFile: string;
  };
}

const sessions = new Map<string, Session>();
const HISTORY_DIR = path.join(process.env.HOME!, '.claude', 'remote-sessions');

// Ensure history directory exists
fs.mkdirSync(HISTORY_DIR, { recursive: true });

const app = express();
app.use(express.json());

// REST API: Create session
app.post('/api/sessions', (req, res) => {
  const sessionId = crypto.randomUUID();
  const cwd = req.body.cwd || process.cwd();
  const historyFile = path.join(HISTORY_DIR, `${sessionId}.log`);

  const ptyProcess = pty.spawn('claude', ['code'], {
    name: 'xterm-256color',
    cols: req.body.cols || 120,
    rows: req.body.rows || 30,
    cwd,
    env: {
      ...process.env,
      TERM: 'xterm-256color',
      COLORTERM: 'truecolor'
    }
  });

  const session: Session = {
    id: sessionId,
    ptyProcess,
    clients: new Set(),
    metadata: {
      cwd,
      createdAt: new Date(),
      lastActivity: new Date(),
      historyFile
    }
  };

  // Log all output to file for replay
  const historyStream = fs.createWriteStream(historyFile, { flags: 'a' });

  ptyProcess.onData((data) => {
    // Write to history file with timestamp
    historyStream.write(JSON.stringify({
      timestamp: Date.now(),
      type: 'output',
      data
    }) + '\n');

    // Broadcast to all connected clients
    session.clients.forEach((ws) => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ type: 'output', data }));
      }
    });
  });

  ptyProcess.onExit((exitCode) => {
    historyStream.end();
    session.clients.forEach((ws) => {
      ws.send(JSON.stringify({ type: 'exit', exitCode }));
      ws.close();
    });
    sessions.delete(sessionId);
  });

  sessions.set(sessionId, session);
  res.json({
    sessionId,
    cwd,
    createdAt: session.metadata.createdAt,
    websocketUrl: `ws://localhost:8080?session=${sessionId}`
  });
});

// REST API: List sessions
app.get('/api/sessions', (req, res) => {
  const sessionList = Array.from(sessions.entries()).map(([id, session]) => ({
    id,
    cwd: session.metadata.cwd,
    createdAt: session.metadata.createdAt,
    lastActivity: session.metadata.lastActivity,
    clientCount: session.clients.size
  }));
  res.json({ sessions: sessionList });
});

// REST API: Get session history (for replay)
app.get('/api/sessions/:id/history', (req, res) => {
  const session = sessions.get(req.params.id);
  if (!session) {
    return res.status(404).json({ error: 'Session not found' });
  }

  const history = fs.readFileSync(session.metadata.historyFile, 'utf-8')
    .trim()
    .split('\n')
    .map(line => JSON.parse(line));

  res.json({ history });
});

// REST API: Send command to session (agent API)
app.post('/api/sessions/:id/command', (req, res) => {
  const session = sessions.get(req.params.id);
  if (!session) {
    return res.status(404).json({ error: 'Session not found' });
  }

  const { command } = req.body;
  session.ptyProcess.write(command + '\n');
  session.metadata.lastActivity = new Date();

  res.json({ success: true });
});

// WebSocket server for terminal I/O
const wss = new WebSocketServer({ port: 8080 });

wss.on('connection', (ws, req) => {
  const url = new URL(req.url!, 'ws://localhost');
  const sessionId = url.searchParams.get('session');
  const readOnly = url.searchParams.get('readonly') === 'true';

  if (!sessionId || !sessions.has(sessionId)) {
    ws.close(4404, 'Session not found');
    return;
  }

  const session = sessions.get(sessionId)!;
  session.clients.add(ws);

  // Send history on connect (for late joiners)
  if (fs.existsSync(session.metadata.historyFile)) {
    const history = fs.readFileSync(session.metadata.historyFile, 'utf-8')
      .trim()
      .split('\n')
      .slice(-100);  // Last 100 lines

    history.forEach((line) => {
      const entry = JSON.parse(line);
      ws.send(JSON.stringify({ type: 'output', data: entry.data }));
    });
  }

  ws.on('message', (msg) => {
    if (readOnly) {
      ws.send(JSON.stringify({
        type: 'error',
        message: 'Read-only mode: cannot send input'
      }));
      return;
    }

    try {
      const { type, data } = JSON.parse(msg.toString());

      if (type === 'input') {
        session.ptyProcess.write(data);
        session.metadata.lastActivity = new Date();
      }

      if (type === 'resize') {
        session.ptyProcess.resize(data.cols, data.rows);
      }
    } catch (err) {
      console.error('Invalid message:', err);
    }
  });

  ws.on('close', () => {
    session.clients.delete(ws);
  });
});

app.listen(3000, () => {
  console.log('Claude Code PTY server running');
  console.log('REST API: http://localhost:3000');
  console.log('WebSocket: ws://localhost:8080');
});
```

---

## Part 2: Browser Client (Human Interface)

**File:** `src/client/terminal-client.ts`

```typescript
import { Terminal } from 'xterm';
import { FitAddon } from 'xterm-addon-fit';
import { WebLinksAddon } from 'xterm-addon-web-links';
import 'xterm/css/xterm.css';

interface SessionInfo {
  sessionId: string;
  cwd: string;
  createdAt: string;
  websocketUrl: string;
}

export class ClaudeCodeTerminal {
  private term: Terminal;
  private ws?: WebSocket;
  private fitAddon: FitAddon;
  private sessionInfo?: SessionInfo;

  constructor(private container: HTMLElement, private readOnly = false) {
    this.term = new Terminal({
      cursorBlink: true,
      fontSize: 14,
      fontFamily: 'Menlo, Monaco, "Courier New", monospace',
      theme: {
        background: '#1e1e1e',
        foreground: '#d4d4d4',
        cursor: '#ffffff',
        selection: '#264f78'
      },
      allowProposedApi: true
    });

    this.fitAddon = new FitAddon();
    this.term.loadAddon(this.fitAddon);
    this.term.loadAddon(new WebLinksAddon());
  }

  async createSession(cwd?: string): Promise<SessionInfo> {
    const response = await fetch('http://localhost:3000/api/sessions', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        cwd: cwd || process.cwd(),
        cols: this.term.cols,
        rows: this.term.rows
      })
    });

    this.sessionInfo = await response.json();
    return this.sessionInfo;
  }

  async attachToSession(sessionId: string): Promise<void> {
    const url = `ws://localhost:8080?session=${sessionId}${this.readOnly ? '&readonly=true' : ''}`;
    this.ws = new WebSocket(url);

    this.ws.onopen = () => {
      console.log('Connected to session:', sessionId);
    };

    this.ws.onmessage = (event) => {
      const { type, data, message, exitCode } = JSON.parse(event.data);

      if (type === 'output') {
        this.term.write(data);
      }

      if (type === 'error') {
        console.error('Session error:', message);
      }

      if (type === 'exit') {
        console.log('Session exited with code:', exitCode);
        this.ws?.close();
      }
    };

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    this.ws.onclose = () => {
      console.log('Disconnected from session');
    };

    // Send user input to session
    if (!this.readOnly) {
      this.term.onData((data) => {
        this.ws?.send(JSON.stringify({ type: 'input', data }));
      });
    }

    // Handle terminal resize
    this.fitAddon.onResize(({ cols, rows }) => {
      this.ws?.send(JSON.stringify({ type: 'resize', data: { cols, rows } }));
    });
  }

  mount(): void {
    this.term.open(this.container);
    this.fitAddon.fit();

    // Auto-resize on window resize
    window.addEventListener('resize', () => {
      this.fitAddon.fit();
    });
  }

  async createAndAttach(cwd?: string): Promise<SessionInfo> {
    const sessionInfo = await this.createSession(cwd);
    await this.attachToSession(sessionInfo.sessionId);
    return sessionInfo;
  }

  destroy(): void {
    this.ws?.close();
    this.term.dispose();
  }
}

// Usage example
const container = document.getElementById('terminal')!;
const terminal = new ClaudeCodeTerminal(container);

terminal.mount();
await terminal.createAndAttach('/home/user/project');
```

**HTML page:**

```html
<!DOCTYPE html>
<html>
<head>
  <title>Claude Code Remote</title>
  <style>
    body {
      margin: 0;
      padding: 0;
      background: #1e1e1e;
      display: flex;
      flex-direction: column;
      height: 100vh;
    }
    #toolbar {
      background: #2d2d30;
      padding: 10px;
      color: white;
      display: flex;
      gap: 10px;
      align-items: center;
    }
    #terminal {
      flex: 1;
      padding: 10px;
    }
    button {
      background: #0e639c;
      border: none;
      color: white;
      padding: 8px 16px;
      cursor: pointer;
      border-radius: 4px;
    }
    button:hover {
      background: #1177bb;
    }
    #status {
      margin-left: auto;
      font-size: 12px;
      color: #cccccc;
    }
  </style>
</head>
<body>
  <div id="toolbar">
    <button id="new-session">New Session</button>
    <button id="attach-session">Attach to Session</button>
    <span id="status">Not connected</span>
  </div>
  <div id="terminal"></div>

  <script type="module">
    import { ClaudeCodeTerminal } from './terminal-client.js';

    const terminal = new ClaudeCodeTerminal(document.getElementById('terminal'));
    terminal.mount();

    document.getElementById('new-session').onclick = async () => {
      const cwd = prompt('Working directory:', process.cwd());
      const sessionInfo = await terminal.createAndAttach(cwd);
      document.getElementById('status').textContent =
        `Connected: ${sessionInfo.sessionId}`;
    };

    document.getElementById('attach-session').onclick = async () => {
      const sessionId = prompt('Session ID:');
      await terminal.attachToSession(sessionId);
      document.getElementById('status').textContent =
        `Connected: ${sessionId}`;
    };
  </script>
</body>
</html>
```

---

## Part 3: Agent API (Programmatic Control)

**File:** `src/agent/controller.ts`

```typescript
export interface SessionInfo {
  sessionId: string;
  cwd: string;
  createdAt: string;
  websocketUrl: string;
}

export interface OutputEvent {
  timestamp: number;
  type: 'output' | 'exit';
  data?: string;
  exitCode?: number;
}

export class ClaudeCodeAgent {
  constructor(
    private apiUrl = 'http://localhost:3000',
    private sessionId?: string
  ) {}

  /**
   * Create a new Claude Code session
   */
  async createSession(cwd?: string): Promise<SessionInfo> {
    const response = await fetch(`${this.apiUrl}/api/sessions`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ cwd })
    });

    const sessionInfo = await response.json();
    this.sessionId = sessionInfo.sessionId;
    return sessionInfo;
  }

  /**
   * List all active sessions
   */
  async listSessions(): Promise<SessionInfo[]> {
    const response = await fetch(`${this.apiUrl}/api/sessions`);
    const { sessions } = await response.json();
    return sessions;
  }

  /**
   * Send a command to the session
   */
  async sendCommand(command: string, sessionId?: string): Promise<void> {
    const id = sessionId || this.sessionId;
    if (!id) throw new Error('No session ID provided');

    await fetch(`${this.apiUrl}/api/sessions/${id}/command`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ command })
    });
  }

  /**
   * Read session history (all output since session started)
   */
  async readHistory(sessionId?: string): Promise<OutputEvent[]> {
    const id = sessionId || this.sessionId;
    if (!id) throw new Error('No session ID provided');

    const response = await fetch(`${this.apiUrl}/api/sessions/${id}/history`);
    const { history } = await response.json();
    return history;
  }

  /**
   * Wait for specific output pattern
   */
  async waitForOutput(
    pattern: RegExp,
    timeoutMs = 30000,
    sessionId?: string
  ): Promise<string> {
    const id = sessionId || this.sessionId;
    if (!id) throw new Error('No session ID provided');

    const startTime = Date.now();

    while (Date.now() - startTime < timeoutMs) {
      const history = await this.readHistory(id);
      const recentOutput = history
        .slice(-50)  // Last 50 events
        .filter(e => e.type === 'output')
        .map(e => e.data)
        .join('');

      const match = recentOutput.match(pattern);
      if (match) {
        return match[0];
      }

      await new Promise(resolve => setTimeout(resolve, 500));
    }

    throw new Error(`Timeout waiting for pattern: ${pattern}`);
  }

  /**
   * Execute a command and wait for completion
   */
  async execute(
    command: string,
    options: {
      timeout?: number;
      waitForPattern?: RegExp;
    } = {}
  ): Promise<string> {
    await this.sendCommand(command);

    if (options.waitForPattern) {
      return await this.waitForOutput(
        options.waitForPattern,
        options.timeout || 30000
      );
    }

    // Default: wait 2 seconds and return recent output
    await new Promise(resolve => setTimeout(resolve, 2000));
    const history = await this.readHistory();
    return history
      .slice(-20)
      .filter(e => e.type === 'output')
      .map(e => e.data)
      .join('');
  }
}

// Usage examples
export async function examples() {
  const agent = new ClaudeCodeAgent();

  // Example 1: Create session and run skill
  await agent.createSession('/home/user/project');
  await agent.sendCommand('/memory-bank-read');
  await agent.waitForOutput(/Memory Bank Summary/, 10000);
  console.log('Memory bank read complete');

  // Example 2: Execute command and get output
  const output = await agent.execute('/pm-db dashboard', {
    timeout: 15000,
    waitForPattern: /Projects: \d+ active/
  });
  console.log('Dashboard output:', output);

  // Example 3: Automate feature development
  await agent.sendCommand('/feature-new "add user profile page"');
  await agent.waitForOutput(/CHECKPOINT 1: Review specifications/, 60000);
  await agent.sendCommand('approve');  // Approve spec
  await agent.waitForOutput(/CHECKPOINT 2: Approve execution plan/, 60000);
  await agent.sendCommand('approve');  // Approve plan
  await agent.waitForOutput(/Phase complete!/, 3600000);  // Wait up to 1 hour

  // Example 4: Monitor progress
  const sessions = await agent.listSessions();
  console.log('Active sessions:', sessions);
}
```

---

## Part 4: Integration with matchlock (SSH-based control)

**matchlock** provides SSH-based session sharing. You can integrate it:

```bash
# Option A: Run PTY server, expose via matchlock
# On your machine:
node src/server/pty-server.ts

# Share via SSH:
matchlock share --port 3000 --port 8080

# Others connect via:
matchlock connect user@host

# They get access to:
# - HTTP API at localhost:3000
# - WebSocket at localhost:8080
```

**Option B: Run Claude Code directly in matchlock session**

```bash
# Start matchlock session
matchlock start

# Inside matchlock session, start Claude Code
claude code

# Others attach read-only:
matchlock attach <session-id> --readonly

# Others attach with control:
matchlock attach <session-id>
```

---

## Part 5: Claude Code Teams + Remote Control

**Use case:** Build this entire system using a multi-agent team

```bash
# Invoke the skill we just created
/remote-control-builder

# This will:
# 1. Create a team with 5 specialized agents
# 2. Assign tasks (PTY server, browser client, agent API, tests, docs)
# 3. Agents work in parallel
# 4. Team lead coordinates communication
# 5. Delivers complete system in 1-2 hours (vs 6-8 hours manually)
```

**What happens behind the scenes:**

```
Team Lead: Creates team "remote-control-builder"
Team Lead: Spawns 5 agents (backend, frontend, api, qa, docs)

[Parallel execution begins]

backend-dev:    Building PTY server... ✓ (45 min)
frontend-dev:   Building browser client... ✓ (40 min)
api-dev:        Building agent API... ✓ (30 min)

[Parallel execution complete - 45 min elapsed]

qa-engineer:    Writing integration tests... ✓ (25 min)
tech-writer:    Writing documentation... ✓ (20 min)

[Sequential execution complete - 70 min total]

Team Lead: All tasks complete!
Team Lead: Shutting down team...
```

**Time savings:** 3x faster than sequential (due to parallelization)

---

## Part 6: Security Considerations

**CRITICAL:** This gives remote control of your development environment.

### Authentication

```typescript
// Add JWT authentication
import jwt from 'jsonwebtoken';

const JWT_SECRET = process.env.JWT_SECRET || crypto.randomBytes(32).toString('hex');

app.post('/api/auth/login', (req, res) => {
  const { username, password } = req.body;

  // Verify credentials (use bcrypt in production)
  if (username === 'admin' && password === process.env.ADMIN_PASSWORD) {
    const token = jwt.sign({ username }, JWT_SECRET, { expiresIn: '24h' });
    res.json({ token });
  } else {
    res.status(401).json({ error: 'Invalid credentials' });
  }
});

// Middleware to verify JWT
function authenticateToken(req, res, next) {
  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1];

  if (!token) return res.sendStatus(401);

  jwt.verify(token, JWT_SECRET, (err, user) => {
    if (err) return res.sendStatus(403);
    req.user = user;
    next();
  });
}

// Protect all API routes
app.use('/api/sessions', authenticateToken);
```

### TLS

```typescript
import https from 'https';
import fs from 'fs';

const httpsOptions = {
  key: fs.readFileSync('server-key.pem'),
  cert: fs.readFileSync('server-cert.pem')
};

https.createServer(httpsOptions, app).listen(3000);
```

### Audit Logging

```typescript
const auditLog = fs.createWriteStream('audit.log', { flags: 'a' });

function logAudit(user: string, action: string, details: any) {
  auditLog.write(JSON.stringify({
    timestamp: new Date().toISOString(),
    user,
    action,
    details
  }) + '\n');
}

// Log all commands
app.post('/api/sessions/:id/command', authenticateToken, (req, res) => {
  logAudit(req.user.username, 'COMMAND', {
    sessionId: req.params.id,
    command: req.body.command
  });

  // ... rest of handler
});
```

---

## Summary

You now have **three layers of control**:

1. **Human control:** Browser UI with xterm.js
2. **Agent control:** REST API + WebSocket for automation
3. **SSH control:** matchlock for temporary sharing

**All integrated with Claude Code's team system** for building complex features with multiple specialized agents.

---

## Next Steps

1. **Build the system:**
   ```bash
   /remote-control-builder
   ```

2. **Deploy:**
   ```bash
   npm install
   npm run build
   npm start
   ```

3. **Test:**
   ```bash
   # Browser: http://localhost:3000
   # API: curl http://localhost:3000/api/sessions
   ```

4. **Secure:**
   - Add JWT authentication
   - Enable TLS
   - Set up audit logging
   - Use matchlock for temporary sharing

5. **Extend:**
   - Add file explorer
   - Add git integration
   - Add multi-user collaboration
   - Add session recording/replay
