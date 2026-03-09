# Feature Requirements Document: Team Collaboration with Role-Based Permissions

**Feature ID:** FEAT-TEAM-COLLAB-001
**Version:** 1.0
**Date:** 2026-03-09
**Status:** Draft
**Tier:** Full

---

## 1. Business Objectives

### 1.1 Problem Statement

AIForge users currently operate in isolation. Workflows, agents, and skills are owned by individual users with no mechanism for collaborative access. Enterprise and government customers require:

- Shared access to workflows within organizational teams
- Fine-grained control over who can view versus edit resources
- Complete audit trails of all permission changes for FedRAMP compliance
- An invitation-based onboarding flow for adding team members

### 1.2 Business Goals

1. **Enable team-based collaboration** -- Allow organizations to form teams and share workflows with controlled access levels.
2. **Enforce least-privilege access** -- Ensure users only have the minimum permissions needed, satisfying NIST 800-53 AC-6.
3. **Maintain compliance posture** -- Log all authorization events (invitations, role changes, access grants/revocations) per NIST 800-53 AU-2.
4. **Improve user retention** -- Teams that collaborate are stickier than individual users.

### 1.3 Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Team creation rate | >30% of active organizations create 1+ team within 30 days | Analytics |
| Invitation acceptance rate | >70% of invitations accepted within 48 hours | Audit log query |
| Workflow sharing adoption | >50% of teams share 1+ workflow within 14 days of team creation | Database query |
| Audit completeness | 100% of permission-related events logged | Audit log verification |
| Permission check latency | <10ms p95 added latency per request | APM monitoring |

---

## 2. User Stories

### US-001: Team Owner Invites a Member

**As a** team owner,
**I want to** invite a user by email to join my team with a specific role,
**So that** I can onboard collaborators with the right level of access.

**Acceptance Criteria:**
- Owner can enter an email address and select a role (Viewer, Editor, Admin)
- System sends an invitation (or creates a pending invitation record)
- Invitation expires after 48 hours if not accepted
- Invitation token is single-use and cryptographically random
- Duplicate invitations to the same email for the same team are rejected
- Audit log records: inviter, invitee email, assigned role, timestamp, IP

### US-002: User Accepts a Team Invitation

**As a** registered user who received a team invitation,
**I want to** accept the invitation and join the team,
**So that** I can access shared resources.

**Acceptance Criteria:**
- User sees pending invitations in their dashboard or navigates via invitation link
- Accepting adds the user as a team member with the role specified in the invitation
- Expired invitations show a clear error message
- Already-accepted invitations show "already joined" status
- Audit log records: acceptance event with user ID, team ID, role

### US-003: Team Admin Assigns Roles

**As a** team owner or admin,
**I want to** change a team member's role (Viewer, Editor, Admin),
**So that** I can adjust access levels as responsibilities change.

**Acceptance Criteria:**
- Owner can change any member's role, including promoting to Admin
- Admin can change roles of Members and Viewers but cannot promote to Owner
- Role changes take effect immediately on subsequent requests
- Last owner cannot be demoted (protected)
- Audit log records: old role, new role, changed by, timestamp

### US-004: Workflow Access Control by Team Role

**As a** team member with Viewer role,
**I want to** see shared team workflows but not edit them,
**So that** I can review work without accidentally modifying it.

**Acceptance Criteria:**
- Viewer: Can list and view team workflows (read-only). Cannot create, edit, or delete.
- Editor (Member): Can list, view, create, and edit team workflows. Cannot delete.
- Admin: Can list, view, create, edit, and delete team workflows. Can manage members.
- Owner: Full access including team settings, deletion, and ownership transfer.
- Personal workflows remain private unless explicitly shared with a team.
- UI disables edit controls for users without edit permission.

### US-005: Audit Log for Compliance

**As a** compliance officer,
**I want to** query audit logs for all team-related permission events,
**So that** I can demonstrate FedRAMP compliance during audits.

**Acceptance Criteria:**
- All team operations are logged: creation, updates, deletion
- All membership operations are logged: invitation sent, accepted, declined, revoked
- All role changes are logged: old role, new role, actor
- All workflow access control events are logged: share, unshare, access denied
- Logs include: actor user ID, target resource ID, action, timestamp, IP address, user agent
- Logs are queryable by date range, team ID, user ID, and action type
- No PII (names, emails) stored in audit log details field

---

## 3. Edge Cases and Error Scenarios

### 3.1 Invitation Edge Cases
- **Invite non-existent user:** Create pending invitation record; if user later registers with that email, show pending invitations on first login.
- **Invite already-member user:** Return 409 Conflict with clear message.
- **Invite self:** Return 400 Bad Request (owner is already a member).
- **Invitation token reuse:** Return 410 Gone (token already consumed).
- **Invitation expiry:** Return 410 Gone with message "Invitation expired. Please ask the team owner to send a new invitation."

### 3.2 Role Change Edge Cases
- **Demote last owner:** Return 403 Forbidden. Team must always have at least one owner.
- **Admin promotes to Owner:** Return 403 Forbidden. Only owners can create new owners.
- **Change own role:** Owners can demote themselves only if another owner exists.
- **Concurrent role changes:** Use optimistic locking or database-level constraint.

### 3.3 Workflow Access Edge Cases
- **User removed from team:** Immediately lose access to team workflows. In-progress edits should save (graceful degradation).
- **Team deleted:** All shared workflows revert to individual ownership (the original creator).
- **Workflow transferred to team:** Original creator retains ownership; team members gain access per role.
- **Viewer attempts edit via API:** Return 403 Forbidden regardless of UI state (server-side enforcement).

---

## 4. Dependencies and Assumptions

### 4.1 Dependencies
- Existing Team/TeamMember Prisma models (in place)
- Existing audit middleware and service (in place)
- Existing team-access middleware (in place, needs extension)
- Email service for invitation delivery (NOT in place -- needed or use in-app only)

### 4.2 Assumptions
- Initial implementation uses in-app invitation (no email sending required for MVP)
- The existing `TeamRole` enum (OWNER, ADMIN, MEMBER, VIEWER) maps directly to the requested roles: Owner=OWNER, Admin=ADMIN, Editor=MEMBER, Viewer=VIEWER
- Workflows are the primary resource for team-based access control (agents already have team access)
- The existing `Permission`/`RolePermission` models will be activated and seeded for resource-level permissions

### 4.3 Out of Scope (v1)
- Email-based invitation delivery (v1 uses in-app invitation links)
- Cross-team workflow sharing (workflows belong to exactly one team)
- Custom permission definitions (fixed role-permission matrix)
- Ownership transfer ceremony (owner can promote another member to owner)
- Real-time collaboration (concurrent editing, presence indicators)
