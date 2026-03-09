# Gherkin Specification: Team Collaboration with Role-Based Permissions

**Document ID:** GS-TEAM-COLLAB-001
**Version:** 1.0
**Date:** 2026-03-09
**Status:** Draft

---

## Feature: Team Invitation System

### Background

```gherkin
Background:
  Given a registered user "Alice" with role "USER"
  And Alice owns a team "Engineering" with slug "engineering"
  And a registered user "Bob" with role "USER" and email "bob@example.com"
  And a registered user "Carol" with role "USER" and email "carol@example.com"
```

### Scenario: Team owner creates an invitation (FR-001)

```gherkin
Scenario: Team owner creates a valid invitation
  Given Alice is authenticated
  And Alice has team role "OWNER" on team "Engineering"
  When Alice sends POST /api/teams/{teamId}/invitations with:
    | email             | role   |
    | bob@example.com   | MEMBER |
  Then the response status is 201
  And the response contains an invitation with status "PENDING"
  And the invitation has a non-empty token
  And the invitation expires in 48 hours
  And an audit log entry exists with action "INVITATION_SENT"
```

### Scenario: Duplicate invitation rejected (FR-001)

```gherkin
Scenario: Duplicate active invitation is rejected
  Given Alice is authenticated
  And a pending invitation exists for "bob@example.com" on team "Engineering"
  When Alice sends POST /api/teams/{teamId}/invitations with:
    | email             | role   |
    | bob@example.com   | MEMBER |
  Then the response status is 409
  And the response detail contains "already has a pending invitation"
```

### Scenario: Invite already-member user rejected (FR-001)

```gherkin
Scenario: Invitation to existing member is rejected
  Given Alice is authenticated
  And Bob is already a member of team "Engineering"
  When Alice sends POST /api/teams/{teamId}/invitations with:
    | email             | role   |
    | bob@example.com   | MEMBER |
  Then the response status is 409
  And the response detail contains "already a member"
```

### Scenario: Viewer cannot create invitations (FR-001)

```gherkin
Scenario: Viewer is forbidden from creating invitations
  Given Carol is authenticated
  And Carol has team role "VIEWER" on team "Engineering"
  When Carol sends POST /api/teams/{teamId}/invitations with:
    | email             | role   |
    | bob@example.com   | MEMBER |
  Then the response status is 403
```

### Scenario: List team invitations (FR-002)

```gherkin
Scenario: Team admin lists pending invitations
  Given Alice is authenticated
  And 3 pending invitations exist for team "Engineering"
  When Alice sends GET /api/teams/{teamId}/invitations
  Then the response status is 200
  And the response contains 3 invitations
  And each invitation includes "email", "role", "status", "expiresAt"
```

### Scenario: Revoke an invitation (FR-003)

```gherkin
Scenario: Team owner revokes a pending invitation
  Given Alice is authenticated
  And a pending invitation with id "inv-123" exists for team "Engineering"
  When Alice sends DELETE /api/teams/{teamId}/invitations/inv-123
  Then the response status is 204
  And the invitation status is "REVOKED"
  And an audit log entry exists with action "INVITATION_REVOKED"
```

---

## Feature: Accept and Decline Invitations

### Scenario: User lists their pending invitations (FR-004)

```gherkin
Scenario: User sees their pending invitations
  Given Bob is authenticated
  And a pending invitation exists for "bob@example.com" on team "Engineering"
  And a pending invitation exists for "bob@example.com" on team "Design"
  When Bob sends GET /api/invitations/mine
  Then the response status is 200
  And the response contains 2 invitations
  And each invitation includes "teamName", "inviterName", "role", "expiresAt"
```

### Scenario: User accepts an invitation (FR-005)

```gherkin
Scenario: User accepts a valid invitation
  Given Bob is authenticated
  And a pending invitation exists for "bob@example.com" on team "Engineering" with role "MEMBER"
  When Bob sends POST /api/invitations/{token}/accept
  Then the response status is 200
  And Bob is a member of team "Engineering" with role "MEMBER"
  And the invitation status is "ACCEPTED"
  And an audit log entry exists with action "INVITATION_ACCEPTED"
```

### Scenario: Accept expired invitation fails (FR-005)

```gherkin
Scenario: Accepting an expired invitation returns error
  Given Bob is authenticated
  And an expired invitation exists for "bob@example.com" on team "Engineering"
  When Bob sends POST /api/invitations/{token}/accept
  Then the response status is 410
  And the response detail contains "expired"
```

### Scenario: Accept already-used invitation fails (FR-005)

```gherkin
Scenario: Accepting an already-accepted invitation returns error
  Given Bob is authenticated
  And an accepted invitation exists for "bob@example.com" on team "Engineering"
  When Bob sends POST /api/invitations/{token}/accept
  Then the response status is 410
  And the response detail contains "already"
```

### Scenario: User declines an invitation (FR-006)

```gherkin
Scenario: User declines a pending invitation
  Given Bob is authenticated
  And a pending invitation exists for "bob@example.com" on team "Engineering"
  When Bob sends POST /api/invitations/{token}/decline
  Then the response status is 200
  And the invitation status is "DECLINED"
  And Bob is NOT a member of team "Engineering"
  And an audit log entry exists with action "INVITATION_DECLINED"
```

### Scenario: Wrong user cannot accept another's invitation (FR-005)

```gherkin
Scenario: User cannot accept invitation sent to different email
  Given Carol is authenticated with email "carol@example.com"
  And a pending invitation exists for "bob@example.com" on team "Engineering"
  When Carol sends POST /api/invitations/{token}/accept
  Then the response status is 403
  And the response detail contains "not intended for you"
```

---

## Feature: Workflow Team Association

### Background

```gherkin
Background:
  Given a team "Engineering" with the following members:
    | user    | role    |
    | Alice   | OWNER   |
    | Bob     | ADMIN   |
    | Carol   | MEMBER  |
    | Dave    | VIEWER  |
  And Alice owns a workflow "Data Pipeline" with status "ACTIVE"
```

### Scenario: Share workflow with team (FR-007)

```gherkin
Scenario: Workflow owner shares workflow with their team
  Given Alice is authenticated
  When Alice sends PUT /api/workflows/{workflowId}/team with:
    | teamId | {Engineering.id} |
  Then the response status is 200
  And workflow "Data Pipeline" has teamId set to Engineering's ID
  And an audit log entry exists with action "WORKFLOW_SHARED"
```

### Scenario: Non-owner cannot share workflow (FR-007)

```gherkin
Scenario: Non-owner cannot share another user's workflow
  Given Bob is authenticated
  And Bob does NOT own workflow "Data Pipeline"
  When Bob sends PUT /api/workflows/{workflowId}/team with:
    | teamId | {Engineering.id} |
  Then the response status is 403
```

### Scenario: Unshare workflow from team (FR-008)

```gherkin
Scenario: Workflow owner removes team association
  Given Alice is authenticated
  And workflow "Data Pipeline" is shared with team "Engineering"
  When Alice sends DELETE /api/workflows/{workflowId}/team
  Then the response status is 200
  And workflow "Data Pipeline" has teamId set to null
  And an audit log entry exists with action "WORKFLOW_UNSHARED"
```

### Scenario: List team workflows (FR-009)

```gherkin
Scenario: Team member lists shared workflows
  Given Carol is authenticated
  And workflow "Data Pipeline" is shared with team "Engineering"
  And workflow "ML Model" is shared with team "Engineering"
  When Carol sends GET /api/teams/{teamId}/workflows
  Then the response status is 200
  And the response contains 2 workflows
```

---

## Feature: Workflow Permission Enforcement

### Scenario Outline: Role-based workflow access (FR-011, FR-012)

```gherkin
Scenario Outline: <role> <action> on team workflow returns <status>
  Given <user> is authenticated
  And <user> has team role "<role>" on team "Engineering"
  And workflow "Data Pipeline" is shared with team "Engineering"
  When <user> sends <method> /api/workflows/{workflowId}<path>
  Then the response status is <status>

  Examples:
    | user  | role    | action           | method | path          | status |
    | Dave  | VIEWER  | views workflow   | GET    |               | 200    |
    | Dave  | VIEWER  | edits workflow   | PUT    |               | 403    |
    | Dave  | VIEWER  | deletes workflow | DELETE |               | 403    |
    | Dave  | VIEWER  | executes workflow| POST   | /execute      | 403    |
    | Carol | MEMBER  | views workflow   | GET    |               | 200    |
    | Carol | MEMBER  | edits workflow   | PUT    |               | 200    |
    | Carol | MEMBER  | deletes workflow | DELETE |               | 403    |
    | Carol | MEMBER  | executes workflow| POST   | /execute      | 200    |
    | Bob   | ADMIN   | views workflow   | GET    |               | 200    |
    | Bob   | ADMIN   | edits workflow   | PUT    |               | 200    |
    | Bob   | ADMIN   | deletes workflow | DELETE |               | 204    |
    | Bob   | ADMIN   | executes workflow| POST   | /execute      | 200    |
    | Alice | OWNER   | views workflow   | GET    |               | 200    |
    | Alice | OWNER   | edits workflow   | PUT    |               | 200    |
    | Alice | OWNER   | deletes workflow | DELETE |               | 204    |
    | Alice | OWNER   | executes workflow| POST   | /execute      | 200    |
```

### Scenario: Non-team-member cannot access team workflow (FR-012)

```gherkin
Scenario: Non-member is forbidden from viewing team workflow
  Given a user "Eve" who is NOT a member of team "Engineering"
  And Eve is authenticated
  And workflow "Data Pipeline" is shared with team "Engineering"
  When Eve sends GET /api/workflows/{workflowId}
  Then the response status is 403
```

### Scenario: Personal workflow access unchanged (FR-012)

```gherkin
Scenario: Owner can still access personal (non-team) workflow
  Given Alice is authenticated
  And Alice owns workflow "Personal Flow" with no teamId
  When Alice sends GET /api/workflows/{workflowId}
  Then the response status is 200
```

### Scenario: Viewer UI shows read-only state (FR-011)

```gherkin
Scenario: Viewer sees disabled edit controls in UI
  Given Dave is authenticated as VIEWER on team "Engineering"
  And workflow "Data Pipeline" is shared with team "Engineering"
  When Dave navigates to the workflow detail page
  Then the "Edit" button is disabled or hidden
  And the "Delete" button is not visible
  And the "Execute" button is not visible
  And the workflow definition is displayed in read-only mode
```

---

## Feature: Audit Log Querying

### Scenario: Query audit logs by team (FR-015)

```gherkin
Scenario: Team owner queries audit logs for their team
  Given Alice is authenticated
  And Alice is OWNER of team "Engineering"
  And 5 audit log entries exist for team "Engineering"
  When Alice sends GET /api/audit-logs?teamId={Engineering.id}
  Then the response status is 200
  And the response contains 5 audit log entries
  And each entry includes "action", "resource", "userId", "createdAt"
```

### Scenario: Non-admin cannot query other team's audit logs (FR-015)

```gherkin
Scenario: User cannot query audit logs for a team they do not own
  Given Carol is authenticated
  And Carol has team role "MEMBER" on team "Engineering"
  When Carol sends GET /api/audit-logs?teamId={Engineering.id}
  Then the response status is 403
```

### Scenario: System admin can query any audit logs (FR-015)

```gherkin
Scenario: System ADMIN can query audit logs for any team
  Given a user "SysAdmin" with system role "ADMIN"
  And SysAdmin is authenticated
  When SysAdmin sends GET /api/audit-logs?teamId={Engineering.id}
  Then the response status is 200
```

---

## Feature: Role Change Protections

### Scenario: Last owner cannot be demoted (FR-011, US-003)

```gherkin
Scenario: Cannot demote the last team owner
  Given Alice is the only OWNER of team "Engineering"
  And Alice is authenticated
  When Alice sends PUT /api/teams/{teamId}/members/{Alice.memberId} with:
    | teamRole | ADMIN |
  Then the response status is 403
  And the response detail contains "last team owner"
```

### Scenario: Admin cannot promote to Owner (US-003)

```gherkin
Scenario: Team admin cannot promote a member to owner
  Given Bob is authenticated
  And Bob has team role "ADMIN" on team "Engineering"
  When Bob sends PUT /api/teams/{teamId}/members/{Carol.memberId} with:
    | teamRole | OWNER |
  Then the response status is 403
  And the response detail contains "Only team owners"
```
