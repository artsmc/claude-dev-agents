# API Design Specification: File Upload Endpoints

**Feature:** File Attachment Support for Workflow Steps
**Version:** 1.0
**Date:** 2026-03-09

---

## 1. Endpoint Summary

All endpoints are mounted under the existing authenticated API router at `/api`.

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| POST | `/api/workflows/:workflowId/steps/:stepId/files` | Upload a file | JWT + Owner/ADMIN |
| GET | `/api/workflows/:workflowId/steps/:stepId/files` | List files for step | JWT + Owner/ADMIN |
| GET | `/api/workflows/:workflowId/steps/:stepId/files/:fileId` | Get file metadata | JWT + Owner/ADMIN |
| GET | `/api/workflows/:workflowId/steps/:stepId/files/:fileId/download` | Download file | JWT + Owner/ADMIN |
| DELETE | `/api/workflows/:workflowId/steps/:stepId/files/:fileId` | Delete file | JWT + Owner/ADMIN |

## 2. Route Registration

New route file: `src/routes/files.ts`

Mounted in `src/routes/index.ts`:
```typescript
import fileRoutes from './files';
// Nested under workflows for ownership validation
router.use('/workflows/:workflowId/steps/:stepId/files', fileRoutes);
```

## 3. Detailed Endpoint Specifications

### 3.1 Upload File

```
POST /api/workflows/:workflowId/steps/:stepId/files
Content-Type: multipart/form-data
Authorization: Bearer <jwt>
```

**Path Parameters:**
| Param | Type | Validation | Description |
|-------|------|------------|-------------|
| workflowId | string | CUID format | Workflow identifier |
| stepId | string | non-empty string | Node ID from workflow definition |

**Request Body (multipart/form-data):**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| file | File | Yes | The file to upload |
| description | string | No | Optional description (max 255 chars) |

**Validation Rules:**
- `workflowId` must be a valid CUID pointing to an existing workflow.
- `stepId` must match a node ID in `workflow.definition.nodes[].id`.
- File size must not exceed `MAX_UPLOAD_FILE_SIZE` (default: 52,428,800 bytes / 50 MB).
- MIME type must be in the configured allowlist.
- User must own the workflow or have ADMIN role.

**Success Response (201 Created):**
```json
{
  "id": "clxxxxxxxxxxxxxxxxxxxxxxxxx",
  "workflowId": "clxxxxxxxxxxxxxxxxxxxxxxxxx",
  "stepId": "step-input-1",
  "filename": "data-import.csv",
  "originalFilename": "data-import.csv",
  "mimeType": "text/csv",
  "sizeBytes": 1048576,
  "s3Key": "uploads/cluser123/clworkflow456/step-input-1/clfile789/data-import.csv",
  "s3Bucket": "forge-uploads-dev",
  "description": "Monthly sales data",
  "uploadedBy": "clxxxxxxxxxxxxxxxxxxxxxxxxx",
  "createdAt": "2026-03-09T12:00:00.000Z"
}
```

**Error Responses:**

| Status | Code | Condition |
|--------|------|-----------|
| 400 | VALIDATION_ERROR | Invalid path params, missing file, disallowed MIME type |
| 401 | UNAUTHORIZED | Missing or invalid JWT |
| 403 | FORBIDDEN | User does not own workflow and is not ADMIN |
| 404 | NOT_FOUND | Workflow not found or stepId not in definition |
| 413 | PAYLOAD_TOO_LARGE | File exceeds size limit or quota exceeded |
| 429 | TOO_MANY_REQUESTS | Rate limit exceeded |

### 3.2 List Files

```
GET /api/workflows/:workflowId/steps/:stepId/files
Authorization: Bearer <jwt>
```

**Query Parameters:**
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| page | integer | 1 | Page number (min: 1) |
| limit | integer | 20 | Items per page (min: 1, max: 100) |
| sortBy | string | createdAt | Sort field |
| sortOrder | string | desc | Sort direction (asc/desc) |

**Success Response (200 OK):**
```json
{
  "data": [
    {
      "id": "clxxxxxxxxxxxxxxxxxxxxxxxxx",
      "workflowId": "clxxxxxxxxxxxxxxxxxxxxxxxxx",
      "stepId": "step-input-1",
      "filename": "data-import.csv",
      "mimeType": "text/csv",
      "sizeBytes": 1048576,
      "description": "Monthly sales data",
      "uploadedBy": "clxxxxxxxxxxxxxxxxxxxxxxxxx",
      "createdAt": "2026-03-09T12:00:00.000Z"
    }
  ],
  "pagination": {
    "total": 3,
    "page": 1,
    "limit": 20,
    "totalPages": 1
  }
}
```

### 3.3 Get File Metadata

```
GET /api/workflows/:workflowId/steps/:stepId/files/:fileId
Authorization: Bearer <jwt>
```

**Success Response (200 OK):**
```json
{
  "id": "clxxxxxxxxxxxxxxxxxxxxxxxxx",
  "workflowId": "clxxxxxxxxxxxxxxxxxxxxxxxxx",
  "stepId": "step-input-1",
  "filename": "data-import.csv",
  "originalFilename": "data-import.csv",
  "mimeType": "text/csv",
  "sizeBytes": 1048576,
  "s3Key": "uploads/cluser123/clworkflow456/step-input-1/clfile789/data-import.csv",
  "s3Bucket": "forge-uploads-dev",
  "description": "Monthly sales data",
  "uploadedBy": "clxxxxxxxxxxxxxxxxxxxxxxxxx",
  "createdAt": "2026-03-09T12:00:00.000Z"
}
```

### 3.4 Download File

```
GET /api/workflows/:workflowId/steps/:stepId/files/:fileId/download
Authorization: Bearer <jwt>
```

**Success Response (302 Found):**
```
Location: https://forge-uploads-dev.s3.amazonaws.com/uploads/...?X-Amz-Signature=...
```

The redirect target is a presigned S3 URL with 15-minute expiry.

**Alternative (streaming for non-public S3):**
Response with file binary:
```
Content-Type: text/csv
Content-Disposition: attachment; filename="data-import.csv"
Content-Length: 1048576
```

### 3.5 Delete File

```
DELETE /api/workflows/:workflowId/steps/:stepId/files/:fileId
Authorization: Bearer <jwt>
```

**Success Response (204 No Content):**
No body.

## 4. Zod Validation Schemas

New file: `src/schemas/file.schema.ts`

```typescript
import { z } from 'zod';
import { CUIDSchema, PaginationSchema, SortSchema } from './common.schema';

// Path parameters for file endpoints nested under workflow steps
export const FilePathParamsSchema = z.object({
  workflowId: CUIDSchema.describe('Workflow CUID'),
  stepId: z.string().min(1).max(100).describe('Workflow step node ID'),
});

export type FilePathParams = z.infer<typeof FilePathParamsSchema>;

// Path parameters including fileId
export const FileIdPathParamsSchema = FilePathParamsSchema.extend({
  fileId: CUIDSchema.describe('File attachment CUID'),
});

export type FileIdPathParams = z.infer<typeof FileIdPathParamsSchema>;

// Upload metadata (non-file fields from multipart body)
export const FileUploadMetadataSchema = z.object({
  description: z.string().max(255).optional(),
});

export type FileUploadMetadata = z.infer<typeof FileUploadMetadataSchema>;

// List files query parameters
export const ListFilesQuerySchema = PaginationSchema.merge(SortSchema);

export type ListFilesQuery = z.infer<typeof ListFilesQuerySchema>;

// File response schema (for documentation/testing)
export const FileResponseSchema = z.object({
  id: CUIDSchema,
  workflowId: CUIDSchema,
  stepId: z.string(),
  filename: z.string(),
  originalFilename: z.string(),
  mimeType: z.string(),
  sizeBytes: z.number().int().nonnegative(),
  s3Key: z.string(),
  s3Bucket: z.string(),
  description: z.string().nullable(),
  uploadedBy: CUIDSchema,
  createdAt: z.string().datetime(),
});

export type FileResponse = z.infer<typeof FileResponseSchema>;
```

## 5. Middleware Considerations

### 5.1 Multipart Parsing

The existing `express.json()` middleware in `app.ts` parses JSON bodies globally. For the file upload endpoint, we need multipart parsing. Options:

**Option A: `multer` (recommended)**
- Well-established Express middleware for multipart handling.
- Supports file size limits, file count limits, and field filtering.
- Stores files in memory buffer (for streaming to S3) or temp disk.
- Configuration: memory storage with 50MB limit.

**Option B: `busboy`**
- Lower-level streaming parser.
- More control but more boilerplate.
- Better for very large files (streaming directly to S3).

**Recommendation:** Use `multer` with memory storage for v1 (files up to 50MB). The memory buffer is streamed directly to S3 via `PutObjectCommand`.

### 5.2 Body Size Limit

The current `express.json({ limit: '1mb' })` in `app.ts` does not affect multipart requests. However, we should add a separate limit for multipart bodies:

```typescript
// In file routes, not globally
const upload = multer({
  storage: multer.memoryStorage(),
  limits: {
    fileSize: parseInt(process.env.MAX_UPLOAD_FILE_SIZE || '52428800'), // 50MB
    files: 1, // Single file per request
  },
  fileFilter: (req, file, cb) => {
    const allowedTypes = (process.env.ALLOWED_FILE_TYPES || '').split(',');
    // ... validation logic
  },
});
```

## 6. Error Response Format

All errors follow the existing RFC 7807 pattern used by `ApiError`:

```json
{
  "type": "https://api.productforge.dev/errors/payload-too-large",
  "title": "Payload Too Large",
  "status": 413,
  "detail": "File size 62914560 bytes exceeds maximum allowed size of 52428800 bytes",
  "instance": "/api/workflows/cl.../steps/step-1/files"
}
```

## 7. Rate Limiting

File upload endpoints should have stricter rate limits than standard API endpoints:

| Endpoint | Rate Limit | Window |
|----------|-----------|---------|
| POST (upload) | 20 requests | 15 minutes |
| GET (list/metadata) | 100 requests | 15 minutes |
| GET (download) | 50 requests | 15 minutes |
| DELETE | 50 requests | 15 minutes |

These are applied per-user (keyed by `req.user.userId`), in addition to the existing global rate limits.

## 8. Swagger/OpenAPI Documentation

All endpoints will be documented with JSDoc-style Swagger annotations, consistent with existing patterns in `src/routes/workflows.ts`. The upload endpoint will use `multipart/form-data` content type in the OpenAPI spec.
