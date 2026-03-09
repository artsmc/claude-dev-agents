# Execution Trace: Notification System with Real-Time WebSocket Events, Email Digests, and In-App Notification Center

**Prompt:** `Build a complete notification system with real-time WebSocket events, email digests, and in-app notification center --team`

**Skill invoked:** `feature-new` (implied by phrase "build a complete ... system")

**Mode detected:** `team` (from `--team` flag)

---

## 1. How I Interpret the --team Flag

The `--team` flag maps to `mode: "team"` in the `feature-new` skill. This changes behavior at two points in the 5-step workflow:

**Step 1 (spec-plan):** The `--team` flag is passed through to spec-plan as a flag argument. Spec-plan's `--team` option is only active at the `full` tier, enabling parallel generation of the 5 spec documents by multiple agents instead of a single sequential agent. Given that a notification system touches 3+ apps (API, Web, Mastra), involves a new architectural pattern (WebSocket server, email queue), and will likely exceed 15 implementation tasks, it will triage as a `full` tier spec — so the team flag is meaningful here.

**Step 5 (execute):** Instead of `start-phase-execute`, the skill routes to `start-phase-execute-team`. This runs implementation waves with multiple specialized agents working in parallel across affected apps, rather than sequential single-agent execution.

The 5-step sequence itself is unchanged. `--team` does not skip any step; it only affects how Steps 1 and 5 operate internally.

---

## 2. Step-by-Step Plan

### Step 1: Generate Feature Specification (spec-plan --team)

**Invocation:**
```
Skill: spec-plan
Args: "Build a complete notification system with real-time WebSocket events,
       email digests, and in-app notification center --team"
```

**Phase 0 — Feature Description:**
The feature description is provided in the prompt, so Phase 0 is satisfied immediately.

**Phase 1 — Clarify Requirements (lightweight):**
Before triaging I would ask the user 2-3 targeted questions:
1. What triggers a notification? (workflow state changes, agent completions, user mentions, system alerts?)
2. Are there any hard performance constraints on WebSocket delivery latency, or email volume/frequency?
3. Any compliance requirements? (e.g., FedRAMP audit logging of notification events)

These answers shape the triage decision and inform the structured brief sent to the spec-writer.

**Phase 2 — Triage Gate:**
Classification: **FULL-SPEC**

Reasons:
- 3+ apps affected: API (notification endpoints, user preferences), Web (in-app notification center UI, WebSocket client), Mastra (triggers notifications on workflow events), possibly Microsandbox (skill execution completion events)
- New architectural pattern: WebSocket server (not currently in the stack), email digest queue, notification storage model
- Estimated 20+ implementation tasks (WebSocket infra, email worker, API endpoints, Prisma schema, React UI, Mastra hooks, preference management)
- Background job processing via PGBoss (Mastra) for email digests introduces cross-service coordination

**Phase 3 — Scope Confirmation:**
Present the following to the user and wait for approval:

```
Based on your description, I've scoped this as a FULL spec:

Feature: Real-time notification system with WebSocket delivery, email digests,
         and in-app notification center
Affected apps: API, Web, Mastra (+ possibly Microsandbox)
Estimated complexity: High

I'll generate:
  [x] task-list.md       — Implementation tasks with dependencies
  [x] FRD.md             — Feature requirements and success criteria
  [x] TR.md              — Technical requirements and API contracts
  [x] FRS.md             — Detailed functional specification
  [x] GS.md              — Gherkin test scenarios

Research scope:
  [x] Memory Bank        — Check existing patterns and active work
  [x] Documentation      — WebSocket patterns, email service patterns
  [x] Deep research      — Architecture review, pitfalls (fan-out at scale,
                           WebSocket reconnection, email deliverability)

Estimated generation time: 5-10 min (team mode, parallel generation)
Estimated tokens: ~120K

Does this scope look right, or should I adjust?
```

**Phase 4 — Budgeted Research (~10K tokens total):**

- **Memory Bank (2K budget):** Read all 6 Memory Bank files. Check activeContext.md for any overlapping in-progress work. Check systemPatterns.md for existing auth/RBAC patterns (notifications require user-scoped data), existing job queue patterns (PGBoss already used in Mastra).

- **Documentation (4K budget):** Fetch WebSocket patterns for Express 5.x (ws or socket.io), Next.js WebSocket client integration patterns, PGBoss scheduled job patterns for email digests, Resend or Nodemailer for transactional email. Stop after finding the primary relevant pattern for each.

- **Codebase deep analysis (3K budget):**
  - Grep for existing WebSocket usage: likely none, this is new infrastructure
  - Map Prisma schema for existing user/auth models to understand where `Notification` and `NotificationPreference` entities attach
  - Check Mastra workflow event hooks: where workflow steps emit completion events
  - Review API auth middleware for how `req.user` is populated (needed for notification ownership)

- **External research (1K budget):** Fan-out delivery patterns for real-time notifications, email digest batching strategies, WebSocket reconnection with exponential backoff.

**Phase 5 — Launch Spec-Writer in Team Mode:**
Because tier is `full` and `--team` was passed, spawn 5 parallel agents via Task tool:

```
Task: spec-writer agent 1 → FRD.md
Task: spec-writer agent 2 → FRS.md
Task: spec-writer agent 3 → GS.md
Task: spec-writer agent 4 → TR.md
Task: spec-writer agent 5 → task-list.md (after other agents draft their sections)
```

Each agent receives the same structured JSON brief:

```json
{
  "feature": {
    "name": "feature-notification-system",
    "description": "Real-time notification system with WebSocket events, email digests, and in-app notification center",
    "problem_statement": "Users have no visibility into async workflow completions, agent outputs, or system events without manually polling",
    "affected_apps": ["api", "web", "mastra"],
    "complexity": "high",
    "tier": "full"
  },
  "deliverables": ["FRD.md", "FRS.md", "GS.md", "TR.md", "task-list.md"],
  "constraints": {
    "security": "Notifications are user-scoped; no cross-user data leakage. WebSocket connections must be JWT-authenticated.",
    "performance": "WebSocket delivery < 500ms P99. Email digest batching to avoid spam.",
    "compliance": "Notification events must be audit-logged (FedRAMP AU-2). PII must not appear in logs."
  },
  "research_findings": {
    "existing_patterns": "PGBoss already used in Mastra for background jobs. JWT auth via authMiddleware. Prisma ORM on API side.",
    "reusable_components": "Existing PGBoss worker setup, JWT middleware, TanStack Query for server state on Web",
    "framework_patterns": "ws library for WebSocket on Express 5, useEffect + useRef for WebSocket client in Next.js",
    "integration_points": "Mastra workflow step hooks → API notification endpoint → WebSocket broadcast to connected clients",
    "pitfalls_to_avoid": "Fan-out bottleneck on high-volume workflows, WebSocket reconnection storms, email digest rate limits"
  },
  "output_path": "/home/artsmc/applications/low-code/job-queue/feature-notification-system/docs/"
}
```

After all 5 agents complete, record:
- `feature_name`: `feature-notification-system`
- `spec_dir`: `/home/artsmc/applications/low-code/job-queue/feature-notification-system/docs/`
- `task_list_path`: `/home/artsmc/applications/low-code/job-queue/feature-notification-system/docs/task-list.md`

**Failure handling:** If spec-plan fails, stop and tell the user:
> "Specification generation failed at Step 1. You can retry directly with: `/spec-plan Build a complete notification system with real-time WebSocket events, email digests, and in-app notification center --tier full --team`"

---

### Step 2: Review Specification Quality (spec-review)

**Invocation:**
```
Skill: spec-review
```

spec-review is tier-aware. For a full-tier spec it validates that all 5 files exist, are internally consistent, and have no structural gaps (missing acceptance criteria, undefined API contracts, unlinked Gherkin scenarios, etc.).

**Expected outcomes:**

- **Clean pass:** Proceed to Step 3.
- **Warnings only** (minor issues like missing one edge case): Proceed to Step 3, note warnings.
- **Errors** (e.g., TR.md missing WebSocket endpoint contract, GS.md scenarios don't cover email unsubscribe): Ask user via AskUserQuestion:
  - "Continue anyway" → proceed to Step 3
  - "Stop and fix" → halt, tell user specs are at `spec_dir`, they can re-run spec-plan or edit manually

**Failure handling:** If spec-review itself errors (tool failure), warn the user that quality validation was skipped, then proceed — spec-review is a safety net, not a hard gate.

---

### Step 3: Create Execution Plan (start-phase-plan)

**Invocation:**
```
Skill: start-phase-plan
Args: "/home/artsmc/applications/low-code/job-queue/feature-notification-system/docs/task-list.md"
```

start-phase-plan analyzes the task list, identifies dependencies, proposes wave structure and agent assignments, then presents the plan to the user for approval before proceeding.

**Expected wave structure for this feature (illustrative):**

```
Wave 1 (Infrastructure/Foundation — parallel):
  - database-schema-specialist: Prisma migration for Notification + NotificationPreference models
  - api-designer: Define WebSocket message contract + REST notification API contract

Wave 2 (Backend Implementation — parallel after Wave 1):
  - express-api-developer: Implement notification CRUD endpoints + WebSocket server on API
  - express-api-developer (2nd agent): Implement email digest PGBoss worker + email service integration
  - Mastra developer: Add workflow event hooks that POST notifications to API

Wave 3 (Frontend — parallel after Wave 2):
  - ui-developer: Build in-app notification center UI components (bell icon, panel, unread count badge)
  - frontend-developer: WebSocket client integration + TanStack Query for notification data fetching + notification preference settings page

Wave 4 (Quality — sequential after Wave 3):
  - qa-engineer: Unit tests for API notification endpoints
  - nextjs-qa-developer: Integration tests for notification center UI
  - security-auditor: Verify JWT-gated WebSocket auth, no cross-user data leakage
```

**Human checkpoint:** start-phase-plan presents this wave structure and asks the user to approve before execution begins. If the user rejects, stop and tell them:
> "Planning halted at user request. Specs are saved at `spec_dir`. Resume planning with: `/start-phase plan {task_list_path}`"

**Failure handling:** If start-phase-plan fails (script error, path not found), verify the task_list_path using Glob before retrying. If path is wrong, locate it with:
```
Glob: "**/feature-notification-system/**/task-list.md"
```

---

### Step 4: Import to PM-DB (best-effort)

**Invocation:**
```
Skill: pm-db
Args: "import --project feature-notification-system --auto-confirm"
```

This imports the feature into the PM-DB tracking database. The `--auto-confirm` flag prevents interactive prompts and makes this non-blocking.

**Expected outcomes:**

- **Success:** PM-DB returns project ID, phase ID, plan ID. Note these for reference in execution tracking.
- **Failure** (DB not running, import error, duplicate project): Warn the user:
  > "PM-DB import failed. Tracking will be unavailable during execution. You can import later with: `/pm-db import --project feature-notification-system`"
  Then proceed to Step 5 unconditionally.

This step is **best-effort only** — it never blocks the workflow.

---

### Step 5: Execute Tasks (start-phase-execute-team)

Because `mode` is `"team"`, route to `start-phase-execute-team`:

**Invocation:**
```
Skill: start-phase-execute-team
Args: "/home/artsmc/applications/low-code/job-queue/feature-notification-system/docs/task-list.md"
```

This skill handles parallel agent execution across waves. Each wave is gated by quality checks before the next wave starts.

**What happens internally:**

1. **Wave 1 execution:** Spawn `database-schema-specialist` and `api-designer` in parallel via Task tool. Wait for both to complete and pass quality gate (schema migration runs cleanly, API contract document is produced).

2. **Wave 2 execution:** Spawn 3 agents in parallel (2x express-api-developer for different concerns, 1 Mastra developer). Each agent works in its own scope. Quality gate: all endpoints return expected responses in local testing.

3. **Wave 3 execution:** Spawn `ui-developer` and `frontend-developer` in parallel. UI agent builds component tree; frontend agent wires WebSocket connection + data fetching. Quality gate: pages render without TypeScript errors, WebSocket connection established.

4. **Wave 4 execution:** QA agents and security auditor run sequentially. Security auditor validates auth boundaries before marking complete.

5. **Git commits:** Each agent commits their own wave's changes with conventional commit messages. `start-phase-execute-team` does not force-push or squash across agents.

6. **PM-DB hooks:** If PM-DB import succeeded in Step 4, execution skill fires hooks to update task status as each task completes.

**Failure handling mid-execution:**
- **Single task failure:** The execution skill retries once, then marks the task as failed and continues remaining non-dependent tasks in the wave. Blocked dependent tasks are skipped and flagged.
- **Wave failure (multiple tasks fail):** Halt execution. Tell the user:
  > "Execution halted in Wave [N]. The following tasks failed: [list]. Resume with: `/feature-continue` or `/start-phase execute {task_list_path}`"
- **Agent spawn failure (Task tool error):** Fall back to sequential execution for that wave if parallel spawn fails. Log the fallback.

---

## 3. Work Organization Across Apps

| App | Work | Agents |
|-----|------|--------|
| **API** (port 4000) | Prisma schema migration (`Notification`, `NotificationPreference` models), REST endpoints (`GET /notifications`, `POST /notifications/:id/read`, `PUT /notifications/preferences`), WebSocket server upgrade on Express 5.x, JWT auth on WebSocket handshake, email digest PGBoss worker | `database-schema-specialist`, `express-api-developer` (x2), `security-auditor` |
| **Web** (port 3500) | Notification center panel component, unread badge, mark-as-read interaction, WebSocket client hook (`useNotifications`), notification preferences settings page, TanStack Query integration for notification list | `ui-developer`, `frontend-developer`, `nextjs-qa-developer` |
| **Mastra** (port 3000) | Workflow step completion event hooks that POST to API notification service, agent output notification triggers | Mastra-specialized developer (or `express-api-developer` with Mastra context) |
| **Shared (libs/)** | Notification event type definitions shared between API and Mastra | Any agent working on API can define these in `libs/shared` |

**Cross-app coordination constraint:** Wave 2 (backend implementation) must complete before Wave 3 (frontend) begins — the frontend needs the WebSocket URL and REST endpoint contracts to be stable before building against them.

---

## 4. Tools and Skills Used

| Step | Tool/Skill | Purpose |
|------|-----------|---------|
| Flag parsing | Built-in string matching on `--team` | Detect team mode |
| Step 1 | `spec-plan` skill | Generate FULL-tier specs in parallel team mode |
| Step 1 | `Task` tool (x5) | Parallel spec-writer agents for 5 documents |
| Step 1 | `Memory Bank` read | Check existing patterns and active work |
| Step 1 | `Grep` / `Glob` | Codebase analysis for integration points |
| Step 1 | `WebSearch` | WebSocket patterns, email service patterns, architecture research |
| Step 2 | `spec-review` skill | Validate spec quality before planning |
| Step 3 | `start-phase-plan` skill | Wave decomposition with user approval checkpoint |
| Step 4 | `pm-db` skill | Import feature for tracking (best-effort) |
| Step 5 | `start-phase-execute-team` skill | Parallel wave execution with multiple specialized agents |
| Step 5 | `Task` tool (multiple) | Spawn specialized agents per wave |
| All steps | `Glob` | Locate output artifacts, verify path state for skip detection |

---

## 5. Failure Scenarios and Recovery

| Scenario | Response |
|----------|----------|
| **Step 1 fails** (spec-plan error) | Stop immediately. Tell user to retry: `/spec-plan "Build a complete notification system..." --tier full --team` |
| **Step 1 partial** (some spec docs missing) | Run spec-review anyway — it will flag missing files. If blockers found, ask user whether to stop and fix or continue. |
| **Step 2 finds errors** | Ask user: "Continue anyway" or "Stop and fix". User decides — never auto-skip errors. |
| **Step 3 fails** (start-phase-plan error) | Verify `task_list_path` with Glob before retrying. If path is bad, re-search. Then tell user: `/start-phase plan {task_list_path}` |
| **Step 3 user rejects plan** | Halt. Specs are saved. User can re-plan with different wave structure. |
| **Step 4 fails** (PM-DB import error) | Warn, proceed. Tracking optional. User can import later: `/pm-db import --project feature-notification-system` |
| **Step 5 single task fails** | Retry once. If still failing, mark failed, continue non-dependent tasks, flag blocked tasks. |
| **Step 5 wave fails** | Halt. Report which tasks failed. User resumes with: `/feature-continue` or `/start-phase execute {task_list_path}` |
| **Task tool spawn failure** | Fall back to sequential for affected wave. Log fallback reason. |
| **WebSocket infra not supported** | Flag in Wave 1 quality gate. Spec-writer should have noted whether `ws` or `socket.io` was appropriate; execution agent checks if package exists in `apps/api/package.json` and installs if missing. |
| **Mid-execution context loss** | `start-phase-execute-team` maintains state in `task-list.md` (checking off completed tasks). Resume capability via `/feature-continue` which re-reads that file. |

---

## Summary

The `--team` flag is detected immediately and sets `mode = "team"`. This passes `--team` to `spec-plan` (enabling parallel 5-agent spec generation at the full tier) and routes Step 5 to `start-phase-execute-team` instead of `start-phase-execute` (enabling parallel wave execution).

The 5-step sequence is preserved exactly: spec-plan → spec-review → start-phase-plan → pm-db → start-phase-execute-team. No steps are skipped, reordered, or merged due to team mode.

The notification system is classified as a full-tier spec (3+ apps, new architectural pattern, 20+ tasks, security-sensitive WebSocket auth). Team mode provides meaningful time savings at both the spec generation phase (parallel docs) and execution phase (parallel waves across API, Web, and Mastra).

All failures follow the principle: fail fast, explain clearly, give a recovery command. Step 4 (PM-DB) is the only best-effort step that does not halt on failure.
