# /mastra-workspace

> Mastra Workspace development - filesystem providers, sandbox execution, skills system, search/indexing, and tool configuration

## What it does

Loads validated patterns for Mastra workspaces: the `Workspace` class from `@mastra/core/workspace`, filesystem providers (`LocalFilesystem`, `S3Filesystem`, `GCSFilesystem`), `filesystem` vs `mounts` (mutually exclusive), sandbox execution (`LocalSandbox`, `E2BSandbox`), the skills system (Agent Skills spec with SKILL.md), BM25/vector/hybrid search via `workspace.search()`/`workspace.index()`, per-tool config with `WORKSPACE_TOOLS`, and containment security. One of the ten satellite guides routed to by `/mastra-dev`.

## When it triggers

- "Give my Mastra agent a filesystem / workspace"
- "Run agent code in a sandbox (local or E2B)"
- "Add skills to a Mastra agent" (Agent Skills spec)
- "Index and search workspace files"
- "Restrict what workspace tools an agent can use"

## Usage

```bash
/mastra-workspace
```

No flags. On-demand guide pattern: `SKILL.md` is a thin stub; the full guide is printed by `bash skill.sh`.

## Context cost

Description always in context (~140 chars); SKILL.md body loads on trigger (~1.1k chars); full guide via `skill.sh` (~40k chars) only when executed.

## Files

| File | Purpose |
|---|---|
| `SKILL.md` | Frontmatter + stub (~1.1k chars) |
| `skill.sh` | Prints the full workspace development guide (~40k chars) |

## Related skills

- `/mastra-dev` — CLI hub that routes here for workspace concepts
- `/mastra-agents` — agent-scoped workspaces and tool binding
- `/mastra-rag` — vector retrieval over documents vs workspace file search
