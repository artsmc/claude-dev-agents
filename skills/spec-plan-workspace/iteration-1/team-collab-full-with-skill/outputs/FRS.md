# Functional Requirement Specification: Team Collaboration with Role-Based Permissions

**Document ID:** FRS-TEAM-COLLAB-001
**Version:** 1.0
**Date:** 2026-03-09
**Status:** Draft
**Tier:** Full

---

## 1. Functional Requirements

### 1.1 Invitation System

**FR-001: Create Team Invitation**
- Team OWNER or ADMIN can create an invitation for a user by email
- System generates a cryptographically random token (32 bytes, base64url encoded)
- Invitation record stores: token, teamId, inviterUserId, inviteeEmail, assignedRole, status, expiresAt
- Token expires 48 hours after creation
- Duplicate active invitations (same email + same team) are rejected with 409

**FR-002: List Pending Invitations (Team View)**
- Team OWNER or ADMIN can list all pending invitations for their team
- Response includes: invitee email, assigned role, created date, expiry date, status
- Supports pagination (default 20 per page)

**FR-003: Revoke Team Invitation**
- Team OWNER or ADMIN can revoke a pending invitation before it is accepted
- Revoked invitations cannot be accepted (status changes to REVOKED)
- Audit log records revocation event

**FR-004: List My Pending Invitations (User View)**
- Authenticated user can list invitations sent to their email address
- Returns invitations in PENDING status where inviteeEmail matches user's email
- Includes team name, inviter name, assigned role, expiry

**FR-005: Accept Team Invitation**
- User provides invitation token to accept
- System validates: token exists, status is PENDING, not expired
- Creates TeamMember record with the assigned role
- Updates invitation status to ACCEPTED
- Audit log records acceptance event

**FR-006: Decline Team Invitation**
- User provides invitation token to decline
- Updates invitation status to DECLINED
- Audit log records decline event

### 1.2 Workflow Team Association

**FR-007: Share Workflow with Team**
- Workflow owner can associate a workflow with a team they belong to
- Sets workflow.teamId to the target team ID
- Workflow owner retains full access regardless of team role
- Audit log records share event

**FR-008: Unshare Workflow from Team**
- Workflow owner (or team OWNER/ADMIN) can remove team association
- Sets workflow.teamId to null
- Audit log records unshare event

**FR-009: List Team Workflows**
- Team members can list workflows where teamId matches their team
- Access level determined by team role (see FR-012)
- Supports pagination, search, and status filtering

**FR-010: Create Workflow in Team Context**
- Team members with MEMBER role or higher can create workflows directly associated with a team
- Workflow.userId set to creator, workflow.teamId set to team
- Creator retains ownership even if removed from team later

### 1.3 Resource-Level Permission Enforcement

**FR-011: Permission Matrix Definition**
The following permission matrix applies to team-scoped workflows:

| Action | VIEWER | MEMBER (Editor) | ADMIN | OWNER |
|--------|--------|-----------------|-------|-------|
| List team workflows | Yes | Yes | Yes | Yes |
| View workflow details | Yes | Yes | Yes | Yes |
| View workflow definition (DAG) | Yes | Yes | Yes | Yes |
| Create workflow in team | No | Yes | Yes | Yes |
| Edit workflow name/description | No | Yes | Yes | Yes |
| Edit workflow definition (DAG) | No | Yes | Yes | Yes |
| Delete workflow | No | No | Yes | Yes |
| Execute workflow | No | Yes | Yes | Yes |
| Share/unshare workflow | No | No | Yes | Yes |

**FR-012: Workflow Access Middleware**
- New middleware `workflowTeamAccessMiddleware` checks team role against required permission
- Middleware runs after `authMiddleware` and extracts workflow's teamId
- If workflow has no teamId, falls back to ownership check (userId match)
- ADMIN system role bypasses all checks (consistent with existing pattern)

**FR-013: Seed Permission Records**
- Seed the existing `Permission` and `RolePermission` tables with the permission matrix
- Permission records: `workflow:list`, `workflow:read`, `workflow:create`, `workflow:update`, `workflow:delete`, `workflow:execute`, `workflow:share`
- RolePermission records map TeamRole to Permission entries

### 1.4 Audit Logging Extensions

**FR-014: New Audit Actions**
Add the following audit actions to `AuditAction` enum:
- `INVITATION_SENT` -- When an invitation is created
- `INVITATION_ACCEPTED` -- When an invitation is accepted
- `INVITATION_DECLINED` -- When an invitation is declined
- `INVITATION_REVOKED` -- When an invitation is revoked
- `INVITATION_EXPIRED` -- When an invitation expires (batch cleanup)
- `WORKFLOW_SHARED` -- When a workflow is associated with a team
- `WORKFLOW_UNSHARED` -- When a workflow team association is removed
- `WORKFLOW_ACCESS_DENIED` -- When a permission check fails (logged at WARN level)

**FR-015: Audit Log Query Endpoint**
- New endpoint: `GET /api/audit-logs`
- Query parameters: teamId, userId, action, startDate, endDate, page, limit
- Accessible by ADMIN system role and team OWNER/ADMIN for their teams
- Returns paginated results sorted by createdAt descending

---

## 2. Component Breakdown

### 2.1 API Components (apps/api)

| Component | Responsibility | New/Modify |
|-----------|---------------|------------|
| `TeamInvitation` Prisma model | Store invitation records | NEW |
| `invitation.schema.ts` | Zod validation for invitation endpoints | NEW |
| `invitation.controller.ts` | Handle invitation CRUD | NEW |
| `invitation.service.ts` | Token generation, expiry logic, email lookup | NEW |
| `routes/invitations.ts` | Route definitions for `/api/teams/:id/invitations` | NEW |
| `Workflow` Prisma model | Add optional teamId foreign key | MODIFY |
| `workflow.controller.ts` | Add team context to workflow CRUD | MODIFY |
| `routes/workflows.ts` | Add teamMemberMiddleware to workflow routes | MODIFY |
| `workflow-team-access.middleware.ts` | Permission check for team-scoped workflows | NEW |
| `audit.middleware.ts` | Add new AuditAction entries | MODIFY |
| `routes/audit-logs.ts` | Audit log query endpoint | NEW |
| `audit-log.controller.ts` | Handle audit log queries | NEW |
| `seed-permissions.ts` | Seed Permission/RolePermission tables | NEW |

### 2.2 Web Components (apps/web)

| Component | Responsibility | New/Modify |
|-----------|---------------|------------|
| `app/(auth)/teams/page.tsx` | Team list page | NEW |
| `app/(auth)/teams/[id]/page.tsx` | Team detail with members | NEW |
| `app/(auth)/teams/[id]/settings/page.tsx` | Team settings (name, desc) | NEW |
| `app/(auth)/teams/[id]/members/page.tsx` | Member management | NEW |
| `app/(auth)/teams/[id]/invitations/page.tsx` | Invitation management | NEW |
| `app/(auth)/teams/[id]/workflows/page.tsx` | Team workflows list | NEW |
| `app/(auth)/invitations/page.tsx` | User's pending invitations | NEW |
| `components/teams/TeamCard.tsx` | Team card for list view | NEW |
| `components/teams/InviteDialog.tsx` | Invitation creation dialog | NEW |
| `components/teams/MemberRoleSelect.tsx` | Role selection dropdown | NEW |
| `components/teams/PermissionGate.tsx` | Conditional render by permission | NEW |
| `lib/api/teams.ts` | API client for team endpoints | NEW |
| `lib/api/invitations.ts` | API client for invitation endpoints | NEW |
| Workflow list/detail pages | Add team context, permission gating | MODIFY |

### 2.3 Mastra Components (apps/mastra)

| Component | Responsibility | New/Modify |
|-----------|---------------|------------|
| Workflow execution handler | Accept and propagate teamId context | MODIFY |
| Execution audit records | Include teamId in audit metadata | MODIFY |

### 2.4 Microsandbox Components (apps/microsandbox)

| Component | Responsibility | New/Modify |
|-----------|---------------|------------|
| Audit service | Include teamId in execution audit records | MODIFY |

---

## 3. User Workflow Diagrams

### 3.1 Invitation Flow

```
Team Owner                    System                       Invitee
    |                            |                            |
    |-- Create invitation ------>|                            |
    |   (email, role)            |                            |
    |                            |-- Generate token           |
    |                            |-- Store invitation         |
    |                            |-- Log audit event          |
    |<-- 201 Created ------------|                            |
    |                            |                            |
    |                            |     (User logs in)         |
    |                            |                            |
    |                            |<-- List my invitations ----|
    |                            |-- Return pending list ---->|
    |                            |                            |
    |                            |<-- Accept invitation ------|
    |                            |   (token)                  |
    |                            |-- Validate token           |
    |                            |-- Create TeamMember        |
    |                            |-- Update invitation status |
    |                            |-- Log audit event          |
    |                            |-- 200 OK ----------------->|
```

### 3.2 Workflow Access Control Flow

```
Team Member                   API Middleware Chain                    Controller
    |                            |                                       |
    |-- GET /api/workflows/:id -->|                                      |
    |                            |-- authMiddleware (JWT)                |
    |                            |-- Extract workflow (find by ID)       |
    |                            |-- Check: has teamId?                  |
    |                            |   YES -> teamWorkflowAccessMiddleware |
    |                            |     -> Lookup TeamMember role         |
    |                            |     -> Check role >= required         |
    |                            |     -> Pass or 403                    |
    |                            |   NO -> ownershipCheck               |
    |                            |     -> userId match?                  |
    |                            |     -> Pass or 403                    |
    |                            |                                       |
    |                            |-- Forward to controller ------------->|
    |<-- 200 JSON response ------|<-- Return workflow data --------------|
```

---

## 4. State Transitions

### 4.1 Invitation States

```
                 create
    [*] ----------------------> PENDING
                                  |
                 +---------+------+------+---------+
                 |         |             |         |
              accept    decline       revoke    expire
                 |         |             |         |
                 v         v             v         v
             ACCEPTED   DECLINED     REVOKED   EXPIRED
```

Valid transitions:
- PENDING -> ACCEPTED (invitee accepts)
- PENDING -> DECLINED (invitee declines)
- PENDING -> REVOKED (team owner/admin revokes)
- PENDING -> EXPIRED (system cleanup after 48hr)

Terminal states: ACCEPTED, DECLINED, REVOKED, EXPIRED (no further transitions)

### 4.2 Workflow Team Association States

```
    [PERSONAL]  <----unshare---- [TEAM-SHARED]
        |                              ^
        |----share with team---------->|
```

- PERSONAL: workflow.teamId is null. Only owner can access.
- TEAM-SHARED: workflow.teamId is set. Team members access per role matrix.

---

## 5. Integration Specifications per App

### 5.1 API Service (apps/api)

- **Schema migration:** Add `TeamInvitation` model; add optional `teamId` to `Workflow`
- **New routes:** `/api/teams/:id/invitations`, `/api/audit-logs`
- **Modified routes:** `/api/workflows` (add team context filtering and permission checks)
- **New middleware:** `workflowTeamAccessMiddleware`
- **Modified middleware:** `audit.middleware.ts` (new action types)

### 5.2 Web Frontend (apps/web)

- **New pages:** Team management suite (list, detail, members, invitations, workflows)
- **New page:** My invitations dashboard
- **Modified pages:** Workflow list (add team filter), Workflow detail (add permission-gated UI)
- **New components:** TeamCard, InviteDialog, MemberRoleSelect, PermissionGate
- **New API clients:** Teams API, Invitations API

### 5.3 Mastra Engine (apps/mastra)

- **Modified:** Workflow execution handler to accept teamId in execution context
- **Modified:** Audit/telemetry records to include teamId metadata

### 5.4 Microsandbox (apps/microsandbox)

- **Modified:** Audit records for skill executions to include teamId when available
