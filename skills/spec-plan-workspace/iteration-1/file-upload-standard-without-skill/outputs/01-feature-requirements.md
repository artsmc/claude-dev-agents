# Feature Requirements Document: File Upload for Workflow Steps

**Feature:** File Attachment Support for Workflow Steps
**Version:** 1.0
**Date:** 2026-03-09
**Status:** Draft

---

## 1. Overview

Enable users to attach files to individual workflow steps. Files are stored in Amazon S3, and the API service exposes new endpoints for uploading, downloading, listing, and deleting file attachments. The web frontend provides a drag-and-drop file upload UI within the workflow builder.

## 2. Problem Statement

Currently, workflow steps in AIForge accept only JSON-serializable input parameters. Users who need to process documents (PDFs, CSVs, images, configuration files) must host them externally and pass URLs. This creates friction, security concerns (public URLs), and traceability gaps (no audit trail for file access).

## 3. Goals

- **G-1:** Users can upload files and associate them with specific workflow steps.
- **G-2:** Files are securely stored in S3 with organization-scoped isolation.
- **G-3:** Files are accessible for download by authorized users (owner or ADMIN).
- **G-4:** File metadata is tracked in PostgreSQL for querying, audit, and lifecycle management.
- **G-5:** Uploaded files are automatically available as inputs during workflow execution (Mastra integration).
- **G-6:** All file operations are audit-logged per FedRAMP AC-3 / AU-2 requirements.

## 4. Non-Goals (v1)

- Real-time collaborative editing of uploaded files.
- File versioning (overwrite replaces; no version history).
- Virus/malware scanning (deferred to v2; noted as a security TODO).
- Direct S3 multipart upload from the browser (presigned URL flow deferred to v2 for files > 100MB).
- File preview/rendering in the web UI (v1 shows filename, size, type, and download link only).

## 5. User Stories

### US-1: Upload a File to a Workflow Step
**As a** workflow builder,
**I want to** attach a file to a specific step in my workflow,
**So that** the step can process the file during execution.

**Acceptance Criteria:**
- Upload via multipart/form-data to a dedicated API endpoint.
- File size limit: 50 MB per file (configurable via environment variable).
- Allowed MIME types: configurable allowlist (default: PDF, CSV, JSON, TXT, PNG, JPG, XLSX, DOCX).
- On success, returns file metadata (id, filename, size, mimeType, s3Key, workflowId, stepId).
- File is stored in S3 under path: `uploads/{userId}/{workflowId}/{stepId}/{fileId}/{originalFilename}`.

### US-2: List Files for a Workflow Step
**As a** workflow builder,
**I want to** see all files attached to a workflow step,
**So that** I can manage which files are available for that step.

**Acceptance Criteria:**
- GET endpoint returns paginated list of file metadata for a given workflow + step.
- Includes: id, filename, mimeType, sizeBytes, uploadedAt, uploadedBy.
- Only the workflow owner or ADMIN can list files.

### US-3: Download a File
**As a** workflow builder,
**I want to** download a previously uploaded file,
**So that** I can verify its contents or use it externally.

**Acceptance Criteria:**
- GET endpoint returns the file binary with correct Content-Type and Content-Disposition headers.
- Generates a time-limited presigned S3 URL (15-minute expiry) and redirects (302) or streams.
- Only the workflow owner or ADMIN can download.

### US-4: Delete a File
**As a** workflow builder,
**I want to** remove a file from a workflow step,
**So that** I can clean up outdated or incorrect attachments.

**Acceptance Criteria:**
- DELETE endpoint removes the file from S3 and deletes the metadata record.
- Returns 204 No Content on success.
- Only the workflow owner or ADMIN can delete.

### US-5: Use Files During Workflow Execution
**As a** workflow builder,
**I want** uploaded files to be automatically available as step inputs during execution,
**So that** my workflow steps can process them without manual URL passing.

**Acceptance Criteria:**
- When a workflow is executed, the execution context for each step includes references to attached files.
- File references include presigned download URLs (valid for the execution duration, max 1 hour).
- The Mastra engine receives file references in the step input payload.

## 6. Functional Requirements

### FR-1: File Upload Endpoint
- **Endpoint:** `POST /api/workflows/:workflowId/steps/:stepId/files`
- **Auth:** JWT required, ownership or ADMIN check.
- **Input:** Multipart form data with `file` field.
- **Validation:**
  - File size <= MAX_FILE_SIZE_BYTES (default 50MB, env: `MAX_UPLOAD_FILE_SIZE`).
  - MIME type in allowlist (env: `ALLOWED_FILE_TYPES`).
  - workflowId is a valid CUID referencing an existing workflow owned by user.
  - stepId is a string matching a node ID in the workflow definition.
- **Processing:**
  - Generate a CUID for the file record.
  - Upload file to S3 at: `uploads/{userId}/{workflowId}/{stepId}/{fileId}/{sanitizedFilename}`.
  - Create a `FileAttachment` record in PostgreSQL.
  - Log audit event: `FILE_UPLOAD`.
- **Response:** 201 Created with file metadata JSON.

### FR-2: List Files Endpoint
- **Endpoint:** `GET /api/workflows/:workflowId/steps/:stepId/files`
- **Auth:** JWT required, ownership or ADMIN check.
- **Query params:** `page`, `limit` (standard pagination).
- **Response:** 200 OK with `{ data: FileAttachment[], pagination: {...} }`.

### FR-3: Download File Endpoint
- **Endpoint:** `GET /api/workflows/:workflowId/steps/:stepId/files/:fileId/download`
- **Auth:** JWT required, ownership or ADMIN check.
- **Processing:**
  - Look up `FileAttachment` record.
  - Generate presigned S3 GET URL (15-minute expiry).
  - Return 302 redirect to presigned URL (or stream directly for smaller files).
- **Response headers:** Content-Type, Content-Disposition (attachment; filename="...").

### FR-4: Delete File Endpoint
- **Endpoint:** `DELETE /api/workflows/:workflowId/steps/:stepId/files/:fileId`
- **Auth:** JWT required, ownership or ADMIN check.
- **Processing:**
  - Delete S3 object.
  - Delete `FileAttachment` database record.
  - Log audit event: `FILE_DELETE`.
- **Response:** 204 No Content.

### FR-5: Get File Metadata Endpoint
- **Endpoint:** `GET /api/workflows/:workflowId/steps/:stepId/files/:fileId`
- **Auth:** JWT required, ownership or ADMIN check.
- **Response:** 200 OK with single `FileAttachment` metadata.

### FR-6: Cascade Deletion
- When a workflow is deleted, all associated `FileAttachment` records are cascade-deleted from the database.
- A background job should clean up corresponding S3 objects (orphan cleanup).

### FR-7: Execution Integration
- When `POST /api/workflows/:id/execute` is called, the API resolves all `FileAttachment` records for the workflow.
- For each step with attachments, presigned download URLs are generated and injected into the step's input payload under a `_files` key.
- The Mastra engine receives these URLs and makes them available to the step execution context.

## 7. Non-Functional Requirements

### NFR-1: Performance
- File upload response time < 5 seconds for files up to 10MB on a stable connection.
- File list endpoint response time < 200ms.
- Presigned URL generation < 100ms.

### NFR-2: Security
- All file operations require valid JWT authentication.
- Ownership validation on every file operation (user must own the workflow or be ADMIN).
- S3 bucket uses server-side encryption (AES-256 or AWS KMS).
- Presigned URLs expire after 15 minutes (download) or 1 hour (execution context).
- File names are sanitized to prevent path traversal attacks.
- Content-Type is validated server-side (not trusted from client headers alone).
- No PII in S3 object keys or log messages.

### NFR-3: Compliance (FedRAMP)
- All file upload, download, and delete operations logged in AuditLog table (AU-2).
- Access control enforced at API level (AC-3).
- File encryption at rest in S3 (SC-28).
- File encryption in transit via HTTPS (SC-8).

### NFR-4: Reliability
- Failed S3 uploads are retried up to 3 times with exponential backoff.
- Database and S3 operations are not in a distributed transaction; the API uses a "database first, S3 second" pattern with cleanup on S3 failure.

### NFR-5: Storage Limits
- Per-user storage quota: 1 GB (configurable, env: `USER_STORAGE_QUOTA_BYTES`).
- Per-workflow storage quota: 500 MB.
- Endpoint returns 413 Payload Too Large when quota exceeded.

## 8. Dependencies

| Dependency | Purpose | Status |
|---|---|---|
| `@aws-sdk/client-s3` | S3 operations (PutObject, GetObject, DeleteObject, presigned URLs) | Available via `libs/storage` |
| `@aws-sdk/s3-request-presigner` | Generate presigned download URLs | New dependency |
| `multer` or `busboy` | Multipart form-data parsing in Express | New dependency |
| `libs/storage` | Existing S3 client singleton, error handling | Existing, needs extension |
| Prisma schema | New `FileAttachment` model | Migration required |
| Mastra integration | Pass file references to workflow step inputs | Requires coordination |

## 9. Open Questions

1. **Q:** Should we support bulk file upload (multiple files per request)?
   **Recommendation:** v1 supports single file per request. Multiple files can be uploaded via multiple requests.

2. **Q:** Should file downloads be streamed through the API or redirected to S3 presigned URLs?
   **Recommendation:** Presigned URL redirect (302) to reduce API server load. Streaming fallback for private S3 buckets without public access.

3. **Q:** How should workflow deletion handle S3 cleanup at scale?
   **Recommendation:** Soft-delete file records, then process S3 deletions asynchronously via a background job queue.

4. **Q:** Should the stepId validation check that the step actually exists in the workflow definition?
   **Recommendation:** Yes. The API should parse `workflow.definition.nodes` and verify the stepId matches a node ID.
