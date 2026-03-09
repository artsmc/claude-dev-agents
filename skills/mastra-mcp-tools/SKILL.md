---
name: mastra-mcp-tools
description: Mastra MCP integration guide - MCPClient for consuming tools, MCPServer for exposing agents/workflows, tool creation, and publishing
---

# Mastra MCP (Model Context Protocol) Integration

Comprehensive guide for MCP integration with Mastra. Covers MCPClient for consuming external MCP servers (stdio/HTTP), MCPServer for exposing Mastra agents and workflows as MCP tools, custom tool creation with `createTool()`, and publishing MCP servers.

## Usage

```bash
/mastra-mcp-tools
```

Provides context for:
- `MCPClient` with `listTools()` and `listToolsets()`
- `MCPServer` constructor: `{ name, version, tools, agents }`
- Server methods: `startStdio()`, `startSSE()`, `startHTTP()`
- `createTool()` with `execute: async ({ context }) => {}`
- Agents become `ask_<key>` tools, workflows become `run_<key>` tools
- Tool annotations (`readOnlyHint`, `destructiveHint`)
- Publishing via npm, Docker, or HTTP
