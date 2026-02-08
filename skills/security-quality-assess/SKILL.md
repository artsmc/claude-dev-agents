---
name: security-quality-assess
description: Automated security vulnerability scanning for Python and JavaScript/TypeScript codebases. Detects OWASP Top 10 vulnerabilities, hardcoded secrets, injection risks, and known CVEs with actionable remediation guidance.
---

# Security Quality Assessment Skill

Comprehensive static security analysis that automatically scans codebases to detect vulnerabilities across OWASP Top 10 (2021) categories.

**Use this skill to** identify security vulnerabilities early in development, maintain security compliance, and receive actionable remediation guidance for detected issues.

## Usage

```bash
# Scan current project
/security-assess .

# Scan specific directory
/security-assess /path/to/project

# Save report to file
/security-assess . --output security-report.md

# Skip network dependency scanning (faster)
/security-assess . --skip-osv

# Verbose logging for debugging
/security-assess . --verbose
```

## What This Skill Does

Performs comprehensive security analysis to answer:
- What security vulnerabilities exist in my codebase?
- Are there hardcoded secrets or credentials?
- Which dependencies have known CVEs?
- What's my overall security risk score?
- How do I fix the identified issues?

## Detection Coverage

### OWASP Top 10 (2021)

✅ **A01 - Broken Access Control**
- Missing authentication decorators
- Unauthenticated route handlers

✅ **A02 - Cryptographic Failures**
- Hardcoded secrets (AWS keys, API tokens, passwords)
- Weak cryptography (MD5, SHA1, DES)
- High-entropy strings (potential secrets)

✅ **A03 - Injection**
- SQL injection (string concatenation in queries)
- Command injection (shell=True, os.system)
- Code injection (eval, exec, compile)
- XSS (innerHTML, dangerouslySetInnerHTML)

✅ **A04 - Insecure Design**
- PII exposure in logs
- Unencrypted sensitive data storage

✅ **A05 - Security Misconfiguration**
- Debug mode enabled in production
- Insecure CORS configurations
- Missing security headers

✅ **A06 - Vulnerable Components**
- Known CVEs from OSV database
- Outdated dependencies with security issues

✅ **A07 - Authentication Failures**
- Weak JWT secrets
- Insecure session cookies
- Hardcoded passwords

## Severity Levels

Findings are prioritized for action:

- **CRITICAL** - Immediate action required (hardcoded credentials, code injection, known CVEs with CVSS 9.0+)
- **HIGH** - Fix within 1 sprint (SQL injection, missing auth, weak crypto, CVSS 7.0-8.9)
- **MEDIUM** - Plan remediation (insecure configs, minor misconfigurations, CVSS 4.0-6.9)
- **LOW** - Nice to fix (code quality improvements, CVSS 0.1-3.9)

## Exit Codes

The tool uses exit codes for CI/CD integration:

- **0** - Clean (no CRITICAL or HIGH findings)
- **1** - Issues found (CRITICAL or HIGH findings detected)
- **2** - Fatal error (analysis failed to complete)

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

## Common Workflows

### Pre-Commit Security Check
```bash
# Run scan before committing
/security-assess . --output report.md

# Check exit code
if [ $? -eq 0 ]; then
  git commit -m "Feature complete"
else
  echo "Security issues found - review report.md"
fi
```

### CI/CD Integration
```bash
# Run in pipeline with verbose logging
/security-assess . --verbose --output security-report.md

# Fail build on critical/high findings
exit_code=$?
if [ $exit_code -eq 1 ]; then
  echo "Security vulnerabilities block merge"
  exit 1
fi
```

### Fast Local Development Scan
```bash
# Skip dependency scanning for faster analysis
/security-assess . --skip-osv --output quick-scan.md
```

## Report Output

The markdown report includes:

1. **Executive Summary** - Risk score, finding counts by severity
2. **Risk Breakdown** - Visual distribution of findings
3. **OWASP Top 10 Coverage** - Findings mapped to categories
4. **Detailed Findings** - Each issue with:
   - File path and line number
   - Code snippet with context
   - OWASP category and CWE reference
   - Specific remediation guidance
5. **Suppressions Summary** - Count of suppressed and expired suppressions

## Limitations

**Language Support**:
- Currently supports Python (.py) and JavaScript/TypeScript (.js, .ts, .jsx, .tsx)
- More languages planned for future releases

**False Positives**:
- Static analysis may flag legitimate code patterns
- Use suppression system to manage false positives
- Tool automatically excludes common test directories

**Network Dependency**:
- CVE detection requires OSV API access
- Use `--skip-osv` flag when offline
- Results cached for 24 hours in `~/.cache/claude-security/osv/`

**Performance**:
- Typical: ~10,000 LOC/second
- OSV API queries add 2-5 seconds per scan
- Large codebases (>100K LOC) may take 30+ seconds

## Technical Details

- **Zero Dependencies** - Pure Python 3.8+ standard library
- **Fast Performance** - Scans 12K LOC in ~0.88 seconds
- **Smart Defaults** - Respects `.gitignore`, excludes test files
- **CVE Database** - Queries OSV.dev API for known vulnerabilities
- **Caching** - 24-hour cache for dependency vulnerability data

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

## Quality Metrics

This skill provides:
- **Risk Score** (0-100) - Weighted by severity
- **Finding Counts** - Breakdown by CRITICAL/HIGH/MEDIUM/LOW
- **OWASP Coverage** - Findings mapped to Top 10 categories
- **Security Posture** - Overall assessment with actionable recommendations

---

**Version**: 1.0.0
**Status**: Production Ready
**Languages Supported**: Python, JavaScript, TypeScript
**Last Updated**: 2026-02-08
