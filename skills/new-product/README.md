# /new-product

> Deep research and architecture design for new product development.

## What it does

Given documentation or a product description, runs a 6-stage deep-research workflow that cross-references technologies and designs the optimal architecture for a new application. Stage 1 produces a big-idea document; stages 2-5 fan out to 4 parallel research agents (runtime execution, abstraction layer, integration layer, output rendering); stage 6 synthesizes an architecture summary and loops on user approval. All document and agent-prompt structures come from `references/templates/` (added in the 2026-07 refactor) — the SKILL.md is the orchestrator, the templates are the spec.

## When it triggers

- "I have a product idea — research the best stack and architecture for it"
- `/new-product "Build a real-time collaborative document editor"`
- `/new-product docs/product-requirements.md` (evaluate tech options from requirements docs)
- "Redesign this monolithic e-commerce platform to microservices"
- "Research how real-time collaboration tools are typically built"

## Usage

```bash
/new-product path/to/docs.md          # from documentation
/new-product "product description"    # from a description
```

Clarifying questions are asked iteratively (via AskUserQuestion), not all upfront: stage 1 covers vision/scale/deployment; each research agent asks its own domain questions. Expect ~20-40 minutes total (stages 2-5 run in parallel, ~15-25 min). At the end you approve, or request a revision of any one of the four architecture documents — that agent re-runs with your feedback.

## Output structure

```
/job-queue/product-{name}/
├── big-idea.md                  # Vision + technology landscape (stage 1)
├── runtime-execution.md         # How the system executes work (stage 2)
├── abstraction-layer.md         # User intent → executable logic (stage 3)
├── integration-layer.md         # External connections, auth, data flow (stage 4)
├── output-rendering.md          # Delivery, rendering strategy, caching (stage 5)
├── ARCHITECTURE-SUMMARY.md      # Stack, decisions, trade-offs, risks (stage 6)
└── research-notes/              # Raw WebSearch/WebFetch notes per stage
```

If a stage fails, completed documents and partial research notes are preserved; re-run `/new-product [input]` and skip completed stages.

## Context cost

Description always in context (~65 chars); SKILL.md body loads on trigger (~6k chars); `references/templates/*.md` (~28k total across 7 files) load per stage — each research agent reads only its own stage template plus the shared closing-sections template.

## Files

| Path | Purpose |
|---|---|
| `SKILL.md` | 6-stage orchestrator: workspace init → big idea → 4 parallel agents → review |
| `references/templates/stage1-big-idea.md` | Stage 1 question text + big-idea.md document structure |
| `references/templates/stage2-runtime-execution.md` | Agent prompt template: execution engine, lifecycle, state, concurrency |
| `references/templates/stage3-abstraction-layer.md` | Agent prompt template: input formats, IR/AST, interpretation vs compilation, plugins |
| `references/templates/stage4-integration-layer.md` | Agent prompt template: connectors, auth, service discovery, data flow, retries |
| `references/templates/stage5-output-rendering.md` | Agent prompt template: formats, SSR/CSR/SSG, streaming, caching |
| `references/templates/stage6-summary-and-review.md` | ARCHITECTURE-SUMMARY structure, completion banner, approval question, failure display |
| `references/templates/common-closing-sections.md` | Deduplicated tail (tech comparison / implementation considerations / sources) shared by all four architecture docs |

## Related skills

- **spec-plan** — specs a *feature* within an existing product; new-product designs the architecture for a *whole new application* before any repo exists.
- **research-gated-build-plan** — inventories what already exists and gates execution phases; use it when the question is "what do we have / what's the gap", not "what should we build this on".
- **feature-new** — end-to-end build workflow; a natural next step after the architecture here is approved.
- Standalone by design: no pm-db tracking, no memory-bank updates, no code or scaffolding — research and planning documentation only.
