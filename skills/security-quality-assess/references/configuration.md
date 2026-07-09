# Configuration Options and Suppression System

## Configuration Options

```bash
/security-assess <path> [OPTIONS]

Options:
  --output, -o FILE    Write report to FILE instead of stdout
  --config FILE        Path to custom .security-suppress.json
  --skip-osv           Skip dependency CVE scanning (faster, offline-friendly)
  --verbose, -v        Enable DEBUG-level logging
  --version            Print version and exit
  --help, -h           Show help message
```

## Suppression System

Suppress false positives while maintaining an audit trail using `.security-suppress.json`:

```json
{
  "version": "1.0",
  "suppressions": [
    {
      "rule_id": "hardcoded-secret",
      "file_path": "tests/fixtures/test_data.py",
      "line_number": 23,
      "reason": "Test fixture with fake credentials",
      "expires": "2026-12-31",
      "approved_by": "security-team"
    }
  ]
}
```

**Suppression Matching**:
1. Exact match: `rule_id` + `file_path` + `line_number` (most specific)
2. File-level: `rule_id` + `file_path` (suppresses all in file)
3. Global: `rule_id` only (suppresses everywhere)

**Expiration Handling**:
- Expired suppressions are ignored
- Tool warns about expired entries
- Review and renew or remove as needed
