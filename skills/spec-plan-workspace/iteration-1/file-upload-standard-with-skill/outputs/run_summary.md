# Spec-Plan Run Summary: File Upload Support

**Date:** 2026-03-09
**Feature Request:** "We need to add file upload support -- users should be able to attach files to workflow steps. The files need to go to S3, and the API needs new endpoints for upload/download."

---

## Phase 0: Feature Description

Used the provided prompt as the starting feature description:
> "We need to add file upload support -- users should be able to attach files to workflow steps. The files need to go to S3, and the API needs new endpoints for upload/download."

---

## Phase 1: Clarification Questions (Simulated)

The following questions were identified as needed for triage. Simulated reasonable answers are provided in brackets.

1. **What problem does this solve for users?** (one sentence)
   > [Users need to attach reference documents, data files, or configuration files to specific workflow steps so those files are available during workflow execution.]

2. **Which apps are affected?** (API / Web / Mastra / Microsandbox)
   > [API (new upload/download endpoints, schema changes) and Web (file upload UI in workflow builder). Mastra is not directly affected -- it consumes workflow definitions which would reference file keys, but no Mastra code changes needed. Microsandbox is not affected.]

3. **Any hard constraints?** (security, performance, compliance)
   > [Files must go to S3 (already have libs/storage with S3 client). Max file size should be reasonable (e.g., 50MB). Files must be associated with authenticated users and respect ownership/RBAC. FedRAMP compliance means audit logging for file operations is required.]

---

## Phase 2: Triage Gate

### Tier Selected: **STANDARD-SPEC**

### Rationale

| Signal | Value | Notes |
|--------|-------|-------|
| Apps affected | 2 (API + Web) | Matches "2 apps affected" standard signal |
| Complexity | Moderate | New data model (FileAttachment), new API contract (upload/download endpoints), new S3 integration for file storage |
| Estimated tasks | 10-12 | Schema + service + controller + routes + validation + storage lib extension + web upload component + integration |
| Pattern type | Known but meaningful | File upload is a well-understood pattern, but requires multipart handling, presigned URLs, DB model, and frontend integration |
| Security sensitivity | Moderate | File validation, size limits, content-type checking, RBAC -- but not a new auth system |

**Decision:** STANDARD tier. This is not a simple single-endpoint change (not Quick), but it also does not introduce a new architectural pattern, does not affect 3+ apps, and does not have deep security/compliance novelty (not Full). The existing `libs/storage` library already has S3 client infrastructure. Two apps are affected with moderate complexity.

---

## Phase 3: Scope Confirmation

```
Based on your description, I've scoped this as a **STANDARD** spec:

Feature: File upload attachments for workflow steps
Affected apps: API, Web
Estimated complexity: moderate

I'll generate:
  [x] task-list.md -- Implementation tasks with dependencies
  [x] FRD.md -- Feature requirements and success criteria
  [x] TR.md -- Technical requirements and API contracts
  [ ] FRS.md -- (not needed at this tier)
  [ ] GS.md -- (not needed at this tier)

Research scope:
  [x] Memory Bank -- Check existing patterns and active work
  [x] Codebase scan -- Existing S3, storage, route patterns
  [x] Documentation -- Framework patterns (presigned URLs, multer)
  [ ] Deep research -- (not needed at this tier)

Estimated generation time: 3-7 min
Estimated tokens: ~35K

Does this scope look right, or should I adjust?
```

---

## Phase 4: Budgeted Research Findings

### Memory Bank (1.5K budget)

**activeContext.md findings:**
- Current focus is on Microsandbox Connectors + Build Stabilization (branch: `Microsandbox-connectors`)
- S3 audit logging was recently implemented (2026-03-09) in `libs/storage`
- Known blocker: Microsandbox `iconv-lite` body-parser issue (irrelevant to file upload)
- Agent CRUD API is next on the roadmap (10 pending tasks)
- No active work on file upload exists

**systemPatterns.md findings:**
- Repository Pattern for DB access (will need FileAttachment repository)
- Service Layer for external APIs (will need FileStorageService)
- RFC 7807 Problem Details for errors (must follow this pattern)
- Zod for runtime validation (new schemas needed)
- Base Controller with asyncHandler (new controller should extend this)
- Factory Function pattern for Express app (consistent with testing strategy)
- Middleware Pipeline pattern (multipart middleware will need to be placed correctly)

### Codebase Analysis (1.5K budget)

**Existing S3 Infrastructure (`libs/storage`):**
- `client.ts` -- Singleton S3Client with LocalStack support, IAM + explicit credentials
- `audit-logs.ts` -- PutObject, GetObject, ListObjectsV2 patterns already implemented
- `errors.ts` -- StorageError hierarchy (ObjectNotFoundError, AccessDeniedError, BucketNotFoundError)
- `types.ts` -- AuditRecord, AuditLogFilters, StorageConfig types
- **Can be extended** with file upload/download functions (uploadFile, downloadFile, generatePresignedUrl)

**API Patterns (apps/api):**
- Routes: `/api/skills`, `/api/workflows`, `/api/agents` -- all follow Router + Controller + Service + Zod validation pattern
- Skills model already has `s3Key` and `s3Bucket` fields in Prisma schema
- No existing multipart/form-data handling (no multer or similar dependency)
- Middleware pipeline: helmet -> cors -> json -> swagger -> rateLimit -> auth -> routes -> error

**Prisma Schema (apps/api/prisma/schema.prisma):**
- Workflow model has `definition Json` field (DAG) but no file attachment relation
- Need new `FileAttachment` model with relation to Workflow (or generic polymorphic via resourceType/resourceId)
- Existing enums and patterns are well-established

**Web App:**
- Workflow-related files exist: `hooks/use-workflows.ts`, `app/api/workflows/route.ts`
- No existing file upload components found
- Uses Next.js 16 with React 19, TanStack Query, React Hook Form

### Documentation (2K budget)

**Key patterns identified (from knowledge):**
- Express 5.x multipart: Use `multer` or `busboy` for multipart/form-data parsing
- S3 presigned URLs: Use `@aws-sdk/s3-request-presigner` for direct browser-to-S3 uploads (better for large files)
- Two upload strategies:
  1. **Server-proxied:** Browser -> API (multer) -> S3 (simpler, size limited by API memory)
  2. **Presigned URL:** Browser -> API (get URL) -> S3 direct (scalable, no server bottleneck)
- Recommendation: Presigned URL for upload, server-proxied for download (or presigned for download too)

---

## Phase 5: Deliverables Generated

### Files Generated

| File | Description | Lines |
|------|-------------|-------|
| `FRD.md` | Feature Requirements Document -- user stories, acceptance criteria, edge cases, success metrics | ~140 lines |
| `TR.md` | Technical Requirements -- API contracts, data model, dependencies, error handling, security | ~190 lines |
| `task-list.md` | Implementation tasks -- phased, atomic tasks with dependencies and agent assignments | ~95 lines |
| `run_summary.md` | This file -- tier selection rationale, scope confirmation, research findings | ~200 lines |

### Structured Brief (JSON)

```json
{
  "feature": {
    "name": "workflow-file-attachments",
    "description": "Users can attach files to workflow steps, stored in S3, with API endpoints for upload/download",
    "problem_statement": "Users need to attach reference documents, data files, or configuration files to specific workflow steps so those files are available during workflow execution",
    "affected_apps": ["api", "web"],
    "complexity": "moderate",
    "tier": "standard"
  },
  "deliverables": [
    "FRD.md",
    "TR.md",
    "task-list.md"
  ],
  "constraints": {
    "security": "Files must respect user ownership and RBAC. File type validation required. Content-type verification. Max size enforcement (50MB). No PII in logs.",
    "performance": "Presigned URL pattern recommended for upload to avoid API memory bottleneck. Download via presigned URL or streaming proxy.",
    "compliance": "FedRAMP Moderate -- audit logging for all file operations (upload, download, delete). 7-year retention for audit records.",
    "deadline": "Not specified"
  },
  "research_findings": {
    "existing_patterns": "Repository pattern, service layer, RFC 7807 errors, Zod validation, Base Controller asyncHandler. All must be followed for new file upload module.",
    "reusable_components": [
      "libs/storage/src/client.ts -- S3Client singleton (reuse directly)",
      "libs/storage/src/errors.ts -- StorageError hierarchy (extend with file-specific errors)",
      "libs/storage/src/audit-logs.ts -- PutObject/GetObject patterns (reference for file operations)",
      "apps/api/src/routes/skills.ts -- Route/Controller/Service/Zod pattern (template for new routes)",
      "Skill model s3Key/s3Bucket fields -- Precedent for S3 references in Prisma schema"
    ],
    "framework_patterns": "Express 5.x + multer for multipart upload OR @aws-sdk/s3-request-presigner for presigned URL approach. Presigned URLs recommended for scalability.",
    "integration_points": [
      "API routes/index.ts -- Mount new /api/files route",
      "Prisma schema -- Add FileAttachment model",
      "libs/storage -- Add uploadFile, downloadFile, generatePresignedUrl functions",
      "Web workflow builder -- Add file upload UI component",
      "Web API proxy routes -- Add /api/files proxy"
    ],
    "pitfalls_to_avoid": [
      "Do NOT add multer before express.json() in middleware pipeline (multer handles its own body parsing for multipart)",
      "Do NOT store file contents in PostgreSQL (use S3 with DB reference only)",
      "Do NOT log file contents or full filenames (PII/compliance risk)",
      "Do NOT allow unlimited file sizes (enforce server-side, not just client-side)",
      "Beware: no existing multipart handling in API -- multer must be added as dependency"
    ]
  },
  "output_path": "/home/artsmc/.claude/skills/spec-plan-workspace/iteration-1/file-upload-standard-with-skill/outputs/"
}
```
