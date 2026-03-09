#!/usr/bin/env bash
# mastra-workspace - Mastra Workspace development (filesystem, sandbox, skills, search)
cat << 'SKILL_EOF'

================================================================================
MASTRA WORKSPACE DEVELOPMENT SKILL
================================================================================

Use this skill when building agents that need file access, code execution,
search, or reusable skills using Mastra Workspaces. Covers the Workspace class,
filesystem providers (Local, S3, GCS), sandbox providers (Local, E2B), the
skills system, search/indexing, mounts, and agent integration.

Package: @mastra/core/workspace (core workspace classes)
         @mastra/s3 (S3 filesystem provider)
         @mastra/gcs (GCS filesystem provider)
         @mastra/e2b (E2B cloud sandbox provider)
Docs: https://mastra.ai/docs/workspace/overview

================================================================================
WORKSPACE OVERVIEW
================================================================================

A Mastra Workspace gives agents a persistent environment for storing files and
executing commands. It is a unified interface that ties together up to four
optional capabilities:

  1. Filesystem  - Read, write, list, delete, copy, move, grep files
  2. Sandbox     - Execute shell commands in a controlled environment
  3. Skills      - Reusable instruction sets following the Agent Skills spec
  4. Search      - BM25 keyword, vector semantic, or hybrid search over content

When you attach a workspace to an agent, Mastra automatically provides the
agent with tools for each configured capability. The agent does not need to
know which provider backs a capability -- it simply calls workspace tools.

### When to Use Workspaces

- Agents that need to read/write files (document managers, report generators)
- Agents that need to run code or shell commands (dev assistants, CI agents)
- Agents that need to search across a corpus of documents or skills
- Agents that combine multiple capabilities (full dev assistant with
  filesystem + sandbox + search + skills)

Install:
  npm install @mastra/core          # Workspace, LocalFilesystem, LocalSandbox
  npm install @mastra/s3            # S3Filesystem (optional)
  npm install @mastra/gcs           # GCSFilesystem (optional)
  npm install @mastra/e2b           # E2BSandbox (optional)

================================================================================
IMPORTS
================================================================================

```typescript
// Core workspace classes and tool constants
import { Workspace, LocalFilesystem, LocalSandbox, WORKSPACE_TOOLS } from '@mastra/core/workspace';

// Agent class - NOTE: singular 'agent', NOT 'agents'
import { Agent } from '@mastra/core/agent';

// Mastra class for global workspace assignment
import { Mastra } from '@mastra/core';

// Cloud providers (install separately)
import { S3Filesystem } from '@mastra/s3';
import { GCSFilesystem } from '@mastra/gcs';
import { E2BSandbox } from '@mastra/e2b';

// Versioned skill source (for custom skill backends)
import { VersionedSkillSource } from '@mastra/core/workspace';
```

================================================================================
WORKSPACE CLASS
================================================================================

The Workspace class is the central container.

### Constructor Parameters

```typescript
new Workspace({
  // --- Single Filesystem Provider ---
  filesystem?: WorkspaceFilesystem;  // Single filesystem provider

  // --- OR Multi-Provider Mounts (mutually exclusive with filesystem) ---
  mounts?: Record<string, WorkspaceFilesystem>;  // Mount providers at paths

  // --- Sandbox Provider ---
  sandbox?: WorkspaceSandbox;        // Command execution provider

  // --- Skills ---
  skills?: string[] | ((context: WorkspaceContext) => string[] | null[]);
  // Paths where SKILL.md files live. Array of paths, or function receiving
  // context that returns paths (can include nulls which are filtered out).

  skillSource?: VersionedSkillSource;
  // Custom skill source for versioned skill management

  // --- Search Configuration ---
  bm25?: boolean | { k1?: number; b?: number };
  // Enable BM25 keyword search. true for defaults, or pass custom params.
  // k1 = term frequency saturation, b = document length normalization

  vectorStore?: MastraVector;        // Vector store for semantic search
  embedder?: (text: string) => Promise<number[]>;
  // Embedding function, required when vectorStore is provided

  autoIndexPaths?: string[];
  // Paths or glob patterns to auto-index when init() is called
  // Example: ['/docs', '/support/faq']

  searchIndexName?: string;
  // Custom name for the vector search index
  // Example: 'my_workspace_vectors'

  // --- Tool Configuration ---
  tools?: {
    enabled?: boolean;               // Global enable/disable all tools
    requireApproval?: boolean;       // Global approval requirement
    // Per-tool overrides using WORKSPACE_TOOLS constants:
    [toolName: string]: {
      enabled?: boolean;
      requireApproval?: boolean;
      requireReadBeforeWrite?: boolean;
    } | boolean;
  };
});
```

### Configuration Patterns

Four valid configurations (mix and match capabilities):

1. **filesystem + sandbox** - Full local setup (file tools + command execution)
2. **mounts + sandbox** - Cloud storage FUSE-mounted into sandbox
3. **filesystem only** - Just file tools, no command execution
4. **sandbox only** - Just execute_command, no file tools

Note: `filesystem` and `mounts` are mutually exclusive. Use one or the other.

### Key Methods

```typescript
// Initialize workspace (creates directories, indexes content from autoIndexPaths)
await workspace.init();

// Manually index content
await workspace.index('/docs/guide.md', content, {
  metadata: { category: 'api' },
});

// Search indexed content (available when bm25 or vectorStore is configured)
const results = await workspace.search('query', {
  topK: 10,
  mode: 'hybrid',       // 'bm25' | 'vector' | 'hybrid'
  minScore: 0.5,        // Minimum relevance score threshold
  vectorWeight: 0.5,    // Weight for vector vs BM25 in hybrid mode (0-1)
});
```

### Full Basic Example

```typescript
import { Workspace, LocalFilesystem, LocalSandbox } from '@mastra/core/workspace';
import { Agent } from '@mastra/core/agent';

const workspace = new Workspace({
  filesystem: new LocalFilesystem({ basePath: './workspace' }),
  sandbox: new LocalSandbox({ workingDirectory: './workspace' }),
  skills: ['/skills'],
  bm25: true,
  autoIndexPaths: ['/docs', '/skills'],
});

await workspace.init();

const agent = new Agent({
  id: 'dev-agent',
  model: 'openai/gpt-4o',
  instructions: 'You are a helpful development assistant with file and command access.',
  workspace,
});

// Agent now has tools: read_file, write_file, edit_file, list_directory,
// delete, mkdir, file_stat, grep, execute_command, search_workspace, etc.
const response = await agent.generate('List all TypeScript files in the project');
```

### Global vs Agent-Scoped Workspace

```typescript
// Global - all agents created via Mastra inherit this workspace
const mastra = new Mastra({ workspace });

// Agent-scoped - overrides the global workspace for this agent only
const agent = new Agent({
  id: 'my-agent',
  model: 'openai/gpt-4o',
  workspace,  // This workspace takes priority over the global one
});
```

================================================================================
WORKSPACE TOOLS (AUTO-PROVIDED TO AGENTS)
================================================================================

When capabilities are configured, Mastra automatically adds these tools to
the agent's toolset:

### Filesystem Tools (when filesystem or mounts is configured)

| Tool Name                      | Description                                        |
|-------------------------------|----------------------------------------------------|
| mastra_workspace_read_file    | Read file contents, supports optional line ranges  |
| mastra_workspace_write_file   | Create or overwrite a file with new content        |
| mastra_workspace_edit_file    | Make targeted edits to an existing file            |
| mastra_workspace_list_directory| List contents of a directory                      |
| mastra_workspace_delete       | Delete a file or directory (supports recursive)    |
| mastra_workspace_mkdir        | Create a directory (creates parents automatically) |
| mastra_workspace_file_stat    | Get metadata (size, type, modification time)       |
| mastra_workspace_grep         | Search file contents with regex, glob filtering    |
| mastra_workspace_copy_file    | Copy a file to a new location                      |
| mastra_workspace_move_file    | Move or rename a file                              |

When readOnly is true on the filesystem, write tools (write_file, edit_file,
delete, mkdir) are NOT added to the agent's toolset.

### Sandbox Tool (when sandbox is configured)

| Tool Name                      | Description                                        |
|-------------------------------|----------------------------------------------------|
| execute_command               | Run shell commands in the sandbox environment       |

### Search Tool (when bm25 or vectorStore is configured)

| Tool Name                      | Description                                        |
|-------------------------------|----------------------------------------------------|
| search_workspace              | Search indexed content (keyword, semantic, hybrid)  |

### Tool Configuration with WORKSPACE_TOOLS

Control tool behavior with granular per-tool settings:

```typescript
import { WORKSPACE_TOOLS } from '@mastra/core/workspace';

const workspace = new Workspace({
  filesystem: new LocalFilesystem({ basePath: './workspace' }),
  sandbox: new LocalSandbox({ workingDirectory: './workspace' }),
  tools: {
    enabled: true,                    // Global: all tools enabled
    requireApproval: false,           // Global: no approval needed by default
    [WORKSPACE_TOOLS.FILESYSTEM.WRITE_FILE]: {
      requireApproval: true,          // Override: require approval for writes
      requireReadBeforeWrite: true,   // Must read file before overwriting
    },
    [WORKSPACE_TOOLS.FILESYSTEM.DELETE]: {
      enabled: false,                 // Disable delete entirely
    },
    [WORKSPACE_TOOLS.SANDBOX.EXECUTE_COMMAND]: {
      requireApproval: true,          // Require approval before running commands
    },
  },
});
```

Available WORKSPACE_TOOLS constants:
- WORKSPACE_TOOLS.FILESYSTEM.WRITE_FILE
- WORKSPACE_TOOLS.FILESYSTEM.DELETE
- WORKSPACE_TOOLS.SANDBOX.EXECUTE_COMMAND

Per-tool config options:
- enabled (boolean) - Whether the tool is available to agents
- requireApproval (boolean) - Whether user must approve before execution
- requireReadBeforeWrite (boolean) - For write tools, require reading first

================================================================================
FILESYSTEM PROVIDERS
================================================================================

All filesystem providers implement the WorkspaceFilesystem interface.

--------------------------------------------------------------------------------
LocalFilesystem
--------------------------------------------------------------------------------

The simplest provider. Operates directly on the local machine's filesystem.
Requires no external services.

Import: `import { LocalFilesystem } from '@mastra/core/workspace';`

### Configuration

```typescript
new LocalFilesystem({
  basePath: string;           // Root directory for all file operations (REQUIRED)
  contained?: boolean;        // Restrict operations within basePath (DEFAULT: true)
  readOnly?: boolean;         // Block all write operations (DEFAULT: false)
  allowedPaths?: string[];    // Additional absolute paths allowed beyond basePath
});
```

### Configuration Details

- **basePath**: All file paths are resolved relative to this directory. If the
  directory does not exist, it is created when init() is called.
- **contained**: When true (default), prevents path traversal attacks and
  symlink escapes. All operations must stay within basePath.
- **allowedPaths**: Useful with contained: true to grant access to specific
  directories outside basePath without disabling containment entirely.
- **readOnly**: When true, write tools are not added to the agent's toolset.

### Dynamic Path Access

You can modify allowed paths at runtime:

```typescript
const fs = new LocalFilesystem({
  basePath: './workspace',
  contained: true,
  allowedPaths: ['/home/user/.config'],
});

// Add new paths dynamically using updater function
fs.setAllowedPaths(prev => [...prev, '/new/path']);
```

### Example

```typescript
import { Workspace, LocalFilesystem } from '@mastra/core/workspace';

const workspace = new Workspace({
  filesystem: new LocalFilesystem({
    basePath: './agent-workspace',
    contained: true,
    readOnly: false,
    allowedPaths: ['/opt/shared-data'],
  }),
});

await workspace.init();
// basePath directory is created if it does not exist
```

--------------------------------------------------------------------------------
S3Filesystem
--------------------------------------------------------------------------------

Cloud filesystem backed by Amazon S3. Suitable for production deployments
and multi-agent scenarios that need shared, durable storage.

Install: `npm install @mastra/s3`
Import: `import { S3Filesystem } from '@mastra/s3';`

### Configuration

```typescript
new S3Filesystem({
  bucket: string;             // S3 bucket name (REQUIRED)
  region: string;             // AWS region (REQUIRED)
  accessKeyId: string;        // AWS access key ID (REQUIRED)
  secretAccessKey: string;    // AWS secret access key (REQUIRED)
});
```

### Example

```typescript
import { Workspace } from '@mastra/core/workspace';
import { S3Filesystem } from '@mastra/s3';

const workspace = new Workspace({
  filesystem: new S3Filesystem({
    bucket: 'my-agent-data',
    region: 'us-east-1',
    accessKeyId: process.env.AWS_ACCESS_KEY_ID!,
    secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY!,
  }),
});
```

--------------------------------------------------------------------------------
GCSFilesystem
--------------------------------------------------------------------------------

Cloud filesystem backed by Google Cloud Storage. Ideal for GCP-native
deployments.

Install: `npm install @mastra/gcs`
Import: `import { GCSFilesystem } from '@mastra/gcs';`

### Configuration

```typescript
new GCSFilesystem({
  bucket: string;             // GCS bucket name (REQUIRED)
});
```

### Example

```typescript
import { Workspace } from '@mastra/core/workspace';
import { GCSFilesystem } from '@mastra/gcs';

const workspace = new Workspace({
  filesystem: new GCSFilesystem({
    bucket: 'agent-skills',
  }),
});
```

================================================================================
MOUNTS: MULTI-PROVIDER FILESYSTEM COMPOSITION
================================================================================

Use mounts when you need multiple filesystem providers or cloud storage
accessible inside a sandbox. When you use the mounts option, Mastra creates
a CompositeFilesystem that routes file operations to the correct provider
based on path prefix.

### How Mounts Work

1. Each mount path maps to a filesystem provider
2. File operations are routed by path prefix
3. Cloud filesystems are FUSE-mounted into sandboxes automatically
4. Commands in the sandbox access mounted paths as local directories

### Important Rules

- Use `mounts` OR `filesystem`, not both (mutually exclusive)
- Each mount path must be unique and non-overlapping
- E2B sandboxes auto-install FUSE tools (s3fs-fuse for S3, gcsfuse for GCS)

### Multi-Provider Example

```typescript
import { Workspace, LocalFilesystem, LocalSandbox } from '@mastra/core/workspace';
import { S3Filesystem } from '@mastra/s3';
import { GCSFilesystem } from '@mastra/gcs';
import { E2BSandbox } from '@mastra/e2b';

const workspace = new Workspace({
  mounts: {
    '/local': new LocalFilesystem({ basePath: './local-data' }),
    '/data': new S3Filesystem({
      bucket: 'my-data-bucket',
      region: 'us-east-1',
      accessKeyId: process.env.AWS_ACCESS_KEY_ID!,
      secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY!,
    }),
    '/skills': new GCSFilesystem({
      bucket: 'agent-skills',
    }),
  },
  sandbox: new E2BSandbox({ id: 'multi-fs-sandbox' }),
});

await workspace.init();

// Agent file tools route by prefix:
//   read_file('/local/README.md')    -> LocalFilesystem
//   read_file('/data/dataset.csv')   -> S3Filesystem
//   read_file('/skills/review.md')   -> GCSFilesystem

// Sandbox commands access mounted paths directly:
//   execute_command('ls /data')      -> lists S3 bucket contents
//   execute_command('cat /skills/config.json') -> reads from GCS
```

================================================================================
SANDBOX PROVIDERS
================================================================================

Sandbox providers give agents the ability to execute shell commands. When you
configure a sandbox, Mastra adds the execute_command tool to the agent.

--------------------------------------------------------------------------------
LocalSandbox
--------------------------------------------------------------------------------

Executes commands on the local machine. Best for development, trusted agents,
and local automation.

Import: `import { LocalSandbox } from '@mastra/core/workspace';`

### Configuration

```typescript
new LocalSandbox({
  workingDirectory?: string;   // Working directory for commands
});
```

### Example

```typescript
import { Workspace, LocalFilesystem, LocalSandbox } from '@mastra/core/workspace';

const PROJECT_DIR = '/home/user/my-project';

const workspace = new Workspace({
  filesystem: new LocalFilesystem({ basePath: PROJECT_DIR }),
  sandbox: new LocalSandbox({
    workingDirectory: PROJECT_DIR,
  }),
});

await workspace.init();
// Agent can now run: execute_command('npm test')
```

### Security Considerations for LocalSandbox

- Commands run with the same permissions as the Node.js process
- Use requireApproval: true for execute_command in production
- For untrusted code, prefer E2BSandbox instead

--------------------------------------------------------------------------------
E2BSandbox
--------------------------------------------------------------------------------

Executes commands in cloud-based isolated sandboxes via E2B. Best for
untrusted code execution and production safety.

Install: `npm install @mastra/e2b`
Import: `import { E2BSandbox } from '@mastra/e2b';`

### Configuration

```typescript
new E2BSandbox({
  id?: string;                 // Sandbox identifier
});
```

### Example

```typescript
import { Agent } from '@mastra/core/agent';
import { Workspace, LocalFilesystem } from '@mastra/core/workspace';
import { E2BSandbox } from '@mastra/e2b';

const workspace = new Workspace({
  filesystem: new LocalFilesystem({ basePath: './workspace' }),
  sandbox: new E2BSandbox({ id: 'code-runner' }),
});

const agent = new Agent({
  id: 'code-executor',
  model: 'openai/gpt-4o',
  instructions: `You run code safely in a cloud sandbox. Always execute
    code the user provides and return the output.`,
  workspace,
});

const response = await agent.generate(
  'Run this Python script: print("Hello from E2B!")'
);
```

### E2B Mount Support

E2BSandbox supports FUSE mounting of cloud filesystems:

- S3 buckets are mounted via s3fs-fuse (auto-installed)
- GCS buckets are mounted via gcsfuse (auto-installed at mount time)

```typescript
const workspace = new Workspace({
  mounts: {
    '/data': new S3Filesystem({
      bucket: 'training-data',
      region: 'us-east-1',
      accessKeyId: process.env.AWS_ACCESS_KEY_ID!,
      secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY!,
    }),
  },
  sandbox: new E2BSandbox({ id: 'ml-sandbox' }),
});

// Commands in E2B sandbox can read/write /data as if local:
// execute_command('ls /data')
// execute_command('python train.py --data /data/dataset.csv')
```

================================================================================
SKILLS SYSTEM
================================================================================

Skills are reusable instructions that teach agents how to perform specific
tasks. They follow the Agent Skills specification (agentskills.io), an open
standard for packaging agent capabilities.

### What Skills Are

- A folder containing a SKILL.md file and optional supporting files
- SKILL.md has YAML frontmatter (metadata) + Markdown body (instructions)
- When an agent activates a skill, its instructions are added to context
- Agents can discover, search, and activate skills during conversations

### Skill Folder Structure

```
skills/
  my-skill/
    SKILL.md            # Required: instructions and metadata
    references/         # Optional: supporting documentation
      api-docs.md
      examples.md
    scripts/            # Optional: executable scripts
      setup.sh
      validate.ts
    assets/             # Optional: images and other files
      diagram.png
```

### SKILL.md Format

```markdown
---
name: code-review
description: Reviews code for quality, security, and best practices
version: 1.0.0
tags: [code-quality, security, review]
---

# Code Review Skill

## Overview
This skill teaches you how to perform thorough code reviews.

## Instructions
1. Read the file using workspace tools
2. Check for security vulnerabilities
3. Check for code quality issues
4. Provide structured feedback

## Output Format
Provide feedback as a structured list with severity levels.
```

### Configuring Skills in a Workspace

```typescript
const workspace = new Workspace({
  filesystem: new LocalFilesystem({ basePath: './workspace' }),

  // Static array of paths
  skills: ['/skills'],

  // Dynamic function with context parameter
  // The function receives a context object and can return nulls (filtered out)
  skills: context => [
    '/skills',
    context.user?.role === 'developer' ? '/dev-skills' : null,
  ],

  // Custom versioned skill source for advanced use cases
  skillSource: new VersionedSkillSource(versionTree, blobStore, versionCreatedAt),

  bm25: true,  // Enable search over skill content
});
```

### How Skills Work at Runtime

1. Agent discovers available skills via search or listing
2. Agent activates a skill relevant to the current task
3. Skill instructions are added to the agent's context
4. Agent follows the skill instructions, using workspace tools as needed
5. Agent can access the skill's references/ and scripts/ directories

### Skills with Search

If BM25 or vector search is enabled on the workspace, skills are
automatically indexed. Agents can search across skill content to find
relevant instructions for their current task.

================================================================================
SEARCH AND INDEXING
================================================================================

Workspaces support three search modes for finding content across files
and skills:

  1. BM25 Keyword Search - Term frequency and document length scoring
  2. Vector Semantic Search - Embedding-based similarity matching
  3. Hybrid Search - Combines both BM25 and vector for best results

### BM25 Keyword Search

BM25 scores documents based on term frequency and document length. Works
well for exact matches and specific terminology.

```typescript
const workspace = new Workspace({
  filesystem: new LocalFilesystem({ basePath: './docs' }),
  bm25: true,                   // Enable with defaults
  autoIndexPaths: ['/docs'],    // Index these paths on init()
});

// OR with custom parameters:
const workspace = new Workspace({
  filesystem: new LocalFilesystem({ basePath: './docs' }),
  bm25: {
    k1: 1.5,                    // Term frequency saturation
    b: 0.75,                    // Document length normalization
  },
  autoIndexPaths: ['**/*.md'],  // Glob patterns supported
});
```

### Vector Semantic Search

Vector search uses embeddings to find semantically similar content.
Requires a vector store and an embedder function.

```typescript
import { embed } from 'ai';
import { openai } from '@ai-sdk/openai';

const workspace = new Workspace({
  filesystem: new LocalFilesystem({ basePath: './knowledge-base' }),
  vectorStore: new PineconeVector({ apiKey, index }),
  embedder: async (text: string) => {
    // Using AI SDK embed function (recommended approach from docs)
    const { embedding } = await embed({
      model: openai.embedding('text-embedding-3-small'),
      value: text,
    });
    return embedding;
  },
  searchIndexName: 'my_workspace_vectors',
  autoIndexPaths: ['/knowledge-base'],
});
```

### Hybrid Search (BM25 + Vector)

Enable both BM25 and vector search for the best of both worlds:

```typescript
const workspace = new Workspace({
  filesystem: new LocalFilesystem({ basePath: './docs' }),
  bm25: true,
  vectorStore: vectorStore,
  embedder: embedderFn,
  autoIndexPaths: ['/docs', '/skills'],
});

await workspace.init();
// init() reads all files in autoIndexPaths and:
//   - BM25: computes term frequencies and document statistics
//   - Vector: embeds content and stores in vector store
```

### Manual Indexing

Index content programmatically with optional metadata:

```typescript
await workspace.index('/docs/guide.md', content, {
  metadata: { category: 'api' },
});
```

### Auto-Indexing

When init() is called, all files in autoIndexPaths are read and indexed.
Paths support glob patterns for selective indexing:

```typescript
autoIndexPaths: [
  '/docs',                // Index everything in /docs recursively
  '/support/faq',         // Index FAQ content
  '/skills',              // Index all skills
  '**/*.md',              // Index all markdown files anywhere
]
```

### Search API

```typescript
const results = await workspace.search('authentication middleware', {
  topK: 10,              // Maximum number of results
  mode: 'hybrid',        // 'bm25' | 'vector' | 'hybrid'
  minScore: 0.5,         // Minimum relevance score threshold
  vectorWeight: 0.5,     // Weight for vector vs BM25 in hybrid (0-1)
});

for (const result of results) {
  console.log(`[${result.score.toFixed(2)}] ${result.id}`);
  console.log(result.content.slice(0, 200));
}
```

### Search Results Structure

```typescript
interface SearchResult {
  id: string;                  // Document identifier
  content: string;             // Matching content
  score: number;               // Relevance score (0-1)
  lineRange?: {                // Optional line range in source file
    start: number;
    end: number;
  };
  metadata?: Record<string, any>; // Optional metadata
  scoreDetails?: {             // Score breakdown in hybrid mode
    vector?: number;
    bm25?: number;
  };
}
```

================================================================================
WORKSPACE + AGENT INTEGRATION
================================================================================

Attaching a workspace to an agent is a single configuration property.

### Minimal Agent with Workspace

```typescript
import { Agent } from '@mastra/core/agent';
import { Workspace, LocalFilesystem, LocalSandbox } from '@mastra/core/workspace';

const workspace = new Workspace({
  filesystem: new LocalFilesystem({ basePath: './data' }),
  sandbox: new LocalSandbox({ workingDirectory: './data' }),
});

const agent = new Agent({
  id: 'assistant',
  model: 'openai/gpt-4o',
  instructions: 'You help users manage files and run commands.',
  workspace,
});

// Agent automatically gets: read_file, write_file, edit_file,
// list_directory, delete, mkdir, file_stat, grep, execute_command
```

### Full-Featured Agent with All Capabilities

```typescript
import { Agent } from '@mastra/core/agent';
import { Workspace, LocalFilesystem, LocalSandbox, WORKSPACE_TOOLS } from '@mastra/core/workspace';

const workspace = new Workspace({
  filesystem: new LocalFilesystem({
    basePath: './project',
    contained: true,
  }),
  sandbox: new LocalSandbox({
    workingDirectory: './project',
  }),
  skills: ['./skills'],
  bm25: true,
  vectorStore: vectorStore,
  embedder: embedderFn,
  autoIndexPaths: ['/src', '/docs', '/skills'],
  tools: {
    enabled: true,
    requireApproval: false,
    [WORKSPACE_TOOLS.FILESYSTEM.WRITE_FILE]: {
      requireApproval: true,
      requireReadBeforeWrite: true,
    },
    [WORKSPACE_TOOLS.FILESYSTEM.DELETE]: {
      enabled: false,
    },
    [WORKSPACE_TOOLS.SANDBOX.EXECUTE_COMMAND]: {
      requireApproval: true,
    },
  },
});

await workspace.init();

const devAgent = new Agent({
  id: 'dev-assistant',
  model: 'openai/gpt-4o',
  instructions: `You are a development assistant with full workspace access.
    You can read/write files, run commands, search code, and use skills.
    Always search the codebase before making changes.
    Ask for approval before writing files or running commands.`,
  workspace,
});
```

### Global Workspace via Mastra

Assign a workspace globally so all agents inherit it:

```typescript
import { Mastra } from '@mastra/core';
import { Workspace, LocalFilesystem, LocalSandbox } from '@mastra/core/workspace';
import { Agent } from '@mastra/core/agent';

const workspace = new Workspace({
  filesystem: new LocalFilesystem({ basePath: './workspace' }),
  sandbox: new LocalSandbox({ workingDirectory: './workspace' }),
});

// All agents created through this Mastra instance inherit the workspace
const mastra = new Mastra({ workspace });

// Agent-scoped workspace overrides the global one
const specialAgent = new Agent({
  id: 'special',
  model: 'openai/gpt-4o',
  workspace: differentWorkspace,  // Overrides global
});
```

================================================================================
COMMON PATTERNS
================================================================================

### Pattern 1: Document Manager Agent

An agent that reads, writes, and organizes documents.

```typescript
import { Agent } from '@mastra/core/agent';
import { Workspace, LocalFilesystem } from '@mastra/core/workspace';

const docWorkspace = new Workspace({
  filesystem: new LocalFilesystem({ basePath: './documents' }),
  bm25: true,
  autoIndexPaths: ['/documents'],
});

await docWorkspace.init();

const docAgent = new Agent({
  id: 'doc-agent',
  model: 'openai/gpt-4o',
  instructions: `You manage a document library. You can:
    - Search for documents by content
    - Read and summarize documents
    - Create new documents
    - Organize files into directories
    Always search before creating to avoid duplicates.`,
  workspace: docWorkspace,
});

const response = await docAgent.generate(
  'Find all documents about authentication and summarize them'
);
```

### Pattern 2: Code Execution Agent

An agent that writes and runs code in a safe sandbox.

```typescript
import { Agent } from '@mastra/core/agent';
import { Workspace, LocalFilesystem } from '@mastra/core/workspace';
import { E2BSandbox } from '@mastra/e2b';

const codeWorkspace = new Workspace({
  filesystem: new LocalFilesystem({ basePath: './sandbox-files' }),
  sandbox: new E2BSandbox({ id: 'code-exec' }),
});

const codeAgent = new Agent({
  id: 'code-agent',
  model: 'openai/gpt-4o',
  instructions: `You execute code safely in a cloud sandbox.
    1. Write the code to a file using write_file
    2. Run the code using execute_command
    3. Return the output to the user
    Support Python, Node.js, and shell scripts.`,
  workspace: codeWorkspace,
});

const response = await codeAgent.generate(
  'Write a Python script that generates the first 20 Fibonacci numbers and run it'
);
```

### Pattern 3: Research Agent with Hybrid Search

An agent that indexes documents and answers questions using hybrid search.

```typescript
import { Agent } from '@mastra/core/agent';
import { Workspace, LocalFilesystem } from '@mastra/core/workspace';

const researchWorkspace = new Workspace({
  filesystem: new LocalFilesystem({
    basePath: './research-docs',
    readOnly: true,  // Agent can only read, not modify
  }),
  bm25: true,
  vectorStore: vectorStore,
  embedder: embedderFn,
  autoIndexPaths: ['/research-docs'],
  searchIndexName: 'research_vectors',
});

await researchWorkspace.init();

const researcher = new Agent({
  id: 'researcher',
  model: 'openai/gpt-4o',
  instructions: `You are a research assistant. Use search_workspace to find
    relevant documents before answering questions. Cite your sources.
    If the answer is not in the documents, say so clearly.`,
  workspace: researchWorkspace,
});
```

### Pattern 4: Full Dev Assistant

Combines filesystem, sandbox, search, and skills for a complete development
assistant.

```typescript
import { Agent } from '@mastra/core/agent';
import { Workspace, LocalFilesystem, LocalSandbox, WORKSPACE_TOOLS } from '@mastra/core/workspace';

const PROJ_DIR = '/home/user/my-app';

const devWorkspace = new Workspace({
  filesystem: new LocalFilesystem({
    basePath: PROJ_DIR,
    contained: true,
    allowedPaths: ['/usr/local/bin'],
  }),
  sandbox: new LocalSandbox({
    workingDirectory: PROJ_DIR,
  }),
  skills: ['/skills'],
  bm25: true,
  autoIndexPaths: ['/src', '/docs', '/skills'],
  tools: {
    enabled: true,
    requireApproval: false,
    [WORKSPACE_TOOLS.FILESYSTEM.WRITE_FILE]: {
      requireApproval: true,
      requireReadBeforeWrite: true,
    },
    [WORKSPACE_TOOLS.FILESYSTEM.DELETE]: {
      requireApproval: true,
    },
    [WORKSPACE_TOOLS.SANDBOX.EXECUTE_COMMAND]: {
      requireApproval: true,
    },
  },
});

await devWorkspace.init();

const devAssistant = new Agent({
  id: 'dev-assistant',
  model: 'openai/gpt-4o',
  instructions: `You are a full-stack development assistant.

    Capabilities:
    - Read, write, and edit source code files
    - Run shell commands (npm, git, tests, builds)
    - Search the codebase for relevant code and documentation
    - Use skills for specialized tasks (code review, testing, etc.)

    Workflow:
    1. Search the codebase to understand existing patterns
    2. Read relevant files before making changes
    3. Make targeted edits (prefer edit_file over write_file)
    4. Run tests after changes
    5. Summarize what you did`,
  workspace: devWorkspace,
});
```

### Pattern 5: Dynamic Skills with Context

Skills that vary based on runtime context (user role, environment, etc.).

```typescript
import { Agent } from '@mastra/core/agent';
import { Workspace, LocalFilesystem } from '@mastra/core/workspace';

const workspace = new Workspace({
  filesystem: new LocalFilesystem({ basePath: './workspace' }),
  skills: context => [
    '/skills',
    context.user?.role === 'developer' ? '/dev-skills' : null,
  ],
  bm25: true,
});
```

### Pattern 6: Production Setup with Cloud Storage + E2B

Cloud-native setup for production workloads.

```typescript
import { Agent } from '@mastra/core/agent';
import { Workspace } from '@mastra/core/workspace';
import { S3Filesystem } from '@mastra/s3';
import { GCSFilesystem } from '@mastra/gcs';
import { E2BSandbox } from '@mastra/e2b';

const workspace = new Workspace({
  mounts: {
    '/data': new S3Filesystem({
      bucket: 'prod-agent-data',
      region: 'us-east-1',
      accessKeyId: process.env.AWS_ACCESS_KEY_ID!,
      secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY!,
    }),
    '/skills': new GCSFilesystem({
      bucket: 'agent-skills',
    }),
  },
  sandbox: new E2BSandbox({ id: 'prod-sandbox' }),
  skills: ['/skills'],
  bm25: true,
  vectorStore: vectorStore,
  embedder: embedderFn,
  autoIndexPaths: ['/data/docs'],
  searchIndexName: 'prod_workspace_vectors',
});

const prodAgent = new Agent({
  id: 'prod-agent',
  model: 'openai/gpt-4o',
  workspace,
});
```

================================================================================
BEST PRACTICES
================================================================================

### Filesystem Selection

- Use LocalFilesystem for development and local automation
- Use S3Filesystem for production on AWS (durable, scalable, shared)
- Use GCSFilesystem for production on GCP
- Use mounts to combine multiple providers under different paths
- Always set contained: true for LocalFilesystem in production
- Use readOnly: true when agents should only read, not modify
- Use setAllowedPaths() for dynamic path access at runtime

### Sandbox Selection

- Use LocalSandbox for development and trusted agent code
- Use E2BSandbox for untrusted code execution in production
- LocalSandbox: commands run with Node.js process permissions (be careful)
- E2BSandbox: fully isolated cloud environment
- Always set requireApproval: true for execute_command in production

### Security

- Use contained: true on LocalFilesystem to prevent path traversal
- Use allowedPaths to grant specific additional directory access
- Enable requireReadBeforeWrite for write tools to prevent blind overwrites
- Use requireApproval for destructive operations (delete, write, execute)
- Use enabled: false on WORKSPACE_TOOLS.FILESYSTEM.DELETE to disable delete

### Search and Indexing

- Enable BM25 for keyword search (no external dependencies needed)
- Add vectorStore + embedder for semantic search capabilities
- Enable both for hybrid search (best results for most use cases)
- Use autoIndexPaths to index on workspace.init()
- Use glob patterns in autoIndexPaths for selective indexing
- Use workspace.index() for manual indexing with metadata
- Skills are automatically indexed when search is enabled
- Use searchIndexName to customize the vector index name
- Use mode, minScore, and vectorWeight in search() for fine-tuned results

### Performance

- Call workspace.init() at application startup to avoid first-use latency
- Use specific autoIndexPaths rather than indexing everything
- Combine filesystem and sandbox on the same directory for LocalFilesystem
  and LocalSandbox so files written are immediately available to commands

### Skills

- Follow the Agent Skills spec (agentskills.io) for portable skills
- Keep skills focused on one task/concern each
- Include references/ for supporting documentation
- Include scripts/ for automation the agent can execute
- Enable BM25 search so agents can discover skills by content
- Use dynamic skills function with context for role-based skill loading
- Use VersionedSkillSource for custom skill backends with versioning

================================================================================
DOCUMENTATION LINKS
================================================================================

Overview & Guides:
- Workspace Overview: https://mastra.ai/docs/workspace/overview
- Filesystem Guide: https://mastra.ai/docs/workspace/filesystem
- Sandbox Guide: https://mastra.ai/docs/workspace/sandbox
- Skills Guide: https://mastra.ai/docs/workspace/skills
- Search and Indexing: https://mastra.ai/docs/workspace/search

Blog & Announcements:
- Announcing Workspaces: https://mastra.ai/blog/announcing-mastra-workspaces
- Announcing Skills: https://mastra.ai/blog/announcing-mastra-skills
- Agent Skills Spec: https://agentskills.io/specification

Templates & Examples:
- Coding Agent Template: https://mastra.ai/templates/coding-agent
- Official Skills Repo: https://github.com/mastra-ai/skills

================================================================================
SKILL_EOF
