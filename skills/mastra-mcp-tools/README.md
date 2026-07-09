# /mastra-mcp-tools

> Mastra MCP integration guide - MCPClient for consuming tools, MCPServer for exposing agents/workflows, tool creation, and publishing

## What it does

Loads validated patterns for MCP work in Mastra: `MCPClient` for consuming external MCP servers (stdio/HTTP) with `listTools()`/`listToolsets()`, `MCPServer` for exposing Mastra agents (`ask_<key>`) and workflows (`run_<key>`) as MCP tools, `createTool()` with the `{ context }` execute signature, tool annotations, and publishing via npm/Docker/HTTP. One of the ten satellite guides routed to by `/mastra-dev`.

## When it triggers

- "Connect my Mastra agent to an MCP server"
- "Expose my agents/workflows as MCP tools"
- "Write a custom tool with createTool()"
- "startStdio vs startHTTP for MCPServer?"
- "Publish this MCP server"

## Usage

```bash
/mastra-mcp-tools
```

No flags. On-demand guide pattern: `SKILL.md` is a thin stub; the full guide is printed by `bash skill.sh`.

## Context cost

Description always in context (~150 chars); SKILL.md body loads on trigger (~0.9k chars); full guide via `skill.sh` (~27k chars) only when executed.

## Files

| File | Purpose |
|---|---|
| `SKILL.md` | Frontmatter + stub (~0.9k chars) |
| `skill.sh` | Prints the full MCP integration guide (~27k chars) |

## Related skills

- `/mastra-dev` — CLI hub; its `mcp add-client` / `mcp configure-server` commands do the scaffolding
- `/mastra-agents` — tool binding on the agent side
- `/mastra-deploy` — exposing agents over plain HTTP instead of MCP
