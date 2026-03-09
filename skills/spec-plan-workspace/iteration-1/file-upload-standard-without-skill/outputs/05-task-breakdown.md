# Task Breakdown: File Upload for Workflow Steps

**Feature:** File Attachment Support for Workflow Steps
**Version:** 1.0
**Date:** 2026-03-09
**Estimated Total:** 45-55 engineering hours

---

## Phase 1: Foundation (Infrastructure & Schema)

### Task 1.1: Prisma Schema - Add FileAttachment Model
**Assignee type:** database-schema-specialist
**Estimated hours:** 2
**Priority:** P0 (blocking)

**Description:**
Add the `FileAttachment` model to the Prisma schema and create the migration.

**Files to modify:**
- `/home/artsmc/applications/low-code/apps/api/prisma/schema.prisma`
  - Add `FileAttachment` model with all fields
  - Add `fileAttachments` relation to `Workflow` model

**Acceptance criteria:**
- [ ] `FileAttachment` model defined with all fields from database schema spec
- [ ] `Workflow` model updated with `fileAttachments FileAttachment[]` relation
- [ ] `onDelete: Cascade` set on workflowId foreign key
- [ ] All indexes defined (workflowId, workflowId+stepId, uploadedBy, createdAt)
- [ ] Migration generated and applied successfully
- [ ] `prisma generate` produces updated client types

**Commands:**
```bash
cd /home/artsmc/applications/low-code
nx run api:prisma-migrate -- --name add_file_attachments
nx run api:prisma-generate
```

---

### Task 1.2: Extend Storage Library - File Upload/Download Utilities
**Assignee type:** express-api-developer
**Estimated hours:** 4
**Priority:** P0 (blocking)

**Description:**
Extend the `libs/storage` library with file upload, download, and delete operations on S3.

**Files to create/modify:**
- `/home/artsmc/applications/low-code/libs/storage/src/file-operations.ts` (new)
- `/home/artsmc/applications/low-code/libs/storage/src/types.ts` (extend)
- `/home/artsmc/applications/low-code/libs/storage/src/index.ts` (export new operations)

**Key functions to implement:**
```typescript
// file-operations.ts
uploadFile(bucket: string, key: string, body: Buffer, contentType: string): Promise<void>
deleteFile(bucket: string, key: string): Promise<void>
getPresignedDownloadUrl(bucket: string, key: string, expirySeconds: number, filename: string): Promise<string>
fileExists(bucket: string, key: string): Promise<boolean>
```

**Acceptance criteria:**
- [ ] `uploadFile` sends PutObjectCommand with AES-256 server-side encryption
- [ ] `deleteFile` sends DeleteObjectCommand with error handling
- [ ] `getPresignedDownloadUrl` generates presigned URL with configurable expiry
- [ ] `fileExists` uses HeadObjectCommand to check existence
- [ ] All functions use the existing `getS3Client()` singleton
- [ ] All S3 errors are wrapped via existing `toStorageError()`
- [ ] Unit tests with mocked S3 client

**Dependencies:**
- New npm dependency: `@aws-sdk/s3-request-presigner`

---

### Task 1.3: Install Dependencies
**Assignee type:** express-api-developer
**Estimated hours:** 0.5
**Priority:** P0 (blocking)

**Description:**
Install required npm packages.

**Commands:**
```bash
cd /home/artsmc/applications/low-code
npm install multer @aws-sdk/s3-request-presigner file-type --workspace=apps/api
npm install -D @types/multer --workspace=apps/api
npm install @aws-sdk/s3-request-presigner --workspace=libs/storage
```

**Acceptance criteria:**
- [ ] `multer` added to apps/api dependencies
- [ ] `@types/multer` added to apps/api devDependencies
- [ ] `@aws-sdk/s3-request-presigner` added to libs/storage dependencies
- [ ] `file-type` added to apps/api dependencies (for magic byte MIME detection)
- [ ] `npm install` runs without errors
- [ ] TypeScript compilation succeeds

---

## Phase 2: API Backend

### Task 2.1: FileAttachment Repository
**Assignee type:** express-api-developer
**Estimated hours:** 3
**Priority:** P0 (blocking)

**Description:**
Implement the repository interface and Prisma implementation for FileAttachment.

**Files to create:**
- `/home/artsmc/applications/low-code/apps/api/src/repositories/interfaces/file-attachment.repository.interface.ts`
- `/home/artsmc/applications/low-code/apps/api/src/repositories/implementations/prisma-file-attachment.repository.ts`

**Files to modify:**
- `/home/artsmc/applications/low-code/apps/api/src/repositories/index.ts` (add exports and singleton factory)

**Methods to implement:**
- `create(data)` - Insert new FileAttachment record
- `findById(id)` - Find by CUID
- `findByWorkflowAndStep(workflowId, stepId, options)` - Paginated list
- `findByWorkflow(workflowId)` - All files for a workflow (for execution context)
- `delete(id)` - Delete single record
- `deleteByWorkflow(workflowId)` - Bulk delete (for cascade)
- `getTotalSizeByUser(userId)` - Sum of sizeBytes for quota checking
- `getTotalSizeByWorkflow(workflowId)` - Sum of sizeBytes for quota checking

**Acceptance criteria:**
- [ ] Interface defined with all required methods
- [ ] Prisma implementation uses singleton PrismaClient
- [ ] Pagination follows existing PaginatedResult pattern
- [ ] Singleton factory function `getFileAttachmentRepository()` added to index.ts
- [ ] Unit tests with mocked Prisma client

---

### Task 2.2: File Service Layer
**Assignee type:** express-api-developer
**Estimated hours:** 5
**Priority:** P0 (blocking)

**Description:**
Create a service that orchestrates file operations between the repository (metadata) and S3 (binary storage).

**Files to create:**
- `/home/artsmc/applications/low-code/apps/api/src/services/file.service.ts`

**Methods to implement:**
- `uploadFile(workflowId, stepId, file, userId, description?)` - Orchestrate upload
- `listFiles(workflowId, stepId, options)` - Delegate to repository
- `getFileMetadata(fileId)` - Delegate to repository
- `getDownloadUrl(fileId)` - Generate presigned URL
- `deleteFile(fileId)` - Delete from S3 and database
- `getFilesForExecution(workflowId)` - Get all files with presigned URLs for execution context
- `validateQuota(userId, workflowId, fileSize)` - Check storage quotas

**Business logic:**
- Filename sanitization
- MIME type detection from file buffer (magic bytes)
- S3 key construction
- Quota validation (per-user and per-workflow)
- "Database first, S3 second" pattern with cleanup on failure
- Audit logging integration

**Acceptance criteria:**
- [ ] Upload flow: validate MIME -> check quota -> create DB record -> upload to S3 -> return metadata
- [ ] On S3 failure after DB insert: delete the DB record (cleanup)
- [ ] Filename sanitization removes path traversal characters
- [ ] MIME detection uses `file-type` package on the buffer
- [ ] Presigned URL generation with configurable expiry
- [ ] Quota checking queries are efficient (aggregation query)
- [ ] All operations log audit events
- [ ] Unit tests with mocked repository and S3 operations

---

### Task 2.3: Zod Validation Schemas
**Assignee type:** express-api-developer
**Estimated hours:** 1.5
**Priority:** P0 (blocking)

**Description:**
Create Zod schemas for file endpoint validation.

**Files to create:**
- `/home/artsmc/applications/low-code/apps/api/src/schemas/file.schema.ts`

**Schemas to define:**
- `FilePathParamsSchema` - { workflowId: CUID, stepId: string }
- `FileIdPathParamsSchema` - extends above with { fileId: CUID }
- `FileUploadMetadataSchema` - { description?: string }
- `ListFilesQuerySchema` - Pagination + Sort
- `FileResponseSchema` - Response shape for documentation

**Acceptance criteria:**
- [ ] All schemas follow existing patterns from `common.schema.ts`
- [ ] TypeScript types exported for all schemas
- [ ] Strict mode applied where appropriate
- [ ] Consistent with existing CUID validation patterns

---

### Task 2.4: File Controller
**Assignee type:** express-api-developer
**Estimated hours:** 4
**Priority:** P0 (blocking)

**Description:**
Implement the controller with all five endpoint handlers.

**Files to create:**
- `/home/artsmc/applications/low-code/apps/api/src/controllers/file.controller.ts`

**Methods to implement:**
- `upload` - Handle multipart upload, call file service
- `list` - List files for a workflow step
- `getMetadata` - Get single file metadata
- `download` - Generate presigned URL and redirect
- `remove` - Delete file

**Pattern:** Extend `BaseController` following the same patterns as `WorkflowController`:
- Use `this.asyncHandler()` for error handling
- Use `this.requireUser()` for authentication
- Use `this.assertOwnership()` for authorization
- Access validated data from `req.validatedParams`, `req.validatedQuery`

**Acceptance criteria:**
- [ ] Controller extends BaseController
- [ ] All handlers use asyncHandler wrapper
- [ ] Ownership checked on every operation (load workflow, assert ownership)
- [ ] stepId validated against workflow definition nodes
- [ ] Upload handler processes multer file from `req.file`
- [ ] Download returns 302 redirect with presigned URL
- [ ] Delete returns 204 No Content
- [ ] Proper HTTP status codes (201 for create, 200 for get/list, 302 for download, 204 for delete)
- [ ] All error scenarios covered (404, 403, 413, 400)

---

### Task 2.5: File Routes
**Assignee type:** express-api-developer
**Estimated hours:** 2
**Priority:** P0 (blocking)

**Description:**
Define Express routes and wire up middleware (auth, validation, multer).

**Files to create:**
- `/home/artsmc/applications/low-code/apps/api/src/routes/files.ts`

**Files to modify:**
- `/home/artsmc/applications/low-code/apps/api/src/routes/index.ts` (mount file routes)

**Route definitions:**
```
POST   /:workflowId/steps/:stepId/files           → multer + file.controller.upload
GET    /:workflowId/steps/:stepId/files           → file.controller.list
GET    /:workflowId/steps/:stepId/files/:fileId   → file.controller.getMetadata
GET    /:workflowId/steps/:stepId/files/:fileId/download → file.controller.download
DELETE /:workflowId/steps/:stepId/files/:fileId   → file.controller.remove
```

**Acceptance criteria:**
- [ ] Routes defined with Swagger JSDoc annotations
- [ ] multer middleware applied only to POST route
- [ ] Validation middleware applied to all routes (params, query)
- [ ] Auth middleware applied
- [ ] Routes registered in main router index
- [ ] Swagger annotations match API design spec

---

### Task 2.6: Swagger Documentation
**Assignee type:** express-api-developer
**Estimated hours:** 1.5
**Priority:** P1

**Description:**
Add comprehensive Swagger/OpenAPI annotations to all file routes.

**Files to modify:**
- `/home/artsmc/applications/low-code/apps/api/src/routes/files.ts` (JSDoc annotations)

**Acceptance criteria:**
- [ ] All five endpoints documented with request/response schemas
- [ ] Upload endpoint documented with multipart/form-data content type
- [ ] Error responses documented (400, 401, 403, 404, 413, 429)
- [ ] Schema references work in Swagger UI
- [ ] Documentation accessible at `/api-docs`

---

## Phase 3: Workflow Execution Integration

### Task 3.1: Inject File References into Execution Context
**Assignee type:** express-api-developer
**Estimated hours:** 3
**Priority:** P1

**Description:**
When a workflow is executed, resolve all file attachments and inject presigned URLs into step inputs.

**Files to modify:**
- `/home/artsmc/applications/low-code/apps/api/src/controllers/workflow.controller.ts` (execute method)
- `/home/artsmc/applications/low-code/apps/api/src/services/file.service.ts` (getFilesForExecution method)

**Behavior:**
1. Before calling `mastraService.executeWorkflow()`, resolve all `FileAttachment` records for the workflow.
2. Group files by stepId.
3. For each file, generate a presigned download URL (1-hour expiry).
4. Inject a `_files` array into the step input for each step that has attachments:
```json
{
  "input": {
    "originalParam": "value",
    "_files": [
      {
        "fileId": "cl...",
        "filename": "data.csv",
        "mimeType": "text/csv",
        "sizeBytes": 1048576,
        "downloadUrl": "https://..."
      }
    ]
  }
}
```

**Acceptance criteria:**
- [ ] File references resolved before workflow execution
- [ ] Presigned URLs generated with 1-hour expiry
- [ ] `_files` array injected only for steps that have attachments
- [ ] Steps without attachments are unaffected
- [ ] No file references leak to steps they don't belong to
- [ ] Execution continues normally if no files are attached
- [ ] Unit tests verify file injection logic

---

## Phase 4: Web Frontend

### Task 4.1: File Upload API Hooks
**Assignee type:** frontend-developer
**Estimated hours:** 3
**Priority:** P1

**Description:**
Create TanStack Query hooks for file operations.

**Files to create:**
- `/home/artsmc/applications/low-code/apps/web/src/hooks/use-files.ts`

**Hooks to implement:**
- `useFiles(workflowId, stepId)` - List files (query)
- `useUploadFile()` - Upload mutation (multipart FormData)
- `useDeleteFile()` - Delete mutation
- `useFileDownloadUrl(workflowId, stepId, fileId)` - Get download URL

**Acceptance criteria:**
- [ ] Hooks follow existing patterns from `use-workflows.ts`
- [ ] Upload sends FormData (not JSON)
- [ ] Query invalidation on upload/delete success
- [ ] Error handling consistent with existing hooks

### Task 4.2: File Upload UI Component
**Assignee type:** ui-developer
**Estimated hours:** 5
**Priority:** P1

**Description:**
Build a file upload component for the workflow step configuration panel.

**Files to create:**
- `/home/artsmc/applications/low-code/apps/web/src/components/workflow-builder/FileUpload.tsx`
- `/home/artsmc/applications/low-code/apps/web/src/components/workflow-builder/FileList.tsx`

**UI features:**
- Drag-and-drop zone for file upload
- File type restriction hints
- Upload progress indicator
- File list with name, size, type, upload date
- Download link for each file
- Delete button with confirmation
- Error states (size limit, type not allowed, quota exceeded)

**Acceptance criteria:**
- [ ] Drag-and-drop file upload works
- [ ] Click-to-browse fallback works
- [ ] File size and type validated client-side before upload
- [ ] Upload progress shown to user
- [ ] File list displays after successful upload
- [ ] Download link opens file in new tab
- [ ] Delete shows confirmation dialog
- [ ] Error messages are user-friendly
- [ ] Accessible (keyboard navigation, screen reader labels)
- [ ] Responsive layout

### Task 4.3: Integrate FileUpload into Workflow Builder
**Assignee type:** frontend-developer
**Estimated hours:** 2
**Priority:** P1

**Description:**
Wire the FileUpload component into the workflow step configuration panel.

**Files to modify:**
- Workflow builder step configuration panel component (identified during implementation)

**Acceptance criteria:**
- [ ] File upload section appears in step config panel
- [ ] Only shows for step types that support file inputs
- [ ] workflowId and stepId passed correctly from context
- [ ] File operations reflect immediately in the UI

---

## Phase 5: Testing

### Task 5.1: API Integration Tests
**Assignee type:** qa-engineer
**Estimated hours:** 5
**Priority:** P1

**Description:**
Write integration tests for all file endpoints.

**Files to create:**
- `/home/artsmc/applications/low-code/apps/api/__test__/files.integration.test.ts`

**Test scenarios:**
- Upload file successfully (201)
- Upload rejected: file too large (413)
- Upload rejected: disallowed MIME type (400)
- Upload rejected: workflow not found (404)
- Upload rejected: stepId not in definition (400)
- Upload rejected: not workflow owner (403)
- List files for step (200, paginated)
- Get file metadata (200)
- Download file (302 redirect)
- Delete file (204)
- Delete file by non-owner (403)
- Quota exceeded (413)
- Cascade deletion when workflow deleted

**Acceptance criteria:**
- [ ] All happy paths tested
- [ ] All error paths tested
- [ ] Tests use Supertest + test database
- [ ] S3 operations mocked or use LocalStack
- [ ] Tests clean up after themselves

### Task 5.2: Storage Library Unit Tests
**Assignee type:** qa-engineer
**Estimated hours:** 2
**Priority:** P1

**Description:**
Unit tests for new file operations in libs/storage.

**Files to create:**
- `/home/artsmc/applications/low-code/libs/storage/__tests__/file-operations.test.ts`

**Acceptance criteria:**
- [ ] Upload, download URL generation, delete, exists operations tested
- [ ] S3 client mocked
- [ ] Error handling tested (ObjectNotFound, AccessDenied, etc.)

### Task 5.3: Frontend Component Tests
**Assignee type:** qa-engineer
**Estimated hours:** 3
**Priority:** P2

**Description:**
React Testing Library tests for file upload components.

**Acceptance criteria:**
- [ ] FileUpload component renders correctly
- [ ] Drag-and-drop simulation
- [ ] Upload success/error states
- [ ] FileList renders file entries
- [ ] Delete confirmation flow

---

## Phase 6: Operations & Documentation

### Task 6.1: Environment Configuration
**Assignee type:** devops-infrastructure
**Estimated hours:** 1
**Priority:** P1

**Description:**
Update environment templates and configuration.

**Files to modify:**
- `/home/artsmc/applications/low-code/apps/api/example.env` (add new env vars)

**New environment variables:**
```
FILE_UPLOAD_BUCKET=forge-uploads-dev
MAX_UPLOAD_FILE_SIZE=52428800
ALLOWED_FILE_TYPES=application/pdf,text/csv,application/json,text/plain,image/png,image/jpeg
USER_STORAGE_QUOTA_BYTES=1073741824
WORKFLOW_STORAGE_QUOTA_BYTES=524288000
PRESIGNED_URL_EXPIRY_SECONDS=900
```

**Acceptance criteria:**
- [ ] All new env vars documented in example.env with comments
- [ ] Defaults specified for all variables
- [ ] LocalStack configuration documented for local development

### Task 6.2: S3 Bucket Setup (LocalStack for Dev)
**Assignee type:** devops-infrastructure
**Estimated hours:** 1
**Priority:** P1

**Description:**
Add S3 bucket creation to Docker Compose for local development.

**Files to modify:**
- `/home/artsmc/applications/low-code/apps/api/docker-compose.yml`

**Acceptance criteria:**
- [ ] LocalStack service added (if not already present)
- [ ] Upload bucket auto-created on startup
- [ ] S3_ENDPOINT configured for LocalStack

---

## Summary

| Phase | Tasks | Hours | Priority |
|-------|-------|-------|----------|
| 1. Foundation | 3 tasks | 6.5h | P0 |
| 2. API Backend | 6 tasks | 17h | P0-P1 |
| 3. Execution Integration | 1 task | 3h | P1 |
| 4. Web Frontend | 3 tasks | 10h | P1 |
| 5. Testing | 3 tasks | 10h | P1-P2 |
| 6. Operations | 2 tasks | 2h | P1 |
| **Total** | **18 tasks** | **48.5h** | |

## Critical Path

```
Task 1.1 (Schema) → Task 1.2 (Storage Lib) → Task 2.1 (Repository)
                  → Task 1.3 (Dependencies) ↗
                                              → Task 2.2 (Service) → Task 2.3 (Schemas)
                                                                    → Task 2.4 (Controller)
                                                                    → Task 2.5 (Routes)
                                                                       → Task 3.1 (Execution)
                                                                       → Task 5.1 (API Tests)

Task 2.5 (Routes) → Task 4.1 (Hooks) → Task 4.2 (UI) → Task 4.3 (Integration)
                                                        → Task 5.3 (Frontend Tests)
```

**Parallel tracks after Phase 1:**
- Backend API development (Phase 2) can proceed independently
- Frontend development (Phase 4) can start once Task 2.5 is complete
- Testing (Phase 5) runs alongside development
- Operations (Phase 6) can proceed in parallel from the start
