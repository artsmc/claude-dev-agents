"""Security misconfiguration analyzer.

Detects CORS misconfigurations, debug mode left enabled, missing security
headers, and verbose error disclosure in Python and JavaScript/TypeScript
source code. This analyzer maps to OWASP A05:2021 (Security
Misconfiguration).

Detection strategies:
    1. **CORS misconfiguration** -- regex-based detection of wildcard CORS
       origins (``Access-Control-Allow-Origin: *``), permissive CORS
       middleware configuration in Flask/Django (``flask_cors.CORS`` with
       ``origins=["*"]``), and Express ``res.header`` calls setting a
       wildcard origin. Wildcard origins combined with credentials are
       especially dangerous.

    2. **Debug mode enabled** -- detects ``DEBUG = True`` in Django
       settings, ``app.debug = True`` and ``app.run(debug=True)`` in Flask,
       and ``NODE_ENV`` set to ``'development'`` in production-like
       configuration files. Debug mode in production exposes stack traces,
       internal paths, and environment variables to attackers.

    3. **Missing security headers** -- scans response-header-setting code
       for the absence of four critical HTTP security headers:
       ``X-Frame-Options``, ``X-Content-Type-Options``,
       ``Strict-Transport-Security``, and ``Content-Security-Policy``. Only
       flags files that already set some response headers (indicating they
       are responsible for HTTP configuration) but omit key security ones.

    4. **Verbose error disclosure** -- detects configurations that expose
       stack traces or detailed error messages to clients, including
       ``PROPAGATE_EXCEPTIONS = True``, debug-mode stack trace exposure,
       and Express error handler middleware that may leak implementation
       details.

All detections produce :class:`Finding` objects categorized under
:attr:`OWASPCategory.A05_SECURITY_MISCONFIGURATION` with appropriate CWE
references:
    - CWE-942: Overly Permissive Cross-domain Whitelist (CORS)
    - CWE-489: Active Debug Code (debug mode)
    - CWE-16: Configuration (missing security headers)
    - CWE-209: Generation of Error Message Containing Sensitive Information

This module uses only the Python standard library and has no external
dependencies.

Classes:
    ConfigAnalyzer: Main analyzer class with analyze() entry point.

References:
    - FRS FR-10: ConfigAnalyzer
    - OWASP A05:2021 Security Misconfiguration
    - CWE-16: Configuration
    - CWE-209: Generation of Error Message Containing Sensitive Information
    - CWE-489: Active Debug Code
    - CWE-942: Overly Permissive Cross-domain Whitelist
"""

import logging
import re
from typing import Any, Dict, List, Set, Tuple

from lib.models.finding import Finding, OWASPCategory, Severity
from lib.models.parse_result import ParseResult

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# CORS misconfiguration patterns
# ---------------------------------------------------------------------------

# HTTP header: Access-Control-Allow-Origin: *
_CORS_HEADER_WILDCARD_PATTERN = re.compile(
    r"""Access-Control-Allow-Origin\s*['":\s]+\*""",
    re.IGNORECASE,
)

# Python flask-cors: CORS(app, origins=["*"]) or CORS(app, resources={...: {"origins": "*"}})
_CORS_FLASK_WILDCARD_PATTERN = re.compile(
    r"""CORS\s*\([^)]*origins\s*=\s*\[?\s*['"]?\*['"]?\s*\]?""",
    re.IGNORECASE,
)

# Python flask-cors: allow_headers="*", expose_headers="*", supports_credentials=True with *
_CORS_FLASK_CREDENTIALS_PATTERN = re.compile(
    r"""CORS\s*\([^)]*supports_credentials\s*=\s*True""",
    re.IGNORECASE | re.DOTALL,
)

# Django CORS headers: CORS_ALLOW_ALL_ORIGINS = True or CORS_ORIGIN_ALLOW_ALL = True
_CORS_DJANGO_ALLOW_ALL_PATTERN = re.compile(
    r"""^(?:CORS_ALLOW_ALL_ORIGINS|CORS_ORIGIN_ALLOW_ALL)\s*=\s*True""",
    re.MULTILINE,
)

# JavaScript/Express: res.header("Access-Control-Allow-Origin", "*")
_CORS_EXPRESS_WILDCARD_PATTERN = re.compile(
    r"""\.(?:header|setHeader|set)\s*\(\s*"""
    r"""['"]Access-Control-Allow-Origin['"]\s*,\s*['"]\*['"]""",
    re.IGNORECASE,
)

# Generic CORS middleware: cors({ origin: "*" }) or cors({ origin: true })
_CORS_MIDDLEWARE_WILDCARD_PATTERN = re.compile(
    r"""cors\s*\(\s*\{[^}]*origin\s*:\s*(?:['"]\*['"]|true)""",
    re.IGNORECASE | re.DOTALL,
)


# ---------------------------------------------------------------------------
# Debug mode patterns
# ---------------------------------------------------------------------------

# Django: DEBUG = True (typically in settings.py)
_DEBUG_DJANGO_PATTERN = re.compile(
    r"""^DEBUG\s*=\s*True\b""",
    re.MULTILINE,
)

# Flask: app.debug = True
_DEBUG_FLASK_ATTR_PATTERN = re.compile(
    r"""\.debug\s*=\s*True\b""",
)

# Flask: app.run(debug=True)
_DEBUG_FLASK_RUN_PATTERN = re.compile(
    r"""\.run\s*\([^)]*debug\s*=\s*True""",
    re.DOTALL,
)

# JavaScript: NODE_ENV = 'development' or NODE_ENV: 'development'
# In production config files this indicates misconfiguration.
_DEBUG_NODE_ENV_PATTERN = re.compile(
    r"""NODE_ENV\s*[:=]\s*['"]development['"]""",
    re.IGNORECASE,
)

# Generic: app.config["DEBUG"] = True
_DEBUG_CONFIG_PATTERN = re.compile(
    r"""config\s*\[\s*['"]DEBUG['"]\s*\]\s*=\s*True""",
    re.IGNORECASE,
)

# Express: app.set("env", "development")
_DEBUG_EXPRESS_ENV_PATTERN = re.compile(
    r"""\.set\s*\(\s*['"]env['"]\s*,\s*['"]development['"]""",
    re.IGNORECASE,
)


# ---------------------------------------------------------------------------
# Security headers that should be set
# ---------------------------------------------------------------------------

# Headers we check for and their recommended values.
_REQUIRED_SECURITY_HEADERS: List[Tuple[str, str, str]] = [
    (
        "X-Frame-Options",
        "x-frame-options",
        "Set X-Frame-Options to 'DENY' or 'SAMEORIGIN' to prevent "
        "clickjacking attacks. For Flask: response.headers['X-Frame-Options'] "
        "= 'DENY'. For Express: app.use(helmet()) which sets this header "
        "automatically. For Django: add 'django.middleware.clickjacking."
        "XFrameOptionsMiddleware' to MIDDLEWARE.",
    ),
    (
        "X-Content-Type-Options",
        "x-content-type-options",
        "Set X-Content-Type-Options to 'nosniff' to prevent MIME type "
        "sniffing attacks. For Flask: response.headers['X-Content-Type-Options'] "
        "= 'nosniff'. For Express: app.use(helmet()) which sets this header "
        "automatically. For Django: SECURE_CONTENT_TYPE_NOSNIFF = True.",
    ),
    (
        "Strict-Transport-Security",
        "strict-transport-security",
        "Set Strict-Transport-Security (HSTS) header to enforce HTTPS "
        "connections. Recommended value: 'max-age=31536000; includeSubDomains'. "
        "For Flask: use flask-talisman. For Express: app.use(helmet.hsts()). "
        "For Django: SECURE_HSTS_SECONDS = 31536000 and "
        "SECURE_HSTS_INCLUDE_SUBDOMAINS = True.",
    ),
    (
        "Content-Security-Policy",
        "content-security-policy",
        "Set Content-Security-Policy header to prevent XSS and data injection "
        "attacks. Start with a restrictive policy: \"default-src 'self'\" and "
        "relax as needed. For Flask: use flask-talisman. For Express: "
        "app.use(helmet.contentSecurityPolicy()). For Django: use "
        "django-csp middleware.",
    ),
]

# Patterns that indicate a file sets response headers (making it a
# candidate for missing-headers analysis).
_SETS_HEADERS_PATTERN = re.compile(
    r"""(?:"""
    r"""\.headers\s*\[|"""
    r"""\.setHeader\s*\(|"""
    r"""\.set\s*\(\s*['"]|"""
    r"""\.header\s*\(\s*['"]|"""
    r"""add_header\s|"""
    r"""response\[|"""
    r"""Header\s*\(|"""
    r"""SECURE_|"""
    r"""MIDDLEWARE\s*=|"""
    r"""helmet\s*\("""
    r""")""",
    re.IGNORECASE,
)

# Django settings that imply security headers are configured.
_DJANGO_HEADER_SETTINGS = {
    "x-frame-options": re.compile(
        r"""X_FRAME_OPTIONS\s*=|XFrameOptionsMiddleware""", re.IGNORECASE
    ),
    "x-content-type-options": re.compile(
        r"""SECURE_CONTENT_TYPE_NOSNIFF\s*=\s*True""", re.IGNORECASE
    ),
    "strict-transport-security": re.compile(
        r"""SECURE_HSTS_SECONDS\s*=""", re.IGNORECASE
    ),
    "content-security-policy": re.compile(
        r"""CSPMiddleware|ContentSecurityPolicy|content.security.policy""",
        re.IGNORECASE,
    ),
}

# Express helmet covers multiple headers at once.
_HELMET_PATTERN = re.compile(
    r"""helmet\s*\(\s*\)""",
    re.IGNORECASE,
)


# ---------------------------------------------------------------------------
# Verbose error disclosure patterns
# ---------------------------------------------------------------------------

# Python Django/Flask: PROPAGATE_EXCEPTIONS = True
_VERBOSE_PROPAGATE_EXCEPTIONS_PATTERN = re.compile(
    r"""PROPAGATE_EXCEPTIONS\s*=\s*True""",
    re.IGNORECASE,
)

# Python: traceback.print_exc() or traceback.format_exc() in response context
_VERBOSE_TRACEBACK_PATTERN = re.compile(
    r"""traceback\.(?:print_exc|format_exc|print_exception)\s*\(""",
)

# Python Flask/Django: returning exception string to client
_VERBOSE_RETURN_EXCEPTION_PATTERN = re.compile(
    r"""(?:return|Response|JsonResponse|jsonify)\s*\(.*(?:str\s*\(\s*(?:e|err|exc|exception)|traceback|format_exc)""",
    re.IGNORECASE | re.DOTALL,
)

# Python: TRAP_HTTP_EXCEPTIONS = True (Flask)
_VERBOSE_TRAP_EXCEPTIONS_PATTERN = re.compile(
    r"""TRAP_HTTP_EXCEPTIONS\s*=\s*True""",
    re.IGNORECASE,
)

# Python: app.debug = True combined with error handling (proxy for verbose
# errors). Detected separately in debug mode, but if found in an error
# handler context it is also a verbose error issue.
_VERBOSE_DEBUG_ERRORHANDLER_PATTERN = re.compile(
    r"""@\s*app\.errorhandler[^)]*\).*?(?:debug|traceback|str\s*\(\s*e\b)""",
    re.IGNORECASE | re.DOTALL,
)

# JavaScript/Express: error handler that sends stack trace
_VERBOSE_EXPRESS_STACK_PATTERN = re.compile(
    r"""(?:err|error)\.stack""",
)

# JavaScript: sending error details in response
_VERBOSE_JS_ERROR_RESPONSE_PATTERN = re.compile(
    r"""(?:res\.(?:send|json|status)\s*\().*(?:err\.(?:message|stack)|error\.(?:message|stack))""",
    re.IGNORECASE | re.DOTALL,
)

# Python: showing detailed errors in production
_VERBOSE_SHOW_ERROR_DETAIL_PATTERN = re.compile(
    r"""(?:SHOW_ERROR_DETAILS|DISPLAY_ERRORS|DETAILED_ERRORS)\s*=\s*True""",
    re.IGNORECASE,
)


# ---------------------------------------------------------------------------
# Config file detection heuristics
# ---------------------------------------------------------------------------

# Filenames that are typically configuration files.
_CONFIG_FILE_PATTERNS: Set[str] = {
    "settings.py",
    "config.py",
    "configuration.py",
    "conf.py",
    "config.js",
    "config.ts",
    "server.js",
    "server.ts",
    "app.js",
    "app.ts",
    "app.py",
    "wsgi.py",
    "asgi.py",
    "manage.py",
    ".env",
    "environment.ts",
    "environment.js",
    "production.py",
    "development.py",
    "base.py",
    "local.py",
    "webpack.config.js",
    "next.config.js",
    "nuxt.config.js",
    "nuxt.config.ts",
}

# Patterns in file paths that suggest production configuration.
_PRODUCTION_PATH_INDICATORS: Tuple[str, ...] = (
    "production",
    "prod",
    "deploy",
    "release",
    "live",
)

# Patterns in file paths that suggest development/test configuration.
_DEVELOPMENT_PATH_INDICATORS: Tuple[str, ...] = (
    "development",
    "dev",
    "local",
    "test",
    "staging",
    "debug",
    "example",
    "sample",
)


# ---------------------------------------------------------------------------
# Finding ID generator
# ---------------------------------------------------------------------------


class _FindingIDGenerator:
    """Thread-unsafe sequential ID generator for config findings.

    Produces IDs in the format "CFG-001", "CFG-002", etc. A new generator
    is created for each analyze() invocation so IDs start from 1.
    """

    def __init__(self) -> None:
        self._counter = 0

    def next_id(self) -> str:
        """Return the next sequential finding ID."""
        self._counter += 1
        return f"CFG-{self._counter:03d}"


# ---------------------------------------------------------------------------
# Main analyzer class
# ---------------------------------------------------------------------------


class ConfigAnalyzer:
    """Detect security misconfigurations in application code.

    This analyzer implements four complementary detection strategies that
    together provide broad coverage of common security misconfiguration
    patterns:

    1. **CORS misconfiguration** (``_detect_cors_misconfiguration``): Scans
       raw source code for wildcard CORS origin configurations across
       Flask (flask-cors), Django (django-cors-headers), and Express.js
       middleware. Produces MEDIUM findings under CWE-942.

    2. **Debug mode enabled** (``_detect_debug_mode``): Detects debug mode
       settings left enabled in application configuration. Covers Django
       ``DEBUG = True``, Flask ``app.debug = True`` / ``app.run(debug=True)``,
       and Node.js ``NODE_ENV = 'development'``. Produces HIGH findings
       under CWE-489.

    3. **Missing security headers** (``_detect_missing_security_headers``):
       Identifies files that set HTTP response headers but omit critical
       security headers (X-Frame-Options, X-Content-Type-Options,
       Strict-Transport-Security, Content-Security-Policy). Produces MEDIUM
       findings under CWE-16.

    4. **Verbose error disclosure** (``_detect_verbose_errors``): Detects
       configurations and code patterns that expose stack traces or detailed
       error information to clients. Produces LOW findings under CWE-209.

    Attributes:
        VERSION: Analyzer version string for AssessmentResult tracking.

    Usage::

        analyzer = ConfigAnalyzer()
        findings = analyzer.analyze(parsed_files, config={})

    Configuration:
        The ``config`` dict passed to ``analyze()`` supports these optional
        keys:

        - ``skip_cors`` (bool): Disable CORS misconfiguration detection.
        - ``skip_debug_mode`` (bool): Disable debug mode detection.
        - ``skip_missing_headers`` (bool): Disable missing security headers
          detection.
        - ``skip_verbose_errors`` (bool): Disable verbose error detection.
    """

    VERSION: str = "1.0.0"

    def analyze(
        self,
        parsed_files: List[ParseResult],
        config: Dict[str, Any],
    ) -> List[Finding]:
        """Run all configuration detection strategies on the parsed files.

        Iterates over each parsed file and applies CORS misconfiguration,
        debug mode, missing security headers, and verbose error detection.
        Results from all four strategies are combined into a single list
        of findings.

        Args:
            parsed_files: List of ParseResult objects from the parsing
                phase. Each represents one source file with extracted
                metadata and raw source content.
            config: Optional configuration overrides. Supported keys:
                ``skip_cors`` (bool),
                ``skip_debug_mode`` (bool),
                ``skip_missing_headers`` (bool),
                ``skip_verbose_errors`` (bool).

        Returns:
            List of Finding objects, one per detected issue. Findings are
            ordered by detection strategy and then by file path within
            each strategy.
        """
        findings: List[Finding] = []
        id_gen = _FindingIDGenerator()

        skip_cors = config.get("skip_cors", False)
        skip_debug = config.get("skip_debug_mode", False)
        skip_headers = config.get("skip_missing_headers", False)
        skip_errors = config.get("skip_verbose_errors", False)

        for parsed_file in parsed_files:
            # Skip lockfiles -- they do not contain app configuration.
            if parsed_file.language == "lockfile":
                continue

            # 1. CORS misconfiguration detection
            if not skip_cors:
                findings.extend(
                    self._detect_cors_misconfiguration(parsed_file, id_gen)
                )

            # 2. Debug mode detection
            if not skip_debug:
                findings.extend(
                    self._detect_debug_mode(parsed_file, id_gen)
                )

            # 3. Missing security headers detection
            if not skip_headers:
                findings.extend(
                    self._detect_missing_security_headers(
                        parsed_file, id_gen
                    )
                )

            # 4. Verbose error disclosure detection
            if not skip_errors:
                findings.extend(
                    self._detect_verbose_errors(parsed_file, id_gen)
                )

        return findings

    # -----------------------------------------------------------------
    # Strategy 1: CORS misconfiguration detection
    # -----------------------------------------------------------------

    def _detect_cors_misconfiguration(
        self,
        parsed_file: ParseResult,
        id_gen: _FindingIDGenerator,
    ) -> List[Finding]:
        """Detect overly permissive CORS configurations.

        Scans raw source code for wildcard CORS origin settings across
        multiple frameworks (Flask flask-cors, Django django-cors-headers,
        Express.js, generic middleware). Wildcard origins allow any
        website to make cross-origin requests to the application, which
        can lead to data theft if the application also allows credentials.

        Args:
            parsed_file: A single parsed file result containing raw source
                code and file metadata.
            id_gen: Sequential ID generator for creating finding IDs.

        Returns:
            List of Finding objects for each CORS misconfiguration found.
        """
        findings: List[Finding] = []

        if not parsed_file.raw_source:
            return findings

        # Track (rule_id, line_number) to avoid duplicates.
        seen: Set[Tuple[str, int]] = set()

        cors_patterns: List[Tuple[re.Pattern, str]] = [  # type: ignore[type-arg]
            (_CORS_HEADER_WILDCARD_PATTERN, "header_wildcard"),
            (_CORS_FLASK_WILDCARD_PATTERN, "flask_cors_wildcard"),
            (_CORS_DJANGO_ALLOW_ALL_PATTERN, "django_cors_allow_all"),
            (_CORS_EXPRESS_WILDCARD_PATTERN, "express_cors_wildcard"),
            (_CORS_MIDDLEWARE_WILDCARD_PATTERN, "middleware_cors_wildcard"),
        ]

        for pattern, detection_type in cors_patterns:
            for match in pattern.finditer(parsed_file.raw_source):
                line_number = (
                    parsed_file.raw_source[: match.start()].count("\n") + 1
                )

                key = ("cors-wildcard", line_number)
                if key in seen:
                    continue

                # Check if this is a comment line.
                full_line = self._get_source_line(
                    parsed_file.source_lines, line_number
                )
                if self._is_comment_line(full_line):
                    continue

                seen.add(key)

                code_sample = self._build_code_sample(
                    parsed_file.source_lines, line_number
                )

                # Higher confidence if credentials are also enabled.
                has_credentials = bool(
                    _CORS_FLASK_CREDENTIALS_PATTERN.search(
                        parsed_file.raw_source
                    )
                )
                confidence = 0.85 if has_credentials else 0.75

                credential_warning = ""
                if has_credentials:
                    credential_warning = (
                        " Additionally, credentials support is enabled "
                        "(supports_credentials=True), which when combined "
                        "with a wildcard origin is a particularly dangerous "
                        "configuration that most browsers will block, but "
                        "older browsers may still allow."
                    )

                findings.append(
                    Finding(
                        id=id_gen.next_id(),
                        rule_id="cors-wildcard",
                        category=OWASPCategory.A05_SECURITY_MISCONFIGURATION,
                        severity=Severity.MEDIUM,
                        title="CORS configured with wildcard origin",
                        description=(
                            "The application is configured to allow "
                            "cross-origin requests from any origin ('*'). "
                            "This means any website can make requests to "
                            "your API from a user's browser, potentially "
                            "accessing sensitive data if the user is "
                            "authenticated. An attacker can host a "
                            "malicious page that silently reads data from "
                            "your API using the victim's session."
                            + credential_warning
                        ),
                        file_path=parsed_file.file_path,
                        line_number=line_number,
                        code_sample=code_sample,
                        remediation=(
                            "Replace the wildcard origin with a specific "
                            "list of trusted origins. For Flask: "
                            "CORS(app, origins=['https://example.com']). "
                            "For Django: CORS_ALLOWED_ORIGINS = "
                            "['https://example.com']. For Express: "
                            "cors({origin: ['https://example.com']}). "
                            "If your API is truly public and does not use "
                            "cookies or auth headers, a wildcard may be "
                            "acceptable -- add a suppression entry with "
                            "an explanation."
                        ),
                        cwe_id="CWE-942",
                        confidence=confidence,
                        metadata={
                            "detection_type": detection_type,
                            "has_credentials": has_credentials,
                            "language": parsed_file.language,
                        },
                    )
                )

        return findings

    # -----------------------------------------------------------------
    # Strategy 2: Debug mode detection
    # -----------------------------------------------------------------

    def _detect_debug_mode(
        self,
        parsed_file: ParseResult,
        id_gen: _FindingIDGenerator,
    ) -> List[Finding]:
        """Detect debug mode left enabled in application configuration.

        Scans raw source for debug mode settings across Django, Flask, and
        Node.js/Express. Debug mode in production is a high-severity issue
        because it typically exposes:

        - Full stack traces with source code paths
        - Environment variables and configuration values
        - Interactive debuggers (e.g., Werkzeug debugger in Flask)
        - Detailed SQL queries and database schema information

        Files in paths that contain development-related keywords
        (development, dev, local, test) are given lower confidence
        because debug mode is expected in those contexts.

        Args:
            parsed_file: A single parsed file result containing raw source
                code and file metadata.
            id_gen: Sequential ID generator for creating finding IDs.

        Returns:
            List of Finding objects for each debug mode detection.
        """
        findings: List[Finding] = []

        if not parsed_file.raw_source:
            return findings

        # Track (rule_id, line_number) to avoid duplicates.
        seen: Set[Tuple[str, int]] = set()

        # Determine if this file is in a development-like path.
        is_dev_path = self._is_development_path(parsed_file.file_path)

        debug_patterns: List[Tuple[re.Pattern, str, str]] = [  # type: ignore[type-arg]
            (
                _DEBUG_DJANGO_PATTERN,
                "django_debug_true",
                "Django DEBUG = True",
            ),
            (
                _DEBUG_FLASK_ATTR_PATTERN,
                "flask_debug_attr",
                "Flask app.debug = True",
            ),
            (
                _DEBUG_FLASK_RUN_PATTERN,
                "flask_debug_run",
                "Flask app.run(debug=True)",
            ),
            (
                _DEBUG_CONFIG_PATTERN,
                "config_debug_true",
                "Config DEBUG = True",
            ),
            (
                _DEBUG_EXPRESS_ENV_PATTERN,
                "express_env_development",
                "Express env set to development",
            ),
        ]

        # Node ENV pattern treated separately with language check.
        if parsed_file.language == "javascript":
            debug_patterns.append((
                _DEBUG_NODE_ENV_PATTERN,
                "node_env_development",
                "NODE_ENV = 'development'",
            ))

        for pattern, detection_type, title in debug_patterns:
            for match in pattern.finditer(parsed_file.raw_source):
                line_number = (
                    parsed_file.raw_source[: match.start()].count("\n") + 1
                )

                key = ("debug-mode-enabled", line_number)
                if key in seen:
                    continue

                full_line = self._get_source_line(
                    parsed_file.source_lines, line_number
                )
                if self._is_comment_line(full_line):
                    continue

                # Skip if the line is behind an environment variable check
                # like: DEBUG = os.environ.get("DEBUG", "False")
                if self._is_env_guarded(full_line):
                    continue

                seen.add(key)

                code_sample = self._build_code_sample(
                    parsed_file.source_lines, line_number
                )

                # Lower confidence for development-path files.
                confidence = 0.70 if is_dev_path else 0.85

                findings.append(
                    Finding(
                        id=id_gen.next_id(),
                        rule_id="debug-mode-enabled",
                        category=OWASPCategory.A05_SECURITY_MISCONFIGURATION,
                        severity=Severity.HIGH,
                        title=f"Debug mode enabled: {title}",
                        description=(
                            "Debug mode is enabled in the application "
                            "configuration. In production, debug mode "
                            "exposes detailed stack traces, environment "
                            "variables, source file paths, and potentially "
                            "interactive debuggers (e.g., Werkzeug debugger "
                            "in Flask which allows arbitrary code execution). "
                            "Attackers can use this information to map the "
                            "application's internals and craft targeted "
                            "exploits."
                        ),
                        file_path=parsed_file.file_path,
                        line_number=line_number,
                        code_sample=code_sample,
                        remediation=(
                            "Set debug mode based on an environment variable "
                            "that defaults to False. For Django: "
                            "DEBUG = os.environ.get('DEBUG', 'False') == 'True'. "
                            "For Flask: app.debug = os.environ.get('FLASK_DEBUG', "
                            "'0') == '1'. For Node.js: ensure NODE_ENV is set to "
                            "'production' in your deployment configuration. "
                            "Never commit DEBUG=True to your main branch."
                        ),
                        cwe_id="CWE-489",
                        confidence=confidence,
                        metadata={
                            "detection_type": detection_type,
                            "is_development_path": is_dev_path,
                            "language": parsed_file.language,
                        },
                    )
                )

        return findings

    # -----------------------------------------------------------------
    # Strategy 3: Missing security headers detection
    # -----------------------------------------------------------------

    def _detect_missing_security_headers(
        self,
        parsed_file: ParseResult,
        id_gen: _FindingIDGenerator,
    ) -> List[Finding]:
        """Detect absence of critical HTTP security headers.

        Identifies files that set HTTP response headers (indicating they
        are responsible for HTTP configuration) but omit one or more of
        the four critical security headers: X-Frame-Options,
        X-Content-Type-Options, Strict-Transport-Security, and
        Content-Security-Policy.

        This strategy only flags files that already participate in header
        management. Files with no header-setting code at all are skipped
        to avoid flooding the report with findings for every source file.

        If the Express ``helmet()`` middleware is detected, all four
        headers are considered covered since helmet sets them by default.

        Args:
            parsed_file: A single parsed file result containing raw source
                code and file metadata.
            id_gen: Sequential ID generator for creating finding IDs.

        Returns:
            List of Finding objects for each missing security header.
        """
        findings: List[Finding] = []

        if not parsed_file.raw_source:
            return findings

        # Only analyze files that set some response headers.
        if not _SETS_HEADERS_PATTERN.search(parsed_file.raw_source):
            return findings

        # If helmet() is used, assume all headers are covered.
        if _HELMET_PATTERN.search(parsed_file.raw_source):
            return findings

        raw_lower = parsed_file.raw_source.lower()

        for header_name, header_key, remediation in _REQUIRED_SECURITY_HEADERS:
            # Check if the header is already set anywhere in the file.
            header_present = header_key in raw_lower

            # Also check framework-specific settings for Django.
            if not header_present and parsed_file.language == "python":
                django_pattern = _DJANGO_HEADER_SETTINGS.get(header_key)
                if django_pattern and django_pattern.search(
                    parsed_file.raw_source
                ):
                    header_present = True

            if header_present:
                continue

            # Determine a representative line number -- use the first
            # header-setting line in the file as context anchor.
            anchor_match = _SETS_HEADERS_PATTERN.search(
                parsed_file.raw_source
            )
            line_number = 1
            if anchor_match:
                line_number = (
                    parsed_file.raw_source[: anchor_match.start()].count("\n")
                    + 1
                )

            code_sample = self._build_code_sample(
                parsed_file.source_lines, line_number
            )

            rule_id = (
                f"missing-security-header-"
                f"{header_name.lower()}"
            )

            findings.append(
                Finding(
                    id=id_gen.next_id(),
                    rule_id=rule_id,
                    category=OWASPCategory.A05_SECURITY_MISCONFIGURATION,
                    severity=Severity.MEDIUM,
                    title=f"Missing security header: {header_name}",
                    description=(
                        f"The file sets HTTP response headers but does not "
                        f"include the '{header_name}' security header. This "
                        f"header is recommended by OWASP and major security "
                        f"frameworks to protect against common web attacks. "
                        f"Without it, the application may be vulnerable to "
                        f"attacks that this header is designed to prevent."
                    ),
                    file_path=parsed_file.file_path,
                    line_number=line_number,
                    code_sample=code_sample,
                    remediation=remediation,
                    cwe_id="CWE-16",
                    confidence=0.70,
                    metadata={
                        "missing_header": header_name,
                        "language": parsed_file.language,
                    },
                )
            )

        return findings

    # -----------------------------------------------------------------
    # Strategy 4: Verbose error disclosure detection
    # -----------------------------------------------------------------

    def _detect_verbose_errors(
        self,
        parsed_file: ParseResult,
        id_gen: _FindingIDGenerator,
    ) -> List[Finding]:
        """Detect verbose error messages that expose internal details.

        Scans raw source for patterns that expose stack traces, exception
        details, or other internal information to clients. This includes
        framework settings like ``PROPAGATE_EXCEPTIONS = True`` and code
        patterns that pass exception strings or stack traces into HTTP
        responses.

        Args:
            parsed_file: A single parsed file result containing raw source
                code and file metadata.
            id_gen: Sequential ID generator for creating finding IDs.

        Returns:
            List of Finding objects for each verbose error pattern found.
        """
        findings: List[Finding] = []

        if not parsed_file.raw_source:
            return findings

        # Track (rule_id, line_number) to avoid duplicates.
        seen: Set[Tuple[str, int]] = set()

        # Python-specific patterns
        python_patterns: List[Tuple[re.Pattern, str, str]] = [  # type: ignore[type-arg]
            (
                _VERBOSE_PROPAGATE_EXCEPTIONS_PATTERN,
                "propagate_exceptions",
                "PROPAGATE_EXCEPTIONS = True allows unhandled exceptions "
                "to bubble up to the client with full stack traces",
            ),
            (
                _VERBOSE_TRAP_EXCEPTIONS_PATTERN,
                "trap_http_exceptions",
                "TRAP_HTTP_EXCEPTIONS = True causes Flask to re-raise HTTP "
                "exceptions instead of returning error responses, potentially "
                "exposing stack traces",
            ),
            (
                _VERBOSE_TRACEBACK_PATTERN,
                "traceback_usage",
                "Traceback formatting function used. If the output is "
                "included in an HTTP response, internal paths and code "
                "structure are exposed to clients",
            ),
            (
                _VERBOSE_RETURN_EXCEPTION_PATTERN,
                "exception_in_response",
                "Exception details appear to be included directly in an "
                "HTTP response. This exposes internal error messages, class "
                "names, and potentially stack traces to clients",
            ),
            (
                _VERBOSE_SHOW_ERROR_DETAIL_PATTERN,
                "show_error_details",
                "Detailed error display is explicitly enabled. In "
                "production, this exposes implementation details to "
                "attackers",
            ),
        ]

        # JavaScript-specific patterns
        javascript_patterns: List[Tuple[re.Pattern, str, str]] = [  # type: ignore[type-arg]
            (
                _VERBOSE_EXPRESS_STACK_PATTERN,
                "error_stack_access",
                "Error stack trace is accessed. If sent in the response, "
                "internal file paths and code structure are exposed",
            ),
            (
                _VERBOSE_JS_ERROR_RESPONSE_PATTERN,
                "error_in_response",
                "Error message or stack trace appears to be included in "
                "an HTTP response. This exposes internal error details to "
                "clients",
            ),
        ]

        # Select patterns based on language.
        patterns_to_check: List[Tuple[re.Pattern, str, str]] = []  # type: ignore[type-arg]
        if parsed_file.language == "python":
            patterns_to_check = python_patterns
        elif parsed_file.language == "javascript":
            patterns_to_check = javascript_patterns
        else:
            # Apply all patterns for unknown language.
            patterns_to_check = python_patterns + javascript_patterns

        for pattern, detection_type, specific_description in patterns_to_check:
            for match in pattern.finditer(parsed_file.raw_source):
                line_number = (
                    parsed_file.raw_source[: match.start()].count("\n") + 1
                )

                key = ("verbose-error-messages", line_number)
                if key in seen:
                    continue

                full_line = self._get_source_line(
                    parsed_file.source_lines, line_number
                )
                if self._is_comment_line(full_line):
                    continue

                seen.add(key)

                code_sample = self._build_code_sample(
                    parsed_file.source_lines, line_number
                )

                findings.append(
                    Finding(
                        id=id_gen.next_id(),
                        rule_id="verbose-error-messages",
                        category=OWASPCategory.A05_SECURITY_MISCONFIGURATION,
                        severity=Severity.LOW,
                        title="Verbose error message may expose internal details",
                        description=(
                            f"{specific_description}. Detailed error messages "
                            "in production can reveal internal implementation "
                            "details such as file paths, framework versions, "
                            "database schema, and third-party library names. "
                            "Attackers use this information for reconnaissance "
                            "to plan targeted attacks."
                        ),
                        file_path=parsed_file.file_path,
                        line_number=line_number,
                        code_sample=code_sample,
                        remediation=(
                            "Return generic error messages to clients and log "
                            "detailed errors server-side. For Python Flask: "
                            "use @app.errorhandler to return sanitized error "
                            "responses. For Django: set DEBUG = False and "
                            "configure custom error views. For Express: use "
                            "a custom error handler that sends a generic "
                            "message: res.status(500).json({error: 'Internal "
                            "server error'}). Log the full error with a "
                            "correlation ID for debugging."
                        ),
                        cwe_id="CWE-209",
                        confidence=0.75,
                        metadata={
                            "detection_type": detection_type,
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
    def _is_env_guarded(line: str) -> bool:
        """Check if a line reads a value from an environment variable.

        Lines that dynamically set configuration from the environment
        (e.g., ``DEBUG = os.environ.get("DEBUG", "False")``) should not
        be flagged as hardcoded debug mode.

        Args:
            line: A single source line.

        Returns:
            True if the line references an environment variable or config
            lookup, suggesting the value is not hardcoded.
        """
        env_patterns = (
            "os.environ",
            "os.getenv",
            "environ.get",
            "process.env",
            "config(",
            "config[",
            "config.get",
            "settings.",
            "getenv(",
        )
        line_lower = line.lower()
        return any(pat in line_lower for pat in env_patterns)

    @staticmethod
    def _is_development_path(file_path: str) -> bool:
        """Check if a file path suggests a development configuration.

        Files in paths containing keywords like 'development', 'dev',
        'local', or 'test' are likely intended for non-production use,
        which lowers the confidence of debug-mode findings.

        Args:
            file_path: Relative path to the source file.

        Returns:
            True if the path contains development-related keywords.
        """
        path_lower = file_path.lower()
        return any(
            indicator in path_lower
            for indicator in _DEVELOPMENT_PATH_INDICATORS
        )

    @staticmethod
    def _is_production_path(file_path: str) -> bool:
        """Check if a file path suggests a production configuration.

        Files in paths containing keywords like 'production', 'prod',
        or 'deploy' are production configurations where misconfigurations
        are more critical.

        Args:
            file_path: Relative path to the source file.

        Returns:
            True if the path contains production-related keywords.
        """
        path_lower = file_path.lower()
        return any(
            indicator in path_lower
            for indicator in _PRODUCTION_PATH_INDICATORS
        )
