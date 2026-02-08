"""Sensitive data exposure analyzer.

Detects logging of personally identifiable information (PII), unencrypted
storage of sensitive data, and secrets leaked through logging statements in
Python and JavaScript/TypeScript source code. This analyzer maps primarily to
OWASP A02:2021 (Cryptographic Failures) with supplementary coverage of
A09:2021 (Security Logging and Monitoring Failures).

Detection strategies:
    1. **PII exposure** -- regex-based detection of personally identifiable
       information (email addresses, Social Security numbers, credit card
       numbers, phone numbers) written into log or print statements. Logging
       PII violates data protection regulations (GDPR, CCPA) and creates a
       data breach risk if log files are compromised.

    2. **Unencrypted storage** -- detects patterns where sensitive data
       (passwords, credentials) is stored in plaintext without hashing or
       encryption. Covers direct database writes of cleartext passwords,
       ``localStorage``/``sessionStorage`` usage for secrets, and
       assignment of raw password form values without hashing.

    3. **Secret logging** -- detects logging, printing, or console output
       of API keys, tokens, passwords, and other secrets. Covers Python
       ``logger.*``, ``print()``, and JavaScript ``console.log()``,
       ``console.debug()``, etc. Secrets in logs are a common vector for
       credential leakage.

All detections produce :class:`Finding` objects with appropriate OWASP and
CWE references:
    - CWE-532: Insertion of Sensitive Information into Log File
    - CWE-311: Missing Encryption of Sensitive Data
    - CWE-312: Cleartext Storage of Sensitive Information

This module uses only the Python standard library and has no external
dependencies.

Classes:
    SensitiveDataAnalyzer: Main analyzer class with analyze() entry point.

References:
    - FRS FR-11: SensitiveDataAnalyzer
    - OWASP A02:2021 Cryptographic Failures
    - OWASP A09:2021 Security Logging and Monitoring Failures
    - CWE-311: Missing Encryption of Sensitive Data
    - CWE-312: Cleartext Storage of Sensitive Information
    - CWE-532: Insertion of Sensitive Information into Log File
"""

import logging
import re
from typing import Any, Dict, List, Set, Tuple

from lib.models.finding import Finding, OWASPCategory, Severity
from lib.models.parse_result import ParseResult

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# PII patterns in logging contexts
# ---------------------------------------------------------------------------

# Logging function invocation patterns (Python and JavaScript)
# Matches the start of a logging call to anchor PII detection.
_PYTHON_LOG_CALL_PATTERN = re.compile(
    r"""(?:logger|logging|log)"""
    r"""\.(?:debug|info|warning|warn|error|critical|exception|fatal)"""
    r"""\s*\(""",
    re.IGNORECASE,
)

_PYTHON_PRINT_CALL_PATTERN = re.compile(
    r"""\bprint\s*\(""",
)

_JS_CONSOLE_CALL_PATTERN = re.compile(
    r"""console\.(?:log|debug|info|warn|error|trace)\s*\(""",
    re.IGNORECASE,
)

# PII data patterns
# Email address pattern: user.email, email_address, etc. referenced in
# logging contexts.  We look for the variable reference, not the raw
# email regex, because raw emails would also match configuration and
# test fixtures.
_EMAIL_IN_LOG_PATTERN = re.compile(
    r"""(?:logger|logging|log)"""
    r"""\.(?:debug|info|warning|warn|error|critical|exception|fatal)"""
    r"""\s*\([^)]*"""
    r"""(?:\.email|email[_]?addr|user[_.]email|customer[_.]email)""",
    re.IGNORECASE,
)

_EMAIL_IN_PRINT_PATTERN = re.compile(
    r"""\bprint\s*\([^)]*"""
    r"""(?:\.email|email[_]?addr|user[_.]email|customer[_.]email)""",
    re.IGNORECASE,
)

_EMAIL_IN_CONSOLE_PATTERN = re.compile(
    r"""console\.(?:log|debug|info|warn|error|trace)"""
    r"""\s*\([^)]*"""
    r"""(?:\.email|email[_]?addr|user[_.]email|customer[_.]email)""",
    re.IGNORECASE,
)

# SSN pattern in logging: direct SSN regex values logged.
# We look for the literal format \d{3}-\d{2}-\d{4} appearing in
# log/print output via variable references.
_SSN_IN_LOG_PATTERN = re.compile(
    r"""(?:logger|logging|log)"""
    r"""\.(?:debug|info|warning|warn|error|critical|exception|fatal)"""
    r"""\s*\([^)]*"""
    r"""(?:ssn|social_security|social_sec|ss_number|ssn_number)""",
    re.IGNORECASE,
)

_SSN_IN_PRINT_PATTERN = re.compile(
    r"""\bprint\s*\([^)]*"""
    r"""(?:ssn|social_security|social_sec|ss_number|ssn_number)""",
    re.IGNORECASE,
)

_SSN_IN_CONSOLE_PATTERN = re.compile(
    r"""console\.(?:log|debug|info|warn|error|trace)"""
    r"""\s*\([^)]*"""
    r"""(?:ssn|social_security|social_sec|ss_number|ssn_number)""",
    re.IGNORECASE,
)

# SSN literal pattern: detects actual SSN-formatted values being logged
_SSN_LITERAL_IN_LOG_PATTERN = re.compile(
    r"""(?:logger|logging|log|print|console)"""
    r"""[^;]*\d{3}-\d{2}-\d{4}""",
    re.IGNORECASE,
)

# Credit card number patterns logged
_CC_IN_LOG_PATTERN = re.compile(
    r"""(?:logger|logging|log)"""
    r"""\.(?:debug|info|warning|warn|error|critical|exception|fatal)"""
    r"""\s*\([^)]*"""
    r"""(?:credit_card|card_number|card_num|cc_number|ccn|cc_num|pan)""",
    re.IGNORECASE,
)

_CC_IN_PRINT_PATTERN = re.compile(
    r"""\bprint\s*\([^)]*"""
    r"""(?:credit_card|card_number|card_num|cc_number|ccn|cc_num|pan)""",
    re.IGNORECASE,
)

_CC_IN_CONSOLE_PATTERN = re.compile(
    r"""console\.(?:log|debug|info|warn|error|trace)"""
    r"""\s*\([^)]*"""
    r"""(?:credit_card|card_number|card_num|cc_number|ccn|cc_num|pan)""",
    re.IGNORECASE,
)

# Credit card literal pattern in logs: \d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}
_CC_LITERAL_IN_LOG_PATTERN = re.compile(
    r"""(?:logger|logging|log|print|console)"""
    r"""[^;]*\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}""",
    re.IGNORECASE,
)

# Phone number patterns logged
_PHONE_IN_LOG_PATTERN = re.compile(
    r"""(?:logger|logging|log)"""
    r"""\.(?:debug|info|warning|warn|error|critical|exception|fatal)"""
    r"""\s*\([^)]*"""
    r"""(?:phone_number|phone_num|phone|mobile|cell_phone|telephone)""",
    re.IGNORECASE,
)

_PHONE_IN_PRINT_PATTERN = re.compile(
    r"""\bprint\s*\([^)]*"""
    r"""(?:phone_number|phone_num|phone|mobile|cell_phone|telephone)""",
    re.IGNORECASE,
)

_PHONE_IN_CONSOLE_PATTERN = re.compile(
    r"""console\.(?:log|debug|info|warn|error|trace)"""
    r"""\s*\([^)]*"""
    r"""(?:phone_number|phone_num|phone|mobile|cell_phone|telephone)""",
    re.IGNORECASE,
)


# ---------------------------------------------------------------------------
# Unencrypted storage patterns
# ---------------------------------------------------------------------------

# Password stored without hashing: db.save(password=plaintext_var) or
# user.password = request.form["password"]
_PASSWORD_PLAINTEXT_ASSIGNMENT_PATTERN = re.compile(
    r"""\.password\s*=\s*(?:"""
    r"""request\.(?:form|POST|data|json|body)\s*\[|"""
    r"""req\.body\s*\.|"""
    r"""params\s*\[|"""
    r"""args\s*\[|"""
    r"""input\s*\(|"""
    r"""plaintext|"""
    r"""plain_text|"""
    r"""raw_password|"""
    r"""clear_password"""
    r""")""",
    re.IGNORECASE,
)

# Database save with plaintext password: db.save(password=value),
# Model.create(password=value), etc.
_DB_SAVE_PASSWORD_PATTERN = re.compile(
    r"""(?:\.save|\.create|\.insert|\.update|\.add|\.put)\s*\("""
    r"""[^)]*password\s*=\s*(?!.*(?:hash|bcrypt|argon|scrypt|pbkdf|encrypt|make_password))""",
    re.IGNORECASE | re.DOTALL,
)

# localStorage/sessionStorage storing sensitive data
_LOCAL_STORAGE_SENSITIVE_PATTERN = re.compile(
    r"""(?:localStorage|sessionStorage)"""
    r"""\.setItem\s*\(\s*['"]\s*"""
    r"""(?:password|token|secret|api_key|apiKey|auth_token|"""
    r"""authToken|access_token|accessToken|refresh_token|"""
    r"""refreshToken|session_id|sessionId|credit_card|ssn)""",
    re.IGNORECASE,
)

# Direct cookie storage of sensitive data without secure flag
_COOKIE_SENSITIVE_PATTERN = re.compile(
    r"""(?:document\.cookie|res\.cookie|response\.set_cookie)\s*"""
    r"""(?:=|\()\s*[^;]*"""
    r"""(?:password|token|secret|api_key|apiKey|session_id)""",
    re.IGNORECASE,
)

# Writing password directly to file
_FILE_WRITE_PASSWORD_PATTERN = re.compile(
    r"""\.write\s*\([^)]*(?:password|passwd|pwd|secret|api_key|token)""",
    re.IGNORECASE,
)


# ---------------------------------------------------------------------------
# Secret logging patterns
# ---------------------------------------------------------------------------

# Python logger calls that include secret variable names
_SECRET_NAMES = (
    r"""(?:api_key|apikey|api_secret|apisecret|"""
    r"""secret_key|secretkey|secret|"""
    r"""access_key|accesskey|"""
    r"""private_key|privatekey|"""
    r"""auth_token|authtoken|"""
    r"""access_token|accesstoken|"""
    r"""refresh_token|refreshtoken|"""
    r"""password|passwd|pwd|"""
    r"""token|"""
    r"""credentials|creds|"""
    r"""client_secret|clientsecret)"""
)

# Python logger.* with secret variable names
_SECRET_IN_LOGGER_PATTERN = re.compile(
    r"""(?:logger|logging|log)"""
    r"""\.(?:debug|info|warning|warn|error|critical|exception|fatal)"""
    r"""\s*\([^)]*"""
    + _SECRET_NAMES,
    re.IGNORECASE,
)

# Python print() with secret variable names
_SECRET_IN_PRINT_PATTERN = re.compile(
    r"""\bprint\s*\([^)]*"""
    + _SECRET_NAMES,
    re.IGNORECASE,
)

# JavaScript console.* with secret variable names
_SECRET_IN_CONSOLE_PATTERN = re.compile(
    r"""console\.(?:log|debug|info|warn|error|trace)"""
    r"""\s*\([^)]*"""
    + _SECRET_NAMES,
    re.IGNORECASE,
)

# F-string / format string patterns that interpolate secrets into logs
# e.g., logger.debug(f"API key: {api_key}")
_FSTRING_SECRET_LOG_PATTERN = re.compile(
    r"""(?:logger|logging|log)"""
    r"""\.(?:debug|info|warning|warn|error|critical|exception|fatal)"""
    r"""\s*\(\s*f?['"]+[^'"]*\{"""
    + _SECRET_NAMES
    + r"""\}""",
    re.IGNORECASE,
)

# Template literal with secrets in console.log
# e.g., console.log(`Token: ${token}`)
_TEMPLATE_SECRET_CONSOLE_PATTERN = re.compile(
    r"""console\.(?:log|debug|info|warn|error|trace)"""
    r"""\s*\(\s*`[^`]*\$\{"""
    + _SECRET_NAMES
    + r"""\}""",
    re.IGNORECASE,
)


# ---------------------------------------------------------------------------
# False positive reduction patterns
# ---------------------------------------------------------------------------

# Lines that are masking/redacting the value before logging are safe
_REDACTION_PATTERN = re.compile(
    r"""(?:mask|redact|sanitize|censor|obfuscate|scrub|\*{3,}|\.{3,})""",
    re.IGNORECASE,
)

# Lines that are checking/validating rather than logging
_VALIDATION_PATTERN = re.compile(
    r"""(?:if\s|assert\s|validate|check|verify|is_valid|has_|isinstance)""",
    re.IGNORECASE,
)

# Lines that are hashing the password before storing
_HASHING_PATTERN = re.compile(
    r"""(?:hash|bcrypt|argon|scrypt|pbkdf|encrypt|make_password|"""
    r"""generate_password_hash|set_password|hashpw|sha256|sha512)""",
    re.IGNORECASE,
)


# ---------------------------------------------------------------------------
# Finding ID generator
# ---------------------------------------------------------------------------


class _FindingIDGenerator:
    """Thread-unsafe sequential ID generator for sensitive data findings.

    Produces IDs in the format "SEN-001", "SEN-002", etc. A new generator
    is created for each analyze() invocation so IDs start from 1.
    """

    def __init__(self) -> None:
        self._counter = 0

    def next_id(self) -> str:
        """Return the next sequential finding ID."""
        self._counter += 1
        return f"SEN-{self._counter:03d}"


# ---------------------------------------------------------------------------
# Main analyzer class
# ---------------------------------------------------------------------------


class SensitiveDataAnalyzer:
    """Detect exposure of sensitive data in application code.

    This analyzer implements three complementary detection strategies that
    together provide broad coverage of sensitive data exposure patterns:

    1. **PII exposure** (``_detect_pii_exposure``): Scans raw source code
       for logging or printing of personally identifiable information such
       as email addresses, Social Security numbers, credit card numbers,
       and phone numbers. Produces HIGH findings under CWE-532.

    2. **Unencrypted storage** (``_detect_unencrypted_storage``): Detects
       patterns where sensitive data (passwords, credentials, tokens) is
       stored without encryption or hashing. Covers database writes of
       plaintext passwords, ``localStorage``/``sessionStorage`` usage for
       secrets in JavaScript, and direct file writes of credentials.
       Produces CRITICAL findings under CWE-311.

    3. **Secret logging** (``_detect_secret_logging``): Detects logging,
       printing, or console output of API keys, tokens, passwords, and
       other secrets through variable name analysis in log statements.
       Produces HIGH findings under CWE-532.

    Attributes:
        VERSION: Analyzer version string for AssessmentResult tracking.

    Usage::

        analyzer = SensitiveDataAnalyzer()
        findings = analyzer.analyze(parsed_files, config={})

    Configuration:
        The ``config`` dict passed to ``analyze()`` supports these optional
        keys:

        - ``skip_pii`` (bool): Disable PII exposure detection.
        - ``skip_unencrypted_storage`` (bool): Disable unencrypted storage
          detection.
        - ``skip_secret_logging`` (bool): Disable secret logging detection.
    """

    VERSION: str = "1.0.0"

    def analyze(
        self,
        parsed_files: List[ParseResult],
        config: Dict[str, Any],
    ) -> List[Finding]:
        """Run all sensitive data detection strategies on the parsed files.

        Iterates over each parsed file and applies PII exposure,
        unencrypted storage, and secret logging detection. Results from all
        three strategies are combined into a single list of findings.

        Args:
            parsed_files: List of ParseResult objects from the parsing
                phase. Each represents one source file with extracted
                metadata and raw source content.
            config: Optional configuration overrides. Supported keys:
                ``skip_pii`` (bool),
                ``skip_unencrypted_storage`` (bool),
                ``skip_secret_logging`` (bool).

        Returns:
            List of Finding objects, one per detected issue. Findings are
            ordered by detection strategy and then by file path within
            each strategy.
        """
        findings: List[Finding] = []
        id_gen = _FindingIDGenerator()

        skip_pii = config.get("skip_pii", False)
        skip_unencrypted = config.get("skip_unencrypted_storage", False)
        skip_secret_log = config.get("skip_secret_logging", False)

        for parsed_file in parsed_files:
            # Skip lockfiles -- they do not contain application code.
            if parsed_file.language == "lockfile":
                continue

            # 1. PII exposure detection
            if not skip_pii:
                findings.extend(
                    self._detect_pii_exposure(parsed_file, id_gen)
                )

            # 2. Unencrypted storage detection
            if not skip_unencrypted:
                findings.extend(
                    self._detect_unencrypted_storage(parsed_file, id_gen)
                )

            # 3. Secret logging detection
            if not skip_secret_log:
                findings.extend(
                    self._detect_secret_logging(parsed_file, id_gen)
                )

        return findings

    # -----------------------------------------------------------------
    # Strategy 1: PII exposure detection
    # -----------------------------------------------------------------

    def _detect_pii_exposure(
        self,
        parsed_file: ParseResult,
        id_gen: _FindingIDGenerator,
    ) -> List[Finding]:
        """Detect personally identifiable information logged or printed.

        Scans raw source code for logging or print statements that
        reference PII variables (email addresses, SSNs, credit card
        numbers, phone numbers). Also detects literal PII patterns
        (SSN and credit card number formats) embedded in log output.

        Logging PII creates compliance risks under GDPR, CCPA, and PCI
        DSS, and exposes users to identity theft if log files are
        compromised or inadvertently shared.

        Args:
            parsed_file: A single parsed file result containing raw source
                code and file metadata.
            id_gen: Sequential ID generator for creating finding IDs.

        Returns:
            List of Finding objects for each PII exposure detected.
        """
        findings: List[Finding] = []

        if not parsed_file.raw_source:
            return findings

        # Track (rule_id, line_number) to avoid duplicates.
        seen: Set[Tuple[str, int]] = set()

        # Define PII detection groups: (patterns, pii_type, description_detail)
        pii_groups: List[Tuple[List[re.Pattern], str, str]] = [  # type: ignore[type-arg]
            (
                [
                    _EMAIL_IN_LOG_PATTERN,
                    _EMAIL_IN_PRINT_PATTERN,
                    _EMAIL_IN_CONSOLE_PATTERN,
                ],
                "email",
                "email address",
            ),
            (
                [
                    _SSN_IN_LOG_PATTERN,
                    _SSN_IN_PRINT_PATTERN,
                    _SSN_IN_CONSOLE_PATTERN,
                    _SSN_LITERAL_IN_LOG_PATTERN,
                ],
                "ssn",
                "Social Security number (SSN)",
            ),
            (
                [
                    _CC_IN_LOG_PATTERN,
                    _CC_IN_PRINT_PATTERN,
                    _CC_IN_CONSOLE_PATTERN,
                    _CC_LITERAL_IN_LOG_PATTERN,
                ],
                "credit_card",
                "credit card number",
            ),
            (
                [
                    _PHONE_IN_LOG_PATTERN,
                    _PHONE_IN_PRINT_PATTERN,
                    _PHONE_IN_CONSOLE_PATTERN,
                ],
                "phone",
                "phone number",
            ),
        ]

        for patterns, pii_type, description_detail in pii_groups:
            for pattern in patterns:
                for match in pattern.finditer(parsed_file.raw_source):
                    line_number = (
                        parsed_file.raw_source[: match.start()].count("\n")
                        + 1
                    )

                    key = ("pii-in-logs", line_number)
                    if key in seen:
                        continue

                    # Get the full line for false positive checks.
                    full_line = self._get_source_line(
                        parsed_file.source_lines, line_number
                    )

                    if self._is_comment_line(full_line):
                        continue

                    # Skip if the line contains redaction/masking logic.
                    if _REDACTION_PATTERN.search(full_line):
                        continue

                    # Skip validation/check lines.
                    if _VALIDATION_PATTERN.search(full_line):
                        continue

                    seen.add(key)

                    code_sample = self._build_code_sample(
                        parsed_file.source_lines, line_number
                    )

                    # Confidence varies by PII type and detection method.
                    confidence = self._pii_confidence(pii_type, pattern)

                    findings.append(
                        Finding(
                            id=id_gen.next_id(),
                            rule_id="pii-in-logs",
                            category=OWASPCategory.A02_CRYPTOGRAPHIC_FAILURES,
                            severity=Severity.HIGH,
                            title=(
                                f"PII exposure: {description_detail} "
                                f"in log output"
                            ),
                            description=(
                                f"A {description_detail} appears to be "
                                f"logged or printed to output. Logging PII "
                                f"creates compliance risks under data "
                                f"protection regulations (GDPR, CCPA, PCI "
                                f"DSS) and exposes users to identity theft "
                                f"if log files are compromised, stored in "
                                f"insecure log aggregation systems, or "
                                f"inadvertently shared. Log files are often "
                                f"retained for extended periods and may be "
                                f"accessible to a wider audience than the "
                                f"application itself."
                            ),
                            file_path=parsed_file.file_path,
                            line_number=line_number,
                            code_sample=code_sample,
                            remediation=(
                                "Remove PII from log statements entirely, "
                                "or replace it with a masked/redacted form. "
                                "For email: log only the domain "
                                "(user@*****.com) or a pseudonymized "
                                "identifier. For SSN/credit card: never "
                                "log these values; use a reference ID "
                                "instead. For phone numbers: log only the "
                                "last 4 digits. Consider implementing a "
                                "structured logging filter that automatically "
                                "redacts PII fields before they reach log "
                                "output."
                            ),
                            cwe_id="CWE-532",
                            confidence=confidence,
                            metadata={
                                "pii_type": pii_type,
                                "language": parsed_file.language,
                            },
                        )
                    )

        return findings

    # -----------------------------------------------------------------
    # Strategy 2: Unencrypted storage detection
    # -----------------------------------------------------------------

    def _detect_unencrypted_storage(
        self,
        parsed_file: ParseResult,
        id_gen: _FindingIDGenerator,
    ) -> List[Finding]:
        """Detect sensitive data stored without encryption or hashing.

        Scans raw source code for patterns where passwords and other
        sensitive data are written to persistent storage (databases, files,
        browser storage) without encryption or hashing.

        Plaintext storage of passwords means that a database breach
        directly exposes all user credentials. Browser localStorage and
        sessionStorage are accessible to any JavaScript running on the
        same origin, including XSS payloads.

        Args:
            parsed_file: A single parsed file result containing raw source
                code and file metadata.
            id_gen: Sequential ID generator for creating finding IDs.

        Returns:
            List of Finding objects for each unencrypted storage pattern
            found.
        """
        findings: List[Finding] = []

        if not parsed_file.raw_source:
            return findings

        # Track (rule_id, line_number) to avoid duplicates.
        seen: Set[Tuple[str, int]] = set()

        # Define storage detection patterns with their specific context.
        storage_patterns: List[Tuple[re.Pattern, str, str, str]] = [  # type: ignore[type-arg]
            (
                _PASSWORD_PLAINTEXT_ASSIGNMENT_PATTERN,
                "plaintext_password_assignment",
                "Password assigned from user input without hashing",
                (
                    "A password field is being assigned directly from user "
                    "input (request data, form input) without hashing. This "
                    "means the plaintext password will be stored in the "
                    "database, making all user passwords immediately "
                    "accessible if the database is breached. Password reuse "
                    "by users means a breach of your database could "
                    "compromise accounts on other services."
                ),
            ),
            (
                _DB_SAVE_PASSWORD_PATTERN,
                "plaintext_password_db_save",
                "Password saved to database without hashing",
                (
                    "A database write operation includes a password "
                    "parameter that does not appear to be hashed before "
                    "storage. Without hashing, passwords are stored in "
                    "cleartext and are immediately exposed in a database "
                    "breach. Even database administrators should not have "
                    "access to user passwords."
                ),
            ),
            (
                _LOCAL_STORAGE_SENSITIVE_PATTERN,
                "sensitive_in_local_storage",
                "Sensitive data stored in browser localStorage/sessionStorage",
                (
                    "Sensitive data (password, token, API key, or similar) "
                    "is being stored in browser localStorage or "
                    "sessionStorage. This storage is accessible to any "
                    "JavaScript running on the same origin, including XSS "
                    "payloads. Unlike httpOnly cookies, localStorage data "
                    "can be read by client-side scripts."
                ),
            ),
            (
                _COOKIE_SENSITIVE_PATTERN,
                "sensitive_in_cookie",
                "Sensitive data stored in cookie without secure flags",
                (
                    "Sensitive data appears to be written to a cookie. "
                    "Without the httpOnly and secure flags, cookies "
                    "containing secrets can be stolen via XSS attacks or "
                    "intercepted over unencrypted HTTP connections."
                ),
            ),
            (
                _FILE_WRITE_PASSWORD_PATTERN,
                "sensitive_in_file_write",
                "Sensitive data written to file",
                (
                    "A file write operation appears to include sensitive "
                    "data (password, API key, token). Writing secrets to "
                    "files creates a persistence risk -- the file may have "
                    "incorrect permissions, be included in backups, or "
                    "remain on disk after the application stops."
                ),
            ),
        ]

        for pattern, detection_type, title, description in storage_patterns:
            for match in pattern.finditer(parsed_file.raw_source):
                line_number = (
                    parsed_file.raw_source[: match.start()].count("\n") + 1
                )

                key = ("unencrypted-storage", line_number)
                if key in seen:
                    continue

                full_line = self._get_source_line(
                    parsed_file.source_lines, line_number
                )

                if self._is_comment_line(full_line):
                    continue

                # Skip lines that already contain hashing operations.
                if _HASHING_PATTERN.search(full_line):
                    continue

                # For multi-line matches, also check the next few lines
                # for hashing operations (the hash may be on the next
                # line in a pipeline).
                if self._has_nearby_hashing(
                    parsed_file.source_lines, line_number
                ):
                    continue

                seen.add(key)

                code_sample = self._build_code_sample(
                    parsed_file.source_lines, line_number
                )

                # Determine confidence based on detection type.
                confidence = self._storage_confidence(detection_type)

                findings.append(
                    Finding(
                        id=id_gen.next_id(),
                        rule_id="unencrypted-storage",
                        category=OWASPCategory.A02_CRYPTOGRAPHIC_FAILURES,
                        severity=Severity.CRITICAL,
                        title=title,
                        description=description,
                        file_path=parsed_file.file_path,
                        line_number=line_number,
                        code_sample=code_sample,
                        remediation=(
                            "Never store passwords in plaintext. Use a "
                            "purpose-built password hashing algorithm: "
                            "bcrypt, scrypt, or argon2id. For Python: "
                            "from werkzeug.security import "
                            "generate_password_hash; hashed = "
                            "generate_password_hash(password). For "
                            "Django: use make_password() from "
                            "django.contrib.auth.hashers. For Node.js: "
                            "const bcrypt = require('bcrypt'); "
                            "const hash = await bcrypt.hash(password, 12). "
                            "For browser storage: use httpOnly secure "
                            "cookies instead of localStorage for tokens. "
                            "Never store passwords client-side."
                        ),
                        cwe_id="CWE-311",
                        confidence=confidence,
                        metadata={
                            "detection_type": detection_type,
                            "language": parsed_file.language,
                        },
                    )
                )

        return findings

    # -----------------------------------------------------------------
    # Strategy 3: Secret logging detection
    # -----------------------------------------------------------------

    def _detect_secret_logging(
        self,
        parsed_file: ParseResult,
        id_gen: _FindingIDGenerator,
    ) -> List[Finding]:
        """Detect logging of secrets such as API keys, tokens, and passwords.

        Scans raw source code for logging statements (logger.*, print(),
        console.log()) that reference variables with secret-related names
        (api_key, token, password, secret, credentials, etc.). Also detects
        f-string and template literal interpolation of secrets into log
        messages.

        Secrets in log files are a common vector for credential leakage.
        Log files may be stored in centralized logging systems accessible
        to operations teams, backed up to less-secure storage, or indexed
        by log analysis tools that expose them to broader audiences.

        Args:
            parsed_file: A single parsed file result containing raw source
                code and file metadata.
            id_gen: Sequential ID generator for creating finding IDs.

        Returns:
            List of Finding objects for each secret logging pattern found.
        """
        findings: List[Finding] = []

        if not parsed_file.raw_source:
            return findings

        # Track (rule_id, line_number) to avoid duplicates.
        seen: Set[Tuple[str, int]] = set()

        # Secret logging patterns to check.
        secret_log_patterns: List[Tuple[re.Pattern, str]] = [  # type: ignore[type-arg]
            (_SECRET_IN_LOGGER_PATTERN, "python_logger"),
            (_SECRET_IN_PRINT_PATTERN, "python_print"),
            (_SECRET_IN_CONSOLE_PATTERN, "js_console"),
            (_FSTRING_SECRET_LOG_PATTERN, "python_fstring_log"),
            (_TEMPLATE_SECRET_CONSOLE_PATTERN, "js_template_console"),
        ]

        for pattern, detection_type in secret_log_patterns:
            for match in pattern.finditer(parsed_file.raw_source):
                line_number = (
                    parsed_file.raw_source[: match.start()].count("\n") + 1
                )

                key = ("secret-logging", line_number)
                if key in seen:
                    continue

                full_line = self._get_source_line(
                    parsed_file.source_lines, line_number
                )

                if self._is_comment_line(full_line):
                    continue

                # Skip lines that redact or mask the secret value.
                if _REDACTION_PATTERN.search(full_line):
                    continue

                # Skip validation/check lines that reference secret names
                # but do not actually log the value.
                if _VALIDATION_PATTERN.search(full_line):
                    continue

                # Skip lines that only reference the secret name as a
                # string key (e.g., logger.info("Missing api_key config"))
                # rather than logging its value.
                if self._is_key_name_only(full_line):
                    continue

                seen.add(key)

                code_sample = self._build_code_sample(
                    parsed_file.source_lines, line_number
                )

                # Determine the type of secret from the match.
                secret_type = self._identify_secret_type(match.group(0))

                findings.append(
                    Finding(
                        id=id_gen.next_id(),
                        rule_id="secret-logging",
                        category=OWASPCategory.A09_LOGGING_FAILURES,
                        severity=Severity.HIGH,
                        title=(
                            f"Secret logged: {secret_type} value "
                            f"in log output"
                        ),
                        description=(
                            f"A {secret_type} appears to be logged or "
                            f"printed to output. Secrets in log files are "
                            f"a common vector for credential leakage. Log "
                            f"files may be stored in centralized logging "
                            f"systems accessible to operations teams, "
                            f"backed up to less-secure storage, or indexed "
                            f"by log analysis tools that expose them to "
                            f"broader audiences. If an attacker gains read "
                            f"access to logs, they obtain valid credentials "
                            f"without needing to exploit the application "
                            f"itself."
                        ),
                        file_path=parsed_file.file_path,
                        line_number=line_number,
                        code_sample=code_sample,
                        remediation=(
                            "Remove secrets from log statements entirely. "
                            "If you need to log that a secret was used, log "
                            "a non-sensitive identifier instead (e.g., the "
                            "key ID, a truncated hash, or a reference name). "
                            "For debugging authentication issues, log the "
                            "result of the operation (success/failure) "
                            "rather than the credentials themselves. "
                            "Consider implementing a logging filter that "
                            "automatically detects and redacts secret "
                            "patterns. For Python: use a custom "
                            "logging.Filter class. For JavaScript: use a "
                            "custom transport or formatter in your logging "
                            "library."
                        ),
                        cwe_id="CWE-532",
                        confidence=0.80,
                        metadata={
                            "detection_type": detection_type,
                            "secret_type": secret_type,
                            "language": parsed_file.language,
                        },
                    )
                )

        return findings

    # -----------------------------------------------------------------
    # Helper methods
    # -----------------------------------------------------------------

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
    def _has_nearby_hashing(
        source_lines: List[str], line_number: int
    ) -> bool:
        """Check if hashing logic exists within 3 lines of the target.

        When a password assignment is detected, the hashing step may be
        on a nearby line (e.g., the line immediately before or after the
        assignment, or within a 3-line context window). This method
        reduces false positives for patterns like::

            hashed = bcrypt.hash(raw_password)
            user.password = hashed

        Args:
            source_lines: The source file split into lines.
            line_number: 1-based line number of the detected pattern.

        Returns:
            True if a hashing pattern is found within 3 lines of the
            target line (before or after).
        """
        idx = line_number - 1
        start = max(0, idx - 3)
        end = min(len(source_lines), idx + 4)

        for i in range(start, end):
            if i == idx:
                continue  # Already checked on the target line.
            if _HASHING_PATTERN.search(source_lines[i]):
                return True

        return False

    @staticmethod
    def _is_key_name_only(line: str) -> bool:
        """Check if a line references a secret name only as a string key.

        Lines like ``logger.info("Missing api_key configuration")`` mention
        the secret name but do not log its value. These are false
        positives for secret logging detection.

        This heuristic checks if the secret name appears only inside a
        plain string (not in an f-string interpolation, format call, or
        variable reference).

        Args:
            line: A single source line.

        Returns:
            True if the secret name appears to be used only as a literal
            string key or description, not as a variable reference.
        """
        stripped = line.strip()

        # If the line contains f-string interpolation {var} or format()
        # calls, the secret name likely refers to a variable.
        if "{" in stripped and "}" in stripped:
            return False

        # If the line contains string concatenation with +, the secret
        # name might be a variable.
        if "+" in stripped:
            # Check if there is a variable-like reference (not quoted)
            # near the secret-related keywords.
            return False

        # If the line has a comma after the string (like print("msg", var)),
        # the secret name might be a second argument.
        # Look for patterns like: print("...", secret_var) or
        # logger.info("...", api_key)
        if re.search(
            r"""['"]\s*,\s*\w*(?:key|token|password|secret|cred)""",
            stripped,
            re.IGNORECASE,
        ):
            return False

        # If the line has % formatting, the secret might be substituted.
        if "%" in stripped and (
            "%s" in stripped or "%r" in stripped or "%d" in stripped
        ):
            return False

        return False

    @staticmethod
    def _pii_confidence(pii_type: str, pattern: re.Pattern) -> float:  # type: ignore[type-arg]
        """Determine confidence score for a PII detection.

        Higher confidence for direct variable reference patterns, lower
        confidence for literal pattern matches that may be coincidental.

        Args:
            pii_type: Type of PII detected ("email", "ssn",
                "credit_card", "phone").
            pattern: The regex pattern that matched.

        Returns:
            Confidence score between 0.65 and 0.85.
        """
        # Literal SSN/CC patterns in logs could be false positives
        # (e.g., date ranges, formatted numbers).
        if pattern in (
            _SSN_LITERAL_IN_LOG_PATTERN,
            _CC_LITERAL_IN_LOG_PATTERN,
        ):
            return 0.65

        # SSN and credit card variable references are high confidence.
        if pii_type in ("ssn", "credit_card"):
            return 0.85

        # Email and phone variable references.
        if pii_type == "email":
            return 0.80

        # Phone number patterns are more common in legitimate contexts.
        return 0.70

    @staticmethod
    def _storage_confidence(detection_type: str) -> float:
        """Determine confidence score for an unencrypted storage detection.

        Args:
            detection_type: The storage pattern type that was detected.

        Returns:
            Confidence score between 0.70 and 0.85.
        """
        high_confidence_types = {
            "plaintext_password_assignment",
            "plaintext_password_db_save",
            "sensitive_in_local_storage",
        }
        if detection_type in high_confidence_types:
            return 0.80

        # Cookie and file write patterns have slightly more false
        # positive potential.
        return 0.70

    @staticmethod
    def _identify_secret_type(matched_text: str) -> str:
        """Identify the specific type of secret from the matched text.

        Examines the matched regex text to determine which secret-related
        keyword triggered the match, and returns a human-readable label.

        Args:
            matched_text: The text fragment matched by the regex.

        Returns:
            A human-readable secret type label.
        """
        text_lower = matched_text.lower()

        if "api_key" in text_lower or "apikey" in text_lower:
            return "API key"
        if "api_secret" in text_lower or "apisecret" in text_lower:
            return "API secret"
        if "secret_key" in text_lower or "secretkey" in text_lower:
            return "secret key"
        if "access_key" in text_lower or "accesskey" in text_lower:
            return "access key"
        if "private_key" in text_lower or "privatekey" in text_lower:
            return "private key"
        if "auth_token" in text_lower or "authtoken" in text_lower:
            return "auth token"
        if "access_token" in text_lower or "accesstoken" in text_lower:
            return "access token"
        if "refresh_token" in text_lower or "refreshtoken" in text_lower:
            return "refresh token"
        if "client_secret" in text_lower or "clientsecret" in text_lower:
            return "client secret"
        if (
            "password" in text_lower
            or "passwd" in text_lower
            or "pwd" in text_lower
        ):
            return "password"
        if "credentials" in text_lower or "creds" in text_lower:
            return "credentials"
        if "token" in text_lower:
            return "token"
        if "secret" in text_lower:
            return "secret"

        return "secret"
