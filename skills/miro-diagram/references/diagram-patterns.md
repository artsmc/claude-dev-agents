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
