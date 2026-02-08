"""Authentication and authorization vulnerability analyzer.

Detects authentication failures, authorization gaps, hardcoded passwords,
weak JWT configurations, and insecure session management in Python and
JavaScript/TypeScript source code. This analyzer maps to OWASP A01:2021
(Broken Access Control) and A07:2021 (Identification and Authentication
Failures).

Detection strategies:
    1. **Hardcoded passwords** -- scans string literal assignments for
       variables whose names match password-related keywords (``password``,
       ``passwd``, ``pwd``, ``secret``, ``api_key``). Direct string
       assignments are flagged; values loaded from environment variables
       or config files are excluded.

    2. **Weak JWT** -- regex-based detection of JWT signing with short
       secrets (fewer than 32 characters) and JWT payload construction
       that omits the ``exp`` (expiration) claim. Both ``jwt.encode``
       (Python PyJWT) and ``jsonwebtoken.sign`` (Node.js) call patterns
       are covered.

    3. **Insecure sessions** -- detects session cookie configuration that
       is missing the ``secure``, ``httpOnly``, or ``sameSite`` flags.
       Covers Python framework patterns (Flask, Django) and JavaScript
       patterns (express-session, ``res.cookie``).

    4. **Missing authentication** -- uses function decorator information
       from :class:`ParseResult` to identify route handler functions that
       lack authentication decorators (``@login_required``,
       ``@authenticated``, ``@jwt_required``, etc.). Only flags functions
       that are themselves decorated with a route decorator
       (``@app.route``, ``@router.get``, etc.).

All detections produce :class:`Finding` objects categorized under
:attr:`OWASPCategory.A07_AUTH_FAILURES` (for password, JWT, and session
issues) or :attr:`OWASPCategory.A01_ACCESS_CONTROL` (for missing
authentication), with appropriate CWE references:
    - CWE-798: Use of Hard-coded Credentials (hardcoded passwords)
    - CWE-287: Improper Authentication (weak JWT)
    - CWE-614: Sensitive Cookie in HTTPS Session Without 'Secure' Attribute
    - CWE-306: Missing Authentication for Critical Function

This module uses only the Python standard library and has no external
dependencies.

Classes:
    AuthAnalyzer: Main analyzer class with analyze() entry point.

References:
    - FRS FR-8: AuthAnalyzer
    - OWASP A01:2021 Broken Access Control
    - OWASP A07:2021 Identification and Authentication Failures
    - CWE-287: Improper Authentication
    - CWE-306: Missing Authentication for Critical Function
    - CWE-614: Sensitive Cookie Without 'Secure' Attribute
    - CWE-798: Use of Hard-coded Credentials
"""

import logging
import re
from typing import Any, Dict, List, Set, Tuple

from lib.models.finding import Finding, OWASPCategory, Severity
from lib.models.parse_result import ParseResult

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Password-related variable name patterns
# ---------------------------------------------------------------------------

# Variable names that strongly suggest a password or secret assignment.
_PASSWORD_VARIABLE_NAMES: Set[str] = {
    "password",
    "passwd",
    "pwd",
    "secret",
    "api_key",
    "apikey",
    "api_secret",
    "auth_token",
    "access_token",
    "secret_key",
    "private_key",
}

# Regex to match assignment of a password variable to a string literal.
# Covers Python and JS:
#   password = "value"
#   PASSWORD = 'value'
#   const api_key = "value"
#   let secret = 'value'
#   var pwd = "value"
# Captures: (variable_name, quote_char, value)
_PASSWORD_ASSIGN_PATTERN = re.compile(
    r"""(?:^|[\s;])"""
    r"""(?:const\s+|let\s+|var\s+)?"""
    r"""("""
    + "|".join(re.escape(name) for name in sorted(_PASSWORD_VARIABLE_NAMES))
    + r""")"""
    r"""\s*[:=]\s*"""
    r"""(['"])(.+?)\2""",
    re.IGNORECASE | re.MULTILINE,
)

# Patterns indicating the value comes from an environment variable or
# config lookup (not a hardcoded literal). These are safe and should be
# excluded from hardcoded password findings.
_ENV_SAFE_PATTERNS = re.compile(
    r"""os\.environ|os\.getenv|environ\.get|"""
    r"""config\[|config\.get|settings\.|"""
    r"""process\.env|getenv\(|"""
    r"""SECRET_KEY\s*=\s*os\.|"""
    r"""import_module|__import__""",
    re.IGNORECASE,
)

# Placeholder / dummy values that are not real credentials.
_PLACEHOLDER_VALUES: Set[str] = {
    "changeme",
    "change_me",
    "your_password",
    "your-password",
    "your_secret",
    "your-secret",
    "xxx",
    "placeholder",
    "TODO",
    "FIXME",
    "password",
    "secret",
    "example",
    "test",
}


# ---------------------------------------------------------------------------
# JWT patterns
# ---------------------------------------------------------------------------

# Python PyJWT: jwt.encode(payload, "short_secret", algorithm="HS256")
# Captures the secret string argument.
_JWT_ENCODE_PYTHON_PATTERN = re.compile(
    r"""jwt\.encode\s*\(\s*"""
    r"""(?:[^,]+),\s*"""               # payload (any expr)
    r"""(['"])(.+?)\1""",              # secret as string literal
    re.IGNORECASE,
)

# Node.js jsonwebtoken: jwt.sign(payload, "short_secret", {algorithm: "HS256"})
_JWT_SIGN_JS_PATTERN = re.compile(
    r"""jwt\.sign\s*\(\s*"""
    r"""(?:[^,]+),\s*"""               # payload
    r"""(['"])(.+?)\1""",              # secret as string literal
    re.IGNORECASE,
)

# Detect JWT secret assignment: JWT_SECRET = "short"
_JWT_SECRET_ASSIGN_PATTERN = re.compile(
    r"""(?:jwt[_-]?secret|jwt[_-]?key|signing[_-]?key|token[_-]?secret)"""
    r"""\s*[:=]\s*['"](.+?)['"]""",
    re.IGNORECASE,
)

# Payload construction without "exp" -- look for dict construction that
# includes JWT-like claims but no "exp" key.
_JWT_PAYLOAD_NO_EXP_PATTERN = re.compile(
    r"""(?:payload|token_data|claims|jwt_payload)\s*=\s*\{"""
    r"""(?:(?![\}]).)*"""              # contents of the dict
    r"""['"](?:sub|iss|iat|aud|nbf)['"]"""  # has JWT claims
    r"""(?:(?![\}]).)*"""
    r"""\}""",
    re.DOTALL | re.IGNORECASE,
)


# ---------------------------------------------------------------------------
# Session cookie patterns
# ---------------------------------------------------------------------------

# Python Flask: session cookie configuration
# app.config["SESSION_COOKIE_SECURE"] = False
_FLASK_SESSION_SECURE_PATTERN = re.compile(
    r"""SESSION_COOKIE_SECURE['"]\s*\]\s*=\s*False""",
    re.IGNORECASE,
)

_FLASK_SESSION_HTTPONLY_PATTERN = re.compile(
    r"""SESSION_COOKIE_HTTPONLY['"]\s*\]\s*=\s*False""",
    re.IGNORECASE,
)

_FLASK_SESSION_SAMESITE_PATTERN = re.compile(
    r"""SESSION_COOKIE_SAMESITE['"]\s*\]\s*=\s*(?:None|['"]None['"])""",
    re.IGNORECASE,
)

# Django: SESSION_COOKIE_SECURE = False
_DJANGO_SESSION_SECURE_PATTERN = re.compile(
    r"""^SESSION_COOKIE_SECURE\s*=\s*False""",
    re.MULTILINE,
)

_DJANGO_SESSION_HTTPONLY_PATTERN = re.compile(
    r"""^SESSION_COOKIE_HTTPONLY\s*=\s*False""",
    re.MULTILINE,
)

# Express: session({ cookie: { secure: false } }) or missing secure
_EXPRESS_SESSION_INSECURE_PATTERN = re.compile(
    r"""(?:session|cookie)\s*\(\s*\{"""
    r"""(?:(?!\}\s*\)).)*"""
    r"""secure\s*:\s*false"""
    r"""(?:(?!\}\s*\)).)*"""
    r"""\}""",
    re.DOTALL | re.IGNORECASE,
)

# res.cookie("name", value) without secure/httpOnly options
_RES_COOKIE_PATTERN = re.compile(
    r"""\.cookie\s*\(\s*['"][^'"]+['"]\s*,\s*[^,)]+""",
    re.IGNORECASE,
)

# Generic cookie configuration with secure=False or httponly=False
_COOKIE_SECURE_FALSE_PATTERN = re.compile(
    r"""secure\s*[:=]\s*(?:False|false)""",
)

_COOKIE_HTTPONLY_FALSE_PATTERN = re.compile(
    r"""http[_-]?only\s*[:=]\s*(?:False|false)""",
    re.IGNORECASE,
)


# ---------------------------------------------------------------------------
# Route decorator patterns (to identify route handlers)
# ---------------------------------------------------------------------------

# Decorator names that indicate a function is a route handler.
_ROUTE_DECORATOR_PREFIXES: Tuple[str, ...] = (
    "app.route",
    "app.get",
    "app.post",
    "app.put",
    "app.delete",
    "app.patch",
    "app.options",
    "app.head",
    "router.route",
    "router.get",
    "router.post",
    "router.put",
    "router.delete",
    "router.patch",
    "router.options",
    "router.head",
    "blueprint.route",
    "blueprint.get",
    "blueprint.post",
    "api.route",
    "api.get",
    "api.post",
    "api.put",
    "api.delete",
    "api_view",
    "action",
)

# Decorator names that indicate the route has authentication applied.
_AUTH_DECORATOR_NAMES: Set[str] = {
    "login_required",
    "authenticated",
    "require_auth",
    "requires_auth",
    "jwt_required",
    "token_required",
    "auth_required",
    "permission_required",
    "permissions_required",
    "require_login",
    "require_authentication",
    "protect",
    "protected",
    "verify_token",
    "check_auth",
    "admin_required",
    "staff_required",
    "superuser_required",
    "role_required",
    "has_permission",
    "has_role",
    "authorize",
    "csrf_protect",
}

# Partial matches for auth decorators (e.g., auth.login_required,
# flask_login.login_required). We check if any segment of a dotted
# decorator name is in this set.
_AUTH_DECORATOR_SEGMENTS: Set[str] = {
    "login_required",
    "authenticated",
    "jwt_required",
    "token_required",
    "auth_required",
    "permission_required",
    "require_auth",
    "protect",
    "authorize",
}

# Route patterns detectable via regex on raw source (for JS/TS).
_JS_ROUTE_PATTERN = re.compile(
    r"""(?:app|router)\s*\.\s*(?:get|post|put|delete|patch|all|use)\s*\(""",
    re.IGNORECASE,
)


# ---------------------------------------------------------------------------
# Finding ID generator
# ---------------------------------------------------------------------------


class _FindingIDGenerator:
    """Thread-unsafe sequential ID generator for auth findings.

    Produces IDs in the format "AUTH-001", "AUTH-002", etc. A new generator
    is created for each analyze() invocation so IDs start from 1.
    """

    def __init__(self) -> None:
        self._counter = 0

    def next_id(self) -> str:
        """Return the next sequential finding ID."""
        self._counter += 1
        return f"AUTH-{self._counter:03d}"


# ---------------------------------------------------------------------------
# Main analyzer class
# ---------------------------------------------------------------------------


class AuthAnalyzer:
    """Detect authentication and authorization vulnerabilities.

    This analyzer implements four complementary detection strategies that
    together provide broad coverage of authentication and access control
    weakness patterns:

    1. **Hardcoded passwords** (``_detect_hardcoded_passwords``): Scans
       string literal assignments in source code for variable names that
       match password-related keywords. Values sourced from environment
       variables or config lookups are excluded. Produces CRITICAL findings
       under CWE-798.

    2. **Weak JWT** (``_detect_weak_jwt``): Scans raw source for JWT
       signing calls (``jwt.encode`` in Python, ``jwt.sign`` in Node.js)
       with short secret strings (fewer than 32 characters), and for JWT
       payload construction that omits the ``exp`` expiration claim.
       Produces HIGH findings under CWE-287.

    3. **Insecure sessions** (``_detect_insecure_sessions``): Detects
       session cookie configuration that explicitly disables or omits the
       ``secure``, ``httpOnly``, or ``sameSite`` flags. Covers Flask,
       Django, and Express session patterns. Produces MEDIUM findings
       under CWE-614.

    4. **Missing authentication** (``_detect_missing_authentication``):
       Uses decorator information from ParseResult to identify route
       handler functions that lack authentication decorators. Only flags
       functions that are decorated with a route decorator (e.g.,
       ``@app.route``, ``@router.get``). Produces HIGH findings under
       CWE-306.

    Attributes:
        MIN_JWT_SECRET_LENGTH: Minimum acceptable length for JWT signing
            secrets. Secrets shorter than this are flagged. Default: 32.
        VERSION: Analyzer version string for AssessmentResult tracking.

    Usage::

        analyzer = AuthAnalyzer()
        findings = analyzer.analyze(parsed_files, config={})

    Configuration:
        The ``config`` dict passed to ``analyze()`` supports these optional
        keys:

        - ``skip_hardcoded_passwords`` (bool): Disable hardcoded password
          detection.
        - ``skip_weak_jwt`` (bool): Disable weak JWT detection.
        - ``skip_insecure_sessions`` (bool): Disable insecure session
          detection.
        - ``skip_missing_auth`` (bool): Disable missing authentication
          detection.
        - ``min_jwt_secret_length`` (int): Override the minimum JWT secret
          length threshold.
    """

    MIN_JWT_SECRET_LENGTH: int = 32
    VERSION: str = "1.0.0"

    def analyze(
        self,
        parsed_files: List[ParseResult],
        config: Dict[str, Any],
    ) -> List[Finding]:
        """Run all authentication detection strategies on the parsed files.

        Iterates over each parsed file and applies hardcoded password,
        weak JWT, insecure session, and missing authentication detection.
        Results from all four strategies are combined into a single list
        of findings.

        Args:
            parsed_files: List of ParseResult objects from the parsing
                phase. Each represents one source file with extracted
                string literals, raw source content, and decorator
                information.
            config: Optional configuration overrides. Supported keys:
                ``skip_hardcoded_passwords`` (bool),
                ``skip_weak_jwt`` (bool),
                ``skip_insecure_sessions`` (bool),
                ``skip_missing_auth`` (bool),
                ``min_jwt_secret_length`` (int).

        Returns:
            List of Finding objects, one per detected issue. Findings are
            ordered by file path and then by line number within each file.
        """
        findings: List[Finding] = []
        id_gen = _FindingIDGenerator()

        skip_passwords = config.get("skip_hardcoded_passwords", False)
        skip_jwt = config.get("skip_weak_jwt", False)
        skip_sessions = config.get("skip_insecure_sessions", False)
        skip_auth = config.get("skip_missing_auth", False)
        min_jwt_length = config.get(
            "min_jwt_secret_length", self.MIN_JWT_SECRET_LENGTH
        )

        for parsed_file in parsed_files:
            # Skip lockfiles -- they do not contain executable code.
            if parsed_file.language == "lockfile":
                continue

            # 1. Hardcoded password detection
            if not skip_passwords:
                findings.extend(
                    self._detect_hardcoded_passwords(parsed_file, id_gen)
                )

            # 2. Weak JWT detection
            if not skip_jwt:
                findings.extend(
                    self._detect_weak_jwt(
                        parsed_file, id_gen, min_jwt_length
                    )
                )

            # 3. Insecure session configuration
            if not skip_sessions:
                findings.extend(
                    self._detect_insecure_sessions(parsed_file, id_gen)
                )

            # 4. Missing authentication on route handlers
            if not skip_auth:
                findings.extend(
                    self._detect_missing_authentication(parsed_file, id_gen)
                )

        return findings

    # -----------------------------------------------------------------
    # Strategy 1: Hardcoded password detection
    # -----------------------------------------------------------------

    def _detect_hardcoded_passwords(
        self,
        parsed_file: ParseResult,
        id_gen: _FindingIDGenerator,
    ) -> List[Finding]:
        """Detect hardcoded passwords and secrets in variable assignments.

        Scans each raw source line for assignments where the left-hand side
        is a password-related variable name and the right-hand side is a
        string literal. Assignments that load values from environment
        variables, config files, or other dynamic sources are excluded.

        Additionally scans parsed string literals for connection strings
        that embed credentials (e.g., ``mongodb://user:pass@host``).

        Args:
            parsed_file: A single parsed file result containing raw source
                and string literals.
            id_gen: Sequential ID generator for creating finding IDs.

        Returns:
            List of Finding objects for each hardcoded password detected.
        """
        findings: List[Finding] = []

        if not parsed_file.raw_source:
            return findings

        # Track (line_number,) to avoid duplicates.
        seen_lines: Set[int] = set()

        # Strategy A: Scan raw source for password variable assignments.
        for match in _PASSWORD_ASSIGN_PATTERN.finditer(parsed_file.raw_source):
            var_name = match.group(1)
            value = match.group(3)

            # Determine line number from match offset.
            line_number = (
                parsed_file.raw_source[: match.start()].count("\n") + 1
            )

            if line_number in seen_lines:
                continue

            # Get the full source line for context analysis.
            full_line = self._get_source_line(
                parsed_file.source_lines, line_number
            )

            # Exclude assignments from environment variables or config.
            if _ENV_SAFE_PATTERNS.search(full_line):
                continue

            # Exclude placeholder / dummy values.
            if value.lower() in _PLACEHOLDER_VALUES:
                continue

            # Exclude very short values (likely defaults or empty sentinels).
            if len(value) < 3:
                continue

            # Exclude values that look like variable references or function
            # calls (not actual string literals being used as passwords).
            if self._is_comment_line(full_line):
                continue

            seen_lines.add(line_number)

            code_sample = self._build_code_sample(
                parsed_file.source_lines, line_number
            )

            # Higher confidence for longer, more realistic password values.
            confidence = 0.90 if len(value) >= 8 else 0.80

            findings.append(
                Finding(
                    id=id_gen.next_id(),
                    rule_id="hardcoded-password",
                    category=OWASPCategory.A07_AUTH_FAILURES,
                    severity=Severity.CRITICAL,
                    title=(
                        f"Hardcoded password in variable '{var_name}'"
                    ),
                    description=(
                        f"The variable '{var_name}' is assigned a hardcoded "
                        "string value that appears to be a password or secret. "
                        "Hardcoded credentials in source code are a critical "
                        "vulnerability because anyone with access to the code "
                        "(including version control history) can extract them. "
                        "Automated tools actively scan public repositories for "
                        "such patterns."
                    ),
                    file_path=parsed_file.file_path,
                    line_number=line_number,
                    code_sample=code_sample,
                    remediation=(
                        "Move the credential to an environment variable or a "
                        "secrets management service. For Python: use "
                        "os.environ['PASSWORD'] or a library like python-dotenv. "
                        "For Node.js: use process.env.PASSWORD. Store secrets in "
                        "a .env file excluded from version control via .gitignore. "
                        "For production, use a secrets manager such as AWS Secrets "
                        "Manager, HashiCorp Vault, or Azure Key Vault."
                    ),
                    cwe_id="CWE-798",
                    confidence=confidence,
                    metadata={
                        "variable_name": var_name.lower(),
                        "value_length": len(value),
                        "language": parsed_file.language,
                    },
                )
            )

        # Strategy B: Detect connection strings with embedded credentials.
        findings.extend(
            self._detect_credential_urls(parsed_file, id_gen, seen_lines)
        )

        return findings

    def _detect_credential_urls(
        self,
        parsed_file: ParseResult,
        id_gen: _FindingIDGenerator,
        seen_lines: Set[int],
    ) -> List[Finding]:
        """Detect connection strings with embedded credentials.

        Searches for patterns like ``mongodb://user:pass@host`` or
        ``postgresql://admin:secret@db.example.com`` in string literals.

        Args:
            parsed_file: A single parsed file result.
            id_gen: Sequential ID generator for creating finding IDs.
            seen_lines: Set of already-processed line numbers (read-only).

        Returns:
            List of Finding objects for credential URL detections.
        """
        findings: List[Finding] = []

        # Pattern: protocol://user:password@host
        cred_url_pattern = re.compile(
            r"""(?:mongodb|postgres(?:ql)?|mysql|redis|amqp|"""
            r"""ftp|smtp|ldap|mssql)://"""
            r"""[^:]+:([^@]+)@""",
            re.IGNORECASE,
        )

        # Collect all string values with their line numbers.
        entries = self._collect_string_entries(parsed_file)

        for value, line_number, _context in entries:
            if line_number in seen_lines:
                continue

            match = cred_url_pattern.search(value)
            if not match:
                continue

            password_part = match.group(1)

            # Skip placeholder values.
            if password_part.lower() in _PLACEHOLDER_VALUES:
                continue

            # Skip environment variable references in the URL.
            if "${" in password_part or "%" in password_part:
                continue

            if len(password_part) < 3:
                continue

            code_sample = self._build_code_sample(
                parsed_file.source_lines, line_number
            )

            findings.append(
                Finding(
                    id=id_gen.next_id(),
                    rule_id="hardcoded-password",
                    category=OWASPCategory.A07_AUTH_FAILURES,
                    severity=Severity.CRITICAL,
                    title="Hardcoded credentials in connection string",
                    description=(
                        "A database or service connection string contains "
                        "embedded credentials. Connection strings with "
                        "hardcoded usernames and passwords are a critical "
                        "vulnerability. Anyone with code access can extract "
                        "the credentials and connect to the service directly."
                    ),
                    file_path=parsed_file.file_path,
                    line_number=line_number,
                    code_sample=code_sample,
                    remediation=(
                        "Remove credentials from connection strings. Use "
                        "environment variables for each component: "
                        "DB_USER, DB_PASSWORD, DB_HOST. Alternatively, use "
                        "IAM-based authentication (e.g., AWS RDS IAM auth) "
                        "that does not require passwords in connection strings. "
                        "For local development, use a .env file excluded from "
                        "version control."
                    ),
                    cwe_id="CWE-798",
                    confidence=0.90,
                    metadata={
                        "detection_type": "credential_url",
                        "language": parsed_file.language,
                    },
                )
            )

        return findings

    # -----------------------------------------------------------------
    # Strategy 2: Weak JWT detection
    # -----------------------------------------------------------------

    def _detect_weak_jwt(
        self,
        parsed_file: ParseResult,
        id_gen: _FindingIDGenerator,
        min_secret_length: int,
    ) -> List[Finding]:
        """Detect weak JWT configurations.

        Scans raw source code for two categories of JWT weakness:

        1. **Short signing secrets**: JWT encode/sign calls where the
           secret argument is a string literal shorter than
           ``min_secret_length`` characters. Short secrets can be
           brute-forced.

        2. **Missing expiration**: JWT payload construction that includes
           standard claims (sub, iss, iat) but omits the ``exp``
           (expiration) claim. Tokens without expiration never expire and
           remain valid indefinitely if compromised.

        Args:
            parsed_file: A single parsed file result containing raw source.
            id_gen: Sequential ID generator for creating finding IDs.
            min_secret_length: Minimum acceptable JWT secret length.

        Returns:
            List of Finding objects for each JWT weakness detected.
        """
        findings: List[Finding] = []

        if not parsed_file.raw_source:
            return findings

        # Track (rule_id, line_number) to avoid duplicates.
        seen: Set[Tuple[str, int]] = set()

        # --- Detect short JWT secrets in encode/sign calls ---
        jwt_patterns = [
            _JWT_ENCODE_PYTHON_PATTERN,
            _JWT_SIGN_JS_PATTERN,
        ]

        for pattern in jwt_patterns:
            for match in pattern.finditer(parsed_file.raw_source):
                secret_value = match.group(2)
                line_number = (
                    parsed_file.raw_source[: match.start()].count("\n") + 1
                )

                key = ("weak-jwt-secret", line_number)
                if key in seen:
                    continue

                # Check if the secret is too short.
                if len(secret_value) >= min_secret_length:
                    continue

                seen.add(key)

                code_sample = self._build_code_sample(
                    parsed_file.source_lines, line_number
                )

                findings.append(
                    Finding(
                        id=id_gen.next_id(),
                        rule_id="weak-jwt-secret",
                        category=OWASPCategory.A07_AUTH_FAILURES,
                        severity=Severity.HIGH,
                        title=(
                            "JWT signed with short secret "
                            f"({len(secret_value)} characters)"
                        ),
                        description=(
                            f"A JWT signing call uses a secret that is only "
                            f"{len(secret_value)} characters long. The minimum "
                            f"recommended length is {min_secret_length} characters. "
                            "Short secrets can be brute-forced using tools like "
                            "hashcat or jwt-cracker, allowing an attacker to "
                            "forge valid tokens and impersonate any user. HMAC "
                            "signing with HS256 requires a secret with at least "
                            "256 bits (32 bytes) of entropy to be considered "
                            "secure."
                        ),
                        file_path=parsed_file.file_path,
                        line_number=line_number,
                        code_sample=code_sample,
                        remediation=(
                            "Use a cryptographically random secret with at "
                            f"least {min_secret_length} characters (256 bits). "
                            "Generate with: python -c \"import secrets; "
                            "print(secrets.token_hex(32))\" or "
                            "openssl rand -hex 32. Store the secret in an "
                            "environment variable, never in source code. "
                            "Consider using RS256 (asymmetric) instead of HS256 "
                            "for improved key management."
                        ),
                        cwe_id="CWE-287",
                        confidence=0.90,
                        metadata={
                            "secret_length": len(secret_value),
                            "min_required": min_secret_length,
                            "language": parsed_file.language,
                        },
                    )
                )

        # --- Detect short JWT secrets in variable assignments ---
        for match in _JWT_SECRET_ASSIGN_PATTERN.finditer(
            parsed_file.raw_source
        ):
            secret_value = match.group(1)
            line_number = (
                parsed_file.raw_source[: match.start()].count("\n") + 1
            )

            key = ("weak-jwt-secret", line_number)
            if key in seen:
                continue

            # Check if the assigned secret is too short.
            if len(secret_value) >= min_secret_length:
                continue

            # Exclude environment variable references.
            full_line = self._get_source_line(
                parsed_file.source_lines, line_number
            )
            if _ENV_SAFE_PATTERNS.search(full_line):
                continue

            seen.add(key)

            code_sample = self._build_code_sample(
                parsed_file.source_lines, line_number
            )

            findings.append(
                Finding(
                    id=id_gen.next_id(),
                    rule_id="weak-jwt-secret",
                    category=OWASPCategory.A07_AUTH_FAILURES,
                    severity=Severity.HIGH,
                    title=(
                        "JWT secret variable assigned short value "
                        f"({len(secret_value)} characters)"
                    ),
                    description=(
                        "A variable used for JWT signing is assigned a string "
                        f"value of only {len(secret_value)} characters. JWT "
                        "secrets should be at least "
                        f"{min_secret_length} characters long to resist "
                        "brute-force attacks. Hardcoded JWT secrets also pose "
                        "a credential exposure risk."
                    ),
                    file_path=parsed_file.file_path,
                    line_number=line_number,
                    code_sample=code_sample,
                    remediation=(
                        "Generate a cryptographically random secret with at "
                        f"least {min_secret_length} characters and store it in "
                        "an environment variable. Never hardcode JWT secrets. "
                        "Example: JWT_SECRET = os.environ['JWT_SECRET']"
                    ),
                    cwe_id="CWE-287",
                    confidence=0.85,
                    metadata={
                        "secret_length": len(secret_value),
                        "min_required": min_secret_length,
                        "detection_type": "variable_assignment",
                        "language": parsed_file.language,
                    },
                )
            )

        # --- Detect missing expiration in JWT payloads ---
        findings.extend(
            self._detect_missing_jwt_expiration(parsed_file, id_gen, seen)
        )

        return findings

    def _detect_missing_jwt_expiration(
        self,
        parsed_file: ParseResult,
        id_gen: _FindingIDGenerator,
        seen: Set[Tuple[str, int]],
    ) -> List[Finding]:
        """Detect JWT payloads that are missing the 'exp' claim.

        Looks for dictionary constructions assigned to JWT-related variable
        names that contain standard JWT claims (sub, iss, iat) but do not
        include an 'exp' key.

        Args:
            parsed_file: A single parsed file result.
            id_gen: Sequential ID generator.
            seen: Set of (rule_id, line_number) pairs already detected.

        Returns:
            List of Finding objects for missing JWT expiration.
        """
        findings: List[Finding] = []

        if not parsed_file.raw_source:
            return findings

        for match in _JWT_PAYLOAD_NO_EXP_PATTERN.finditer(
            parsed_file.raw_source
        ):
            matched_text = match.group(0)

            # Verify that 'exp' is indeed missing from the payload dict.
            if re.search(r"""['"]exp['"]""", matched_text):
                continue

            line_number = (
                parsed_file.raw_source[: match.start()].count("\n") + 1
            )

            key = ("missing-jwt-expiration", line_number)
            if key in seen:
                continue
            seen.add(key)

            code_sample = self._build_code_sample(
                parsed_file.source_lines, line_number
            )

            findings.append(
                Finding(
                    id=id_gen.next_id(),
                    rule_id="missing-jwt-expiration",
                    category=OWASPCategory.A07_AUTH_FAILURES,
                    severity=Severity.HIGH,
                    title="JWT payload missing 'exp' (expiration) claim",
                    description=(
                        "A JWT payload dictionary is constructed with standard "
                        "claims (sub, iss, iat, etc.) but does not include the "
                        "'exp' (expiration) claim. Tokens without an expiration "
                        "remain valid indefinitely. If a token is leaked or "
                        "stolen, the attacker can use it forever unless the "
                        "server maintains a token revocation list."
                    ),
                    file_path=parsed_file.file_path,
                    line_number=line_number,
                    code_sample=code_sample,
                    remediation=(
                        "Always include an 'exp' claim in JWT payloads. "
                        "For Python PyJWT: payload['exp'] = datetime.utcnow() "
                        "+ timedelta(hours=1). For Node.js jsonwebtoken: "
                        "jwt.sign(payload, secret, {expiresIn: '1h'}). "
                        "Use short expiration times (15 minutes to 1 hour) for "
                        "access tokens and implement refresh token rotation "
                        "for longer sessions."
                    ),
                    cwe_id="CWE-287",
                    confidence=0.80,
                    metadata={
                        "detection_type": "missing_expiration",
                        "language": parsed_file.language,
                    },
                )
            )

        return findings

    # -----------------------------------------------------------------
    # Strategy 3: Insecure session detection
    # -----------------------------------------------------------------

    def _detect_insecure_sessions(
        self,
        parsed_file: ParseResult,
        id_gen: _FindingIDGenerator,
    ) -> List[Finding]:
        """Detect insecure session cookie configurations.

        Scans raw source code for session cookie settings that explicitly
        disable or omit security flags. Covers Flask, Django, and Express
        patterns.

        Detection targets:
        - ``secure=False`` or missing ``secure`` flag
        - ``httpOnly=False`` or missing ``httpOnly`` flag
        - ``sameSite=None`` without ``secure=True``

        Args:
            parsed_file: A single parsed file result containing raw source.
            id_gen: Sequential ID generator for creating finding IDs.

        Returns:
            List of Finding objects for each insecure session setting.
        """
        findings: List[Finding] = []

        if not parsed_file.raw_source:
            return findings

        # Track (rule_id, line_number) to avoid duplicates.
        seen: Set[Tuple[str, int]] = set()

        # --- Detect secure=False patterns ---
        secure_false_patterns = [
            (_FLASK_SESSION_SECURE_PATTERN, "Flask SESSION_COOKIE_SECURE=False"),
            (_DJANGO_SESSION_SECURE_PATTERN, "Django SESSION_COOKIE_SECURE=False"),
            (_COOKIE_SECURE_FALSE_PATTERN, "Cookie secure=False"),
        ]

        for pattern, detection_type in secure_false_patterns:
            for match in pattern.finditer(parsed_file.raw_source):
                line_number = (
                    parsed_file.raw_source[: match.start()].count("\n") + 1
                )

                key = ("insecure-session-cookie", line_number)
                if key in seen:
                    continue
                seen.add(key)

                code_sample = self._build_code_sample(
                    parsed_file.source_lines, line_number
                )

                findings.append(
                    Finding(
                        id=id_gen.next_id(),
                        rule_id="insecure-session-cookie",
                        category=OWASPCategory.A07_AUTH_FAILURES,
                        severity=Severity.MEDIUM,
                        title="Session cookie missing 'secure' flag",
                        description=(
                            "A session cookie is configured without the "
                            "'secure' flag (or with secure=False). Without "
                            "the secure flag, the browser will send the "
                            "session cookie over unencrypted HTTP connections, "
                            "allowing an attacker on the network to intercept "
                            "it via a man-in-the-middle attack and hijack the "
                            "user's session."
                        ),
                        file_path=parsed_file.file_path,
                        line_number=line_number,
                        code_sample=code_sample,
                        remediation=(
                            "Set the secure flag to True on all session cookies. "
                            "For Flask: app.config['SESSION_COOKIE_SECURE'] = True. "
                            "For Django: SESSION_COOKIE_SECURE = True. "
                            "For Express: session({cookie: {secure: true}}). "
                            "Ensure your application is served over HTTPS in "
                            "production."
                        ),
                        cwe_id="CWE-614",
                        confidence=0.85,
                        metadata={
                            "detection_type": detection_type,
                            "flag": "secure",
                            "language": parsed_file.language,
                        },
                    )
                )

        # --- Detect httpOnly=False patterns ---
        httponly_false_patterns = [
            (_FLASK_SESSION_HTTPONLY_PATTERN, "Flask SESSION_COOKIE_HTTPONLY=False"),
            (_DJANGO_SESSION_HTTPONLY_PATTERN, "Django SESSION_COOKIE_HTTPONLY=False"),
            (_COOKIE_HTTPONLY_FALSE_PATTERN, "Cookie httpOnly=False"),
        ]

        for pattern, detection_type in httponly_false_patterns:
            for match in pattern.finditer(parsed_file.raw_source):
                line_number = (
                    parsed_file.raw_source[: match.start()].count("\n") + 1
                )

                key = ("insecure-session-cookie", line_number)
                if key in seen:
                    continue
                seen.add(key)

                code_sample = self._build_code_sample(
                    parsed_file.source_lines, line_number
                )

                findings.append(
                    Finding(
                        id=id_gen.next_id(),
                        rule_id="insecure-session-cookie",
                        category=OWASPCategory.A07_AUTH_FAILURES,
                        severity=Severity.MEDIUM,
                        title="Session cookie missing 'httpOnly' flag",
                        description=(
                            "A session cookie is configured without the "
                            "'httpOnly' flag (or with httpOnly=False). Without "
                            "this flag, client-side JavaScript can access the "
                            "cookie via document.cookie, making it vulnerable "
                            "to theft via Cross-Site Scripting (XSS) attacks. "
                            "An attacker who exploits an XSS vulnerability can "
                            "extract the session cookie and hijack the session."
                        ),
                        file_path=parsed_file.file_path,
                        line_number=line_number,
                        code_sample=code_sample,
                        remediation=(
                            "Set the httpOnly flag to True on all session cookies. "
                            "For Flask: app.config['SESSION_COOKIE_HTTPONLY'] = True. "
                            "For Django: SESSION_COOKIE_HTTPONLY = True (default). "
                            "For Express: session({cookie: {httpOnly: true}}). "
                            "The httpOnly flag prevents JavaScript from reading "
                            "the cookie, mitigating XSS-based session theft."
                        ),
                        cwe_id="CWE-614",
                        confidence=0.85,
                        metadata={
                            "detection_type": detection_type,
                            "flag": "httpOnly",
                            "language": parsed_file.language,
                        },
                    )
                )

        # --- Detect sameSite=None patterns ---
        samesite_patterns = [
            (_FLASK_SESSION_SAMESITE_PATTERN, "Flask SESSION_COOKIE_SAMESITE=None"),
        ]

        for pattern, detection_type in samesite_patterns:
            for match in pattern.finditer(parsed_file.raw_source):
                line_number = (
                    parsed_file.raw_source[: match.start()].count("\n") + 1
                )

                key = ("insecure-session-cookie", line_number)
                if key in seen:
                    continue
                seen.add(key)

                code_sample = self._build_code_sample(
                    parsed_file.source_lines, line_number
                )

                findings.append(
                    Finding(
                        id=id_gen.next_id(),
                        rule_id="insecure-session-cookie",
                        category=OWASPCategory.A07_AUTH_FAILURES,
                        severity=Severity.MEDIUM,
                        title="Session cookie 'sameSite' set to None",
                        description=(
                            "A session cookie is configured with sameSite=None. "
                            "This disables the SameSite protection, allowing "
                            "the cookie to be sent in cross-origin requests. "
                            "This makes the application vulnerable to "
                            "Cross-Site Request Forgery (CSRF) attacks where "
                            "a malicious site can submit requests to your "
                            "application while the user is authenticated."
                        ),
                        file_path=parsed_file.file_path,
                        line_number=line_number,
                        code_sample=code_sample,
                        remediation=(
                            "Set sameSite to 'Lax' or 'Strict'. "
                            "For Flask: app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'. "
                            "For Django: SESSION_COOKIE_SAMESITE = 'Lax'. "
                            "For Express: session({cookie: {sameSite: 'lax'}}). "
                            "'Lax' is the recommended default as it allows "
                            "top-level navigations while blocking cross-origin "
                            "POST requests."
                        ),
                        cwe_id="CWE-614",
                        confidence=0.80,
                        metadata={
                            "detection_type": detection_type,
                            "flag": "sameSite",
                            "language": parsed_file.language,
                        },
                    )
                )

        # --- Detect Express insecure session patterns ---
        for match in _EXPRESS_SESSION_INSECURE_PATTERN.finditer(
            parsed_file.raw_source
        ):
            line_number = (
                parsed_file.raw_source[: match.start()].count("\n") + 1
            )

            key = ("insecure-session-cookie", line_number)
            if key in seen:
                continue
            seen.add(key)

            code_sample = self._build_code_sample(
                parsed_file.source_lines, line_number
            )

            findings.append(
                Finding(
                    id=id_gen.next_id(),
                    rule_id="insecure-session-cookie",
                    category=OWASPCategory.A07_AUTH_FAILURES,
                    severity=Severity.MEDIUM,
                    title=(
                        "Express session configured with secure: false"
                    ),
                    description=(
                        "An Express session or cookie middleware is configured "
                        "with secure: false. This allows the session cookie to "
                        "be transmitted over unencrypted HTTP connections, "
                        "making it vulnerable to interception."
                    ),
                    file_path=parsed_file.file_path,
                    line_number=line_number,
                    code_sample=code_sample,
                    remediation=(
                        "Set secure: true in the session cookie configuration: "
                        "app.use(session({cookie: {secure: true, httpOnly: true, "
                        "sameSite: 'lax'}}))). Use the 'trust proxy' setting if "
                        "behind a reverse proxy: app.set('trust proxy', 1)."
                    ),
                    cwe_id="CWE-614",
                    confidence=0.85,
                    metadata={
                        "detection_type": "express_session_insecure",
                        "flag": "secure",
                        "language": parsed_file.language,
                    },
                )
            )

        return findings

    # -----------------------------------------------------------------
    # Strategy 4: Missing authentication detection
    # -----------------------------------------------------------------

    def _detect_missing_authentication(
        self,
        parsed_file: ParseResult,
        id_gen: _FindingIDGenerator,
    ) -> List[Finding]:
        """Detect route handlers that lack authentication decorators.

        Uses the ``function_decorators`` field from ParseResult (populated
        by the Python parser's ``extract_all_function_decorators`` method)
        to identify functions that are decorated with route decorators but
        do not also have an authentication decorator.

        For JavaScript/TypeScript files where decorator information is not
        available from parsing, falls back to regex-based detection on raw
        source.

        Only flags functions that are explicitly route handlers (have a
        route decorator), reducing false positives from utility functions.

        Args:
            parsed_file: A single parsed file result containing decorator
                information and raw source.
            id_gen: Sequential ID generator for creating finding IDs.

        Returns:
            List of Finding objects for route handlers missing
            authentication.
        """
        findings: List[Finding] = []

        # Track line numbers to avoid duplicates.
        seen_lines: Set[int] = set()

        # --- Python: use parsed decorator information ---
        if (
            parsed_file.language == "python"
            and parsed_file.function_decorators
        ):
            findings.extend(
                self._detect_missing_auth_python(
                    parsed_file, id_gen, seen_lines
                )
            )

        # --- JavaScript: regex-based route detection ---
        if parsed_file.language == "javascript":
            findings.extend(
                self._detect_missing_auth_javascript(
                    parsed_file, id_gen, seen_lines
                )
            )

        return findings

    def _detect_missing_auth_python(
        self,
        parsed_file: ParseResult,
        id_gen: _FindingIDGenerator,
        seen_lines: Set[int],
    ) -> List[Finding]:
        """Detect Python route handlers missing authentication decorators.

        Iterates over function decorator information from ParseResult and
        flags functions that have a route decorator but no authentication
        decorator.

        Args:
            parsed_file: A parsed Python file with decorator information.
            id_gen: Sequential ID generator.
            seen_lines: Set of line numbers already processed (mutated).

        Returns:
            List of Finding objects for unprotected Python routes.
        """
        findings: List[Finding] = []

        for func_name, line_number, decorators in (
            parsed_file.function_decorators or []
        ):
            if line_number in seen_lines:
                continue

            # Check if this function is a route handler.
            if not self._has_route_decorator(decorators):
                continue

            # Check if this function has an authentication decorator.
            if self._has_auth_decorator(decorators):
                continue

            # Skip common non-sensitive route names that typically do not
            # require authentication (login, register, health check, etc.).
            if self._is_public_route_name(func_name):
                continue

            seen_lines.add(line_number)

            code_sample = self._build_code_sample(
                parsed_file.source_lines, line_number
            )

            findings.append(
                Finding(
                    id=id_gen.next_id(),
                    rule_id="missing-authentication",
                    category=OWASPCategory.A01_ACCESS_CONTROL,
                    severity=Severity.HIGH,
                    title=(
                        f"Route handler '{func_name}' has no "
                        "authentication decorator"
                    ),
                    description=(
                        f"The function '{func_name}' is decorated with a "
                        "route decorator but does not have any authentication "
                        "decorator (e.g., @login_required, @jwt_required). "
                        "This means the endpoint is publicly accessible "
                        "without any authentication check. If this endpoint "
                        "handles sensitive data or operations, an "
                        "unauthenticated attacker can access it directly."
                    ),
                    file_path=parsed_file.file_path,
                    line_number=line_number,
                    code_sample=code_sample,
                    remediation=(
                        "Add an authentication decorator to the route handler. "
                        "For Flask: @login_required (from flask-login). "
                        "For Django: @login_required (from django.contrib.auth.decorators). "
                        "For FastAPI: use Depends(get_current_user) as a "
                        "dependency. If this endpoint is intentionally public "
                        "(e.g., login page, health check), add a suppression "
                        "entry to .security-suppress.json with a reason."
                    ),
                    cwe_id="CWE-306",
                    confidence=0.70,
                    metadata={
                        "function_name": func_name,
                        "decorators": decorators,
                        "language": parsed_file.language,
                    },
                )
            )

        return findings

    def _detect_missing_auth_javascript(
        self,
        parsed_file: ParseResult,
        id_gen: _FindingIDGenerator,
        seen_lines: Set[int],
    ) -> List[Finding]:
        """Detect JavaScript route handlers potentially missing auth middleware.

        Uses regex to find Express-style route definitions and checks if
        they include common authentication middleware patterns in their
        handler chain.

        This detection has lower confidence than the Python decorator-based
        approach because JavaScript middleware is harder to detect without
        AST analysis.

        Args:
            parsed_file: A parsed JavaScript/TypeScript file.
            id_gen: Sequential ID generator.
            seen_lines: Set of line numbers already processed (mutated).

        Returns:
            List of Finding objects for potentially unprotected JS routes.
        """
        findings: List[Finding] = []

        if not parsed_file.raw_source:
            return findings

        # Auth middleware patterns commonly seen in Express route handlers.
        auth_middleware_pattern = re.compile(
            r"""(?:authenticate|isAuthenticated|requireAuth|"""
            r"""verifyToken|checkAuth|passport\.authenticate|"""
            r"""ensureAuthenticated|isLoggedIn|authMiddleware|"""
            r"""requireLogin|jwt|auth)""",
            re.IGNORECASE,
        )

        for match in _JS_ROUTE_PATTERN.finditer(parsed_file.raw_source):
            line_number = (
                parsed_file.raw_source[: match.start()].count("\n") + 1
            )

            if line_number in seen_lines:
                continue

            # Get the full line and a few lines after to check for
            # middleware in the handler chain.
            full_line = self._get_source_line(
                parsed_file.source_lines, line_number
            )

            # Extend context to capture multi-line route definitions.
            context_end = min(
                len(parsed_file.source_lines), line_number + 3
            )
            context_lines = parsed_file.source_lines[
                line_number - 1 : context_end
            ]
            context_text = " ".join(context_lines)

            # Check if any auth middleware is in the route definition.
            if auth_middleware_pattern.search(context_text):
                continue

            # Extract the route path if possible, for public route check.
            route_path_match = re.search(
                r"""['"](/[^'"]*?)['"]""", full_line
            )
            if route_path_match:
                route_path = route_path_match.group(1)
                if self._is_public_route_path(route_path):
                    continue

            seen_lines.add(line_number)

            code_sample = self._build_code_sample(
                parsed_file.source_lines, line_number
            )

            findings.append(
                Finding(
                    id=id_gen.next_id(),
                    rule_id="missing-authentication",
                    category=OWASPCategory.A01_ACCESS_CONTROL,
                    severity=Severity.HIGH,
                    title="Route handler may lack authentication middleware",
                    description=(
                        "An Express-style route handler was detected without "
                        "visible authentication middleware in its handler "
                        "chain. If this endpoint handles sensitive data or "
                        "operations, it may be accessible without "
                        "authentication. Note: authentication may be applied "
                        "globally via app.use() -- verify that this route is "
                        "covered by global middleware."
                    ),
                    file_path=parsed_file.file_path,
                    line_number=line_number,
                    code_sample=code_sample,
                    remediation=(
                        "Add authentication middleware to the route handler: "
                        "router.get('/path', authenticate, handler). "
                        "For Passport.js: router.get('/path', "
                        "passport.authenticate('jwt'), handler). "
                        "Alternatively, apply authentication globally: "
                        "app.use('/api', authenticate). If this endpoint is "
                        "intentionally public, add a suppression entry."
                    ),
                    cwe_id="CWE-306",
                    confidence=0.55,
                    metadata={
                        "detection_type": "regex_based",
                        "language": parsed_file.language,
                    },
                )
            )

        return findings

    # -----------------------------------------------------------------
    # Helper methods
    # -----------------------------------------------------------------

    def _collect_string_entries(
        self, parsed_file: ParseResult
    ) -> List[Tuple[str, int, str]]:
        """Collect all string literals from a parsed file into a uniform list.

        Merges Python StringLiteral and JavaScript JSStringLiteral objects
        into a list of (value, line_number, context) tuples for uniform
        processing.

        Args:
            parsed_file: A single parsed file result.

        Returns:
            List of (value, line_number, context) tuples.
        """
        entries: List[Tuple[str, int, str]] = []

        for sl in parsed_file.string_literals:
            entries.append((sl.value, sl.line_number, sl.context))

        for jsl in parsed_file.js_string_literals:
            entries.append((jsl.value, jsl.line_number, ""))

        return entries

    @staticmethod
    def _build_code_sample(source_lines: List[str], line_number: int) -> str:
        """Build a 3-line code sample centered on the given line number.

        Returns up to 3 lines of source code (the target line plus one
        line above and one below) for inclusion in the finding's
        code_sample field.

        Args:
            source_lines: The source file split into lines.
            line_number: 1-based line number of the finding.

        Returns:
            A string containing the code sample with lines joined by
            newlines. Returns "<source unavailable>" if source lines
            are empty or the line number is out of range.
        """
        if not source_lines or line_number < 1:
            return "<source unavailable>"

        idx = line_number - 1
        start = max(0, idx - 1)
        end = min(len(source_lines), idx + 2)

        if start >= len(source_lines):
            return "<source unavailable>"

        return "\n".join(source_lines[start:end])

    @staticmethod
    def _get_source_line(source_lines: List[str], line_number: int) -> str:
        """Get a single source line by 1-based line number.

        Args:
            source_lines: The source file split into lines.
            line_number: 1-based line number.

        Returns:
            The source line content, or an empty string if out of range.
        """
        idx = line_number - 1
        if 0 <= idx < len(source_lines):
            return source_lines[idx]
        return ""

    @staticmethod
    def _is_comment_line(line: str) -> bool:
        """Check if a source line is a comment.

        Args:
            line: A single source line (possibly with leading whitespace).

        Returns:
            True if the line is a Python or JavaScript comment.
        """
        stripped = line.strip()
        return stripped.startswith("#") or stripped.startswith("//")

    @staticmethod
    def _has_route_decorator(decorators: List[str]) -> bool:
        """Check if a list of decorator names contains a route decorator.

        Args:
            decorators: List of decorator name strings from the parser.

        Returns:
            True if any decorator matches a known route decorator pattern.
        """
        for dec in decorators:
            dec_lower = dec.lower()
            for prefix in _ROUTE_DECORATOR_PREFIXES:
                if dec_lower == prefix or dec_lower.startswith(prefix + "."):
                    return True
                # Also match when the decorator is a method call variant,
                # e.g., "app.route" matches "MyApp.route".
                parts = dec_lower.split(".")
                if len(parts) >= 2:
                    method = ".".join(parts[-2:])
                    if method == prefix or method.startswith(prefix):
                        return True
        return False

    @staticmethod
    def _has_auth_decorator(decorators: List[str]) -> bool:
        """Check if a list of decorator names contains an auth decorator.

        Checks both exact matches against the full decorator name and
        partial matches against individual segments of dotted names.

        Args:
            decorators: List of decorator name strings from the parser.

        Returns:
            True if any decorator matches a known auth decorator pattern.
        """
        for dec in decorators:
            dec_lower = dec.lower()

            # Exact match against full name.
            if dec_lower in _AUTH_DECORATOR_NAMES:
                return True

            # Check individual segments of dotted names.
            # e.g., "flask_login.login_required" -> check "login_required"
            segments = dec_lower.split(".")
            for segment in segments:
                if segment in _AUTH_DECORATOR_SEGMENTS:
                    return True

            # Fuzzy match: check if any auth keyword appears as a
            # substring of the decorator name.
            for auth_name in _AUTH_DECORATOR_SEGMENTS:
                if auth_name in dec_lower:
                    return True

        return False

    @staticmethod
    def _is_public_route_name(func_name: str) -> bool:
        """Check if a function name suggests a publicly accessible route.

        Routes like login, register, health check, and public API endpoints
        are commonly unauthenticated by design.

        Args:
            func_name: The function name of the route handler.

        Returns:
            True if the function name suggests it should be public.
        """
        public_names: Set[str] = {
            "login",
            "logout",
            "register",
            "signup",
            "sign_up",
            "sign_in",
            "signin",
            "health",
            "healthcheck",
            "health_check",
            "ping",
            "ready",
            "readiness",
            "liveness",
            "status",
            "index",
            "home",
            "root",
            "favicon",
            "robots",
            "sitemap",
            "openapi",
            "swagger",
            "docs",
            "redoc",
            "callback",
            "oauth_callback",
            "webhook",
            "webhooks",
            "reset_password",
            "forgot_password",
            "confirm_email",
            "verify_email",
            "public",
        }

        name_lower = func_name.lower()

        # Exact match.
        if name_lower in public_names:
            return True

        # Prefix match for common patterns like get_health, do_login.
        for public in public_names:
            if name_lower.startswith(public) or name_lower.endswith(public):
                return True

        return False

    @staticmethod
    def _is_public_route_path(route_path: str) -> bool:
        """Check if a route path suggests a publicly accessible endpoint.

        Args:
            route_path: The URL path from the route definition.

        Returns:
            True if the path suggests it should be public.
        """
        public_paths: Set[str] = {
            "/",
            "/login",
            "/logout",
            "/register",
            "/signup",
            "/signin",
            "/health",
            "/healthcheck",
            "/health-check",
            "/ping",
            "/ready",
            "/status",
            "/favicon.ico",
            "/robots.txt",
            "/sitemap.xml",
            "/api/docs",
            "/api/swagger",
            "/api/openapi",
            "/api/health",
            "/callback",
            "/oauth/callback",
            "/webhook",
            "/webhooks",
            "/reset-password",
            "/forgot-password",
            "/confirm-email",
            "/verify-email",
            "/public",
        }

        path_lower = route_path.lower().rstrip("/")
        if not path_lower:
            path_lower = "/"

        return path_lower in public_paths
