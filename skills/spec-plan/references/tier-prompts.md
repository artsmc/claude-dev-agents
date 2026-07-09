# Tier Research Budgets & Agent Prompt Templates

Reference for spec-plan. Read the section you need:
- **Per-tier research budgets** — read during Phase 4 (Budgeted Research) for the confirmed tier.
- **Tier-specific agent prompts** — read during Phase 5 before launching the spec-writer; use the template matching the tier verbatim.

---

## Per-Tier Research Budgets (Phase 4)

### Quick Tier Research (~2K tokens budget)

```
Memory Bank check only:
  - Read activeContext.md (is someone already working on this?)
  - Search memory nodes for feature keywords
  - Budget: 1K tokens max for Memory Bank findings

Codebase scan:
  - Grep for existing implementations of similar patterns
  - Identify the target file(s) for changes
  - Budget: 1K tokens max for codebase findings
```

### Standard Tier Research (~5K tokens budget)

```
Memory Bank (1.5K budget):
  - Read activeContext.md
  - Read systemPatterns.md (architecture constraints)
  - Search memory nodes for feature keywords

Documentation (2K budget):
  - Fetch relevant framework docs via MCP or WebSearch
  - Focus: API patterns, data fetching, state management
  - Stop after finding the primary relevant pattern

Codebase analysis (1.5K budget):
  - Identify existing components to reuse
  - Map integration points
  - Check existing API contracts if API changes needed
```

### Full Tier Research (~10K tokens budget)

```
Memory Bank (2K budget):
  - Read all 6 Memory Bank files
  - Full architecture context

Documentation (4K budget):
  - Fetch framework docs for each relevant pattern
  - Search for case studies and known pitfalls
  - Check for recent breaking changes in dependencies

Codebase deep analysis (3K budget):
  - Full dependency mapping across affected apps
  - Security pattern analysis (if security-sensitive)
  - Existing test patterns for similar features
  - Current auth/RBAC implementation (if auth-related)

External research (1K budget):
  - Similar implementations in open source
  - Known anti-patterns to avoid
```

---

## Tier-Specific Agent Prompts (Phase 5)

### Quick Tier → Single Agent (spec-writer)

```
Generate a focused implementation task list for: {{feature.name}}

CONTEXT BRIEF:
{{structured_brief_json}}

DELIVERABLE: task-list.md ONLY

Requirements for task-list.md:
- Start with a 3-5 line feature summary (inline requirements — no separate FRD)
- Break down into numbered, atomic tasks
- Each task: what to do, which file(s), what pattern to follow
- Include task dependencies (e.g., "depends on Task 2")
- Group into logical phases (setup → implementation → testing)
- Target: 3-8 tasks (if you need more than 8, flag that this may need a higher tier)

DO NOT generate FRD.md, FRS.md, GS.md, or TR.md.
Output: {{output_path}}/task-list.md
```

### Standard Tier → Single Agent (spec-writer)

```
Generate feature specifications for: {{feature.name}}

CONTEXT BRIEF:
{{structured_brief_json}}

DELIVERABLES (3 files):

1. FRD.md — Feature Requirements Document
   - Feature overview (what and why)
   - User stories or use cases (2-5)
   - Acceptance criteria (measurable)
   - Edge cases and error scenarios
   - Success metrics
   MAX LENGTH: 150 lines

2. TR.md — Technical Requirements
   - API contracts (endpoints, methods, request/response schemas)
   - Data model changes (entities, fields, types, migrations)
   - Dependencies (libraries, services, infrastructure)
   - Error handling strategy
   - Security considerations (if applicable)
   MAX LENGTH: 200 lines

3. task-list.md — Implementation Tasks
   - Numbered phases with atomic tasks
   - Each task: specific action, target file(s), pattern to follow
   - Task dependencies noted
   - Agent assignment recommendations (which agent type per task)
   MAX LENGTH: 100 lines

DO NOT generate FRS.md or GS.md (not needed at this tier).
Output: {{output_path}}/
```

### Full Tier → Single Agent or Team

**Single agent (default):**

```
Generate comprehensive specifications for: {{feature.name}}

CONTEXT BRIEF:
{{structured_brief_json}}

DELIVERABLES (5 files):

1. FRD.md — Feature Requirements Document
   - Business objectives and user problems
   - Detailed user stories with acceptance criteria
   - Success metrics with measurable targets
   - Edge cases, error scenarios, boundary conditions
   - Dependencies and assumptions

2. FRS.md — Functional Requirement Specification
   - Detailed functional requirements (FR-001, FR-002, etc.)
   - Component breakdown with responsibilities
   - User workflow diagrams (text-based)
   - State transitions (if stateful)
   - Integration specifications per affected app

3. GS.md — Gherkin Specification
   - Feature declaration
   - Background (shared setup)
   - Scenarios with Given/When/Then
   - Scenario Outlines with Example tables
   - Cover all FRS requirements (1+ scenario per FR)

4. TR.md — Technical Requirements
   - API contracts (endpoints, methods, schemas, error codes)
   - Data models (entities, fields, types, relationships, migrations)
   - Architecture decisions with rationale
   - Security requirements (auth, RBAC, validation, encryption)
   - Performance requirements (latency, throughput, limits)
   - Infrastructure needs (new services, queues, storage)

5. task-list.md — Implementation Tasks
   - Numbered phases with atomic tasks
   - Each task: specific action, target file(s), pattern to follow
   - Task dependencies with blocking relationships
   - Agent assignment (which agent type per task)
   - Estimated complexity per task (S/M/L)

Output: {{output_path}}/
```

**Team mode (with --team flag or auto for very complex features):**

See TEAM-ENHANCEMENT.md for parallel generation workflow.
Team mode is ONLY available for full tier.
