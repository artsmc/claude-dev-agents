# Mastra Dev Command Reference

> Part of the `mastra-dev` skill. Per-command documentation for all six capability areas (agents, workflows, tools, server, MCP, analysis/debugging) with full flag lists, generated-file examples, and sample outputs. Moved verbatim from SKILL.md.

## Features

### 1. Agent Management

Create, list, and analyze Mastra agents with intelligent scaffolding.

**Commands:**

```bash
# Create new agent
/mastra-dev create-agent \
  --name <agent-name> \
  --model <provider/model> \
  --description <description> \
  [--instructions <instructions-text>] \
  [--tools <comma-separated-tool-ids>]

# List all agents
/mastra-dev list-agents

# Analyze agent configuration
/mastra-dev analyze-agent --name <agent-name>
```

**Example - Create Contract Analysis Agent:**

```bash
/mastra-dev create-agent \
  --name "contract-analyzer" \
  --model "anthropic/claude-3-5-sonnet-20241022" \
  --description "Federal contract analysis expert" \
  --instructions "You are an expert in analyzing federal contracts for compliance, risks, and key terms. Focus on FAR/DFARS requirements." \
  --tools "document-parser,sam-gov-lookup,far-compliance"
```

**Generated File:** `apps/mastra/src/agents/contract-analyzer.ts`

```typescript
import { Agent } from '@mastra/core';

export const contractAnalyzerAgent = new Agent({
  id: 'contract-analyzer',
  name: 'Federal Contract Analysis Expert',
  description: 'Federal contract analysis expert',
  instructions: `You are an expert in analyzing federal contracts for compliance, risks, and key terms. Focus on FAR/DFARS requirements.`,
  model: {
    provider: 'anthropic',
    model: 'claude-3-5-sonnet-20241022'
  },
  tools: ['document-parser', 'sam-gov-lookup', 'far-compliance']
});
```

**What Gets Updated:**
- ✅ Agent file created at `apps/mastra/src/agents/contract-analyzer.ts`
- ✅ Registered in `apps/mastra/src/config/mastra.config.ts`
- ✅ Proper TypeScript imports and exports
- ✅ Zod validation ready
- ✅ Compatible with Mastra Studio

### 2. Workflow Management

Design, build, and test DAG-based workflows with step composition.

**Commands:**

```bash
# Create new workflow
/mastra-dev create-workflow \
  --name <workflow-name> \
  --description <description> \
  [--input-schema <json-schema>] \
  [--output-schema <json-schema>]

# Add step to workflow
/mastra-dev add-step \
  --workflow <workflow-name> \
  --step-name <step-name> \
  --step-type <transform|api-call|agent-call|parallel|branch> \
  [--input-schema <json-schema>] \
  [--output-schema <json-schema>]

# Test workflow execution
/mastra-dev test-workflow \
  --name <workflow-name> \
  --input <json-input>

# List all workflows
/mastra-dev list-workflows
```

**Example - Build Form Generation Workflow:**

```bash
# Step 1: Create workflow
/mastra-dev create-workflow \
  --name "form-generation" \
  --description "Auto-fill government forms from SAM.gov data" \
  --input-schema '{"opportunityId": "string"}' \
  --output-schema '{"formData": "object", "pdfUrl": "string"}'

# Step 2: Add fetch step
/mastra-dev add-step \
  --workflow "form-generation" \
  --step-name "fetch-opportunity" \
  --step-type "api-call" \
  --input-schema '{"opportunityId": "string"}' \
  --output-schema '{"opportunity": "object"}'

# Step 3: Add transform step
/mastra-dev add-step \
  --workflow "form-generation" \
  --step-name "extract-data" \
  --step-type "transform" \
  --input-schema '{"opportunity": "object"}' \
  --output-schema '{"formData": "object"}'

# Step 4: Add PDF generation step
/mastra-dev add-step \
  --workflow "form-generation" \
  --step-name "generate-pdf" \
  --step-type "transform" \
  --input-schema '{"formData": "object"}' \
  --output-schema '{"pdfUrl": "string"}'

# Test the workflow
/mastra-dev test-workflow \
  --name "form-generation" \
  --input '{"opportunityId": "abc-123"}'
```

**Generated File:** `apps/mastra/src/workflows/form-generation.ts`

```typescript
import { createWorkflow, createStep } from '@mastra/core/workflows';
import { z } from 'zod';

const fetchOpportunityStep = createStep({
  id: 'fetch-opportunity',
  inputSchema: z.object({ opportunityId: z.string() }),
  outputSchema: z.object({ opportunity: z.any() }),
  execute: async ({ inputData }) => {
    // API call implementation
    const response = await fetch(`https://api.sam.gov/opportunities/${inputData.opportunityId}`);
    return { opportunity: await response.json() };
  }
});

const extractDataStep = createStep({
  id: 'extract-data',
  inputSchema: z.object({ opportunity: z.any() }),
  outputSchema: z.object({ formData: z.any() }),
  execute: async ({ inputData }) => {
    // Transform logic
    return { formData: { /* extracted data */ } };
  }
});

const generatePdfStep = createStep({
  id: 'generate-pdf',
  inputSchema: z.object({ formData: z.any() }),
  outputSchema: z.object({ pdfUrl: z.string() }),
  execute: async ({ inputData }) => {
    // PDF generation
    return { pdfUrl: 'https://example.com/form.pdf' };
  }
});

export const formGenerationWorkflow = createWorkflow({
  id: 'form-generation',
  description: 'Auto-fill government forms from SAM.gov data',
  inputSchema: z.object({ opportunityId: z.string() }),
  outputSchema: z.object({ formData: z.any(), pdfUrl: z.string() })
})
  .then(fetchOpportunityStep)
  .then(extractDataStep)
  .then(generatePdfStep)
  .commit();
```

**Control Flow Patterns:**

- **Sequential:** `.then(stepA).then(stepB).then(stepC)`
- **Parallel:** `.parallel([stepA, stepB, stepC])`
- **Conditional:** `.branch({ when: (data) => data.score > 0.8, then: highPath, otherwise: lowPath })`

### 3. Tool Management

Create reusable tools with schema validation and type safety.

**Commands:**

```bash
# Create new tool
/mastra-dev create-tool \
  --name <tool-name> \
  --description <description> \
  [--input-schema <json-schema>] \
  [--output-schema <json-schema>]

# List all tools
/mastra-dev list-tools

# Test tool execution
/mastra-dev test-tool \
  --name <tool-name> \
  --input <json-input>
```

**Example - Create PDF Generator Tool:**

```bash
/mastra-dev create-tool \
  --name "pdf-generator" \
  --description "Generate PDF from template and data" \
  --input-schema '{"template": "string", "data": "object"}' \
  --output-schema '{"pdfUrl": "string", "size": "number"}'
```

**Generated File:** `apps/mastra/src/tools/pdf-generator.ts`

```typescript
import { createTool } from '@mastra/core/tools';
import { z } from 'zod';

export const pdfGeneratorTool = createTool({
  id: 'pdf-generator',
  description: 'Generate PDF from template and data',
  inputSchema: z.object({
    template: z.string(),
    data: z.record(z.any())
  }),
  outputSchema: z.object({
    pdfUrl: z.string(),
    size: z.number()
  }),
  execute: async ({ inputData }) => {
    // PDF generation logic
    const pdfUrl = await generatePdf(inputData.template, inputData.data);
    return {
      pdfUrl,
      size: 12345
    };
  }
});
```

### 4. Server Management

Control Mastra server lifecycle and monitor logs.

**Commands:**

```bash
# Start Mastra server
/mastra-dev server start

# Stop Mastra server
/mastra-dev server stop

# Check server status
/mastra-dev server status

# View server logs
/mastra-dev server logs [--tail <lines>]

# Start Mastra Studio (observability UI)
/mastra-dev studio start
```

**Example - Server Management Workflow:**

```bash
# Check if server is running
/mastra-dev server status
# Output: ❌ Mastra server is not running (port 6000)

# Start the server
/mastra-dev server start
# Output: ✅ Mastra server started on port 6000 (PID: 12345)

# Verify it's running
/mastra-dev server status
# Output: ✅ Mastra server is running on port 6000 (PID: 12345)
#         Uptime: 5 minutes
#         Memory: 245 MB

# View recent logs
/mastra-dev server logs --tail 50
# Output: [Shows last 50 lines from apps/mastra/logs/mastra.log]

# Start Mastra Studio for observability
/mastra-dev studio start
# Output: ✅ Mastra Studio started on http://localhost:4111
#         Connected to Mastra API at http://localhost:6000
```

**What Happens:**
- **server start:** Launches Mastra Express server via `npm run dev:mastra`
- **server stop:** Gracefully terminates process via SIGTERM
- **server status:** Checks port 6000, parses `ps aux | grep mastra`
- **server logs:** Tails from `apps/mastra/logs/mastra.log`
- **studio start:** Launches Mastra Studio CLI on port 4111

### 5. MCP Management

Configure Model Context Protocol integration for external tool access.

**Commands:**

```bash
# Add MCPClient for consuming external servers
/mastra-dev mcp add-client \
  --name <server-name> \
  --command <command> \
  [--args <comma-separated-args>] \
  [--url <http-url>]

# Configure MCPServer to expose Mastra tools
/mastra-dev mcp configure-server \
  [--agents <comma-separated-agent-ids>] \
  [--workflows <comma-separated-workflow-ids>] \
  [--tools <comma-separated-tool-ids>]

# List all MCP servers
/mastra-dev mcp list-servers

# Test MCP server connection
/mastra-dev mcp test --server <server-name>
```

**Example - Add External MCP Servers:**

```bash
# Add local stdio MCP server (Wikipedia)
/mastra-dev mcp add-client \
  --name "wikipedia" \
  --command "npx" \
  --args "-y,wikipedia-mcp"

# Add remote HTTP MCP server (Weather)
/mastra-dev mcp add-client \
  --name "weather" \
  --url "https://server.smithery.ai/@smithery-ai/national-weather-service/mcp"

# Add Puppeteer for browser automation
/mastra-dev mcp add-client \
  --name "puppeteer" \
  --command "npx" \
  --args "-y,@modelcontextprotocol/server-puppeteer"
```

**Updated Configuration:** `apps/mastra/src/config/mcp.config.ts`

```typescript
import { MCPClient } from '@mastra/mcp';

export const mcpClient = new MCPClient({
  id: 'mastra-mcp-client',
  servers: {
    wikipedia: {
      command: 'npx',
      args: ['-y', 'wikipedia-mcp']
    },
    weather: {
      url: new URL('https://server.smithery.ai/@smithery-ai/national-weather-service/mcp')
    },
    puppeteer: {
      command: 'npx',
      args: ['-y', '@modelcontextprotocol/server-puppeteer']
    }
  }
});
```

**Example - Expose Mastra Workflows via MCP:**

```bash
# Configure MCPServer to expose workflows
/mastra-dev mcp configure-server \
  --workflows "form-generation,contract-analysis"
```

**Updated Configuration:**

```typescript
import { MCPServer } from '@mastra/mcp';
import { formGenerationWorkflow } from '../workflows/form-generation.js';
import { contractAnalysisWorkflow } from '../workflows/contract-analysis.js';

export const mastraMcpServer = new MCPServer({
  id: 'mastra-workflows',
  name: 'Mastra Workflow Engine',
  version: '1.0.0',
  workflows: {
    formGeneration: formGenerationWorkflow,
    contractAnalysis: contractAnalysisWorkflow
  }
});
```

**Testing MCP Connection:**

```bash
/mastra-dev mcp test --server "wikipedia"
# Output: ✅ Connected to wikipedia MCP server
#         Available tools: search_wikipedia, get_article, get_summary
#         Transport: stdio
#         Status: healthy
```

### 6. Analysis & Debugging

Analyze Mastra setup, debug workflow execution, and validate configurations.

**Commands:**

```bash
# Analyze entire Mastra setup
/mastra-dev analyze

# Debug workflow execution
/mastra-dev debug-workflow \
  --name <workflow-name> \
  --execution-id <execution-id>

# Show workflow DAG visualization
/mastra-dev show-graph --workflow <workflow-name>

# Validate all configurations
/mastra-dev validate
```

**Example - Comprehensive Analysis:**

```bash
/mastra-dev analyze
```

**Output:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔍 Mastra Setup Analysis
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 AGENTS (3 found)
  ✅ contract-analyzer
     Model: anthropic/claude-3-5-sonnet-20241022
     Tools: document-parser, sam-gov-lookup, far-compliance
     Status: Registered in mastra.config.ts

  ✅ proposal-writer
     Model: openai/gpt-4-turbo
     Tools: sam-gov-lookup, company-data
     Status: Registered in mastra.config.ts

  ✅ data-analyst
     Model: anthropic/claude-3-5-sonnet-20241022
     Tools: database-query, chart-generator
     Status: Registered in mastra.config.ts

📊 WORKFLOWS (2 found)
  ✅ form-generation
     Steps: 3 (fetch-opportunity, extract-data, generate-pdf)
     Type: Sequential DAG
     Status: Registered in MCP Server

  ✅ contract-analysis
     Steps: 4 (extract-text, identify-clauses, check-compliance, assess-risks)
     Type: Sequential DAG
     Status: Registered in MCP Server

📊 TOOLS (5 found)
  ✅ pdf-generator
  ✅ document-parser
  ✅ sam-gov-lookup
  ✅ far-compliance
  ✅ database-query

📊 MCP SERVERS (3 configured)
  ✅ wikipedia (stdio)
  ✅ weather (HTTP)
  ✅ puppeteer (stdio)

📊 DATABASE
  ✅ PostgreSQL connected
  ✅ Schema: mastra
  ✅ Tables: tenants, workflows, workflow_executions, step_execution_logs

📊 SERVER STATUS
  ✅ Running on port 6000
  ✅ PID: 12345
  ✅ Uptime: 2 hours 15 minutes
  ✅ Memory: 245 MB

✅ All configurations valid
```

**Example - Debug Failed Workflow:**

```bash
/mastra-dev debug-workflow \
  --name "contract-analysis" \
  --execution-id "550e8400-e29b-41d4-a716-446655440000"
```

**Output:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🐛 Workflow Execution Debug
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Workflow: contract-analysis
Execution ID: 550e8400-e29b-41d4-a716-446655440000
Status: ❌ FAILED
Started: 2026-02-11 14:23:15
Completed: 2026-02-11 14:23:47
Duration: 32 seconds

📊 STEP EXECUTION BREAKDOWN:

  ✅ Step 1: extract-text
     Status: COMPLETED
     Duration: 8s
     Input: {"documentUrl": "https://example.com/contract.pdf"}
     Output: {"text": "CONTRACT AGREEMENT..."}

  ✅ Step 2: identify-clauses
     Status: COMPLETED
     Duration: 12s
     Input: {"text": "CONTRACT AGREEMENT..."}
     Output: {"clauses": ["FAR 52.212-4", "FAR 52.212-5"]}

  ❌ Step 3: check-compliance
     Status: FAILED
     Duration: 5s
     Input: {"clauses": ["FAR 52.212-4", "FAR 52.212-5"]}
     Error: TypeError: Cannot read property 'farClause' of undefined
     Stack Trace:
       at checkComplianceStep.execute (workflows/contract-analysis.ts:45:23)

  ⏸️ Step 4: assess-risks
     Status: SKIPPED (previous step failed)

🔍 ROOT CAUSE:
  Step 'check-compliance' failed due to undefined property access.

  Likely issue: Missing FAR compliance database connection or
  incorrect data structure returned from identify-clauses step.

💡 SUGGESTED FIX:
  1. Verify far-compliance tool is properly configured
  2. Check inputData schema in check-compliance step
  3. Add null checking: if (!inputData.clauses) throw new Error(...)
  4. Review step schema compatibility

📝 LOGS:
  [2026-02-11 14:23:40] ERROR: FAR compliance check failed
  [2026-02-11 14:23:40] ERROR: Database connection timeout
```

**Example - Show Workflow DAG:**

```bash
/mastra-dev show-graph --workflow "form-generation"
```

**Output (ASCII DAG):**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Workflow DAG: form-generation
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Input: { opportunityId: string }
  │
  ├─> [fetch-opportunity]
  │     Input: { opportunityId: string }
  │     Output: { opportunity: object }
  │
  ├─> [extract-data]
  │     Input: { opportunity: object }
  │     Output: { formData: object }
  │
  ├─> [generate-pdf]
  │     Input: { formData: object }
  │     Output: { pdfUrl: string }
  │
  └─> Output: { formData: object, pdfUrl: string }

Composition: Sequential (.then chain)
Total Steps: 3
Schema Validation: ✅ All schemas compatible
```

**Example - Validate All Configurations:**

```bash
/mastra-dev validate
```

**Output:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔍 Configuration Validation
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ mastra.config.ts
   - All agents registered correctly
   - All workflows registered correctly
   - Storage configuration valid (PostgresStore)
   - MCP servers configured properly

✅ mcp.config.ts
   - MCPClient configuration valid
   - 3 servers configured (wikipedia, weather, puppeteer)
   - MCPServer exports 2 workflows

✅ Agent Files
   - contract-analyzer.ts: Valid TypeScript, proper imports
   - proposal-writer.ts: Valid TypeScript, proper imports
   - data-analyst.ts: Valid TypeScript, proper imports

✅ Workflow Files
   - form-generation.ts: Valid DAG, schemas compatible
   - contract-analysis.ts: Valid DAG, schemas compatible

✅ Tool Files
   - pdf-generator.ts: Valid TypeScript, Zod schemas correct
   - document-parser.ts: Valid TypeScript, Zod schemas correct

✅ Database Schema
   - mastra schema exists
   - All required tables present
   - Migrations up to date

⚠️ WARNINGS (1):
  - Tool 'far-compliance' referenced in agent but not found in tools directory
    Recommendation: Create tools/far-compliance.ts or remove from agent

✅ Overall Status: VALID (1 warning)
```

