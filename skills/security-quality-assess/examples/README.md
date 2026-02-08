# Security Quality Assessment - Examples

This directory contains example configurations and documentation for the Security Quality Assessment skill.

## Suppression Configuration

The `.security-suppress.json` file shows how to configure finding suppressions for your project.

### File Location

Place your suppression file at the root of your project:
```
your-project/
├── .security-suppress.json
├── src/
├── tests/
└── ...
```

### File Structure

```json
{
  "version": "1.0",
  "suppressions": [
    {
      "rule_id": "hardcoded-secret",
      "file_path": "tests/fixtures/auth_test.py",
      "line_number": 42,
      "reason": "Test fixture password for unit tests",
      "expires": "2027-12-31",
      "created_by": "security-team@example.com",
      "approved_by": "tech-lead@example.com"
    }
  ]
}
```

### Field Descriptions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `version` | string | Yes | Schema version (currently "1.0") |
| `suppressions` | array | Yes | List of suppression rules |

#### Suppression Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `rule_id` | string | Yes | Exact rule ID to suppress (e.g., "hardcoded-secret") |
| `file_path` | string | Yes | Relative path from project root (use forward slashes) |
| `line_number` | number or null | Yes | Specific line to suppress, or `null` for entire file |
| `reason` | string | Yes | Justification for the suppression |
| `expires` | string | Yes | ISO date ("YYYY-MM-DD") when suppression expires |
| `created_by` | string | Yes | Email or username of creator |
| `approved_by` | string or null | No | Email or username of approver (optional) |

### Matching Logic

Suppressions match findings based on these rules:

1. **Rule ID**: Must match exactly (case-sensitive)
2. **File Path**: Normalized to use forward slashes, then compared exactly
3. **Line Number**:
   - If `line_number` is a number: Must match exactly
   - If `line_number` is `null`: Matches ALL lines in the file (file-level suppression)

### Use Cases

#### 1. Test Fixtures
Suppress known test data that triggers security rules:
```json
{
  "rule_id": "hardcoded-secret",
  "file_path": "tests/fixtures/auth_test.py",
  "line_number": 42,
  "reason": "Test fixture password. Not used in production.",
  "expires": "2027-12-31",
  "created_by": "dev@example.com"
}
```

#### 2. False Positives
Suppress findings that are incorrectly flagged:
```json
{
  "rule_id": "sql-injection",
  "file_path": "src/database/queries.py",
  "line_number": 156,
  "reason": "False positive: Uses parameterized SQLAlchemy query. String formatting is only in logging.",
  "expires": "2026-12-31",
  "created_by": "backend-dev@example.com",
  "approved_by": "security-team@example.com"
}
```

#### 3. Temporary Suppressions
Suppress findings with a near-term expiration:
```json
{
  "rule_id": "hardcoded-secret",
  "file_path": "scripts/migration_rollback.py",
  "line_number": 89,
  "reason": "Temporary during Q1 2026 migration. Remove after completion (ticket SEC-1234).",
  "expires": "2026-03-31",
  "created_by": "db-admin@example.com",
  "approved_by": "security-team@example.com"
}
```

#### 4. File-Level Suppressions
Suppress all findings of a type in an entire file:
```json
{
  "rule_id": "api-key-exposed",
  "file_path": "docs/api-guide.md",
  "line_number": null,
  "reason": "Documentation file contains only example API keys with 'example-' prefix.",
  "expires": "2028-06-30",
  "created_by": "docs-team@example.com",
  "approved_by": "security-team@example.com"
}
```

#### 5. Intentional Security Exceptions
Suppress findings for legitimate architectural decisions:
```json
{
  "rule_id": "missing-authentication",
  "file_path": "src/api/health.py",
  "line_number": 23,
  "reason": "Health check endpoint is intentionally public. Required by load balancer.",
  "expires": "2029-01-01",
  "created_by": "devops@example.com",
  "approved_by": "security-team@example.com"
}
```

### Best Practices

#### Expiration Dates

- **Test fixtures**: Long expiration (2-3 years) since they rarely change
- **False positives**: Annual review (1 year) in case detection improves
- **Temporary issues**: Near-term (1-3 months) with ticket reference
- **Intentional exceptions**: Long expiration (3-5 years) with architecture review cadence

#### Reason Field

Good reasons should explain:
- **Why** the finding exists
- **Why** it's safe to suppress
- **What** makes this case different
- **When** it will be resolved (if temporary)
- **Where** to find more context (ticket/doc reference)

Examples:
- ✅ "Test fixture password for unit tests. Not used in production. Value is 'test123'."
- ✅ "False positive: Uses parameterized query. String format is only in logging statement."
- ❌ "Not a real issue"
- ❌ "Ignored"

#### Approval Process

Use the `approved_by` field to enforce two-person review:
- Creator documents the suppression
- Security team or tech lead approves
- Both identities are tracked in the config

### Expiration Handling

When a suppression expires:
1. The finding will reappear in assessment reports
2. The expired suppression remains in the config file (manual cleanup required)
3. Review the finding to determine if:
   - The suppression should be renewed (update `expires` date)
   - The suppression is no longer needed (remove from config)
   - The underlying issue has been fixed (remove from config)

### Common Rule IDs

Based on the security quality assessment skill, common rule IDs include:

- `hardcoded-secret` - Hardcoded passwords, API keys, tokens
- `api-key-exposed` - API keys in code or config
- `sql-injection` - SQL injection vulnerabilities
- `missing-authentication` - Endpoints without auth checks
- `path-traversal` - Path traversal vulnerabilities
- `xss` - Cross-site scripting vulnerabilities
- `command-injection` - OS command injection
- `insecure-crypto` - Weak cryptographic algorithms
- `missing-csrf-protection` - Missing CSRF tokens
- `insecure-deserialization` - Unsafe deserialization

Refer to your assessment output for the exact rule IDs used in your project.
