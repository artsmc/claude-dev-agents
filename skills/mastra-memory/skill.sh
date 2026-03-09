#!/usr/bin/env bash
# mastra-memory - Mastra Memory system development for agent conversation management
cat << 'SKILL_EOF'

================================================================================
MASTRA MEMORY SKILL
================================================================================

Use this skill when building memory-enabled agents with Mastra. Covers
thread-based conversations, message history, semantic recall, working memory,
observational memory, and memory processors.

Package: @mastra/memory
Docs: https://mastra.ai/docs/memory/overview

================================================================================
MEMORY OVERVIEW
================================================================================

Memory gives Mastra agents coherence across conversations. Without memory,
each agent interaction is stateless. With memory, agents can:

- Remember conversation history within a thread
- Extract and recall facts over time (observational memory)
- Maintain structured state across turns (working memory)
- Retrieve relevant past conversations (semantic recall)

### Memory Types

| Type                | Purpose                                         |
|---------------------|------------------------------------------------|
| Message History     | Recent conversation context (last N messages)  |
| Working Memory      | Structured scratchpad state (persistent data)  |
| Semantic Recall     | Embedding-based retrieval of past conversations|
| Observational       | Long-context compressed observation logs       |

### Architecture

Memory is configured via the Memory class options object, NOT via explicit
processor class imports. Mastra automatically manages the underlying processors.

```
User Message --> Memory Processors (input) --> Agent LLM --> Response
                                                                |
Response --> Memory Processors (output) --> Storage (Thread/Messages)
```

Install:
  npm install @mastra/memory @mastra/libsql

================================================================================
MEMORY SETUP
================================================================================

### Basic Setup

```typescript
import { Memory } from '@mastra/memory';
import { Agent } from '@mastra/core/agent';

// Simplest setup: uses default LibSQL file storage
const agent = new Agent({
  id: 'test-agent',
  name: 'My Agent',
  instructions: 'You are a helpful assistant with memory.',
  model: 'openai/gpt-4o',
  memory: new Memory({
    options: {
      lastMessages: 10   // Include last 10 messages in context
    }
  })
});
```

### Using Memory with Agent

```typescript
// Generate with thread context
// Both thread and resource are required identifiers
const response = await agent.generate(
  'Hello, my name is Alex. I work on the API team.',
  {
    memory: {
      thread: 'conversation-abc-123',   // Thread identifier
      resource: 'user-123'               // User/resource identifier
    }
  }
);

// Continue the conversation - agent remembers previous messages
const response2 = await agent.generate(
  'What team did I say I work on?',
  {
    memory: {
      thread: 'conversation-abc-123',
      resource: 'user-123'
    }
  }
);
// Agent can answer: "You said you work on the API team."
```

### Memory Constructor

```typescript
const memory = new Memory({
  storage?: MastraCompositeStore,       // Persistence layer (default: file:memory.db)
  vector?: MastraVector | false,        // Vector store for semantic recall
  embedder?: EmbeddingModel,            // Embedding model for semantic recall
  options?: MemoryConfig                // Configuration options
});
```

### MemoryConfig Options

| Option              | Type                  | Default | Description                                |
|---------------------|-----------------------|---------|--------------------------------------------|
| lastMessages        | number | false        | 10      | Recent messages in context (false=disable) |
| readOnly            | boolean               | false   | Prevents saving; read-only context         |
| semanticRecall      | boolean | object      | false   | Enable semantic search                     |
| workingMemory       | WorkingMemoryConfig   | {enabled:false} | Persistent user info storage      |
| observationalMemory | boolean | object      | false   | Long-context agentic memory                |
| generateTitle       | boolean | object      | false   | Auto-generate thread titles                |

================================================================================
STORAGE BACKENDS
================================================================================

Memory requires a storage backend for persisting threads and messages.
Storage is configured at the Mastra instance level OR per-agent.

### Instance-Level Storage (Recommended)

```typescript
import { Mastra } from '@mastra/core';
import { LibSQLStore } from '@mastra/libsql';

export const mastra = new Mastra({
  storage: new LibSQLStore({
    id: 'mastra-storage',
    url: 'file:./mastra.db'
  })
});
```

### LibSQLStore (Easiest to Start)

```typescript
import { LibSQLStore } from '@mastra/libsql';

const storage = new LibSQLStore({
  id: 'mastra-storage',
  url: 'file:./mastra.db'           // Local file (no external DB needed)
});

// For Turso cloud:
const storage = new LibSQLStore({
  id: 'mastra-storage',
  url: process.env.LIBSQL_URL,
  authToken: process.env.LIBSQL_AUTH_TOKEN
});
```

Install: `npm install @mastra/libsql`

NOTE: When running Mastra Studio alongside your app, use absolute paths
to ensure both processes access the same database.

### PostgresStore (Production)

```typescript
import { PostgresStore } from '@mastra/pg';

const storage = new PostgresStore({
  id: 'pg-storage',
  connectionString: process.env.DATABASE_URL
});
```

Install: `npm install @mastra/pg`

### MongoDB

```typescript
import { MongoDBStore } from '@mastra/mongodb';

const storage = new MongoDBStore({
  id: 'mongo-storage',
  url: process.env.MONGODB_URL
});
```

Install: `npm install @mastra/mongodb`

### UpstashStore (Serverless)

```typescript
import { UpstashStore } from '@mastra/upstash';

const storage = new UpstashStore({
  id: 'upstash-storage',
  url: process.env.UPSTASH_REDIS_URL,
  token: process.env.UPSTASH_REDIS_TOKEN
});
```

Install: `npm install @mastra/upstash`

### Other Supported Providers

- Cloudflare D1, Cloudflare Durable Objects
- Convex
- DynamoDB
- LanceDB
- Microsoft SQL Server

### Composite Storage

Combine multiple providers for different operational needs:

```typescript
import { MastraCompositeStore } from '@mastra/core/storage';

export const mastra = new Mastra({
  storage: new MastraCompositeStore({
    id: 'composite',
    domains: {
      memory: new LibSQLStore({ id: 'mem', url: 'file:./memory.db' }),
      workflows: new PostgresStore({ id: 'wf', connectionString: process.env.DATABASE_URL })
    }
  })
});
```

### Agent-Level Storage Override

```typescript
export const agent = new Agent({
  id: 'agent',
  memory: new Memory({
    storage: new PostgresStore({
      id: 'agent-storage',
      connectionString: process.env.AGENT_DATABASE_URL
    })
  })
});
```

### Default Storage

If no storage is provided, Memory defaults to:
  DefaultStorage({ config: { url: "file:memory.db" } })
This is in-memory/file-based and suitable for development only.

================================================================================
MESSAGE HISTORY
================================================================================

Controls how many recent messages are included in the agent's context window.
This is the most basic and important form of memory.

```typescript
import { Memory } from '@mastra/memory';

const memory = new Memory({
  options: {
    lastMessages: 10   // Include last 10 messages (default)
  }
});
```

### Configuration Options

| Value        | Behavior                                    |
|-------------|---------------------------------------------|
| 10 (default)| Include last 10 messages                    |
| 20-60       | Good for multi-turn problem solving         |
| 100+        | Long sessions (watch context limits)        |
| false       | Disable loading message history entirely    |

### Two Retrieval Patterns

1. **Automatic** - Mastra fetches recent messages automatically (default)
2. **Manual** - Use recall() for custom queries with pagination and filters

### Context Window Strategy

- Small context (10-20 messages): Fast, focused conversations
- Medium context (40-60 messages): Good for multi-turn problem solving
- Large context (100+ messages): Long sessions, monitor token usage

================================================================================
OBSERVATIONAL MEMORY
================================================================================

Long-context memory system that uses background Observer and Reflector agents
to maintain compressed observation logs instead of raw message history.

### Quick Setup

```typescript
const memory = new Memory({
  options: {
    observationalMemory: true   // Enable with defaults
  }
});

// Or with custom configuration:
const memory = new Memory({
  options: {
    observationalMemory: {
      model: 'deepseek/deepseek-reasoner'   // Custom model for observer
    }
  }
});
```

### Default Model

google/gemini-2.5-flash (also tested with DeepSeek, Qwen3, GLM-4.7)

### How It Works

The system operates in three tiers:
1. **Recent messages** - current task conversation history
2. **Observations** - compressed notes when message tokens exceed ~30,000
3. **Reflections** - further condensed observations when observation tokens exceed ~40,000

Key benefits:
- Prompt caching: context is stable (observations append over time)
- Compression: typically achieves 5-40x reduction
- Zero context rot: prevents degradation from noisy tool calls

### Scope Options

- **Thread scope** (default): isolated observations per conversation thread
- **Resource scope** (experimental): shared observations across user's threads

### Async Buffering

Enabled by default. Background Observer calls pre-compute observations
without blocking agent responses. Disable via `bufferTokens: false`.

================================================================================
WORKING MEMORY
================================================================================

Maintains persistent information about users across interactions. Functions
as the agent's "active thoughts or scratchpad."

### Basic Setup

```typescript
const agent = new Agent({
  id: 'personal-assistant',
  name: 'PersonalAssistant',
  instructions: 'You are a helpful personal assistant.',
  model: 'openai/gpt-4o',
  memory: new Memory({
    options: {
      workingMemory: {
        enabled: true
      }
    }
  })
});
```

### Two Scope Options

**Resource-Scoped (Default):** Memory persists across all conversation threads
for the same user. Ideal for personal assistants and customer service bots.

**Thread-Scoped:** Memory isolates to individual conversation threads. Useful
for ephemeral conversations about separate topics.

### Two Implementation Approaches

**1. Template-Based (Free-form Markdown)**

Uses replace semantics (agent provides complete content on updates):

```typescript
const memory = new Memory({
  options: {
    workingMemory: {
      enabled: true,
      template: `## User Profile
- Name: [unknown]
- Role: [unknown]
- Team: [unknown]

## Preferences
- Language: [unknown]
- Framework: [unknown]
- Tone: [e.g., Formal]

## Current Task
- Description: [none]
- Status: [none]
- Blockers: [none]`
    }
  }
});
```

**2. Schema-Based (Structured JSON with Zod)**

Uses merge semantics (agent provides only fields to update):

```typescript
import { z } from 'zod';

const userProfileSchema = z.object({
  name: z.string().optional(),
  location: z.string().optional(),
  timezone: z.string().optional(),
  preferences: z.object({
    language: z.string().optional(),
    framework: z.string().optional()
  }).optional()
});

const memory = new Memory({
  options: {
    workingMemory: {
      enabled: true,
      schema: userProfileSchema
    }
  }
});
```

### Template Design Best Practices

- Use short, focused labels
- Maintain consistent capitalization
- Include simple placeholder hints like [e.g., Formal]
- Abbreviate lengthy values

### Read-Only Working Memory

Set readOnly: true to allow agent access without modification capability.
Useful for routing or sub-agents that should read but not update state.

```typescript
const memory = new Memory({
  options: {
    workingMemory: {
      enabled: true,
      readOnly: true
    }
  }
});
```

### Storage Requirements

Resource-scoped working memory requires storage adapters that support the
`mastra_resources` table: libSQL, PostgreSQL, Upstash, or MongoDB.

================================================================================
SEMANTIC RECALL
================================================================================

Uses vector embeddings to retrieve relevant past conversation segments.
RAG-based search that helps agents maintain context across longer interactions
when messages are no longer within recent message history.

### Default Behavior

Semantic recall activates automatically when memory is added to an agent:

```typescript
const agent = new Agent({
  id: 'support-agent',
  name: 'SupportAgent',
  instructions: 'You are a helpful support agent.',
  model: 'openai/gpt-4o',
  memory: new Memory()   // Semantic recall enabled by default
});
```

### Configuration

```typescript
const memory = new Memory({
  options: {
    semanticRecall: {
      topK: 3,            // Number of similar messages to retrieve (default: 4)
      messageRange: 2,    // Context messages around each match (default: {before:1,after:1})
      scope: 'resource'   // Search across all user's threads (default: thread)
    }
  }
});

// Or with detailed messageRange:
const memory = new Memory({
  options: {
    semanticRecall: {
      topK: 5,
      messageRange: {
        before: 2,        // Messages before the match
        after: 2          // Messages after the match
      }
    }
  }
});

// Disable semantic recall:
const memory = new Memory({
  options: {
    semanticRecall: false
  }
});
```

### Custom Vector Store and Embedder

```typescript
import { PgVector } from '@mastra/pg';
import { ModelRouterEmbeddingModel } from '@mastra/core/llm';

const memory = new Memory({
  vector: new PgVector({
    id: 'pg-vector',
    connectionString: process.env.POSTGRES_CONNECTION_STRING
  }),
  embedder: new ModelRouterEmbeddingModel('openai/text-embedding-3-small'),
  options: {
    semanticRecall: {
      topK: 3,
      messageRange: 2
    }
  }
});
```

### Supported Vector Stores

Default: LibSQL (same DB as storage). Mastra supports 17+ vector store
options including PostgreSQL, Pinecone, MongoDB, Elasticsearch, and more.

### Supported Embedding Models

- openai/text-embedding-3-small (default)
- openai/text-embedding-3-large
- openai/text-embedding-ada-002
- google/gemini-embedding-001
- Local FastEmbed

### When to Disable Semantic Recall

- When message history provides sufficient context
- In realtime two-way audio scenarios (embedding latency impacts responsiveness)
- When you want to minimize API calls and cost

### How It Works

1. New messages are embedded and stored in the vector database
2. On new user input, the message is embedded and used to search past conversations
3. Relevant past segments (with surrounding context) are injected into agent context
4. Agent can reference information from any past conversation with that user

================================================================================
THREAD MANAGEMENT
================================================================================

Threads represent individual conversations. Each thread belongs to a
resource (typically a user).

### Using Threads with Agents

```typescript
// Generate with thread context (recommended pattern)
const response = await agent.generate('Hello!', {
  memory: {
    thread: 'conversation-abc-123',
    resource: 'user-123'
  }
});
```

### Memory.recall() - Manual Message Retrieval

```typescript
// Basic recall
const { messages } = await memory.recall({
  threadId: 'conversation-abc-123'
});

// Recall with options
const { messages } = await memory.recall({
  threadId: 'conversation-abc-123',
  resourceId: 'user-123',               // Validate thread ownership
  vectorSearchString: 'authentication',  // Semantic search
  perPage: 20,                           // Batch size (false = all)
  page: 0,                               // Zero-based pagination
  filter: {
    from: new Date('2024-01-01'),        // Date range filtering
    to: new Date()
  },
  orderBy: { createdAt: 'desc' }         // Sort order
});
```

### recall() Parameters

| Parameter          | Type    | Required | Description                           |
|--------------------|---------|----------|---------------------------------------|
| threadId           | string  | Yes      | Thread to retrieve messages from      |
| resourceId         | string  | No       | Validate thread ownership             |
| vectorSearchString | string  | No       | Semantic similarity search            |
| perPage            | number  | No       | Batch size (false = all messages)     |
| page               | number  | No       | Zero-based pagination index           |
| filter             | object  | No       | Date range filtering                  |
| orderBy            | object  | No       | Sort config (default: desc createdAt) |
| include            | array   | No       | Specific message IDs with context     |
| threadConfig       | object  | No       | Override semantic/working memory config|

### Thread Listing

```typescript
const threads = await memory.listThreads({
  resourceId: 'user-123'
});
```

### Getting a Thread by ID

```typescript
const thread = await memory.getThreadById(threadId);
```

### Deleting Messages

```typescript
await memory.deleteMessages({
  threadId: 'conversation-abc-123',
  ids: ['msg-1', 'msg-2']   // Specific message IDs
});

// Or clear entire thread:
await memory.deleteMessages({
  threadId: 'conversation-abc-123'
});
```

### Thread Cloning

Clone threads for testing, branching, or checkpointing:

```typescript
const clonedThread = await memory.cloneThread({
  threadId: originalThread.id,
  resourceId: 'user-123'
});
```

### Auto-Generated Thread Titles

```typescript
const memory = new Memory({
  options: {
    generateTitle: true   // Auto-generate from first user message
  }
});

// Custom title generation:
const memory = new Memory({
  options: {
    generateTitle: {
      model: 'openai/gpt-4o-mini',
      instructions: 'Generate a 1 word title'
    }
  }
});
```

### Security Note

The memory system does NOT enforce access control. Developers must verify
user authorization before querying threads.

================================================================================
MEMORY PROCESSORS
================================================================================

Mastra has three built-in memory processors that run automatically when
memory features are enabled. You do NOT need to import or instantiate these
manually - they are managed by the Memory class options.

### Built-in Processors

| Processor       | Triggered By                  | What It Does                         |
|-----------------|-------------------------------|--------------------------------------|
| MessageHistory  | options.lastMessages          | Retrieves/persists recent messages   |
| SemanticRecall  | options.semanticRecall        | Vector search for relevant past msgs |
| WorkingMemory   | options.workingMemory.enabled | Retrieves/persists working memory    |

### Execution Order

**Input flow:**
  Memory processors run first --> then user-added processors (guardrails)

**Output flow:**
  User processors run first --> then memory processors persist data

This ensures that if an output guardrail calls abort(), no messages are
persisted to storage.

### Deduplication Control

If you manually add a memory processor to inputProcessors or outputProcessors,
Mastra will NOT auto-add it. This allows custom configuration like different
message limits or custom ordering with additional processors.

### Guardrail Integration

Both input and output guardrails work safely with memory:
- Output guardrails can block before memory saves
- Input guardrails prevent LLM calls and subsequent storage if triggered

### Custom Input/Output Processors

For advanced use cases, you can add custom processors alongside memory:

```typescript
const agent = new Agent({
  id: 'my-agent',
  model: 'openai/gpt-4o',
  memory: new Memory({
    options: { lastMessages: 20 }
  }),
  inputProcessors: [myCustomInputFilter],
  outputProcessors: [myCustomOutputFilter]
});
```

================================================================================
COMPREHENSIVE MEMORY CONFIGURATION EXAMPLE
================================================================================

Production-ready memory setup with multiple features:

```typescript
import { Memory } from '@mastra/memory';
import { PostgresStore, PgVector } from '@mastra/pg';
import { ModelRouterEmbeddingModel } from '@mastra/core/llm';
import { Agent } from '@mastra/core/agent';

// --- Memory Configuration ---
const memory = new Memory({
  // Storage backend
  storage: new PostgresStore({
    id: 'pg-storage',
    connectionString: process.env.DATABASE_URL
  }),

  // Vector store for semantic recall
  vector: new PgVector({
    id: 'pg-vector',
    connectionString: process.env.DATABASE_URL
  }),

  // Embedding model for semantic recall
  embedder: new ModelRouterEmbeddingModel('openai/text-embedding-3-small'),

  // Memory options
  options: {
    // Message history
    lastMessages: 40,

    // Semantic recall from past conversations
    semanticRecall: {
      topK: 3,
      messageRange: { before: 1, after: 1 },
      scope: 'resource'
    },

    // Working memory for persistent user state
    workingMemory: {
      enabled: true,
      template: `## User Context
- Name: [unknown]
- Role: [unknown]
- Project: [unknown]
- Preferences: [unknown]

## Session State
- Current Topic: [none]
- Action Items: [none]`
    },

    // Observational memory for long-context compression
    observationalMemory: {
      model: 'google/gemini-2.5-flash'
    },

    // Auto-generate thread titles
    generateTitle: true
  }
});

// --- Agent with Full Memory ---
const agent = new Agent({
  id: 'full-memory-agent',
  name: 'Full Memory Agent',
  instructions: `You are an intelligent assistant with comprehensive memory.

You can:
- Remember conversation history within this thread
- Recall relevant information from past conversations
- Track user preferences and facts over time
- Maintain structured state about the current session

Update your working memory whenever you learn new user information.
Reference past observations when they are relevant.`,
  model: 'openai/gpt-4o',
  memory
});

// --- Usage ---
const response = await agent.generate(
  'Hi, I am Jordan. I work on the data pipeline team.',
  {
    memory: {
      thread: 'thread-001',
      resource: 'user-123'
    }
  }
);
```

================================================================================
BEST PRACTICES
================================================================================

### Start Simple, Add Complexity

1. Begin with lastMessages alone (default: 10)
2. Enable semanticRecall when cross-session memory is needed
3. Enable workingMemory for stateful workflows
4. Enable observationalMemory for very long conversations
5. Add generateTitle for better thread organization

### Performance Considerations

- Semantic recall adds latency (embedding + vector search per turn)
- Set topK conservatively (3-5) for semantic recall
- Observational memory adds background LLM calls
- Use faster models for observer (google/gemini-2.5-flash)
- Large lastMessages values increase context window size and cost

### Storage Selection

| Provider     | Best For                        | Package        |
|--------------|---------------------------------|----------------|
| LibSQLStore  | Development, getting started    | @mastra/libsql |
| PostgresStore| Production, existing Postgres   | @mastra/pg     |
| MongoDBStore | Existing MongoDB infrastructure | @mastra/mongodb|
| UpstashStore | Serverless applications         | @mastra/upstash|

### Compliance (FedRAMP/NIST)

- Audit thread access with resourceId for RBAC compliance
- Use PostgresStore for data retention requirements
- Implement custom input/output processors for PII filtering
- Verify user authorization before recall() calls
- Memory system does NOT enforce access control by default

### Common Patterns

**Customer Support Agent:**
  lastMessages: 20, semanticRecall: { topK: 3, scope: 'resource' }

**Coding Assistant:**
  lastMessages: 40, workingMemory: { enabled: true }

**Personal Assistant:**
  lastMessages: 20, semanticRecall: { topK: 3 }, workingMemory: { enabled: true }

**Long-Running Agent:**
  lastMessages: 10, observationalMemory: true

================================================================================
DOCUMENTATION LINKS
================================================================================

- Memory Overview: https://mastra.ai/docs/memory/overview
- Message History: https://mastra.ai/docs/memory/message-history
- Observational Memory: https://mastra.ai/docs/memory/observational-memory
- Working Memory: https://mastra.ai/docs/memory/working-memory
- Semantic Recall: https://mastra.ai/docs/memory/semantic-recall
- Memory Processors: https://mastra.ai/docs/memory/memory-processors
- Storage Backends: https://mastra.ai/docs/memory/storage
- Agent Memory: https://mastra.ai/docs/agents/agent-memory
- API Reference - Memory Class: https://mastra.ai/reference/memory/memory-class
- API Reference - recall(): https://mastra.ai/reference/memory/recall
- API Reference - createThread: https://mastra.ai/reference/memory/createThread
- API Reference - getThreadById: https://mastra.ai/reference/memory/getThreadById
- API Reference - listThreads: https://mastra.ai/reference/memory/listThreads
- API Reference - deleteMessages: https://mastra.ai/reference/memory/deleteMessages
- API Reference - cloneThread: https://mastra.ai/reference/memory/cloneThread

================================================================================
SKILL_EOF
