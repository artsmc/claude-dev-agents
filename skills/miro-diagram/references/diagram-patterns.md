# Diagram Patterns — Miro

Common patterns for each diagram type. These are conceptual guides — always fetch the actual DSL syntax via `diagram_get_dsl` before writing DSL.

---

## Flowchart Patterns

### Architecture Overview
Show system components and their connections. Use color to distinguish layers (frontend, API, database, external services).

**Structure:**
- User/client at top or left
- Services in the middle layer
- Data stores at the bottom or right
- External services on the periphery

### Decision Tree
Show branching logic with decision diamonds and outcome nodes.

**Structure:**
- Entry point at top
- Decision nodes branch left/right or into multiple paths
- Leaf nodes are outcomes/actions
- Color-code by outcome type (success=green, error=red, pending=yellow)

### Pipeline / Data Flow
Show sequential processing stages.

**Structure:**
- Linear left-to-right or top-to-bottom
- Each stage is a node
- Arrows show data transformation
- Side branches for error handling or logging

### Event-Driven Architecture
Show event producers, event bus, and consumers.

**Structure:**
- Producers on the left
- Event bus/queue in the center
- Consumers on the right
- Fan-out pattern from bus to consumers

---

## UML Sequence Diagram Patterns

### Request-Response (Synchronous)
Show a client making a request and receiving a response.

**Structure:**
- Actors: Client, Server, Database
- Solid arrows for requests, dashed for responses
- Include status codes and payload descriptions

### Authentication Flow
Show multi-step auth with token exchange.

**Structure:**
- Actors: User, Frontend, Auth Server, API, Token Store
- Show each redirect, token exchange, and validation step
- Highlight where tokens are stored/verified

### Saga / Orchestration
Show a coordinator managing multiple service calls.

**Structure:**
- Orchestrator in center
- Service calls fan out
- Compensation (rollback) paths shown as dashed/red arrows

---

## Entity-Relationship Diagram Patterns

### Normalized Schema
Standard relational database design.

**Structure:**
- Core entities with primary keys
- Junction tables for many-to-many
- Foreign key relationships as connections
- Include column types and constraints

### Domain Model
Business domain entities and their relationships.

**Structure:**
- Aggregate roots highlighted (primary color)
- Value objects grouped near their parent entity
- Relationship labels describe the business rule (e.g., "places", "contains", "manages")

---

## UML Class Diagram Patterns

### Service Layer
Show service classes, their methods, and dependencies.

**Structure:**
- Interface at top
- Implementing classes below
- Dependencies shown as dashed arrows
- Group by domain/module

### Module Architecture
Show packages/modules and their public interfaces.

**Structure:**
- Each module as a class with key exports
- Dependencies between modules as arrows
- Highlight circular dependencies in red

---

## Multi-Diagram Boards

When a topic needs multiple perspectives, create several diagrams on the same board:

| Perspective | Diagram Type | Purpose |
|-------------|-------------|---------|
| "What components exist?" | Flowchart | Architecture overview |
| "How do they talk?" | UML Sequence | Interaction patterns |
| "What data do they store?" | Entity-Relationship | Data model |
| "What's the class structure?" | UML Class | Code organization |

Place them in a grid layout with 300px spacing, and optionally add a `doc_create` legend/index document in the top-left corner explaining the set.

---

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

---

## Worked Examples

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
