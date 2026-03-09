# Technical Requirements: Workflow File Attachments

**Feature Name:** workflow-file-attachments
**Version:** 1.0
**Date:** 2026-03-09

---

## 1. API Contracts

### 1.1 POST /api/files/presign-upload

Generate a presigned S3 URL for direct file upload.

**Auth:** Required (JWT Bearer)

**Request Body:**
```json
{
  "workflowId": "string (cuid)",
  "stepId": "string (optional, workflow step identifier)",
  "filename": "string (1-255 chars)",
  "contentType": "string (MIME type)",
  "fileSize": "number (bytes, 1 - 52428800)"
}
```

**Response 200:**
```json
{
  "data": {
    "uploadUrl": "string (presigned S3 PUT URL)",
    "fileId": "string (cuid, pre-generated)",
    "s3Key": "string (S3 object key)",
    "expiresAt": "string (ISO 8601, ~15 min from now)"
  }
}
```

**Errors:**
- 400: Invalid request (bad content type, size out of range, missing fields)
- 401: Not authenticated
- 403: User does not own the workflow
- 404: Workflow not found
- 413: File size exceeds 50MB limit

### 1.2 POST /api/files/confirm-upload

Confirm that a presigned upload completed successfully. Creates the DB record.

**Auth:** Required (JWT Bearer)

**Request Body:**
```json
{
  "fileId": "string (cuid, from presign-upload response)",
  "workflowId": "string (cuid)",
  "s3Key": "string (from presign-upload response)"
}
```

**Response 201:**
```json
{
  "data": {
    "id": "string (cuid)",
    "filename": "string",
    "contentType": "string",
    "fileSize": "number",
    "s3Key": "string",
    "workflowId": "string",
    "stepId": "string | null",
    "uploadedBy": "string (userId)",
    "createdAt": "string (ISO 8601)"
  }
}
```

**Errors:**
- 400: Invalid request or file not found in S3
- 401: Not authenticated
- 403: User does not own the workflow
- 404: Workflow not found
- 409: FileId already confirmed

### 1.3 GET /api/files?workflowId=xxx

List file attachments for a workflow.

**Auth:** Required (JWT Bearer)

**Query Parameters:**
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| workflowId | string (cuid) | required | Filter by workflow |
| stepId | string | optional | Filter by workflow step |
| page | int | 1 | Page number |
| limit | int | 20 | Items per page (max 100) |
| sortBy | string | createdAt | Sort field |
| sortOrder | asc/desc | desc | Sort direction |

**Response 200:**
```json
{
  "data": [
    {
      "id": "string",
      "filename": "string",
      "contentType": "string",
      "fileSize": "number",
      "workflowId": "string",
      "stepId": "string | null",
      "uploadedBy": "string",
      "createdAt": "string"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 42,
    "totalPages": 3
  }
}
```

**Errors:**
- 400: Invalid query parameters
- 401: Not authenticated
- 403: User does not have access to the workflow

### 1.4 GET /api/files/:id/download

Generate a presigned S3 download URL (or stream the file).

**Auth:** Required (JWT Bearer)

**Response 200:**
```json
{
  "data": {
    "downloadUrl": "string (presigned S3 GET URL)",
    "filename": "string",
    "contentType": "string",
    "fileSize": "number",
    "expiresAt": "string (ISO 8601, ~15 min)"
  }
}
```

**Errors:**
- 401: Not authenticated
- 403: User does not have access to the parent workflow
- 404: File not found

### 1.5 DELETE /api/files/:id

Delete a file attachment (S3 object + DB record).

**Auth:** Required (JWT Bearer)

**Response 204:** No content

**Errors:**
- 401: Not authenticated
- 403: User does not own the file (or parent workflow)
- 404: File not found

---

## 2. Data Model Changes

### 2.1 New Prisma Model: FileAttachment

```prisma
model FileAttachment {
  id          String  @id @default(cuid())
  filename    String                         // Original filename (display)
  contentType String                         // MIME type
  fileSize    Int                            // Size in bytes
  s3Key       String                         // S3 object key
  s3Bucket    String                         // S3 bucket name
  stepId      String?                        // Optional workflow step reference

  // Ownership
  workflowId  String
  workflow     Workflow @relation(fields: [workflowId], references: [id], onDelete: Cascade)
  uploadedBy  String                         // userId of uploader

  // Timestamps
  createdAt   DateTime @default(now())

  // Indexes
  @@index([workflowId])
  @@index([uploadedBy])
  @@index([workflowId, stepId])
  @@map("file_attachments")
}
```

### 2.2 Workflow Model Update

Add relation to FileAttachment:

```prisma
model Workflow {
  // ... existing fields ...
  fileAttachments FileAttachment[]
}
```

### 2.3 Migration Strategy

- Create migration via `prisma migrate dev --name add-file-attachments`
- Migration adds `file_attachments` table with foreign key to `workflows`
- No data migration needed (new table)
- Rollback: Drop `file_attachments` table

---

## 3. S3 Storage Design

### 3.1 Bucket and Key Structure

**Bucket:** `forge-file-uploads-{env}` (e.g., `forge-file-uploads-dev`, `forge-file-uploads-prod`)

**Key pattern:** `files/{workflowId}/{fileId}/{sanitized-filename}`

Example: `files/clx123abc/clx456def/data-export.csv`

### 3.2 Storage Library Extensions (libs/storage)

New exports to add to `libs/storage/src/index.ts`:

```typescript
// File operations
export { uploadFile, getFileStream, deleteFile, generatePresignedUploadUrl, generatePresignedDownloadUrl } from './file-storage';

// File types
export type { FileUploadParams, FileMetadata } from './types';
```

### 3.3 Presigned URL Configuration

| Parameter | Value |
|-----------|-------|
| Upload URL expiry | 15 minutes |
| Download URL expiry | 15 minutes |
| Max file size (enforced in presigned URL conditions) | 52,428,800 bytes (50MB) |
| Allowed content types | Configurable allowlist (see Section 5) |

---

## 4. Dependencies

### New npm Packages

| Package | Version | Purpose | App |
|---------|---------|---------|-----|
| `@aws-sdk/s3-request-presigner` | ^3.x | Generate presigned S3 URLs | libs/storage |
| `multer` | ^2.x | Multipart form-data parsing (fallback upload route) | apps/api |
| `@types/multer` | ^2.x | TypeScript types for multer | apps/api (dev) |

### Existing Dependencies (No Changes)

| Package | Current | Used For |
|---------|---------|----------|
| `@aws-sdk/client-s3` | (in libs/storage) | S3 operations |
| `zod` | ^4.3.6 | Request validation |
| `express` | 5.2.1 | HTTP framework |

---

## 5. Error Handling Strategy

All errors follow the RFC 7807 Problem Details format via `ApiError` class.

| Error | HTTP Status | Error Type URL |
|-------|-------------|----------------|
| File too large | 413 | `https://api.productforge.dev/errors/file-too-large` |
| Unsupported file type | 400 | `https://api.productforge.dev/errors/unsupported-file-type` |
| File not found | 404 | `https://api.productforge.dev/errors/not-found` |
| S3 unavailable | 503 | `https://api.productforge.dev/errors/service-unavailable` |
| Upload not confirmed | 400 | `https://api.productforge.dev/errors/upload-not-confirmed` |
| Duplicate confirmation | 409 | `https://api.productforge.dev/errors/conflict` |

### File Type Allowlist

```
application/pdf, application/json, text/plain, text/csv,
image/png, image/jpeg, image/gif,
application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,
application/vnd.openxmlformats-officedocument.wordprocessingml.document,
application/zip, application/gzip
```

---

## 6. Security Considerations

### 6.1 Access Control
- All file endpoints require JWT authentication
- Upload/delete: user must own the parent workflow OR be ADMIN
- Download/list: user must own the parent workflow, be a team member, or be ADMIN
- Presigned URLs are scoped to specific S3 keys (no wildcard)

### 6.2 Input Validation
- Filename: sanitized (strip path separators, null bytes, control chars)
- Content-type: validated against allowlist
- File size: enforced both in presigned URL conditions and API validation
- S3 key: never user-provided (generated server-side from fileId + workflowId)

### 6.3 Audit Logging
- Log all file operations: UPLOAD, DOWNLOAD, DELETE
- Audit fields: userId, fileId, workflowId, action, timestamp, fileSize
- Do NOT log: file contents, full original filename (may contain PII)
- Logs go to AuditLog table (existing pattern)

### 6.4 S3 Security
- Bucket policy: deny public access
- Server-side encryption: AES-256 (SSE-S3) or KMS
- Presigned URLs include content-type and content-length conditions
- CORS on S3 bucket: allow origin from web app domain only

---

## 7. Performance Requirements

| Metric | Requirement |
|--------|-------------|
| Presigned URL generation | < 200ms p95 |
| File metadata CRUD | < 100ms p95 |
| List files (paginated) | < 200ms p95 |
| Max concurrent uploads per user | 5 |
| S3 bucket region | Same region as API (us-east-1) for low latency |

---

## 8. Infrastructure Needs

### New Resources
- S3 bucket: `forge-file-uploads-{env}` with:
  - Lifecycle rule: delete incomplete multipart uploads after 7 days
  - CORS configuration for web app domain
  - Server-side encryption enabled
  - Versioning: disabled (v1, no file versioning)
- IAM permissions: `s3:PutObject`, `s3:GetObject`, `s3:DeleteObject`, `s3:ListBucket` on the new bucket

### LocalStack Configuration
- Add bucket creation to `infrastructure/local/localstack-init.sh`
- Ensure presigned URLs work with LocalStack endpoint
