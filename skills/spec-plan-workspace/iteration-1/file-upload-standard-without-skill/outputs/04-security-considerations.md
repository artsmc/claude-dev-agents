# Security Considerations: File Upload Feature

**Feature:** File Attachment Support for Workflow Steps
**Version:** 1.0
**Date:** 2026-03-09

---

## 1. Threat Model

### 1.1 Attack Surfaces

| Surface | Threats | Mitigation |
|---------|---------|------------|
| Upload endpoint | Malicious file upload, path traversal, DoS via large files | MIME validation, size limits, filename sanitization |
| S3 storage | Unauthorized access, data exfiltration | Bucket policies, encryption, no public access |
| Presigned URLs | URL sharing/leaking, replay attacks | Short expiry (15 min), single-use consideration |
| Multipart parsing | Buffer overflow, request smuggling | Use battle-tested library (multer), memory limits |
| Filename handling | Path traversal, XSS via filename in UI | Server-side sanitization, Content-Disposition header |

### 1.2 STRIDE Analysis

| Threat | Category | Risk | Mitigation |
|--------|----------|------|------------|
| Attacker uploads malware disguised as allowed type | Spoofing | Medium | MIME validation via magic bytes, not just extension/header |
| Attacker accesses files from another user's workflow | Tampering/Info Disclosure | High | Ownership check on every endpoint, S3 key includes userId |
| Attacker exhausts storage quota via rapid uploads | Denial of Service | Medium | Per-user quota, rate limiting, file size limit |
| Attacker discovers S3 keys via error messages | Information Disclosure | Low | Never expose internal S3 paths in error responses |
| Attacker modifies file metadata after upload | Tampering | Low | FileAttachment records are immutable after creation |

## 2. Authentication and Authorization

### 2.1 Authentication
- All file endpoints require a valid JWT Bearer token.
- Token is validated by the existing `authMiddleware` before reaching file routes.
- No anonymous file access.

### 2.2 Authorization
- **Ownership Check:** Every file operation validates that the authenticated user owns the parent workflow OR has the ADMIN role.
- **Implementation:** Reuse the `BaseController.assertOwnership()` pattern from the existing workflow controller.
- **Step Validation:** The stepId must correspond to an actual node in the workflow's definition JSON.

### 2.3 Authorization Flow
```
Request → authMiddleware (JWT) → fileController → loadWorkflow → assertOwnership → operation
```

## 3. Input Validation

### 3.1 File Content Validation

**MIME Type Validation (Server-Side):**
- Do NOT trust the `Content-Type` header from the client.
- Use `file-type` npm package to detect MIME type from the file's magic bytes (first few bytes of the buffer).
- Compare detected type against the allowlist.
- Reject files where detected type does not match the client-reported type.

**Allowlist (Default):**
```
application/pdf
text/csv
application/json
text/plain
image/png
image/jpeg
application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
application/vnd.openxmlformats-officedocument.wordprocessingml.document
```

### 3.2 Filename Sanitization

The original filename is preserved for display but the S3 key uses a sanitized version:

```typescript
function sanitizeFilename(filename: string): string {
  return filename
    .replace(/[^a-zA-Z0-9._-]/g, '_')  // Replace special chars
    .replace(/\.{2,}/g, '.')             // No double dots (path traversal)
    .replace(/^\.+/, '')                  // No leading dots
    .substring(0, 255);                   // Max length
}
```

### 3.3 Path Parameter Validation
- `workflowId`: Validated as CUID via Zod schema.
- `stepId`: Validated as non-empty string, max 100 characters.
- `fileId`: Validated as CUID via Zod schema.

## 4. S3 Security

### 4.1 Encryption
- **At Rest:** Server-side encryption enabled via `ServerSideEncryption: 'AES256'` on every `PutObjectCommand`.
- **In Transit:** All S3 API calls use HTTPS. Bucket policy denies unencrypted transport.

### 4.2 Bucket Configuration
- **Block Public Access:** All public access settings blocked.
- **Bucket Policy:** Enforces encryption and HTTPS.
- **No Static Website Hosting:** Bucket is not configured as a website.
- **Versioning:** Optional; recommended for compliance but not required for v1.

### 4.3 IAM Permissions (Principle of Least Privilege)
The API service's IAM role should have only these permissions on the upload bucket:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:DeleteObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::forge-uploads-*",
        "arn:aws:s3:::forge-uploads-*/*"
      ]
    }
  ]
}
```

### 4.4 Presigned URLs
- Generated server-side using `@aws-sdk/s3-request-presigner`.
- Expiry: 15 minutes for user-initiated downloads, 1 hour for execution-context URLs.
- Presigned URLs are scoped to the specific S3 object (no wildcard access).
- URLs contain a signature that is tied to the IAM credentials and cannot be extended.

## 5. Audit Logging

### 5.1 Events to Log

| Event | Action | Details |
|-------|--------|---------|
| File uploaded | `FILE_UPLOAD` | fileId, workflowId, stepId, filename, sizeBytes, mimeType, userId |
| File downloaded | `FILE_DOWNLOAD` | fileId, workflowId, stepId, userId |
| File deleted | `FILE_DELETE` | fileId, workflowId, stepId, userId |
| File access denied | `FILE_ACCESS_DENIED` | workflowId, stepId, userId, reason |
| Upload rejected (validation) | `FILE_UPLOAD_REJECTED` | filename, reason (size, type), userId |
| Quota exceeded | `FILE_QUOTA_EXCEEDED` | userId, currentUsage, quotaLimit |

### 5.2 Audit Record Format
Uses the existing `AuditLog` Prisma model:

```typescript
await auditLogRepository.create({
  action: 'FILE_UPLOAD',
  resource: 'FileAttachment',
  resourceId: fileAttachment.id,
  userId: user.userId,
  details: {
    workflowId,
    stepId,
    filename: sanitizedFilename,
    sizeBytes: file.size,
    mimeType: detectedMimeType,
  },
  ipAddress: req.ip,
  userAgent: req.get('user-agent'),
});
```

### 5.3 Compliance Notes
- **No PII in logs:** File contents are never logged. Only metadata (filename, size, type).
- **7-year retention:** AuditLog records are stored in PostgreSQL with no automatic deletion.
- **Immutable:** Audit records are insert-only; no update or delete operations.

## 6. Rate Limiting

File upload is a resource-intensive operation and requires stricter rate limits:

| Endpoint | Per-User Limit | Window |
|----------|---------------|--------|
| POST (upload) | 20 requests | 15 minutes |
| GET (download) | 50 requests | 15 minutes |
| Other GET/DELETE | 100 requests | 15 minutes |

Implementation: Use Express middleware applied specifically to file routes, separate from the global rate limiter.

## 7. Denial of Service Prevention

### 7.1 Upload Limits
- **File size limit:** 50 MB (configurable).
- **Memory storage:** multer buffers the file in memory. For a 50 MB limit, this is acceptable for a single concurrent upload per request.
- **Files per request:** Limited to 1.
- **Per-user quota:** 1 GB total storage.
- **Per-workflow quota:** 500 MB total storage.

### 7.2 Slow Upload Attack
- Express connection timeout is set via `server.timeout` in `main.ts`.
- multer has built-in handling for incomplete/stalled uploads.
- Consider adding a request timeout middleware specifically for upload routes (e.g., 60 seconds).

## 8. Future Security Enhancements (v2)

- **Virus scanning:** Integrate ClamAV or AWS Macie for uploaded files before making them available.
- **Content Security Policy:** Serve downloaded files with strict CSP headers to prevent XSS.
- **Presigned URL tracking:** Log every presigned URL generation and correlate with actual downloads.
- **File integrity:** Store SHA-256 hash of uploaded files and verify on download.
- **Encryption key per organization:** Use AWS KMS with org-specific keys for multi-tenant isolation.
