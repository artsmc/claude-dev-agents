# Mastra Core Developer — MCP & Multi-LLM Module

Load this module when the task requires MCP (Model Context Protocol) server/client setup, tool registration, or multi-LLM provider configuration via LiteLLM.

---

## MCP Integration (Model Context Protocol)

### MCPClient — Consuming External MCP Servers

```typescript
import { MCPClient } from '@mastra/mcp';

export const mcpClient = new MCPClient({
  id: 'mastra-mcp-client',
  servers: {
    // Local stdio server (subprocess)
    wikipedia: {
      command: 'npx',
      args: ['-y', '@modelcontextprotocol/server-wikipedia']
    },
    // Remote HTTP server
    weather: {
      url: new URL('https://server.smithery.ai/@smithery-ai/national-weather-service/mcp')
    },
    // Custom server with environment variables
    github: {
      command: 'npx',
      args: ['-y', '@modelcontextprotocol/server-github'],
      env: {
        GITHUB_TOKEN: process.env.GITHUB_TOKEN
      }
    }
  }
});

// Use in agents — auto-loads all MCP tools
const researchAgent = new Agent({
  id: 'research-agent',
  name: 'Research Assistant',
  tools: await mcpClient.listTools(),
  model: {
    provider: 'openai',
    model: 'gpt-4'
  }
});
```

### MCPServer — Exposing Mastra Tools/Workflows

```typescript
import { MCPServer } from '@mastra/mcp';
import { mastra } from './mastra.config.js';

export const mastraMcpServer = new MCPServer({
  id: 'mastra-workflows',
  name: 'Mastra Workflow Engine',
  version: '1.0.0',
  tools: {
    pdfGenerator: pdfGeneratorTool,
    documentParser: documentParserTool
  },
  workflows: {
    formGeneration: formGenerationWorkflow,
    contractAnalysis: contractAnalysisWorkflow
  },
  agents: mastra.agents  // Auto-converts to tools named `ask_<agentKey>`
});

// Expose via Express HTTP endpoint
app.all('/mcp', async (req, res) => {
  const url = new URL(req.url, `http://${req.headers.host}`);
  await mastraMcpServer.startHTTP({ url, httpPath: '/mcp', req, res });
});
```

### MCP Transport Types

**stdio (local subprocess):** Use for MCP servers running as local processes
```typescript
servers: {
  myServer: {
    command: 'node',
    args: ['path/to/server.js'],
    env: { MY_VAR: 'value' }
  }
}
```

**HTTP (remote server):** Use for MCP servers accessible via URL
```typescript
servers: {
  remoteServer: {
    url: new URL('https://mcp.example.com/endpoint')
  }
}
```

### MCP Configuration in mastra.config.ts

```typescript
import { MCPClient } from '@mastra/mcp';
import { Mastra } from '@mastra/core';

const mcpClient = new MCPClient({
  id: 'mastra-mcp-client',
  servers: {
    wikipedia: {
      command: 'npx',
      args: ['-y', '@modelcontextprotocol/server-wikipedia']
    }
  }
});

export const mastra = new Mastra({
  storage,
  agents: {
    researchAgent: new Agent({
      id: 'research-agent',
      tools: await mcpClient.listTools()
    })
  }
});
```

### MCP Tool Discovery and Testing

```bash
# Verify MCP server is available
npx -y @modelcontextprotocol/server-wikipedia

# Check tools are loaded in Mastra
curl http://localhost:3000/api/agents/research-agent/tools

# Test MCP tool via agent
curl -X POST http://localhost:3000/api/agents/research-agent/generate \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"Search Wikipedia for Mastra framework"}]}'
```

---

## Multi-LLM Provider Configuration (LiteLLM)

### Basic Provider Setup

```typescript
const agent = new Agent({
  id: 'multi-model-agent',
  model: {
    provider: 'anthropic',  // or 'openai', 'groq', 'open-router', etc.
    model: 'claude-3-5-sonnet-20241022'
  }
});
```

### Provider-Specific Options

```typescript
// Anthropic with caching
const anthropicAgent = new Agent({
  id: 'anthropic-agent',
  model: {
    provider: 'anthropic',
    model: 'claude-3-5-sonnet-20241022'
  },
  providerOptions: {
    anthropic: {
      cacheControl: true,     // Enable prompt caching
      maxTokens: 4000
    }
  }
});

// OpenAI with extended reasoning
const openaiAgent = new Agent({
  id: 'openai-agent',
  model: {
    provider: 'openai',
    model: 'gpt-4o'
  },
  providerOptions: {
    openai: {
      reasoningEffort: 'high',
      maxTokens: 4000
    }
  }
});

// Groq for fast inference
const groqAgent = new Agent({
  id: 'groq-agent',
  model: {
    provider: 'groq',
    model: 'llama-3.1-70b-versatile'
  }
});
```

### Supported Providers (40+ via LiteLLM)

**Tier 1 (primary for AIForge platform):**
- `anthropic` — `claude-3-5-sonnet-20241022`, `claude-3-opus-20240229`, `claude-opus-4-6`
- `openai` — `gpt-4o`, `gpt-4-turbo`, `gpt-3.5-turbo`

**Tier 2 (cost optimization):**
- `groq` — `llama-3.1-70b-versatile`, `mixtral-8x7b-32768` (fastest inference)
- `open-router` — Any model via `open-router/<model-name>` (aggregator)

**Tier 3 (specialized):**
- `google` — `gemini/gemini-1.5-pro`, `gemini/gemini-flash`
- `cohere` — `command-r-plus`
- `together` — Open source models via Together AI

### Model Selection Pattern

```typescript
// Runtime model switching based on task complexity
function selectModel(taskComplexity: 'simple' | 'complex' | 'creative') {
  const models = {
    simple: { provider: 'groq', model: 'llama-3.1-70b-versatile' },      // Fast + cheap
    complex: { provider: 'anthropic', model: 'claude-opus-4-6' },         // Best reasoning
    creative: { provider: 'anthropic', model: 'claude-3-5-sonnet-20241022' }  // Balanced
  };
  return models[taskComplexity];
}

const agent = new Agent({
  id: 'adaptive-agent',
  model: selectModel('complex')
});
```

### LiteLLM Proxy Configuration

If using LiteLLM proxy (configured in AIForge at port 4040):

```typescript
// Point to LiteLLM proxy instead of provider directly
const agent = new Agent({
  id: 'proxy-agent',
  model: {
    provider: 'openai',  // LiteLLM is OpenAI-compatible
    model: 'gpt-4'
  },
  // Override base URL to point to LiteLLM proxy
  baseURL: process.env.LITELLM_URL || 'http://localhost:4040'
});
```

---

## Tool Development (Full Patterns)

### Basic Tool with External API

```typescript
import { createTool } from '@mastra/core/tools';
import { z } from 'zod';

const samGovLookupTool = createTool({
  id: 'sam-gov-lookup',
  description: 'Search SAM.gov for contract opportunities. Use when user asks about government contracts, RFPs, or federal procurement.',
  inputSchema: z.object({
    keywords: z.string().describe('Search keywords for opportunity matching'),
    naicsCode: z.string().optional().describe('NAICS classification code'),
    limit: z.number().default(10).describe('Maximum results to return (1-100)')
  }),
  outputSchema: z.object({
    opportunities: z.array(z.object({
      id: z.string(),
      title: z.string(),
      postedDate: z.string(),
      responseDeadline: z.string(),
      naicsCode: z.string()
    }))
  }),
  execute: async ({ inputData }) => {
    const params = new URLSearchParams({
      api_key: process.env.SAM_GOV_API_KEY!,
      keywords: inputData.keywords,
      limit: inputData.limit.toString()
    });
    if (inputData.naicsCode) {
      params.append('naicsCode', inputData.naicsCode);
    }

    const response = await fetch(`https://api.sam.gov/opportunities/v2/search?${params}`);
    const data = await response.json();

    return {
      opportunities: data.opportunitiesData.map((opp: any) => ({
        id: opp.noticeId,
        title: opp.title,
        postedDate: opp.postedDate,
        responseDeadline: opp.responseDeadLine,
        naicsCode: opp.naicsCode
      }))
    };
  }
});
```

### Database-Backed Tool

```typescript
import { db } from '../config/database.config.js';
import { companies } from '../db/schema.js';
import { eq } from 'drizzle-orm';

const getCompanyDataTool = createTool({
  id: 'get-company-data',
  description: 'Retrieve company information from the AIForge database.',
  inputSchema: z.object({
    companyId: z.string().uuid()
  }),
  outputSchema: z.object({
    company: z.object({
      name: z.string(),
      duns: z.string(),
      cageCode: z.string(),
      certifications: z.array(z.string())
    })
  }),
  execute: async ({ inputData }) => {
    const rows = await db
      .select()
      .from(companies)
      .where(eq(companies.id, inputData.companyId));

    if (rows.length === 0) {
      throw new Error(`Company ${inputData.companyId} not found`);
    }

    return { company: rows[0] };
  }
});
```

### Microsandbox Integration Tool

```typescript
const microsandboxTool = createTool({
  id: 'execute-skill',
  description: 'Execute user-defined skill code in the secure Microsandbox.',
  inputSchema: z.object({
    skillCode: z.string(),
    input: z.record(z.any())
  }),
  outputSchema: z.object({
    output: z.any(),
    logs: z.array(z.string())
  }),
  execute: async ({ inputData }) => {
    const response = await fetch('http://localhost:5000/api/execute', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${process.env.MICROSANDBOX_TOKEN}`
      },
      body: JSON.stringify({
        code: inputData.skillCode,
        input: inputData.input,
        timeout: 30000
      })
    });

    return await response.json();
  }
});
```

---

## Agent Tool Composition

### Combining MCP and Custom Tools

```typescript
const researchAgent = new Agent({
  id: 'research-agent',
  name: 'Research Assistant',
  instructions: 'Help users research topics using multiple sources. Always cite your sources.',
  model: {
    provider: 'openai',
    model: 'gpt-4'
  },
  tools: {
    // MCP tools (Wikipedia, GitHub, etc.)
    ...await mcpClient.listTools(),
    // Custom tools
    databaseQuery: databaseQueryTool,
    samGovLookup: samGovLookupTool,
    microsandbox: microsandboxTool
  }
});
```

### Agent with Memory and Tools

```typescript
import { Agent } from '@mastra/core';

const agentWithMemory = new Agent({
  id: 'memory-agent',
  name: 'Memory-Enabled Agent',
  instructions: 'Remember previous conversations and user preferences.',
  model: {
    provider: 'openai',
    model: 'gpt-4'
  },
  memory: {
    enabled: true,
    maxMessages: 100
  },
  tools: {
    userProfile: getUserProfileTool,
    updatePreferences: updatePreferencesTool
  }
});
```

### Streaming Agent Responses

```typescript
// Server-side streaming via Express
app.post('/api/agents/:id/stream', async (req, res) => {
  const agent = mastra.agents[req.params.id];

  res.setHeader('Content-Type', 'text/event-stream');
  res.setHeader('Cache-Control', 'no-cache');
  res.setHeader('Connection', 'keep-alive');

  const stream = await agent.stream({
    prompt: req.body.prompt,
    context: req.body.context
  });

  for await (const chunk of stream) {
    res.write(`data: ${JSON.stringify(chunk)}\n\n`);
  }

  res.end();
});
```

---

## Troubleshooting MCP Issues

| Problem | Likely Cause | Fix |
|---------|-------------|-----|
| `mcpClient.listTools()` returns empty | Server not running or not registered | Verify server command works standalone: `npx -y <server-package>` |
| Tool not available after config change | Server not restarted | Restart Mastra server after any MCP config changes |
| HTTP MCP server connection refused | URL incorrect or server down | Verify URL and check server logs |
| `stdio` server fails to start | Missing package or wrong args | Test `npx -y <package>` independently in terminal |
| Tools registered but not used by agent | Agent instructions don't reference tools | Update instructions to describe when to use each tool |

---

## MCP & Multi-LLM Checklist

- [ ] MCPClient or MCPServer properly configured in `mastra.config.ts`
- [ ] Transport type correct (stdio for local subprocess, HTTP for remote)
- [ ] Tools/workflows/agents registered in MCPServer if exposing
- [ ] Authentication configured if needed (API keys in env vars)
- [ ] Tools tested independently before agent integration
- [ ] Server restart performed after config changes
- [ ] LLM provider API keys set in environment variables
- [ ] Provider and model name correctly formatted (`provider/model-name`)
- [ ] Model selection appropriate for task complexity (see spec rationale)
