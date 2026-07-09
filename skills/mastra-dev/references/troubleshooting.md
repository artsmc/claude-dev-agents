# Mastra Dev Troubleshooting

> Part of the `mastra-dev` skill. Ten common issues (server not running, unregistered agent, schema errors, MCP timeouts, Studio blank page, TS compile errors, DB connection, permissions, Python missing, workflow not exposed) with symptoms and fixes. Moved verbatim from SKILL.md.

## Troubleshooting

### Issue 1: "Mastra server is not running"

**Symptoms:**
```
❌ Mastra server is not running (port 6000)
```

**Solutions:**
```bash
# Start the server
/mastra-dev server start

# If that fails, check if port is in use
lsof -i :6000

# Kill existing process if needed
kill -9 <PID>

# Start again
/mastra-dev server start
```

### Issue 2: "Agent not found in mastra.config.ts"

**Symptoms:**
```
⚠️ Agent 'my-agent' exists but not registered in mastra.config.ts
```

**Solutions:**
```bash
# Re-run create-agent with --force flag (if implemented)
/mastra-dev create-agent --name "my-agent" --force

# Or manually add to mastra.config.ts:
# 1. Import: import { myAgent } from '../agents/my-agent.js';
# 2. Register: agents: { myAgent }
```

### Issue 3: "Workflow execution failed with schema error"

**Symptoms:**
```
❌ Step 'fetch-data' failed: Input validation error
Expected { userId: string }, got { user_id: string }
```

**Solutions:**
- Verify step schemas match data flow
- Check previous step's output schema
- Update input schema to match actual data structure
- Use schema transformation step if needed

```bash
# Debug the workflow
/mastra-dev debug-workflow --name "my-workflow" --execution-id "abc-123"

# Check DAG visualization
/mastra-dev show-graph --workflow "my-workflow"
```

### Issue 4: "MCP server connection timeout"

**Symptoms:**
```
❌ Failed to connect to MCP server 'wikipedia'
Connection timeout after 5000ms
```

**Solutions:**
```bash
# Test MCP server independently
npx -y wikipedia-mcp

# Check if command is correct
/mastra-dev mcp list-servers

# Remove and re-add server
/mastra-dev mcp remove-client --name "wikipedia"
/mastra-dev mcp add-client --name "wikipedia" --command "npx" --args "-y,wikipedia-mcp"

# Restart Mastra server
/mastra-dev server stop
/mastra-dev server start
```

### Issue 5: "Mastra Studio shows blank page"

**Symptoms:**
- Studio loads but shows empty interface
- "Cannot connect to server" error

**Solutions:**
```bash
# Ensure Mastra server is running first
/mastra-dev server status

# If not running, start it
/mastra-dev server start

# Then start Studio
/mastra-dev studio start

# Check CORS configuration in apps/mastra/src/app.ts
# Should include: http://localhost:4111 in allowed origins
```

### Issue 6: "TypeScript compilation errors after generation"

**Symptoms:**
```
Error: Cannot find module '@mastra/core'
```

**Solutions:**
```bash
# Install dependencies
cd apps/mastra
npm install

# Or from monorepo root
npm install

# Rebuild
npm run build:mastra
```

### Issue 7: "Database connection error"

**Symptoms:**
```
❌ PostgreSQL connection failed
Error: connect ECONNREFUSED 127.0.0.1:5432
```

**Solutions:**
```bash
# Check if PostgreSQL is running
pg_isready -h localhost -p 5432

# Start PostgreSQL (Docker)
cd apps/mastra
docker-compose up -d postgres

# Or use system PostgreSQL
sudo service postgresql start

# Verify DATABASE_URL environment variable
echo $DATABASE_URL
```

### Issue 8: "Permission denied when running skill"

**Symptoms:**
```
bash: /home/artsmc/.claude/skills/mastra-dev/skill.sh: Permission denied
```

**Solutions:**
```bash
# Make skill executable
chmod +x /home/artsmc/.claude/skills/mastra-dev/skill.sh

# Or run with bash explicitly
bash /home/artsmc/.claude/skills/mastra-dev/skill.sh server status
```

### Issue 9: "Python not found"

**Symptoms:**
```
❌ Error: Python 3 is required
```

**Solutions:**
```bash
# Check Python installation
python3 --version

# Install Python 3 (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install python3

# Install Python 3 (macOS)
brew install python3
```

### Issue 10: "Workflow not exposed in MCP server"

**Symptoms:**
- Workflow exists but not available as MCP tool
- External MCP clients can't see workflow

**Solutions:**
```bash
# Configure workflow for MCP exposure
/mastra-dev mcp configure-server --workflows "my-workflow"

# Verify MCP configuration
/mastra-dev mcp list-servers

# Restart Mastra server to apply changes
/mastra-dev server stop
/mastra-dev server start

# Test MCP connection
/mastra-dev mcp test --server "mastra-workflows"
```

