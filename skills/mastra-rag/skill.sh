#!/usr/bin/env bash
# mastra-rag - Mastra RAG (Retrieval-Augmented Generation) pipeline development
cat << 'SKILL_EOF'

================================================================================
MASTRA RAG (RETRIEVAL-AUGMENTED GENERATION) SKILL
================================================================================

Use this skill when building RAG pipelines with Mastra. Covers document
ingestion, chunking, embedding, vector storage, retrieval, and generation.

Package: @mastra/rag (core RAG utilities)
Embedding: Uses Vercel AI SDK (ai package) with @mastra/core/llm model router
Docs: https://mastra.ai/docs/rag/overview

================================================================================
RAG PIPELINE OVERVIEW
================================================================================

The RAG pipeline follows this flow:

  Document Ingestion --> Chunking --> Embedding --> Vector Storage
                                                        |
  User Query --> Embed Query --> Similarity Search ------+
                                        |
                                  Retrieved Chunks --> LLM Generation --> Response

Mastra provides end-to-end support for every stage of this pipeline through
the @mastra/rag package, Vercel AI SDK embedding functions, and vector store
integrations.

Install:
  npm install @mastra/rag ai @mastra/core

================================================================================
DOCUMENT PROCESSING
================================================================================

MDocument is the entry point for loading documents into the RAG pipeline.
It supports multiple input formats.

### Creating Documents

```typescript
import { MDocument } from '@mastra/rag';

// From plain text
const textDoc = MDocument.fromText('Long document content here...');

// From markdown
const mdDoc = MDocument.fromMarkdown(`
# Architecture Guide

## Overview
This system uses a microservices architecture...

## Components
- API Gateway
- Auth Service
- Data Pipeline
`);

// From HTML
const htmlDoc = MDocument.fromHTML(`
<html>
<body>
  <h1>Product Documentation</h1>
  <p>This guide covers installation and configuration...</p>
</body>
</html>
`);

// From JSON
const jsonDoc = MDocument.fromJSON(JSON.stringify({
  title: 'API Reference',
  endpoints: [
    { path: '/users', method: 'GET', description: 'List all users' },
    { path: '/users/:id', method: 'GET', description: 'Get user by ID' }
  ]
}));
```

### MDocument Constructor (Alternative)

```typescript
const doc = new MDocument({
  text: 'Your document content here...',
  metadata: { source: 'user-manual' }
});
```

### MDocument Methods

| Method           | Description                                    |
|------------------|------------------------------------------------|
| fromText()       | Create from plain text                         |
| fromHTML()       | Create from HTML content                       |
| fromMarkdown()   | Create from Markdown content                   |
| fromJSON()       | Create from JSON content                       |
| chunk()          | Split document into chunks                     |
| getDocs()        | Retrieve processed document chunks             |
| getText()        | Return text strings from chunks                |
| getMetadata()    | Return metadata objects from chunks            |
| extractMetadata()| Extract metadata using specified extractors    |

================================================================================
CHUNKING STRATEGIES
================================================================================

After loading a document, chunk it into smaller pieces for embedding.
Choose the strategy based on your content type.

### Available Strategies

| Strategy           | Best For                               | Description                                  |
|--------------------|----------------------------------------|----------------------------------------------|
| recursive          | General text (DEFAULT)                 | Splits on paragraphs, sentences, words       |
| character          | Simple, predictable splits             | Splits at character boundaries               |
| token              | LLM token-aware splitting              | Splits based on token count                  |
| markdown           | Markdown documents                     | Splits on markdown structure (headers)       |
| semantic-markdown  | Markdown with related header families  | Merges related sections by semantic meaning  |
| html               | HTML content                           | Splits on HTML tags and structure            |
| json               | JSON data                              | Splits on JSON keys/structure                |
| latex              | LaTeX documents                        | Splits on LaTeX sections                     |
| sentence           | Sentence-boundary splitting            | Respects sentence boundaries                 |

### Basic Chunking

```typescript
const doc = MDocument.fromText('Long document content...');

// Default recursive chunking
const chunks = await doc.chunk({
  strategy: 'recursive',
  maxSize: 512,
  overlap: 50
});
```

### Strategy-Specific Examples

```typescript
// Recursive (best general-purpose strategy)
const chunks = await doc.chunk({
  strategy: 'recursive',
  maxSize: 512,
  overlap: 50,
  separators: ['\n\n', '\n', '. ', ' '], // Custom separators
  extract: { metadata: true }             // Extract metadata (summary, keywords)
});

// Token-based (respects LLM token limits)
const chunks = await doc.chunk({
  strategy: 'token',
  maxSize: 256,       // tokens, not characters
  overlap: 20,
  modelName: 'gpt-4o',       // Tokenizer model
  encodingName: 'cl100k_base' // Or specify encoding directly
});

// Markdown-aware (preserves document structure)
const chunks = await doc.chunk({
  strategy: 'markdown',
  maxSize: 1000,
  overlap: 100
  // Splits on headers: #, ##, ###, etc.
});

// Semantic-markdown (merges related header families)
const chunks = await doc.chunk({
  strategy: 'semantic-markdown',
  joinThreshold: 500,    // Token threshold for merging sections
  modelName: 'gpt-3.5-turbo'
});

// Sentence-aware splitting
const chunks = await doc.chunk({
  strategy: 'sentence',
  maxSize: 450,
  minSize: 50,
  overlap: 0,
  sentenceEnders: ['.', '!', '?']
});

// HTML-aware
const chunks = await doc.chunk({
  strategy: 'html',
  maxSize: 1000,
  overlap: 100,
  headers: [
    ['h1', 'Header 1'],
    ['h2', 'Header 2']
  ]
});

// JSON chunking
const chunks = await doc.chunk({
  strategy: 'json',
  maxSize: 500,
  minSize: 100
});
```

### General Chunk Parameters

| Parameter       | Default | Description                                    |
|-----------------|---------|------------------------------------------------|
| strategy        | auto    | Chunking strategy (auto-selects based on type) |
| maxSize         | 4000    | Maximum chunk size in characters               |
| overlap         | 50      | Overlap between sequential chunks              |
| stripWhitespace | true    | Strip leading/trailing whitespace              |
| addStartIndex   | false   | Add position metadata to chunks                |
| extract         | -       | Enable metadata extraction (summary, keywords) |

### Chunking Best Practices

- Start with `recursive` strategy and maxSize 512 for most use cases
- Use `overlap` of 10-20% of chunk size to preserve context at boundaries
- Use `markdown` strategy for markdown docs to preserve heading hierarchy
- Use `semantic-markdown` to merge related header sections
- Use `token` strategy when you need precise token-count control
- Use `sentence` strategy for clean sentence-boundary splits
- Smaller chunks (256-512) = more precise retrieval
- Larger chunks (1024-2048) = more context per result

================================================================================
EMBEDDING
================================================================================

Mastra uses the Vercel AI SDK (ai package) for embedding, with the
ModelRouterEmbeddingModel from @mastra/core/llm for provider routing.

IMPORTANT: Embedding functions come from 'ai' package, NOT from '@mastra/rag'.
The model router comes from '@mastra/core/llm'.

### Basic Embedding

```typescript
import { embed, embedMany } from 'ai';
import { ModelRouterEmbeddingModel } from '@mastra/core/llm';

// Embed a single string
const { embedding } = await embed({
  model: new ModelRouterEmbeddingModel('openai/text-embedding-3-small'),
  value: 'Query text here',
  maxRetries: 2
});

// Embed multiple chunks at once
const { embeddings } = await embedMany({
  model: new ModelRouterEmbeddingModel('openai/text-embedding-3-small'),
  values: chunks.map(c => c.text),
  maxRetries: 2
});
```

### Custom Dimensions

OpenAI text-embedding-3 models support custom dimensions:

```typescript
const { embeddings } = await embedMany({
  model: new ModelRouterEmbeddingModel('openai/text-embedding-3-small'),
  values: chunks.map(c => c.text),
  options: { dimensions: 256 }
});
```

### Embedding Parameters (embed / embedMany)

| Parameter    | Type              | Required | Description                         |
|-------------|-------------------|----------|-------------------------------------|
| model       | EmbeddingModel    | Yes      | Embedding model instance            |
| value/values| string or string[]| Yes      | Text to embed                       |
| maxRetries  | number            | No       | Retry attempts (default: 2)         |
| abortSignal | AbortSignal       | No       | Request cancellation control        |
| headers     | Record            | No       | Custom HTTP headers for providers   |

### Return Values

- embed() returns: { embedding: number[] }
- embedMany() returns: { embeddings: number[][] }

### Embedding Providers (via Model Router)

| Provider String               | Dimensions | Notes                    |
|-------------------------------|------------|--------------------------|
| openai/text-embedding-3-small | 1536       | Good balance cost/quality|
| openai/text-embedding-3-large | 3072       | Highest quality          |
| openai/text-embedding-ada-002 | 1536       | Legacy, still works      |
| cohere/embed-english-v3.0     | 1024       | English optimized        |
| cohere/embed-multilingual-v3.0| 1024       | Multilingual             |

IMPORTANT: Index dimension must match embedding model dimensions.

================================================================================
VECTOR DATABASE INTEGRATION
================================================================================

Mastra supports 13+ vector store backends. Each requires its own package.

### Supported Vector Stores

| Store               | Package                  | Best For                          |
|---------------------|--------------------------|-----------------------------------|
| PgVector            | @mastra/pg               | Existing PostgreSQL infrastructure|
| Pinecone            | @mastra/pinecone         | Managed cloud vector DB           |
| Qdrant              | @mastra/qdrant           | High-performance self-hosted      |
| Chroma              | @mastra/chroma           | Local development, prototyping    |
| MongoDB Atlas       | @mastra/mongodb          | Existing MongoDB infrastructure   |
| Astra DB            | @mastra/astra            | DataStax managed Cassandra        |
| LanceDB             | @mastra/lance            | Embedded, serverless              |
| libSQL              | @mastra/libsql           | Edge/embedded SQLite              |
| Upstash             | @mastra/upstash          | Serverless Redis-based            |
| Elasticsearch       | @mastra/elasticsearch    | Full-text + vector hybrid         |
| OpenSearch          | @mastra/opensearch       | AWS-native search + vector        |
| Cloudflare Vectorize| @mastra/vectorize        | Cloudflare Workers                |
| Couchbase           | @mastra/couchbase        | Multi-model database              |

### PgVector (Recommended for AIForge)

```typescript
import { PgVector } from '@mastra/pg';

const vectorStore = new PgVector({
  id: 'pg-vector',
  connectionString: process.env.POSTGRES_CONNECTION_STRING
});

// Create an index (table with vector column)
await vectorStore.createIndex({
  indexName: 'knowledge-base',
  dimension: 1536,        // Must match embedding model dimensions
  metric: 'cosine'        // or 'euclidean', 'dotProduct'
});

// Upsert embeddings with metadata
await vectorStore.upsert({
  indexName: 'knowledge-base',
  vectors: embeddings,
  metadata: chunks.map((chunk, i) => ({
    text: chunk.text,
    source: chunk.metadata?.source,
    chunkIndex: i
  }))
});

// Query for similar vectors
const results = await vectorStore.query({
  indexName: 'knowledge-base',
  queryVector: queryEmbedding,
  topK: 5,
  filter: {
    source: { $eq: 'technical-docs' }
  },
  includeMetadata: true
});
```

### Pinecone

```typescript
import { PineconeVector } from '@mastra/pinecone';

const vectorStore = new PineconeVector({
  apiKey: process.env.PINECONE_API_KEY,
  environment: process.env.PINECONE_ENVIRONMENT
});

await vectorStore.createIndex({
  indexName: 'my-index',
  dimension: 1536,
  metric: 'cosine'
});
```

### Qdrant

```typescript
import { QdrantVector } from '@mastra/qdrant';

const vectorStore = new QdrantVector({
  url: process.env.QDRANT_URL || 'http://localhost:6333',
  apiKey: process.env.QDRANT_API_KEY // optional for local
});

await vectorStore.createIndex({
  indexName: 'documents',
  dimension: 1536,
  metric: 'cosine'
});
```

### Chroma (Good for Development)

```typescript
import { ChromaVector } from '@mastra/chroma';

const vectorStore = new ChromaVector({
  path: 'http://localhost:8000' // Local Chroma server
});

await vectorStore.createIndex({
  indexName: 'dev-docs',
  dimension: 1536
});
```

### Upstash (Serverless)

```typescript
import { UpstashVector } from '@mastra/upstash';

const vectorStore = new UpstashVector({
  url: process.env.UPSTASH_VECTOR_URL,
  token: process.env.UPSTASH_VECTOR_TOKEN
});
```

### Common Vector Store Interface

All vector stores implement the same interface:

```typescript
interface MastraVector {
  createIndex(params: {
    indexName: string;
    dimension: number;
    metric?: string;
  }): Promise<void>;

  upsert(params: {
    indexName: string;
    vectors: number[][];
    metadata?: Record<string, any>[];
  }): Promise<string[]>;

  query(params: {
    indexName: string;
    queryVector: number[];
    topK: number;
    filter?: object;
    includeMetadata?: boolean;
  }): Promise<QueryResult[]>;

  deleteVectors(params: {
    indexName: string;
    ids?: string[];
    filter?: object;
  }): Promise<void>;

  deleteIndex(indexName: string): Promise<void>;
  listIndexes(): Promise<string[]>;
  describeIndex(indexName: string): Promise<IndexStats>;
}
```

IMPORTANT: Always store at least the source text in metadata. Without it,
you only have numerical embeddings with no way to return the original text
or filter results. Index dimensions cannot be changed post-creation.

================================================================================
RETRIEVAL PATTERNS
================================================================================

### Basic Semantic Search

```typescript
import { embed } from 'ai';
import { ModelRouterEmbeddingModel } from '@mastra/core/llm';
import { PgVector } from '@mastra/pg';

// Embed the user query
const { embedding: queryEmbedding } = await embed({
  model: new ModelRouterEmbeddingModel('openai/text-embedding-3-small'),
  value: 'How do I configure authentication?'
});

const pgVector = new PgVector({
  id: 'pg-vector',
  connectionString: process.env.POSTGRES_CONNECTION_STRING
});

// Search for similar chunks
const results = await pgVector.query({
  indexName: 'knowledge-base',
  queryVector: queryEmbedding,
  topK: 10,
  includeMetadata: true
});

// results: [{ id, score, metadata: { text, source, ... } }, ...]
```

### Metadata Filtering

Filter results by metadata fields before similarity ranking.
Uses MongoDB-style query syntax across all supported vector stores.

```typescript
const results = await vectorStore.query({
  indexName: 'knowledge-base',
  queryVector: queryEmbedding,
  topK: 5,
  filter: {
    // Exact match
    source: { $eq: 'api-docs' },
    // Numeric comparison
    version: { $gte: 2 },
    // In set
    category: { $in: ['auth', 'security'] },
    // Logical operators
    $and: [
      { source: { $eq: 'docs' } },
      { version: { $gte: 3 } }
    ]
  }
});
```

### Supported Filter Operators

| Operator | Description          | Example                        |
|----------|----------------------|--------------------------------|
| $eq      | Equals               | { field: { $eq: 'value' } }   |
| $ne      | Not equals           | { field: { $ne: 'value' } }   |
| $gt      | Greater than         | { field: { $gt: 10 } }        |
| $gte     | Greater or equal     | { field: { $gte: 10 } }       |
| $lt      | Less than            | { field: { $lt: 100 } }       |
| $lte     | Less or equal        | { field: { $lte: 100 } }      |
| $in      | In array             | { field: { $in: ['a','b'] } } |
| $nin     | Not in array         | { field: { $nin: ['x'] } }    |
| $and     | Logical AND          | { $and: [...conditions] }      |
| $or      | Logical OR           | { $or: [...conditions] }       |

### Reranking

Improve result relevance by reranking after initial retrieval.
The rerank() function combines semantic, vector, and position scoring.

IMPORTANT: Each result must include text in its metadata.text field for
semantic scoring to work during re-ranking.

```typescript
import { rerank } from '@mastra/rag';

// rerank() signature:
// rerank(results, query, model, options?)
const reranked = await rerank(
  results,                    // QueryResult[] from vector search
  'How do I configure auth?', // Query string
  model,                      // Vercel AI SDK language model (e.g. Cohere rerank-v3.5)
  {
    weights: {
      semantic: 0.4,          // Default: 0.4
      vector: 0.4,            // Default: 0.4
      position: 0.2           // Default: 0.2
    },
    topK: 3                   // Number of results to return (default: 3)
  }
);

// reranked: [{ result: QueryResult, score: number, details: ScoringDetails }]
```

### Reranking with Custom Scorer

```typescript
import { rerankWithScorer, MastraAgentRelevanceScorer } from '@mastra/rag';

// Create a relevance scorer
const scorer = new MastraAgentRelevanceScorer(
  'relevance-scorer',
  'openai/gpt-4o'
);

// rerankWithScorer() takes a named-params object:
const reranked = await rerankWithScorer({
  results: initialResults,        // QueryResult[]
  query: 'authentication config', // Query string
  scorer: scorer,                 // RelevanceScoreProvider instance
  options: {
    weights: {
      semantic: 0.5,
      vector: 0.3,
      position: 0.2
    },
    topK: 3
  }
});
```

### Supported Reranking Providers

- Cohere (rerank-v3.5) - native reranking support
- ZeroEntropy - relevance scoring
- MastraAgentRelevanceScorer - uses any LLM for scoring

================================================================================
AGENT INTEGRATION TOOLS
================================================================================

Mastra provides pre-built tools to integrate RAG into agents.

### Vector Query Tool

```typescript
import { createVectorQueryTool } from '@mastra/rag';
import { ModelRouterEmbeddingModel } from '@mastra/core/llm';

const queryTool = createVectorQueryTool({
  vectorStoreName: 'pgVector',       // Name registered in Mastra config
  indexName: 'knowledge-base',
  model: new ModelRouterEmbeddingModel('openai/text-embedding-3-small'),
  enableFilter: true,                // Optional: enable metadata filtering
  reranker: {                        // Optional: add reranking
    model: rerankerModel,            // Vercel AI SDK model
    options: {
      weights: { semantic: 0.5, vector: 0.3, position: 0.2 },
      topK: 5
    }
  }
});
```

#### createVectorQueryTool Parameters

| Parameter       | Type              | Required | Description                          |
|-----------------|-------------------|----------|--------------------------------------|
| vectorStoreName | string            | Yes      | Name of vector store in Mastra config|
| indexName       | string            | Yes      | Index within the vector store        |
| model           | EmbeddingModel    | Yes      | Embedding model instance             |
| enableFilter    | boolean           | No       | Enable metadata-based filtering      |
| reranker        | object            | No       | Reranking configuration              |
| databaseConfig  | object            | No       | Provider-specific query options      |
| vectorStore     | MastraVector      | No       | Direct instance or resolver function |
| id              | string            | No       | Custom tool ID                       |
| description     | string            | No       | Custom tool description              |

#### Return Structure

```typescript
{
  relevantContext: string,    // Concatenated text from top-matching chunks
  sources: QueryResult[]      // Array with id, metadata, score, document text
}
```

#### Database-Specific Config

```typescript
// PgVector specific options
const queryTool = createVectorQueryTool({
  vectorStoreName: 'pgVector',
  indexName: 'knowledge-base',
  model: new ModelRouterEmbeddingModel('openai/text-embedding-3-small'),
  databaseConfig: {
    minScore: 0.7,    // Similarity threshold
    ef: 200,          // HNSW accuracy control
    probes: 10        // IVFFlat probe optimization
  }
});

// Pinecone specific options
const queryTool = createVectorQueryTool({
  vectorStoreName: 'pinecone',
  indexName: 'my-index',
  model: new ModelRouterEmbeddingModel('openai/text-embedding-3-small'),
  databaseConfig: {
    namespace: 'production'
  }
});
```

### Document Chunker Tool

```typescript
import { createDocumentChunkerTool, MDocument } from '@mastra/rag';

const document = new MDocument({
  text: 'Your document content here...',
  metadata: { source: 'user-manual' }
});

const chunkerTool = createDocumentChunkerTool({
  doc: document,
  params: {
    strategy: 'recursive',
    size: 512,
    overlap: 50,
    separator: '\n'
  }
});

// Execute the tool
const { chunks } = await chunkerTool.execute();
// chunks: DocumentChunk[] with content and metadata
```

### GraphRAG Tool

```typescript
import { createGraphRAGTool } from '@mastra/rag';
import { ModelRouterEmbeddingModel } from '@mastra/core/llm';

const graphRagTool = createGraphRAGTool({
  vectorStoreName: 'pgVector',
  indexName: 'knowledge-graph',
  model: new ModelRouterEmbeddingModel('openai/text-embedding-3-small'),
  graphOptions: {
    dimension: 1536,
    threshold: 0.7,       // Similarity threshold for graph edges (0-1)
    randomWalkSteps: 100, // Steps in random walk traversal
    restartProb: 0.15     // Restart probability from query node
  }
});
```

#### createGraphRAGTool Parameters

| Parameter       | Type           | Required | Description                          |
|-----------------|----------------|----------|--------------------------------------|
| vectorStoreName | string         | Yes      | Name of vector store in Mastra config|
| indexName       | string         | Yes      | Index within the vector store        |
| model           | EmbeddingModel | Yes      | Embedding model instance             |
| graphOptions    | object         | No       | Graph traversal configuration        |
| enableFilter    | boolean        | No       | Enable metadata-based filtering      |
| includeSources  | boolean        | No       | Include full retrieval objects (true) |
| vectorStore     | MastraVector   | No       | Direct instance or resolver function |

### Using Tools with an Agent

```typescript
import { Agent } from '@mastra/core/agent';

const ragAgent = new Agent({
  id: 'rag-agent',
  name: 'Knowledge Assistant',
  instructions: `You are a helpful assistant that answers questions using
    the knowledge base. Always use the queryTool to search for relevant
    information before answering. Cite your sources.`,
  model: 'openai/gpt-4o',   // String format: provider/model
  tools: {
    queryKnowledge: queryTool,
    graphSearch: graphRagTool
  }
});

// Use the agent
const response = await ragAgent.generate(
  'How do I set up JWT authentication in Express?'
);
```

================================================================================
GRAPH RAG
================================================================================

GraphRAG enhances standard RAG with knowledge graph relationships between
chunks, enabling multi-hop reasoning and discovery of indirect connections.

### When to Use GraphRAG

- Questions requiring reasoning across multiple documents
- Complex queries that need multi-hop connections
- When information is spread across multiple documents
- Documents that reference each other
- When standard vector similarity misses relevant context

### How GraphRAG Works

1. Chunks are embedded and stored as usual
2. A knowledge graph is built where:
   - Nodes = document chunks
   - Edges = similarity relationships above a threshold
3. At query time, traversal finds both directly similar AND graph-connected chunks

### Threshold Guidance

- High (0.8-0.9): Precise but potentially incomplete (sparse graph)
- Medium (0.6-0.8): Balanced, recommended starting point
- Low (0.4-0.6): Broader context with noise risk (dense graph)

### GraphRAG Setup

```typescript
import { createGraphRAGTool } from '@mastra/rag';
import { ModelRouterEmbeddingModel } from '@mastra/core/llm';

const graphTool = createGraphRAGTool({
  vectorStoreName: 'pgVector',
  indexName: 'knowledge-graph',
  model: new ModelRouterEmbeddingModel('openai/text-embedding-3-small'),
  graphOptions: {
    dimension: 1536,
    threshold: 0.7,
    randomWalkSteps: 100,
    restartProb: 0.15
  }
});

const ragAgent = new Agent({
  id: 'graph-rag-agent',
  name: 'GraphRAG Agent',
  model: 'openai/gpt-4o',
  tools: { graphQueryTool: graphTool }
});
```

================================================================================
COMPLETE RAG PIPELINE EXAMPLE
================================================================================

End-to-end example: ingest documents, create embeddings, store, and query.

```typescript
import { MDocument } from '@mastra/rag';
import { createVectorQueryTool } from '@mastra/rag';
import { embed, embedMany } from 'ai';
import { ModelRouterEmbeddingModel } from '@mastra/core/llm';
import { PgVector } from '@mastra/pg';
import { Agent } from '@mastra/core/agent';

const embeddingModel = new ModelRouterEmbeddingModel('openai/text-embedding-3-small');

// --- Step 1: Set up vector store ---
const vectorStore = new PgVector({
  id: 'pg-vector',
  connectionString: process.env.POSTGRES_CONNECTION_STRING
});

await vectorStore.createIndex({
  indexName: 'product-docs',
  dimension: 1536,
  metric: 'cosine'
});

// --- Step 2: Ingest and chunk documents ---
const documents = [
  MDocument.fromMarkdown(apiDocsContent),
  MDocument.fromMarkdown(userGuideContent),
  MDocument.fromText(faqContent)
];

const allChunks = [];
for (const doc of documents) {
  const chunks = await doc.chunk({
    strategy: 'recursive',
    maxSize: 512,
    overlap: 50
  });
  allChunks.push(...chunks);
}

// --- Step 3: Generate embeddings ---
const { embeddings } = await embedMany({
  model: embeddingModel,
  values: allChunks.map(c => c.text),
  maxRetries: 2
});

// --- Step 4: Store in vector database ---
await vectorStore.upsert({
  indexName: 'product-docs',
  vectors: embeddings,
  metadata: allChunks.map((chunk, i) => ({
    text: chunk.text,
    source: chunk.metadata?.source || 'unknown',
    chunkIndex: i
  }))
});

// --- Step 5: Create query tool for agent ---
const queryTool = createVectorQueryTool({
  vectorStoreName: 'pgVector',
  indexName: 'product-docs',
  model: embeddingModel
});

// --- Step 6: Create RAG agent ---
const agent = new Agent({
  id: 'product-support-agent',
  name: 'Product Support Agent',
  instructions: `You answer product questions using the knowledge base.
    Always search the knowledge base before answering.
    If the knowledge base doesn't contain relevant information, say so.
    Cite which document source your answer comes from.`,
  model: 'openai/gpt-4o',
  tools: { queryKnowledge: queryTool }
});

// --- Step 7: Query ---
const response = await agent.generate(
  'How do I configure two-factor authentication?'
);
console.log(response.text);
```

================================================================================
REGISTERING VECTOR STORES WITH MASTRA
================================================================================

To use vector store tools with agents, register them in the Mastra config:

```typescript
import { Mastra } from '@mastra/core';
import { PgVector } from '@mastra/pg';

const mastra = new Mastra({
  vectors: {
    pgVector: new PgVector({
      id: 'pg-vector',
      connectionString: process.env.POSTGRES_CONNECTION_STRING
    })
  },
  agents: {
    ragAgent: ragAgent
  }
});
```

The key name ('pgVector') is what you reference in tool configurations
via `vectorStoreName`.

================================================================================
BEST PRACTICES
================================================================================

### Chunk Size Recommendations
- General text: 512 maxSize with 50 overlap
- Technical docs: 256-512 maxSize (more precise retrieval)
- Long-form content: 1024 maxSize (more context per result)
- Code: Use smaller chunks (256) to isolate functions/classes

### Embedding Model Selection
- Default: openai/text-embedding-3-small (1536 dims, good cost/quality)
- Higher quality: openai/text-embedding-3-large (3072 dims)
- Google: gemini-embedding-001 (768 dims, supports custom dimensions)
- IMPORTANT: Index dimension must match embedding model dimensions
- Dimensions cannot be changed post-creation

### Index Optimization
- Use cosine similarity for normalized embeddings (most common)
- Use dotProduct for performance when vectors are normalized
- Use euclidean for absolute distance comparisons
- Create separate indexes for different document types/domains

### Metadata Best Practices
- ALWAYS store source text in metadata (without it you only have vectors)
- Maintain consistent field naming to prevent query issues
- Store timestamps to track content freshness
- Include only filterable fields to minimize storage overhead

### Hybrid Search Patterns
- Combine vector similarity with metadata filters for precision
- Use reranking to improve top-K quality after initial retrieval
- Consider GraphRAG for multi-hop reasoning requirements

### Performance
- Batch embedding calls using embedMany() instead of single embed()
- Use appropriate topK values (5-10 for most use cases)
- Index frequently-queried metadata fields
- Monitor vector store size and consider partitioning for large datasets

### Data Pipeline
- Re-chunk and re-embed when document content changes significantly
- Version your indexes (e.g., 'docs-v1', 'docs-v2') for safe migrations
- Store original text in metadata for display (don't re-retrieve from source)
- Track document source and version in chunk metadata for traceability

================================================================================
DOCUMENTATION LINKS
================================================================================

- RAG Overview: https://mastra.ai/docs/rag/overview
- Retrieval: https://mastra.ai/docs/rag/retrieval
- Chunking & Embedding: https://mastra.ai/docs/rag/chunking-and-embedding
- Vector Databases: https://mastra.ai/docs/rag/vector-databases
- GraphRAG: https://mastra.ai/docs/rag/graph-rag
- API Reference - MDocument: https://mastra.ai/reference/rag/document
- API Reference - .chunk(): https://mastra.ai/reference/rag/chunk
- API Reference - Embeddings: https://mastra.ai/reference/rag/embeddings
- API Reference - rerank: https://mastra.ai/reference/rag/rerank
- API Reference - rerankWithScorer: https://mastra.ai/reference/rag/rerankWithScorer
- API Reference - Metadata Filters: https://mastra.ai/reference/rag/metadata-filters
- API Reference - createVectorQueryTool: https://mastra.ai/reference/tools/vector-query-tool
- API Reference - createDocumentChunkerTool: https://mastra.ai/reference/tools/document-chunker-tool
- API Reference - createGraphRAGTool: https://mastra.ai/reference/tools/graph-rag-tool
- Examples: https://mastra.ai/en/examples/rag

================================================================================
SKILL_EOF
