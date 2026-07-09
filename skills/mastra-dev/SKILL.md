---
name: mastra-dev
description: Ultimate Mastra Framework development toolkit for agent orchestration, workflow design, and MCP integration
args:
  command:
    type: string
    description: Operation to perform (create-agent, create-workflow, server, mcp, etc.)
    required: true
  options:
    type: object
    description: Command-specific options
    required: false
---

# Ultimate Mastra Development Toolkit

A comprehensive skill for developing, managing, and debugging Mastra Framework applications: automated scaffolding (agents, workflows, tools), server/Studio lifecycle, MCP integration, and analysis/debugging via the `/mastra-dev` CLI (`skill.sh` → `scripts/main.py`). Targets the AIForge Mastra app at `apps/mastra` (configurable via `.mastra-dev-config.json`).

## Quick Start

```bash
/mastra-dev server status                                    # Check Mastra server
/mastra-dev analyze                                          # Analyze current setup
/mastra-dev create-agent --name "contract-analyzer" --model "anthropic/claude-3-5-sonnet-20241022"
/mastra-dev create-workflow --name "form-generation" --description "Auto-fill government forms"
/mastra-dev server start                                     # Start server (port 6000)
/mastra-dev studio start                                     # Observability UI (port 4111)
```

## Command Index

| Area | Commands | What they do |
|---|---|---|
| Agents | `create-agent`, `list-agents`, `analyze-agent` | Scaffold agent in `src/agents/`, auto-register in `mastra.config.ts`; inventory and inspect agents |
| Workflows | `create-workflow`, `add-step`, `test-workflow`, `list-workflows` | Scaffold DAG workflows in `src/workflows/` (`.then()`/`.parallel()`/`.branch()`), add typed steps, execute with test input |
| Tools | `create-tool`, `list-tools`, `test-tool` | Scaffold Zod-validated tools in `src/tools/`, test independently |
| Server | `server start\|stop\|status\|logs`, `studio start` | Manage Express server (port 6000, logs at `apps/mastra/logs/mastra.log`) and Mastra Studio (port 4111) |
| MCP | `mcp add-client`, `mcp configure-server`, `mcp list-servers`, `mcp test`, `mcp remove-client` | Consume external MCP servers (stdio or HTTP) and expose Mastra agents/workflows/tools via `mcp.config.ts` |
| Analysis | `analyze`, `validate`, `debug-workflow`, `show-graph` | Full setup scan, config validation, execution debugging from DB logs, ASCII DAG visualization |

Full flag lists, generated-file examples, and sample outputs per command: `references/command-reference.md`.

## Routing: mastra-* Satellite Skills

This skill is the CLI/scaffolding hub. For Mastra concepts, APIs, and hand-written code patterns, route to the satellite skill for the topic — each carries a full guide that loads only when invoked:

| Topic | Skill |
|---|---|
| Agent creation, tools-on-agents, networks, processors, guardrails, voice, structured output | `mastra-agents` |
| Workflow DAGs, control flow, suspend/resume, HITL, time travel, state | `mastra-workflows` |
| MCPClient/MCPServer code, tool creation and publishing | `mastra-mcp-tools` |
| Memory: storage backends, history, working/semantic memory, threads | `mastra-memory` |
| RAG: chunking, embedding, vector DBs, retrieval, GraphRAG | `mastra-rag` |
| Streaming: agent/workflow/tool streams, SSE, AI SDK React/Next.js | `mastra-streaming` |
| Evals: scorers, datasets, experiments, CI | `mastra-evals` |
| Deployment: server adapters, auth, middleware, client SDK, cloud | `mastra-deploy` |
| Workspace: filesystem providers, sandbox execution, skills, search | `mastra-workspace` |
| Team orchestration and execution planning for Mastra work | `mastra-planning` |

## References (load on demand)

- `references/cli-faq.md` — the five core how-do-I questions (create agent, build multi-step workflow, integrate MCP servers, debug execution, inventory constructs) with full invocations. Read when a user asks "how do I X with /mastra-dev".
- `references/command-reference.md` — per-command docs for all six areas: every flag, generated TypeScript, sample outputs. Read before running an unfamiliar command or explaining its behavior.
- `references/configuration.md` — `.mastra-dev-config.json` options, AIForge app integration (directory layout, auto-registration), and the four `templates/*.template.ts` variables. Read when configuring paths/ports or debugging generation output.
- `references/best-practices.md` — DO/DON'T checklists for agents, workflows, tools, MCP, and testing. Read before designing new constructs.
- `references/troubleshooting.md` — ten common issues (server down, unregistered agent, schema errors, MCP timeouts, Studio blank, TS/DB/permission/Python errors, workflow not exposed) with fixes. Read when a command or the server fails.
- `references/use-cases.md` — three end-to-end walkthroughs (contract analysis system, form auto-filling, multi-agent research). Read for a full build recipe to adapt.

## Metadata

- **Version:** 1.0.0
- **Status:** Active
- **Author:** AIForge Development Team
- **Last Updated:** 2026-02-11
- **Dependencies:** Python 3.x (stdlib only), Mastra Framework, TypeScript, Node.js 20+
- **Compatibility:** Mastra v1.3.0+, AIForge monorepo structure
- **License:** MIT

## Related Skills

- `/feature-new` - Complete feature development workflow
- `/security-quality-assess` - Security vulnerability scanning
- `/pm-db` - Project management database

## Support

For issues, questions, or contributions:
- **GitHub Issues:** https://github.com/your-org/aiforge/issues
- **Documentation:** /home/artsmc/applications/low-code/job-queue/product-forge/
- **Mastra Docs:** https://mastra.ai/docs
