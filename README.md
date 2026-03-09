# Claude Dev Agents

**A multi-agent development framework built on Claude Code CLI**

[![Agents: 19](https://img.shields.io/badge/Agents-19-green)](./agents/)
[![Skills: 34](https://img.shields.io/badge/Skills-34-blue)](./skills/)
[![Modules: 5](https://img.shields.io/badge/Modules-5-purple)](./agents/modules/)
[![Zero Dependencies](https://img.shields.io/badge/Dependencies-Zero-green)](#installation)

> Turn Claude Code into a coordinated team of specialized AI agents. 19 agents, 34 skills, model-routed for cost efficiency, with shadow git rollback and cross-agent working memory.

## What This Is

A framework that sits in `~/.claude/` and transforms Claude Code from a single-agent tool into a multi-agent development team. Agents have specialized expertise, model assignments (Opus for deep reasoning, Sonnet for implementation), tool restrictions, and team coordination patterns.

## Quick Start

```bash
# Clone into ~/.claude
git clone https://github.com/artsmc/claude-dev-agents.git ~/.claude

# Verify
ls ~/.claude/agents/    # 19 specialized agents
ls ~/.claude/skills/    # 34 workflow skills
~/.claude/scripts/health-check.sh  # Validate installation
```

Then open Claude Code -- agents and skills are available immediately via `/skill-name` commands.

## Architecture

```
~/.claude/
├── agents/              # 19 specialized agent personas (.md)
│   └── modules/         # 5 extracted deep-reference modules
├── skills/              # 34 workflow skills
├── hooks/               # PreToolUse shadow git snapshots
├── memory-bank/         # 6-file project context (episodic memory)
├── working-memory/      # Cross-agent scratchpad (per-team, session-scoped)
├── scripts/             # Health check, utilities
├── enhancements/        # Research, specs, validation reports
├── lib/                 # Python utilities (project_database.py)
└── projects.db          # SQLite PM-DB (25 tables)
```

## Agents (19)

Every agent has standardized YAML frontmatter with `name`, `model`, and `tools` fields.

### Model Routing

| Model | Count | Agents | Use Case |
|-------|-------|--------|----------|
| Opus | 6 | debugger-specialist, mastra-core-developer, mastra-framework-expert, security-auditor, strategic-planner, team-lead | Deep reasoning, architecture, security analysis |
| Sonnet | 13 | All others | Implementation, review, documentation (~40-60% cheaper) |

### Tool Restriction Profiles

| Profile | Agents | Access |
|---------|--------|--------|
| Read-only | api-designer, nextjs-code-reviewer, strategic-planner, team-lead, technical-writer, mastra-framework-expert | Read, Grep, Glob only |
| Write (no shell) | accessibility-specialist, frontend-developer, spec-writer, ui-developer | Read, Grep, Glob, Write, Edit |
| Full | express-api-developer, database-schema-specialist, debugger-specialist, devops-infrastructure, and others | All tools including Bash |

### Modularized Agents

Three large agents were split into core + loadable modules:

| Agent | Core | Modules |
|-------|------|---------|
| security-auditor | 9KB | `modules/security-auditor-compliance.md`, `modules/security-auditor-pentest.md` |
| mastra-core-developer | 9KB | `modules/mastra-core-developer-workflows.md`, `modules/mastra-core-developer-mcp.md` |
| technical-writer | 9KB | `modules/technical-writer-style.md` |

Modules are loaded on-demand only when the task requires them.

## Skills (34)

### Core Workflows
- `/feature-new` -- Full feature development lifecycle (spec -> design -> code -> test)
- `/feature-continue` -- Resume interrupted feature work
- `/start-phase-plan` -- Strategic planning with user approval
- `/start-phase-execute` -- Structured execution with quality gates
- `/start-phase-execute-team` -- Parallel multi-agent team execution

### Code Quality
- `/security-quality-assess` -- OWASP Top 10 vulnerability scanning (v1.0.0)
- `/code-duplication` -- Deep duplication analysis with refactoring suggestions
- `/architecture-quality-assess` -- Architecture assessment

### Documentation
- `/memory-bank-read` / `/memory-bank-update` / `/memory-bank-sync` -- Project context management
- `/document-hub-initialize` / `/document-hub-update` -- Documentation hub management
- `/spec-plan` -- Feature specification planning
- `/spec-review` -- Specification validation

### Mastra Framework (10 skills)
- `/mastra-dev` -- CLI toolkit for agent orchestration and workflow design
- `/mastra-agents` -- Agent creation, tools, memory, guardrails
- `/mastra-workflows` -- DAG composition, suspend/resume, HITL
- `/mastra-rag` -- Document processing, chunking, embedding, retrieval
- `/mastra-memory` -- Storage backends, semantic recall, thread management
- `/mastra-streaming` -- Agent/workflow streams, SSE, AI SDK integration
- `/mastra-mcp-tools` -- MCP client/server, tool creation, publishing
- `/mastra-deploy` -- Server adapters, auth, middleware, cloud providers
- `/mastra-evals` -- Scorers, datasets, experiments, CI integration
- `/mastra-workspace` -- Filesystem, sandbox execution, search/indexing

### Project Management
- `/pm-db` -- SQLite-based project tracking (specs, jobs, tasks, reviews)
- `/skill-creator` -- Create, modify, and benchmark skills

## Safety Features

### Shadow Git Snapshots
A `PreToolUse` hook automatically creates a git branch checkpoint before every Write/Edit operation. Instant rollback:

```bash
# List snapshots
git branch --list 'shadow/*'

# Restore a file
git checkout shadow/20260309_143022 -- path/to/file

# Auto-cleanup runs on branches older than 24h
```

### Working Memory
Teams share a `working-memory/{team-name}.md` scratchpad. Agents write decisions, discoveries, and handoff notes. Next agent reads them -- no more starting from zero.

### Health Check
```bash
~/.claude/scripts/health-check.sh
```
Validates: projects.db exists, tables initialized, hooks executable, Memory Bank files present.

## Memory Bank

Six files providing hierarchical project context:

```
projectbrief.md      -> High-level goals and scope
productContext.md     -> User-facing features and UX
techContext.md        -> Technical stack and setup
systemPatterns.md     -> Architecture patterns and decisions
activeContext.md      -> Current focus and active work
progress.md           -> Status updates and metrics
```

Agents read these before starting work. Updated via `/memory-bank-update`.

## Installation

### Requirements
- Python 3.8+ (for utility scripts)
- Claude Code CLI
- Git

### Install
```bash
# Fresh install
git clone https://github.com/artsmc/claude-dev-agents.git ~/.claude

# Or merge with existing ~/.claude
cd ~/.claude
git remote add origin https://github.com/artsmc/claude-dev-agents.git
git fetch && git merge origin/main --allow-unrelated-histories
```

### Verify
```bash
~/.claude/scripts/health-check.sh    # Should pass all checks
ls ~/.claude/agents/ | wc -l         # Should show 19
ls ~/.claude/skills/ | wc -l         # Should show 34
```

## Research & Enhancements

The framework was recently overhauled based on analysis of the OpenDev paper ([arxiv:2603.05344v1](https://arxiv.org/html/2603.05344v1)). Key improvements:

- Standardized all 19 agent definitions (frontmatter, model routing, tool restrictions)
- Modularized 3 bloated agents (41KB -> 9KB core + modules)
- Added shadow git snapshots for instant rollback
- Added working memory for cross-agent context sharing
- Fixed foundation (PM-DB path, hook documentation, health check)
- Refreshed Memory Bank (27 days stale -> current)

Details: [`enhancements/research.md`](./enhancements/research.md) | [`enhancements/index.md`](./enhancements/index.md)

## License

MIT
