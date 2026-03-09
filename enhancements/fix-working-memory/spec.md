# Fix 3: Working Memory for Team Coordination

## Problem

When Agent A finishes and Agent B starts on the same team, Agent B has zero knowledge of:
- What Agent A decided (e.g., "chose Zod over Yup for validation")
- What Agent A discovered (e.g., "Prisma schema already has this field")
- What Agent A tried and failed (e.g., "tried approach X, hit auth issue")
- Handoff notes (e.g., "Agent B should start from file Y, line 42")

**Example:** A `database-schema-specialist` designs a schema and completes their task. The `express-api-developer` spawns next but has no idea why the schema looks the way it does, which field names were renamed during design, or which migrations already ran. They re-read everything from scratch or make wrong assumptions.

This costs tokens, causes mistakes, and forces the team lead to repeat context in every message.

---

## Solution

A simple shared markdown file at `~/.claude/working-memory/{team-name}.md`, created when the team starts and deleted when the team closes. Any agent can read or append to it. No tooling required — just file reads and writes.

### File Convention

```
~/.claude/working-memory/{team-name}.md
```

- `{team-name}` matches the name passed to `TeamCreate` exactly
- Created by the team lead at team initialization
- Deleted by the team lead at team shutdown (after `TeamDelete`)
- Readable and writable by all agents on the team

### Template

```markdown
# Working Memory: {team-name}

**Created:** {YYYY-MM-DD HH:MM}
**Team Lead:** {lead-agent-name}
**Goal:** {one-sentence description of what the team is building}

---

## Decisions

> Key choices made — include WHY, not just WHAT.

- [team-lead @ 14:23] Using Zod for request validation (already used across API, consistency)
- [database-schema-specialist @ 14:31] Added `workflow_run_id` as UUID not INT — matches Mastra's existing pattern

---

## Discoveries

> Facts found in the codebase that others should know before starting work.

- [database-schema-specialist @ 14:29] `apps/api/prisma/schema.prisma` already has a `Job` model with `status` enum — reuse it
- [express-api-developer @ 15:02] Auth middleware is in `apps/api/src/middleware/auth.ts`, exports `authMiddleware` and `roleMiddleware`

---

## Blockers & Resolutions

> What went wrong, and how it was resolved (or if it's still open).

- [express-api-developer @ 15:15] BLOCKED: Prisma client not generated after schema change. RESOLVED: ran `nx run api:prisma-generate`
- [qa-engineer @ 15:40] OPEN: Test DB not seeded — waiting for `database-schema-specialist` to confirm seed script path

---

## Handoff Notes

> Targeted notes from one agent to the next.

- [database-schema-specialist → express-api-developer] Migration `20260309_add_workflow_run.sql` is applied. Start from `WorkflowRun` model in schema. Field `external_id` is the public-facing identifier.
- [express-api-developer → qa-engineer] Endpoints are at `POST /api/workflow-runs` and `GET /api/workflow-runs/:id`. Both require Bearer token. See `src/routes/workflowRun.routes.ts`.
```

### Team Lead Integration

Add to `team-lead.md` under **Team Lifecycle > Initialization**:

```markdown
### Working Memory Setup
After `TeamCreate`, create the working memory file:

Path: `~/.claude/working-memory/{team-name}.md`

Use the Write tool to create it from the template in
`~/.claude/enhancements/fix-working-memory/spec.md`.

When sending task instructions to any agent, include:
"Read ~/.claude/working-memory/{team-name}.md before starting.
Append your decisions and discoveries as you work."
```

Add to **Shutdown** section:

```markdown
After `TeamDelete`, delete the working memory file:
`~/.claude/working-memory/{team-name}.md`
```

### Agent Integration

Add to any agent's instructions when spawned by a team lead:

```
Before starting: read ~/.claude/working-memory/{team-name}.md
As you work: append to Decisions, Discoveries, or Blockers sections
Before finishing: add a Handoff Note for the next agent if applicable
```

The team lead includes this in the `prompt` field when calling `Task(...)`.

### Lifecycle

```
TeamCreate(team-name)
  → Team lead creates ~/.claude/working-memory/{team-name}.md from template

Agent A spawned
  → Reads working memory (empty or prior state)
  → Appends discoveries and decisions
  → Adds handoff note before completing task

Agent B spawned
  → Reads working memory (Agent A's entries present)
  → Continues with full context
  → Appends own entries

...

TeamDelete()
  → Team lead deletes ~/.claude/working-memory/{team-name}.md
```

---

## Task List

1. Create `~/.claude/working-memory/` directory
2. Add working memory initialization step to `team-lead.md` (Initialization section)
3. Add working memory deletion step to `team-lead.md` (Shutdown section)
4. Add "read and append working memory" to the default agent spawn prompt pattern in `team-lead.md`
5. Verify: run a 2-agent team, confirm Agent B reads Agent A's entries correctly
