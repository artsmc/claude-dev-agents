#!/usr/bin/env bash
################################################################################
# mastra-agents - Mastra Agent Development Skill
#
# Outputs comprehensive guidance for building AI agents with the Mastra framework.
# Usage: bash skill.sh
################################################################################

cat << 'SKILL_EOF'
# Mastra Agent Development Guide

## Table of Contents
1. Agent Basics
2. Model Configuration
3. Tool Integration
4. Memory Integration
5. Structured Output
6. Agent Networks
7. Processors (Guardrails)
8. Agent Approval (Human-in-the-Loop)
9. Voice Integration
10. Common Patterns
11. Debugging Tips

---

## 1. Agent Basics

Create an agent using the `Agent` class from `@mastra/core/agent`:

```typescript
import { Agent } from '@mastra/core/agent';

const myAgent = new Agent({
  id: 'my-agent',
  name: 'My Agent',
  description: 'A helpful assistant that performs specific tasks',
  instructions: 'You are a helpful assistant. Always respond concisely and accurately.',
  model: 'anthropic/claude-sonnet-4-20250514',
  tools: {},
});
```

### Constructor Parameters

| Parameter           | Type                                         | Required | Description                                           |
|---------------------|----------------------------------------------|----------|-------------------------------------------------------|
| `id`                | `string`                                     | No       | Unique identifier (defaults to `name` if not set)     |
| `name`              | `string`                                     | Yes      | Human-readable display name                           |
| `description`       | `string`                                     | No       | Description of the agent's purpose                    |
| `instructions`      | `SystemMessage \| (ctx) => SystemMessage`    | Yes      | System prompt - string, array, or dynamic function    |
| `model`             | `MastraLanguageModel \| (ctx) => ...`        | Yes      | Model string like `'provider/model-name'`             |
| `tools`             | `ToolsInput \| (ctx) => ...`                 | No       | Tools the agent can invoke                            |
| `agents`            | `Record<string, Agent> \| (ctx) => ...`      | No       | Sub-agents (auto-converted to tools)                  |
| `workflows`         | `Record<string, Workflow> \| (ctx) => ...`   | No       | Workflows (auto-converted to tools)                   |
| `memory`            | `MastraMemory \| (ctx) => ...`               | No       | Memory instance for conversation persistence          |
| `inputProcessors`   | `Processor[] \| (ctx) => ...`                | No       | Input guardrails/processors                           |
| `outputProcessors`  | `Processor[] \| (ctx) => ...`                | No       | Output guardrails/processors                          |
| `voice`             | `CompositeVoice`                             | No       | Voice settings for TTS/STT                            |
| `defaultOptions`    | `AgentExecutionOptions \| (ctx) => ...`      | No       | Default options for stream()/generate()               |

### Model String Format

Models use the `'provider/model-name'` format:

```typescript
model: 'openai/gpt-5.1'
model: 'anthropic/claude-sonnet-4-20250514'
model: 'google/gemini-2.5-flash'
model: 'groq/llama-3.1-70b-versatile'
model: 'mistral/mistral-large-latest'
model: 'deepseek/deepseek-chat'
```

### Instruction Formats

Instructions support multiple formats:

```typescript
// String (most common)
instructions: 'You are a helpful assistant.'

// Array of strings
instructions: ['You are a helpful assistant.', 'Always be polite.']

// System message object
instructions: { role: 'system', content: 'You are a helpful assistant.' }

// Array of system messages
instructions: [
  { role: 'system', content: 'You are a helpful assistant.' },
  { role: 'system', content: 'You have expertise in TypeScript.' },
]

// With provider-specific options (caching, reasoning)
instructions: {
  role: 'system',
  content: 'You are an expert code reviewer.',
  providerOptions: {
    openai: { reasoningEffort: 'high' },
    anthropic: { cacheControl: { type: 'ephemeral' } },
  },
}
```

### Dynamic Instructions

Instructions can be an async function for context-aware prompts:

```typescript
const agent = new Agent({
  // ...
  instructions: async ({ requestContext }) => {
    const userTier = requestContext.get('user-tier');
    return `You are a helpful assistant. User tier: ${userTier}.`;
  },
});
```

### Dynamic Model Selection

```typescript
const agent = new Agent({
  // ...
  model: ({ requestContext }) => {
    const userTier = requestContext.get('user-tier');
    return userTier === 'enterprise' ? 'openai/gpt-5' : 'openai/gpt-4.1-nano';
  },
});
```

Docs: https://mastra.ai/docs/agents/overview

---

## 2. Model Configuration

### Supported Providers (600+ models)

| Provider      | Example Model String                     | Notes                       |
|--------------|------------------------------------------|-----------------------------|
| `openai`     | `openai/gpt-5.1`, `openai/gpt-4o`      | GPT family                  |
| `anthropic`  | `anthropic/claude-sonnet-4-20250514`     | Claude family               |
| `google`     | `google/gemini-2.5-flash`               | Gemini family               |
| `groq`       | `groq/llama-3.1-70b-versatile`          | Fast inference              |
| `mistral`    | `mistral/mistral-large-latest`          | Mistral family              |
| `deepseek`   | `deepseek/deepseek-chat`               | DeepSeek family             |
| `fireworks`  | `fireworks/...`                         | Open-source models          |
| `together`   | `together/meta-llama/Llama-3-70b`      | Open-source models          |
| `cohere`     | `cohere/command-r-plus`                 | Cohere family               |
| `perplexity` | `perplexity/llama-3.1-sonar-large`     | Search-augmented            |

### Model Settings (in generate/stream options)

```typescript
const result = await agent.generate('Hello', {
  modelSettings: {
    maxOutputTokens: 4096,
    temperature: 0.7,
    topP: 0.9,
  },
});
```

Docs: https://mastra.ai/models

---

## 3. Tool Integration

### Creating Tools

```typescript
import { createTool } from '@mastra/core/tools';
import { z } from 'zod';

export const weatherTool = createTool({
  id: 'weather-tool',
  description: 'Fetches weather for a location',
  inputSchema: z.object({
    location: z.string(),
  }),
  outputSchema: z.object({
    weather: z.string(),
  }),
  execute: async (inputData) => {
    const { location } = inputData;
    const response = await fetch(`https://wttr.in/${location}?format=3`);
    const weather = await response.text();
    return { weather };
  },
});
```

### Attaching Tools to Agents

```typescript
import { Agent } from '@mastra/core/agent';
import { weatherTool } from '../tools/weather-tool';

export const weatherAgent = new Agent({
  id: 'weather-agent',
  name: 'Weather Agent',
  instructions: `You are a helpful weather assistant.
    Use the weatherTool to fetch current weather data.`,
  model: 'openai/gpt-5.1',
  tools: { weatherTool },
});
```

### Using Agents as Tools (Sub-agents)

Agents can be added to other agents via `agents`. Mastra auto-converts them to tools named `agent-<key>`:

```typescript
const parentAgent = new Agent({
  id: 'parent-agent',
  name: 'Parent Agent',
  instructions: 'You coordinate sub-agents.',
  model: 'openai/gpt-5.1',
  agents: {
    researcher: researchAgent,   // becomes tool: agent-researcher
    writer: writingAgent,        // becomes tool: agent-writer
  },
});
```

### Using Workflows as Tools

Workflows can be added via `workflows`. Auto-converted to tools named `workflow-<key>`:

```typescript
const agent = new Agent({
  id: 'research-agent',
  name: 'Research Agent',
  instructions: 'Use the research workflow to gather information.',
  model: 'openai/gpt-5.1',
  tools: { weatherTool },
  workflows: {
    research: researchWorkflow,  // becomes tool: workflow-research
  },
});
```

### MCP (Model Context Protocol) Tools

```typescript
import { MCPClient } from '@mastra/mcp';

const mcpClient = new MCPClient({
  servers: {
    filesystem: {
      command: 'npx',
      args: ['-y', '@modelcontextprotocol/server-filesystem', '/tmp'],
    },
    github: {
      url: new URL('https://api.github.com/mcp'),
      requestInit: {
        headers: { Authorization: `Bearer ${process.env.GITHUB_TOKEN}` },
      },
    },
  },
});

const agent = new Agent({
  // ...
  tools: {
    ...await mcpClient.getTools(),
    ...localTools,
  },
});
```

### Tool Name in Stream Responses

The `toolName` in stream responses comes from the **object key**, not the tool's `id`:

```typescript
tools: { weatherTool }           // toolName: "weatherTool"
tools: { [weatherTool.id]: weatherTool }  // toolName: "weather-tool"
tools: { "my-custom-name": weatherTool }  // toolName: "my-custom-name"
```

Docs: https://mastra.ai/docs/agents/using-tools

---

## 4. Memory Integration

### Basic Memory Setup

```typescript
import { Agent } from '@mastra/core/agent';
import { Memory } from '@mastra/memory';

export const memoryAgent = new Agent({
  id: 'memory-agent',
  name: 'Memory Agent',
  instructions: 'You are a helpful assistant with conversation memory.',
  model: 'anthropic/claude-sonnet-4-20250514',
  memory: new Memory({
    options: {
      lastMessages: 20,
    },
  }),
});
```

### Storage Provider (required for persistence)

Add storage to the Mastra instance (shared across agents):

```typescript
import { Mastra } from '@mastra/core';
import { LibSQLStore } from '@mastra/libsql';

export const mastra = new Mastra({
  agents: { memoryAgent },
  storage: new LibSQLStore({
    id: 'mastra-storage',
    url: ':memory:',
  }),
});
```

Or add storage directly to an agent's memory:

```typescript
import { Memory } from '@mastra/memory';
import { LibSQLStore } from '@mastra/libsql';

const memory = new Memory({
  storage: new LibSQLStore({
    id: 'mastra-storage',
    url: ':memory:',
  }),
  options: {
    lastMessages: 20,
  },
});
```

### Using Memory in Conversations

Pass `memory` object with `resource` and `thread` to track history:

```typescript
// Store information
const response = await memoryAgent.generate('My favorite color is blue.', {
  memory: {
    resource: 'user-123',
    thread: 'conversation-456',
  },
});

// Recall information (same resource + thread)
const response2 = await memoryAgent.generate("What's my favorite color?", {
  memory: {
    resource: 'user-123',
    thread: 'conversation-456',
  },
});
```

### Observational Memory (Long-term)

For long-running conversations, observational memory compresses old messages:

```typescript
const memoryAgent = new Agent({
  id: 'memory-agent',
  name: 'Memory Agent',
  memory: new Memory({
    options: {
      observationalMemory: true,  // uses google/gemini-2.5-flash by default
    },
  }),
});

// Or with custom config:
const memoryAgent2 = new Agent({
  id: 'memory-agent-2',
  name: 'Memory Agent 2',
  memory: new Memory({
    options: {
      observationalMemory: {
        model: 'deepseek/deepseek-reasoner',
        observation: {
          messageTokens: 20_000,
        },
      },
    },
  }),
});
```

### Memory Packages

| Package           | Purpose                                  |
|-------------------|------------------------------------------|
| `@mastra/memory`  | Core Memory class                        |
| `@mastra/libsql`  | LibSQL storage provider                  |
| `@mastra/pg`      | PostgreSQL storage provider              |

Docs: https://mastra.ai/docs/agents/agent-memory

---

## 5. Structured Output

### Basic Structured Output (Zod)

```typescript
import { z } from 'zod';

const response = await agent.generate('Help me plan my day.', {
  structuredOutput: {
    schema: z.array(
      z.object({
        name: z.string(),
        activities: z.array(z.string()),
      }),
    ),
  },
});

console.log(response.object);
// [{ name: "Morning Routine", activities: ["Wake up", "Exercise"] }, ...]
```

### Structured Output with JSON Schema

```typescript
const response = await agent.generate('Help me plan my day.', {
  structuredOutput: {
    schema: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          name: { type: 'string' },
          activities: { type: 'array', items: { type: 'string' } },
        },
        required: ['name', 'activities'],
      },
    },
  },
});
```

### Separate Structuring Model

When the main agent isn't good at structured output, use a second model:

```typescript
const response = await agent.generate('Analyze TypeScript.', {
  structuredOutput: {
    schema: z.object({
      overview: z.string(),
      strengths: z.array(z.string()),
      weaknesses: z.array(z.string()),
    }),
    model: 'openai/gpt-4o',  // Second model for structuring
  },
});
```

### Structured Output with Streaming

```typescript
const stream = await agent.stream('Help me plan my day.', {
  structuredOutput: {
    schema: z.array(
      z.object({
        name: z.string(),
        activities: z.array(z.string()),
      }),
    ),
  },
});

for await (const chunk of stream.fullStream) {
  if (chunk.type === 'object-result') {
    console.log(chunk);
  }
}

console.log(await stream.object);
```

### Error Handling for Structured Output

```typescript
const response = await agent.generate('Tell me about TypeScript.', {
  structuredOutput: {
    schema: z.object({
      summary: z.string(),
      keyFeatures: z.array(z.string()),
    }),
    errorStrategy: 'fallback',  // 'strict' | 'warn' | 'fallback'
    fallbackValue: {
      summary: 'TypeScript is a typed superset of JavaScript',
      keyFeatures: ['Static typing', 'Compiles to JavaScript'],
    },
  },
});
```

### JSON Prompt Injection (for models without response_format)

```typescript
const response = await agent.generate('Help me plan my day.', {
  structuredOutput: {
    schema: mySchema,
    jsonPromptInjection: true,  // Required for Gemini 2.5 with tools
  },
});
```

Docs: https://mastra.ai/docs/agents/structured-output

---

## 6. Agent Networks

Agent networks coordinate multiple agents, workflows, and tools. A routing agent uses LLM reasoning to decide which primitives to call.

### Creating a Network

```typescript
import { Agent } from '@mastra/core/agent';
import { Memory } from '@mastra/memory';
import { LibSQLStore } from '@mastra/libsql';

const researchAgent = new Agent({
  id: 'research-agent',
  name: 'Research Agent',
  description: 'Gathers research insights in bullet-point form.',
  instructions: 'You research topics thoroughly.',
  model: 'anthropic/claude-sonnet-4-20250514',
  tools: { searchTool },
});

const writingAgent = new Agent({
  id: 'writing-agent',
  name: 'Writing Agent',
  description: 'Turns research into well-structured written content.',
  instructions: 'You write clear, engaging content based on research.',
  model: 'anthropic/claude-sonnet-4-20250514',
});

// The routing agent delegates to sub-agents, workflows, and tools
const routingAgent = new Agent({
  id: 'routing-agent',
  name: 'Routing Agent',
  instructions: `You are a network of writers and researchers.
    Always respond with a complete report in full paragraphs.`,
  model: 'openai/gpt-5.1',
  agents: {
    researchAgent,
    writingAgent,
  },
  workflows: {
    cityWorkflow,
  },
  tools: {
    weatherTool,
  },
  memory: new Memory({
    storage: new LibSQLStore({
      id: 'mastra-storage',
      url: 'file:../mastra.db',
    }),
  }),
});
```

### Calling Agent Networks

Use `.network()` to trigger the routing agent:

```typescript
const result = await routingAgent.network('Tell me three cool ways to use Mastra');

for await (const chunk of result) {
  console.log(chunk.type);
  if (chunk.type === 'network-execution-event-step-finish') {
    console.log(chunk.payload.result);
  }
}
```

### Network with Structured Output

```typescript
import { z } from 'zod';

const stream = await routingAgent.network('Research AI trends', {
  structuredOutput: {
    schema: z.object({
      summary: z.string(),
      recommendations: z.array(z.string()),
      confidence: z.number().min(0).max(1),
    }),
  },
});

for await (const chunk of stream) {
  if (chunk.type === 'network-object-result') {
    console.log('Final:', chunk.payload.object);
  }
}

const result = await stream.object;
```

### Key Network Principles

- **Memory is required** for `.network()` - stores task history and determines completion
- **Descriptions matter** - primitives are selected based on their descriptions
- **Schema helps routing** - `inputSchema`/`outputSchema` guide the routing agent

Docs: https://mastra.ai/docs/agents/networks

---

## 7. Processors (Guardrails)

Processors apply guardrails to agent inputs and outputs. They run before or after each interaction to review, transform, or block information.

### Input Processors

Applied **before** messages reach the LLM:

```typescript
import { Agent } from '@mastra/core/agent';
import { ModerationProcessor, PromptInjectionDetector, PIIDetector, UnicodeNormalizer } from '@mastra/core/processors';

const secureAgent = new Agent({
  id: 'secure-agent',
  name: 'Secure Agent',
  instructions: 'You are a helpful assistant.',
  model: 'openai/gpt-5.1',
  inputProcessors: [
    new UnicodeNormalizer({
      stripControlChars: true,
      collapseWhitespace: true,
    }),
    new PromptInjectionDetector({
      model: 'openrouter/openai/gpt-oss-safeguard-20b',
      threshold: 0.8,
      strategy: 'rewrite',
      detectionTypes: ['injection', 'jailbreak', 'system-override'],
    }),
    new PIIDetector({
      model: 'openrouter/openai/gpt-oss-safeguard-20b',
      threshold: 0.6,
      strategy: 'redact',
      redactionMethod: 'mask',
      detectionTypes: ['email', 'phone', 'credit-card'],
    }),
    new ModerationProcessor({
      model: 'openrouter/openai/gpt-oss-safeguard-20b',
      categories: ['hate', 'harassment', 'violence'],
      threshold: 0.7,
      strategy: 'block',
    }),
  ],
});
```

### Output Processors

Applied **after** the LLM generates a response:

```typescript
import { BatchPartsProcessor, TokenLimiterProcessor, SystemPromptScrubber } from '@mastra/core/processors';

const agent = new Agent({
  // ...
  outputProcessors: [
    new BatchPartsProcessor({
      batchSize: 5,
      maxWaitTime: 100,
      emitOnNonText: true,
    }),
    new TokenLimiterProcessor({
      limit: 1000,
      strategy: 'truncate',
      countMode: 'cumulative',
    }),
    new SystemPromptScrubber({
      model: 'openrouter/openai/gpt-oss-safeguard-20b',
      strategy: 'redact',
      redactionMethod: 'placeholder',
      placeholderText: '[REDACTED]',
    }),
  ],
});
```

### Available Processors

**Input Processors:**
| Processor                 | Description                                      |
|---------------------------|--------------------------------------------------|
| `UnicodeNormalizer`       | Cleans and normalizes Unicode, whitespace         |
| `PromptInjectionDetector` | Detects injection, jailbreak, system overrides    |
| `LanguageDetector`        | Detects and translates user messages              |

**Output Processors:**
| Processor                 | Description                                      |
|---------------------------|--------------------------------------------------|
| `BatchPartsProcessor`     | Batches streamed output for network efficiency    |
| `TokenLimiterProcessor`   | Limits tokens in responses                        |
| `SystemPromptScrubber`    | Redacts system prompts from responses             |

**Hybrid Processors (input or output):**
| Processor                 | Description                                      |
|---------------------------|--------------------------------------------------|
| `ModerationProcessor`     | Detects inappropriate/harmful content             |
| `PIIDetector`             | Detects and redacts PII (emails, phones, etc.)    |

### Processor Strategies

Most processors support `strategy`: `block`, `warn`, `detect`, or `redact`.

When `block` is used, the processor calls `abort()` and stops the request:

```typescript
// Handling blocked requests
const result = await agent.generate('...');

if (result.tripwire) {
  console.error('Blocked:', result.tripwire.reason);
  console.error('Processor:', result.tripwire.processorId);
}
```

### Custom Processors

Create custom processors by extending the `Processor` class:

```typescript
export class QualityChecker implements Processor {
  id = 'quality-checker';

  async processOutputStep({ text, abort, retryCount }) {
    const score = await evaluateQuality(text);

    if (score < 0.7 && retryCount < 3) {
      abort('Response quality too low.', { retry: true, metadata: { score } });
    }

    return [];
  }
}
```

Docs: https://mastra.ai/docs/agents/guardrails

---

## 8. Agent Approval (Human-in-the-Loop)

Agent approval enables human oversight of tool calls. Use `requireToolApproval` option:

```typescript
const result = await agent.generate('Delete the old records', {
  requireToolApproval: true,
  maxSteps: 10,
});

if (result.finishReason === 'suspended') {
  console.log('Tool needs approval:', result.suspendPayload);
  // { toolCallId, toolName, args }

  // Approve:
  const approved = await agent.approveToolCallGenerate({
    runId: result.runId,
    toolCallId: result.suspendPayload.toolCallId,
    memory: { resource: 'user-123', thread: 'thread-456' },
  });

  // Or decline:
  const declined = await agent.declineToolCallGenerate({
    runId: result.runId,
    toolCallId: result.suspendPayload.toolCallId,
    memory: { resource: 'user-123', thread: 'thread-456' },
  });
}
```

Docs: https://mastra.ai/docs/agents/agent-approval

---

## 9. Voice Integration

Mastra agents can integrate with TTS and STT providers.

### Adding Voice to an Agent

```typescript
import { Agent } from '@mastra/core/agent';
import { OpenAIVoice } from '@mastra/voice-openai';

const voice = new OpenAIVoice({
  apiKey: process.env.OPENAI_API_KEY,
  speaker: 'alloy', // alloy, echo, fable, onyx, nova, shimmer
});

const agent = new Agent({
  id: 'voice-agent',
  name: 'Voice Agent',
  instructions: 'You are a voice-enabled assistant.',
  model: 'openai/gpt-4o',
  voice,
});

// Text-to-Speech
const audioStream = await agent.voice.speak('Hello!');

// Speech-to-Text
const transcript = await agent.voice.listen(audioBuffer);
```

### Supported Voice Providers

| Provider      | Package                    | Features  |
|--------------|----------------------------|-----------|
| OpenAI       | `@mastra/voice-openai`     | TTS + STT |
| ElevenLabs   | `@mastra/voice-elevenlabs` | TTS       |
| Google Cloud | `@mastra/voice-google`     | TTS + STT |
| Deepgram     | `@mastra/voice-deepgram`   | STT       |
| PlayHT       | `@mastra/voice-playht`     | TTS       |

Docs: https://mastra.ai/docs/agents/adding-voice

---

## 10. Common Patterns

### Registering Agents with Mastra

```typescript
import { Mastra } from '@mastra/core';
import { testAgent } from './agents/test-agent';

export const mastra = new Mastra({
  agents: { testAgent },
});

// Later, reference the agent
const agent = mastra.getAgent('testAgent');
```

### Multi-Tool Agent

```typescript
const agent = new Agent({
  id: 'multi-tool-agent',
  name: 'Swiss Army Agent',
  instructions: `You have multiple tools. Choose the right one for each task.`,
  model: 'anthropic/claude-sonnet-4-20250514',
  tools: { searchTool, calculatorTool, emailTool },
});

const result = await agent.generate('Find the population of Tokyo and calculate 15% of it', {
  maxSteps: 10,
});
```

### Agent with Memory and Observational Memory

```typescript
const agent = new Agent({
  id: 'memory-agent',
  name: 'Memory Agent',
  instructions: 'You remember past conversations.',
  model: 'anthropic/claude-sonnet-4-20250514',
  memory: new Memory({
    options: {
      lastMessages: 20,
      observationalMemory: true,
    },
  }),
});

// Conversations are automatically persisted
await agent.generate('My favorite color is blue', {
  memory: { resource: 'user-1', thread: 'thread-1' },
});

// Later, the agent can recall this
await agent.generate('What is my favorite color?', {
  memory: { resource: 'user-1', thread: 'thread-1' },
});
```

### Streaming Agent Responses

```typescript
const stream = await agent.stream('Tell me about quantum computing');

for await (const chunk of stream.textStream) {
  process.stdout.write(chunk);
}

// Or with full event stream
for await (const event of stream.fullStream) {
  switch (event.type) {
    case 'text-delta':
      process.stdout.write(event.textDelta);
      break;
    case 'tool-call':
      console.log('Tool called:', event.toolName);
      break;
    case 'tool-result':
      console.log('Tool result:', event.result);
      break;
  }
}
```

### Multi-step with onStepFinish

```typescript
const response = await agent.generate('Help me organize my day', {
  maxSteps: 10,
  onStepFinish: ({ text, toolCalls, toolResults, finishReason, usage }) => {
    console.log({ text, toolCalls, toolResults, finishReason, usage });
  },
});
```

### Streaming with onFinish

```typescript
const stream = await agent.stream('Help me organize my day', {
  onFinish: ({ steps, text, finishReason, usage }) => {
    console.log({ steps, text, finishReason, usage });
  },
});

for await (const chunk of stream.textStream) {
  process.stdout.write(chunk);
}
```

### Multi-step with prepareStep

Control tools and output per step:

```typescript
const result = await agent.stream('weather in vancouver?', {
  prepareStep: async ({ stepNumber }) => {
    if (stepNumber === 0) {
      return {
        model: 'anthropic/claude-sonnet-4-20250514',
        tools: { weatherTool },
        toolChoice: 'required',
      };
    }
    return {
      model: 'anthropic/claude-sonnet-4-20250514',
      tools: undefined,
      structuredOutput: {
        schema: z.object({
          temperature: z.number(),
          humidity: z.number(),
        }),
      },
    };
  },
});
```

---

## 11. Debugging Tips

### Common Issues and Solutions

1. **Model provider credential errors**
   - Mastra auto-detects env vars: `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, etc.
   - Verify: `console.log(process.env.MY_KEY?.slice(0, 8))`

2. **Tool schema validation errors**
   - Ensure `inputSchema` and `outputSchema` use valid Zod schemas
   - Use `.describe()` on schema fields for better LLM understanding
   - Test parsing: `mySchema.parse(testData)`

3. **Agent not using tools**
   - Make tool descriptions clear and specific
   - Mention tools in agent instructions
   - Verify tools are passed as an object (not array)
   - Increase `maxSteps` (default is 1)

4. **Memory not persisting**
   - Ensure `resource` and `thread` are consistent across calls
   - Verify storage provider is configured (on Mastra or Memory instance)

5. **Structured output parsing failures**
   - Try `errorStrategy: 'fallback'` with a `fallbackValue`
   - Use `jsonPromptInjection: true` for models without `response_format`
   - Try a separate structuring `model`

6. **Enable tracing for debugging**
   ```typescript
   const mastra = new Mastra({
     agents: { myAgent },
     logger: { level: 'debug' },
   });
   ```

7. **Test agents with Studio**
   - Use Mastra Studio to chat with agents, inspect tool calls, view traces
   - Default endpoint: `http://localhost:4111/api/agents/myAgent/generate`

---

## Quick Reference Links

- Agents Overview: https://mastra.ai/docs/agents/overview
- Using Tools: https://mastra.ai/docs/agents/using-tools
- Agent Memory: https://mastra.ai/docs/agents/agent-memory
- Structured Output: https://mastra.ai/docs/agents/structured-output
- Agent Networks: https://mastra.ai/docs/agents/networks
- Guardrails/Processors: https://mastra.ai/docs/agents/guardrails
- Voice: https://mastra.ai/docs/agents/adding-voice
- Agent Approval: https://mastra.ai/docs/agents/agent-approval
- Model Providers: https://mastra.ai/models
- MCP Integration: https://mastra.ai/docs/mcp/overview
- API Reference - Agent: https://mastra.ai/reference/agents/agent
- API Reference - generate(): https://mastra.ai/reference/agents/generate

SKILL_EOF
