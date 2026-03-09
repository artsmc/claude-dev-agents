---
name: mastra-rag
description: Mastra RAG pipeline development - document processing, chunking, embedding, vector databases, retrieval, GraphRAG, and agent integration tools
---

# Mastra RAG Pipeline Development

Comprehensive guide for building retrieval-augmented generation pipelines with Mastra. Covers document processing (MDocument), chunking strategies, embedding with AI SDK, 17+ vector database providers, retrieval patterns, reranking, GraphRAG, and agent integration tools.

## Usage

```bash
/mastra-rag
```

Provides context for:
- `MDocument` class (fromText, fromMarkdown, fromHTML)
- Chunking with `.chunk({ strategy, maxSize, overlap })`
- Embedding via AI SDK `embed()` from `'ai'`
- Vector store setup (PgVector, Pinecone, Qdrant, Chroma, etc.)
- `createVectorQueryTool()`, `createDocumentChunkerTool()`, `createGraphRAGTool()`
- Reranking with `rerank()` and `rerankWithScorer()`
- Metadata filters
