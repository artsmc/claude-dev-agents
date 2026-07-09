# Mastra Dev Configuration, App Integration, and Templates

> Part of the `mastra-dev` skill. .mastra-dev-config.json options, integration with the AIForge Mastra app (directory structure, auto-registration, development workflow), and the four code-generation templates with their variables. Moved verbatim from SKILL.md.

## Configuration

The skill supports optional configuration via `.mastra-dev-config.json` in your project root:

```json
{
  "mastraPath": "apps/mastra",
  "defaultModel": "anthropic/claude-3-5-sonnet-20241022",
  "defaultProvider": "anthropic",
  "serverPort": 6000,
  "studioPort": 4111,
  "autoRegister": true,
  "templateDefaults": {
    "agent": {
      "instructions": "You are a helpful AI assistant.",
      "tools": []
    },
    "workflow": {
      "composition": "sequential"
    }
  },
  "logging": {
    "level": "info",
    "format": "pretty"
  }
}
```

**Configuration Options:**

- `mastraPath` - Relative path to Mastra app (default: "apps/mastra")
- `defaultModel` - Default LLM model for agents
- `defaultProvider` - Default LLM provider
- `serverPort` - Mastra server port (default: 6000)
- `studioPort` - Mastra Studio port (default: 4111)
- `autoRegister` - Automatically register agents/workflows in config files
- `templateDefaults` - Default values for generated files
- `logging` - Log level and format configuration

## Integration with Mastra App

This skill integrates seamlessly with the existing Mastra app at `/home/artsmc/applications/low-code/apps/mastra`:

### Directory Structure

```
apps/mastra/
├── src/
│   ├── agents/                  # ← Generated agent files
│   │   ├── contract-analyzer.ts
│   │   ├── proposal-writer.ts
│   │   └── data-analyst.ts
│   ├── workflows/               # ← Generated workflow files
│   │   ├── hello-world.ts       # Existing example
│   │   ├── form-generation.ts
│   │   └── contract-analysis.ts
│   ├── tools/                   # ← Generated tool files
│   │   ├── pdf-generator.ts
│   │   ├── document-parser.ts
│   │   └── sam-gov-lookup.ts
│   ├── config/
│   │   ├── mastra.config.ts     # ← Auto-updated registration
│   │   └── mcp.config.ts        # ← Auto-updated MCP config
│   └── app.ts                   # Express server (unchanged)
└── package.json
```

### Auto-Registration

When you create agents, workflows, or tools, the skill automatically:

1. **Generates TypeScript files** in the correct directories
2. **Updates `mastra.config.ts`** to register new constructs
3. **Updates `mcp.config.ts`** to expose workflows as MCP tools
4. **Validates TypeScript syntax** before writing
5. **Preserves existing code** (no destructive edits)

**Example Registration Update:**

Before:
```typescript
// apps/mastra/src/config/mastra.config.ts
export const mastra = new Mastra({
  storage,
  agents: {},
  workflows: {},
  tools: {}
});
```

After running `/mastra-dev create-agent --name "proposal-writer"`:
```typescript
import { proposalWriterAgent } from '../agents/proposal-writer.js';

export const mastra = new Mastra({
  storage,
  agents: {
    proposalWriter: proposalWriterAgent  // ← Auto-added
  },
  workflows: {},
  tools: {}
});
```

### Development Workflow

1. **Start Mastra server** (if not running):
   ```bash
   /mastra-dev server start
   ```

2. **Create constructs** as needed:
   ```bash
   /mastra-dev create-agent --name "my-agent"
   /mastra-dev create-workflow --name "my-workflow"
   /mastra-dev create-tool --name "my-tool"
   ```

3. **Edit generated files** to implement logic:
   - Agents: Add custom instructions and tool configurations
   - Workflows: Implement step `execute` functions
   - Tools: Add business logic to `execute` functions

4. **Test locally**:
   ```bash
   /mastra-dev test-workflow --name "my-workflow" --input '{...}'
   /mastra-dev test-tool --name "my-tool" --input '{...}'
   ```

5. **Use Mastra Studio** for visual debugging:
   ```bash
   /mastra-dev studio start
   # Open http://localhost:4111
   ```

6. **Validate before commit**:
   ```bash
   /mastra-dev validate
   ```

## Templates

The skill uses four TypeScript templates for code generation:

### 1. Agent Template

**File:** `templates/agent.template.ts`

**Variables:**
- `{{agentName}}` - Camel-cased agent name (e.g., "contractAnalyzer")
- `{{agentId}}` - Kebab-cased agent ID (e.g., "contract-analyzer")
- `{{agentDisplayName}}` - Human-readable name (e.g., "Contract Analyzer")
- `{{description}}` - Agent description
- `{{instructions}}` - Agent behavior instructions
- `{{provider}}` - LLM provider (e.g., "anthropic", "openai")
- `{{model}}` - Model name (e.g., "claude-3-5-sonnet-20241022")
- `{{tools}}` - Comma-separated tool IDs

**Example Usage:**
```bash
/mastra-dev create-agent \
  --name "contract-analyzer" \
  --model "anthropic/claude-3-5-sonnet-20241022" \
  --description "Federal contract analysis expert"
```

### 2. Workflow Template

**File:** `templates/workflow.template.ts`

**Variables:**
- `{{workflowName}}` - Camel-cased workflow name
- `{{workflowId}}` - Kebab-cased workflow ID
- `{{workflowDisplayName}}` - Human-readable name
- `{{description}}` - Workflow description
- `{{inputSchema}}` - Zod object schema for input
- `{{outputSchema}}` - Zod object schema for output
- `{{steps}}` - Step definitions (generated)
- `{{composition}}` - DAG composition (`.then()`, `.parallel()`, etc.)

**Example Usage:**
```bash
/mastra-dev create-workflow \
  --name "form-generation" \
  --description "Auto-fill government forms"
```

### 3. Tool Template

**File:** `templates/tool.template.ts`

**Variables:**
- `{{toolName}}` - Camel-cased tool name
- `{{toolId}}` - Kebab-cased tool ID
- `{{toolDisplayName}}` - Human-readable name
- `{{description}}` - Tool description
- `{{inputSchema}}` - Zod object schema for input
- `{{outputSchema}}` - Zod object schema for output
- `{{executeBody}}` - Function body implementation

**Example Usage:**
```bash
/mastra-dev create-tool \
  --name "pdf-generator" \
  --description "Generate PDF from template"
```

### 4. Step Template

**File:** `templates/step.template.ts`

**Variables:**
- `{{stepName}}` - Camel-cased step name
- `{{stepId}}` - Kebab-cased step ID
- `{{stepDisplayName}}` - Human-readable name
- `{{description}}` - Step description
- `{{inputSchema}}` - Zod object schema for input
- `{{outputSchema}}` - Zod object schema for output
- `{{executeBody}}` - Function body implementation

**Example Usage:**
```bash
/mastra-dev add-step \
  --workflow "my-workflow" \
  --step-name "fetch-data" \
  --step-type "api-call"
```

