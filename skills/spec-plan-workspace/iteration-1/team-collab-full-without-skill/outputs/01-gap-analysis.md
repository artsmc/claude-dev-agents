# Gap Analysis: Team Collaboration Feature with Role-Based Permissions

**Date:** 2026-03-09
**Scope:** AIForge Monorepo - Team collaboration with workflow access control and audit logging

---

## 1. What Already Exists

### 1.1 Database Schema (Prisma)

| Entity | Status | Notes |
|--------|--------|-------|
| `Team` model | COMPLETE | id, name, slug, description, isDefault, timestamps |
| `TeamMember` model | COMPLETE | id, teamRole, userId, teamId, joinedAt |
| `TeamRole` enum | COMPLETE | OWNER, ADMIN, MEMBER, VIEWER |
| `Permission` model | EXISTS (unused) | name, description, resource, action |
| `RolePermission` model | EXISTS (unused) | role, permissionId |
| `AuditLog` model | COMPLETE | action, resource, resourceId, details, ipAddress, userAgent, userId |
| `Workflow` model | EXISTS | **Missing**: teamId foreign key (only userId-scoped currently) |
| `Agent` model | EXISTS | Already has optional teamId FK |

### 1.2 API Service (Express)

| Component | Status | Notes |
|-----------|--------|-------|
| Team CRUD routes | COMPLETE | POST/GET/PUT/DELETE /api/teams |
| Team member routes | COMPLETE | GET/POST/PUT/DELETE /api/teams/:id/members |
| Team access middleware | COMPLETE | `teamMemberMiddleware()` with role checking |
| RBAC middleware | COMPLETE | `roleMiddleware()` for system-level roles |
| Audit middleware | COMPLETE | `auditMiddleware()` with fire-and-forget pattern |
| Audit service | COMPLETE | `createAuditLog()` with FedRAMP compliance |
| Team schemas (Zod) | COMPLETE | CreateTeam, UpdateTeam, AddMember, UpdateMember |
| Team repository | COMPLETE | Full CRUD with pagination, search, slug generation |
| Team member repository | COMPLETE | Add, update role, remove, owner protection |
| Workflow routes | EXISTS | **Missing**: Team-scoped workflow access |
| Workflow controller | EXISTS | Uses `assertOwnership()` - user-only, no team context |

### 1.3 Web Frontend (Next.js)

| Component | Status | Notes |
|-----------|--------|-------|
| Teams API proxy | EXISTS | `/api/teams/route.ts` - list only |
| Team pages (coverage only) | STUBS | Coverage reports show teams pages existed but actual source files are missing from `src/app/(auth)/teams/` |
| Settings > Teams | STUBS | Coverage report references exist |
| Team components | MISSING | No team-specific React components found |
| Workflow pages | EXISTS | `/app/(auth)/workflows/` with list and detail pages |

### 1.4 Mastra / Microsandbox

| Component | Status | Notes |
|-----------|--------|-------|
| Mastra team awareness | MISSING | No team-scoped workflow execution |
| Microsandbox team awareness | MISSING | No team-scoped skill execution |

---

## 2. Critical Gaps

### Gap 1: Workflows Are Not Team-Scoped (CRITICAL)

**Current state:** Workflows belong to individual users via `userId`. There is no `teamId` on the Workflow model. The `assertOwnership()` check in `workflow.controller.ts` only compares `workflow.userId === user.userId` or checks ADMIN role.

**Required:** Workflows need optional team ownership. Team members with EDITOR/ADMIN/OWNER roles should be able to edit team workflows. VIEWER role members should have read-only access.

**Impact:** Database migration + API controller changes + new middleware + frontend changes.

### Gap 2: No Invitation System (MAJOR)

**Current state:** Adding team members requires providing a `userId` directly via `POST /api/teams/:id/members`. There is no email-based invitation flow.

**Required:** Team owners/admins should be able to invite members by email. Invitations should have an accept/decline workflow. Pending invitations should be trackable.

**Impact:** New database model (TeamInvitation) + new API endpoints + email integration + frontend UI.

### Gap 3: No Resource-Level Permission Enforcement (MAJOR)

**Current state:** The `Permission` and `RolePermission` Prisma models exist but are completely unused. No code references them. Team roles (OWNER/ADMIN/MEMBER/VIEWER) are defined but not mapped to specific resource actions (edit workflow, view workflow, execute workflow).

**Required:** Clear permission mapping from team roles to resource actions. The VIEWER role should only allow read access. MEMBER maps to the requested "editor" concept. Team roles need to gate specific actions on workflows.

**Impact:** New middleware or enhanced existing middleware + permission matrix implementation.

### Gap 4: No Team-Workflow Association UI (MAJOR)

**Current state:** Frontend has workflow pages but no way to assign workflows to teams, view team workflows, or respect team-based permissions in the UI.

**Required:** Frontend needs team-scoped workflow views, team selector in workflow creation, and role-appropriate UI (hide edit buttons for viewers).

**Impact:** Multiple frontend pages and components.

### Gap 5: Audit Logging Gaps for New Operations (MODERATE)

**Current state:** Audit logging exists for team CRUD and member management. Workflow CRUD does not have audit logging.

**Required:** Audit logging for workflow access (view/edit/delete) scoped to team context, invitation events, and permission changes. All needed for FedRAMP compliance.

**Impact:** Additional audit middleware on workflow routes + new audit action types.

### Gap 6: Skills Not Team-Scoped (MODERATE)

**Current state:** Skills have no team association at all. They exist as standalone entities.

**Required:** Skills should optionally belong to teams with the same permission model as workflows.

**Impact:** Database migration + API changes (similar pattern to workflows).

---

## 3. Role Mapping: Requested vs Existing

The user requested: **viewer, editor, admin** (plus owner implied).

The existing `TeamRole` enum has: **OWNER, ADMIN, MEMBER, VIEWER**.

| Requested Role | Maps To | Permissions Needed |
|---------------|---------|-------------------|
| Owner | OWNER (exists) | Full team control, invite, manage all roles, CRUD all resources |
| Admin | ADMIN (exists) | Invite members, assign roles (except OWNER), CRUD team resources |
| Editor | MEMBER (exists, rename conceptually) | Edit workflows, skills; execute workflows; cannot manage team |
| Viewer | VIEWER (exists) | Read-only access to team workflows, skills, executions |

The existing enum works. The "editor" concept maps naturally to "MEMBER" since the current MEMBER role has no permission enforcement yet -- we define it as the editing role.

---

## 4. Summary of Work Required

| Category | Effort | Priority |
|----------|--------|----------|
| Prisma schema: Add teamId to Workflow, TeamInvitation model | Medium | P0 |
| API: Team-scoped workflow access middleware | Medium | P0 |
| API: Workflow controller team-aware authorization | Medium | P0 |
| API: Invitation endpoints (create, accept, decline, list) | Large | P0 |
| API: Audit logging for workflows | Small | P0 |
| Web: Team detail page with member management | Large | P1 |
| Web: Team-scoped workflow list/detail views | Medium | P1 |
| Web: Invitation UI (send, accept/decline) | Medium | P1 |
| Web: Role-appropriate UI rendering | Medium | P1 |
| API: Skill team-scoping (same pattern as workflows) | Medium | P2 |
| Mastra: Team context in workflow execution | Small | P2 |
| API: Populate Permission/RolePermission tables | Small | P2 |
