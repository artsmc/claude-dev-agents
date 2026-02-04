# New Product Research Skill

Deep architecture research and design for new product development.

## Overview

Given documentation or a product description, this skill performs comprehensive research and cross-references technologies to design the optimal application architecture. It produces 5 detailed architectural documents covering all aspects of system design.

## Usage

```bash
# With documentation path
/new-product path/to/docs.md

# With product description
/new-product "Build a real-time collaborative document editor"

# With multiple doc paths (space-separated)
/new-product "docs/requirements.md docs/vision.md"
```

## What It Does

### Stage 0: Workspace Setup
- Creates `/job-queue/product-{name}/` directory structure
- Parses input (docs or description)
- Extracts product name

### Stage 1: Big Idea Generation
- Analyzes input and clarifies product vision
- Performs high-level technology research
- Asks initial clarifying questions (vision, scale, deployment)
- Generates `big-idea.md` with:
  - Product overview
  - High-level architecture approach
  - Technology landscape (frontend, backend, database, deployment options)
  - Key challenges identified

### Stages 2-5: Parallel Deep Research
Launches **4 parallel research agents** to generate:

1. **`runtime-execution.md`** - How the system executes work
   - Core execution engine selection
   - Process lifecycle (init → run → teardown)
   - State management strategies
   - Concurrency/threading models
   - Hot-reload and optimization

2. **`abstraction-layer.md`** - How user intent translates to executable logic
   - Input formats (code, config, visual, NLP)
   - Intermediate representations (IR/AST)
   - Translation mechanisms (interpretation vs compilation)
   - Extension points (plugins, hooks, middleware)

3. **`integration-layer.md`** - How the system connects to external resources
   - Connector architecture and protocols
   - Authentication and credential management
   - Service discovery mechanisms
   - Data flow patterns (push, pull, streaming)
   - Error handling and retry logic

4. **`output-rendering.md`** - How results are delivered to consumers
   - Output formats and serialization
   - Rendering strategies (SSR, CSR, SSG, hybrid)
   - Streaming and real-time updates
   - Component/template systems
   - Caching and performance optimization

### Stage 6: Final Review
- Generates `ARCHITECTURE-SUMMARY.md` with:
  - Recommended technology stack
  - Key design decisions
  - Trade-offs and risks
  - Next steps
- Presents all documents for user approval
- Allows revision of specific architectural areas

## Output Structure

```
/job-queue/product-{name}/
├── big-idea.md                  # High-level vision
├── runtime-execution.md         # Execution architecture
├── abstraction-layer.md         # Abstraction design
├── integration-layer.md         # Integration patterns
├── output-rendering.md          # Rendering strategy
├── ARCHITECTURE-SUMMARY.md      # Executive summary
└── research-notes/              # Raw research data
    ├── stage1-research.md
    ├── runtime-research.md
    ├── abstraction-research.md
    ├── integration-research.md
    └── output-research.md
```

## Key Features

### Deep Research
- Extensive WebSearch queries for each architectural dimension
- WebFetch to read official documentation
- Cross-references multiple technologies
- Compares trade-offs and provides recommendations

### Parallel Execution
- 4 research agents run simultaneously
- Significantly faster than sequential research
- Each agent focuses on one architectural domain

### Iterative Questions
- Asks clarifying questions during each stage
- Context-aware questions based on previous answers
- Not all questions upfront - natural conversation flow

### Comprehensive Documentation
- Industry-standard architectural documentation
- Code examples and configuration samples
- Technology comparison tables
- Implementation considerations
- Research sources cited

## Interaction Model

The skill asks questions iteratively throughout the process:

**Stage 1 Questions:**
- Product vision and goals
- Scale and audience expectations
- Deployment context

**Stage 2 Questions (Runtime):**
- Execution model preference
- Concurrency needs
- State management approach

**Stage 3 Questions (Abstraction):**
- Input format preference
- Translation approach
- Extensibility requirements

**Stage 4 Questions (Integration):**
- External systems to integrate
- Authentication strategy
- Service discovery mechanism

**Stage 5 Questions (Rendering):**
- Rendering strategy preference
- Real-time requirements
- Output format needs

## Expected Duration

- **Stage 0**: ~10 seconds (setup)
- **Stage 1**: ~5-10 minutes (big idea + initial research)
- **Stages 2-5**: ~15-25 minutes (parallel deep research)
- **Stage 6**: ~2-3 minutes (summary + review)

**Total**: ~20-40 minutes

## Use Cases

### 1. New Product Ideation
You have a product idea and want to research the best tech stack and architecture.

```bash
/new-product "Build a platform for AI-powered video editing"
```

### 2. Architecture Redesign
You want to redesign an existing product's architecture.

```bash
/new-product "Redesign monolithic e-commerce platform to microservices"
```

### 3. Technology Evaluation
You have requirements docs and need to evaluate technology options.

```bash
/new-product docs/product-requirements.md
```

### 4. Competitive Analysis
You want to research how similar products are built.

```bash
/new-product "Research architecture patterns for real-time collaboration tools"
```

## What You Get

By the end, you'll have:

1. **Clear technology recommendations** - Frontend, backend, database, deployment
2. **Architectural blueprints** - Detailed designs for 4 key dimensions
3. **Trade-off analysis** - Understanding what you're gaining/losing
4. **Implementation roadmap** - Next steps to begin development
5. **Research citations** - URLs to official docs and best practices

## Next Steps After Completion

1. **Review** the generated architecture documents
2. **Approve or revise** specific architectural areas
3. **Set up development environment** based on chosen tech stack
4. **Create project structure** following architectural patterns
5. **Begin implementation** with confidence in your architecture

## Integration with Other Skills

This skill is standalone and doesn't integrate with:
- PM-DB (no project tracking)
- Memory Bank (no automatic updates)
- Feature workflows (different purpose)

It's designed for **research and planning phase** before you start building.

## Notes

- **Documentation-first**: Always uses latest 2026 documentation
- **No assumptions**: Asks questions instead of guessing preferences
- **Deep analysis**: Not surface-level, actually reads documentation
- **Practical focus**: Emphasizes implementation considerations
- **Research transparency**: Cites all sources consulted

## Limitations

- Requires internet access for WebSearch and WebFetch
- Research quality depends on available online documentation
- Does not write actual code (only architectural documentation)
- Does not create project scaffolding (only documentation)
- Does not integrate with pm-db or memory-bank systems

## Error Recovery

If a stage fails, partial work is saved:

```
/job-queue/product-{name}/
├── big-idea.md              # ✅ Saved if Stage 1 completed
├── runtime-execution.md     # ✅ Saved if Stage 2 completed
├── abstraction-layer.md     # ❌ Not saved if Stage 3 failed
└── research-notes/          # ✅ Partial research always saved
```

To resume: simply run `/new-product [input]` again and skip already-completed stages.

---

**Created**: 2026-02-04
**Version**: 1.0.0
**Author**: Product Research Skill
