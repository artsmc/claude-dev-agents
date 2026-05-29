# Team Lead — Playbook Module

Load this module when you need pre-built team compositions for common scenarios, the agent selection reference table, or metrics and reporting guidance.

---

## Common Team Compositions

### Planning → Spec → Implementation

Use for major new features that need formal documentation before coding begins.

Agents:
1. **strategic-planner** — Overall implementation plan and architecture
2. **spec-writer** — FRD, FRS, GS, and TR documents
3. **express-api-developer** — API endpoint implementation
4. **qa-engineer** — Integration tests (can run parallel with API dev)
5. **technical-writer** — API documentation (after endpoints stabilize)

Sequence:
1. strategic-planner creates plan
2. spec-writer generates specifications from the plan
3. express-api-developer + qa-engineer work in parallel from the spec
4. technical-writer documents after endpoints are stable
5. Team lead validates cross-agent consistency before shutdown

### Cross-Service Feature

Use when a feature spans the Express API (apps/api), the Next.js web app (apps/web), and/or the Mastra workflow engine (apps/mastra).

Agents:
1. **strategic-planner** — Architecture overview and integration points
2. **database-schema-specialist** — Shared schema design (blocks downstream agents)
3. **express-api-developer** — Express API endpoints (parallel after schema)
4. **frontend-developer** — Next.js UI components (parallel after schema)
5. **nextjs-backend-developer** — Next.js API routes or server actions (if needed)

Sequence:
1. Architecture and schema first — these decisions unblock everything else
2. Express API + frontend in parallel once schema is settled
3. Integration and end-to-end testing coordinated by team lead

### Large Refactoring + Testing

Use when refactoring requires a safety net and security validation before merging.

Agents:
1. **refactoring-specialist** — Code modernization and technical debt reduction
2. **qa-engineer** — Test suite updates (parallel with refactoring)
3. **security-auditor** — Security impact assessment (after refactoring stabilizes)
4. **code-reviewer** — Final review pass

Sequence:
1. refactoring-specialist + qa-engineer work in parallel
2. security-auditor validates after refactoring is stable
3. code-reviewer does final pass; team lead coordinates any revisions

---

## Agent Selection Reference

| Work Type | Agent |
|-----------|-------|
| Express API endpoints (apps/api) | express-api-developer |
| Next.js UI components (apps/web) | frontend-developer |
| Next.js API routes or server actions | nextjs-backend-developer |
| Database schema design and migrations | database-schema-specialist |
| Test writing (unit, integration, E2E) | qa-engineer |
| API and developer documentation | technical-writer |
| Architecture planning and strategy | strategic-planner |
| Formal specs (FRD, FRS, GS, TR) | spec-writer |
| Code review and best practices | code-reviewer |
| Security audit and OWASP compliance | security-auditor |
| Technical debt and code modernization | refactoring-specialist |
| Codebase exploration and investigation | Explore (via Task tool) |
| Infrastructure, CI/CD, deployment | devops-infrastructure |

---

## Scenario Walkthroughs

### Feature Development: "Add SSO authentication with RBAC"

```
1. TeamCreate: "sso-rbac-feature"
2. Create working memory file
3. Spawn strategic-planner → generate plan covering auth flows and RBAC model
4. Spawn spec-writer → generate FRD/FRS from plan
5. Create tasks from spec: SSO token validation, RBAC middleware, test suite
6. Spawn express-api-developer → implement POST /api/auth/sso and RBAC middleware
7. Spawn qa-engineer → write tests in parallel
8. Validate cross-agent consistency (do tokens and RBAC checks align?)
9. Shutdown agents, TeamDelete, rm working memory file
```

### Cross-Service Feature: "Real-time workflow execution dashboard"

```
1. TeamCreate: "workflow-dashboard"
2. Create working memory file
3. Spawn strategic-planner → define polling/SSE architecture
4. Spawn express-api-developer → add SSE or polling endpoints to apps/api
5. Spawn nextjs-backend-developer → SSE streaming handler in apps/web (parallel)
6. Spawn frontend-developer → React dashboard consuming the stream (parallel)
7. Coordinate integration points: endpoint URLs, event schema, auth headers
8. Validate end-to-end flow (API → Next.js → React)
9. Shutdown, TeamDelete, rm working memory file
```

### Large Refactoring: "Refactor auth middleware to support SSO"

```
1. TeamCreate: "auth-refactor"
2. Create working memory file
3. Spawn refactoring-specialist → modernize auth middleware
4. Spawn qa-engineer → update + expand test coverage in parallel
5. After refactoring stabilizes: spawn security-auditor → validate security posture
6. Spawn code-reviewer → final review
7. Coordinate any revisions via direct messages
8. Shutdown, TeamDelete, rm working memory file
```

---

## Metrics and Reporting

**Track during execution:**
- Tasks completed vs total (use `TaskList` regularly)
- Blockers encountered and how they were resolved
- Key architectural or implementation decisions made
- Integration issues discovered between agents

**Report at completion:**
- Total tasks completed and agents used
- Key decisions (reference the working memory file before it's deleted)
- Deliverables produced: files, endpoints, test suites, documentation
- Recommended next steps (follow-on tasks, open questions, monitoring needs)
