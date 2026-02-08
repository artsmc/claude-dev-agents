# Security Quality Assessment Skill - Design Document

**Date:** 2026-02-08
**Status:** Approved Design
**Author:** Brainstorming Session

---

## Executive Summary

A comprehensive security analysis tool that scans Python and JavaScript/TypeScript codebases to detect vulnerabilities across all OWASP Top 10 (2021) categories. The tool generates markdown reports with severity ratings, compliance mapping, and remediation guidance.

### Key Features

- **Multi-language support**: Python + JavaScript/TypeScript
- **Hybrid detection**: AST analysis + pattern matching + OSV CVE database
- **OWASP Top 10 coverage**: All 10 categories (2021)
- **Comprehensive reports**: Executive summary + detailed findings + compliance mapping
- **Suppression system**: Config-based false positive management
- **Simple CLI**: `/security-assess /path/to/project`
- **Zero dependencies**: Pure Python stdlib

---

## Architecture Overview

Following the proven architecture-quality-assess pattern:

```
security-quality-assess/
├── lib/
│   ├── models/          # Data models (Finding, Severity, Suppression)
│   ├── parsers/         # Language-specific AST parsers
│   │   ├── base.py
│   │   ├── python_parser.py
│   │   └── javascript_parser.py
│   ├── analyzers/       # Security analyzers (cross-language)
│   │   ├── base.py
│   │   ├── secrets_analyzer.py
│   │   ├── injection_analyzer.py
│   │   ├── auth_analyzer.py
│   │   ├── dependency_analyzer.py
│   │   ├── config_analyzer.py
│   │   └── sensitive_data_analyzer.py
│   └── reporters/
│       └── markdown_reporter.py
└── scripts/
    └── assess.py        # Main CLI
```

### Design Principles

- **Hybrid organization**: Language-specific parsers + cross-language security analyzers
- **Consistency**: Follows architecture-quality-assess structure for maintainability
- **Extensibility**: Plugin architecture for adding new analyzers
- **Graceful degradation**: Continue analysis even if some files fail to parse

---

## Data Models

### Finding

Represents a security issue:

```python
@dataclass
class Finding:
    id: str                    # Unique finding ID
    rule_id: str              # e.g., "hardcoded-secret", "sql-injection"
    category: OWASPCategory   # Maps to OWASP Top 10
    severity: Severity        # CRITICAL/HIGH/MEDIUM/LOW
    title: str
    description: str
    file_path: Path
    line_number: int
    code_sample: str          # The vulnerable code snippet
    remediation: str          # How to fix it
    cwe_id: Optional[str]     # CWE reference if applicable
    confidence: float         # 0.0-1.0 (for entropy-based detections)
```

### Severity Levels

Matching architecture-quality-assess pattern:

- **CRITICAL**: Immediate exploitation risk (exposed secrets, SQL injection)
- **HIGH**: Significant risk (weak crypto, auth bypass potential)
- **MEDIUM**: Moderate risk (missing security headers, weak configs)
- **LOW**: Best practice violations (outdated dependencies with no known CVE)

### Suppression

From `.security-suppress.json`:

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
      "created_by": "security-team",
      "approved_by": "tech-lead"
    }
  ]
}
```

---

## Parser Layer

### BaseParser

Reuse from architecture-quality-assess:
- AST parsing for Python and JavaScript/TypeScript
- Extracts imports, functions, classes, string literals
- Handles encoding detection (UTF-8 → latin-1 fallback)

### PythonParser Enhancements

- Extract all string literals (for secrets detection)
- Identify dangerous functions: `eval()`, `exec()`, `subprocess.call()`
- Parse SQL query strings (detect string concatenation patterns)
- Extract decorator usage (check for `@login_required`, `@authenticated`)

### JavaScriptParser Enhancements

- Extract template literals and string values
- Identify dangerous patterns: `eval()`, `innerHTML`, `dangerouslySetInnerHTML`
- Parse database queries (Sequelize, Prisma, raw SQL)
- Extract route handlers and middleware chains

### DependencyParser (New)

- Parse `package-lock.json` (npm)
- Parse `poetry.lock` (Python Poetry)
- Parse `yarn.lock` (Yarn)
- Extract exact package versions for OSV API queries

---

## Security Analyzers

### BaseAnalyzer

Extends architecture-quality-assess pattern:
- `analyze(parsed_files, config) → List[Finding]`
- Helper methods: `create_finding()`, `is_suppressed()`

### SecretsAnalyzer

**OWASP Category**: A02 - Cryptographic Failures

**Detections**:
- **Pattern matching**: AWS keys, GitHub tokens, API keys, private keys (regex)
- **Entropy analysis**: Flag strings with Shannon entropy > 4.5 (likely secrets)
- **Weak crypto**: Detect MD5, SHA1, DES usage

**Output**: CRITICAL findings for exposed secrets

### InjectionAnalyzer

**OWASP Category**: A03 - Injection

**Detections**:
- **SQL injection**: String concatenation in queries (`"SELECT * FROM " + table`)
- **Command injection**: Shell=True with variables, `os.system()` with user input
- **Code injection**: `eval()`, `exec()` with any arguments

**Approach**: Pattern-based detection (no data flow analysis initially)

**Output**: HIGH findings for injection risks

### AuthAnalyzer

**OWASP Categories**: A01 (Access Control), A07 (Auth Failures)

**Detections**:
- **Hardcoded passwords**: Variables named "password", "secret" with string values
- **Weak JWT**: HS256 with short secrets, missing expiration
- **Insecure sessions**: Session cookies without secure/httpOnly flags

**Output**: HIGH findings for auth weaknesses

### DependencyAnalyzer

**OWASP Category**: A06 - Vulnerable Components

**Process**:
1. Parse lockfiles to extract exact package versions
2. Query OSV API: `https://api.osv.dev/v1/query`
3. Match CVEs to installed packages
4. Cache OSV responses to avoid rate limiting

**Severity Mapping**:
- CVSS 9.0+ → CRITICAL
- CVSS 7.0-8.9 → HIGH
- CVSS 4.0-6.9 → MEDIUM
- CVSS <4.0 → LOW

### ConfigAnalyzer

**OWASP Category**: A05 - Security Misconfiguration

**Detections**:
- **CORS**: Overly permissive origins (`Access-Control-Allow-Origin: *`)
- **Debug mode**: `DEBUG=True`, `NODE_ENV=development` in production
- **Error disclosure**: Verbose error messages exposing stack traces
- **Security headers**: Missing CSP, X-Frame-Options, HSTS

**Output**: MEDIUM findings for misconfigurations

### SensitiveDataAnalyzer

**OWASP Categories**: A02 (Crypto Failures), A04 (Insecure Design)

**Detections**:
- **PII exposure**: Email, SSN patterns in logs or responses
- **Unencrypted storage**: Password fields stored without hashing
- **Logging secrets**: API keys, tokens logged to console/files

**Output**: HIGH findings for data exposure

### Additional OWASP Coverage

**Lower priority checks** (A08-A10):
- **A08**: Integrity failures (unsigned packages, missing SRI)
- **A09**: Logging failures (no audit logs, insufficient monitoring)
- **A10**: SSRF patterns (requests to user-controlled URLs)

---

## Report Generation

### Markdown Reporter

**Report Structure**:

```markdown
# Security Assessment Report

## Executive Summary
- **Overall Risk Score**: 72/100 (MEDIUM risk)
- **Total Findings**: 23 (3 CRITICAL, 8 HIGH, 9 MEDIUM, 3 LOW)
- **Suppressed Findings**: 2
- **Files Scanned**: 45 Python, 32 JavaScript
- **Scan Date**: 2026-02-08

## Risk Breakdown by Severity
🔴 CRITICAL: 3 findings (13%)
🟠 HIGH: 8 findings (35%)
🟡 MEDIUM: 9 findings (39%)
⚪ LOW: 3 findings (13%)

## OWASP Top 10 Coverage
- ✅ A01: Broken Access Control (2 findings)
- ✅ A02: Cryptographic Failures (5 findings)
- ✅ A03: Injection (4 findings)
- ⚠️ A04: Insecure Design (1 finding)
- ✅ A05: Security Misconfiguration (3 findings)
- ✅ A06: Vulnerable Components (7 findings)
- ✅ A07: Identification/Auth Failures (1 finding)
- ⚪ A08: Software/Data Integrity Failures (0 findings)
- ⚪ A09: Security Logging Failures (0 findings)
- ⚪ A10: Server-Side Request Forgery (0 findings)

## Detailed Findings

### CRITICAL Severity

#### 1. Hardcoded AWS Access Key
**Rule ID**: `hardcoded-secret`
**Category**: A02 - Cryptographic Failures
**CWE**: CWE-798 (Use of Hard-coded Credentials)
**Confidence**: 100%

**Location**: `src/config/aws.py:15`

**Code Sample**:
```python
AWS_ACCESS_KEY = "AKIAIOSFODNN7EXAMPLE"
```

**Description**:
AWS access key hardcoded in source code. If committed to version control,
this credential is exposed and can be used to access AWS resources.

**Remediation**:
Move credentials to environment variables or secure secret management
(AWS Secrets Manager, HashiCorp Vault). Use `os.getenv('AWS_ACCESS_KEY')`
instead of hardcoding.
```

**Report Sections**:
1. Executive Summary (risk score, counts, metadata)
2. Risk Breakdown (visual severity distribution)
3. OWASP Top 10 Coverage (compliance mapping)
4. Detailed Findings (grouped by severity)
   - Rule ID, Category, CWE reference
   - File location and line number
   - Code sample
   - Description
   - Remediation guidance

---

## CLI & Execution Flow

### Command Line Interface

**Usage**:
```bash
/security-assess /path/to/project
```

**Behavior**:
- Scans project directory recursively
- Generates markdown report to stdout
- Default output: `security-assessment.md` in current directory
- Exit code: 0 if no CRITICAL findings, 1 if CRITICAL present

### Execution Pipeline

**1. File Discovery**
- Scan for Python (`.py`) and JavaScript/TypeScript (`.js`, `.ts`, `.jsx`, `.tsx`)
- Respect `.gitignore` patterns
- Find lockfiles: `package-lock.json`, `poetry.lock`, `yarn.lock`

**2. Parse Files**
- Use language-specific parsers to extract AST
- Extract strings, functions, imports, dangerous patterns
- Parse dependency lockfiles for exact versions
- Handle encoding issues gracefully

**3. Run Analyzers**
- Execute all security analyzers in sequence
- Each analyzer produces `List[Finding]`
- Load suppressions from `.security-suppress.json` if present
- Filter suppressed findings

**4. Calculate Metrics**
- Risk score: Weighted by severity (CRITICAL=10, HIGH=7, MEDIUM=4, LOW=1)
- OWASP coverage: Which categories have findings
- File-level risk ranking

**5. Generate Report**
- Write markdown to stdout or output file
- Include executive summary, detailed findings, remediation
- Show suppressed findings count
- Exit with appropriate code

---

## Suppression System

### Configuration File

**Location**: `.security-suppress.json` in project root

**Schema**:
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
      "created_by": "security-team",
      "approved_by": "tech-lead"
    }
  ]
}
```

### Matching Logic

- **Exact match**: rule_id + file_path + line_number (most specific)
- **File-level match**: rule_id + file_path (suppresses all instances in file)
- **Expired suppressions**: Warn if suppression is past expiration date
- **Audit trail**: Include created_by, approved_by for governance

### Report Handling

- Suppressed findings don't appear in main findings list
- Count shown in executive summary: "Suppressed Findings: 2"
- Optional separate section at end listing suppressed items

---

## Implementation Details

### Performance Targets

- **Speed**: <30 seconds for 10K LOC codebase
- **File caching**: Reuse parsed ASTs (like architecture-quality-assess)
- **OSV API caching**: Cache CVE responses locally for 24 hours
- **Parallel analysis**: Run analyzers concurrently on different files

### Error Handling

- **Graceful degradation**: Skip unparseable files, continue analysis
- **OSV API failures**: Warn about dependency scan failure, complete other checks
- **Encoding issues**: UTF-8 → latin-1 fallback (existing parser logic)
- **Missing lockfiles**: Log warning, skip dependency analysis

### Extensibility

- **Plugin architecture**: Easy to add new analyzers
- **Registry pattern**: Auto-discover analyzers (like architecture-quality-assess)
- **Custom rules**: Future support for user-defined security rules
- **Analyzer interface**: Clear contract for new security checks

### Testing Strategy

- **Unit tests**: Each analyzer with fixture files containing known vulnerabilities
- **Integration tests**: End-to-end scan on test projects
- **Vulnerability fixtures**: Known vulnerable patterns for validation
- **False positive tracking**: Monitor and reduce FP rate over time
- **Regression tests**: Ensure fixes don't break existing detections

### Zero External Dependencies

- Pure Python stdlib (no extra packages)
- OSV API via `urllib` (no requests library)
- AST parsing using built-in `ast` module
- JSON parsing using built-in `json` module

---

## OWASP Top 10 (2021) Mapping

| Category | Title | Analyzers | Priority |
|----------|-------|-----------|----------|
| A01 | Broken Access Control | AuthAnalyzer | HIGH |
| A02 | Cryptographic Failures | SecretsAnalyzer, SensitiveDataAnalyzer | CRITICAL |
| A03 | Injection | InjectionAnalyzer | CRITICAL |
| A04 | Insecure Design | SensitiveDataAnalyzer | MEDIUM |
| A05 | Security Misconfiguration | ConfigAnalyzer | MEDIUM |
| A06 | Vulnerable Components | DependencyAnalyzer | HIGH |
| A07 | Identification/Auth Failures | AuthAnalyzer | HIGH |
| A08 | Software/Data Integrity | (Future) | LOW |
| A09 | Security Logging Failures | (Future) | LOW |
| A10 | SSRF | (Future) | MEDIUM |

---

## Success Criteria

### Functionality
- ✅ Detect all OWASP Top 10 categories (A01-A07 initially)
- ✅ Support Python and JavaScript/TypeScript
- ✅ Generate comprehensive markdown reports
- ✅ Support suppression via config file
- ✅ Query OSV API for dependency vulnerabilities

### Quality
- ✅ Zero external dependencies
- ✅ <30 second execution for 10K LOC
- ✅ Graceful error handling
- ✅ False positive rate <20%
- ✅ Comprehensive test coverage

### Usability
- ✅ Simple CLI: `/security-assess <path>`
- ✅ Clear, actionable remediation guidance
- ✅ OWASP compliance mapping in reports
- ✅ Easy suppression workflow

---

## Future Enhancements

### Short Term
- Add JSON report format for tool integration
- Implement A08-A10 OWASP categories
- Data flow analysis for injection detection
- Confidence scoring for all findings

### Medium Term
- Support for Java, Go, Rust
- Custom rule definition via YAML
- CI/CD exit code configuration (fail on HIGH vs CRITICAL)
- HTML report generation with interactive charts

### Long Term
- IDE plugin for real-time security feedback
- Machine learning for pattern detection
- Automated fix suggestions
- Security trends over time

---

## Appendix: Detection Rules

### Secrets Patterns (SecretsAnalyzer)

```python
PATTERNS = {
    "aws-access-key": r"AKIA[0-9A-Z]{16}",
    "github-token": r"ghp_[a-zA-Z0-9]{36}",
    "generic-api-key": r"api[_-]?key['\"]?\s*[:=]\s*['\"]([a-zA-Z0-9]{32,})['\"]",
    "private-key": r"-----BEGIN (RSA |EC |DSA )?PRIVATE KEY-----",
}
```

### Entropy Threshold

Shannon entropy > 4.5 for strings longer than 20 characters

### Dangerous Functions

**Python**:
- `eval()`, `exec()`, `compile()`
- `subprocess.call()` with `shell=True`
- `os.system()`, `os.popen()`
- `pickle.loads()` (insecure deserialization)

**JavaScript**:
- `eval()`
- `Function()` constructor
- `innerHTML`, `outerHTML`
- `dangerouslySetInnerHTML`
- `document.write()`

---

**End of Design Document**
