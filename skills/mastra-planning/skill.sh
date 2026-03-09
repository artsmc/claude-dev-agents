#!/usr/bin/env bash
# mastra-planning - Strategic planning and team orchestration for Mastra development tasks
cat << 'SKILL_EOF'

# Mastra Planning & Team Orchestration

You are now in **Mastra Planning Mode**. Your job is to analyze the user's Mastra development task,
design the optimal team composition, create a structured execution plan, and spin up the team.

---

## PHASE 1: Task Analysis

Analyze the user's request and classify it across these Mastra domains:

### Domain Detection Matrix

| Domain | Signals | Skill | Agent Type |
|--------|---------|-------|------------|
| **Agents** | "create agent", "LLM", "chat", "instructions", "tools" | `/mastra-agents` | `mastra-core-developer` |
| **Workflows** | "workflow", "pipeline", "steps", "DAG", "orchestration" | `/mastra-workflows` | `mastra-core-developer` |
| **RAG** | "documents", "search", "embeddings", "vector", "knowledge base" | `/mastra-rag` | `general-purpose` |
| **Memory** | "remember", "context", "conversation history", "recall" | `/mastra-memory` | `general-purpose` |
| **Evals** | "test", "evaluate", "quality", "score", "benchmark" | `/mastra-evals` | `qa-engineer` |
| **Streaming** | "real-time", "stream", "SSE", "live updates" | `/mastra-streaming` | `frontend-developer` |
| **Deploy** | "deploy", "production", "server", "hosting", "auth" | `/mastra-deploy` | `devops-infrastructure` |
| **MCP** | "MCP", "tools", "protocol", "expose", "publish" | `/mastra-mcp-tools` | `mastra-core-developer` |
| **Workspace** | "files", "sandbox", "execute code", "filesystem", "search files", "S3", "GCS" | `/mastra-workspace` | `general-purpose` |
| **Frontend** | "UI", "dashboard", "React", "Next.js", "component" | N/A | `ui-developer` / `frontend-developer` |
| **API** | "endpoint", "REST", "Express", "route" | N/A | `express-api-developer` |
| **Database** | "schema", "migration", "table", "query" | N/A | `database-schema-specialist` |
| **Security** | "auth", "RBAC", "JWT", "compliance", "audit" | N/A | `security-auditor` |

### Complexity Classification

**Level 1 - Single Domain** (1 agent, no team needed):
- "Create a weather agent with tools"
- "Add semantic recall to the chat agent"
- "Deploy to Vercel"

**Level 2 - Multi-Domain** (2-3 agents, small team):
- "Build an agent with RAG and memory"
- "Create a workflow that uses agents and streams results"
- "Add MCP tools and deploy"

**Level 3 - Full Stack Feature** (4+ agents, full team):
- "Build a document Q&A system with agents, RAG, memory, streaming UI, and deployment"
- "Create a multi-agent research workflow with human-in-the-loop, evals, and monitoring"
- "Build an AI-powered code review system end-to-end"

---

## PHASE 2: Team Composition Design

Based on the domains detected, design the team:

### Team Composition Templates

#### Template A: Agent Builder (Domains: Agents + Tools + Memory)
```
Team: mastra-agent-build
Agents:
  - mastra-lead (mastra-core-developer) → Agent design, tool creation, memory config
  - qa-tester (qa-engineer) → Test agent behavior, edge cases
Tasks:
  1. Design agent architecture (instructions, model, tools) → mastra-lead
  2. Create tools with Zod schemas → mastra-lead
  3. Configure memory (storage + processors) → mastra-lead
  4. Write agent tests → qa-tester
  5. Integration testing → qa-tester
```

#### Template B: Workflow Builder (Domains: Workflows + Agents)
```
Team: mastra-workflow-build
Agents:
  - workflow-lead (mastra-core-developer) → Workflow design, step creation
  - agent-dev (mastra-core-developer) → Agent steps within workflow
  - qa-tester (qa-engineer) → Workflow execution testing
Tasks:
  1. Design workflow DAG (steps, control flow, schemas) → workflow-lead
  2. Create agent steps → agent-dev
  3. Implement non-agent steps → workflow-lead
  4. Wire up DAG composition (.then, .parallel, .branch) → workflow-lead
  5. Test workflow execution → qa-tester
```

#### Template C: RAG Pipeline (Domains: RAG + Agents + Memory)
```
Team: mastra-rag-build
Agents:
  - rag-lead (general-purpose) → Pipeline design, vector DB setup
  - agent-dev (mastra-core-developer) → Agent with RAG tools
  - db-specialist (database-schema-specialist) → Vector store optimization
Tasks:
  1. Design chunking strategy → rag-lead
  2. Set up vector store and embeddings → db-specialist
  3. Build ingestion pipeline → rag-lead
  4. Create RAG agent with query tools → agent-dev
  5. Configure memory for context → agent-dev
  6. Test retrieval quality → rag-lead
```

#### Template D: Full Stack Feature (Domains: Agents + Workflows + UI + API + Deploy)
```
Team: mastra-fullstack
Agents:
  - architect (mastra-core-developer) → Agent/workflow design
  - backend-dev (express-api-developer) → API endpoints
  - frontend-dev (ui-developer) → React UI components
  - frontend-logic (frontend-developer) → State management, data fetching
  - qa-tester (qa-engineer) → Testing
Tasks:
  1. Design Mastra agents and workflows → architect
  2. Create API endpoints for agent interaction → backend-dev
  3. Build agent/workflow Mastra code → architect
  4. Create UI components → frontend-dev
  5. Wire up frontend state and API calls → frontend-logic
  6. Integration testing → qa-tester
```

#### Template E: Production Deployment (Domains: Deploy + Security + Monitoring)
```
Team: mastra-deploy
Agents:
  - deploy-lead (devops-infrastructure) → Server config, cloud deployment
  - security-lead (security-auditor) → Auth, RBAC, compliance
  - qa-tester (qa-engineer) → Smoke tests, health checks
Tasks:
  1. Configure server adapter and middleware → deploy-lead
  2. Set up authentication → security-lead
  3. Configure observability (tracing, logging) → deploy-lead
  4. Security review → security-lead
  5. Deploy and verify → deploy-lead
  6. Smoke tests → qa-tester
```

#### Template F: Eval & Quality Pipeline (Domains: Evals + Agents)
```
Team: mastra-eval-build
Agents:
  - eval-lead (qa-engineer) → Scorer design, dataset creation
  - agent-dev (mastra-core-developer) → Agent under test
Tasks:
  1. Define evaluation criteria and scorers → eval-lead
  2. Create test datasets → eval-lead
  3. Configure agent for evaluation → agent-dev
  4. Run experiments → eval-lead
  5. Analyze results and iterate → eval-lead
```

#### Template G: MCP Integration (Domains: MCP + Tools + Agents)
```
Team: mastra-mcp-build
Agents:
  - mcp-lead (mastra-core-developer) → MCP server/client setup
  - tool-dev (mastra-core-developer) → Tool creation
Tasks:
  1. Design MCP tool interface → mcp-lead
  2. Create tools with schemas → tool-dev
  3. Configure MCP server or client → mcp-lead
  4. Test tool discovery and execution → mcp-lead
  5. Publish/distribute → mcp-lead
```

---

## PHASE 3: Execution Plan Generation

Generate a structured plan with these elements:

### Plan Format

```markdown
## Mastra Development Plan: [Feature Name]

### Detected Domains
- [x] Agents
- [x] Workflows
- [ ] RAG
- [x] Memory
- [ ] Evals
- [x] Streaming
- [ ] Deploy
- [ ] MCP

### Complexity: Level [1/2/3]

### Team Composition
Using Template [X] with modifications:

| Role | Agent Type | Responsibilities |
|------|-----------|-----------------|
| ... | ... | ... |

### Task Breakdown

| # | Task | Owner | Depends On | Skill Reference |
|---|------|-------|------------|----------------|
| 1 | ... | ... | - | `/mastra-agents` |
| 2 | ... | ... | #1 | `/mastra-workflows` |
| 3 | ... | ... | #1 | `/mastra-streaming` |
| 4 | ... | ... | #2, #3 | N/A |

### Parallel Execution Groups
- **Group 1** (parallel): Tasks #1
- **Group 2** (parallel, after Group 1): Tasks #2, #3
- **Group 3** (sequential, after Group 2): Task #4

### Key Technical Decisions
- Storage: [PostgresStore / LibSQL / etc.]
- Vector DB: [PgVector / Pinecone / etc. if RAG]
- Server Adapter: [Express / Hono / etc. if Deploy]
- Auth: [JWT / Clerk / etc. if Auth needed]

### Risk Areas
- [Potential issues and mitigations]
```

---

## PHASE 4: Team Spinup

After the user approves the plan, execute it:

### Step 1: Create Team
```
TeamCreate(team_name="mastra-[feature-name]", description="[Feature description]")
```

### Step 2: Create Tasks with Dependencies
```
TaskCreate(subject="[Task 1]", description="[Detailed description with acceptance criteria]", activeForm="[Doing Task 1]")
TaskCreate(subject="[Task 2]", description="...", activeForm="...")
# Set dependencies
TaskUpdate(taskId="2", addBlockedBy=["1"])
```

### Step 3: Spawn Teammates
```
Task(subagent_type="[agent-type]", team_name="mastra-[feature-name]", name="[role-name]", prompt="[Detailed instructions referencing task IDs and skills]")
```

### Step 4: Assign Tasks
```
TaskUpdate(taskId="1", owner="[role-name]")
```

### Step 5: Monitor and Coordinate
- Watch for task completions
- Unblock dependent tasks
- Handle issues and reassign if needed
- Run integration checks after all tasks complete

---

## PHASE 5: Skill Injection

When spawning agents, inject relevant skill knowledge into their prompts:

### Prompt Template for Teammates
```
You are [role] on the [team-name] team.

Your assigned task: [task description]

## Relevant Mastra Knowledge
[Paste key sections from the relevant /mastra-* skill output]

## Key Patterns for This Task
[Specific code patterns they'll need]

## Files to Work With
- [List specific file paths in /home/artsmc/applications/low-code/apps/mastra/]

## Acceptance Criteria
- [ ] [Specific, testable criteria]
- [ ] [...]

## When Done
Mark your task as completed using TaskUpdate and notify the team lead.
```

---

## DECISION FRAMEWORK: When to Use What

### "I need an AI agent that..."
→ Start with `/mastra-agents` skill
→ Spawn `mastra-core-developer` agent
→ If agent needs knowledge → add `/mastra-rag`
→ If agent needs conversation history → add `/mastra-memory`
→ If agent responses stream to UI → add `/mastra-streaming`

### "I need a workflow that..."
→ Start with `/mastra-workflows` skill
→ Spawn `mastra-core-developer` agent
→ If workflow has agent steps → add `/mastra-agents`
→ If workflow needs human approval → HITL pattern from `/mastra-workflows`
→ If workflow streams progress → add `/mastra-streaming`

### "I need to search/query documents..."
→ Start with `/mastra-rag` skill
→ Spawn team: `general-purpose` (pipeline) + `mastra-core-developer` (agent) + `database-schema-specialist` (vector DB)
→ If results feed into agent → add `/mastra-agents`
→ If results feed into workflow → add `/mastra-workflows`

### "I need to deploy/ship this..."
→ Start with `/mastra-deploy` skill
→ Spawn team: `devops-infrastructure` (deploy) + `security-auditor` (auth/security)
→ If exposing as MCP → add `/mastra-mcp-tools`

### "I need to test/evaluate quality..."
→ Start with `/mastra-evals` skill
→ Spawn `qa-engineer` agent
→ If testing agents → also reference `/mastra-agents` for agent patterns
→ If CI integration → include GitHub Actions config from evals skill

### "I need to expose tools via MCP..."
→ Start with `/mastra-mcp-tools` skill
→ Spawn `mastra-core-developer` agent
→ If tools use RAG → add `/mastra-rag`
→ If publishing as package → add deploy considerations

---

## EXECUTION INSTRUCTIONS

When this skill is invoked:

1. **ASK** the user to describe their Mastra development task
2. **ANALYZE** using the Domain Detection Matrix (Phase 1)
3. **CLASSIFY** complexity level (1, 2, or 3)
4. **SELECT** the appropriate team template (Phase 2) or create a custom composition
5. **GENERATE** the structured execution plan (Phase 3)
6. **PRESENT** the plan to the user for approval
7. **EXECUTE** by spinning up the team (Phase 4) with skill-injected prompts (Phase 5)
8. **COORDINATE** the team through task completion
9. **INTEGRATE** results and verify the feature works end-to-end

### Important Rules
- ALWAYS present the plan before executing
- ALWAYS use TaskCreate with proper dependencies
- ALWAYS inject relevant skill knowledge into agent prompts
- PREFER parallel execution groups over sequential when possible
- ALWAYS include a QA/testing task
- ALWAYS reference the AIForge monorepo paths:
  - Mastra app: `/home/artsmc/applications/low-code/apps/mastra`
  - API app: `/home/artsmc/applications/low-code/apps/api`
  - Web app: `/home/artsmc/applications/low-code/apps/web`
  - Microsandbox: `/home/artsmc/applications/low-code/apps/microsandbox`

### Available Skills for Reference
| Skill | Invoke | Domain |
|-------|--------|--------|
| Mastra Agents | `/mastra-agents` | Agent creation, tools, networks, guardrails |
| Mastra Workflows | `/mastra-workflows` | DAG workflows, control flow, HITL |
| Mastra RAG | `/mastra-rag` | Document processing, vector search, retrieval |
| Mastra Memory | `/mastra-memory` | Conversation persistence, recall, processors |
| Mastra Evals | `/mastra-evals` | Testing, scoring, datasets, experiments |
| Mastra Streaming | `/mastra-streaming` | Real-time output, SSE, AI SDK |
| Mastra Deploy | `/mastra-deploy` | Server config, auth, cloud deployment |
| Mastra MCP Tools | `/mastra-mcp-tools` | MCP client/server, tool publishing |
| Mastra Workspace | `/mastra-workspace` | Filesystem, sandbox, skills, search & indexing |
| Mastra Dev | `/mastra-dev` | Code scaffolding CLI |

SKILL_EOF
