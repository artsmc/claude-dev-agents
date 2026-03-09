#!/usr/bin/env bash
################################################################################
# mastra-mcp-tools - Mastra MCP & Tool Integration Skill
#
# Outputs comprehensive guidance for MCP (Model Context Protocol) integration,
# tool creation, RAG tools, and registering everything with Mastra.
# Usage: bash skill.sh
################################################################################

cat << 'SKILL_EOF'
# Mastra MCP & Tool Integration Guide

## Table of Contents
1. MCP Overview
2. MCPClient - Consuming External Tools
3. MCPServer - Exposing Mastra as MCP
4. Publishing MCP Servers
5. Tool Creation (createTool)
6. RAG Tools
7. Mastra Registration
8. Best Practices
9. Debugging & Troubleshooting

---

## 1. MCP Overview

The **Model Context Protocol (MCP)** is an open standard for AI tool interoperability. Mastra supports MCP in two ways:

1. **MCPClient** - Connect to external MCP servers and use their tools in your agents
2. **MCPServer** - Expose your Mastra tools and agents as an MCP server

### How MCP Works

```
+---------------+    MCP Protocol    +---------------+
|  MCP Client   |<------------------>|  MCP Server   |
|  (Consumer)   |  Tool Discovery    |  (Provider)   |
|               |  Tool Invocation   |               |
|  e.g. Mastra  |  Tool Results      |  e.g. GitHub  |
|       Agent   |                    |       Server  |
+---------------+                    +---------------+
```

**Transports:**
- **stdio** - Communication via stdin/stdout (local processes, CLI tools)
- **HTTP/SSE** - Communication via HTTP with Server-Sent Events (remote servers)
- **Streamable HTTP** - Newer transport for serverless-compatible communication

Docs: https://mastra.ai/docs/tools-mcp/mcp-overview

---

## 2. MCPClient - Consuming External Tools

Use `MCPClient` to connect to external MCP servers and make their tools available to your agents.

### Basic Setup

```typescript
import { MCPClient } from '@mastra/mcp';

const mcpClient = new MCPClient({
  servers: {
    // stdio transport - local CLI tools
    filesystem: {
      command: 'npx',
      args: ['-y', '@modelcontextprotocol/server-filesystem', '/path/to/dir'],
    },
    // HTTP/SSE transport - remote servers
    weather: {
      url: new URL('https://weather-mcp.example.com/sse'),
      requestInit: {
        headers: {
          Authorization: `Bearer ${process.env.WEATHER_API_KEY}`,
        },
      },
    },
  },
  timeout: 60000, // Global timeout in ms (default: 60000)
});
```

### Constructor Options

```typescript
new MCPClient({
  id?: string,         // Unique ID to prevent memory leaks with duplicate configs
  servers: {           // Map of server identifiers to configurations
    [name: string]: {
      // stdio transport
      command: string,
      args?: string[],
      env?: Record<string, string>,
    } | {
      // HTTP transport
      url: URL,
      requestInit?: RequestInit,
      eventSourceInit?: EventSourceInit,
      fetch?: typeof fetch,     // Custom fetch for token refresh
      authProvider?: MCPOAuthClientProvider, // OAuth support
    }
  },
  timeout?: number,    // Global timeout (default: 60000)
});
```

### Getting Tools for Agent Use

```typescript
// listTools() returns all tools from all servers with namespaced names
// Format: serverName_toolName (e.g., "filesystem_readFile")
const tools = await mcpClient.listTools();

const agent = new Agent({
  id: 'mcp-agent',
  name: 'MCP-Enabled Agent',
  instructions: 'You have access to filesystem and weather tools.',
  model: { provider: 'ANTHROPIC', name: 'claude-sonnet-4-20250514' },
  tools,
});
```

### Getting Toolsets (Dynamic/Per-Request)

```typescript
// listToolsets() returns tools that can be passed to agent.generate() or .stream()
// Useful for multi-tenant systems where config varies per user
const toolsets = await mcpClient.listToolsets();

const result = await agent.generate('Read the readme file', {
  toolsets,
});
```

### stdio Transport Examples

```typescript
const mcpClient = new MCPClient({
  servers: {
    // Filesystem access
    filesystem: {
      command: 'npx',
      args: ['-y', '@modelcontextprotocol/server-filesystem', '/tmp'],
    },
    // GitHub integration
    github: {
      command: 'npx',
      args: ['-y', '@modelcontextprotocol/server-github'],
      env: {
        GITHUB_TOKEN: process.env.GITHUB_TOKEN!,
      },
    },
    // Brave Search
    braveSearch: {
      command: 'npx',
      args: ['-y', '@modelcontextprotocol/server-brave-search'],
      env: {
        BRAVE_API_KEY: process.env.BRAVE_API_KEY!,
      },
    },
    // Postgres database
    postgres: {
      command: 'npx',
      args: ['-y', '@modelcontextprotocol/server-postgres', process.env.DATABASE_URL!],
    },
    // Custom local server
    myServer: {
      command: 'node',
      args: ['./my-mcp-server/dist/index.js'],
      env: { MY_SECRET: process.env.MY_SECRET! },
    },
  },
});
```

### HTTP/SSE Transport Examples

```typescript
const mcpClient = new MCPClient({
  servers: {
    // Remote API with auth headers
    myRemoteApi: {
      url: new URL('https://api.example.com/mcp/sse'),
      requestInit: {
        headers: {
          Authorization: `Bearer ${process.env.API_TOKEN}`,
          'X-API-Version': '2',
        },
      },
    },
    // OAuth-protected server
    oauthServer: {
      url: new URL('https://protected.example.com/mcp'),
      authProvider: myOAuthProvider, // MCPOAuthClientProvider instance
    },
    // Custom fetch for dynamic auth
    dynamicAuth: {
      url: new URL('https://api.example.com/mcp'),
      fetch: async (url, init) => {
        const token = await refreshToken();
        return fetch(url, {
          ...init,
          headers: { ...init?.headers, Authorization: `Bearer ${token}` },
        });
      },
    },
  },
});
```

### MCPClient Resources

```typescript
// Access resources from MCP servers
const resources = await mcpClient.resources.list();
// Returns resources grouped by server name

// Read a specific resource
const content = await mcpClient.resources.read('serverName', 'resource://uri');

// Subscribe to resource updates
await mcpClient.resources.subscribe('serverName', 'resource://uri');
mcpClient.resources.onUpdated('serverName', (notification) => {
  console.log('Resource updated:', notification);
});
mcpClient.resources.onListChanged('serverName', () => {
  console.log('Resource list changed');
});
```

### MCPClient Prompts

```typescript
// List available prompts
const prompts = await mcpClient.prompts.list();

// Get a specific prompt
const prompt = await mcpClient.prompts.get({
  serverName: 'myServer',
  name: 'greeting-prompt',
  args: { userName: 'Alice' },
});
```

### MCPClient Cleanup

```typescript
// Disconnect from all servers and clean up resources
await mcpClient.disconnect();
```

**Important:** Creating multiple MCPClient instances with identical configurations without an `id` will throw an error to prevent memory leaks. Either provide unique `id` values or disconnect before recreating.

Docs: https://mastra.ai/reference/tools/mcp-client

---

## 3. MCPServer - Exposing Mastra as MCP

Use `MCPServer` to expose your Mastra tools and agents as an MCP server that clients like Cursor, Claude Desktop, or Windsurf can connect to.

### Basic MCPServer Setup

```typescript
import { MCPServer } from '@mastra/mcp';
import { createTool } from '@mastra/core/tools';
import { Agent } from '@mastra/core/agent';
import { z } from 'zod';

const searchTool = createTool({
  id: 'search',
  description: 'Search for information',
  inputSchema: z.object({ query: z.string() }),
  outputSchema: z.object({ results: z.array(z.string()) }),
  execute: async ({ context }) => {
    return { results: [`Result for: ${context.query}`] };
  },
});

const assistant = new Agent({
  id: 'assistant',
  name: 'Assistant',
  description: 'A helpful assistant', // REQUIRED for MCPServer exposure
  instructions: 'You are a helpful assistant.',
  model: { provider: 'ANTHROPIC', name: 'claude-sonnet-4-20250514' },
  tools: { searchTool },
});

// MCPServer takes tools and agents directly (NOT a Mastra instance)
const mcpServer = new MCPServer({
  name: 'my-assistant-mcp',
  version: '1.0.0',
  tools: { searchTool },
  agents: { assistant },
});
```

### Constructor Parameters

```typescript
new MCPServer({
  // Required
  name: string,          // Display name for the server
  version: string,       // Semantic version
  tools: ToolsInput,     // Tool definitions to expose

  // Optional
  id?: string,           // Unique identifier
  agents?: Record<string, Agent>,     // Agents (become ask_<key> tools)
  workflows?: Record<string, Workflow>, // Workflows (become run_<key> tools)
  description?: string,
  instructions?: string,

  // Advanced
  resources?: MCPServerResources,  // Expose data resources
  prompts?: MCPServerPrompts,      // Expose prompt templates
});
```

### Agent and Workflow Conversion

- **Agents** become tools named `ask_<agentKey>` (e.g., `ask_assistant`)
  - Agent MUST have a non-empty `description` property or initialization fails
- **Workflows** become tools named `run_<workflowKey>` (e.g., `run_analyzeWorkflow`)

### Starting the Server

```typescript
// stdio transport (for CLI/desktop integration like Cursor, Claude Desktop)
await mcpServer.startStdio();

// SSE transport (for HTTP integration with existing web server)
// Called from your web server's SSE route handler
app.get('/mcp/sse', (req, res) => {
  mcpServer.startSSE(
    serverUrl,   // Base URL
    ssePath,     // SSE endpoint path
    messagePath, // Message endpoint path
    req,
    res,
  );
});

// Streamable HTTP transport (serverless-compatible)
app.post('/mcp', (req, res) => {
  mcpServer.startHTTP(
    serverUrl,
    httpPath,
    req,
    res,
    { serverless: true }, // Options
  );
});
```

### MCPServer Resources

```typescript
const mcpServer = new MCPServer({
  name: 'my-server',
  version: '1.0.0',
  tools: { searchTool },
  resources: {
    listResources: async () => [
      { uri: 'docs://readme', name: 'README', mimeType: 'text/markdown' },
    ],
    readResource: async (uri) => {
      if (uri === 'docs://readme') {
        return { contents: [{ text: '# My Docs', uri, mimeType: 'text/markdown' }] };
      }
      throw new Error('Resource not found');
    },
  },
});

// Notify clients of resource changes
mcpServer.resources.notifyUpdated({ uri: 'docs://readme' });
mcpServer.resources.notifyListChanged();
```

### MCPServer Prompts

```typescript
const mcpServer = new MCPServer({
  name: 'my-server',
  version: '1.0.0',
  tools: { searchTool },
  prompts: {
    listPrompts: async () => [
      { name: 'greeting', description: 'A greeting prompt' },
    ],
    getPrompt: async ({ name, args }) => {
      if (name === 'greeting') {
        return {
          messages: [
            { role: 'user', content: { type: 'text', text: `Hello ${args?.name}!` } },
          ],
        };
      }
      throw new Error('Prompt not found');
    },
  },
});
```

### Information Methods

```typescript
// Get server metadata
const info = mcpServer.getServerInfo();

// Get list of available tools
const toolList = mcpServer.getToolListInfo();

// Execute a tool directly
const result = await mcpServer.executeTool('search', { query: 'hello' });
```

Docs: https://mastra.ai/reference/tools/mcp-server

---

## 4. Publishing MCP Servers

### 1. npm Package (stdio transport)

```json
{
  "name": "@myorg/my-mcp-server",
  "version": "1.0.0",
  "bin": {
    "my-mcp-server": "./dist/index.js"
  },
  "files": ["dist"],
  "scripts": {
    "build": "tsc",
    "prepublishOnly": "npm run build"
  }
}
```

```typescript
#!/usr/bin/env node
// src/index.ts
import { MCPServer } from '@mastra/mcp';
import { createTool } from '@mastra/core/tools';
import { z } from 'zod';

const myTool = createTool({
  id: 'my-tool',
  description: 'Does something useful',
  inputSchema: z.object({ input: z.string() }),
  outputSchema: z.object({ output: z.string() }),
  execute: async ({ context }) => {
    return { output: `Processed: ${context.input}` };
  },
});

const server = new MCPServer({
  name: 'my-mcp-server',
  version: '1.0.0',
  tools: { myTool },
});

server.startStdio();
```

```bash
# Build and publish
npm run build
npm publish

# Users consume via MCPClient:
# { command: 'npx', args: ['-y', '@myorg/my-mcp-server'] }
```

### 2. HTTP/SSE Server (Express)

```typescript
import express from 'express';
import { MCPServer } from '@mastra/mcp';

const app = express();

const mcpServer = new MCPServer({
  name: 'my-server',
  version: '1.0.0',
  tools: { myTool },
});

const serverUrl = 'http://localhost:8080';
const ssePath = '/sse';
const messagePath = '/message';

app.get(ssePath, (req, res) => {
  mcpServer.startSSE(serverUrl, ssePath, messagePath, req, res);
});

app.post(messagePath, (req, res) => {
  // Handle messages from MCP clients
});

app.listen(8080);
```

### 3. Docker (HTTP)

```dockerfile
FROM node:20-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --production
COPY dist ./dist
EXPOSE 8080
CMD ["node", "dist/index.js"]
```

Docs: https://mastra.ai/docs/mcp/publishing-mcp-server

---

## 5. Tool Creation (createTool)

### Basic Tool

```typescript
import { createTool } from '@mastra/core/tools';
import { z } from 'zod';

const searchTool = createTool({
  id: 'web-search',
  description: 'Search the web for information',
  inputSchema: z.object({
    query: z.string().describe('Search query'),
    maxResults: z.number().default(5).describe('Max results to return'),
  }),
  outputSchema: z.object({
    results: z.array(z.object({
      title: z.string(),
      url: z.string(),
      snippet: z.string(),
    })),
  }),
  execute: async ({ context }) => {
    // context contains the validated input data
    const response = await fetch(
      `https://api.search.com/search?q=${encodeURIComponent(context.query)}&limit=${context.maxResults}`
    );
    const data = await response.json();
    return { results: data.results };
  },
});
```

### createTool Parameters

```typescript
createTool({
  // Required
  id: string,              // Unique tool identifier
  description: string,     // What the tool does (agents read this)
  execute: async (params) => { ... }, // Tool logic

  // Optional
  inputSchema?: ZodSchema, // Zod schema for input validation
  outputSchema?: ZodSchema,// Zod schema for output validation
  suspendSchema?: ZodSchema, // For suspend/resume patterns
  resumeSchema?: ZodSchema,  // For resume data validation
  requireApproval?: boolean,  // Require explicit approval before execution
  requestContextSchema?: ZodSchema, // Validate request context values

  // MCP annotations (when exposed via MCPServer)
  mcp?: {
    title?: string,           // Human-readable display name
    readOnlyHint?: boolean,   // Read-only behavior
    destructiveHint?: boolean,// Destructive operations
    idempotentHint?: boolean, // Idempotent behavior
    openWorldHint?: boolean,  // External system interaction
  },
});
```

### Execute Function Parameters

The `execute` function receives an object with:

```typescript
execute: async ({
  context,         // Validated input (matches inputSchema)
  runtimeContext,  // Runtime context (API keys, user info)
  tracingContext,  // Tracing/observability data
  abortSignal,    // Request cancellation signal
}) => {
  // Return value must match outputSchema
  return { ... };
}
```

### Lifecycle Hooks

```typescript
createTool({
  id: 'my-tool',
  description: 'Tool with lifecycle hooks',
  inputSchema: z.object({ query: z.string() }),
  outputSchema: z.object({ result: z.string() }),

  // Called when streaming begins
  onInputStart: ({ toolCallId, abortSignal }) => {
    console.log('Input streaming started');
  },

  // Called for each incoming text chunk
  onInputDelta: ({ toolCallId, delta, abortSignal }) => {
    console.log('Received chunk:', delta);
  },

  // Called when complete validated input arrives
  onInputAvailable: ({ toolCallId, input, abortSignal }) => {
    console.log('Complete input:', input);
  },

  // Called after successful execution
  onOutput: ({ toolCallId, output, abortSignal }) => {
    console.log('Tool output:', output);
  },

  execute: async ({ context }) => {
    return { result: `Processed: ${context.query}` };
  },
});
```

### Tool with Error Handling

```typescript
const apiTool = createTool({
  id: 'fetch-api',
  description: 'Fetch data from an external API',
  inputSchema: z.object({
    url: z.string().url().describe('API endpoint URL'),
    method: z.enum(['GET', 'POST']).default('GET'),
    body: z.record(z.any()).optional(),
  }),
  outputSchema: z.object({
    data: z.any(),
    statusCode: z.number(),
    success: z.boolean(),
    error: z.string().optional(),
  }),
  execute: async ({ context }) => {
    try {
      const response = await fetch(context.url, {
        method: context.method,
        headers: { 'Content-Type': 'application/json' },
        body: context.body ? JSON.stringify(context.body) : undefined,
      });
      const data = await response.json();
      return { data, statusCode: response.status, success: response.ok };
    } catch (error) {
      return {
        data: null,
        statusCode: 0,
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error',
      };
    }
  },
});
```

Docs: https://mastra.ai/reference/tools/create-tool

---

## 6. RAG Tools

Mastra provides pre-built tools for Retrieval-Augmented Generation (RAG) workflows.

### Vector Query Tool

```typescript
import { createVectorQueryTool } from '@mastra/rag';

const vectorTool = createVectorQueryTool({
  vectorStore: myVectorStore,
  indexName: 'my-docs',
  embedModel: {
    provider: 'OPEN_AI',
    model: 'text-embedding-3-small',
  },
  topK: 5,
  filter: { category: 'documentation' },
});
```

### Full RAG Pipeline

```typescript
import { Agent } from '@mastra/core/agent';
import { createVectorQueryTool } from '@mastra/rag';
import { PgVector } from '@mastra/pg';

const vectorStore = new PgVector({
  connectionString: process.env.DATABASE_URL!,
});

const queryTool = createVectorQueryTool({
  vectorStore,
  indexName: 'company-docs',
  embedModel: { provider: 'OPEN_AI', model: 'text-embedding-3-small' },
  topK: 10,
});

const ragAgent = new Agent({
  id: 'rag-agent',
  name: 'Knowledge Base Agent',
  description: 'Answers questions from the knowledge base',
  instructions: `You are a knowledge base assistant. Use the vector query tool
    to search for relevant information before answering questions.`,
  model: { provider: 'ANTHROPIC', name: 'claude-sonnet-4-20250514' },
  tools: { queryTool },
});
```

### Vector Store Providers

| Provider    | Package             | Description                    |
|------------|---------------------|--------------------------------|
| PgVector   | `@mastra/pg`        | PostgreSQL with pgvector       |
| Pinecone   | `@mastra/pinecone`  | Pinecone vector database       |
| Qdrant     | `@mastra/qdrant`    | Qdrant vector database         |
| Chroma     | `@mastra/chroma`    | ChromaDB vector database       |
| Weaviate   | `@mastra/weaviate`  | Weaviate vector database       |
| Astra DB   | `@mastra/astra`     | DataStax Astra DB              |
| Upstash    | `@mastra/upstash`   | Upstash Vector                 |
| MongoDB    | `@mastra/mongodb`   | MongoDB Atlas Vector Search    |
| Milvus     | `@mastra/milvus`    | Milvus vector database         |
| Cloudflare | `@mastra/vectorize` | Cloudflare Vectorize           |

Docs: https://mastra.ai/docs/rag/overview

---

## 7. Mastra Registration

Register all components with the Mastra instance for unified access.

### Complete Registration Example

```typescript
import { Mastra } from '@mastra/core';
import { Agent } from '@mastra/core/agent';
import { createTool } from '@mastra/core/tools';
import { MCPClient, MCPServer } from '@mastra/mcp';
import { Memory } from '@mastra/memory';
import { PostgresStore, PgVector } from '@mastra/pg';
import { createVectorQueryTool } from '@mastra/rag';
import { registerApiRoute } from '@mastra/core/server';
import { z } from 'zod';

// --- Tools ---
const searchTool = createTool({
  id: 'search',
  description: 'Search the web',
  inputSchema: z.object({ query: z.string() }),
  outputSchema: z.object({ results: z.array(z.string()) }),
  execute: async ({ context }) => ({ results: [] }),
});

// --- RAG Tools ---
const vectorStore = new PgVector({ connectionString: process.env.DATABASE_URL! });
const vectorTool = createVectorQueryTool({
  vectorStore,
  indexName: 'documents',
  embedModel: { provider: 'OPEN_AI', model: 'text-embedding-3-small' },
});

// --- MCP Client ---
const mcpClient = new MCPClient({
  servers: {
    filesystem: {
      command: 'npx',
      args: ['-y', '@modelcontextprotocol/server-filesystem', '/data'],
    },
  },
});
const mcpTools = await mcpClient.listTools();

// --- Memory ---
const memory = new Memory({
  storage: new PostgresStore({ connectionString: process.env.DATABASE_URL! }),
  vector: vectorStore,
  embedder: { provider: 'OPEN_AI', model: 'text-embedding-3-small' },
});

// --- Agents ---
const researchAgent = new Agent({
  id: 'researcher',
  name: 'Research Agent',
  description: 'Researches topics using available tools',
  instructions: 'Research topics using available tools.',
  model: { provider: 'ANTHROPIC', name: 'claude-sonnet-4-20250514' },
  tools: { searchTool, vectorTool, ...mcpTools },
  memory,
});

const assistantAgent = new Agent({
  id: 'assistant',
  name: 'General Assistant',
  description: 'Helps users with general questions',
  instructions: 'Help users with general questions.',
  model: { provider: 'ANTHROPIC', name: 'claude-sonnet-4-20250514' },
  memory,
});

// --- Mastra Instance ---
export const mastra = new Mastra({
  agents: {
    researcher: researchAgent,
    assistant: assistantAgent,
  },
  tools: {
    searchTool,
    vectorTool,
    ...mcpTools,
  },
  vectors: {
    documents: vectorStore,
  },
  server: {
    apiRoutes: [
      registerApiRoute('/custom', {
        method: 'GET',
        handler: async (c) => {
          return c.json({ status: 'ok' });
        },
      }),
    ],
  },
  logger: {
    level: process.env.NODE_ENV === 'production' ? 'info' : 'debug',
  },
});

// --- MCPServer (optional: expose as MCP) ---
const mcpServer = new MCPServer({
  name: 'my-app-mcp',
  version: '1.0.0',
  tools: { searchTool, vectorTool },
  agents: { researcher: researchAgent, assistant: assistantAgent },
});

// Start as stdio server for CLI integration
await mcpServer.startStdio();
```

---

## 8. Best Practices

### Tool Design
- **Always validate schemas with Zod** - Use `z.object()` for both input and output
- **Use `.describe()` on ALL schema fields** - The LLM reads descriptions to decide when/how to use tools
- **Write clear tool descriptions** - Be specific about capabilities and limitations
- **Keep tools focused** - One tool should do one thing well
- **Use meaningful IDs** - Tool IDs should be descriptive: `web-search`, not `tool1`

### MCP Integration
- **Use stdio transport for local tools** - Lower latency, no network overhead
- **Use HTTP/SSE transport for remote tools** - Enables cross-network tool sharing
- **Handle connection failures gracefully** - MCP servers may be unavailable
- **Set appropriate timeouts** - Tool execution should have timeouts
- **Version your MCP servers** - Use semantic versioning for breaking changes
- **Provide unique `id` values** when creating multiple MCPClient instances

### Schema Design
```typescript
// Good: Descriptive schema with defaults
inputSchema: z.object({
  query: z.string().min(1).describe('Search query - be specific for better results'),
  maxResults: z.number().min(1).max(50).default(10).describe('Number of results (1-50)'),
  language: z.enum(['en', 'es', 'fr']).default('en').describe('Result language'),
})

// Bad: Vague schema without descriptions
inputSchema: z.object({
  q: z.string(),
  n: z.number(),
  lang: z.string(),
})
```

### Testing
- **Test tools independently** before integrating with agents
- **Validate schemas** by parsing test data through them
- **Use MCP annotations** (readOnlyHint, destructiveHint) to help clients understand behavior

```typescript
// Test a tool directly
const result = await myTool.execute({
  context: { query: 'test' },
});
console.log('Result:', result);

// Test schema validation
const parsed = myTool.inputSchema.safeParse({ query: 'test' });
if (!parsed.success) console.error('Schema error:', parsed.error);
```

---

## 9. Debugging & Troubleshooting

### Common Issues

1. **MCP server connection failed**
   - Verify the command/path exists: `which npx`, `ls ./my-server/dist/index.js`
   - Check environment variables are set for the MCP server process
   - For HTTP transport, verify the URL is accessible
   - Check firewall rules for HTTP transport

2. **Tools not appearing in agent**
   - Verify `await mcpClient.listTools()` returns tools (check with `console.log`)
   - Ensure tools are spread into the agent's tools object: `tools: { ...mcpTools }`
   - Check MCP server is exposing tools correctly

3. **MCPClient memory leak error**
   - Provide unique `id` values when creating multiple instances with identical configs
   - Or call `await mcpClient.disconnect()` before recreating

4. **MCPServer agent initialization fails**
   - Ensure all agents have a non-empty `description` property
   - Agents without descriptions will cause MCPServer initialization to fail

5. **Tool execution timeout**
   - Set `timeout` in MCPClient constructor
   - Check if the tool's underlying service is responsive

6. **Schema validation errors**
   - Test schema independently: `schema.safeParse(data)`
   - Check for required fields the LLM might not provide
   - Use `.optional()` and `.default()` for non-critical fields

### Debugging Commands

```bash
# Test MCP server locally (stdio)
echo '{"jsonrpc":"2.0","method":"tools/list","id":1}' | npx @myorg/my-mcp-server

# Test MCP server (HTTP)
curl http://localhost:8080/sse
```

---

## Quick Reference Links

- MCP Overview: https://mastra.ai/docs/tools-mcp/mcp-overview
- MCPClient Reference: https://mastra.ai/reference/tools/mcp-client
- MCPServer Reference: https://mastra.ai/reference/tools/mcp-server
- createTool Reference: https://mastra.ai/reference/tools/create-tool
- Publishing MCP Servers: https://mastra.ai/docs/mcp/publishing-mcp-server
- Tool Creation Guide: https://mastra.ai/docs/tools-mcp/overview
- Advanced Tool Usage: https://mastra.ai/docs/tools-mcp/advanced-usage
- RAG Overview: https://mastra.ai/docs/rag/overview
- MCP Protocol Spec: https://modelcontextprotocol.io

SKILL_EOF
