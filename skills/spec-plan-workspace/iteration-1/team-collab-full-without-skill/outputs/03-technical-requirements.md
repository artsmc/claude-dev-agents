# Technical Requirements: Team Collaboration with Role-Based Permissions

**Date:** 2026-03-09
**Affected Services:** API (primary), Web (primary), Mastra (minor)

---

## 1. Database Schema Changes

### 1.1 Prisma Schema Modifications

#### Add `TeamInvitation` Model

```prisma
model TeamInvitation {
  id          String           @id @default(cuid())
  email       String           // Invitee's email address
  teamRole    TeamRole         @default(MEMBER)
  status      InvitationStatus @default(PENDING)
  token       String           @unique // Cryptographic token for accept/decline
  expiresAt   DateTime         // Default: 7 days from creation
  message     String?          @db.Text // Optional message from inviter

  // Relations
  teamId      String
  team        Team             @relation(fields: [teamId], references: [id], onDelete: Cascade)
  inviterId   String
  inviter     User             @relation("InvitedBy", fields: [inviterId], references: [id])
  inviteeId   String?          // Null until invitation is accepted or if user doesn't exist yet
  invitee     User?            @relation("InvitedTo", fields: [inviteeId], references: [id])

  // Timestamps
  createdAt   DateTime         @default(now())
  respondedAt DateTime?        // When invitation was accepted/declined

  // Indexes
  @@index([teamId])
  @@index([email])
  @@index([inviterId])
  @@index([status])
  @@index([token])
  @@index([expiresAt])
  @@unique([teamId, email, status]) // Prevent duplicate pending invitations
  @@map("team_invitations")
}

enum InvitationStatus {
  PENDING
  ACCEPTED
  DECLINED
  EXPIRED
  REVOKED
}
```

#### Modify `Workflow` Model

```prisma
model Workflow {
  // ... existing fields ...

  // Team ownership (optional - null means personal workflow)
  teamId String?
  team   Team?   @relation(fields: [teamId], references: [id], onDelete: SetNull)

  // ... existing relations ...

  // Add new index
  @@index([teamId])
}
```

#### Modify `Team` Model

```prisma
model Team {
  // ... existing fields ...

  // Add relations
  workflows   Workflow[]
  invitations TeamInvitation[]

  // ... existing relations remain ...
}
```

#### Modify `User` Model

```prisma
model User {
  // ... existing fields ...

  // Add invitation relations
  sentInvitations     TeamInvitation[] @relation("InvitedBy")
  receivedInvitations TeamInvitation[] @relation("InvitedTo")

  // ... existing relations remain ...
}
```

### 1.2 Migration Strategy

1. Create migration: `npx prisma migrate dev --name add-team-collab`
2. The migration is additive (new columns/tables only), no destructive changes
3. `teamId` on Workflow is nullable, so existing data requires no backfill
4. Deploy migration before code changes (backward compatible)

---

## 2. API Service Changes

### 2.1 New Files to Create

| File | Purpose |
|------|---------|
| `src/schemas/team-invitation.schema.ts` | Zod schemas for invitation endpoints |
| `src/controllers/team-invitation.controller.ts` | Invitation CRUD controller |
| `src/repositories/interfaces/team-invitation.repository.interface.ts` | Repository interface |
| `src/repositories/implementations/prisma-team-invitation.repository.ts` | Prisma implementation |
| `src/types/repositories/team-invitation.types.ts` | TypeScript types for invitation entities |
| `src/middleware/team-workflow-access.middleware.ts` | Team-scoped workflow authorization |
| `src/routes/team-invitations.ts` | Invitation route definitions (nested under teams) |

### 2.2 Files to Modify

| File | Changes |
|------|---------|
| `prisma/schema.prisma` | Add TeamInvitation model; add teamId to Workflow; update relations |
| `src/routes/teams.ts` | Mount invitation sub-routes |
| `src/routes/workflows.ts` | Add team-workflow-access middleware to relevant routes |
| `src/controllers/workflow.controller.ts` | Replace `assertOwnership` with team-aware authorization |
| `src/schemas/workflow.schema.ts` | Add optional `teamId` to CreateWorkflowRequestSchema |
| `src/middleware/audit.middleware.ts` | Add new AuditAction enum values for invitations and team-workflow events |
| `src/repositories/implementations/prisma-workflow.repository.ts` | Add team-scoped queries |
| `src/repositories/interfaces/workflow.repository.interface.ts` | Add team-scoped method signatures |
| `src/types/repositories/workflow.types.ts` | Add teamId to workflow types |
| `src/routes/index.ts` | No change needed (invitations mount under teams) |

### 2.3 New API Endpoints

#### Invitation Endpoints

| Method | Path | Access | Description |
|--------|------|--------|-------------|
| POST | `/api/teams/:id/invitations` | OWNER, ADMIN | Create invitation |
| GET | `/api/teams/:id/invitations` | OWNER, ADMIN | List team invitations |
| DELETE | `/api/teams/:id/invitations/:invitationId` | OWNER, ADMIN | Revoke invitation |
| POST | `/api/invitations/:token/accept` | Authenticated invitee | Accept invitation |
| POST | `/api/invitations/:token/decline` | Authenticated invitee | Decline invitation |
| GET | `/api/users/me/invitations` | Authenticated user | List my pending invitations |

#### Modified Workflow Endpoints

| Method | Path | Change |
|--------|------|--------|
| POST | `/api/workflows` | Accept optional `teamId` in body |
| GET | `/api/workflows` | Return both personal and team workflows |
| PUT | `/api/workflows/:id` | Team-aware authorization check |
| DELETE | `/api/workflows/:id` | Team-aware authorization (OWNER/ADMIN only for team workflows) |
| POST | `/api/workflows/:id/execute` | Team-aware authorization (not VIEWER) |

#### New Team-Workflow Management Endpoint

| Method | Path | Access | Description |
|--------|------|--------|-------------|
| PUT | `/api/workflows/:id/team` | Workflow owner + Team OWNER/ADMIN | Assign/unassign workflow to team |

### 2.4 Team-Workflow Access Middleware

New middleware: `teamWorkflowAccessMiddleware`

```typescript
/**
 * Middleware factory for team-scoped workflow authorization.
 *
 * Logic:
 * 1. If workflow has no teamId -> fallback to assertOwnership (existing behavior)
 * 2. If workflow has teamId -> check user's team membership + role
 * 3. System ADMIN bypasses all checks
 *
 * @param requiredMinRole - Minimum team role required ('VIEWER' | 'MEMBER' | 'ADMIN' | 'OWNER')
 * @param allowOwner - Whether the workflow creator always has access regardless of team role
 */
export function teamWorkflowAccessMiddleware(options: {
  minTeamRole: 'VIEWER' | 'MEMBER' | 'ADMIN' | 'OWNER';
  allowWorkflowOwner?: boolean;
}) { ... }
```

**Role hierarchy for permission checks:**
```
OWNER > ADMIN > MEMBER > VIEWER
```

A check for `minTeamRole: 'MEMBER'` grants access to MEMBER, ADMIN, and OWNER.

### 2.5 Invitation Zod Schemas

```typescript
// CreateInvitationSchema
{
  email: z.string().email(),
  teamRole: z.enum(['ADMIN', 'MEMBER', 'VIEWER']).default('MEMBER'),  // Cannot invite as OWNER
  message: z.string().max(500).optional(),
}

// InvitationTokenParamsSchema
{
  token: z.string().min(32).max(64),
}

// ListInvitationsQuerySchema
{
  status: z.enum(['PENDING', 'ACCEPTED', 'DECLINED', 'EXPIRED', 'REVOKED']).optional(),
  page: z.number().int().min(1).default(1),
  limit: z.number().int().min(1).max(100).default(20),
}
```

---

## 3. Web Frontend Changes

### 3.1 New Pages

| Page Route | Component | Description |
|------------|-----------|-------------|
| `/teams` | `TeamsListPage` | List all user's teams with member counts |
| `/teams/[id]` | `TeamDetailPage` | Team overview with tabs: Workflows, Members, Invitations, Settings |
| `/teams/[id]/workflows` | `TeamWorkflowsTab` | Team-scoped workflow list |
| `/teams/[id]/members` | `TeamMembersTab` | Member list with role management |
| `/teams/[id]/invitations` | `TeamInvitationsTab` | Pending/historical invitations |
| `/teams/[id]/settings` | `TeamSettingsTab` | Team name, description, danger zone (delete) |

### 3.2 New Components

| Component | Description |
|-----------|-------------|
| `InviteMemberDialog` | Modal dialog for inviting by email with role selection |
| `MemberRoleDropdown` | Dropdown to change a member's role (with permissions) |
| `TeamRoleBadge` | Visual badge showing OWNER/ADMIN/MEMBER/VIEWER |
| `InvitationList` | List of pending/sent invitations with status |
| `InvitationBanner` | Top-level notification for pending invitations |
| `TeamSelector` | Dropdown for selecting a team when creating workflows |
| `WorkflowTeamAssignment` | UI for assigning/unassigning a workflow to a team |
| `PermissionGate` | React component that conditionally renders children based on team role |

### 3.3 Modified Components

| Component | Changes |
|-----------|---------|
| Workflow list page | Add team context, show team badge on team workflows |
| Workflow detail page | Show team info, respect role-based UI |
| Workflow create form | Add optional team selector |
| Navigation sidebar | Add teams section with pending invitation count |
| Dashboard | Show team activity feed |

### 3.4 New API Proxy Routes (Next.js)

| Route | Maps To |
|-------|---------|
| `/api/teams/[id]/invitations` | `POST /api/teams/:id/invitations` |
| `/api/teams/[id]/members` | `GET/POST/PUT/DELETE` |
| `/api/invitations/[token]/accept` | `POST /api/invitations/:token/accept` |
| `/api/invitations/[token]/decline` | `POST /api/invitations/:token/decline` |
| `/api/users/me/invitations` | `GET` |

### 3.5 State Management

| Store | Type | Purpose |
|-------|------|---------|
| `useTeamsQuery` | TanStack Query | Fetch and cache team list |
| `useTeamDetailQuery` | TanStack Query | Fetch team with members |
| `useTeamWorkflowsQuery` | TanStack Query | Fetch team-scoped workflows |
| `useInvitationsQuery` | TanStack Query | Fetch user's pending invitations |
| `useActiveTeamStore` | Zustand | Track currently selected team context |

---

## 4. Mastra Service Changes (Minor)

### 4.1 Workflow Execution Context

When the API triggers workflow execution via Mastra, include `teamId` in the execution metadata:

```typescript
// mastra.service.ts - executeWorkflow()
const mastraResponse = await mastraService.executeWorkflow({
  workflowId: workflow.id,
  input,
  metadata: {
    teamId: workflow.teamId,  // NEW: include team context
    triggeredBy: user.userId,
  }
}, req.rawToken);
```

No other Mastra changes required for Phase 1.

---

## 5. Audit Logging Additions

### 5.1 New AuditAction Values

```typescript
export enum AuditAction {
  // ... existing values ...

  // Invitation Events
  INVITATION_CREATED = 'INVITATION_CREATED',
  INVITATION_ACCEPTED = 'INVITATION_ACCEPTED',
  INVITATION_DECLINED = 'INVITATION_DECLINED',
  INVITATION_REVOKED = 'INVITATION_REVOKED',
  INVITATION_EXPIRED = 'INVITATION_EXPIRED',

  // Team-Workflow Events
  WORKFLOW_ASSIGNED_TO_TEAM = 'WORKFLOW_ASSIGNED_TO_TEAM',
  WORKFLOW_REMOVED_FROM_TEAM = 'WORKFLOW_REMOVED_FROM_TEAM',
  TEAM_WORKFLOW_VIEWED = 'TEAM_WORKFLOW_VIEWED',
  TEAM_WORKFLOW_EDITED = 'TEAM_WORKFLOW_EDITED',
  TEAM_WORKFLOW_DELETED = 'TEAM_WORKFLOW_DELETED',
  TEAM_WORKFLOW_EXECUTED = 'TEAM_WORKFLOW_EXECUTED',
}
```

### 5.2 Audit Detail Schemas

All team-related audit entries MUST include `teamId` in the `details` JSON field:

```json
{
  "teamId": "cuid_xxx",
  "workflowId": "cuid_yyy",
  "action": "edit",
  "changedFields": ["name", "definition"],
  "performedBy": "cuid_zzz",
  "teamRole": "MEMBER"
}
```

---

## 6. Security Considerations

### 6.1 Invitation Token Generation

```typescript
import crypto from 'crypto';

function generateInvitationToken(): string {
  return crypto.randomBytes(32).toString('hex'); // 64 character hex string
}
```

### 6.2 Authorization Check Order

For team-scoped workflows, authorization checks follow this order:

1. **Authentication**: JWT valid? (authMiddleware)
2. **System Role**: Is user ADMIN? (bypass all) (existing RBAC)
3. **Workflow Owner**: Is user the workflow creator? (preserve backward compat)
4. **Team Membership**: Is user a member of the workflow's team?
5. **Team Role**: Does user's team role meet the minimum required role?

### 6.3 Rate Limiting

- Invitation creation: Max 20 invitations per team per hour
- Invitation acceptance: Max 10 per user per minute (prevent spam-accept attacks)

---

## 7. Migration Path & Backward Compatibility

### 7.1 Database Migration

- `teamId` on Workflow is NULLABLE with default NULL
- Existing workflows remain personal (userId-scoped)
- No data loss or behavioral change for existing features

### 7.2 API Backward Compatibility

- All existing API endpoints maintain their current behavior
- New `teamId` parameter in workflow creation is OPTIONAL
- Existing workflow queries continue to work (personal + team workflows returned)
- No breaking changes to the API contract

### 7.3 Frontend Backward Compatibility

- Existing workflow pages continue to work
- Team features are additive (new pages/tabs)
- No changes to authentication flow
