"""Centralized regex pattern library for security detection.

Provides a single, authoritative source of all regex patterns used across
the security quality assessment analyzers. Each pattern includes metadata
(description, CWE reference) for reporting and documentation.

This module is a **reference library**, not an active analyzer. Analyzers
may use these patterns directly or maintain their own specialized variants
with additional context (severity, confidence, remediation). The purpose
of centralizing patterns here is:

    1. **Discoverability** -- new contributors can see all detection
       patterns in one place, organized by security category.
    2. **Reuse** -- utility functions and new analyzers can import
       patterns without depending on a specific analyzer module.
    3. **Consistency** -- pattern definitions are canonical. When a
       pattern needs refinement, it can be updated here and all
       consumers benefit.

Pattern categories:
    - **Secrets**: Hardcoded API keys, tokens, private keys, JWTs.
    - **PII**: Email addresses, SSNs, credit card numbers, phone numbers.
    - **Injection**: SQL injection, command injection, code injection.
    - **JavaScript**: DOM XSS vectors (eval, innerHTML, document.write).
    - **Weak cryptography**: MD5, SHA-1, DES in Python and JavaScript.
    - **Configuration**: Debug mode, CORS wildcard, missing headers.
    - **SSRF**: Server-side request forgery (Python and JavaScript).
    - **XXE**: XML external entity injection (ElementTree, lxml, SAX, minidom).
    - **NoSQL injection**: MongoDB operator injection, unsanitized query input.
    - **Deserialization**: Unsafe YAML, marshal, shelve deserialization.
    - **JS command injection**: child_process exec, execSync, execFile, spawn.
    - **Extended weak crypto**: DES, Blowfish, RC4, 3DES, ECB mode.
    - **Access control**: Path traversal, insecure permissions, prototype pollution.
    - **Insecure transport**: Credentials over unencrypted HTTP.

All patterns in this module use only the Python standard library (``re``,
``typing``). There are no external dependencies.

Classes:
    SecurityPatterns: Main class with categorized pattern attributes
        and metadata retrieval methods.

Usage::

    from lib.utils.patterns import SecurityPatterns

    # Access a single pattern as a raw string
    aws_re = SecurityPatterns.AWS_ACCESS_KEY

    # Get all patterns with metadata
    all_patterns = SecurityPatterns.get_all_patterns()
    for rule_id, (regex, description, cwe_id) in all_patterns.items():
        compiled = re.compile(regex)
        ...

    # Get compiled patterns for a specific category
    secret_patterns = SecurityPatterns.get_compiled_secrets_patterns()
    for rule_id, (compiled, description, cwe_id) in secret_patterns.items():
        if compiled.search(source_line):
            ...

References:
    - TR.md Section 6.2: Pattern Library
    - OWASP Top 10 2021
    - MITRE CWE Database
"""

import re
from typing import Dict, List, Tuple


# ---------------------------------------------------------------------------
# Type aliases
# ---------------------------------------------------------------------------

# (regex_string, description, cwe_id)
PatternEntry = Tuple[str, str, str]

# (compiled_regex, description, cwe_id)
CompiledPatternEntry = Tuple["re.Pattern[str]", str, str]


class SecurityPatterns:
    """Centralized regex patterns for security vulnerability detection.

    All patterns are defined as class-level string attributes, organized
    into categories that mirror the OWASP Top 10 and CWE taxonomy. Each
    attribute holds a raw regex string suitable for ``re.compile()``.

    The class provides two retrieval interfaces:

    - ``get_all_patterns()`` returns all patterns as a flat dictionary
      mapping rule IDs to ``(regex_string, description, cwe_id)`` tuples.
    - Category-specific ``get_compiled_*_patterns()`` methods return
      pre-compiled ``re.Pattern`` objects for performance-sensitive
      scanning loops.

    Pattern naming convention:
        Class attributes use UPPER_SNAKE_CASE and are grouped by
        category comment blocks. Rule IDs in the metadata dictionaries
        use lowercase-hyphenated format matching the IDs used by
        analyzers (e.g., ``"hardcoded-aws-key"``).

    This class is not instantiated. All methods are class methods or
    static methods.
    """

    # ===================================================================
    # SECRETS PATTERNS
    # ===================================================================
    # Patterns for detecting hardcoded secrets, API keys, tokens, and
    # private keys embedded in source code. Maps to CWE-798: Use of
    # Hard-coded Credentials.

    AWS_ACCESS_KEY: str = r"AKIA[0-9A-Z]{16}"
    """AWS IAM access key ID. Begins with 'AKIA' followed by 16 uppercase
    alphanumeric characters. High confidence -- this prefix is unique to
    AWS access keys."""

    AWS_SECRET_KEY: str = r"(?<![A-Za-z0-9/+=])[A-Za-z0-9/+=]{40}(?![A-Za-z0-9/+=])"
    """AWS secret access key. 40 characters of base64-like characters.
    Lower confidence due to potential false positives; best used in
    conjunction with nearby AWS_ACCESS_KEY detection."""

    GITHUB_TOKEN: str = r"ghp_[a-zA-Z0-9]{36}"
    """GitHub personal access token (classic). Begins with 'ghp_' followed
    by 36 alphanumeric characters."""

    GITHUB_OAUTH_TOKEN: str = r"gho_[a-zA-Z0-9]{36}"
    """GitHub OAuth access token. Begins with 'gho_' followed by 36
    alphanumeric characters."""

    GITHUB_APP_TOKEN: str = r"(?:ghu|ghs)_[a-zA-Z0-9]{36}"
    """GitHub App user-to-server or server-to-server token. Begins with
    'ghu_' or 'ghs_' followed by 36 alphanumeric characters."""

    GITHUB_FINE_GRAINED_TOKEN: str = r"github_pat_[a-zA-Z0-9]{22}_[a-zA-Z0-9]{59}"
    """GitHub fine-grained personal access token. Has a specific format
    with two segments separated by an underscore."""

    SLACK_TOKEN: str = r"xox[baprs]-[0-9a-zA-Z]{10,48}"
    """Slack API token. Begins with 'xoxb-' (bot), 'xoxa-' (app),
    'xoxp-' (user), 'xoxr-' (refresh), or 'xoxs-' (session) followed
    by 10-48 alphanumeric characters."""

    GENERIC_API_KEY: str = (
        r"""api[_-]?key['\"]?\s*[:=]\s*['\"]([a-zA-Z0-9]{32,})['\"]"""
    )
    """Generic API key assignment pattern. Matches variable names
    containing 'api_key' or 'api-key' assigned a string value of 32+
    alphanumeric characters. Case-insensitive matching recommended."""

    GENERIC_SECRET: str = (
        r"""(?:secret|token|passwd|password|credentials?)['\"]?\s*[:=]\s*['\"]([a-zA-Z0-9/+=]{16,})['\"]"""
    )
    """Generic secret assignment pattern. Matches common secret-related
    variable names assigned string values of 16+ characters. Broader
    than GENERIC_API_KEY with more false positive potential."""

    PRIVATE_KEY: str = r"-----BEGIN[\s]+(RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----"
    """PEM-encoded private key header. Matches RSA, EC, DSA, and OpenSSH
    private key formats. Very high confidence -- PEM headers are
    unambiguous."""

    JWT_TOKEN: str = (
        r"eyJ[A-Za-z0-9-_]+\.eyJ[A-Za-z0-9-_]+\.[A-Za-z0-9-_.+/]+"
    )
    """JSON Web Token (JWT). Three base64url-encoded segments separated
    by dots, with the first two segments beginning with 'eyJ' (base64
    encoding of '{"'). High confidence pattern."""

    # ===================================================================
    # PII PATTERNS
    # ===================================================================
    # Patterns for detecting personally identifiable information. These
    # are used primarily by the SensitiveDataAnalyzer to flag PII
    # appearing in log statements, responses, or storage operations.

    EMAIL: str = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
    """Standard email address pattern. Matches user@domain.tld format
    with common special characters in the local part. Does not validate
    against RFC 5322 exhaustively but covers practical cases."""

    SSN: str = r"\b\d{3}-\d{2}-\d{4}\b"
    """US Social Security Number in standard format (XXX-XX-XXXX). Uses
    word boundaries to avoid matching within longer numeric strings.
    Does not validate area/group number ranges."""

    CREDIT_CARD: str = r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b"
    """Credit card number pattern. Matches 16-digit numbers with optional
    hyphens or spaces between 4-digit groups. Covers Visa, Mastercard,
    Discover formats. Does not perform Luhn validation (that is a
    runtime check)."""

    PHONE_US: str = r"\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"
    """US phone number in various formats: (555) 123-4567, 555-123-4567,
    555.123.4567, +1-555-123-4567. Broad pattern; may match other
    10-digit number formats."""

    PHONE_INTERNATIONAL: str = r"\b\+\d{1,3}[-.\s]?\d{4,14}\b"
    """International phone number with country code. Matches +CC followed
    by 4-14 digits with optional separators. Intentionally broad to
    cover diverse international formats."""

    # ===================================================================
    # INJECTION PATTERNS
    # ===================================================================
    # Patterns for detecting injection vulnerabilities (SQL, command,
    # code). These supplement the structural detection performed by
    # parsers and are used for raw source code scanning.

    # --- SQL Injection ---

    SQL_KEYWORDS: str = (
        r"\b(SELECT|INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|TRUNCATE"
        r"|UNION|EXEC|EXECUTE)\b"
    )
    """SQL keywords used in dynamic query construction detection. Matches
    major DML and DDL keywords. Case-insensitive matching recommended."""

    SQL_CONCATENATION: str = r"""['\"](?:SELECT|INSERT|UPDATE|DELETE)\s+.*?['\"]?\s*\+"""
    """SQL query built with string concatenation. Detects a SQL keyword
    inside a string literal followed by the concatenation operator (+).
    Indicates dynamic query construction vulnerable to injection."""

    SQL_FORMAT_STRING: str = (
        r"""['\"](?:SELECT|INSERT|UPDATE|DELETE)\s+.*?\{.*?\}"""
    )
    """SQL query built with Python format strings or f-strings. Detects
    a SQL keyword inside a string literal containing curly brace
    placeholders."""

    SQL_PERCENT_FORMAT: str = (
        r"""['\"](?:SELECT|INSERT|UPDATE|DELETE)\s+.*?%[sd]"""
    )
    """SQL query built with Python % string formatting. Detects a SQL
    keyword inside a string literal containing %s or %d placeholders
    (not parameterized -- these are string-level substitutions)."""

    # --- Command Injection ---

    COMMAND_SHELL_TRUE: str = r"""(?:subprocess\.(?:call|run|Popen))\s*\([^)]*shell\s*=\s*True"""
    """Python subprocess call with shell=True. When shell=True is set,
    the command string is interpreted by the shell, enabling injection
    via metacharacters (; | && ` $())."""

    COMMAND_OS_SYSTEM: str = r"""\bos\.system\s*\("""
    """Python os.system() call. Always executes through the shell.
    Any user input in the command string enables arbitrary command
    execution."""

    COMMAND_OS_POPEN: str = r"""\bos\.popen\s*\("""
    """Python os.popen() call. Executes through the shell and returns
    a pipe to the process. Same risk profile as os.system()."""

    # --- Code Injection ---

    PYTHON_EVAL: str = r"""\beval\s*\("""
    """Python eval() call. Evaluates arbitrary Python expressions.
    If the argument string is user-controlled, enables arbitrary
    code execution."""

    PYTHON_EXEC: str = r"""\bexec\s*\("""
    """Python exec() call. Executes arbitrary Python statements.
    More powerful than eval() as it can execute multi-line code."""

    PYTHON_COMPILE: str = r"""\bcompile\s*\("""
    """Python compile() call. Compiles source into a code object
    for later execution via eval() or exec()."""

    UNSAFE_PICKLE: str = r"""\bpickle\.(?:load|loads)\s*\("""
    """Python pickle deserialization. The pickle protocol allows
    arbitrary code execution during unpickling via __reduce__.
    Deserializing untrusted data is equivalent to eval()."""

    UNSAFE_YAML: str = r"""\byaml\.(?:load|unsafe_load)\s*\("""
    """Python YAML unsafe loading. yaml.load() without a safe Loader
    can execute arbitrary Python code via YAML tags. Use
    yaml.safe_load() instead."""

    # --- NoSQL Injection ---

    NOSQL_MONGOOSE_QUERY: str = (
        r"""\.(?:findOne|find|updateOne|updateMany|deleteOne|deleteMany"""
        r"""|findOneAndUpdate|findOneAndDelete|countDocuments|aggregate)\s*\("""
    )
    """MongoDB/Mongoose query method call. When receiving unsanitized
    user input (req.body, req.query), vulnerable to NoSQL operator
    injection (e.g., {"$gt": ""})."""

    NOSQL_JSON_PARSE_REQ: str = r"""JSON\.parse\s*\(\s*req\.(?:query|body|params)\b"""
    """JSON.parse() of user request data. When the parsed result is
    passed to a MongoDB query, enables arbitrary query operator
    injection."""

    # --- JavaScript Command Injection (child_process) ---

    JS_EXEC_TEMPLATE: str = r"""\bexec(?:Sync)?\s*\(\s*`[^`]*\$\{"""
    """Node.js child_process exec/execSync with template literal
    interpolation. Allows command injection when user input is
    embedded in the command string."""

    JS_EXEC_CONCAT: str = (
        r"""\bexec(?:Sync)?\s*\([^)]*(?:['"][^'"]*['"]\s*\+|\+\s*['"][^'"]*['"])"""
    )
    """Node.js child_process exec/execSync with string concatenation.
    Allows command injection via shell metacharacters."""

    # --- XXE (XML External Entity) ---

    XXE_ET_PARSE: str = r"""\bET\.(?:fromstring|parse)\s*\("""
    """Python xml.etree.ElementTree parsing. Default parser may
    resolve external entities in older Python versions."""

    XXE_LXML_RESOLVE: str = r"""resolve_entities\s*=\s*True"""
    """lxml XMLParser with resolve_entities=True. Explicitly enables
    external entity resolution, allowing XXE attacks."""

    XXE_XML_SAX: str = r"""\bxml\.sax\.(?:parse|parseString|make_parser)\s*\("""
    """Python xml.sax usage. Without explicit feature disabling,
    may resolve external entities."""

    # --- SSRF (Server-Side Request Forgery) ---

    SSRF_PY_URLLIB: str = r"""\burllib\.request\.urlopen\s*\("""
    """Python urllib.request.urlopen(). When called with a
    user-controlled URL, enables SSRF attacks."""

    SSRF_PY_REQUESTS: str = r"""\brequests\.(?:get|post|put|delete|patch|head)\s*\("""
    """Python requests library HTTP call. When the URL argument
    is user-controlled, enables SSRF attacks."""

    SSRF_PY_HTTPX: str = r"""\bhttpx\.(?:get|post|put|delete|patch|head)\s*\("""
    """Python httpx HTTP call. When the URL argument is
    user-controlled, enables SSRF attacks."""

    SSRF_JS_FETCH: str = r"""\bfetch\s*\("""
    """JavaScript fetch() call. When the URL argument is derived
    from user input (req.query, req.body), enables SSRF."""

    SSRF_JS_AXIOS: str = r"""\baxios\.(?:get|post|put|delete|patch|head|request)\s*\("""
    """JavaScript axios HTTP call. When the URL argument is
    user-controlled, enables SSRF attacks."""

    # ===================================================================
    # JAVASCRIPT PATTERNS
    # ===================================================================
    # Patterns for detecting JavaScript/TypeScript specific security
    # issues, primarily DOM-based XSS vectors.

    JS_EVAL: str = r"""\beval\s*\("""
    """JavaScript eval() call. Executes arbitrary JavaScript code.
    If the evaluated string contains user input, enables XSS or
    arbitrary code execution in Node.js."""

    JS_FUNCTION_CONSTRUCTOR: str = r"""\bnew\s+Function\s*\("""
    """JavaScript Function constructor. Creates a function from a code
    string, functionally equivalent to eval(). Same risk profile."""

    JS_INNER_HTML: str = r"""\.innerHTML\s*="""
    """JavaScript innerHTML assignment. Inserts raw HTML into the DOM
    without escaping. If the value contains user input, enables XSS
    via script injection or event handler attributes."""

    JS_OUTER_HTML: str = r"""\.outerHTML\s*="""
    """JavaScript outerHTML assignment. Replaces an element with raw
    HTML. Same XSS risk as innerHTML."""

    JS_DANGEROUSLY_SET_INNER_HTML: str = r"""dangerouslySetInnerHTML"""
    """React dangerouslySetInnerHTML prop. Explicitly bypasses React's
    built-in XSS protection. The name itself is a warning from the
    React team."""

    JS_DOCUMENT_WRITE: str = r"""document\.write(?:ln)?\s*\("""
    """JavaScript document.write() / document.writeln(). Writes raw
    HTML directly into the document. After page load, overwrites the
    entire document. XSS vector if content includes user input."""

    JS_SET_TIMEOUT_STRING: str = r"""setTimeout\s*\(\s*['"]"""
    """JavaScript setTimeout() with a string argument. When a string
    is passed (instead of a function), it is evaluated like eval().
    Should pass a function reference instead."""

    JS_SET_INTERVAL_STRING: str = r"""setInterval\s*\(\s*['"]"""
    """JavaScript setInterval() with a string argument. Same risk as
    setTimeout() with a string -- the string is eval'd on each
    interval tick."""

    # ===================================================================
    # WEAK CRYPTOGRAPHY PATTERNS
    # ===================================================================
    # Patterns for detecting usage of broken or deprecated cryptographic
    # algorithms. Maps to CWE-327: Use of a Broken or Risky
    # Cryptographic Algorithm.

    PYTHON_MD5: str = r"""\bhashlib\.md5\b"""
    """Python hashlib.md5() usage. MD5 is cryptographically broken with
    practical collision attacks. Should not be used for security
    purposes (integrity checks, signatures, password hashing)."""

    PYTHON_SHA1: str = r"""\bhashlib\.sha1\b"""
    """Python hashlib.sha1() usage. SHA-1 has demonstrated collision
    attacks (SHAttered, 2017). Deprecated for security use."""

    PYTHON_DES: str = r"""\bCrypto\.Cipher\.DES\b"""
    """PyCryptodome DES cipher. DES uses a 56-bit key that can be
    brute-forced in hours. Superseded by AES since 2001."""

    PYTHON_PYCRYPTO_MD5: str = r"""\bCrypto\.Hash\.MD5\b"""
    """PyCryptodome MD5 hash. Same weakness as hashlib.md5."""

    PYTHON_PYCRYPTO_SHA1: str = r"""\bCrypto\.Hash\.SHA1\b"""
    """PyCryptodome SHA-1 hash. Same weakness as hashlib.sha1."""

    JS_CRYPTO_MD5: str = (
        r"""(?:crypto|require\s*\(\s*['"]crypto['"]\s*\))"""
        r"""\.createHash\s*\(\s*['"]md5['"]\s*\)"""
    )
    """Node.js crypto.createHash('md5'). MD5 should not be used for
    any security-sensitive purpose."""

    JS_CRYPTO_SHA1: str = (
        r"""(?:crypto|require\s*\(\s*['"]crypto['"]\s*\))"""
        r"""\.createHash\s*\(\s*['"]sha1['"]\s*\)"""
    )
    """Node.js crypto.createHash('sha1'). SHA-1 is cryptographically
    weak and should not be used for security."""

    JS_CRYPTO_DES: str = r"""\.createCipheriv\s*\(\s*['"]des[^'"]*['"]\s*"""
    """Node.js DES cipher usage. DES is insecure; use AES-256-GCM."""

    JS_CRYPTO_RC4: str = r"""\.createCipheriv\s*\(\s*['"]rc4['"]\s*"""
    """Node.js RC4 cipher usage. RC4 is insecure; use AES-256-GCM."""

    JS_CRYPTO_ECB: str = r"""\.createCipheriv\s*\(\s*['"][^'"]*-ecb['"]\s*"""
    """Node.js ECB mode cipher usage. ECB is weak; use GCM mode."""

    PYTHON_RC4: str = r"""\bARC4\.new\s*\("""
    """PyCryptodome RC4 (ARC4) cipher. RC4 has multiple known biases
    and was prohibited by RFC 7465. Use AES-256-GCM instead."""

    PYTHON_BLOWFISH: str = r"""\bBlowfish\.new\s*\("""
    """PyCryptodome Blowfish cipher. Blowfish has a 64-bit block size
    vulnerable to birthday attacks (Sweet32). Use AES-256-GCM instead."""

    PYTHON_ECB_MODE: str = r"""\bMODE_ECB\b"""
    """ECB (Electronic Codebook) mode. Identical plaintext blocks produce
    identical ciphertext, leaking plaintext structure. Use GCM mode."""

    # ===================================================================
    # ACCESS CONTROL PATTERNS
    # ===================================================================
    # Patterns for detecting access control vulnerabilities. Maps to
    # OWASP A01:2021 Broken Access Control.

    PATH_TRAVERSAL_FSTRING: str = r"""\bopen\s*\(\s*f['"].*\{[^}]+\}"""
    """Python open() with f-string containing user variable. Enables
    path traversal via ../../ sequences."""

    PATH_TRAVERSAL_CONCAT: str = r"""\bopen\s*\([^)]*\+[^)]*\)"""
    """Python open() with string concatenation. Enables path traversal
    if one operand is user-controlled."""

    UNSAFE_CHMOD_777: str = r"""\bos\.chmod\s*\([^)]*\b0o(?:777|666)\b"""
    """os.chmod() with world-writable permissions (0o777 or 0o666).
    Grants excessive access to all system users."""

    PROTOTYPE_POLLUTION: str = r"""\bObject\.assign\s*\([^,]+,\s*(?:req|request)\.body"""
    """JavaScript Object.assign() with request body. Enables prototype
    pollution via __proto__ or constructor keys."""

    SUDO_SUBPROCESS: str = r"""\bsubprocess\.(?:run|call|Popen|check_call|check_output)\s*\(\s*\[?\s*['"]sudo['"]"""
    """Python subprocess call with sudo. Escalates to root privileges."""

    SETUID_ROOT: str = r"""\bos\.setuid\s*\(\s*0\s*\)"""
    """Python os.setuid(0). Sets process to root UID."""

    # ===================================================================
    # CONFIGURATION PATTERNS
    # ===================================================================
    # Patterns for detecting security misconfigurations. Maps to
    # OWASP A05:2021 Security Misconfiguration.

    DEBUG_DJANGO: str = r"""^DEBUG\s*=\s*True\b"""
    """Django DEBUG = True setting. Exposes stack traces, SQL queries,
    and environment variables in error pages."""

    DEBUG_FLASK_ATTR: str = r"""\.debug\s*=\s*True\b"""
    """Flask app.debug = True. Enables the Werkzeug debugger which
    allows arbitrary code execution from the browser."""

    DEBUG_FLASK_RUN: str = r"""\.run\s*\([^)]*debug\s*=\s*True"""
    """Flask app.run(debug=True). Same risk as setting app.debug."""

    DEBUG_NODE_ENV: str = r"""NODE_ENV\s*[:=]\s*['"]development['"]"""
    """Node.js NODE_ENV set to 'development'. In production this enables
    verbose error output and may disable security features."""

    CORS_WILDCARD: str = r"""Access-Control-Allow-Origin\s*['":\s]+\*"""
    """CORS wildcard origin header. Allows any website to make cross-
    origin requests, potentially exposing authenticated data."""

    CORS_FLASK_WILDCARD: str = (
        r"""CORS\s*\([^)]*origins\s*=\s*\[?\s*['"]?\*['"]?\s*\]?"""
    )
    """Flask-CORS wildcard configuration. Same risk as the raw header."""

    CORS_DJANGO_ALLOW_ALL: str = (
        r"""^(?:CORS_ALLOW_ALL_ORIGINS|CORS_ORIGIN_ALLOW_ALL)\s*=\s*True"""
    )
    """Django django-cors-headers CORS_ALLOW_ALL_ORIGINS = True. Allows
    all origins to make cross-origin requests."""

    # ===================================================================
    # AUTH PATTERNS
    # ===================================================================
    # Patterns for detecting authentication and authorization issues.
    # Maps to OWASP A01:2021 and A07:2021.

    HARDCODED_PASSWORD: str = (
        r"""(?:password|passwd|pwd)\s*[:=]\s*['\"][^'\"]{4,}['\"]"""
    )
    """Hardcoded password assignment. Matches password-like variable
    names assigned a string literal of 4+ characters. High false
    positive rate; use with context filtering."""

    JWT_WEAK_SECRET: str = (
        r"""(?:jwt\.encode|sign)\s*\([^)]*['\"]([a-zA-Z0-9]{1,31})['\"]"""
    )
    """JWT signing with a potentially weak secret (under 32 characters).
    Short secrets are vulnerable to brute-force attacks."""

    SESSION_NO_SECURE: str = (
        r"""(?:session|cookie)\s*.*?(?:secure\s*[:=]\s*(?:False|false|0)"""
        r"""|(?!.*secure))"""
    )
    """Session cookie without the 'secure' flag. The cookie can be
    transmitted over unencrypted HTTP connections."""

    LOCAL_STORAGE_SENSITIVE: str = (
        r"""(?:localStorage|sessionStorage)\.setItem\s*\(\s*['"]\s*"""
        r"""(?:password|token|secret|api_key|apiKey|auth_token|"""
        r"""authToken|access_token|accessToken|refresh_token|"""
        r"""refreshToken|session_id|sessionId|credit_card|ssn)"""
    )
    """Sensitive data stored in browser localStorage or sessionStorage.
    These storage mechanisms are accessible to any JavaScript on the
    same origin, including XSS payloads."""

    # ===================================================================
    # SSRF PATTERNS (List-based)
    # ===================================================================
    # Patterns for detecting Server-Side Request Forgery vulnerabilities.
    # Maps to CWE-918: Server-Side Request Forgery (SSRF).

    SSRF_PATTERNS: List[dict] = [
        # Python SSRF
        {"pattern": r"urllib\.request\.urlopen\s*\(", "rule_id": "ssrf-urllib", "description": "SSRF risk: urllib.request.urlopen() with potentially user-controlled URL", "cwe": "CWE-918"},
        {"pattern": r"requests\.(get|post|put|delete|patch|head)\s*\([^)]*\b(url|target|endpoint|callback|webhook|redirect)\b", "rule_id": "ssrf-requests", "description": "SSRF risk: requests library call with potentially user-controlled URL parameter", "cwe": "CWE-918"},
        {"pattern": r"http\.client\.HTTP[S]?Connection\s*\(", "rule_id": "ssrf-http-client", "description": "SSRF risk: http.client connection with potentially user-controlled host", "cwe": "CWE-918"},
    ]
    """List-based SSRF patterns for Python code. Each entry is a dict with
    pattern, rule_id, description, and cwe keys. Supplements the individual
    SSRF_PY_* class attributes with more targeted detection."""

    JS_SSRF_PATTERNS: List[dict] = [
        {"pattern": r"(?:fetch|axios(?:\.(?:get|post|put|delete|patch))?\s*)\s*\(\s*(?:req\.|request\.|params\.|query\.|body\.)", "rule_id": "ssrf-fetch", "description": "SSRF risk: fetch/axios with user-controlled URL from request parameters", "cwe": "CWE-918"},
        {"pattern": r"(?:http|https)\.(?:get|request)\s*\(\s*(?:req\.|request\.|params\.|query\.|body\.)", "rule_id": "ssrf-http-module", "description": "SSRF risk: Node.js http module with user-controlled URL", "cwe": "CWE-918"},
    ]
    """List-based SSRF patterns for JavaScript/Node.js code. Detects
    fetch/axios and http module calls with user-controlled URL inputs."""

    # ===================================================================
    # XXE PATTERNS (List-based)
    # ===================================================================
    # Patterns for detecting XML External Entity vulnerabilities.
    # Maps to CWE-611: Improper Restriction of XML External Entity Reference.

    XXE_PATTERNS: List[dict] = [
        {"pattern": r"ET\.fromstring\s*\(|ET\.parse\s*\(|xml\.etree\.ElementTree", "rule_id": "xxe-etree", "description": "XXE risk: xml.etree.ElementTree default parser allows entity expansion", "cwe": "CWE-611"},
        {"pattern": r"etree\.fromstring\s*\(|etree\.parse\s*\(|lxml\.etree", "rule_id": "xxe-lxml", "description": "XXE risk: lxml parser may allow external entity resolution", "cwe": "CWE-611"},
        {"pattern": r"xml\.sax\.parseString\s*\(|xml\.sax\.parse\s*\(", "rule_id": "xxe-sax", "description": "XXE risk: SAX parser may allow external entity resolution", "cwe": "CWE-611"},
        {"pattern": r"xml\.dom\.minidom\.parseString\s*\(|xml\.dom\.minidom\.parse\s*\(", "rule_id": "xxe-minidom", "description": "XXE risk: minidom parser may allow external entity resolution", "cwe": "CWE-611"},
        {"pattern": r"resolve_entities\s*=\s*True", "rule_id": "xxe-resolve-entities", "description": "XXE: External entity resolution explicitly enabled", "cwe": "CWE-611"},
    ]
    """List-based XXE patterns for Python XML parsing libraries. Covers
    ElementTree, lxml, SAX, and minidom parsers."""

    # ===================================================================
    # NOSQL INJECTION PATTERNS (List-based)
    # ===================================================================
    # Patterns for detecting NoSQL injection vulnerabilities.
    # Maps to CWE-943: Improper Neutralization of Special Elements in
    # Data Query Logic.

    NOSQL_INJECTION_PATTERNS: List[dict] = [
        {"pattern": r"\.(?:find|findOne|findOneAndUpdate|findOneAndDelete|updateOne|updateMany|deleteOne|deleteMany|aggregate|countDocuments)\s*\(\s*(?:req\.body|req\.query|req\.params|request\.json|request\.form|request\.args)", "rule_id": "nosql-injection-direct", "description": "NoSQL injection: MongoDB query using unsanitized user input directly", "cwe": "CWE-943"},
        {"pattern": r"JSON\.parse\s*\(.*(?:req\.query|req\.params|request\.args)", "rule_id": "nosql-injection-parsed", "description": "NoSQL injection: User input parsed as JSON and potentially used in query", "cwe": "CWE-943"},
        {"pattern": r"\$(?:gt|gte|lt|lte|ne|in|nin|regex|where|exists)\b", "rule_id": "nosql-operator-in-input", "description": "NoSQL operator in code that may accept user-controlled values", "cwe": "CWE-943"},
    ]
    """List-based NoSQL injection patterns. Detects direct use of
    unsanitized user input in MongoDB queries and NoSQL operator usage."""

    # ===================================================================
    # DESERIALIZATION PATTERNS (List-based)
    # ===================================================================
    # Patterns for detecting insecure deserialization vulnerabilities.
    # Maps to CWE-502: Deserialization of Untrusted Data.

    DESERIALIZATION_PATTERNS: List[dict] = [
        {"pattern": r"yaml\.load\s*\([^)]*\)(?!\s*,\s*Loader\s*=\s*yaml\.SafeLoader)", "rule_id": "yaml-unsafe-load", "description": "Insecure deserialization: yaml.load() without SafeLoader can execute arbitrary code", "cwe": "CWE-502"},
        {"pattern": r"yaml\.unsafe_load\s*\(", "rule_id": "yaml-unsafe-load-explicit", "description": "Insecure deserialization: yaml.unsafe_load() explicitly allows arbitrary code execution", "cwe": "CWE-502"},
        {"pattern": r"marshal\.loads?\s*\(", "rule_id": "marshal-deserialize", "description": "Insecure deserialization: marshal module can execute arbitrary code", "cwe": "CWE-502"},
        {"pattern": r"shelve\.open\s*\(", "rule_id": "shelve-deserialize", "description": "Insecure deserialization: shelve uses pickle internally", "cwe": "CWE-502"},
    ]
    """List-based deserialization patterns for Python. Detects unsafe
    YAML loading, marshal, and shelve usage."""

    # ===================================================================
    # JS COMMAND INJECTION PATTERNS (List-based)
    # ===================================================================
    # Patterns for detecting JavaScript command injection vulnerabilities.
    # Maps to CWE-78: Improper Neutralization of Special Elements used
    # in an OS Command ('OS Command Injection').

    JS_COMMAND_INJECTION_PATTERNS: List[dict] = [
        {"pattern": r"(?:child_process\.)?exec\s*\(", "rule_id": "cmd-injection-exec", "description": "Command injection: child_process.exec() passes input through shell", "cwe": "CWE-78"},
        {"pattern": r"(?:child_process\.)?execSync\s*\(", "rule_id": "cmd-injection-execsync", "description": "Command injection: child_process.execSync() passes input through shell", "cwe": "CWE-78"},
        {"pattern": r"(?:child_process\.)?execFile\s*\(", "rule_id": "cmd-injection-execfile", "description": "Command execution: child_process.execFile() runs external program", "cwe": "CWE-78"},
        {"pattern": r"child_process\.spawn\s*\([^)]*shell\s*:\s*true", "rule_id": "cmd-injection-spawn-shell", "description": "Command injection: spawn() with shell:true passes input through shell", "cwe": "CWE-78"},
    ]
    """List-based command injection patterns for JavaScript/Node.js.
    Detects child_process exec, execSync, execFile, and spawn with shell."""

    # ===================================================================
    # EXTENDED WEAK CRYPTO PATTERNS (List-based)
    # ===================================================================
    # Extended patterns for detecting weak cryptographic algorithm usage.
    # Maps to CWE-327: Use of a Broken or Risky Cryptographic Algorithm.

    EXTENDED_WEAK_CRYPTO_PATTERNS: List[dict] = [
        {"pattern": r"(?:Crypto\.Cipher\.)?DES\.new\s*\(|from\s+Crypto\.Cipher\s+import\s+DES", "rule_id": "weak-crypto-des", "description": "Weak encryption: DES has 56-bit key, easily brute-forced", "cwe": "CWE-327"},
        {"pattern": r"(?:Crypto\.Cipher\.)?Blowfish\.new\s*\(|from\s+Crypto\.Cipher\s+import\s+Blowfish", "rule_id": "weak-crypto-blowfish", "description": "Weak encryption: Blowfish has known weaknesses for large data", "cwe": "CWE-327"},
        {"pattern": r"(?:Crypto\.Cipher\.)?ARC4\.new\s*\(|from\s+Crypto\.Cipher\s+import\s+ARC4", "rule_id": "weak-crypto-rc4", "description": "Weak encryption: RC4 has critical biases in keystream", "cwe": "CWE-327"},
        {"pattern": r"(?:Crypto\.Cipher\.)?DES3\.new\s*\(|from\s+Crypto\.Cipher\s+import\s+DES3", "rule_id": "weak-crypto-3des", "description": "Weak encryption: 3DES is deprecated, use AES instead", "cwe": "CWE-327"},
        {"pattern": r"\.MODE_ECB\b|mode\s*=\s*['\"]ECB['\"]|mode\s*=\s*['\"]ecb['\"]", "rule_id": "weak-crypto-ecb", "description": "Weak encryption mode: ECB mode does not provide semantic security", "cwe": "CWE-327"},
        {"pattern": r"createCipheriv?\s*\(\s*['\"](?:des|rc4|blowfish|bf)['\"]", "rule_id": "weak-crypto-node-legacy", "description": "Weak encryption: Legacy cipher algorithm in Node.js crypto", "cwe": "CWE-327"},
        {"pattern": r"createCipheriv?\s*\(\s*['\"][^'\"]*-ecb['\"]", "rule_id": "weak-crypto-node-ecb", "description": "Weak encryption mode: ECB mode in Node.js crypto", "cwe": "CWE-327"},
    ]
    """List-based extended weak cryptography patterns. Covers DES, Blowfish,
    RC4, 3DES, ECB mode in both Python and Node.js."""

    # ===================================================================
    # ACCESS CONTROL PATTERNS (List-based)
    # ===================================================================
    # Extended patterns for detecting access control vulnerabilities.
    # Maps to CWE-22 (Path Traversal), CWE-732 (Incorrect Permission),
    # CWE-250 (Execution with Unnecessary Privileges).

    ACCESS_CONTROL_PATTERNS: List[dict] = [
        {"pattern": r"open\s*\(\s*(?:f['\"]|['\"].*\{).*(?:filename|filepath|file_path|path|fname)", "rule_id": "path-traversal", "description": "Path traversal risk: file opened with potentially user-controlled path", "cwe": "CWE-22"},
        {"pattern": r"os\.chmod\s*\([^)]*0o?777\b", "rule_id": "world-writable-permissions", "description": "World-writable file permissions (0777) allow any user to modify the file", "cwe": "CWE-732"},
        {"pattern": r"os\.chmod\s*\([^)]*0o?666\b", "rule_id": "world-readable-writable", "description": "World-readable-writable permissions (0666) expose file contents", "cwe": "CWE-732"},
        {"pattern": r"\bsudo\b.*(?:subprocess|os\.system|os\.popen|exec)", "rule_id": "privilege-escalation-sudo", "description": "Privilege escalation: sudo used in subprocess call", "cwe": "CWE-250"},
        {"pattern": r"subprocess\.(?:run|call|Popen|check_output)\s*\(\s*\[?\s*['\"]sudo['\"]", "rule_id": "privilege-escalation-subprocess", "description": "Privilege escalation: subprocess invoked with sudo", "cwe": "CWE-250"},
    ]
    """List-based access control patterns for Python. Detects path traversal,
    insecure file permissions, and privilege escalation via sudo."""

    JS_ACCESS_CONTROL_PATTERNS: List[dict] = [
        {"pattern": r"Object\.assign\s*\([^,]+,\s*(?:req\.body|req\.query|request\.body)", "rule_id": "prototype-pollution-assign", "description": "Prototype pollution: Object.assign with user-controlled input", "cwe": "CWE-1321"},
        {"pattern": r"_\.merge\s*\([^,]+,\s*(?:req\.body|req\.query|request\.body)", "rule_id": "prototype-pollution-merge", "description": "Prototype pollution: lodash merge with user-controlled input", "cwe": "CWE-1321"},
    ]
    """List-based access control patterns for JavaScript. Detects prototype
    pollution via Object.assign and lodash merge with user input."""

    # ===================================================================
    # INSECURE TRANSPORT PATTERNS (List-based)
    # ===================================================================
    # Patterns for detecting credentials transmitted over unencrypted HTTP.
    # Maps to CWE-319: Cleartext Transmission of Sensitive Information.

    INSECURE_TRANSPORT_PATTERNS: List[dict] = [
        {"pattern": r"['\"]http://[^'\"]*(?:login|auth|token|password|credential|api[_-]?key)", "rule_id": "http-credential-url", "description": "Credentials transmitted over unencrypted HTTP", "cwe": "CWE-319"},
        {"pattern": r"requests\.(?:get|post)\s*\(\s*['\"]http://", "rule_id": "http-requests-call", "description": "HTTP request without TLS encryption", "cwe": "CWE-319"},
    ]
    """List-based insecure transport patterns. Detects credential URLs
    and requests made over unencrypted HTTP connections."""

    # ===================================================================
    # FALSE POSITIVE REDUCTION PATTERNS
    # ===================================================================
    # Patterns used to exclude common false positive matches.

    URL_PATTERN: str = r"""^https?://|^\w+://"""
    """URL string pattern. Strings starting with a protocol scheme
    are typically not secrets (though they may contain tokens in
    query parameters, which are detected separately)."""

    FILE_PATH_PATTERN: str = r"""^[/\\.]|[/\\][\w.-]+[/\\]"""
    """File path pattern. Strings with path separators are typically
    not secrets."""

    UUID_PATTERN: str = (
        r"""^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"""
    )
    """UUID v4 pattern. UUIDs are identifiers, not secrets."""

    PLACEHOLDER_PATTERN: str = r"""\$\{|\{\{|%\(|__\w+__"""
    """Template / placeholder variable pattern. Strings containing
    template syntax are configuration templates, not hardcoded values."""

    # ===================================================================
    # RETRIEVAL METHODS
    # ===================================================================

    @classmethod
    def get_all_patterns(cls) -> Dict[str, PatternEntry]:
        """Get all security detection patterns with metadata.

        Returns a flat dictionary mapping rule IDs to tuples of
        ``(regex_string, description, cwe_id)``. Rule IDs use the same
        lowercase-hyphenated format as the analyzers, enabling direct
        correlation between pattern library entries and analyzer findings.

        The dictionary is constructed fresh on each call; callers may
        cache the result if needed for performance.

        Returns:
            Dictionary mapping rule IDs to (regex, description, cwe_id)
            tuples. The regex string has not been compiled; call
            ``re.compile()`` as needed.

        Example::

            patterns = SecurityPatterns.get_all_patterns()
            for rule_id, (regex, desc, cwe) in patterns.items():
                print(f"{rule_id}: {desc} [{cwe}]")
        """
        patterns: Dict[str, PatternEntry] = {}

        # Secrets
        patterns.update(cls._secrets_patterns())

        # PII
        patterns.update(cls._pii_patterns())

        # Injection
        patterns.update(cls._injection_patterns())

        # JavaScript
        patterns.update(cls._javascript_patterns())

        # Weak cryptography
        patterns.update(cls._weak_crypto_patterns())

        # Configuration
        patterns.update(cls._configuration_patterns())

        # Auth
        patterns.update(cls._auth_patterns())

        # SSRF
        patterns.update(cls._ssrf_patterns())

        # SSRF (list-based extended)
        patterns.update(cls._ssrf_list_patterns())

        # XXE (list-based extended)
        patterns.update(cls._xxe_list_patterns())

        # NoSQL Injection (list-based extended)
        patterns.update(cls._nosql_injection_list_patterns())

        # Deserialization (list-based extended)
        patterns.update(cls._deserialization_list_patterns())

        # JS Command Injection (list-based extended)
        patterns.update(cls._js_command_injection_list_patterns())

        # Extended Weak Crypto (list-based)
        patterns.update(cls._extended_weak_crypto_list_patterns())

        # Access Control (list-based extended)
        patterns.update(cls._access_control_list_patterns())

        # Insecure Transport (list-based)
        patterns.update(cls._insecure_transport_list_patterns())

        return patterns

    @classmethod
    def get_secrets_patterns(cls) -> Dict[str, PatternEntry]:
        """Get all secrets detection patterns with metadata.

        Returns:
            Dictionary mapping rule IDs to (regex, description, cwe_id)
            tuples for secrets patterns only.
        """
        return cls._secrets_patterns()

    @classmethod
    def get_pii_patterns(cls) -> Dict[str, PatternEntry]:
        """Get all PII detection patterns with metadata.

        Returns:
            Dictionary mapping rule IDs to (regex, description, cwe_id)
            tuples for PII patterns only.
        """
        return cls._pii_patterns()

    @classmethod
    def get_injection_patterns(cls) -> Dict[str, PatternEntry]:
        """Get all injection detection patterns with metadata.

        Returns:
            Dictionary mapping rule IDs to (regex, description, cwe_id)
            tuples for injection patterns only.
        """
        return cls._injection_patterns()

    @classmethod
    def get_javascript_patterns(cls) -> Dict[str, PatternEntry]:
        """Get all JavaScript-specific detection patterns with metadata.

        Returns:
            Dictionary mapping rule IDs to (regex, description, cwe_id)
            tuples for JavaScript patterns only.
        """
        return cls._javascript_patterns()

    @classmethod
    def get_weak_crypto_patterns(cls) -> Dict[str, PatternEntry]:
        """Get all weak cryptography detection patterns with metadata.

        Returns:
            Dictionary mapping rule IDs to (regex, description, cwe_id)
            tuples for weak cryptography patterns only.
        """
        return cls._weak_crypto_patterns()

    @classmethod
    def get_configuration_patterns(cls) -> Dict[str, PatternEntry]:
        """Get all configuration detection patterns with metadata.

        Returns:
            Dictionary mapping rule IDs to (regex, description, cwe_id)
            tuples for configuration patterns only.
        """
        return cls._configuration_patterns()

    @classmethod
    def get_auth_patterns(cls) -> Dict[str, PatternEntry]:
        """Get all authentication/authorization patterns with metadata.

        Returns:
            Dictionary mapping rule IDs to (regex, description, cwe_id)
            tuples for auth patterns only.
        """
        return cls._auth_patterns()

    @classmethod
    def get_ssrf_patterns(cls) -> Dict[str, PatternEntry]:
        """Get all SSRF detection patterns with metadata.

        Returns:
            Dictionary mapping rule IDs to (regex, description, cwe_id)
            tuples for SSRF patterns only.
        """
        return cls._ssrf_patterns()

    @classmethod
    def get_ssrf_list_patterns(cls) -> Dict[str, PatternEntry]:
        """Get extended SSRF detection patterns (list-based) with metadata.

        Returns:
            Dictionary mapping rule IDs to (regex, description, cwe_id)
            tuples for extended SSRF patterns (Python and JS).
        """
        return cls._ssrf_list_patterns()

    @classmethod
    def get_xxe_list_patterns(cls) -> Dict[str, PatternEntry]:
        """Get extended XXE detection patterns (list-based) with metadata.

        Returns:
            Dictionary mapping rule IDs to (regex, description, cwe_id)
            tuples for XXE patterns.
        """
        return cls._xxe_list_patterns()

    @classmethod
    def get_nosql_injection_list_patterns(cls) -> Dict[str, PatternEntry]:
        """Get extended NoSQL injection detection patterns (list-based).

        Returns:
            Dictionary mapping rule IDs to (regex, description, cwe_id)
            tuples for NoSQL injection patterns.
        """
        return cls._nosql_injection_list_patterns()

    @classmethod
    def get_deserialization_list_patterns(cls) -> Dict[str, PatternEntry]:
        """Get deserialization detection patterns (list-based) with metadata.

        Returns:
            Dictionary mapping rule IDs to (regex, description, cwe_id)
            tuples for deserialization patterns.
        """
        return cls._deserialization_list_patterns()

    @classmethod
    def get_js_command_injection_list_patterns(cls) -> Dict[str, PatternEntry]:
        """Get JS command injection detection patterns (list-based).

        Returns:
            Dictionary mapping rule IDs to (regex, description, cwe_id)
            tuples for JS command injection patterns.
        """
        return cls._js_command_injection_list_patterns()

    @classmethod
    def get_extended_weak_crypto_list_patterns(cls) -> Dict[str, PatternEntry]:
        """Get extended weak crypto detection patterns (list-based).

        Returns:
            Dictionary mapping rule IDs to (regex, description, cwe_id)
            tuples for extended weak crypto patterns.
        """
        return cls._extended_weak_crypto_list_patterns()

    @classmethod
    def get_access_control_list_patterns(cls) -> Dict[str, PatternEntry]:
        """Get extended access control detection patterns (list-based).

        Returns:
            Dictionary mapping rule IDs to (regex, description, cwe_id)
            tuples for access control patterns (Python and JS).
        """
        return cls._access_control_list_patterns()

    @classmethod
    def get_insecure_transport_list_patterns(cls) -> Dict[str, PatternEntry]:
        """Get insecure transport detection patterns (list-based).

        Returns:
            Dictionary mapping rule IDs to (regex, description, cwe_id)
            tuples for insecure transport patterns.
        """
        return cls._insecure_transport_list_patterns()

    # ===================================================================
    # COMPILED PATTERN METHODS
    # ===================================================================

    @classmethod
    def get_compiled_secrets_patterns(
        cls,
    ) -> Dict[str, CompiledPatternEntry]:
        """Get pre-compiled regex objects for secrets detection.

        Compiles each secrets pattern once and returns them in a
        dictionary suitable for use in scanning loops. Patterns that
        benefit from case-insensitive matching (GENERIC_API_KEY) are
        compiled with ``re.IGNORECASE``.

        Returns:
            Dictionary mapping rule IDs to
            (compiled_regex, description, cwe_id) tuples.
        """
        raw = cls._secrets_patterns()
        compiled: Dict[str, CompiledPatternEntry] = {}

        # Patterns that need IGNORECASE
        case_insensitive = {"hardcoded-generic-api-key", "hardcoded-generic-secret"}

        for rule_id, (regex, description, cwe_id) in raw.items():
            flags = re.IGNORECASE if rule_id in case_insensitive else 0
            compiled[rule_id] = (re.compile(regex, flags), description, cwe_id)

        return compiled

    @classmethod
    def get_compiled_pii_patterns(
        cls,
    ) -> Dict[str, CompiledPatternEntry]:
        """Get pre-compiled regex objects for PII detection.

        Returns:
            Dictionary mapping rule IDs to
            (compiled_regex, description, cwe_id) tuples.
        """
        raw = cls._pii_patterns()
        compiled: Dict[str, CompiledPatternEntry] = {}

        for rule_id, (regex, description, cwe_id) in raw.items():
            compiled[rule_id] = (re.compile(regex), description, cwe_id)

        return compiled

    @classmethod
    def get_compiled_injection_patterns(
        cls,
    ) -> Dict[str, CompiledPatternEntry]:
        """Get pre-compiled regex objects for injection detection.

        SQL keyword patterns are compiled with ``re.IGNORECASE``.

        Returns:
            Dictionary mapping rule IDs to
            (compiled_regex, description, cwe_id) tuples.
        """
        raw = cls._injection_patterns()
        compiled: Dict[str, CompiledPatternEntry] = {}

        # SQL patterns need IGNORECASE
        sql_rules = {
            "sql-keywords",
            "sql-concatenation",
            "sql-format-string",
            "sql-percent-format",
        }

        for rule_id, (regex, description, cwe_id) in raw.items():
            flags = re.IGNORECASE if rule_id in sql_rules else 0
            compiled[rule_id] = (re.compile(regex, flags), description, cwe_id)

        return compiled

    @classmethod
    def get_compiled_javascript_patterns(
        cls,
    ) -> Dict[str, CompiledPatternEntry]:
        """Get pre-compiled regex objects for JavaScript detection.

        Returns:
            Dictionary mapping rule IDs to
            (compiled_regex, description, cwe_id) tuples.
        """
        raw = cls._javascript_patterns()
        compiled: Dict[str, CompiledPatternEntry] = {}

        for rule_id, (regex, description, cwe_id) in raw.items():
            compiled[rule_id] = (re.compile(regex), description, cwe_id)

        return compiled

    @classmethod
    def get_compiled_weak_crypto_patterns(
        cls,
    ) -> Dict[str, CompiledPatternEntry]:
        """Get pre-compiled regex objects for weak cryptography detection.

        DES patterns are compiled with ``re.IGNORECASE`` to match
        case variations in cipher names.

        Returns:
            Dictionary mapping rule IDs to
            (compiled_regex, description, cwe_id) tuples.
        """
        raw = cls._weak_crypto_patterns()
        compiled: Dict[str, CompiledPatternEntry] = {}

        case_insensitive = {"weak-crypto-des-js", "weak-crypto-rc4-js", "weak-crypto-ecb-mode-js"}

        for rule_id, (regex, description, cwe_id) in raw.items():
            flags = re.IGNORECASE if rule_id in case_insensitive else 0
            compiled[rule_id] = (re.compile(regex, flags), description, cwe_id)

        return compiled

    @classmethod
    def get_compiled_ssrf_list_patterns(
        cls,
    ) -> Dict[str, CompiledPatternEntry]:
        """Get pre-compiled regex objects for extended SSRF detection.

        Returns:
            Dictionary mapping rule IDs to
            (compiled_regex, description, cwe_id) tuples.
        """
        raw = cls._ssrf_list_patterns()
        compiled: Dict[str, CompiledPatternEntry] = {}

        for rule_id, (regex, description, cwe_id) in raw.items():
            compiled[rule_id] = (re.compile(regex), description, cwe_id)

        return compiled

    @classmethod
    def get_compiled_xxe_list_patterns(
        cls,
    ) -> Dict[str, CompiledPatternEntry]:
        """Get pre-compiled regex objects for extended XXE detection.

        Returns:
            Dictionary mapping rule IDs to
            (compiled_regex, description, cwe_id) tuples.
        """
        raw = cls._xxe_list_patterns()
        compiled: Dict[str, CompiledPatternEntry] = {}

        for rule_id, (regex, description, cwe_id) in raw.items():
            compiled[rule_id] = (re.compile(regex), description, cwe_id)

        return compiled

    @classmethod
    def get_compiled_nosql_injection_list_patterns(
        cls,
    ) -> Dict[str, CompiledPatternEntry]:
        """Get pre-compiled regex objects for extended NoSQL injection detection.

        Returns:
            Dictionary mapping rule IDs to
            (compiled_regex, description, cwe_id) tuples.
        """
        raw = cls._nosql_injection_list_patterns()
        compiled: Dict[str, CompiledPatternEntry] = {}

        for rule_id, (regex, description, cwe_id) in raw.items():
            compiled[rule_id] = (re.compile(regex), description, cwe_id)

        return compiled

    @classmethod
    def get_compiled_deserialization_list_patterns(
        cls,
    ) -> Dict[str, CompiledPatternEntry]:
        """Get pre-compiled regex objects for deserialization detection.

        Returns:
            Dictionary mapping rule IDs to
            (compiled_regex, description, cwe_id) tuples.
        """
        raw = cls._deserialization_list_patterns()
        compiled: Dict[str, CompiledPatternEntry] = {}

        for rule_id, (regex, description, cwe_id) in raw.items():
            compiled[rule_id] = (re.compile(regex), description, cwe_id)

        return compiled

    @classmethod
    def get_compiled_js_command_injection_list_patterns(
        cls,
    ) -> Dict[str, CompiledPatternEntry]:
        """Get pre-compiled regex objects for JS command injection detection.

        Returns:
            Dictionary mapping rule IDs to
            (compiled_regex, description, cwe_id) tuples.
        """
        raw = cls._js_command_injection_list_patterns()
        compiled: Dict[str, CompiledPatternEntry] = {}

        for rule_id, (regex, description, cwe_id) in raw.items():
            compiled[rule_id] = (re.compile(regex), description, cwe_id)

        return compiled

    @classmethod
    def get_compiled_extended_weak_crypto_list_patterns(
        cls,
    ) -> Dict[str, CompiledPatternEntry]:
        """Get pre-compiled regex objects for extended weak crypto detection.

        Node.js legacy cipher patterns are compiled with ``re.IGNORECASE``.

        Returns:
            Dictionary mapping rule IDs to
            (compiled_regex, description, cwe_id) tuples.
        """
        raw = cls._extended_weak_crypto_list_patterns()
        compiled: Dict[str, CompiledPatternEntry] = {}

        case_insensitive = {"weak-crypto-node-legacy", "weak-crypto-node-ecb"}

        for rule_id, (regex, description, cwe_id) in raw.items():
            flags = re.IGNORECASE if rule_id in case_insensitive else 0
            compiled[rule_id] = (re.compile(regex, flags), description, cwe_id)

        return compiled

    @classmethod
    def get_compiled_access_control_list_patterns(
        cls,
    ) -> Dict[str, CompiledPatternEntry]:
        """Get pre-compiled regex objects for extended access control detection.

        Returns:
            Dictionary mapping rule IDs to
            (compiled_regex, description, cwe_id) tuples.
        """
        raw = cls._access_control_list_patterns()
        compiled: Dict[str, CompiledPatternEntry] = {}

        for rule_id, (regex, description, cwe_id) in raw.items():
            compiled[rule_id] = (re.compile(regex), description, cwe_id)

        return compiled

    @classmethod
    def get_compiled_insecure_transport_list_patterns(
        cls,
    ) -> Dict[str, CompiledPatternEntry]:
        """Get pre-compiled regex objects for insecure transport detection.

        Returns:
            Dictionary mapping rule IDs to
            (compiled_regex, description, cwe_id) tuples.
        """
        raw = cls._insecure_transport_list_patterns()
        compiled: Dict[str, CompiledPatternEntry] = {}

        for rule_id, (regex, description, cwe_id) in raw.items():
            compiled[rule_id] = (re.compile(regex), description, cwe_id)

        return compiled

    # ===================================================================
    # UTILITY METHODS
    # ===================================================================

    @classmethod
    def get_pattern_categories(cls) -> List[str]:
        """Get the list of available pattern category names.

        Returns:
            List of category name strings that can be used to select
            a specific ``get_*_patterns()`` method.
        """
        return [
            "secrets",
            "pii",
            "injection",
            "javascript",
            "weak_crypto",
            "configuration",
            "auth",
            "ssrf",
            "ssrf_list",
            "xxe_list",
            "nosql_injection_list",
            "deserialization_list",
            "js_command_injection_list",
            "extended_weak_crypto_list",
            "access_control_list",
            "insecure_transport_list",
        ]

    @classmethod
    def get_patterns_by_cwe(cls, cwe_id: str) -> Dict[str, PatternEntry]:
        """Get all patterns associated with a specific CWE identifier.

        Args:
            cwe_id: The CWE identifier to filter by (e.g., "CWE-798").

        Returns:
            Dictionary mapping rule IDs to (regex, description, cwe_id)
            tuples for patterns matching the specified CWE.
        """
        all_patterns = cls.get_all_patterns()
        return {
            rule_id: entry
            for rule_id, entry in all_patterns.items()
            if entry[2] == cwe_id
        }

    @classmethod
    def count_patterns(cls) -> int:
        """Return the total number of patterns in the library.

        Returns:
            Integer count of all registered patterns.
        """
        return len(cls.get_all_patterns())

    # ===================================================================
    # PRIVATE CATEGORY BUILDERS
    # ===================================================================

    @classmethod
    def _secrets_patterns(cls) -> Dict[str, PatternEntry]:
        """Build the secrets pattern dictionary."""
        return {
            "hardcoded-aws-key": (
                cls.AWS_ACCESS_KEY,
                "AWS access key ID (AKIA...) detected in source code",
                "CWE-798",
            ),
            "hardcoded-aws-secret": (
                cls.AWS_SECRET_KEY,
                "Potential AWS secret access key (40-char base64) detected",
                "CWE-798",
            ),
            "hardcoded-github-token": (
                cls.GITHUB_TOKEN,
                "GitHub personal access token (ghp_...) detected",
                "CWE-798",
            ),
            "hardcoded-github-oauth-token": (
                cls.GITHUB_OAUTH_TOKEN,
                "GitHub OAuth access token (gho_...) detected",
                "CWE-798",
            ),
            "hardcoded-github-app-token": (
                cls.GITHUB_APP_TOKEN,
                "GitHub App token (ghu_/ghs_...) detected",
                "CWE-798",
            ),
            "hardcoded-github-fine-grained-token": (
                cls.GITHUB_FINE_GRAINED_TOKEN,
                "GitHub fine-grained personal access token detected",
                "CWE-798",
            ),
            "hardcoded-slack-token": (
                cls.SLACK_TOKEN,
                "Slack API token (xox[baprs]-...) detected",
                "CWE-798",
            ),
            "hardcoded-generic-api-key": (
                cls.GENERIC_API_KEY,
                "Generic API key assignment pattern detected",
                "CWE-798",
            ),
            "hardcoded-generic-secret": (
                cls.GENERIC_SECRET,
                "Generic secret/token/password assignment pattern detected",
                "CWE-798",
            ),
            "hardcoded-private-key": (
                cls.PRIVATE_KEY,
                "PEM-encoded private key header detected in source code",
                "CWE-798",
            ),
            "hardcoded-jwt-token": (
                cls.JWT_TOKEN,
                "Hardcoded JSON Web Token (JWT) detected",
                "CWE-798",
            ),
        }

    @classmethod
    def _pii_patterns(cls) -> Dict[str, PatternEntry]:
        """Build the PII pattern dictionary."""
        return {
            "pii-email": (
                cls.EMAIL,
                "Email address pattern detected",
                "CWE-359",
            ),
            "pii-ssn": (
                cls.SSN,
                "US Social Security Number pattern detected",
                "CWE-359",
            ),
            "pii-credit-card": (
                cls.CREDIT_CARD,
                "Credit card number pattern detected",
                "CWE-359",
            ),
            "pii-phone-us": (
                cls.PHONE_US,
                "US phone number pattern detected",
                "CWE-359",
            ),
            "pii-phone-international": (
                cls.PHONE_INTERNATIONAL,
                "International phone number pattern detected",
                "CWE-359",
            ),
        }

    @classmethod
    def _injection_patterns(cls) -> Dict[str, PatternEntry]:
        """Build the injection pattern dictionary."""
        return {
            "sql-keywords": (
                cls.SQL_KEYWORDS,
                "SQL keyword detected in potential dynamic query",
                "CWE-89",
            ),
            "sql-concatenation": (
                cls.SQL_CONCATENATION,
                "SQL query built with string concatenation",
                "CWE-89",
            ),
            "sql-format-string": (
                cls.SQL_FORMAT_STRING,
                "SQL query built with format string interpolation",
                "CWE-89",
            ),
            "sql-percent-format": (
                cls.SQL_PERCENT_FORMAT,
                "SQL query built with percent string formatting",
                "CWE-89",
            ),
            "command-injection-shell-true": (
                cls.COMMAND_SHELL_TRUE,
                "Subprocess call with shell=True enables command injection",
                "CWE-78",
            ),
            "command-injection-os-system": (
                cls.COMMAND_OS_SYSTEM,
                "os.system() passes commands to the shell",
                "CWE-78",
            ),
            "command-injection-os-popen": (
                cls.COMMAND_OS_POPEN,
                "os.popen() passes commands to the shell",
                "CWE-78",
            ),
            "code-injection-eval": (
                cls.PYTHON_EVAL,
                "eval() executes arbitrary Python expressions",
                "CWE-94",
            ),
            "code-injection-exec": (
                cls.PYTHON_EXEC,
                "exec() executes arbitrary Python statements",
                "CWE-94",
            ),
            "code-injection-compile": (
                cls.PYTHON_COMPILE,
                "compile() prepares arbitrary code for execution",
                "CWE-94",
            ),
            "code-injection-pickle": (
                cls.UNSAFE_PICKLE,
                "pickle deserialization can execute arbitrary code",
                "CWE-502",
            ),
            "code-injection-yaml": (
                cls.UNSAFE_YAML,
                "Unsafe YAML loading can execute arbitrary code",
                "CWE-502",
            ),
            "nosql-mongoose-query": (
                cls.NOSQL_MONGOOSE_QUERY,
                "MongoDB/Mongoose query may receive unsanitized user input",
                "CWE-943",
            ),
            "nosql-json-parse-req": (
                cls.NOSQL_JSON_PARSE_REQ,
                "JSON.parse(req.*) result may be used in NoSQL query",
                "CWE-943",
            ),
            "js-command-injection-exec-template": (
                cls.JS_EXEC_TEMPLATE,
                "child_process exec/execSync with template literal interpolation",
                "CWE-78",
            ),
            "js-command-injection-exec-concat": (
                cls.JS_EXEC_CONCAT,
                "child_process exec/execSync with string concatenation",
                "CWE-78",
            ),
            "xxe-et-parse": (
                cls.XXE_ET_PARSE,
                "xml.etree.ElementTree parsing may allow XXE",
                "CWE-611",
            ),
            "xxe-lxml-resolve-entities": (
                cls.XXE_LXML_RESOLVE,
                "lxml parser with resolve_entities=True enables XXE",
                "CWE-611",
            ),
            "xxe-xml-sax": (
                cls.XXE_XML_SAX,
                "xml.sax parsing without feature disabling may allow XXE",
                "CWE-611",
            ),
        }

    @classmethod
    def _ssrf_patterns(cls) -> Dict[str, PatternEntry]:
        """Build the SSRF pattern dictionary."""
        return {
            "ssrf-py-urllib": (
                cls.SSRF_PY_URLLIB,
                "urllib.request.urlopen() with user-controlled URL (SSRF)",
                "CWE-918",
            ),
            "ssrf-py-requests": (
                cls.SSRF_PY_REQUESTS,
                "requests library HTTP call with user-controlled URL (SSRF)",
                "CWE-918",
            ),
            "ssrf-py-httpx": (
                cls.SSRF_PY_HTTPX,
                "httpx HTTP call with user-controlled URL (SSRF)",
                "CWE-918",
            ),
            "ssrf-js-fetch": (
                cls.SSRF_JS_FETCH,
                "fetch() with user-controlled URL (SSRF)",
                "CWE-918",
            ),
            "ssrf-js-axios": (
                cls.SSRF_JS_AXIOS,
                "axios HTTP call with user-controlled URL (SSRF)",
                "CWE-918",
            ),
        }

    @classmethod
    def _javascript_patterns(cls) -> Dict[str, PatternEntry]:
        """Build the JavaScript pattern dictionary."""
        return {
            "js-eval": (
                cls.JS_EVAL,
                "JavaScript eval() executes arbitrary code",
                "CWE-94",
            ),
            "js-function-constructor": (
                cls.JS_FUNCTION_CONSTRUCTOR,
                "new Function() creates code from a string (like eval)",
                "CWE-94",
            ),
            "js-inner-html": (
                cls.JS_INNER_HTML,
                "innerHTML assignment inserts unescaped HTML (XSS risk)",
                "CWE-79",
            ),
            "js-outer-html": (
                cls.JS_OUTER_HTML,
                "outerHTML assignment inserts unescaped HTML (XSS risk)",
                "CWE-79",
            ),
            "js-dangerously-set-inner-html": (
                cls.JS_DANGEROUSLY_SET_INNER_HTML,
                "React dangerouslySetInnerHTML bypasses XSS protection",
                "CWE-79",
            ),
            "js-document-write": (
                cls.JS_DOCUMENT_WRITE,
                "document.write() inserts unescaped content (XSS risk)",
                "CWE-79",
            ),
            "js-set-timeout-string": (
                cls.JS_SET_TIMEOUT_STRING,
                "setTimeout() with string argument is eval-like",
                "CWE-94",
            ),
            "js-set-interval-string": (
                cls.JS_SET_INTERVAL_STRING,
                "setInterval() with string argument is eval-like",
                "CWE-94",
            ),
        }

    @classmethod
    def _weak_crypto_patterns(cls) -> Dict[str, PatternEntry]:
        """Build the weak cryptography pattern dictionary."""
        return {
            "weak-crypto-md5": (
                cls.PYTHON_MD5,
                "Weak hash algorithm: MD5 (hashlib)",
                "CWE-327",
            ),
            "weak-crypto-sha1": (
                cls.PYTHON_SHA1,
                "Weak hash algorithm: SHA-1 (hashlib)",
                "CWE-327",
            ),
            "weak-crypto-des": (
                cls.PYTHON_DES,
                "Weak encryption algorithm: DES (PyCryptodome)",
                "CWE-327",
            ),
            "weak-crypto-rc4": (
                cls.PYTHON_RC4,
                "Weak encryption algorithm: RC4 (PyCryptodome)",
                "CWE-327",
            ),
            "weak-crypto-blowfish": (
                cls.PYTHON_BLOWFISH,
                "Weak encryption algorithm: Blowfish (PyCryptodome)",
                "CWE-327",
            ),
            "weak-crypto-ecb-mode": (
                cls.PYTHON_ECB_MODE,
                "Weak cipher mode: ECB (Electronic Codebook)",
                "CWE-327",
            ),
            "weak-crypto-md5-pycrypto": (
                cls.PYTHON_PYCRYPTO_MD5,
                "Weak hash algorithm: MD5 (PyCryptodome)",
                "CWE-327",
            ),
            "weak-crypto-sha1-pycrypto": (
                cls.PYTHON_PYCRYPTO_SHA1,
                "Weak hash algorithm: SHA-1 (PyCryptodome)",
                "CWE-327",
            ),
            "weak-crypto-md5-js": (
                cls.JS_CRYPTO_MD5,
                "Weak hash algorithm: MD5 (Node.js crypto)",
                "CWE-327",
            ),
            "weak-crypto-sha1-js": (
                cls.JS_CRYPTO_SHA1,
                "Weak hash algorithm: SHA-1 (Node.js crypto)",
                "CWE-327",
            ),
            "weak-crypto-des-js": (
                cls.JS_CRYPTO_DES,
                "Weak encryption algorithm: DES (Node.js crypto)",
                "CWE-327",
            ),
            "weak-crypto-rc4-js": (
                cls.JS_CRYPTO_RC4,
                "Weak encryption algorithm: RC4 (Node.js crypto)",
                "CWE-327",
            ),
            "weak-crypto-ecb-mode-js": (
                cls.JS_CRYPTO_ECB,
                "Weak cipher mode: ECB (Node.js crypto)",
                "CWE-327",
            ),
        }

    @classmethod
    def _configuration_patterns(cls) -> Dict[str, PatternEntry]:
        """Build the configuration pattern dictionary."""
        return {
            "debug-mode-django": (
                cls.DEBUG_DJANGO,
                "Django DEBUG = True enables verbose error pages",
                "CWE-489",
            ),
            "debug-mode-flask-attr": (
                cls.DEBUG_FLASK_ATTR,
                "Flask app.debug = True enables interactive debugger",
                "CWE-489",
            ),
            "debug-mode-flask-run": (
                cls.DEBUG_FLASK_RUN,
                "Flask app.run(debug=True) enables interactive debugger",
                "CWE-489",
            ),
            "debug-mode-node-env": (
                cls.DEBUG_NODE_ENV,
                "NODE_ENV set to development in configuration",
                "CWE-489",
            ),
            "cors-wildcard-header": (
                cls.CORS_WILDCARD,
                "CORS Access-Control-Allow-Origin set to wildcard (*)",
                "CWE-942",
            ),
            "cors-wildcard-flask": (
                cls.CORS_FLASK_WILDCARD,
                "Flask-CORS configured with wildcard origin",
                "CWE-942",
            ),
            "cors-allow-all-django": (
                cls.CORS_DJANGO_ALLOW_ALL,
                "Django CORS_ALLOW_ALL_ORIGINS = True",
                "CWE-942",
            ),
        }

    @classmethod
    def _auth_patterns(cls) -> Dict[str, PatternEntry]:
        """Build the authentication/authorization pattern dictionary."""
        return {
            "hardcoded-password": (
                cls.HARDCODED_PASSWORD,
                "Hardcoded password detected in source code",
                "CWE-798",
            ),
            "jwt-weak-secret": (
                cls.JWT_WEAK_SECRET,
                "JWT signed with a potentially weak secret (< 32 chars)",
                "CWE-287",
            ),
            "sensitive-local-storage": (
                cls.LOCAL_STORAGE_SENSITIVE,
                "Sensitive data stored in browser localStorage/sessionStorage",
                "CWE-922",
            ),
        }

    # ===================================================================
    # PRIVATE CATEGORY BUILDERS (List-based patterns)
    # ===================================================================

    @classmethod
    def _list_patterns_to_dict(cls, pattern_list: List[dict]) -> Dict[str, PatternEntry]:
        """Convert a list of pattern dicts to the standard PatternEntry dict format.

        Helper method that transforms the list-based pattern format
        (list of dicts with 'pattern', 'rule_id', 'description', 'cwe' keys)
        into the canonical ``Dict[str, PatternEntry]`` format used by
        all retrieval methods.

        Args:
            pattern_list: List of pattern dictionaries, each with keys
                'pattern', 'rule_id', 'description', 'cwe'.

        Returns:
            Dictionary mapping rule IDs to (regex, description, cwe_id) tuples.
        """
        result: Dict[str, PatternEntry] = {}
        for entry in pattern_list:
            result[entry["rule_id"]] = (
                entry["pattern"],
                entry["description"],
                entry["cwe"],
            )
        return result

    @classmethod
    def _ssrf_list_patterns(cls) -> Dict[str, PatternEntry]:
        """Build the extended SSRF pattern dictionary from list-based attributes."""
        patterns: Dict[str, PatternEntry] = {}
        patterns.update(cls._list_patterns_to_dict(cls.SSRF_PATTERNS))
        patterns.update(cls._list_patterns_to_dict(cls.JS_SSRF_PATTERNS))
        return patterns

    @classmethod
    def _xxe_list_patterns(cls) -> Dict[str, PatternEntry]:
        """Build the extended XXE pattern dictionary from list-based attributes."""
        return cls._list_patterns_to_dict(cls.XXE_PATTERNS)

    @classmethod
    def _nosql_injection_list_patterns(cls) -> Dict[str, PatternEntry]:
        """Build the extended NoSQL injection pattern dictionary from list-based attributes."""
        return cls._list_patterns_to_dict(cls.NOSQL_INJECTION_PATTERNS)

    @classmethod
    def _deserialization_list_patterns(cls) -> Dict[str, PatternEntry]:
        """Build the deserialization pattern dictionary from list-based attributes."""
        return cls._list_patterns_to_dict(cls.DESERIALIZATION_PATTERNS)

    @classmethod
    def _js_command_injection_list_patterns(cls) -> Dict[str, PatternEntry]:
        """Build the JS command injection pattern dictionary from list-based attributes."""
        return cls._list_patterns_to_dict(cls.JS_COMMAND_INJECTION_PATTERNS)

    @classmethod
    def _extended_weak_crypto_list_patterns(cls) -> Dict[str, PatternEntry]:
        """Build the extended weak crypto pattern dictionary from list-based attributes."""
        return cls._list_patterns_to_dict(cls.EXTENDED_WEAK_CRYPTO_PATTERNS)

    @classmethod
    def _access_control_list_patterns(cls) -> Dict[str, PatternEntry]:
        """Build the extended access control pattern dictionary from list-based attributes."""
        patterns: Dict[str, PatternEntry] = {}
        patterns.update(cls._list_patterns_to_dict(cls.ACCESS_CONTROL_PATTERNS))
        patterns.update(cls._list_patterns_to_dict(cls.JS_ACCESS_CONTROL_PATTERNS))
        return patterns

    @classmethod
    def _insecure_transport_list_patterns(cls) -> Dict[str, PatternEntry]:
        """Build the insecure transport pattern dictionary from list-based attributes."""
        return cls._list_patterns_to_dict(cls.INSECURE_TRANSPORT_PATTERNS)
