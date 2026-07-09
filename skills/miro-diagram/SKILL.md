---
name: miro-diagram
description: >
  Create diagrams on Miro boards using the Miro MCP tools — flowcharts, UML class/sequence
  diagrams, and ERDs. Use whenever the user wants to diagram or visualize anything on a
  Miro board: architecture, system flows, database schemas, process maps, interaction
  sequences — or just says "diagram this" with the Miro MCP connected. For multi-element
  layouts (diagrams + text + tables + metrics), use miro-infographic instead.
compatibility:
  tools:
    - mcp__miro__diagram_get_dsl
    - mcp__miro__diagram_create
    - mcp__miro__context_explore
    - mcp__miro__context_get
    - mcp__miro__doc_create
---

# Miro Diagram Creator

Create diagrams on Miro boards that communicate clearly. Miro auto-layouts everything — your job is to give it clean, structured input so it produces a readable result.

## The Two-Step Process

Every diagram requires exactly two Miro MCP calls:

1. **`diagram_get_dsl`** — Fetch the DSL syntax rules for your diagram type. Read the response carefully — it contains the exact grammar, palette rules, and examples. Never guess DSL syntax.

2. **`diagram_create`** — Submit your DSL to create the diagram on the board.

## Miro's Layout Engine — What You Need to Know

Miro auto-layouts your diagram. You cannot control pixel positions of nodes. This means:

- **Fewer nodes = better layout.** The layout engine works well with 8-12 nodes. Past 15, things get messy — giant whitespace gaps, overlapping connections, nodes hidden inside bloated clusters.
- **Fewer cross-cluster connections = cleaner result.** Every connection between different clusters forces the layout to stretch.
- **Clusters should be small.** 2-5 nodes per cluster is ideal. A cluster with 7+ nodes becomes a giant empty box.
- **Direction matters.** `LR` (left-to-right) works best for architecture and data flow. `TB` (top-to-bottom) works best for process/decision flows.

## Emoji Icons in Labels

Miro renders emoji in node labels, entity titles, actor names, and cluster titles. Use them — they dramatically improve visual scannability. Add port numbers to service labels when relevant (e.g., `:3500`, `:4000`). The per-domain emoji table (👤 user, 🌐 web, 🔐 auth, 🐘 database, ⚡ cache, …) is in `references/diagram-patterns.md` — read it when picking labels.

## Flowchart Diagrams

### The Golden Rules

1. **8-12 nodes maximum.** One node per major component or decision point. Internal details (middleware, ORM layers) belong in labels or companion docs, not separate nodes.

2. **2-3 palette colors.** Each color = a meaning. Use only Miro's approved hex colors and recommended palettes — listed in `references/color-palette.md`; read it before choosing a `palette` line.

3. **2-3 clusters with 2-5 nodes each.** Clusters organize the story — "Application Layer" vs "Data Layer" — but too many clusters with cross-connections create spaghetti.

4. **Use node types semantically:**
   - `flowchart-process` — Services, components, actions (rectangle)
   - `flowchart-decision` — Branch points, conditions (diamond)
   - `flowchart-terminator` — Start/end points (rounded)
   - `flowchart-data` — Databases, files, storage (parallelogram)

5. **Connection labels: 1-3 words.** Use `-` for self-evident connections. Label decisions (`YES`/`NO`) and cross-service connections (`REST`, `Queue`, `Triggers`).

A full worked example (8-node architecture flowchart DSL) is in `references/diagram-patterns.md` under "Worked Examples" — read it before writing your first flowchart DSL.

## UML Sequence Diagrams

Good for showing multi-service interactions over time — auth flows, API call chains, workflow executions.

### Key Patterns

- **Actors** get a color each. Use the same semantic colors as flowcharts.
- **Message types:**
  - `sync_call` — Request that blocks until response (solid arrow)
  - `sync_return` — Response to a sync call (dashed arrow back)
  - `async_call` — Fire-and-forget or user action (solid arrow, no wait)
  - `async_return` — Async response/callback (dashed arrow)
- **Self-calls** (same source and target) show internal processing — useful for validation, parsing, etc.
- **Keep actors to 5-7.** More than 7 actors makes the diagram too wide.
- **Group related messages.** The eye reads top-to-bottom, so put the happy path first, error handling after.

A worked auth-flow sequence example is in `references/diagram-patterns.md` under "Worked Examples".

## Entity-Relationship Diagrams

Good for database schemas and data models.

### Key Patterns

- **Attributes use TAB characters** (not spaces) to separate key, field, and type.
- **Key types:** `PK` (primary), `FK` (foreign), `UQ` (unique), `NULL`, `NOT_NULL`
- **Cardinalities:** `one`, `many`, `one_or_many`, `only_one`, `zero_or_many`, `zero_or_one`
- **Connector types:** `--` (identifying — parent PK is part of child PK), `..` (non-identifying — normal FK)
- **Color entities by domain** — e.g., blue for core entities, purple for AI-specific, teal for audit/logging.
- **5-8 entities maximum** per diagram. For large schemas, split into focused diagrams (e.g., "User Domain", "Workflow Domain").
- **Emoji in entity titles** work and improve readability.

A worked 3-entity ERD example (with correct TAB usage) is in `references/diagram-patterns.md` under "Worked Examples".

## Handling Complex Systems

When the user asks for something detailed, don't try to fit everything in one diagram. Instead:

**Option A: Simplify to one clean diagram** with 8-12 nodes. Put details in a companion document using `doc_create`.

**Option B: Multiple focused diagrams** on the same board:
- "System Overview" (flowchart, 8 nodes)
- "Auth Flow" (sequence, 5 actors)
- "Data Model" (ERD, 5-8 entities)

Position multiple diagrams using x/y. The `diagram_create` response includes bounds — use previous width/height + 300px spacing to prevent overlap.

## Companion Documents

Use `doc_create` for details that would clutter the diagram — legends, implementation notes, full field definitions, API specs:

```
doc_create(
  board_id: "...",
  content: "# Architecture Details\n\n## Web App (Next.js 16 — Port 3500)\n- React 19...",
  x: <near the diagram>,
  y: <below or right of diagram>
)
```

## Before You Create — Checklist

- [ ] Called `diagram_get_dsl` first? (DSL syntax can change)
- [ ] Node count under 12?
- [ ] Using 2-3 palette colors with semantic meaning?
- [ ] Clusters have 2-5 nodes each?
- [ ] Emoji in labels for visual scannability?
- [ ] Port numbers on service labels?
- [ ] Connection labels are 1-3 words?
- [ ] Chose the right direction? (LR for architecture, TB for processes)
- [ ] Complex details moved to companion doc?

## Reference Files

- `references/color-palette.md` — Miro's approved hex colors, semantic mappings, and recommended palettes. Read before writing a `palette` line.
- `references/diagram-patterns.md` — Per-type structural patterns, the emoji-by-domain table, and worked DSL examples (flowchart, sequence, ERD). Read before writing DSL for a diagram type you haven't produced this session.
