# mastra-dev Skill - Developer Documentation

Developer guide for maintaining and extending the mastra-dev skill for the Mastra Framework.

## Overview

The **mastra-dev** skill is a comprehensive development toolkit for building AI agent systems using the Mastra Framework. It provides command-line operations for creating agents, workflows, tools, managing MCP server integrations, and debugging Mastra applications.

### Key Capabilities

1. **Agent Management** - Create and configure LLM-powered agents
2. **Workflow Management** - Design DAG-based multi-step workflows
3. **Tool Management** - Build reusable tools for agents
4. **Server Management** - Control Mastra API server and infrastructure
5. **MCP Management** - Integrate Model Context Protocol servers
6. **Analysis & Debugging** - Validate, analyze, and debug Mastra apps

### Design Philosophy

- **Zero External Dependencies** - Uses Python stdlib only for maximum portability
- **TypeScript Generation** - Produces production-ready TypeScript files
- **Convention Over Configuration** - Follows Mastra best practices by default
- **Idempotent Operations** - Safe to run commands multiple times
- **Developer-Friendly** - Clear error messages and helpful feedback

## Architecture

### High-Level Architecture

```
mastra-dev skill
├── skill.sh               # Entry point (bash wrapper)
├── scripts/
│   ├── main.py           # Command-line interface and routing
│   ├── agent_generator.py  # Agent creation and management
│   ├── workflow_generator.py # Workflow and step management
│   ├── tool_generator.py   # Tool creation and management
│   ├── server_manager.py # Server lifecycle management
│   ├── mcp_manager.py    # MCP client integration
│   └── lib/
│       ├── analyzers/
│       │   └── mastra_analyzer.py # Analysis and validation
│       ├── models/       # Configuration dataclasses
│       └── utils/        # File writing and validation
├── templates/            # TypeScript code templates
│   ├── agent.template.ts
│   ├── workflow.template.ts
│   ├── tool.template.ts
│   └── step.template.ts
├── SKILL.md              # User-facing documentation
└── README.md             # This file (developer docs)
```

### Component Responsibilities

#### skill.sh
- Entry point for the skill
- Validates Python availability
- Validates Mastra project structure
- Passes arguments to main.py
- Returns exit codes to Claude Code

#### scripts/main.py
- Command-line argument parsing (argparse)
- Command routing to appropriate modules
- Error handling and user feedback
- Configuration file loading (.mastra-dev-config.json)

#### Generator Modules
Each generator handles code generation for specific entities:

- **agent_generator.py** - Agent CRUD operations, model configuration
- **workflow_generator.py** - Workflow creation, step management, DAG composition
- **tool_generator.py** - Tool generation with Zod schemas
- **server_manager.py** - Mastra server lifecycle (start/stop/status/logs)
- **mcp_manager.py** - MCP client configuration and testing

#### Template System
- TypeScript templates with {{placeholder}} substitution
- Ensures generated code follows Mastra conventions
- Supports multiple LLM providers via pattern matching
- Validates generated TypeScript syntax

## File Structure

```
/home/artsmc/.claude/skills/mastra-dev/
├── skill.sh                          # Bash entry point
├── SKILL.md                          # User documentation
├── README.md                         # Developer documentation
└── scripts/
    ├── __init__.py
    ├── main.py                       # CLI router (main entry)
    ├── agent_generator.py            # Agent operations
    ├── workflow_generator.py         # Workflow operations
    ├── tool_generator.py             # Tool operations
    ├── server_manager.py             # Server management
    ├── mcp_manager.py                # MCP integration
    └── lib/
        ├── __init__.py
        ├── models/
        │   ├── __init__.py
        │   ├── agent_config.py       # Agent dataclass
        │   ├── workflow_config.py    # Workflow dataclass
        │   └── tool_config.py        # Tool dataclass
        ├── analyzers/
        │   ├── __init__.py
        │   └── mastra_analyzer.py    # Analysis & debugging
        └── utils/
            ├── __init__.py
            ├── file_writer.py        # TypeScript file writing
            └── validator.py          # Configuration validation
└── templates/
    ├── agent.template.ts
    ├── workflow.template.ts
    ├── tool.template.ts
    └── step.template.ts
└── examples/
    ├── example-agent.yaml
    ├── example-workflow.yaml
    └── example-tool.yaml
```

### Generated Files Location

The skill generates files in the target Mastra app (default: `/home/artsmc/applications/low-code/apps/mastra`):

```
apps/mastra/
├── src/
│   ├── agents/
│   │   └── {agent-name}.ts
│   ├── workflows/
│   │   └── {workflow-name}.ts
│   └── tools/
│       └── {tool-name}.ts
├── config/
│   ├── mastra.config.ts              # Auto-updated with registrations
│   └── mcp.config.ts                 # Auto-updated with MCP clients
```

## Development Setup

### Prerequisites

- Python 3.8 or higher (no external packages required)
- Access to Mastra app directory
- Basic understanding of Mastra Framework
- TypeScript knowledge (for template modifications)

### Installation

The skill is installed as part of the Claude Code skills system:

```bash
# Skill location
cd /home/artsmc/.claude/skills/mastra-dev

# Verify structure
ls -la
# Expected: skill.sh, SKILL.md, README.md, scripts/, templates/

# Make executable
chmod +x skill.sh

# Test skill execution
./skill.sh --help
```

### Configuration

Create optional `.mastra-dev-config.json` in the skill directory:

```json
{
  "mastraAppPath": "/home/artsmc/applications/low-code/apps/mastra",
  "defaultModel": "openai/gpt-4-turbo",
  "defaultAgentInstructions": "You are a helpful AI assistant",
  "autoStartServer": false,
  "studioPort": 4111,
  "mcpPresets": {
    "wikipedia": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-wikipedia"]
    }
  }
}
```

### Development Environment

```bash
# Set up development environment
cd /home/artsmc/.claude/skills/mastra-dev

# Make skill.sh executable
chmod +x skill.sh

# Test basic commands
./skill.sh analyze
./skill.sh list-agents
./skill.sh validate
```

## Adding New Capabilities

### Adding a New Command

Follow these steps to add a new command to the skill:

#### 1. Update main.py

Add command-line argument parsing in the appropriate section:

```python
# scripts/main.py

# Add subparser for your command
parser_new = subparsers.add_parser('new-command', help='Description of new command')
parser_new.add_argument('--param', required=True, help='Parameter description')
parser_new.add_argument('--optional', help='Optional parameter')

# Add handler in main() function
if args.command == 'new-command':
    from new_module import handle_new_command
    result = handle_new_command(args.param, args.optional)
    print(result)
    sys.exit(0 if result['success'] else 1)
```

#### 2. Create Implementation Module

Create a new module file (e.g., `scripts/new_module.py`):

```python
#!/usr/bin/env python3
"""
New capability for mastra-dev skill.
"""

import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any

def handle_new_command(param: str, optional: Optional[str] = None) -> Dict[str, Any]:
    """
    Handle the new command operation.

    Args:
        param: Required parameter
        optional: Optional parameter

    Returns:
        Dict with success status and message

    Raises:
        ValueError: If parameters are invalid
    """
    # Validate inputs
    if not param:
        raise ValueError("Parameter 'param' is required")

    # Perform operation
    result = {
        'success': True,
        'message': f"Executed new command with param: {param}"
    }

    return result
```

#### 3. Add Template (if needed)

For commands that generate code, create a template:

```typescript
// templates/new-entity.template.ts
import { SomeImport } from '@mastra/core';

export const {{entityName}}Entity = new SomeEntity({
  id: '{{entity-id}}',
  name: '{{entityDisplayName}}',
  config: {
    // Configuration here
  },
});
```

#### 4. Update SKILL.md

Document the new command in user-facing documentation:

```markdown
### new-command

Description of what the command does.

\`\`\`bash
/mastra-dev new-command --param "value" --optional "value"
\`\`\`

**Options:**
- `--param` (required): Parameter description
- `--optional` (optional): Optional parameter description

**Output:**
- Expected output description
```

#### 5. Test the New Command

```bash
# Test basic execution
./skill.sh new-command --param "test-value"

# Test error handling
./skill.sh new-command  # Should fail with helpful error

# Test with optional parameters
./skill.sh new-command --param "test" --optional "extra"
```

## Testing

### Manual Testing

Test each command manually to verify behavior:

```bash
# Agent Management
./skill.sh create-agent --name "test-agent" --model "openai/gpt-4"
./skill.sh list-agents
./skill.sh analyze-agent --name "test-agent"

# Workflow Management
./skill.sh create-workflow --name "test-workflow"
./skill.sh add-step --workflow "test-workflow" --step-name "step1"
./skill.sh list-workflows
./skill.sh show-graph --workflow "test-workflow"

# Tool Management
./skill.sh create-tool --name "test-tool"
./skill.sh list-tools

# Server Management
./skill.sh server status
./skill.sh server logs --tail 10

# MCP Management
./skill.sh mcp list-servers

# Analysis
./skill.sh analyze
./skill.sh validate
```

### Testing Generated Code

Verify generated TypeScript compiles correctly:

```bash
cd /home/artsmc/applications/low-code

# Generate test entities
cd /home/artsmc/.claude/skills/mastra-dev
./skill.sh create-agent --name "test-agent"
./skill.sh create-workflow --name "test-workflow"
./skill.sh create-tool --name "test-tool"

# Verify TypeScript compilation
cd /home/artsmc/applications/low-code
npx tsc --noEmit

# Expected: No errors

# Clean up test files
rm apps/mastra/src/agents/test-agent.ts
rm apps/mastra/src/workflows/test-workflow.ts
rm apps/mastra/src/tools/test-tool.ts
```

### Error Handling Tests

Test error scenarios:

```bash
# Invalid agent name
./skill.sh create-agent --name "Invalid Name"
# Expected: Error with helpful message

# Missing required parameter
./skill.sh create-agent
# Expected: Error showing required --name parameter

# Invalid model format
./skill.sh create-agent --name "test" --model "invalid"
# Expected: Error about model format (should be provider/model)
```

## Code Organization Rationale

### Why Separate Generator Modules?

Each generator module handles a specific domain:
- **Separation of Concerns** - Each file has a single responsibility
- **Easier Maintenance** - Changes to one capability don't affect others
- **Parallel Development** - Multiple developers can work simultaneously
- **Testability** - Each module can be tested independently

### Why Template-Based Generation?

Templates provide:
- **Consistency** - All generated code follows same patterns
- **Maintainability** - Easy to update patterns across all generations
- **Flexibility** - Placeholders allow customization without complex logic
- **Quality** - Pre-validated templates ensure working code

### Why Python Stdlib Only?

Using only Python standard library provides:
- **Zero Dependencies** - No pip install required
- **Maximum Portability** - Works on any system with Python 3.8+
- **Fast Startup** - No package loading overhead
- **Security** - No third-party code vulnerabilities
- **Simplicity** - Easy to understand and modify

### File Naming Conventions

- **kebab-case** for generated entity names (`research-assistant`, `content-pipeline`)
- **camelCase** for TypeScript identifiers (`researchAssistant`, `contentPipeline`)
- **snake_case** for Python module names (`agent_generator.py`, `workflow_generator.py`)

## Integration with Mastra App

### File Generation Strategy

The skill generates files in the target Mastra app following this strategy:

1. **Read existing configuration** - Parse `mastra.config.ts` to understand current state
2. **Generate new entity** - Create TypeScript file from template
3. **Update configuration** - Add new entity registration to config
4. **Preserve existing code** - Only append, never delete or modify existing entities
5. **Validate syntax** - Check generated TypeScript is valid

### TypeScript Template Placeholders

Templates use these placeholder patterns:

- `{{agentName}}` - camelCase entity name (e.g., `researchAssistant`)
- `{{agentId}}` - kebab-case entity name (e.g., `research-assistant`)
- `{{agentDisplayName}}` - Human-readable name (e.g., `Research Assistant`)
- `{{provider}}` - LLM provider (e.g., `anthropic`, `openai`)
- `{{model}}` - Model identifier (e.g., `gpt-4`, `claude-3-5-sonnet-20241022`)
- `{{instructions}}` - Agent instructions text
- `{{description}}` - Entity description
- `{{tools}}` - Comma-separated tool IDs
- `{{inputSchema}}` - Zod input schema
- `{{outputSchema}}` - Zod output schema
- `{{steps}}` - Step definitions for workflows
- `{{composition}}` - DAG composition (.then(), .parallel(), etc.)

## Common Development Patterns

### Pattern 1: Safe File Operations

Always use atomic file operations:

```python
import tempfile
import shutil
from pathlib import Path

def safe_write_file(path: Path, content: str) -> None:
    """Write file atomically to prevent corruption."""
    # Write to temporary file
    with tempfile.NamedTemporaryFile(mode='w', dir=path.parent, delete=False) as temp_file:
        temp_file.write(content)
        temp_path = temp_file.name

    try:
        # Atomic rename
        shutil.move(temp_path, path)
    except Exception:
        # Clean up temp file on error
        if os.path.exists(temp_path):
            os.unlink(temp_path)
        raise
```

### Pattern 2: Error Messages with Context

Provide actionable error messages:

```python
def validate_agent_name(name: str) -> None:
    """Validate agent name format."""
    if not name:
        raise ValueError("Agent name is required")

    if ' ' in name:
        raise ValueError(
            f"Invalid agent name: '{name}'\n"
            "Agent names must use kebab-case (lowercase with hyphens).\n"
            "Example: 'customer-support-agent'"
        )

    if name.upper() == name:
        raise ValueError(
            f"Invalid agent name: '{name}'\n"
            "Agent names should be lowercase, not uppercase.\n"
            f"Did you mean: '{name.lower()}'?"
        )
```

### Pattern 3: Idempotent Operations

Make operations safe to run multiple times:

```python
def create_agent(name: str, model: str) -> dict:
    """Create agent (idempotent)."""
    agent_path = get_agent_path(name)

    # Check if already exists
    if agent_path.exists():
        return {
            'success': True,
            'message': f"Agent '{name}' already exists",
            'created': False,
            'path': str(agent_path)
        }

    # Create new agent
    content = generate_agent_code(name, model)
    agent_path.write_text(content)
    update_mastra_config(name)

    return {
        'success': True,
        'message': f"Created agent '{name}'",
        'created': True,
        'path': str(agent_path)
    }
```

## Troubleshooting Development Issues

### Issue: Generated TypeScript Has Syntax Errors

**Problem:** Generated files fail TypeScript compilation

**Diagnosis:**
```bash
cd /home/artsmc/applications/low-code
npx tsc --noEmit
# Look for errors in generated files
```

**Solution:**
1. Check template file for syntax errors
2. Verify placeholder substitution is complete
3. Ensure imports are correctly added
4. Test with minimal example

### Issue: Skill Commands Not Found

**Problem:** `./skill.sh command` returns "command not found"

**Diagnosis:**
```bash
# Check skill.sh is executable
ls -la skill.sh

# Check main.py exists
ls -la scripts/main.py

# Test Python directly
python3 scripts/main.py --help
```

**Solution:**
```bash
# Make skill.sh executable
chmod +x skill.sh

# Verify shebang in skill.sh
head -1 skill.sh
# Should be: #!/usr/bin/env bash
```

### Issue: mastra.config.ts Gets Corrupted

**Problem:** Adding entities breaks the config file

**Diagnosis:**
```bash
# Check git diff
cd /home/artsmc/applications/low-code
git diff apps/mastra/src/config/mastra.config.ts
```

**Solution:**
1. Use atomic file operations (temp file + rename)
2. Validate file syntax before writing
3. Keep backup of original file
4. Test update logic thoroughly

## Best Practices for Maintainers

### Code Style

- **PEP 8** - Follow Python style guide
- **Type Hints** - Use type hints for function signatures
- **Docstrings** - Document all public functions
- **Error Handling** - Catch specific exceptions, provide helpful messages
- **DRY** - Extract common logic into utility functions

### Testing Before Commit

```bash
# 1. Test all major commands
./skill.sh analyze
./skill.sh list-agents
./skill.sh validate

# 2. Test error handling
./skill.sh create-agent  # Should fail with helpful error

# 3. Test generated code compiles
cd /home/artsmc/applications/low-code
npx tsc --noEmit

# 4. Clean up test files if any
```

### Documentation Updates

When adding features, update:
1. **SKILL.md** - User-facing documentation
2. **README.md** - Developer documentation (this file)
3. **Code comments** - Inline documentation
4. **Function docstrings** - API documentation

## Resources

### External Documentation

- **Mastra Framework:** https://mastra.ai/docs
- **MCP Specification:** https://modelcontextprotocol.io/
- **LiteLLM Providers:** https://docs.litellm.ai/docs/providers
- **Python argparse:** https://docs.python.org/3/library/argparse.html
- **TypeScript Handbook:** https://www.typescriptlang.org/docs/

### Internal Resources

- **AIForge Monorepo:** `/home/artsmc/applications/low-code/`
- **Mastra App:** `/home/artsmc/applications/low-code/apps/mastra/`
- **Claude Code Skills:** `/home/artsmc/.claude/skills/`
- **Custom Agents:** `/home/artsmc/.claude/agents/`

### Related Skills

- **document-hub-initialize** - Initialize documentation structure
- **memory-bank-initialize** - Initialize project memory
- **security-quality-assess** - Security vulnerability scanning
- **code-duplication** - Code duplication analysis

---

**Maintainer:** AIForge Team
**Last Updated:** 2026-02-11
**Version:** 1.0.0
**Status:** Active
