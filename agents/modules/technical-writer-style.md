# Technical Writer — Style Guide Module

Load this module when tasks require adherence to detailed style conventions, voice/tone guidelines, API documentation formatting, or changelog format rules.

---

## Voice and Tone

### Core Principles

**Active Voice Always**
- Write: "The API returns a JSON object."
- Not: "A JSON object is returned by the API."
- Write: "Click Save to confirm."
- Not: "The Save button should be clicked."

**Second Person**
- Write: "You can configure the timeout."
- Not: "The user can configure the timeout."
- Not: "One can configure the timeout."

**Present Tense**
- Write: "The function validates the input."
- Not: "The function will validate the input."

**Direct and Confident**
- Write: "Set the `timeout` to 30 seconds."
- Not: "You might want to consider setting the `timeout` to perhaps 30 seconds."

**Avoid Filler Words**
Remove: simply, just, easily, obviously, clearly, basically, straightforward
- Write: "Run `npm install`."
- Not: "Simply run `npm install`."

### Tone Calibration by Audience

**For Developers (API docs, README, tutorials):**
- Technical precision over hand-holding
- Assume fluency with code and CLI
- Skip obvious setup steps (e.g., don't explain what npm is)
- Include edge cases and gotchas

**For End Users (guides, how-to):**
- Plain language, define technical terms
- More context for "why" before "how"
- Screenshots and visual aids expected
- Troubleshooting sections essential

**For Operations/DevOps:**
- Commands with expected output shown
- Failure modes and recovery steps
- Reference exact version numbers and environment requirements
- Security implications highlighted

---

## Grammar Rules

### Capitalization

- **Product/Feature names:** Capitalize proper names (e.g., Mastra Studio, AIForge, Microsandbox)
- **UI elements:** Use exact capitalization as shown in UI ("Click **Save Changes**", not "Save changes")
- **Code terms inline:** Use backtick formatting, not capitalization (`userId`, `DATABASE_URL`)
- **Section headings:** Title case for H1/H2, sentence case for H3 and below

### Punctuation

- **Oxford comma:** Always use in lists: "agents, workflows, and tools"
- **Em dash:** Use for parenthetical asides — like this — not hyphens
- **Ellipsis:** Avoid in technical docs; use only in UI text for truncation
- **Periods in bullets:** Include when bullet is a full sentence; omit for fragments

### Numbers

- **Under 10:** Spell out (one, two, three)
- **10 and above:** Use numerals (10, 42, 1000)
- **Exception:** Always use numerals for: version numbers (v2.0), port numbers (port 4000), measurements (30 seconds, 128MB), code values (`limit: 5`)

### Abbreviations

- **First use:** Spell out with abbreviation in parentheses: "Role-Based Access Control (RBAC)"
- **Subsequent uses:** Abbreviation only: "RBAC"
- **Common tech abbreviations:** API, URL, HTTP, JSON, SQL, JWT — acceptable without spelling out

---

## Markdown Formatting Conventions

### Heading Hierarchy

```markdown
# H1: Document title only — one per document
## H2: Major sections (Installation, Configuration, API Reference)
### H3: Subsections within a major section
#### H4: Use sparingly — consider restructuring if needed frequently
```

### Code Formatting

**Inline code** — for all of these:
- Variable names: `userId`
- File names: `package.json`, `.env`
- CLI commands inline in prose: Run `npm install` before continuing
- Config keys: Set `PORT=4000` in your environment
- HTTP methods: `GET`, `POST`
- Status codes: `401 Unauthorized`

**Code blocks** — always specify language:
```markdown
```typescript
// TypeScript code
```

```bash
# Shell commands
```

```json
{
  "key": "value"
}
```

```yaml
field: value
```
```

**Command output** — use `text` or no language tag for raw output:
```text
✓ Successfully installed 3 packages
```

### Callout Boxes

Use blockquote with bold lead:

```markdown
> **Note:** Additional context that is helpful but not critical.

> **Warning:** Information about potential data loss or irreversible actions.

> **Tip:** Best practice or time-saving suggestion.

> **Important:** Behavior that differs from expectation or common mistakes.
```

Do not use emoji in callouts for technical documentation. Use emoji in README feature lists only.

### Tables

Always include header row and alignment:

```markdown
| Column 1 | Column 2 | Column 3 |
|----------|----------|----------|
| data     | data     | data     |
```

Use tables for:
- Configuration options (name, type, default, required, description)
- Error codes (code, description, common cause)
- Environment variables
- Feature comparison

Do not use tables for: sequential steps (use numbered list), prose content.

### Lists

**Numbered lists** — use for: sequential steps, ranked items, ordered procedures
**Bullet lists** — use for: unordered items, feature lists, non-sequential options

Keep bullets parallel in structure:
```markdown
The API supports:
- JSON request and response bodies
- Bearer token authentication
- Rate limiting via X-RateLimit headers
```

Not:
```markdown
The API supports:
- JSON bodies
- You can authenticate with Bearer tokens
- Rate limiting is applied
```

---

## API Documentation Conventions

### Endpoint Documentation Structure

Every endpoint must follow this order:

1. **Method and path** as H3: `### POST /api/v1/users`
2. **One-sentence description** of purpose and when to use
3. **Authentication** — what's required
4. **Request** section with subsections:
   - URL Parameters (if any)
   - Query Parameters (if any)
   - Request Headers
   - Request Body with full schema
5. **Response** section:
   - Success case with full example JSON
   - Error codes table
   - Error response format example
6. **Examples** — cURL, then JavaScript, then Python
7. **Notes** — rate limits, edge cases, deprecation warnings

### Schema Documentation

For request/response bodies, document every field:

```markdown
| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `name` | string | Yes | — | Display name, 1–100 characters |
| `role` | enum | No | `USER` | One of: `USER`, `ADMIN`, `CONTRACTOR` |
| `tags` | string[] | No | `[]` | Searchable labels, max 10 |
```

### Error Documentation

Always document the complete error contract:

```markdown
### Error Responses

The API uses RFC 7807 Problem Details format:

```json
{
  "type": "https://yourapi.com/errors/validation-failed",
  "title": "Validation Failed",
  "status": 400,
  "detail": "The email field must be a valid email address",
  "field": "email"
}
```

| Status | Code | Description |
|--------|------|-------------|
| 400 | `VALIDATION_FAILED` | Request body fails schema validation |
| 401 | `UNAUTHORIZED` | Missing or invalid authentication token |
| 403 | `FORBIDDEN` | Token valid but insufficient permissions |
| 404 | `NOT_FOUND` | Resource with given ID does not exist |
| 429 | `RATE_LIMITED` | Exceeded rate limit; retry after `X-RateLimit-Reset` |
| 500 | `INTERNAL_ERROR` | Server error; contact support with request ID |
```

### Versioning Notation

- Reference API versions explicitly: "This endpoint is available in API v2 and later."
- Mark deprecated endpoints: `> **Deprecated:** Use \`POST /api/v2/users\` instead. This endpoint will be removed in Q3 2026.`
- Note breaking changes prominently at the top of the section

---

## Changelog Format Rules

Follow [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) format strictly.

### Structure

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
### Changed
### Deprecated
### Removed
### Fixed
### Security

## [2.1.0] - 2026-03-09

### Added
- New `GET /api/v1/workflows/:id/status` endpoint for real-time execution status
- Support for webhook callbacks on workflow completion

### Changed
- **BREAKING:** `POST /api/v1/workflows/execute` now returns `202 Accepted` instead of `200 OK`
- Rate limits increased from 100 to 500 requests per minute

### Fixed
- Fixed memory leak in long-running workflow executions (#123)
- Corrected timezone handling in `scheduledAt` timestamp fields

[Unreleased]: https://github.com/org/repo/compare/v2.1.0...HEAD
[2.1.0]: https://github.com/org/repo/compare/v2.0.0...v2.1.0
```

### Change Entry Rules

- **One change per bullet.** Do not combine: "Added X and fixed Y" → two separate bullets.
- **Breaking changes:** Mark with bold "**BREAKING:**" prefix. Always include migration guidance.
- **Issue/PR references:** Link to GitHub issues or PRs: "Fixed race condition (#456)"
- **Deprecation warnings:** Always include the replacement and removal timeline.
- **Security fixes:** Reference CVE if applicable: "Patched CVE-2024-1234 in dependency X"

### Version Types (Semantic Versioning)

- **MAJOR (X.0.0):** Breaking API changes
- **MINOR (0.X.0):** New backwards-compatible features
- **PATCH (0.0.X):** Backwards-compatible bug fixes and security patches

---

## Documentation File Structure

### Location Rules (per CLAUDE.md)

- All documentation files (*.md) go to `/home/artsmc/applications/low-code/job-queue/`
- Product specs: `/home/artsmc/applications/low-code/job-queue/product-forge/`
- Never create markdown files in: `apps/`, `libs/`, `src/`

### File Naming

- Lowercase, hyphenated: `api-authentication.md`, `getting-started.md`
- Descriptive, not generic: `workflow-execution-api.md` not `api.md`
- Version suffix when multiple versions exist: `api-v1.md`, `api-v2.md`

### Internal Links

Always use relative paths for internal document links:
- `[Getting Started](./getting-started.md)` — same directory
- `[API Reference](../api/reference.md)` — parent directory
- Never use absolute paths in documentation

---

## Style Checklist

Before finalizing any document, verify:

- [ ] Active voice used throughout
- [ ] Second person ("you") not third person ("the user")
- [ ] Oxford commas in all lists
- [ ] Filler words removed (simply, just, easily, obviously)
- [ ] All code terms in backticks
- [ ] Code blocks have language specifiers
- [ ] Headings follow hierarchy (no skipping levels)
- [ ] Tables have header row and proper alignment
- [ ] Callouts use correct format (Note/Warning/Tip/Important)
- [ ] Numbered lists for sequences, bullets for unordered items
- [ ] Bullets are parallel in structure
- [ ] Breaking changes marked with "**BREAKING:**"
- [ ] Changelog follows Keep a Changelog format
- [ ] Internal links use relative paths
- [ ] No emoji except in README feature lists
