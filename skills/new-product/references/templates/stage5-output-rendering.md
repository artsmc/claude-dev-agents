# Stage 5 Agent Prompt: Output Rendering Research

Orchestrator: the prompt below is passed verbatim to a `Task` agent (`subagent_type="general-purpose"`). Substitute [Product Name], paste the full big-idea.md content into CONTEXT, and replace the [COMMON CLOSING SECTIONS] marker with the block from `common-closing-sections.md` (Stage 5 variants).

---

You are researching output rendering architecture for: [Product Name]

CONTEXT:
[Include big-idea.md content]

YOUR GOAL:
Create a comprehensive `output-rendering.md` document that explains how results are delivered to consumers.

RESEARCH APPROACH:
1. Research rendering strategies for the chosen tech stack
2. Use WebSearch for:
   - "[technology] rendering strategies 2026"
   - "SSR vs CSR vs SSG comparison 2026"
   - "[technology] streaming rendering 2026"
   - "[technology] caching strategies 2026"

3. Use WebFetch for framework-specific rendering docs

4. Ask user clarifying questions

QUESTIONS TO ASK USER:

1. **Rendering Strategy**
   - Header: "Rendering"
   - Question: "How should content be rendered?"
   - Options:
     - "Server-side (SSR)" - "Render on server, send HTML"
     - "Client-side (CSR)" - "Render in browser with JS"
     - "Static generation (SSG)" - "Pre-render at build time"
     - "Hybrid" - "Mix of SSR/CSR/SSG per route"

2. **Real-time Requirements**
   - Header: "Real-time"
   - Question: "Do outputs need real-time updates?"
   - Options:
     - "No real-time needed" - "Traditional request-response"
     - "Polling" - "Client polls for updates"
     - "WebSockets" - "Bidirectional real-time"
     - "Server-sent events (SSE)" - "Unidirectional streaming"

3. **Output Formats**
   - Header: "Formats"
   - Question: "What output formats do you need?"
   - MultiSelect: true
   - Options:
     - "HTML" - "Web pages"
     - "JSON/XML" - "API responses"
     - "Binary (images, PDFs)" - "Generated files"
     - "Streams" - "Continuous data streams"

DOCUMENT STRUCTURE:

Create: /job-queue/product-{name}/output-rendering.md

# Output Rendering Architecture

## Executive Summary
[How results are delivered to consumers]

## Output Formats

### Supported Formats
- HTML (web UI)
- JSON (API responses)
- Binary (files, images)
- Streams (continuous data)

### Serialization Strategy
[How data is serialized for each format]

### Content Negotiation
[How clients request specific formats]

## Rendering Pipeline

### Chosen Rendering Strategy
[SSR, CSR, SSG, hybrid]

### Rendering Flow
[Step-by-step: data → rendered output]

### Server-Side Rendering (if applicable)
- Template engine: [e.g., React Server Components, Jinja2]
- Hydration strategy
- Performance characteristics

### Client-Side Rendering (if applicable)
- JavaScript framework: [React, Vue, Svelte]
- Bundle strategy
- Initial load performance

### Static Generation (if applicable)
- Build-time generation
- Incremental static regeneration (ISR)
- When to use vs SSR

## Streaming & Real-Time Updates

### Real-Time Strategy
[None, polling, WebSockets, SSE]

### Streaming Architecture
[How data streams to client]

### Example: Real-Time Flow
```
1. Client subscribes to updates
2. Server pushes incremental changes
3. Client updates UI reactively
```

## Template/Component System

### Component Architecture
[How UI is composed: components, templates, views]

### Component Library
[Design system, reusable components]

### Composition Patterns
[How components are nested and composed]

### Example Component Structure
```
<Layout>
  <Header />
  <Main>
    <DataGrid data={...} />
  </Main>
  <Footer />
</Layout>
```

## Caching & Persistence

### Caching Layers
1. **CDN caching**: [CloudFlare, CloudFront]
2. **Server caching**: [Redis, in-memory]
3. **Client caching**: [Service worker, browser cache]

### Cache Invalidation
[How caches are invalidated when data changes]

### Persistence Strategy
[How outputs are stored: database, file system, object storage]

## Performance Optimization

### Bundle Optimization
- Code splitting
- Tree shaking
- Lazy loading

### Image Optimization
- Responsive images
- Format selection (WebP, AVIF)
- CDN delivery

### Data Fetching
- Parallel fetching
- Request deduplication
- Prefetching strategies

[COMMON CLOSING SECTIONS — orchestrator: insert the block from references/templates/common-closing-sections.md here, using the Stage 5 (rendering) variants: Technology Comparison, Implementation Considerations, Research Sources]

---

Write to: /job-queue/product-{name}/output-rendering.md
Research notes: /job-queue/product-{name}/research-notes/output-research.md
