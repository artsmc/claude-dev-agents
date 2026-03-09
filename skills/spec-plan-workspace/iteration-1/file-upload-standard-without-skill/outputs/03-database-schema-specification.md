# Database Schema Specification: FileAttachment Model

**Feature:** File Attachment Support for Workflow Steps
**Version:** 1.0
**Date:** 2026-03-09

---

## 1. Overview

A new `FileAttachment` Prisma model is added to track file metadata in PostgreSQL. The actual file binary is stored in S3; the database holds metadata, S3 coordinates, and ownership information.

## 2. Prisma Schema Addition

Add to `/home/artsmc/applications/low-code/apps/api/prisma/schema.prisma`:

```prisma
// ================================
// File Attachments
// ================================

model FileAttachment {
  id               String  @id @default(cuid())

  // Workflow association
  workflowId       String
  workflow         Workflow @relation(fields: [workflowId], references: [id], onDelete: Cascade)
  stepId           String   // Node ID from workflow definition (not a foreign key)

  // File metadata
  filename         String   // Sanitized filename used in S3 key
  originalFilename String   // Original filename as uploaded by user
  mimeType         String   // Validated MIME type
  sizeBytes        Int      // File size in bytes
  description      String?  @db.Text

  // S3 storage coordinates
  s3Key            String   // Full S3 object key
  s3Bucket         String   // S3 bucket name

  // Ownership and audit
  uploadedBy       String   // User ID who uploaded the file

  // Timestamps
  createdAt        DateTime @default(now())

  // Indexes
  @@index([workflowId])
  @@index([workflowId, stepId])
  @@index([uploadedBy])
  @@index([createdAt])
  @@map("file_attachments")
}
```

## 3. Relation Updates

The `Workflow` model needs a new relation field:

```prisma
model Workflow {
  // ... existing fields ...

  // Relations
  executions Execution[]
  fileAttachments FileAttachment[]  // <-- NEW

  // ... rest of model ...
}
```

## 4. Migration Plan

### 4.1 Generate Migration

```bash
cd /home/artsmc/applications/low-code
nx run api:prisma-migrate -- --name add_file_attachments
```

This generates:
- Migration SQL in `apps/api/prisma/migrations/YYYYMMDDHHMMSS_add_file_attachments/migration.sql`
- Updated Prisma Client types after `prisma generate`

### 4.2 Expected Migration SQL

```sql
-- CreateTable
CREATE TABLE "file_attachments" (
    "id" TEXT NOT NULL,
    "workflowId" TEXT NOT NULL,
    "stepId" TEXT NOT NULL,
    "filename" TEXT NOT NULL,
    "originalFilename" TEXT NOT NULL,
    "mimeType" TEXT NOT NULL,
    "sizeBytes" INTEGER NOT NULL,
    "description" TEXT,
    "s3Key" TEXT NOT NULL,
    "s3Bucket" TEXT NOT NULL,
    "uploadedBy" TEXT NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "file_attachments_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE INDEX "file_attachments_workflowId_idx" ON "file_attachments"("workflowId");
CREATE INDEX "file_attachments_workflowId_stepId_idx" ON "file_attachments"("workflowId", "stepId");
CREATE INDEX "file_attachments_uploadedBy_idx" ON "file_attachments"("uploadedBy");
CREATE INDEX "file_attachments_createdAt_idx" ON "file_attachments"("createdAt");

-- AddForeignKey
ALTER TABLE "file_attachments"
    ADD CONSTRAINT "file_attachments_workflowId_fkey"
    FOREIGN KEY ("workflowId") REFERENCES "workflows"("id")
    ON DELETE CASCADE ON UPDATE CASCADE;
```

## 5. S3 Key Structure

```
uploads/
  {userId}/
    {workflowId}/
      {stepId}/
        {fileId}/
          {sanitized-filename}
```

**Example:**
```
uploads/cluserxxxxxxxxxx/clworkflowxxxxxxxx/step-input-1/clfilexxxxxxxxxx/monthly-report.csv
```

**Design Rationale:**
- **userId prefix:** Enables per-user IAM policies and quota tracking via S3 prefix listing.
- **workflowId:** Groups all files for a workflow together for bulk operations.
- **stepId:** Allows efficient listing of files for a specific step.
- **fileId:** Prevents filename collisions (multiple uploads of same filename).
- **sanitized-filename:** Human-readable suffix for debugging/auditing.

## 6. Repository Interface

New file: `src/repositories/interfaces/file-attachment.repository.interface.ts`

```typescript
import type { FileAttachment } from '@prisma/client';
import type { PaginatedResult, ListOptions } from '../../types/repositories/common.types';

export interface CreateFileAttachmentData {
  workflowId: string;
  stepId: string;
  filename: string;
  originalFilename: string;
  mimeType: string;
  sizeBytes: number;
  s3Key: string;
  s3Bucket: string;
  description?: string;
  uploadedBy: string;
}

export interface IFileAttachmentRepository {
  create(data: CreateFileAttachmentData): Promise<FileAttachment>;
  findById(id: string): Promise<FileAttachment | null>;
  findByWorkflowAndStep(
    workflowId: string,
    stepId: string,
    options: ListOptions
  ): Promise<PaginatedResult<FileAttachment>>;
  findByWorkflow(workflowId: string): Promise<FileAttachment[]>;
  delete(id: string): Promise<void>;
  deleteByWorkflow(workflowId: string): Promise<number>;
  getTotalSizeByUser(userId: string): Promise<number>;
  getTotalSizeByWorkflow(workflowId: string): Promise<number>;
}
```

## 7. S3 Bucket Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `FILE_UPLOAD_BUCKET` | `forge-uploads-dev` | S3 bucket for file uploads |
| `MAX_UPLOAD_FILE_SIZE` | `52428800` | Max file size in bytes (50 MB) |
| `ALLOWED_FILE_TYPES` | `application/pdf,text/csv,application/json,text/plain,image/png,image/jpeg,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,application/vnd.openxmlformats-officedocument.wordprocessingml.document` | Comma-separated MIME types |
| `USER_STORAGE_QUOTA_BYTES` | `1073741824` | Per-user storage quota (1 GB) |
| `WORKFLOW_STORAGE_QUOTA_BYTES` | `524288000` | Per-workflow storage quota (500 MB) |
| `PRESIGNED_URL_EXPIRY_SECONDS` | `900` | Presigned URL expiry (15 min) |

### S3 Bucket Policy (Recommended)

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "EnforceEncryption",
      "Effect": "Deny",
      "Principal": "*",
      "Action": "s3:PutObject",
      "Resource": "arn:aws:s3:::forge-uploads-*/*",
      "Condition": {
        "StringNotEquals": {
          "s3:x-amz-server-side-encryption": "AES256"
        }
      }
    },
    {
      "Sid": "DenyUnencryptedTransport",
      "Effect": "Deny",
      "Principal": "*",
      "Action": "s3:*",
      "Resource": [
        "arn:aws:s3:::forge-uploads-*",
        "arn:aws:s3:::forge-uploads-*/*"
      ],
      "Condition": {
        "Bool": {
          "aws:SecureTransport": "false"
        }
      }
    }
  ]
}
```

## 8. Data Lifecycle

### Cascade Deletion
When a workflow is deleted via `DELETE /api/workflows/:id`:
1. Prisma cascade deletes all `FileAttachment` records (via `onDelete: Cascade`).
2. An `afterDelete` hook or background job reads the deleted file records and issues S3 `DeleteObject` calls.

### Orphan Cleanup
A scheduled background job (daily) scans for S3 objects under `uploads/` that have no corresponding `FileAttachment` record in the database, and deletes them.

### Retention
File attachments follow the same retention policy as their parent workflow. No independent TTL.
