# API Designer — Reference Module

Load this module when the task requires deep REST/OpenAPI reference, security design guidance, edge case handling, or quality standards beyond the core workflow.

---

## REST API Design Principles

- **Resource-based URLs:** Collections vs individual resources (`/api/users` vs `/api/users/:id`)
- **HTTP verb semantics:** GET (read), POST (create), PUT (replace), PATCH (update), DELETE (remove)
- **Status codes:** 2xx (success), 4xx (client errors), 5xx (server errors)
- **Idempotency:** GET, PUT, DELETE are idempotent; POST is not
- **HATEOAS:** Hypermedia links for API discoverability where appropriate
- **Filtering, sorting, pagination:** `?filter=active&sort=name&page=2&limit=50`

---

## Next.js App Router Patterns

- **Structure:** `app/api/[resource]/route.ts`
- **Types:** `NextRequest`, `NextResponse` from `next/server`
- **Dynamic routes:** `[id]` for path parameters, `[...slug]` for catch-all routes
- **Route handlers:** Export named functions (`GET`, `POST`, `PUT`, `DELETE`, `PATCH`)
- **Edge Runtime:** Use edge runtime only when you need global distribution and can accept its constraints (no Node.js APIs, no Prisma); default to Node.js runtime
- **Middleware:** Attach auth, rate limiting, CORS, and logging at the middleware layer, not inline in route handlers

---

## OpenAPI 3.x Standards

- **Document structure:** `openapi`, `info`, `servers`, `paths`, `components`, `security`, `tags`
- **Schema definitions:** Use `$ref` for reusability; `allOf`/`oneOf`/`anyOf` for composition
- **Security schemes:** `bearerAuth`, `apiKey`, `oauth2`, custom schemes
- **Examples:** Inline examples and `examples` objects for every operation
- **Deprecation:** Mark endpoints with `deprecated: true` and document the replacement
- **Versioning strategies:** URL versioning (`/v2/api/`) is simplest; header or media-type versioning for APIs requiring backward compatibility in the same URL

---

## Type Safety and Validation

- No `any` types — explicit typing for all requests, responses, and function signatures
- Runtime validation: Zod (preferred in this stack), Yup, or class-validator
- Type guards: custom type predicates for narrowing union types
- Discriminated unions: use a `type` discriminator field for polymorphic types
- Generics: for reusable service patterns and pagination wrappers
- Strict TypeScript config: `strict: true`, `noImplicitAny: true`, `strictNullChecks: true`

---

## Security Design Checklist

**Input Validation**
- [ ] Sanitize and validate all user inputs at the route layer before reaching services
- [ ] Parameterized queries only (no string concatenation in SQL)
- [ ] NoSQL injection prevented (sanitize inputs for MongoDB-style operators)
- [ ] XSS prevention: Content Security Policy, no `dangerouslySetInnerHTML` with unsanitized input
- [ ] CSRF protection: tokens for state-changing operations, SameSite cookies
- [ ] Path traversal prevention: no user-controlled file paths
- [ ] File uploads: validate MIME type, size limits, content magic bytes, safe filename generation

**Authorization Design**
- [ ] Every protected endpoint specifies required role or permission
- [ ] RBAC (role-based) for coarse-grained access; ABAC (attribute-based) for fine-grained ownership checks
- [ ] Ownership checks: resource owner must be verified before any mutation
- [ ] Admin endpoints explicitly protected from regular users
- [ ] Rate limiting: per-IP and per-user limits specified per endpoint

**Secrets and Transport**
- [ ] All secrets come from environment variables, never hardcoded
- [ ] HTTPS enforcement specified (HSTS header)
- [ ] JWT design: short-lived access tokens (15m), refresh token pattern (7d)

---

## Performance and Scalability

- **Pagination:** Cursor-based (scalable for large datasets) vs offset-based (simple, fine for small datasets) — pick one per API and be consistent
- **Field selection:** `?fields=id,name,email` lets clients reduce payload size
- **Caching:** HTTP caching headers (ETag, Cache-Control) for idempotent reads; Redis for computed/expensive results
- **Compression:** Enable gzip/brotli for responses in the HTTP layer
- **Async operations:** Background jobs (PGBoss) for long-running tasks; return a job ID for polling or webhooks
- **N+1 query prevention:** Design service layer to use eager loading, data loaders, or query batching

---

## Edge Cases Catalog

**No existing `openapi.yaml`**
Create from scratch with `openapi: 3.0.3`, `info`, `servers`, `paths`, `components`, and `securitySchemes`. Establish conventions that all future endpoints will follow.

**Conflicting API patterns in existing codebase**
Identify inconsistencies (error formats, auth, pagination). Propose a unification strategy with a migration path for legacy endpoints. Do not silently adopt the inconsistent pattern.

**GraphQL vs REST decision**
REST: simple CRUD, stable query patterns, easy caching, well-understood tooling.
GraphQL: highly variable query shapes, deeply nested resources, client-driven field selection, real-time subscriptions.
Provide a trade-off analysis with a recommendation and justification; do not leave this decision to the implementer.

**Breaking changes required**
Design URL versioning (`/v2/api/`) unless the project already uses header or media-type versioning. Document a migration guide for clients and a deprecation timeline for the old version.

**Unclear requirements (Low Confidence)**
List exactly what is ambiguous, what assumptions would need to be made, and what alternatives exist. Request clarification before producing any specification.

**Complex authorization needs**
Design a permission matrix: roles × actions × resources. Define role hierarchy and attribute evaluation rules. For ABAC, specify which attributes (owner, tenant, status) gate which actions.

**Real-time requirements**
Server-Sent Events (SSE): one-way server push, simple, works over HTTP/1.1. WebSockets: bidirectional, requires connection management. Polling: simplest fallback. Provide trade-off analysis including fallback strategy.

**File upload design**
Use multipart/form-data. Specify size limits, allowed MIME types, virus scanning strategy, and storage backend (S3, local disk, database BLOB). Design safe filename generation (UUIDs, not user-supplied names).

**Batch operations**
Design `POST /api/resources/batch`. Specify maximum batch size, partial success handling (return per-item status array), and rollback strategy (all-or-nothing vs best-effort).

**Service growing too large**
If a service module is projected to exceed a manageable size, split it along domain boundaries. Design clear interfaces between the sub-services and identify shared utility functions to extract.

---

## Quality Standards

### Completeness
- All endpoints have full request and response schemas
- All error cases documented with examples
- Authentication/authorization requirements specified per endpoint
- Rate limiting strategy defined
- Caching strategy specified where applicable

### Consistency
- Uniform naming convention (pick one: camelCase for JSON fields, kebab-case for URLs)
- Standard error response format across all endpoints
- Consistent pagination approach — cursor or offset, not both
- Uniform authentication mechanism unless legacy support explicitly required

### Maintainability
- OpenAPI schemas use `$ref` to avoid duplication
- Reusable types defined in shared type files
- Clear separation of concerns across all three tiers
- Module boundaries respect `keyPairResponsibility.md`

### Integration Alignment
- Designs follow existing patterns from `systemArchitecture.md`
- Terminology matches `glossary.md`
- Technology choices align with `techStack.md`
