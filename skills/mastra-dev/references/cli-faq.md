# Mastra Dev CLI FAQ

> Part of the `mastra-dev` skill. Answers to the five core /mastra-dev questions (create agent, build workflow, integrate MCP, debug execution, inventory constructs) with full command invocations and what-happens detail. Moved verbatim from SKILL.md.

## What This Skill Does

This skill answers critical questions for Mastra developers:

### 1. How do I create a new Mastra agent?

```bash
/mastra-dev create-agent \
  --name "proposal-writer" \
  --model "openai/gpt-4-turbo" \
  --description "Expert technical writer for government proposals" \
  --instructions "You are an expert technical writer..." \
  --tools "sam-gov-lookup,company-data"
```

**What happens:**
- Generates `apps/mastra/src/agents/proposal-writer.ts` with proper structure
- Registers agent in `apps/mastra/src/config/mastra.config.ts`
- Follows Mastra best practices with TypeScript typing
- Includes Zod schemas for validation
- Auto-imports required dependencies

### 2. How do I build a workflow with multiple steps?

```bash
# Create workflow
/mastra-dev create-workflow \
  --name "contract-analysis" \
  --description "Analyze government contract for risks"

# Add steps sequentially
/mastra-dev add-step \
  --workflow "contract-analysis" \
  --step-name "extract-text" \
  --step-type "transform" \
  --input-schema '{"documentUrl": "string"}' \
  --output-schema '{"text": "string"}'

/mastra-dev add-step \
  --workflow "contract-analysis" \
  --step-name "identify-clauses" \
  --step-type "transform" \
  --input-schema '{"text": "string"}' \
  --output-schema '{"clauses": "array"}'

# Test the workflow
/mastra-dev test-workflow \
  --name "contract-analysis" \
  --input '{"documentUrl": "https://example.com/contract.pdf"}'
```

**What happens:**
- Creates workflow file at `apps/mastra/src/workflows/contract-analysis.ts`
- Generates steps with proper DAG composition (`.then()`, `.parallel()`, `.branch()`)
- Validates schema compatibility between steps
- Registers workflow in MCP server configuration
- Provides execution testing capability

### 3. How do I integrate external MCP servers?

```bash
# Add Wikipedia MCP server
/mastra-dev mcp add-client \
  --name "wikipedia" \
  --command "npx" \
  --args "-y,wikipedia-mcp"

# Add remote HTTP MCP server
/mastra-dev mcp add-client \
  --name "weather" \
  --url "https://server.smithery.ai/@smithery-ai/national-weather-service/mcp"

# Configure MCP server to expose workflows
/mastra-dev mcp configure-server \
  --agents "proposal-writer" \
  --workflows "contract-analysis"

# List all configured MCP servers
/mastra-dev mcp list-servers

# Test MCP connection
/mastra-dev mcp test --server "wikipedia"
```

**What happens:**
- Updates `apps/mastra/src/config/mcp.config.ts` with MCPClient configuration
- Supports both stdio (local) and HTTP (remote) transports
- Configures MCPServer to expose Mastra agents/workflows as tools
- Validates MCP connections and tool availability

### 4. How do I debug workflow execution?

```bash
# Debug specific workflow execution
/mastra-dev debug-workflow \
  --name "contract-analysis" \
  --execution-id "abc-123-def-456"

# Show workflow DAG visualization
/mastra-dev show-graph --workflow "contract-analysis"

# Validate all Mastra configurations
/mastra-dev validate

# View detailed logs
/mastra-dev server logs --tail 100
```

**What happens:**
- Queries `mastra.workflow_executions` table for execution state
- Retrieves step-by-step logs from `mastra.step_execution_logs`
- Identifies failed steps with error details
- Shows input/output data for each step
- Generates ASCII visualization of workflow DAG
- Validates schema compatibility and configuration correctness

### 5. What agents/workflows/tools are currently defined?

```bash
# List all agents
/mastra-dev list-agents

# Analyze specific agent
/mastra-dev analyze-agent --name "proposal-writer"

# List all workflows
/mastra-dev list-workflows

# List all tools
/mastra-dev list-tools

# Comprehensive analysis
/mastra-dev analyze
```

**What happens:**
- Scans `apps/mastra/src/agents/*.ts` for agent definitions
- Scans `apps/mastra/src/workflows/*.ts` for workflows
- Scans `apps/mastra/src/tools/*.ts` for tools
- Parses TypeScript files to extract configurations
- Shows registration status in `mastra.config.ts`
- Displays model providers, tool usage, and dependencies

