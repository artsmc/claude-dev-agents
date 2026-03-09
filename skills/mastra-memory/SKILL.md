---
name: mastra-memory
description: Mastra Memory system guide - storage backends, message history, observational memory, working memory, semantic recall, and thread management
---

# Mastra Memory System Development

Comprehensive guide for configuring Mastra memory systems. Covers storage backends, message history, observational memory (auto fact extraction), working memory (structured state), semantic recall (embedding-based), and thread management. Memory features are configured via options, not processor classes.

## Usage

```bash
/mastra-memory
```

Provides context for:
- `Memory` class constructor with options-based config
- Storage backends (LibSQLStore, PostgresStore, UpstashStore)
- `options.lastMessages` for message history
- `options.semanticRecall` for embedding-based recall
- `options.workingMemory` for structured state
- `options.observationalMemory` for fact extraction
- Thread management and cloning
- Agent integration via `memory` property
