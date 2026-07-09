# /mastra-rag

> Mastra RAG pipeline development - document processing, chunking, embedding, vector databases, retrieval, GraphRAG, and agent integration tools

## What it does

Loads validated patterns for retrieval-augmented generation with Mastra: `MDocument` (fromText/fromMarkdown/fromHTML), chunking strategies via `.chunk({ strategy, maxSize, overlap })`, embedding with the AI SDK `embed()`, 17+ vector store providers (PgVector, Pinecone, Qdrant, Chroma, ...), the RAG agent tools (`createVectorQueryTool()`, `createDocumentChunkerTool()`, `createGraphRAGTool()`), reranking, and metadata filters. One of the ten satellite guides routed to by `/mastra-dev`.

## When it triggers

- "Build a RAG pipeline in Mastra"
- "Chunk and embed these documents"
- "Set up pgvector/Pinecone with Mastra"
- "Give my agent a vector search tool"
- "Add reranking or GraphRAG to retrieval"

## Usage

```bash
/mastra-rag
```

No flags. On-demand guide pattern: `SKILL.md` is a thin stub; the full guide is printed by `bash skill.sh`.

## Context cost

Description always in context (~160 chars); SKILL.md body loads on trigger (~0.9k chars); full guide via `skill.sh` (~33k chars) only when executed.

## Files

| File | Purpose |
|---|---|
| `SKILL.md` | Frontmatter + stub (~0.9k chars) |
| `skill.sh` | Prints the full RAG pipeline guide (~33k chars) |

## Related skills

- `/mastra-dev` — CLI hub that routes here for RAG concepts
- `/mastra-memory` — semantic recall over conversation history vs RAG over documents
- `/mastra-agents` — binding the RAG tools onto an agent
