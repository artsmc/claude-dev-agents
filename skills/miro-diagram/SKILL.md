---
name: miro-diagram
description: >
  Create professional diagrams directly on Miro boards using the Miro MCP tools.
  Supports flowcharts, UML class diagrams, UML sequence diagrams, and entity-relationship diagrams.
  Use this skill whenever the user wants to create, visualize, or diagram anything on a Miro board —
  architecture diagrams, system flows, database schemas, interaction sequences, process maps,
  decision trees, or any visual that communicates structure and relationships.
  Also trigger when the user says things like "draw this on Miro", "make a diagram",
  "visualize this architecture", "create an ERD", "map out this flow",
  "sequence diagram for this interaction", or "put this on my Miro board".
  Even if the user just says "diagram this" without mentioning Miro, use this skill
  if the Miro MCP is connected.
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

Miro renders emoji in node labels, entity titles, actor names, and cluster titles. Use them — they dramatically improve visual scannability.

**Recommended emoji by domain:**

| Domain | Emoji | Example Label |
|--------|-------|---------------|
| User/Actor | 👤 | `👤 User` |
| Web/Frontend | 🌐 | `🌐 Web App :3500` |
| API/Auth | 🔐 | `🔐 API Gateway :4000` |
| AI/ML | 🤖 | `🤖 Mastra Engine :3000` |
| Container/Sandbox | 📦 | `📦 Microsandbox :5000` |
| Database | 🐘 | `🐘 PostgreSQL` |
| Cache/Fast store | ⚡ | `⚡ Redis` |
| Logs/Audit | 📋 | `📋 S3 Audit Logs` |
| Workflow | 🔄 | `🔄 Workflow` |
| Skill/Plugin | 🧩 | `🧩 Skill` |
| Execution | ⚡ | `⚡ Execution` |
| Storage | 💾 | `💾 Data Layer` (cluster) |
| App layer | 🖥️ | `🖥️ Application Layer` (cluster) |
| External | 🌍 | `🌍 Third-party API` |
| Queue/Async | 📬 | `📬 Job Queue` |
| Config | ⚙️ | `⚙️ Config Service` |

Add port numbers to service labels when relevant (e.g., `:3500`, `:4000`) — they provide useful context at a glance.

## Flowchart Diagrams

### The Golden Rules

1. **8-12 nodes maximum.** One node per major component or decision point. Internal details (middleware, ORM layers) belong in labels or companion docs, not separate nodes.

2. **2-3 palette colors.** Each color = a meaning. Use Miro's approved colors:
   ```
   #ffc6c6 (red)    #f8d3af (orange)  #fff6b6 (yellow)
   #dbfaad (lime)   #adf0c7 (green)   #c3faf5 (teal)
   #ccf4ff (ltblue) #c6dcff (blue)    #dedaff (purple)
   #ffd8f4 (pink)   #e7e7e7 (gray)
   ```

3. **2-3 clusters with 2-5 nodes each.** Clusters organize the story — "Application Layer" vs "Data Layer" — but too many clusters with cross-connections create spaghetti.

4. **Use node types semantically:**
   - `flowchart-process` — Services, components, actions (rectangle)
   - `flowchart-decision` — Branch points, conditions (diamond)
   - `flowchart-terminator` — Start/end points (rounded)
   - `flowchart-data` — Databases, files, storage (parallelogram)

5. **Connection labels: 1-3 words.** Use `-` for self-evident connections. Label decisions (`YES`/`NO`) and cross-service connections (`REST`, `Queue`, `Triggers`).

### Example: Architecture Flowchart

```
graphdir LR
palette #c6dcff #c3faf5 #adf0c7 #dedaff

n1 👤 User flowchart-terminator 2
n2 🌐 Web App :3500 flowchart-process 0
n3 🔐 API Gateway :4000 flowchart-process 0
n4 🤖 Mastra Engine :3000 flowchart-process 3
n5 📦 Microsandbox :5000 flowchart-process 0
n6 🐘 PostgreSQL flowchart-data 1
n7 ⚡ Redis flowchart-data 1
n8 📋 S3 Audit Logs flowchart-data 1

c n1 HTTPS n2
c n2 REST n3
c n3 Workflows n4
c n3 Skills n5
c n3 Query n6
c n4 State n6
c n4 Jobs n7
c n5 Logs n8

cluster c1 "🖥️ Application Layer" n2 n3 n4 n5
cluster c2 "💾 Data Layer" n6 n7 n8
```

Why this works: 8 nodes, 3 colors, 2 clusters, LR direction, emoji labels with ports, short connection labels.

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

### Example: Auth + API Call Sequence

```
graphdir LR

n1 "👤 User" #adf0c7
n2 "🌐 Web App" #c6dcff
n3 "🔐 API Service" #c6dcff
n4 "🐘 Database" #c3faf5

e1 "Login request" n1 n2 async_call
e2 "POST /api/auth/login" n2 n3 sync_call
e3 "Validate credentials" n3 n4 sync_call
e4 "Return user record" n4 n3 sync_return
e5 "Generate JWT (15min)" n3 n3 sync_call
e6 "200 OK + tokens" n3 n2 sync_return
e7 "Store token, show dashboard" n2 n1 async_call
```

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

### Example: Core Data Model

```
graphdir LR

n1 "👤 User" "PK	id	uuid
	email	string
	role	enum" #c6dcff

n2 "🔄 Workflow" "PK	id	uuid
FK	userId	uuid
	name	string
	status	enum" #c6dcff

n3 "⚡ Execution" "PK	id	uuid
FK	workflowId	uuid
	status	enum
	startedAt	timestamp" #adf0c7

e1 "creates" n1 one .. zero_or_many n2
e2 "triggers" n2 one .. zero_or_many n3
e3 "runs" n1 one .. zero_or_many n3
```

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

- `references/color-palette.md` — Miro's approved colors and semantic mappings
- `references/diagram-patterns.md` — Common patterns for each diagram type
