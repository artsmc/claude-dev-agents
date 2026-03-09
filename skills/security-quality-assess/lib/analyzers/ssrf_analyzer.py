"""Server-Side Request Forgery (SSRF) analyzer.

Detects SSRF vulnerabilities in Python and JavaScript/TypeScript source code.
This analyzer maps to OWASP A10:2021 (Server-Side Request Forgery).

Detection strategies:
    1. **Python SSRF** -- regex-based detection of HTTP request functions
       (``urllib.request.urlopen``, ``requests.get/post``,
       ``http.client.HTTPConnection``, ``httpx.get/post``) where the URL
       argument is a variable assigned from user input
       (``request.args``, ``request.form``, ``request.json``,
       ``request.data``).

    2. **JavaScript SSRF** -- regex-based detection of HTTP request functions
       (``fetch()``, ``axios.get/post``, ``http.get``, ``https.get``) where
       the URL argument is a variable assigned from user input
       (``req.query``, ``req.body``, ``req.params``).

The key heuristic is: look for HTTP request functions where the URL argument
is a variable that was assigned from user input within approximately 10 lines
before the HTTP call, and that same variable name is used in the call.

All detections produce :class:`Finding` objects categorized under
:attr:`OWASPCategory.A10_SSRF` with CWE-918 reference.

This module uses only the Python standard library and has no external
dependencies.

Classes:
    SSRFAnalyzer: Main analyzer class with analyze() entry point.

References:
    - OWASP A10:2021 Server-Side Request Forgery
    - CWE-918: Server-Side Request Forgery (SSRF)
"""

import logging
import re
from typing import Any, Dict, List, Set, Tuple

from lib.models.finding import Finding, OWASPCategory, Severity
from lib.models.parse_result import ParseResult

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Python SSRF patterns
# ---------------------------------------------------------------------------

# HTTP request functions in Python that take a URL as first argument.
_PY_HTTP_REQUEST_FUNCTIONS = re.compile(
    r"""\b(?:urllib\.request\.urlopen|"""
    r"""requests\.(?:get|post|put|delete|patch|head|options)|"""
    r"""http\.client\.HTTPConnection|"""
    r"""http\.client\.HTTPSConnection|"""
    r"""httpx\.(?:get|post|put|delete|patch|head|options))\s*\(""",
)

# Python user input sources (Flask, Django, FastAPI).
_PY_USER_INPUT_PATTERN = re.compile(
    r"""(?:request\.(?:args|form|json|data|values)|"""
    r"""request\.(?:args|form|json|data|values)\.get\s*\(|"""
    r"""request\.GET|request\.POST|"""
    r"""request\.query_params)""",
)

# Variable assignment from user input in Python.
_PY_VAR_ASSIGNMENT = re.compile(
    r"""^\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*(?:"""
    r"""request\.(?:args|form|json|data|values)\.get\s*\(|"""
    r"""request\.(?:args|form|json|data|values)\[|"""
    r"""request\.(?:GET|POST)\.get\s*\(|"""
    r"""request\.(?:GET|POST)\[|"""
    r"""request\.query_params\.get\s*\()""",
    re.MULTILINE,
)


# ---------------------------------------------------------------------------
# JavaScript SSRF patterns
# ---------------------------------------------------------------------------

# HTTP request functions in JavaScript that take a URL as first argument.
_JS_HTTP_REQUEST_FUNCTIONS = re.compile(
    r"""\b(?:fetch|"""
    r"""axios\.(?:get|post|put|delete|patch|head|options|request)|"""
    r"""https?\.(?:get|request)|"""
    r"""got(?:\.(?:get|post|put|delete|patch))?|"""
    r"""superagent\.(?:get|post|put|delete|patch)|"""
    r"""node-fetch)\s*\(""",
)

# JavaScript user input sources (Express).
_JS_USER_INPUT_PATTERN = re.compile(
    r"""req\.(?:query|body|params)""",
)

# Variable assignment from user input in JavaScript.
_JS_VAR_ASSIGNMENT = re.compile(
    r"""(?:const|let|var)\s+(?:\{[^}]*\}\s*=\s*req\.(?:query|body|params)|"""
    r"""([a-zA-Z_$][a-zA-Z0-9_$]*)\s*=\s*req\.(?:query|body|params)(?:\.|(?:\[|\.get)))""",
    re.MULTILINE,
)

# Destructuring assignment from req.body/query/params.
_JS_DESTRUCTURE_ASSIGNMENT = re.compile(
    r"""(?:const|let|var)\s+\{\s*([^}]+)\s*\}\s*=\s*req\.(?:query|body|params)""",
    re.MULTILINE,
)

# Simple variable assignment: const url = req.query.url
_JS_SIMPLE_VAR_ASSIGNMENT = re.compile(
    r"""(?:const|let|var)\s+([a-zA-Z_$][a-zA-Z0-9_$]*)\s*=\s*req\.(?:query|body|params)""",
    re.MULTILINE,
)


# ---------------------------------------------------------------------------
# Finding ID generator
# ---------------------------------------------------------------------------


class _FindingIDGenerator:
    """Thread-unsafe sequential ID generator for SSRF findings.

    Produces IDs in the format "SSRF-001", "SSRF-002", etc. A new generator
    is created for each analyze() invocation so IDs start from 1.
    """

    def __init__(self) -> None:
        self._counter = 0

    def next_id(self) -> str:
        """Return the next sequential finding ID."""
        self._counter += 1
        return f"SSRF-{self._counter:03d}"


# ---------------------------------------------------------------------------
# Main analyzer class
# ---------------------------------------------------------------------------


class SSRFAnalyzer:
    """Detect Server-Side Request Forgery (SSRF) vulnerabilities.

    This analyzer detects SSRF vulnerabilities where user-controlled input
    is passed as a URL to HTTP request functions, allowing an attacker to
    force the server to make requests to arbitrary destinations including
    internal services, cloud metadata endpoints, and other sensitive
    resources.

    Detection uses a two-phase approach:
    1. Identify HTTP request function calls in the source code.
    2. For each call, check if the URL argument is a variable that was
       assigned from user input within approximately 10 lines before the
       call.

    Attributes:
        VERSION: Analyzer version string for AssessmentResult tracking.

    Usage::

        analyzer = SSRFAnalyzer()
        findings = analyzer.analyze(parsed_files, config={})

    Configuration:
        The ``config`` dict passed to ``analyze()`` supports these optional
        keys:

        - ``skip_ssrf`` (bool): Disable SSRF detection entirely.
    """

    VERSION: str = "1.0.0"

    def analyze(
        self,
        parsed_files: List[ParseResult],
        config: Dict[str, Any],
    ) -> List[Finding]:
        """Run SSRF detection strategies on the parsed files.

        Iterates over each parsed file and applies Python and JavaScript
        SSRF detection based on the file language.

        Args:
            parsed_files: List of ParseResult objects from the parsing phase.
            config: Optional configuration overrides. Supported keys:
                ``skip_ssrf`` (bool).

        Returns:
            List of Finding objects, one per detected issue.
        """
        findings: List[Finding] = []
        id_gen = _FindingIDGenerator()

        if config.get("skip_ssrf", False):
            return findings

        for parsed_file in parsed_files:
            if parsed_file.language == "lockfile":
                continue

            if parsed_file.language == "python":
                findings.extend(
                    self._detect_python_ssrf(parsed_file, id_gen)
                )
            elif parsed_file.language == "javascript":
                findings.extend(
                    self._detect_js_ssrf(parsed_file, id_gen)
                )

        return findings

    # -----------------------------------------------------------------
    # Python SSRF detection
    # -----------------------------------------------------------------

    def _detect_python_ssrf(
        self,
        parsed_file: ParseResult,
        id_gen: _FindingIDGenerator,
    ) -> List[Finding]:
        """Detect SSRF vulnerabilities in Python source code.

        Scans for HTTP request functions (urllib, requests, httpx, etc.)
        where the URL argument is a variable assigned from user input
        (Flask request.args, Django request.GET, etc.).

        Args:
            parsed_file: A single parsed file result.
            id_gen: Sequential ID generator for creating finding IDs.

        Returns:
            List of Finding objects for each Python SSRF vulnerability.
        """
        findings: List[Finding] = []

        if not parsed_file.raw_source:
            return findings

        raw = parsed_file.raw_source
        source_lines = parsed_file.source_lines
        seen_lines: set[int] = set()

        # Collect variable names assigned from user input and their lines.
        user_input_vars: Dict[str, int] = {}
        for match in _PY_VAR_ASSIGNMENT.finditer(raw):
            var_name = match.group(1)
            line_num = raw[: match.start()].count("\n") + 1
            user_input_vars[var_name] = line_num

        # Scan for HTTP request function calls.
        for match in _PY_HTTP_REQUEST_FUNCTIONS.finditer(raw):
            call_line = raw[: match.start()].count("\n") + 1

            if call_line in seen_lines:
                continue

            # Get the line text to extract the argument.
            line_text = self._get_source_line(source_lines, call_line)

            # Skip comment lines.
            if line_text.strip().startswith("#"):
                continue

            # Check if the call line directly contains user input references.
            has_direct_input = bool(
                _PY_USER_INPUT_PATTERN.search(line_text)
            )

            # Check if a user-input variable is used in the call.
            has_variable_input = False
            matched_var = ""
            for var_name, assign_line in user_input_vars.items():
                # Variable must be assigned before the call and within
                # ~10 lines.
                if assign_line < call_line and (call_line - assign_line) <= 10:
                    if re.search(r"\b" + re.escape(var_name) + r"\b", line_text):
                        has_variable_input = True
                        matched_var = var_name
                        break

            if not has_direct_input and not has_variable_input:
                continue

            seen_lines.add(call_line)

            code_sample = self._build_code_sample(source_lines, call_line)

            func_match = re.search(
                r"((?:urllib\.request\.urlopen|requests\.\w+|"
                r"httpx\.\w+|http\.client\.\w+))",
                line_text,
            )
            func_name = func_match.group(1) if func_match else "HTTP request function"

            confidence = 0.90 if has_direct_input else 0.85

            findings.append(
                Finding(
                    id=id_gen.next_id(),
                    rule_id="ssrf-user-input",
                    category=OWASPCategory.A10_SSRF,
                    severity=Severity.HIGH,
                    title=(
                        f"SSRF risk: {func_name}() called with "
                        "user-controlled URL"
                    ),
                    description=(
                        f"The function {func_name}() is called with a URL "
                        "that appears to be derived from user input. An "
                        "attacker can control the destination URL to force "
                        "the server to make requests to internal services "
                        "(e.g., http://169.254.169.254/ for cloud metadata), "
                        "localhost ports, or other internal resources that "
                        "are not accessible from the public internet. This "
                        "can lead to information disclosure, internal service "
                        "exploitation, or denial of service."
                    ),
                    file_path=parsed_file.file_path,
                    line_number=call_line,
                    code_sample=code_sample,
                    remediation=(
                        "Validate and sanitize user-provided URLs before "
                        "making HTTP requests. Implement an allowlist of "
                        "permitted domains/IP ranges. Block requests to "
                        "private IP ranges (10.0.0.0/8, 172.16.0.0/12, "
                        "192.168.0.0/16, 169.254.0.0/16, 127.0.0.0/8) and "
                        "cloud metadata endpoints. Use a URL parsing library "
                        "to validate the scheme (http/https only) and host. "
                        "Consider using a dedicated SSRF protection library "
                        "or proxy service for outbound requests."
                    ),
                    cwe_id="CWE-918",
                    confidence=confidence,
                    metadata={
                        "function_name": func_name,
                        "detection_type": (
                            "direct_input" if has_direct_input
                            else f"variable_input:{matched_var}"
                        ),
                        "language": parsed_file.language,
                    },
                )
            )

        return findings

    # -----------------------------------------------------------------
    # JavaScript SSRF detection
    # -----------------------------------------------------------------

    def _detect_js_ssrf(
        self,
        parsed_file: ParseResult,
        id_gen: _FindingIDGenerator,
    ) -> List[Finding]:
        """Detect SSRF vulnerabilities in JavaScript/TypeScript source code.

        Scans for HTTP request functions (fetch, axios, http.get, etc.)
        where the URL argument is a variable assigned from user input
        (Express req.query, req.body, req.params).

        Args:
            parsed_file: A single parsed file result.
            id_gen: Sequential ID generator for creating finding IDs.

        Returns:
            List of Finding objects for each JavaScript SSRF vulnerability.
        """
        findings: List[Finding] = []

        if not parsed_file.raw_source:
            return findings

        raw = parsed_file.raw_source
        source_lines = parsed_file.source_lines
        seen_lines: set[int] = set()

        # Collect variable names assigned from user input and their lines.
        user_input_vars: Dict[str, int] = {}

        # Simple assignments: const url = req.query.url
        for match in _JS_SIMPLE_VAR_ASSIGNMENT.finditer(raw):
            var_name = match.group(1)
            line_num = raw[: match.start()].count("\n") + 1
            user_input_vars[var_name] = line_num

        # Destructuring assignments: const { url, callback_url } = req.body
        for match in _JS_DESTRUCTURE_ASSIGNMENT.finditer(raw):
            destructured = match.group(1)
            line_num = raw[: match.start()].count("\n") + 1
            # Parse out individual variable names from destructuring.
            for var_part in destructured.split(","):
                var_part = var_part.strip()
                # Handle renaming: original: renamed
                if ":" in var_part:
                    var_part = var_part.split(":")[1].strip()
                # Handle defaults: name = default
                if "=" in var_part:
                    var_part = var_part.split("=")[0].strip()
                if var_part and re.match(r"^[a-zA-Z_$][a-zA-Z0-9_$]*$", var_part):
                    user_input_vars[var_part] = line_num

        # Scan for HTTP request function calls.
        for match in _JS_HTTP_REQUEST_FUNCTIONS.finditer(raw):
            call_line = raw[: match.start()].count("\n") + 1

            if call_line in seen_lines:
                continue

            # Get the line text.
            line_text = self._get_source_line(source_lines, call_line)

            # Skip comment lines.
            if line_text.strip().startswith("//"):
                continue

            # Check if the call line directly references req.query/body/params.
            has_direct_input = bool(
                _JS_USER_INPUT_PATTERN.search(line_text)
            )

            # Check if a user-input variable is used in the call.
            has_variable_input = False
            matched_var = ""
            for var_name, assign_line in user_input_vars.items():
                if assign_line < call_line and (call_line - assign_line) <= 10:
                    if re.search(r"\b" + re.escape(var_name) + r"\b", line_text):
                        has_variable_input = True
                        matched_var = var_name
                        break

            if not has_direct_input and not has_variable_input:
                continue

            seen_lines.add(call_line)

            code_sample = self._build_code_sample(source_lines, call_line)

            func_match = re.search(
                r"(fetch|axios\.\w+|https?\.\w+|got(?:\.\w+)?|"
                r"superagent\.\w+|node-fetch)",
                line_text,
            )
            func_name = func_match.group(1) if func_match else "HTTP request function"

            confidence = 0.90 if has_direct_input else 0.85

            findings.append(
                Finding(
                    id=id_gen.next_id(),
                    rule_id="ssrf-user-input",
                    category=OWASPCategory.A10_SSRF,
                    severity=Severity.HIGH,
                    title=(
                        f"SSRF risk: {func_name}() called with "
                        "user-controlled URL"
                    ),
                    description=(
                        f"The function {func_name}() is called with a URL "
                        "that appears to be derived from user input (req.query, "
                        "req.body, or req.params). An attacker can control the "
                        "destination URL to force the server to make requests "
                        "to internal services (e.g., http://169.254.169.254/ "
                        "for cloud metadata), localhost ports, or other "
                        "internal resources not accessible from the public "
                        "internet. This can lead to information disclosure, "
                        "internal service exploitation, or denial of service."
                    ),
                    file_path=parsed_file.file_path,
                    line_number=call_line,
                    code_sample=code_sample,
                    remediation=(
                        "Validate and sanitize user-provided URLs before making "
                        "HTTP requests. Implement an allowlist of permitted "
                        "domains/IP ranges. Block requests to private IP ranges "
                        "(10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16, "
                        "169.254.0.0/16, 127.0.0.0/8) and cloud metadata "
                        "endpoints. Use the URL constructor to parse and "
                        "validate the scheme (http/https only) and hostname. "
                        "Consider using a library like ssrf-req-filter or "
                        "ssrf-agent for Node.js."
                    ),
                    cwe_id="CWE-918",
                    confidence=confidence,
                    metadata={
                        "function_name": func_name,
                        "detection_type": (
                            "direct_input" if has_direct_input
                            else f"variable_input:{matched_var}"
                        ),
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
