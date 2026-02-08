"""Injection vulnerability analyzer.

Detects SQL injection, command injection, and code injection (including XSS)
vulnerabilities in Python and JavaScript/TypeScript source code. This analyzer
maps primarily to OWASP A03:2021 (Injection).

Detection strategies:
    1. **SQL injection** -- uses SQLQuery and JSDBQuery objects extracted by
       language parsers. Flags queries where ``is_parametrized`` is False,
       indicating string concatenation, f-strings, or ``.format()`` usage.
       Safe parameterized patterns (``?``, ``%s``, ``$1``, ``:name``) are
       excluded.

    2. **Command injection** -- uses DangerousCall objects from the Python
       parser. Flags ``subprocess.call/run/Popen`` with ``shell=True``,
       ``os.system()``, and ``os.popen()``. These allow arbitrary command
       execution when called with untrusted input.

    3. **Code injection** -- uses DangerousCall objects (Python) and
       DangerousPattern objects (JavaScript). Flags ``eval()``, ``exec()``,
       ``compile()`` in Python, and ``eval()``, ``new Function()``,
       ``innerHTML``, ``outerHTML``, ``dangerouslySetInnerHTML``, and
       ``document.write()`` in JavaScript/TypeScript. The JavaScript DOM
       manipulation patterns additionally produce XSS findings.

All detections produce :class:`Finding` objects categorized under
:attr:`OWASPCategory.A03_INJECTION` with appropriate CWE references:
    - CWE-78: OS Command Injection
    - CWE-79: Improper Neutralization of Input (XSS)
    - CWE-89: SQL Injection
    - CWE-94: Improper Control of Generation of Code (Code Injection)

This module uses only the Python standard library and has no external
dependencies.

Classes:
    InjectionAnalyzer: Main analyzer class with analyze() entry point.

References:
    - TR.md Section 4.3: InjectionAnalyzer
    - OWASP A03:2021 Injection
    - CWE-78: Improper Neutralization of Special Elements in OS Command
    - CWE-79: Improper Neutralization of Input During Web Page Generation
    - CWE-89: Improper Neutralization of Special Elements in SQL Command
    - CWE-94: Improper Control of Generation of Code
"""

import logging
import re
from typing import Any, Dict, List, Tuple

from lib.models.finding import Finding, OWASPCategory, Severity
from lib.models.parse_result import ParseResult

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# ORM / safe-call exclusion patterns for SQL injection
# ---------------------------------------------------------------------------

# SQLAlchemy query builder methods that are not raw SQL.
_ORM_METHOD_PATTERN = re.compile(
    r"\b(?:session\.query|Model\.query|\.filter\(|\.filter_by\(|\.join\("
    r"|\.select_from\(|\.subquery\(|\.with_entities\(|\.order_by\()",
    re.IGNORECASE,
)

# Django ORM patterns (safe by default).
_DJANGO_ORM_PATTERN = re.compile(
    r"\b(?:objects\.filter|objects\.get|objects\.exclude|objects\.annotate"
    r"|objects\.aggregate|objects\.values|objects\.create|objects\.all\()",
    re.IGNORECASE,
)


# ---------------------------------------------------------------------------
# Command injection: function sets
# ---------------------------------------------------------------------------

# Subprocess functions that are dangerous with shell=True.
_SUBPROCESS_FUNCTIONS = frozenset({
    "subprocess.call",
    "subprocess.run",
    "subprocess.Popen",
})

# OS-level command execution functions (always dangerous with dynamic input).
_OS_COMMAND_FUNCTIONS = frozenset({
    "os.system",
    "os.popen",
})

# Combined set of all command execution functions.
_COMMAND_FUNCTIONS = _SUBPROCESS_FUNCTIONS | _OS_COMMAND_FUNCTIONS


# ---------------------------------------------------------------------------
# Code injection: function sets
# ---------------------------------------------------------------------------

# Python builtins that execute arbitrary code.
_PYTHON_CODE_EXEC_FUNCTIONS = frozenset({
    "eval",
    "exec",
    "compile",
})

# Unsafe deserialization functions (closely related to code injection).
_DESERIALIZATION_FUNCTIONS = frozenset({
    "pickle.load",
    "pickle.loads",
})


# ---------------------------------------------------------------------------
# JavaScript XSS pattern types from DangerousPattern
# ---------------------------------------------------------------------------

# Pattern types that represent DOM-based XSS vectors.
_XSS_PATTERN_TYPES = frozenset({
    "innerHTML",
    "outerHTML",
    "dangerouslySetInnerHTML",
    "document.write",
})

# Pattern types that represent code injection vectors.
_CODE_INJECTION_PATTERN_TYPES = frozenset({
    "eval",
    "Function_constructor",
})


# ---------------------------------------------------------------------------
# Finding ID generator
# ---------------------------------------------------------------------------


class _FindingIDGenerator:
    """Thread-unsafe sequential ID generator for injection findings.

    Produces IDs in the format "INJ-001", "INJ-002", etc. A new generator
    is created for each analyze() invocation so IDs start from 1.
    """

    def __init__(self) -> None:
        self._counter = 0

    def next_id(self) -> str:
        """Return the next sequential finding ID."""
        self._counter += 1
        return f"INJ-{self._counter:03d}"


# ---------------------------------------------------------------------------
# Main analyzer class
# ---------------------------------------------------------------------------


class InjectionAnalyzer:
    """Detect SQL, command, and code injection vulnerabilities.

    This analyzer implements three complementary detection strategies that
    together provide broad coverage of injection attack vectors:

    1. **SQL injection** (``_detect_sql_injection``): Examines SQLQuery
       objects (Python) and JSDBQuery objects (JavaScript) extracted by the
       language parsers. Queries built with string concatenation, f-strings,
       or ``.format()`` are flagged. Queries using parameterized placeholders
       or ORM query builders are excluded.

    2. **Command injection** (``_detect_command_injection``): Examines
       DangerousCall objects for subprocess and os module calls.
       ``subprocess.call/run/Popen`` with ``shell=True`` and ``os.system``/
       ``os.popen`` calls are flagged as they allow arbitrary command
       execution when passed untrusted input.

    3. **Code injection** (``_detect_code_injection``): Examines both
       DangerousCall objects (Python ``eval``/``exec``/``compile``) and
       DangerousPattern objects (JavaScript ``eval``/``new Function``/
       ``innerHTML``/``document.write``). DOM manipulation patterns like
       ``innerHTML`` and ``dangerouslySetInnerHTML`` additionally produce
       XSS findings with CWE-79.

    All findings are categorized under OWASP A03:2021 (Injection).

    Attributes:
        VERSION: Analyzer version string for AssessmentResult tracking.

    Usage::

        analyzer = InjectionAnalyzer()
        findings = analyzer.analyze(parsed_files, config={})

    Configuration:
        The ``config`` dict passed to ``analyze()`` supports these optional
        keys:

        - ``skip_sql_injection`` (bool): Disable SQL injection detection.
        - ``skip_command_injection`` (bool): Disable command injection detection.
        - ``skip_code_injection`` (bool): Disable code injection detection.
    """

    VERSION: str = "1.0.0"

    def analyze(
        self,
        parsed_files: List[ParseResult],
        config: Dict[str, Any],
    ) -> List[Finding]:
        """Run all injection detection strategies on the parsed files.

        Iterates over each parsed file and applies SQL injection, command
        injection, and code injection detection. Results from all three
        strategies are combined into a single list of findings.

        Args:
            parsed_files: List of ParseResult objects from the parsing phase.
                Each represents one source file with extracted SQL queries,
                dangerous calls, and dangerous patterns.
            config: Optional configuration overrides. Supported keys:
                ``skip_sql_injection`` (bool), ``skip_command_injection``
                (bool), ``skip_code_injection`` (bool).

        Returns:
            List of Finding objects, one per detected issue. Findings are
            ordered by file path and then by line number within each file.
        """
        findings: List[Finding] = []
        id_gen = _FindingIDGenerator()

        skip_sql = config.get("skip_sql_injection", False)
        skip_command = config.get("skip_command_injection", False)
        skip_code = config.get("skip_code_injection", False)

        for parsed_file in parsed_files:
            # Skip lockfiles -- they do not contain executable code.
            if parsed_file.language == "lockfile":
                continue

            # 1. SQL injection detection
            if not skip_sql:
                findings.extend(
                    self._detect_sql_injection(parsed_file, id_gen)
                )

            # 2. Command injection detection
            if not skip_command:
                findings.extend(
                    self._detect_command_injection(parsed_file, id_gen)
                )

            # 3. Code injection detection (includes XSS)
            if not skip_code:
                findings.extend(
                    self._detect_code_injection(parsed_file, id_gen)
                )

        return findings

    # -----------------------------------------------------------------
    # Strategy 1: SQL injection detection
    # -----------------------------------------------------------------

    def _detect_sql_injection(
        self,
        parsed_file: ParseResult,
        id_gen: _FindingIDGenerator,
    ) -> List[Finding]:
        """Detect SQL injection vulnerabilities from parsed query objects.

        Examines SQLQuery objects (from Python source) and JSDBQuery objects
        (from JavaScript/TypeScript source) that were extracted by the
        language parsers. Queries where ``is_parametrized`` is False are
        flagged as potential SQL injection vectors.

        Additional exclusion filters are applied to reduce false positives:
        - ORM query builder patterns (SQLAlchemy, Django) are excluded.
        - Queries containing only parameterized placeholders are excluded.

        Args:
            parsed_file: A single parsed file result containing SQL query
                extraction data.
            id_gen: Sequential ID generator for creating finding IDs.

        Returns:
            List of Finding objects for each SQL injection vulnerability
            detected. Each finding includes the query pattern, file location,
            and specific remediation guidance.
        """
        findings: List[Finding] = []

        # Track (line_number,) to avoid duplicate findings when Python and
        # JS queries overlap on the same line (unlikely but defensive).
        seen_lines: set[int] = set()

        # --- Python SQL queries ---
        for query in parsed_file.sql_queries:
            if query.is_parametrized:
                continue

            if query.line_number in seen_lines:
                continue

            # Exclude ORM query builder patterns (safe by construction).
            if self._is_orm_safe_pattern(query.query_pattern):
                continue

            seen_lines.add(query.line_number)

            code_sample = self._build_code_sample(
                parsed_file.source_lines, query.line_number
            )

            # Determine confidence based on query pattern clarity.
            confidence = self._sql_confidence(query.query_pattern)

            findings.append(
                Finding(
                    id=id_gen.next_id(),
                    rule_id="sql-injection",
                    category=OWASPCategory.A03_INJECTION,
                    severity=Severity.HIGH,
                    title="Potential SQL injection via string construction",
                    description=(
                        "A SQL query is constructed using string concatenation, "
                        "f-string interpolation, or .format() rather than "
                        "parameterized placeholders. An attacker who controls "
                        "any interpolated variable can manipulate the query to "
                        "read, modify, or delete arbitrary database records, "
                        "or in some cases execute operating system commands "
                        "via database extensions (e.g., xp_cmdshell, COPY TO "
                        "PROGRAM)."
                    ),
                    file_path=parsed_file.file_path,
                    line_number=query.line_number,
                    code_sample=code_sample,
                    remediation=(
                        "Use parameterized queries with placeholders instead of "
                        "string concatenation. For Python: use cursor.execute("
                        "'SELECT * FROM users WHERE id = ?', (user_id,)) or "
                        "cursor.execute('SELECT * FROM users WHERE id = %s', "
                        "(user_id,)). For ORMs like SQLAlchemy, use the query "
                        "builder API: session.query(User).filter(User.id == "
                        "user_id). Never construct SQL strings by embedding "
                        "user input directly."
                    ),
                    cwe_id="CWE-89",
                    confidence=confidence,
                    metadata={
                        "query_pattern": query.query_pattern[:200],
                        "language": parsed_file.language,
                        "detection_source": "python_parser",
                    },
                )
            )

        # --- JavaScript/TypeScript SQL queries ---
        for js_query in parsed_file.js_db_queries:
            if js_query.is_parametrized:
                continue

            if js_query.line_number in seen_lines:
                continue

            seen_lines.add(js_query.line_number)

            code_sample = self._build_code_sample(
                parsed_file.source_lines, js_query.line_number
            )

            confidence = self._sql_confidence(js_query.query_pattern)

            findings.append(
                Finding(
                    id=id_gen.next_id(),
                    rule_id="sql-injection",
                    category=OWASPCategory.A03_INJECTION,
                    severity=Severity.HIGH,
                    title="Potential SQL injection via string construction",
                    description=(
                        "A SQL query is constructed using string concatenation "
                        "or template literal interpolation rather than "
                        "parameterized placeholders. An attacker who controls "
                        "any interpolated variable can manipulate the query to "
                        "read, modify, or delete arbitrary database records."
                    ),
                    file_path=parsed_file.file_path,
                    line_number=js_query.line_number,
                    code_sample=code_sample,
                    remediation=(
                        "Use parameterized queries with placeholders instead of "
                        "string concatenation. For Sequelize: use "
                        "sequelize.query('SELECT * FROM users WHERE id = ?', "
                        "{replacements: [userId]}). For Prisma: use "
                        "prisma.$queryRaw`SELECT * FROM users WHERE id = "
                        "${userId}` (tagged template literals are auto-"
                        "parameterized). For Knex: use knex('users').where("
                        "'id', userId). Never embed user input in SQL strings."
                    ),
                    cwe_id="CWE-89",
                    confidence=confidence,
                    metadata={
                        "query_pattern": js_query.query_pattern[:200],
                        "language": parsed_file.language,
                        "detection_source": "javascript_parser",
                    },
                )
            )

        return findings

    # -----------------------------------------------------------------
    # Strategy 2: Command injection detection
    # -----------------------------------------------------------------

    def _detect_command_injection(
        self,
        parsed_file: ParseResult,
        id_gen: _FindingIDGenerator,
    ) -> List[Finding]:
        """Detect command injection vulnerabilities from dangerous call objects.

        Examines DangerousCall objects extracted by the Python parser for
        subprocess and OS command execution calls. Two risk tiers exist:

        **CRITICAL** (always dangerous):
            - ``os.system(cmd)`` -- passes command directly to the shell.
            - ``os.popen(cmd)`` -- passes command directly to the shell.
            - ``subprocess.call/run/Popen(..., shell=True)`` -- when
              ``shell=True`` is set, the command string is passed to the
              shell for interpretation, enabling injection via shell
              metacharacters.

        **HIGH** (dangerous depending on context):
            - ``subprocess.call/run/Popen(...)`` without ``shell=True`` --
              still flagged as a warning because the call site may be
              passing unsanitized input as the command or arguments, but
              at reduced severity since the shell is not invoked.

        JavaScript command injection (e.g., ``child_process.exec``) is
        detected via the raw source scanning in code injection detection
        and DangerousPattern objects.

        Args:
            parsed_file: A single parsed file result containing dangerous
                call extraction data.
            id_gen: Sequential ID generator for creating finding IDs.

        Returns:
            List of Finding objects for each command injection vulnerability
            detected.
        """
        findings: List[Finding] = []

        # Track line numbers to avoid duplicates.
        seen_lines: set[int] = set()

        for call in parsed_file.dangerous_calls:
            # Only process command execution functions.
            if call.function_name not in _COMMAND_FUNCTIONS:
                continue

            if call.line_number in seen_lines:
                continue
            seen_lines.add(call.line_number)

            code_sample = self._build_code_sample(
                parsed_file.source_lines, call.line_number
            )

            # Determine severity based on shell usage.
            if call.function_name in _OS_COMMAND_FUNCTIONS:
                # os.system and os.popen always use the shell.
                severity = Severity.CRITICAL
                confidence = 0.90
                title = (
                    f"Command injection risk: {call.function_name}() "
                    "passes input to the system shell"
                )
                description = (
                    f"The function {call.function_name}() is called, which "
                    "passes its argument directly to the operating system "
                    "shell for execution. If any part of the command string "
                    "is derived from user input, an attacker can inject "
                    "arbitrary shell commands using metacharacters such as "
                    "; | && ` $() and others. Even seemingly safe commands "
                    "can be exploited through argument injection."
                )
            elif call.has_shell_true:
                # subprocess with shell=True is critical.
                severity = Severity.CRITICAL
                confidence = 0.90
                title = (
                    f"Command injection risk: {call.function_name}() "
                    "called with shell=True"
                )
                description = (
                    f"The function {call.function_name}() is called with "
                    "shell=True, which causes the command to be executed "
                    "through the system shell. If any part of the command "
                    "string is derived from user input, an attacker can "
                    "inject arbitrary shell commands. The combination of "
                    "subprocess functions with shell=True is one of the "
                    "most common command injection vectors in Python."
                )
            else:
                # subprocess without shell=True is lower risk but still notable.
                severity = Severity.MEDIUM
                confidence = 0.60
                title = (
                    f"Potential command injection: {call.function_name}() "
                    "executes external process"
                )
                description = (
                    f"The function {call.function_name}() is called without "
                    "shell=True. While this avoids shell interpretation, the "
                    "function still executes an external process. If the "
                    "command name or arguments are derived from user input, "
                    "an attacker may be able to execute unintended programs "
                    "or pass malicious arguments."
                )

            remediation = (
                "Avoid os.system() and os.popen() entirely -- use "
                "subprocess.run() with shell=False (the default) and pass "
                "arguments as a list: subprocess.run(['cmd', 'arg1', 'arg2']). "
                "Never pass user input as part of a shell command string. "
                "If shell features are required, validate input against a "
                "strict allowlist of permitted values. Use shlex.quote() to "
                "escape individual arguments when shell=True cannot be avoided."
            )

            findings.append(
                Finding(
                    id=id_gen.next_id(),
                    rule_id="command-injection",
                    category=OWASPCategory.A03_INJECTION,
                    severity=severity,
                    title=title,
                    description=description,
                    file_path=parsed_file.file_path,
                    line_number=call.line_number,
                    code_sample=code_sample,
                    remediation=remediation,
                    cwe_id="CWE-78",
                    confidence=confidence,
                    metadata={
                        "function_name": call.function_name,
                        "has_shell_true": call.has_shell_true,
                        "arguments": call.arguments[:200],
                        "language": parsed_file.language,
                    },
                )
            )

        return findings

    # -----------------------------------------------------------------
    # Strategy 3: Code injection and XSS detection
    # -----------------------------------------------------------------

    def _detect_code_injection(
        self,
        parsed_file: ParseResult,
        id_gen: _FindingIDGenerator,
    ) -> List[Finding]:
        """Detect code injection and XSS vulnerabilities.

        Examines two sources of data:

        **Python DangerousCall objects:**
            - ``eval()`` -- executes arbitrary Python expressions.
            - ``exec()`` -- executes arbitrary Python statements.
            - ``compile()`` -- compiles arbitrary Python code objects.
            - ``pickle.load/loads()`` -- deserializes Python objects, which
              can execute arbitrary code during unpickling.

        **JavaScript DangerousPattern objects:**
            - ``eval()`` -- executes arbitrary JavaScript code.
            - ``new Function()`` -- creates a function from a code string.
            - ``innerHTML``/``outerHTML`` assignment -- injects unescaped HTML.
            - ``dangerouslySetInnerHTML`` -- React's explicit XSS bypass.
            - ``document.write()`` -- writes unescaped content to the DOM.

        DOM manipulation patterns (innerHTML, outerHTML,
        dangerouslySetInnerHTML, document.write) are classified as XSS
        vulnerabilities (CWE-79) rather than general code injection (CWE-94)
        since their primary attack vector is cross-site scripting.

        Args:
            parsed_file: A single parsed file result containing dangerous
                call and pattern extraction data.
            id_gen: Sequential ID generator for creating finding IDs.

        Returns:
            List of Finding objects for each code injection or XSS
            vulnerability detected.
        """
        findings: List[Finding] = []

        # Track line numbers to avoid duplicates.
        seen_lines: set[int] = set()

        # --- Python code injection (DangerousCall objects) ---
        findings.extend(
            self._detect_python_code_injection(parsed_file, id_gen, seen_lines)
        )

        # --- JavaScript code injection and XSS (DangerousPattern objects) ---
        findings.extend(
            self._detect_js_code_injection(parsed_file, id_gen, seen_lines)
        )

        return findings

    def _detect_python_code_injection(
        self,
        parsed_file: ParseResult,
        id_gen: _FindingIDGenerator,
        seen_lines: set[int],
    ) -> List[Finding]:
        """Detect Python-specific code injection from DangerousCall objects.

        Handles eval(), exec(), compile(), and unsafe deserialization
        (pickle.load/loads).

        Args:
            parsed_file: A single parsed file result.
            id_gen: Sequential ID generator for creating finding IDs.
            seen_lines: Set of already-processed line numbers (mutated).

        Returns:
            List of Finding objects for Python code injection vulnerabilities.
        """
        findings: List[Finding] = []

        for call in parsed_file.dangerous_calls:
            # Skip command injection functions (handled separately).
            if call.function_name in _COMMAND_FUNCTIONS:
                continue

            if call.line_number in seen_lines:
                continue

            # Determine the finding type based on the function.
            if call.function_name in _PYTHON_CODE_EXEC_FUNCTIONS:
                seen_lines.add(call.line_number)
                findings.append(
                    self._create_python_code_exec_finding(
                        parsed_file, call, id_gen
                    )
                )
            elif call.function_name in _DESERIALIZATION_FUNCTIONS:
                seen_lines.add(call.line_number)
                findings.append(
                    self._create_deserialization_finding(
                        parsed_file, call, id_gen
                    )
                )

        return findings

    def _detect_js_code_injection(
        self,
        parsed_file: ParseResult,
        id_gen: _FindingIDGenerator,
        seen_lines: set[int],
    ) -> List[Finding]:
        """Detect JavaScript-specific code injection and XSS from DangerousPattern objects.

        Code injection patterns (eval, new Function) produce CWE-94 findings.
        DOM manipulation patterns (innerHTML, dangerouslySetInnerHTML,
        document.write) produce CWE-79 XSS findings.

        Args:
            parsed_file: A single parsed file result.
            id_gen: Sequential ID generator for creating finding IDs.
            seen_lines: Set of already-processed line numbers (mutated).

        Returns:
            List of Finding objects for JavaScript injection/XSS vulnerabilities.
        """
        findings: List[Finding] = []

        for pattern in parsed_file.dangerous_patterns:
            if pattern.line_number in seen_lines:
                continue

            if pattern.pattern_type in _CODE_INJECTION_PATTERN_TYPES:
                seen_lines.add(pattern.line_number)
                findings.append(
                    self._create_js_code_injection_finding(
                        parsed_file, pattern, id_gen
                    )
                )
            elif pattern.pattern_type in _XSS_PATTERN_TYPES:
                seen_lines.add(pattern.line_number)
                findings.append(
                    self._create_xss_finding(
                        parsed_file, pattern, id_gen
                    )
                )

        return findings

    # -----------------------------------------------------------------
    # Finding factory methods
    # -----------------------------------------------------------------

    def _create_python_code_exec_finding(
        self,
        parsed_file: ParseResult,
        call: Any,
        id_gen: _FindingIDGenerator,
    ) -> Finding:
        """Create a Finding for Python eval/exec/compile usage.

        Args:
            parsed_file: The parsed file containing the call.
            call: A DangerousCall object for eval, exec, or compile.
            id_gen: Sequential ID generator.

        Returns:
            A Finding object with code-injection classification.
        """
        code_sample = self._build_code_sample(
            parsed_file.source_lines, call.line_number
        )

        func = call.function_name

        if func == "eval":
            title = "Code injection risk: eval() executes arbitrary expressions"
            description = (
                "The built-in eval() function is called, which evaluates an "
                "arbitrary Python expression and returns the result. If the "
                "expression string is derived from user input, an attacker "
                "can execute arbitrary Python code, including importing "
                "modules, accessing the file system, and running shell "
                "commands via os.system() or subprocess."
            )
            confidence = 0.85
        elif func == "exec":
            title = "Code injection risk: exec() executes arbitrary statements"
            description = (
                "The built-in exec() function is called, which executes an "
                "arbitrary Python code block. Unlike eval(), exec() can "
                "execute multi-line statements including imports, class "
                "definitions, and loops. If the code string is derived from "
                "user input, an attacker has full code execution capability."
            )
            confidence = 0.85
        else:
            # compile()
            title = "Code injection risk: compile() prepares code for execution"
            description = (
                "The built-in compile() function is called, which compiles a "
                "source string into a code object that can be executed by "
                "eval() or exec(). If the source string is derived from user "
                "input, this enables arbitrary code execution when the "
                "compiled code object is subsequently evaluated."
            )
            confidence = 0.80

        return Finding(
            id=id_gen.next_id(),
            rule_id="code-injection",
            category=OWASPCategory.A03_INJECTION,
            severity=Severity.HIGH,
            title=title,
            description=description,
            file_path=parsed_file.file_path,
            line_number=call.line_number,
            code_sample=code_sample,
            remediation=(
                f"Avoid using {func}() with any input that could be "
                "influenced by users. If dynamic behavior is required, use "
                "safer alternatives: ast.literal_eval() for evaluating data "
                "literals, a restricted expression parser for mathematical "
                "expressions, or a sandboxed execution environment. For "
                "configuration-driven logic, use a data-driven approach "
                "(dictionaries, strategy pattern) instead of executing "
                "arbitrary code strings."
            ),
            cwe_id="CWE-94",
            confidence=confidence,
            metadata={
                "function_name": call.function_name,
                "arguments": call.arguments[:200],
                "language": parsed_file.language,
            },
        )

    def _create_deserialization_finding(
        self,
        parsed_file: ParseResult,
        call: Any,
        id_gen: _FindingIDGenerator,
    ) -> Finding:
        """Create a Finding for unsafe pickle deserialization.

        Pickle deserialization is a form of code injection because the pickle
        protocol allows arbitrary Python code execution during unpickling
        via the ``__reduce__`` method.

        Args:
            parsed_file: The parsed file containing the call.
            call: A DangerousCall object for pickle.load or pickle.loads.
            id_gen: Sequential ID generator.

        Returns:
            A Finding object with code-injection classification.
        """
        code_sample = self._build_code_sample(
            parsed_file.source_lines, call.line_number
        )

        return Finding(
            id=id_gen.next_id(),
            rule_id="code-injection",
            category=OWASPCategory.A03_INJECTION,
            severity=Severity.HIGH,
            title=(
                f"Unsafe deserialization: {call.function_name}() can "
                "execute arbitrary code"
            ),
            description=(
                f"The function {call.function_name}() is called to "
                "deserialize data using Python's pickle protocol. Pickle is "
                "not a secure serialization format -- a maliciously crafted "
                "pickle payload can execute arbitrary Python code during "
                "deserialization via the __reduce__ method. This is "
                "equivalent to remote code execution if the pickled data "
                "comes from an untrusted source."
            ),
            file_path=parsed_file.file_path,
            line_number=call.line_number,
            code_sample=code_sample,
            remediation=(
                "Never use pickle to deserialize data from untrusted sources. "
                "Use JSON, MessagePack, or Protocol Buffers for data "
                "interchange. If pickle is required for internal use, "
                "implement HMAC-based signing to verify data integrity before "
                "deserialization. Consider using the 'restrictedpickle' or "
                "'fickling' library to analyze pickle payloads for safety."
            ),
            cwe_id="CWE-94",
            confidence=0.85,
            metadata={
                "function_name": call.function_name,
                "arguments": call.arguments[:200],
                "language": parsed_file.language,
                "sub_category": "unsafe_deserialization",
            },
        )

    def _create_js_code_injection_finding(
        self,
        parsed_file: ParseResult,
        pattern: Any,
        id_gen: _FindingIDGenerator,
    ) -> Finding:
        """Create a Finding for JavaScript eval() or new Function() usage.

        Args:
            parsed_file: The parsed file containing the pattern.
            pattern: A DangerousPattern object for eval or Function_constructor.
            id_gen: Sequential ID generator.

        Returns:
            A Finding object with code-injection classification.
        """
        code_sample = self._build_code_sample(
            parsed_file.source_lines, pattern.line_number
        )

        if pattern.pattern_type == "eval":
            title = (
                "Code injection risk: eval() executes arbitrary JavaScript"
            )
            description = (
                "The eval() function is called, which executes an arbitrary "
                "JavaScript expression or statement. If the evaluated string "
                "is derived from user input (URL parameters, form fields, "
                "postMessage data), an attacker can execute arbitrary "
                "JavaScript in the context of the application, leading to "
                "session hijacking, data theft, or privilege escalation."
            )
            confidence = 0.85
        else:
            # Function_constructor
            title = (
                "Code injection risk: new Function() creates code from string"
            )
            description = (
                "The Function constructor is used to create a function from "
                "a string argument. This is functionally equivalent to eval() "
                "and executes arbitrary JavaScript code. If the function body "
                "string is derived from user input, an attacker can inject "
                "arbitrary JavaScript code."
            )
            confidence = 0.85

        return Finding(
            id=id_gen.next_id(),
            rule_id="code-injection",
            category=OWASPCategory.A03_INJECTION,
            severity=Severity.HIGH,
            title=title,
            description=description,
            file_path=parsed_file.file_path,
            line_number=pattern.line_number,
            code_sample=code_sample,
            remediation=(
                "Avoid eval() and new Function() entirely. For JSON parsing, "
                "use JSON.parse(). For dynamic property access, use bracket "
                "notation: obj[key]. For template rendering, use a proper "
                "template engine with auto-escaping (Handlebars, EJS, Nunjucks). "
                "If dynamic code execution is absolutely required, use a "
                "sandboxed environment such as a Web Worker with restricted "
                "APIs or the vm2 library in Node.js."
            ),
            cwe_id="CWE-94",
            confidence=confidence,
            metadata={
                "pattern_type": pattern.pattern_type,
                "context": pattern.context[:200],
                "language": parsed_file.language,
            },
        )

    def _create_xss_finding(
        self,
        parsed_file: ParseResult,
        pattern: Any,
        id_gen: _FindingIDGenerator,
    ) -> Finding:
        """Create a Finding for DOM-based XSS vulnerabilities.

        Covers innerHTML, outerHTML, dangerouslySetInnerHTML, and
        document.write() patterns.

        Args:
            parsed_file: The parsed file containing the pattern.
            pattern: A DangerousPattern object for an XSS vector.
            id_gen: Sequential ID generator.

        Returns:
            A Finding object with XSS (CWE-79) classification.
        """
        code_sample = self._build_code_sample(
            parsed_file.source_lines, pattern.line_number
        )

        # Build pattern-specific title and description.
        title, description, confidence = self._xss_details(
            pattern.pattern_type
        )

        return Finding(
            id=id_gen.next_id(),
            rule_id="xss-vulnerability",
            category=OWASPCategory.A03_INJECTION,
            severity=Severity.HIGH,
            title=title,
            description=description,
            file_path=parsed_file.file_path,
            line_number=pattern.line_number,
            code_sample=code_sample,
            remediation=self._xss_remediation(pattern.pattern_type),
            cwe_id="CWE-79",
            confidence=confidence,
            metadata={
                "pattern_type": pattern.pattern_type,
                "context": pattern.context[:200],
                "language": parsed_file.language,
                "sub_category": "dom_based_xss",
            },
        )

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
    def _is_orm_safe_pattern(query_pattern: str) -> bool:
        """Check if a SQL query pattern is from a safe ORM query builder.

        ORM query builder APIs (SQLAlchemy's ``session.query``, Django's
        ``objects.filter``, etc.) construct parameterized queries internally
        and are not vulnerable to SQL injection.

        Args:
            query_pattern: The query pattern string from a SQLQuery object.

        Returns:
            True if the pattern matches a known-safe ORM query builder call.
        """
        if _ORM_METHOD_PATTERN.search(query_pattern):
            return True
        if _DJANGO_ORM_PATTERN.search(query_pattern):
            return True
        return False

    @staticmethod
    def _sql_confidence(query_pattern: str) -> float:
        """Calculate detection confidence for a SQL injection finding.

        Higher confidence is assigned when the query pattern clearly shows
        string interpolation with SQL keywords.

        Args:
            query_pattern: The query pattern string from a SQLQuery or
                JSDBQuery object.

        Returns:
            Confidence score between 0.0 and 1.0.
        """
        # Patterns with explicit SQL keywords get higher confidence.
        sql_keywords_found = len(re.findall(
            r"\b(SELECT|INSERT|UPDATE|DELETE|DROP)\b",
            query_pattern,
            re.IGNORECASE,
        ))

        if sql_keywords_found >= 2:
            return 0.95
        if sql_keywords_found == 1:
            return 0.90
        # Fallback for patterns where the SQL keyword was in a
        # different part of the expression.
        return 0.80

    @staticmethod
    def _xss_details(
        pattern_type: str,
    ) -> Tuple[str, str, float]:
        """Return title, description, and confidence for an XSS pattern type.

        Args:
            pattern_type: One of "innerHTML", "outerHTML",
                "dangerouslySetInnerHTML", "document.write".

        Returns:
            Tuple of (title, description, confidence).
        """
        if pattern_type == "innerHTML":
            return (
                "XSS risk: innerHTML assignment with potentially untrusted data",
                (
                    "The innerHTML property is assigned a value, which "
                    "inserts raw HTML into the DOM without escaping. If the "
                    "assigned value contains user-controlled data, an attacker "
                    "can inject <script> tags, event handlers (onerror, onload), "
                    "or other malicious HTML to execute arbitrary JavaScript in "
                    "the victim's browser session."
                ),
                0.80,
            )
        if pattern_type == "outerHTML":
            return (
                "XSS risk: outerHTML assignment with potentially untrusted data",
                (
                    "The outerHTML property is assigned a value, which "
                    "replaces the element and its content with raw HTML. Like "
                    "innerHTML, this does not escape the inserted content and "
                    "is vulnerable to XSS if the value contains user input."
                ),
                0.80,
            )
        if pattern_type == "dangerouslySetInnerHTML":
            return (
                "XSS risk: dangerouslySetInnerHTML used in React component",
                (
                    "The React property dangerouslySetInnerHTML is used, which "
                    "explicitly bypasses React's built-in XSS protection by "
                    "inserting raw HTML into the DOM. The name itself is a "
                    "warning from the React team. If the __html value contains "
                    "user-controlled data that has not been sanitized, an "
                    "attacker can inject arbitrary JavaScript."
                ),
                0.85,
            )
        # document.write
        return (
            "XSS risk: document.write() inserts unescaped content into the DOM",
            (
                "The document.write() or document.writeln() function is called, "
                "which writes raw HTML content directly into the document. If "
                "the written content includes user input, an attacker can inject "
                "malicious scripts. Additionally, document.write() called after "
                "page load will overwrite the entire document."
            ),
            0.80,
        )

    @staticmethod
    def _xss_remediation(pattern_type: str) -> str:
        """Return pattern-specific remediation guidance for XSS findings.

        Args:
            pattern_type: The XSS pattern type string.

        Returns:
            Remediation guidance string.
        """
        if pattern_type == "innerHTML":
            return (
                "Replace innerHTML with textContent or innerText when "
                "inserting text content. If HTML insertion is required, "
                "sanitize the content first using DOMPurify: "
                "element.innerHTML = DOMPurify.sanitize(userInput). "
                "In React, use JSX expressions which auto-escape by default. "
                "Consider using the DOM API (createElement, appendChild) "
                "for dynamic content construction."
            )
        if pattern_type == "outerHTML":
            return (
                "Avoid using outerHTML with user-controlled data. Use "
                "textContent for text-only updates, or sanitize HTML with "
                "DOMPurify before assignment. Prefer DOM manipulation "
                "methods (createElement, replaceChild) over HTML string "
                "injection."
            )
        if pattern_type == "dangerouslySetInnerHTML":
            return (
                "Avoid dangerouslySetInnerHTML whenever possible. If raw "
                "HTML rendering is required (e.g., from a CMS or markdown "
                "renderer), always sanitize the HTML first using DOMPurify: "
                "dangerouslySetInnerHTML={{__html: DOMPurify.sanitize(html)}}. "
                "Consider using a markdown rendering library that produces "
                "React elements instead of raw HTML strings."
            )
        # document.write
        return (
            "Avoid document.write() entirely. Use DOM manipulation methods "
            "instead: document.createElement(), element.appendChild(), or "
            "element.textContent. In modern frameworks, use the framework's "
            "templating system which auto-escapes by default. If dynamic "
            "content insertion is needed, use textContent for text and "
            "DOMPurify.sanitize() for HTML."
        )
