# Implementation Task List: Workflow File Attachments

**Feature:** workflow-file-attachments
**Tier:** Standard
**Estimated Tasks:** 12
**Date:** 2026-03-09

---

## Phase 1: Data Model & Infrastructure (Setup)

### Task 1: Add FileAttachment model to Prisma schema
- **Action:** Add `FileAttachment` model to `apps/api/prisma/schema.prisma`. Add `fileAttachments FileAttachment[]` relation to existing `Workflow` model. Run `prisma migrate dev --name add-file-attachments` and `prisma generate`.
- **Files:** `apps/api/prisma/schema.prisma`
- **Pattern:** Follow existing model conventions (cuid IDs, @@map, @@index, timestamps)
- **Dependencies:** None
- **Agent:** `database-schema-specialist`
- **Complexity:** S

### Task 2: Create S3 bucket and LocalStack config
- **Action:** Add `forge-file-uploads-dev` bucket creation to `infrastructure/local/localstack-init.sh`. Configure CORS policy. Add `FILE_UPLOAD_BUCKET` env var to `apps/api/example.env`.
- **Files:** `infrastructure/local/localstack-init.sh`, `apps/api/example.env`
- **Pattern:** Follow existing LocalStack bucket setup pattern
- **Dependencies:** None
- **Agent:** `devops-infrastructure`
- **Complexity:** S

### Task 3: Extend libs/storage with file operations
- **Action:** Create `libs/storage/src/file-storage.ts` with functions: `uploadFile`, `deleteFile`, `generatePresignedUploadUrl`, `generatePresignedDownloadUrl`, `headFile` (check existence). Add `@aws-sdk/s3-request-presigner` dependency. Export new functions from `libs/storage/src/index.ts`. Add types to `libs/storage/src/types.ts`.
- **Files:** `libs/storage/src/file-storage.ts` (new), `libs/storage/src/types.ts`, `libs/storage/src/index.ts`, `libs/storage/package.json`
- **Pattern:** Follow `audit-logs.ts` patterns (singleton client, error wrapping, typed params)
- **Dependencies:** None
- **Agent:** `express-api-developer`
- **Complexity:** M

---

## Phase 2: API Implementation (Core)

### Task 4: Create Zod validation schemas for file endpoints
- **Action:** Create `apps/api/src/schemas/file.schema.ts` with schemas: `PresignUploadRequestSchema`, `ConfirmUploadRequestSchema`, `ListFilesQuerySchema`, `FileIdParamsSchema`. Include file type allowlist, size limits, and cuid validation.
- **Files:** `apps/api/src/schemas/file.schema.ts` (new)
- **Pattern:** Follow `apps/api/src/schemas/skill.schema.ts` pattern (Zod schemas with exports)
- **Dependencies:** Task 1 (need model understanding)
- **Agent:** `express-api-developer`
- **Complexity:** S

### Task 5: Create FileStorageService
- **Action:** Create `apps/api/src/services/file-storage.service.ts` with methods: `requestPresignedUpload`, `confirmUpload`, `listFiles`, `getFileDownloadUrl`, `deleteFile`. Service wraps `libs/storage` functions and handles DB operations via Prisma. Include workflow ownership verification.
- **Files:** `apps/api/src/services/file-storage.service.ts` (new)
- **Pattern:** Follow `apps/api/src/services/skill/skill-crud.service.ts` pattern (service class with Prisma, error handling)
- **Dependencies:** Task 1, Task 3
- **Agent:** `express-api-developer`
- **Complexity:** M

### Task 6: Create FileController
- **Action:** Create `apps/api/src/controllers/file.controller.ts` with handlers: `presignUpload`, `confirmUpload`, `list`, `download`, `remove`. Extend BaseController pattern with asyncHandler. Include audit logging calls.
- **Files:** `apps/api/src/controllers/file.controller.ts` (new)
- **Pattern:** Follow `apps/api/src/controllers/skill.controller.ts` pattern (BaseController, asyncHandler, sendData)
- **Dependencies:** Task 4, Task 5
- **Agent:** `express-api-developer`
- **Complexity:** M

### Task 7: Create file routes and mount in router
- **Action:** Create `apps/api/src/routes/files.ts` with all 5 endpoints. Mount as `/api/files` in `apps/api/src/routes/index.ts`. Apply auth middleware, Zod validation middleware. Add Swagger JSDoc annotations.
- **Files:** `apps/api/src/routes/files.ts` (new), `apps/api/src/routes/index.ts`
- **Pattern:** Follow `apps/api/src/routes/skills.ts` pattern (Router + middleware + swagger)
- **Dependencies:** Task 4, Task 6
- **Agent:** `express-api-developer`
- **Complexity:** M

---

## Phase 3: Web Frontend (UI)

### Task 8: Create file upload hook and API client
- **Action:** Create `apps/web/src/hooks/use-file-attachments.ts` with TanStack Query hooks: `useFileAttachments` (list), `useUploadFile` (mutation), `useDeleteFile` (mutation), `useDownloadFile`. Create corresponding API proxy routes at `apps/web/src/app/api/files/`. Add query keys to `apps/web/src/lib/query-keys.ts`.
- **Files:** `apps/web/src/hooks/use-file-attachments.ts` (new), `apps/web/src/app/api/files/route.ts` (new), `apps/web/src/app/api/files/[id]/download/route.ts` (new), `apps/web/src/lib/query-keys.ts`
- **Pattern:** Follow `apps/web/src/hooks/use-workflows.ts` pattern (TanStack Query hooks)
- **Dependencies:** Task 7 (API must exist)
- **Agent:** `frontend-developer`
- **Complexity:** M

### Task 9: Build FileUpload UI component
- **Action:** Create `apps/web/src/components/workflow/FileUploadPanel.tsx` with: drag-and-drop zone, file list with metadata, upload progress bar, download/delete buttons. Uses presigned URL flow (get URL from API, PUT to S3, confirm with API). Include file type/size validation on client side.
- **Files:** `apps/web/src/components/workflow/FileUploadPanel.tsx` (new)
- **Pattern:** React 19 component with Tailwind CSS styling, React Hook Form for validation
- **Dependencies:** Task 8
- **Agent:** `ui-developer`
- **Complexity:** M

---

## Phase 4: Testing & Documentation

### Task 10: Write API integration tests
- **Action:** Create `apps/api/__test__/routes/files.test.ts` with tests for all 5 endpoints. Test cases: successful upload flow, size limit enforcement, type validation, ownership checks, 404 on missing workflow, 403 on non-owner access, presigned URL generation. Mock S3 client.
- **Files:** `apps/api/__test__/routes/files.test.ts` (new)
- **Pattern:** Follow existing test files in `apps/api/__test__/` (supertest + jest + mock Prisma)
- **Dependencies:** Task 7
- **Agent:** `qa-engineer`
- **Complexity:** M

### Task 11: Write storage lib unit tests
- **Action:** Create `libs/storage/__tests__/file-storage.spec.ts` with tests for `generatePresignedUploadUrl`, `generatePresignedDownloadUrl`, `deleteFile`, `headFile`. Mock S3 client using existing test patterns.
- **Files:** `libs/storage/__tests__/file-storage.spec.ts` (new)
- **Pattern:** Follow `libs/storage/__tests__/audit-logs.spec.ts` pattern
- **Dependencies:** Task 3
- **Agent:** `qa-engineer`
- **Complexity:** S

### Task 12: Add Swagger documentation for file endpoints
- **Action:** Create `apps/api/src/config/swagger/schemas/file.swagger.ts` with OpenAPI schema definitions for FileAttachment response, upload request/response, error responses. Verify Swagger UI renders correctly at `/api-docs`.
- **Files:** `apps/api/src/config/swagger/schemas/file.swagger.ts` (new)
- **Pattern:** Follow `apps/api/src/config/swagger/schemas/skill.swagger.ts` pattern
- **Dependencies:** Task 7
- **Agent:** `express-api-developer`
- **Complexity:** S

---

## Task Dependency Graph

```
Phase 1 (parallel):
  Task 1 ─┐
  Task 2 ─┤
  Task 3 ─┘
           │
Phase 2 (sequential within, parallel with Phase 1 where possible):
           ├── Task 4 (depends: Task 1)
           ├── Task 5 (depends: Task 1, Task 3)
           ├── Task 6 (depends: Task 4, Task 5)
           └── Task 7 (depends: Task 4, Task 6)
                │
Phase 3 (depends on Phase 2):
                ├── Task 8 (depends: Task 7)
                └── Task 9 (depends: Task 8)
                     │
Phase 4 (parallel, depends on relevant implementation):
                     ├── Task 10 (depends: Task 7)
                     ├── Task 11 (depends: Task 3)
                     └── Task 12 (depends: Task 7)
```

## Summary

| Phase | Tasks | Parallel Agents | Estimated Time |
|-------|-------|-----------------|----------------|
| Phase 1: Setup | 1, 2, 3 | database-schema-specialist, devops-infrastructure, express-api-developer | 1-2 hours |
| Phase 2: API | 4, 5, 6, 7 | express-api-developer | 3-5 hours |
| Phase 3: Web | 8, 9 | frontend-developer, ui-developer | 2-3 hours |
| Phase 4: Testing | 10, 11, 12 | qa-engineer, express-api-developer | 2-3 hours |
| **Total** | **12 tasks** | **5 agent types** | **8-13 hours** |
