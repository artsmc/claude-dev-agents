# Claude Code Agents & Commands

A collection of custom agents and commands for [Claude Code](https://github.com/anthropics/claude-code), designed to enhance development workflows with specialized AI agents and automated commands.

## Contents

### Agents

Custom agent definitions for specialized development tasks:

- **ui-developer.md** - Frontend UI development agent specialized in React, Playwright testing, and Gherkin-first workflows
- **front-end-developer.md** - Application logic and data management for frontend (state management, API integration, routing)
- **nextjs-backend-developer.md** - Backend development within Next.js (API routes, service integration, database)
- **nextjs-code-reviewer.md** - Code review agent for Next.js projects
- **nextjs-qa-developer.md** - QA and testing specialist for Next.js applications
- **spec-writer.md** - Feature specification and documentation generator

### Commands

Workflow automation commands:

- **spec.md** - Initiates documentation-first feature planning workflow
- **start-phase.md** - Project phase management and organization
- **memory-bank.md** - System architecture and knowledge management
- **document-hub.md** - Centralized documentation access

## Usage

1. Copy the `agents/` and `commands/` folders to your Claude Code configuration directory (typically `~/.claude/`)
2. Restart Claude Code or reload the configuration
3. Agents will be available via the Task tool
4. Commands will be available as slash commands (e.g., `/spec`, `/start-phase`)

## Requirements

- [Claude Code](https://github.com/anthropics/claude-code)
- The agents are optimized for Next.js and React development workflows

## About

These agents and commands implement a documentation-first, test-driven development approach with emphasis on:
- Gherkin specifications for clear requirements
- Playwright testing for UI verification
- MCP tool integration for latest framework documentation
- Memory Bank for project knowledge persistence
- Structured task breakdowns and planning

## License

MIT
