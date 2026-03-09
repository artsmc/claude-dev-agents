# Feature Requirements Document: Team Collaboration with Role-Based Permissions

**Feature ID:** TEAM-COLLAB-001
**Date:** 2026-03-09
**Priority:** P0 (Core Platform Feature)
**Affected Apps:** API, Web, Mastra (minor)

---

## 1. Executive Summary

This feature extends AIForge's existing team infrastructure to enable true team collaboration on workflows. Team owners can invite members via email, assign granular roles (VIEWER, MEMBER/Editor, ADMIN, OWNER), and control who can edit workflows versus who can only view them. All actions are audit-logged for FedRAMP Moderate compliance.

The platform already has the foundational team management (CRUD, member management, role-based access middleware, audit logging). This feature builds on that foundation to add: (1) workflow-team association, (2) an invitation system, (3) resource-level permission enforcement, and (4) frontend UI for all of the above.

---

## 2. User Stories

### 2.1 Team Owner Stories

| ID | Story | Acceptance Criteria |
|----|-------|-------------------|
| US-01 | As a team owner, I want to invite users to my team by email so they can collaborate on workflows | Email invitation sent; pending invitation visible; invitee can accept/decline |
| US-02 | As a team owner, I want to assign roles when inviting so I control access levels from the start | Role selection during invite; default role is MEMBER |
| US-03 | As a team owner, I want to change member roles after they join so I can adjust permissions as needed | Role dropdown on member list; immediate effect; audit logged |
| US-04 | As a team owner, I want to remove members so I can revoke access when needed | Remove button; confirmation dialog; cascading access revocation; audit logged |
| US-05 | As a team owner, I want to transfer ownership so another person can manage the team | Transfer ownership flow; cannot leave as last owner; audit logged |
| US-06 | As a team owner, I want to assign workflows to my team so members can collaborate on them | Team selector when creating/editing workflows; existing user workflows can be moved |

### 2.2 Team Admin Stories

| ID | Story | Acceptance Criteria |
|----|-------|-------------------|
| US-07 | As a team admin, I want to invite members so I can help manage the team | Same invite flow as owner except cannot assign OWNER role |
| US-08 | As a team admin, I want to manage member roles (except OWNER) so I can help with team governance | Can change roles up to ADMIN; cannot demote owners |
| US-09 | As a team admin, I want to assign/unassign workflows to the team | Can set teamId on workflows they own or that belong to the team |

### 2.3 Team Member (Editor) Stories

| ID | Story | Acceptance Criteria |
|----|-------|-------------------|
| US-10 | As a team member, I want to view all team workflows so I can find relevant work | Team workflows tab visible; full list with search/filter |
| US-11 | As a team member, I want to edit team workflows so I can collaborate on them | Edit button visible; can modify name, description, definition; audit logged |
| US-12 | As a team member, I want to execute team workflows so I can test my changes | Execute button visible; execution tracked with team context |
| US-13 | As a team member, I want to create workflows within my team context | Team auto-selected when creating from team view |

### 2.4 Team Viewer Stories

| ID | Story | Acceptance Criteria |
|----|-------|-------------------|
| US-14 | As a viewer, I want to view team workflows so I can understand what the team is building | Workflow list and detail pages accessible; read-only |
| US-15 | As a viewer, I want to view workflow execution history so I can monitor status | Execution list visible; cannot trigger new executions |
| US-16 | As a viewer, I should NOT be able to edit or execute workflows | Edit/execute buttons hidden; API returns 403 if attempted |

### 2.5 Invited User Stories

| ID | Story | Acceptance Criteria |
|----|-------|-------------------|
| US-17 | As an invited user, I want to see my pending invitations so I can accept them | Invitation badge/notification; invitation list page |
| US-18 | As an invited user, I want to accept an invitation to join a team | One-click accept; immediately gain access; audit logged |
| US-19 | As an invited user, I want to decline an invitation I don't want | One-click decline; invitation removed; inviter can see status |

### 2.6 Compliance Stories

| ID | Story | Acceptance Criteria |
|----|-------|-------------------|
| US-20 | As a compliance officer, I want all team permission changes audit-logged | Every role change, member add/remove, invitation event creates AuditLog entry |
| US-21 | As a compliance officer, I want workflow access within teams audit-logged | Every view, edit, delete, execute on team workflows logged with team context |
| US-22 | As a compliance officer, I want to query audit logs by team | Audit log filtering by teamId (future: audit dashboard) |

---

## 3. Functional Requirements

### 3.1 Team-Workflow Association

**FR-01:** Workflows MUST support optional team ownership via a `teamId` foreign key.

**FR-02:** When a workflow has a `teamId`, access control MUST be based on the user's team role:
- OWNER, ADMIN: Full CRUD + execute
- MEMBER: Read + edit + execute (NOT delete)
- VIEWER: Read only

**FR-03:** When a workflow has no `teamId`, the existing user-ownership model (`userId`) applies unchanged.

**FR-04:** A workflow MUST always have a `userId` (creator) regardless of team association.

**FR-05:** Workflow listing MUST include both personal workflows and team workflows the user has access to.

**FR-06:** Admins and Owners can move their personal workflows into a team (set `teamId`).

### 3.2 Invitation System

**FR-07:** Team OWNER and ADMIN roles can create invitations.

**FR-08:** Invitations MUST include: inviter user ID, invitee email, team ID, proposed role, status, expiration.

**FR-09:** Invitation statuses: PENDING, ACCEPTED, DECLINED, EXPIRED, REVOKED.

**FR-10:** Invitations MUST expire after 7 days (configurable).

**FR-11:** If the invitee email matches an existing user, the invitation links directly. If not, the invitation is stored and resolved upon user registration.

**FR-12:** A user CANNOT be invited if they are already a team member.

**FR-13:** A user CANNOT have duplicate pending invitations to the same team.

**FR-14:** Invitations can be revoked by OWNER or ADMIN before acceptance.

### 3.3 Permission Enforcement

**FR-15:** The `teamMemberMiddleware` MUST be extended or complemented with resource-level permission checking.

**FR-16:** Permission matrix:

| Action | OWNER | ADMIN | MEMBER | VIEWER |
|--------|-------|-------|--------|--------|
| View team details | Y | Y | Y | Y |
| Edit team settings | Y | Y | N | N |
| Delete team | Y | N | N | N |
| Invite members | Y | Y | N | N |
| Remove members | Y | Y | N | N |
| Change roles | Y | Y (not OWNER) | N | N |
| View team workflows | Y | Y | Y | Y |
| Create team workflows | Y | Y | Y | N |
| Edit team workflows | Y | Y | Y | N |
| Delete team workflows | Y | Y | N | N |
| Execute team workflows | Y | Y | Y | N |
| View execution history | Y | Y | Y | Y |

**FR-17:** System-level ADMIN role (from the `Role` enum) bypasses all team permission checks (existing behavior maintained).

### 3.4 Audit Logging

**FR-18:** The following events MUST be audit-logged:
- Invitation created (inviter, invitee email, proposed role)
- Invitation accepted (by whom)
- Invitation declined (by whom)
- Invitation revoked (by whom)
- Invitation expired (system event)
- Workflow assigned to team (by whom, old owner, new team)
- Workflow removed from team (by whom)
- Team workflow viewed (viewer, workflow ID, team ID)
- Team workflow edited (editor, workflow ID, changes summary)
- Team workflow deleted (deleter, workflow ID)
- Team workflow executed (executor, workflow ID, execution ID)

**FR-19:** Audit log entries MUST include: userId, action, resource, resourceId, teamId (in details JSON), ipAddress, userAgent, timestamp.

**FR-20:** Audit logs MUST be immutable (append-only, no updates or deletes).

---

## 4. Non-Functional Requirements

### 4.1 Performance

**NFR-01:** Team membership checks (middleware) MUST complete within 50ms for cached results.

**NFR-02:** Workflow listing with team context MUST not degrade beyond 200ms for teams with up to 100 members and 1000 workflows.

### 4.2 Security

**NFR-03:** All permission checks MUST be enforced server-side regardless of frontend state.

**NFR-04:** Invitation tokens MUST be cryptographically random (minimum 32 bytes).

**NFR-05:** Invitation acceptance MUST be idempotent (double-accept does not create duplicate membership).

**NFR-06:** PII (email addresses in invitations) MUST NOT appear in application logs.

### 4.3 Compliance

**NFR-07:** All audit events MUST follow NIST 800-53 AU-2 (auditable events) and AU-3 (content of audit records).

**NFR-08:** Audit logs MUST support 7-year retention per AU-11.

**NFR-09:** Role changes MUST satisfy AC-2 (account management) controls.

### 4.4 Scalability

**NFR-10:** A team can have up to 500 members.

**NFR-11:** A team can own up to 10,000 workflows.

---

## 5. Out of Scope (Phase 1)

- Email delivery for invitations (invitations are API-only; email notifications deferred)
- Team-scoped skills (same pattern, Phase 2)
- Team-scoped agents (already has teamId FK but no permission enforcement)
- Audit log dashboard/query UI
- Team billing or quota management
- Cross-team workflow sharing
- SSO-based auto-team-assignment
