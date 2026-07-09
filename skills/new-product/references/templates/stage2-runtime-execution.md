# Stage 2 Agent Prompt: Runtime Execution Research

Orchestrator: the prompt below is passed verbatim to a `Task` agent (`subagent_type="general-purpose"`). Substitute [Product Name], paste the full big-idea.md content into CONTEXT, and replace the [COMMON CLOSING SECTIONS] marker with the block from `common-closing-sections.md` (Stage 2 variants).

---

You are researching runtime execution architecture for: [Product Name]

CONTEXT:
[Include big-idea.md content]

YOUR GOAL:
Create a comprehensive `runtime-execution.md` document that explains how the system executes work.

RESEARCH APPROACH:
1. Based on the technology options in big-idea.md, research each option's runtime model
2. Use WebSearch to find:
   - "[technology] runtime architecture 2026"
   - "[technology] execution model 2026"
   - "[technology] process lifecycle 2026"
   - "[technology] concurrency model 2026"

3. Use WebFetch to read official documentation for top candidates

4. Ask user clarifying questions about runtime preferences using AskUserQuestion

QUESTIONS TO ASK USER:

1. **Execution Model**
   - Header: "Execution"
   - Question: "How should the system execute work?"
   - Options:
     - "Request-response" - "Traditional HTTP request/response"
     - "Event-driven" - "Async processing with queues"
     - "Stream processing" - "Continuous data flow"
     - "Batch processing" - "Scheduled periodic jobs"

2. **Concurrency Needs**
   - Header: "Concurrency"
   - Question: "What concurrency model do you need?"
   - Options:
     - "Single-threaded async" - "Node.js style, high I/O"
     - "Multi-threaded" - "Python/Java threads, CPU work"
     - "Actor model" - "Erlang/Akka style isolation"
     - "Function-based" - "Serverless auto-scaling"

3. **State Management**
   - Header: "State"
   - Question: "How should runtime state be managed?"
   - Options:
     - "Stateless" - "No server-side state, scale easily"
     - "In-memory cache" - "Redis/Memcached for sessions"
     - "Persistent state" - "Database-backed state"
     - "Distributed state" - "Multi-node coordination"

DOCUMENT STRUCTURE:

Create: /job-queue/product-{name}/runtime-execution.md

# Runtime Execution Architecture

## Executive Summary
[2-3 paragraphs: What runtime model was chosen and why]

## Core Execution Engine

### Selected Technology
- **Primary Runtime**: [chosen technology]
- **Rationale**: [why this choice]
- **Trade-offs**: [what we're giving up]

### Execution Paradigm
[Describe: request-response, event-driven, streaming, batch]

## Process Lifecycle

### Initialization
[How the system starts up, bootstraps, loads config]

### Request Handling
[How incoming work is received and routed]

### Execution Flow
[Step-by-step: what happens when work arrives]

### Teardown/Cleanup
[How resources are released, graceful shutdown]

## State Management

### State Architecture
[Where state lives: memory, cache, database]

### State Lifecycle
[How state is created, updated, invalidated]

### State Consistency
[How consistency is maintained across requests]

## Concurrency Model

### Concurrency Approach
[Threads, async, actors, serverless]

### Parallelism Strategy
[How work is distributed across cores/nodes]

### Synchronization
[Locks, queues, coordination mechanisms]

## Hot-Reload & Dynamic Updates

### Development Experience
[Hot reload during dev? How does it work?]

### Production Updates
[Zero-downtime deploys? Blue-green? Rolling?]

## Resource Constraints & Optimization

### Memory Management
[How memory is allocated, GC considerations]

### CPU Utilization
[How CPU is used, optimization strategies]

### I/O Patterns
[Network, disk, database access patterns]

### Scaling Strategy
[Vertical vs horizontal, auto-scaling triggers]

[COMMON CLOSING SECTIONS — orchestrator: insert the block from references/templates/common-closing-sections.md here, using the Stage 2 (runtime) variants: Technology Comparison, Implementation Considerations, Research Sources]

---

After completing research and asking user questions, write this document to:
/job-queue/product-{name}/runtime-execution.md

Also save your raw research notes to:
/job-queue/product-{name}/research-notes/runtime-research.md
