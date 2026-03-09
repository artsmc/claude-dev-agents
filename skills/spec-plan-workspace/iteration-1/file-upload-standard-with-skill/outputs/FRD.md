# Feature Requirements Document: Workflow File Attachments

**Feature Name:** workflow-file-attachments
**Version:** 1.0
**Status:** Draft
**Date:** 2026-03-09
**Author:** spec-plan (automated)

---

## 1. Feature Overview

### What
Enable users to attach files to workflow steps. Files are stored in Amazon S3 and referenced via metadata in the PostgreSQL database. The API exposes endpoints for uploading, downloading, listing, and deleting file attachments. The web frontend provides a file upload UI within the workflow builder.

### Why
Users building workflows often need to reference external data -- configuration files, CSV datasets, template documents, or reference images. Without file attachment support, users must manually manage files outside the platform and hardcode external URLs into workflow definitions. This creates a fragmented experience and prevents workflows from being self-contained and portable.

### Scope
- **In scope:** Upload, download, list, delete files via API. File metadata in DB. S3 storage. Web upload UI. Presigned URL generation. File type/size validation. Audit logging.
- **Out of scope:** File versioning (future enhancement). File preview/rendering. Virus scanning (infrastructure concern, not application). Batch upload API. File sharing across workflows.

---

## 2. User Stories

### US-1: Attach a File to a Workflow Step
**As a** workflow builder,
**I want to** upload a file and associate it with a specific step in my workflow,
**So that** the file is available as input when that workflow step executes.

**Acceptance Criteria:**
- User can select a file (up to 50MB) from their local machine
- File is uploaded to S3 and metadata is persisted in the database
- File is associated with a specific workflow ID and optionally a step identifier
- Upload progress is visible in the UI
- Upload succeeds for common file types (PDF, CSV, JSON, TXT, PNG, JPG, XLSX, ZIP)

### US-2: Download an Attached File
**As a** workflow builder,
**I want to** download a file that was previously attached to a workflow step,
**So that** I can review or update the file contents.

**Acceptance Criteria:**
- User can click a download link/button for any attached file
- File downloads with its original filename
- Download works for the file owner and team members with access to the workflow
- Non-owners without access receive a 403 error

### US-3: List Files for a Workflow
**As a** workflow builder,
**I want to** see all files attached to my workflow,
**So that** I can manage attachments and understand what data the workflow uses.

**Acceptance Criteria:**
- File list shows: filename, size, upload date, associated step (if any), content type
- List is paginated (default 20 per page)
- Files are sorted by upload date (newest first) by default

### US-4: Delete an Attached File
**As a** workflow builder,
**I want to** remove a file attachment from a workflow step,
**So that** I can clean up unused files and manage storage.

**Acceptance Criteria:**
- User can delete any file they own
- ADMIN users can delete any file
- Deletion removes both the S3 object and the database record
- Deletion is audited
- Deleted files cannot be recovered (no soft delete in v1)

### US-5: Presigned URL for Direct Upload
**As a** system,
**I want to** generate presigned S3 URLs for file uploads,
**So that** large files bypass the API server and upload directly to S3, reducing server load.

**Acceptance Criteria:**
- API returns a presigned PUT URL with a 15-minute expiration
- Client uploads directly to S3 using the presigned URL
- After upload completes, client confirms via a separate API call to register metadata
- Presigned URL is scoped to the specific S3 key (no wildcard access)

---

## 3. Edge Cases and Error Scenarios

| Scenario | Expected Behavior |
|----------|-------------------|
| File exceeds 50MB limit | API returns 413 Payload Too Large with RFC 7807 error |
| Unsupported file type | API returns 400 Bad Request with list of allowed types |
| Upload to non-existent workflow | API returns 404 Not Found |
| Upload by non-owner of workflow | API returns 403 Forbidden |
| S3 service unavailable | API returns 503 Service Unavailable |
| Download of deleted file | API returns 404 Not Found |
| Presigned URL expired | S3 returns 403; client should request a new presigned URL |
| Concurrent uploads to same workflow | Both succeed (unique file IDs) |
| File with duplicate name in same workflow | Allowed -- files have unique IDs, names are display-only |
| Empty file (0 bytes) | Rejected with 400 Bad Request |
| Filename with special characters | Sanitized for S3 key; original name preserved in metadata |

---

## 4. Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Upload success rate | >= 99% (excluding client-side cancellations) | API logs + S3 upload completion events |
| Upload latency (presigned URL generation) | < 200ms p95 | API response time metrics |
| Download latency (presigned URL generation) | < 200ms p95 | API response time metrics |
| File attachment adoption | >= 30% of active workflows have at least 1 file within 30 days of launch | Database query on FileAttachment count |
| Storage cost efficiency | < $0.05/workflow/month average | S3 billing metrics per workflow |

---

## 5. Dependencies and Assumptions

### Dependencies
- `libs/storage` S3 client infrastructure (exists)
- `@aws-sdk/s3-request-presigner` package (new dependency)
- `multer` package for multipart fallback (new dependency)
- S3 bucket for file storage (new bucket or new prefix in existing bucket)
- Prisma schema migration capability

### Assumptions
- Users authenticate via existing JWT auth flow
- Workflow ownership/access checks use existing RBAC patterns
- S3 bucket exists and API service has IAM permissions (PutObject, GetObject, DeleteObject)
- LocalStack is available for local development (existing infra supports this)
- File content is opaque to the platform (no parsing or transformation)
