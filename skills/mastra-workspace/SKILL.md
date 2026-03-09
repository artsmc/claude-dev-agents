---
name: mastra-workspace
description: Mastra Workspace development - filesystem providers, sandbox execution, skills system, search/indexing, and tool configuration
---

# Mastra Workspace Development

Comprehensive guide for Mastra workspaces. Covers filesystem providers (LocalFilesystem, S3Filesystem, GCSFilesystem), sandbox execution (LocalSandbox, E2BSandbox), mounts for multi-provider composition, skills system (Agent Skills spec), BM25/vector/hybrid search, tool configuration with WORKSPACE_TOOLS, and containment security.

## Usage

```bash
/mastra-workspace
```

Provides context for:
- `Workspace` class from `@mastra/core/workspace`
- `filesystem` vs `mounts` (mutually exclusive)
- `LocalFilesystem({ basePath, contained, readOnly, allowedPaths })`
- `LocalSandbox({ workingDirectory })` and `E2BSandbox({ id })`
- `WORKSPACE_TOOLS` for per-tool config (enabled, requireApproval, requireReadBeforeWrite)
- Skills with SKILL.md (Agent Skills spec)
- Search: `workspace.search()`, `workspace.index()`, BM25/vector/hybrid
- Global workspace via `Mastra({ workspace })` or agent-scoped
