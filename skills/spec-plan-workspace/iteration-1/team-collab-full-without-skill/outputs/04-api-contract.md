# API Contract Specification: Team Collaboration Endpoints

**Date:** 2026-03-09
**Base URL:** `/api`
**Authentication:** All endpoints require `Authorization: Bearer <JWT>` unless noted

---

## 1. Invitation Management Endpoints

### 1.1 Create Invitation

```
POST /api/teams/:id/invitations
```

**Access:** Team OWNER or ADMIN

**Request Body:**
```json
{
  "email": "user@example.com",
  "teamRole": "MEMBER",
  "message": "Join our engineering team!"
}
```

| Field | Type | Required | Default | Validation |
|-------|------|----------|---------|------------|
| email | string | Yes | - | Valid email format |
| teamRole | enum | No | MEMBER | ADMIN, MEMBER, VIEWER (not OWNER) |
| message | string | No | null | Max 500 characters |

**Success Response (201):**
```json
{
  "id": "cjld2cyuq0000t3rmniod1foy",
  "email": "user@example.com",
  "teamRole": "MEMBER",
  "status": "PENDING",
  "message": "Join our engineering team!",
  "teamId": "cjld2cyuq0001t3rmniod1foz",
  "teamName": "Engineering Team",
  "inviterId": "cjld2cyuq0002t3rmniod1fo0",
  "inviterName": "John Doe",
  "expiresAt": "2026-03-16T00:00:00.000Z",
  "createdAt": "2026-03-09T00:00:00.000Z"
}
```

**Error Responses:**

| Status | Condition |
|--------|-----------|
| 400 | Invalid email format; invalid role; message too long |
| 403 | User is not OWNER or ADMIN of the team |
| 404 | Team not found |
| 409 | User already a member of the team; pending invitation already exists |

**Audit Event:** `INVITATION_CREATED`

---

### 1.2 List Team Invitations

```
GET /api/teams/:id/invitations?status=PENDING&page=1&limit=20
```

**Access:** Team OWNER or ADMIN

**Query Parameters:**

| Param | Type | Required | Default | Options |
|-------|------|----------|---------|---------|
| status | enum | No | all | PENDING, ACCEPTED, DECLINED, EXPIRED, REVOKED |
| page | integer | No | 1 | Min: 1 |
| limit | integer | No | 20 | Min: 1, Max: 100 |

**Success Response (200):**
```json
{
  "data": [
    {
      "id": "cjld2cyuq0000t3rmniod1foy",
      "email": "user@example.com",
      "teamRole": "MEMBER",
      "status": "PENDING",
      "message": "Join our engineering team!",
      "inviterId": "cjld2cyuq0002t3rmniod1fo0",
      "inviterName": "John Doe",
      "inviteeId": null,
      "expiresAt": "2026-03-16T00:00:00.000Z",
      "createdAt": "2026-03-09T00:00:00.000Z",
      "respondedAt": null
    }
  ],
  "pagination": {
    "total": 5,
    "page": 1,
    "limit": 20,
    "totalPages": 1
  }
}
```

---

### 1.3 Revoke Invitation

```
DELETE /api/teams/:id/invitations/:invitationId
```

**Access:** Team OWNER or ADMIN

**Success Response (204):** No content

**Error Responses:**

| Status | Condition |
|--------|-----------|
| 403 | Not OWNER or ADMIN |
| 404 | Invitation not found or does not belong to team |
| 409 | Invitation already accepted/declined |

**Audit Event:** `INVITATION_REVOKED`

---

### 1.4 Accept Invitation

```
POST /api/invitations/:token/accept
```

**Access:** Authenticated user whose email matches the invitation

**Request Body:** None

**Success Response (200):**
```json
{
  "teamId": "cjld2cyuq0001t3rmniod1foz",
  "teamName": "Engineering Team",
  "teamRole": "MEMBER",
  "joinedAt": "2026-03-09T12:00:00.000Z"
}
```

**Error Responses:**

| Status | Condition |
|--------|-----------|
| 400 | Invitation expired or already responded |
| 403 | Authenticated user's email does not match invitation email |
| 404 | Invalid token |
| 409 | User is already a member of the team |

**Audit Event:** `INVITATION_ACCEPTED`

---

### 1.5 Decline Invitation

```
POST /api/invitations/:token/decline
```

**Access:** Authenticated user whose email matches the invitation

**Request Body:** None

**Success Response (200):**
```json
{
  "status": "DECLINED"
}
```

**Error Responses:** Same as accept.

**Audit Event:** `INVITATION_DECLINED`

---

### 1.6 List My Pending Invitations

```
GET /api/users/me/invitations?page=1&limit=20
```

**Access:** Authenticated user

**Success Response (200):**
```json
{
  "data": [
    {
      "id": "cjld2cyuq0000t3rmniod1foy",
      "teamId": "cjld2cyuq0001t3rmniod1foz",
      "teamName": "Engineering Team",
      "teamRole": "MEMBER",
      "message": "Join our engineering team!",
      "inviterName": "John Doe",
      "token": "abc123...",
      "expiresAt": "2026-03-16T00:00:00.000Z",
      "createdAt": "2026-03-09T00:00:00.000Z"
    }
  ],
  "pagination": {
    "total": 2,
    "page": 1,
    "limit": 20,
    "totalPages": 1
  }
}
```

---

## 2. Modified Workflow Endpoints

### 2.1 Create Workflow (Modified)

```
POST /api/workflows
```

**Request Body (Updated):**
```json
{
  "name": "Data Pipeline",
  "description": "ETL workflow for user data",
  "definition": { "nodes": [], "edges": [] },
  "teamId": "cjld2cyuq0001t3rmniod1foz"
}
```

| Field | Type | Required | Default | Notes |
|-------|------|----------|---------|-------|
| name | string | Yes | - | 1-100 chars |
| description | string | No | null | Max 500 chars |
| definition | object | No | {} | Workflow DAG |
| **teamId** | **string** | **No** | **null** | **NEW: Team CUID. User must be MEMBER+ in team** |

**Authorization for teamId:**
- If `teamId` is provided, user must be at least MEMBER in that team
- If `teamId` is null/omitted, personal workflow (existing behavior)

**Audit Event:** `WORKFLOW_CREATED` (with `teamId` in details if team workflow)

---

### 2.2 List Workflows (Modified)

```
GET /api/workflows?page=1&limit=20&teamId=xxx
```

**New Query Parameter:**

| Param | Type | Required | Default | Notes |
|-------|------|----------|---------|-------|
| teamId | string | No | null | Filter by team. If omitted, returns personal + all team workflows |

**Behavior Changes:**
- Without `teamId`: Returns user's personal workflows AND all team workflows they have access to
- With `teamId`: Returns only workflows belonging to that specific team (user must be a member)

**Response (Updated) -- new field on each workflow:**
```json
{
  "data": [
    {
      "id": "cuid_xxx",
      "name": "Data Pipeline",
      "description": "...",
      "status": "DRAFT",
      "userId": "cuid_yyy",
      "teamId": "cuid_zzz",
      "teamName": "Engineering Team",
      "myTeamRole": "MEMBER",
      "createdAt": "2026-03-09T00:00:00.000Z",
      "updatedAt": "2026-03-09T00:00:00.000Z"
    }
  ],
  "pagination": { ... }
}
```

---

### 2.3 Update Workflow (Modified Authorization)

```
PUT /api/workflows/:id
```

**Authorization Changes:**
- Personal workflow: Owner or ADMIN (unchanged)
- Team workflow: Team MEMBER, ADMIN, or OWNER (NEW)
- System ADMIN: Always allowed (unchanged)

**Audit Event:** `TEAM_WORKFLOW_EDITED` (if team workflow)

---

### 2.4 Delete Workflow (Modified Authorization)

```
DELETE /api/workflows/:id
```

**Authorization Changes:**
- Personal workflow: Owner or ADMIN (unchanged)
- Team workflow: Team ADMIN or OWNER only (MEMBER cannot delete)
- System ADMIN: Always allowed (unchanged)

**Audit Event:** `TEAM_WORKFLOW_DELETED` (if team workflow)

---

### 2.5 Execute Workflow (Modified Authorization)

```
POST /api/workflows/:id/execute
```

**Authorization Changes:**
- Personal workflow: Owner or ADMIN (unchanged)
- Team workflow: Team MEMBER, ADMIN, or OWNER (VIEWER cannot execute)
- System ADMIN: Always allowed (unchanged)

**Audit Event:** `TEAM_WORKFLOW_EXECUTED` (if team workflow)

---

## 3. Team-Workflow Assignment Endpoint (New)

### 3.1 Assign/Unassign Workflow to Team

```
PUT /api/workflows/:id/team
```

**Access:** Workflow creator who is also OWNER or ADMIN of the target team

**Request Body:**
```json
{
  "teamId": "cjld2cyuq0001t3rmniod1foz"
}
```

To unassign from team:
```json
{
  "teamId": null
}
```

**Success Response (200):**
```json
{
  "id": "cuid_xxx",
  "name": "Data Pipeline",
  "teamId": "cjld2cyuq0001t3rmniod1foz",
  "teamName": "Engineering Team",
  "updatedAt": "2026-03-09T12:00:00.000Z"
}
```

**Error Responses:**

| Status | Condition |
|--------|-----------|
| 403 | User is not workflow owner; or not OWNER/ADMIN in target team |
| 404 | Workflow not found; team not found |

**Audit Event:** `WORKFLOW_ASSIGNED_TO_TEAM` or `WORKFLOW_REMOVED_FROM_TEAM`

---

## 4. Error Response Format

All error responses follow RFC 7807 Problem Details (existing pattern):

```json
{
  "type": "https://api.productforge.dev/errors/forbidden",
  "title": "Forbidden",
  "status": 403,
  "detail": "Insufficient team permissions. Required: MEMBER, ADMIN, or OWNER",
  "instance": "/api/workflows/cuid_xxx"
}
```
