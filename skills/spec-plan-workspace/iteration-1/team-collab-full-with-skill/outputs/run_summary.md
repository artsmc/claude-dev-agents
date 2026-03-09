# Spec-Plan Run Summary: Team Collaboration with Role-Based Permissions

**Date:** 2026-03-09
**Feature:** Team Collaboration with Role-Based Permissions
**Skill Version:** spec-plan v2.0

---

## Phase 0: Feature Description

**User prompt:**
> "Build a team collaboration feature with role-based permissions -- team owners can invite members, assign roles (viewer, editor, admin), and control who can edit workflows vs just view them. Needs audit logging for compliance."

---

## Phase 1: Clarification Questions (Simulated)

The following questions were posed and answered with reasonable assumptions:

### Q1: What problem does this solve for users?
**Simulated answer:** Users currently work in isolation. Teams need to share workflows and agents collaboratively, with fine-grained control over who can view vs edit, to support enterprise and government customers who require access controls for compliance.

### Q2: Which apps are affected?
**Simulated answer:** API (team/RBAC/invitation system + workflow permission enforcement), Web (team management UI, invitation flow, permission-gated workflow views), Mastra (workflow execution needs team context for access control), and potentially Microsandbox (audit logging of execution with team context).

**Result: 3-4 apps affected.**

### Q3: Any hard constraints?
**Simulated answer:** FedRAMP Moderate compliance is required -- all role changes, invitations, and permission modifications must be audit-logged per NIST 800-53 AU-2. Must enforce least privilege (AC-6). WCAG 2.1 AA accessibility required. Must integrate with existing JWT auth and TeamRole enum (OWNER, ADMIN, MEMBER, VIEWER).

---

## Phase 2: Triage Gate -- FULL TIER Selected

### Classification Rationale

This feature qualifies as **FULL-SPEC** based on multiple signals:

| Signal | Match | Details |
|--------|-------|---------|
| 3+ apps affected | YES | API + Web + Mastra + Microsandbox |
| Security-sensitive | YES | RBAC, permission enforcement, access control |
| Compliance implications | YES | FedRAMP, NIST 800-53 (AC-2, AC-3, AC-6, AU-2) |
| New architectural pattern | YES | Invitation system, resource-level permissions, team-scoped workflows |
| 15+ implementation tasks | YES | Estimated 25-30 tasks across 4 apps |
| Unknown patterns needed | PARTIAL | Invitation token flow, email sending, resource-level permissions |

**Tier selected: FULL-SPEC (FRD + FRS + GS + TR + task-list)**

---

## Phase 3: Scope Confirmation

```
Based on your description, I've scoped this as a **FULL** spec:

Feature: Team collaboration with role-based permissions and invitation system
Affected apps: API, Web, Mastra, Microsandbox
Estimated complexity: high

I'll generate:
  [x] task-list.md -- Implementation tasks with dependencies
  [x] FRD.md -- Feature requirements and success criteria
  [x] TR.md -- Technical requirements and API contracts
  [x] FRS.md -- Detailed functional specification
  [x] GS.md -- Gherkin test scenarios

Research scope:
  [x] Memory Bank -- Check existing patterns and active work
  [x] Documentation -- Fetch latest framework patterns
  [x] Deep research -- Case studies, pitfalls, architecture review

Estimated generation time: 8-15 min
Estimated tokens: ~80K

Does this scope look right, or should I adjust?
```

**Simulated response:** "Looks good, proceed."

---

## Phase 4: Budgeted Research Findings

### Memory Bank (2K budget)
- No Memory Bank exists for the low-code monorepo. Skipped.

### Documentation (4K budget)
- Existing CLAUDE.md documents FedRAMP compliance requirements (NIST 800-53 controls AC-2, AC-3, AC-6, AU-2)
- JWT auth flow documented: 15min access tokens, 7-day refresh tokens
- Existing role system: USER, ADMIN, CONTRACTOR at system level
- Existing team roles: OWNER, ADMIN, MEMBER, VIEWER at team level

### Codebase Deep Analysis (3K budget)

**Existing Infrastructure (SIGNIFICANT -- reduces scope):**

1. **Prisma Schema** already has:
   - `Team` model with slug, description, isDefault
   - `TeamMember` model with `TeamRole` enum (OWNER, ADMIN, MEMBER, VIEWER)
   - `Permission` model with resource/action pairs
   - `RolePermission` model linking system roles to permissions
   - `AuditLog` model with action, resource, resourceId, details (JSON), IP, user agent
   - `Agent` model already has optional `teamId` for team scoping

2. **Middleware** already has:
   - `rbac.middleware.ts` -- System-level role checking (ADMIN bypass)
   - `team-access.middleware.ts` -- Team-level role checking with membership validation
   - `audit.middleware.ts` -- FedRAMP audit middleware with AuditAction enum (includes TEAM_MEMBER_ADDED, TEAM_MEMBER_REMOVED, TEAM_ROLE_CHANGED)

3. **API Routes** already have:
   - Full team CRUD at `/api/teams`
   - Team member management at `/api/teams/:id/members` (add, update role, remove)
   - Audit logging on all team operations

4. **Services** already have:
   - `audit.service.ts` -- Fire-and-forget audit logging to PostgreSQL
   - `team.service.ts` -- Slug generation, last-owner protection
   - `agent-access.service.ts` -- Agent-level team access control

5. **What's MISSING (the actual work):**
   - **Invitation system** -- No invitation tokens, email-based invites, or accept/reject flow
   - **Workflow-level team permissions** -- Workflows have `userId` but no `teamId`; no team-scoped workflow access
   - **Resource-level permission enforcement** -- The `Permission`/`RolePermission` models exist but are NOT wired into middleware
   - **Granular edit vs view** -- `team-access.middleware.ts` checks team role but workflow routes don't use it
   - **Web frontend** -- Only a basic team list route exists; no team management UI, invitation UI, or permission-gated views
   - **Mastra integration** -- No team context propagation for workflow executions

### External Research (1K budget)
- Common pitfall: Invitation tokens must be single-use and time-limited (24-48hr expiry)
- Common pitfall: Owner transfer must require confirmation from both parties
- Pattern: Use "editor" role name instead of "member" for clarity in permissions (maps to MEMBER in existing enum)

---

## Phase 5: Deliverables Generated

### Files Generated

| File | Description | Lines |
|------|-------------|-------|
| `run_summary.md` | This file -- tier selection, scope confirmation, research |
| `FRD.md` | Feature Requirements Document -- business objectives, user stories, success metrics |
| `FRS.md` | Functional Requirement Specification -- detailed FR list, component breakdown, state transitions |
| `GS.md` | Gherkin Specification -- BDD test scenarios covering all FRS requirements |
| `TR.md` | Technical Requirements -- API contracts, data models, security, performance |
| `task-list.md` | Implementation task list -- phased tasks with dependencies and agent assignments |

### Structured Brief (JSON)

```json
{
  "feature": {
    "name": "Team Collaboration with Role-Based Permissions",
    "description": "Team owners can invite members, assign roles (viewer, editor, admin), and control who can edit workflows vs just view them, with audit logging for compliance",
    "problem_statement": "Users work in isolation with no way to share workflows collaboratively within teams. Enterprise and government customers require fine-grained access controls and audit trails for FedRAMP compliance.",
    "affected_apps": ["api", "web", "mastra", "microsandbox"],
    "complexity": "high",
    "tier": "full"
  },
  "deliverables": [
    "FRD.md",
    "FRS.md",
    "GS.md",
    "TR.md",
    "task-list.md"
  ],
  "constraints": {
    "security": "FedRAMP Moderate compliance required. RBAC enforcement per NIST 800-53 AC-2, AC-3, AC-6. All permission changes audit-logged per AU-2. Invitation tokens must be single-use, time-limited (48hr), cryptographically random.",
    "performance": "Permission checks must add <10ms latency per request. Invitation token lookup must be indexed. Team member queries should support pagination.",
    "compliance": "NIST 800-53 AU-2 (audit events), AU-3 (audit content), AU-11 (7-year retention). Section 508/WCAG 2.1 AA accessibility. No PII in logs.",
    "deadline": "Not specified"
  },
  "research_findings": {
    "existing_patterns": "Extensive existing infrastructure: Team/TeamMember models with OWNER/ADMIN/MEMBER/VIEWER roles, team-access middleware, audit middleware with FedRAMP-compliant logging, agent-level team access control service, Permission/RolePermission models (unused).",
    "reusable_components": [
      "TeamMember model and TeamRole enum (Prisma schema)",
      "teamMemberMiddleware (team-access.middleware.ts)",
      "auditMiddleware with AuditAction enum (audit.middleware.ts)",
      "createAuditLog fire-and-forget service (audit.service.ts)",
      "AgentAccessService team access pattern (agent-access.service.ts)",
      "Permission and RolePermission models (schema exists, not wired)",
      "BaseController with pagination helpers",
      "Zod validation middleware pattern",
      "RFC 7807 error handling via ApiError"
    ],
    "framework_patterns": "Express 5.x middleware chain: auth -> rbac -> team-access -> validation -> controller -> audit. Prisma ORM for data access. Repository pattern with interfaces. Fire-and-forget audit logging.",
    "integration_points": [
      "Workflow model needs teamId foreign key (schema migration)",
      "Workflow routes need teamMemberMiddleware integration",
      "Web frontend needs team management pages and invitation flow",
      "Mastra workflow execution needs team context propagation",
      "Permission/RolePermission tables need seeding and middleware integration"
    ],
    "pitfalls_to_avoid": [
      "Invitation tokens must be single-use (prevent replay attacks)",
      "Must handle edge case: last owner cannot leave or be demoted (already handled for team members, need for workflows too)",
      "Don't break existing agent team-access patterns when adding workflow team-access",
      "Email invitation requires email service integration (not currently in stack)",
      "Permission model already exists but is unused -- wire it up rather than creating parallel system"
    ]
  },
  "output_path": "/home/artsmc/.claude/skills/spec-plan-workspace/iteration-1/team-collab-full-with-skill/outputs/"
}
```
