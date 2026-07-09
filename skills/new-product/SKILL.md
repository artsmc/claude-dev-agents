---
name: new-product
description: Deep research and architecture design for new product development
args:
  input:
    type: string
    description: Path to documentation files or product description
    required: true
---

# New Product - Deep Research & Architecture Design

Given documentation or a product description, perform deep research and cross-reference technologies to determine the optimal architecture for building a new application.

## Your Task

You are orchestrating a 6-stage deep research workflow to design product architecture. Run the stages in order, use 4 parallel agents for the deep-research stages, and present a final comprehensive review at the end.

All document and agent-prompt templates live in this skill's `references/templates/` — read the listed template at each stage; do not improvise document structures.

---

## Stage 0: Initialize Product Workspace

- Parse the input argument: if it is a file path (contains `/` or ends in `.md`, `.txt`, etc.), read the documentation; otherwise treat it as a product description.
- Extract a short kebab-case product name (from the doc's project/product title, or derived from the description, e.g. "real-time chat app" → `realtime-chat`). Store it for later stages.
- `mkdir -p /job-queue/product-{name}/research-notes`
- Display: "🚀 Stage 0/6: Workspace created at /job-queue/product-{name}/"

---

## Stage 1: Big Idea & High-Level Research

1. **Analyze input.** From documentation: extract features, user flows, requirements, technical hints/constraints. From a description: core functionality, target users, key features, scale expectations.
2. **Ask 3 initial clarifying questions** via `AskUserQuestion` — Product Vision, Scale & Audience, Deployment Context. Exact question/option text: `references/templates/stage1-big-idea.md`.
3. **High-level technology research** via `WebSearch`: "[product type] architecture patterns 2026", "[product type] technology stack comparison 2026", "[product type] best practices 2026", "[scale level] architecture considerations 2026". `WebFetch` the top 2-3 articles per search; extract common patterns, recommended technologies, pitfalls. Save notes to `/job-queue/product-{name}/research-notes/stage1-research.md`.
4. **Write `/job-queue/product-{name}/big-idea.md`** using the content structure in `references/templates/stage1-big-idea.md` (overview, value proposition, architecture approach, frontend/backend/database/deployment options with pros/cons, key challenges, next steps, research sources).
5. Display: "✅ Stage 1/6: Big idea generated at product-{name}/big-idea.md"

---

## Stages 2-5: Parallel Deep Research for Architectural Documents

Launch **all 4 research agents at once** via the `Task` tool with `subagent_type="general-purpose"`. Each agent researches one architectural document independently.

| Stage | Task description | Output document | Prompt template |
|---|---|---|---|
| 2 | "Runtime execution research" — how the system executes work | `runtime-execution.md` | `references/templates/stage2-runtime-execution.md` |
| 3 | "Abstraction layer research" — how user intent becomes executable logic | `abstraction-layer.md` | `references/templates/stage3-abstraction-layer.md` |
| 4 | "Integration layer research" — how the system connects to external resources | `integration-layer.md` | `references/templates/stage4-integration-layer.md` |
| 5 | "Output rendering research" — how results are delivered to consumers | `output-rendering.md` | `references/templates/stage5-output-rendering.md` |

**Build each agent prompt from its template:**

1. Read the stage's template plus `references/templates/common-closing-sections.md` — the single deduplicated tail (Technology Comparison / Implementation Considerations / Research Sources) shared by all four documents; insert it at the template's `[COMMON CLOSING SECTIONS]` marker with that stage's variants.
2. Substitute `[Product Name]` and `{name}`, and paste the full big-idea.md content into the CONTEXT block (every agent needs it for cross-referencing).

Each template already instructs the agent to WebSearch/WebFetch, ask its own `AskUserQuestion` clarifications, and write both its document and raw notes under `/job-queue/product-{name}/`.

**Wait for all 4 agents to complete**, then display "✅ Stage N/6: [topic] research complete" for stages 2-5.

---

## Stage 6: Final Review & Presentation

1. Read all 5 generated documents (big-idea.md + the 4 architecture docs).
2. Write `/job-queue/product-{name}/ARCHITECTURE-SUMMARY.md` (stack, style, key decisions, trade-offs, risks, next steps) and print the completion banner — both templates in `references/templates/stage6-summary-and-review.md`.
3. Ask for feedback via `AskUserQuestion` (exact text in the same template): Approve, or Revise runtime execution / abstraction layer / integration layer / output rendering.
   - **Approve** → display "✅ Architecture approved! Ready for implementation."
   - **Revise** → re-run that stage's research agent with the feedback, regenerate the document, re-present for approval.

---

## Error Handling

On any stage failure: display which stage failed, list completed vs failed stages, show the error, note partial work saved at `/job-queue/product-{name}/`, and give recovery instructions (resume with `/new-product [input]` or continue manually). Example failure display: `references/templates/stage6-summary-and-review.md`.

---

## Notes

- **Tools**: WebSearch + WebFetch (deep research — use extensively), Task (parallel agents), AskUserQuestion (iterative clarification), Read/Write (documents).
- Ask clarifying questions during each stage, not all upfront; each agent reads big-idea.md for context. Documents must be comprehensive, well-structured, actionable.
- Duration ~20-40 min: Stage 0 seconds; Stage 1 ~5-10 min; Stages 2-5 ~15-25 min (parallel); Stage 6 ~2-3 min.
- Done = 6 documents in `/job-queue/product-{name}/` (big-idea, 4 architecture docs, ARCHITECTURE-SUMMARY), trade-offs and risks identified, user approval obtained.
