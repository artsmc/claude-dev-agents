"""JavaScript/TypeScript security parser using regex-based analysis.

Provides a regex-based parser specialized for security vulnerability detection
in JavaScript and TypeScript source code. Extracts string literals (for secrets
detection), dangerous API usage patterns (eval, innerHTML, document.write),
and database query construction patterns (for injection detection).

This module uses only the Python standard library (re module) and has no
external dependencies. Unlike the PythonSecurityParser which uses AST analysis,
this parser operates via line-by-line regex matching since no JS/TS AST parser
is available in the Python stdlib.

Data structures:
    JSStringLiteral: A string constant found in JS/TS source code with context.
    DangerousPattern: A usage of a known-dangerous API or pattern.
    JSDBQuery: A database query construction pattern with injection risk flag.

Classes:
    JavaScriptSecurityParser: Main parser class orchestrating all extractions.

References:
    - TR.md Section 3.2: JavaScriptParser Extensions
    - OWASP A03:2021 Injection
    - OWASP A07:2021 Cross-Site Scripting (XSS)
    - CWE-79: Improper Neutralization of Input During Web Page Generation
    - CWE-89: SQL Injection
    - CWE-95: Eval Injection
"""

import logging
import re
from dataclasses import dataclass
from typing import List, Tuple

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------


@dataclass
class JSStringLiteral:
    """A string literal extracted from JavaScript/TypeScript source code.

    Used by the secrets analyzer to scan for hardcoded credentials, API keys,
    and other sensitive values embedded directly in source code.

    Attributes:
        value: The raw string value as it appears in the source code,
            excluding the surrounding quote characters.
        line_number: 1-based line number where the string appears.
        quote_type: The quoting style used: ``"single"``, ``"double"``,
            or ``"backtick"`` (template literal).
    """

    value: str
    line_number: int
    quote_type: str = "double"


@dataclass
class DangerousPattern:
    """A usage of a known-dangerous JavaScript/TypeScript API or pattern.

    Captures usage of APIs that introduce XSS, code injection, or other
    client-side vulnerabilities when used with untrusted input.

    Attributes:
        pattern_type: Category of dangerous pattern detected. One of:
            ``"eval"``, ``"Function_constructor"``, ``"innerHTML"``,
            ``"outerHTML"``, ``"dangerouslySetInnerHTML"``,
            ``"document.write"``.
        line_number: 1-based line number where the pattern appears.
        context: The full source line (stripped) where the pattern was
            detected, providing surrounding context for the finding.
    """

    pattern_type: str
    line_number: int
    context: str = ""


@dataclass
class JSDBQuery:
    """A database query construction pattern detected in JS/TS source code.

    Identifies how SQL queries are built in JavaScript ORM contexts,
    distinguishing between safe parameterized queries and unsafe string
    concatenation or template literal interpolation approaches.

    Attributes:
        query_pattern: The SQL-containing expression as it appears in
            source code. May be truncated for very long expressions.
        line_number: 1-based line number where the SQL construction appears.
        is_parametrized: True if the query uses parameterized placeholders
            (``?``, ``$1``, ``$2``, etc.) or bound parameters. False if the
            query is built via string concatenation or unsafe template
            literal interpolation.
    """

    query_pattern: str
    line_number: int
    is_parametrized: bool = False


# ---------------------------------------------------------------------------
# Regex patterns
# ---------------------------------------------------------------------------

# Matches single-line // comments (but not inside strings -- handled by
# checking position relative to string boundaries).
_LINE_COMMENT_PATTERN = re.compile(r"//.*$", re.MULTILINE)

# Matches block comments /* ... */ including multiline.
_BLOCK_COMMENT_PATTERN = re.compile(r"/\*[\s\S]*?\*/")

# Double-quoted strings: handles escaped quotes.
_DOUBLE_QUOTE_PATTERN = re.compile(r'"(?:[^"\\]|\\.)*"')

# Single-quoted strings: handles escaped quotes.
_SINGLE_QUOTE_PATTERN = re.compile(r"'(?:[^'\\]|\\.)*'")

# Template literals (backtick strings): handles escaped backticks.
# Note: this is a simplified pattern that works for single-line template
# literals and many multiline cases, but may not capture deeply nested
# template expressions with backticks inside.
_BACKTICK_PATTERN = re.compile(r"`(?:[^`\\]|\\.)*`", re.DOTALL)

# Dangerous pattern detectors.
_EVAL_PATTERN = re.compile(
    r"\beval\s*\(", re.MULTILINE
)
_FUNCTION_CONSTRUCTOR_PATTERN = re.compile(
    r"\bnew\s+Function\s*\(", re.MULTILINE
)
_INNERHTML_PATTERN = re.compile(
    r"\.innerHTML\s*=", re.MULTILINE
)
_OUTERHTML_PATTERN = re.compile(
    r"\.outerHTML\s*=", re.MULTILINE
)
_DANGEROUSLY_SET_PATTERN = re.compile(
    r"dangerouslySetInnerHTML", re.MULTILINE
)
_DOCUMENT_WRITE_PATTERN = re.compile(
    r"\bdocument\.write(?:ln)?\s*\(", re.MULTILINE
)

# SQL keywords indicating a query is being constructed.
_SQL_KEYWORDS_PATTERN = re.compile(
    r"\b(SELECT|INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|TRUNCATE|REPLACE|MERGE)\b",
    re.IGNORECASE,
)

# Parameterized query placeholders indicating safe usage.
_PARAM_PLACEHOLDER_PATTERN = re.compile(
    r"(\?\s*[,)]|\$\d+\b|:\w+)",
)

# Sequelize .query() with string concatenation (single-line).
_SEQUELIZE_QUERY_PATTERN = re.compile(
    r"""\.query\s*\(\s*(?:["'`][^"'`\n]*["'`]\s*\+|[^)\n]*\+\s*["'`])""",
)

# Prisma $queryRaw with template literal (tagged template).
_PRISMA_QUERY_RAW_PATTERN = re.compile(
    r"\.\$queryRaw\s*`", re.MULTILINE
)

# Prisma $queryRawUnsafe with any argument.
_PRISMA_QUERY_RAW_UNSAFE_PATTERN = re.compile(
    r"\.\$queryRawUnsafe\s*\(", re.MULTILINE
)

# Generic SQL string concatenation: "SELECT ... " + variable
_SQL_CONCAT_PATTERN = re.compile(
    r"""(?:["'`])(?:[^"'`]*?\b(?:SELECT|INSERT|UPDATE|DELETE)\b[^"'`]*?)(?:["'`])\s*\+""",
    re.IGNORECASE,
)

# SQL in template literal with interpolation: `SELECT ... ${...}`
_SQL_TEMPLATE_LITERAL_PATTERN = re.compile(
    r"""`[^`]*?\b(?:SELECT|INSERT|UPDATE|DELETE)\b[^`]*?\$\{[^}]+\}[^`]*?`""",
    re.IGNORECASE | re.DOTALL,
)

# Knex/generic .raw() with string concatenation (single-line).
_RAW_QUERY_CONCAT_PATTERN = re.compile(
    r"""\.raw\s*\(\s*(?:["'`][^"'`\n]*["'`]\s*\+|[^)\n]*\+\s*["'`])""",
)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _strip_comments(content: str) -> str:
    """Remove JavaScript comments from source content.

    Removes both single-line (``//``) and block (``/* */``) comments.
    This is a best-effort approach that handles most common cases. String
    literals containing comment-like sequences may be affected, but for
    security scanning purposes this is acceptable -- we err on the side
    of fewer false positives from comment content.

    Args:
        content: JavaScript/TypeScript source code as a string.

    Returns:
        Source code with comments replaced by whitespace to preserve
        line numbering.
    """
    # First remove block comments, preserving line count.
    def _replace_block_comment(match: re.Match) -> str:  # type: ignore[type-arg]
        text = match.group(0)
        # Preserve newlines so line numbering stays correct.
        return "\n" * text.count("\n")

    result = _BLOCK_COMMENT_PATTERN.sub(_replace_block_comment, content)
    # Then remove line comments.
    result = _LINE_COMMENT_PATTERN.sub("", result)
    return result


def _line_number_at_offset(content: str, offset: int) -> int:
    """Calculate the 1-based line number for a character offset.

    Args:
        content: The full source string.
        offset: 0-based character offset within *content*.

    Returns:
        1-based line number corresponding to the offset.
    """
    return content[:offset].count("\n") + 1


def _unescape_js_string(value: str) -> str:
    """Unescape common JavaScript string escape sequences.

    Handles ``\\n``, ``\\t``, ``\\r``, ``\\\"``, ``\\'``, ``\\\\``,
    and ``\\` `` (backtick). Does NOT handle unicode escapes (``\\uXXXX``)
    or hex escapes (``\\xHH``) as those are rarely relevant for
    secrets detection.

    Args:
        value: The raw string content between quotes.

    Returns:
        String with common escape sequences resolved.
    """
    replacements = [
        ("\\\\", "\x00BACKSLASH\x00"),  # Temporary placeholder
        ('\\"', '"'),
        ("\\'", "'"),
        ("\\`", "`"),
        ("\\n", "\n"),
        ("\\t", "\t"),
        ("\\r", "\r"),
    ]
    result = value
    for old, new in replacements:
        result = result.replace(old, new)
    result = result.replace("\x00BACKSLASH\x00", "\\")
    return result


def _context_for_line(lines: List[str], lineno: int) -> str:
    """Return the source line at *lineno* (1-based), stripped.

    Args:
        lines: List of source lines.
        lineno: 1-based line number.

    Returns:
        The stripped line content, or an empty string if the line number
        is out of range.
    """
    idx = lineno - 1
    if 0 <= idx < len(lines):
        return lines[idx].strip()
    return ""


# ---------------------------------------------------------------------------
# Main parser class
# ---------------------------------------------------------------------------


class JavaScriptSecurityParser:
    """JavaScript/TypeScript source code parser specialized for security analysis.

    Uses Python's built-in ``re`` module to scan JavaScript and TypeScript
    source code for security-relevant patterns including string literals,
    dangerous API usage, and database query construction patterns.

    This parser is intentionally independent of any JavaScript AST parser
    and operates entirely via regex-based line and content scanning. It
    handles both ``.js`` and ``.ts`` files identically.

    Usage::

        parser = JavaScriptSecurityParser()
        content = open("app.js").read()
        strings = parser.extract_string_literals(content)
        dangerous = parser.extract_dangerous_patterns(content)
        queries = parser.extract_database_queries(content)

    All extraction methods are safe to call independently and will not raise
    exceptions for any input string. Malformed or empty input returns empty
    lists.

    Attributes:
        logger: Logger instance for diagnostic messages.
    """

    def __init__(self) -> None:
        """Initialize the JavaScript security parser."""
        self.logger = logging.getLogger(self.__class__.__name__)

    def extract_string_literals(self, content: str) -> List[JSStringLiteral]:
        """Extract all string literals from JavaScript/TypeScript source code.

        Scans source code for single-quoted, double-quoted, and backtick
        (template literal) strings. Comments are stripped before extraction
        to avoid false positives from commented-out code.

        Handles escaped quotes within strings. Template literals with
        ``${...}`` interpolation are captured as-is (the interpolation
        expressions remain in the extracted value).

        Args:
            content: JavaScript/TypeScript source code as a string.

        Returns:
            List of ``JSStringLiteral`` instances, one per string literal
            found in the source code. Each contains the unescaped string
            value (without surrounding quotes), the 1-based line number,
            and the quote type (``"single"``, ``"double"``, or
            ``"backtick"``).

        Example:
            >>> parser = JavaScriptSecurityParser()
            >>> literals = parser.extract_string_literals('const key = "sk-live-abc";')
            >>> literals[0].value
            'sk-live-abc'
            >>> literals[0].quote_type
            'double'
        """
        if not content or not content.strip():
            return []

        cleaned = _strip_comments(content)
        literals: List[JSStringLiteral] = []

        # Process each quote type with its corresponding pattern and label.
        quote_configs: List[Tuple[re.Pattern, str]] = [  # type: ignore[type-arg]
            (_DOUBLE_QUOTE_PATTERN, "double"),
            (_SINGLE_QUOTE_PATTERN, "single"),
            (_BACKTICK_PATTERN, "backtick"),
        ]

        for pattern, quote_type in quote_configs:
            for match in pattern.finditer(cleaned):
                raw = match.group(0)
                # Strip surrounding quote characters.
                inner = raw[1:-1]
                value = _unescape_js_string(inner)

                # Skip empty strings -- not useful for secrets detection.
                if not value.strip():
                    continue

                line_num = _line_number_at_offset(cleaned, match.start())
                literals.append(
                    JSStringLiteral(
                        value=value,
                        line_number=line_num,
                        quote_type=quote_type,
                    )
                )

        # Sort by line number for deterministic output.
        literals.sort(key=lambda lit: (lit.line_number, lit.value))
        return literals

    def extract_dangerous_patterns(self, content: str) -> List[DangerousPattern]:
        """Extract dangerous JavaScript/TypeScript API usage patterns.

        Scans source code for patterns known to introduce security
        vulnerabilities when used with untrusted input:

        **Code injection:**
            ``eval(expr)`` -- arbitrary code execution.
            ``new Function(code)`` -- dynamic function creation.

        **Cross-site scripting (XSS):**
            ``element.innerHTML = ...`` -- unescaped HTML insertion.
            ``element.outerHTML = ...`` -- unescaped HTML replacement.
            ``dangerouslySetInnerHTML`` -- React's explicit XSS bypass.
            ``document.write(html)`` -- direct DOM manipulation.

        Comments are stripped before scanning to avoid false positives
        from commented-out code.

        Args:
            content: JavaScript/TypeScript source code as a string.

        Returns:
            List of ``DangerousPattern`` instances. Each contains the
            pattern type string, the 1-based line number, and the full
            source line (stripped) as context.

        Example:
            >>> parser = JavaScriptSecurityParser()
            >>> patterns = parser.extract_dangerous_patterns('eval(userInput);')
            >>> patterns[0].pattern_type
            'eval'
            >>> patterns[0].line_number
            1
        """
        if not content or not content.strip():
            return []

        cleaned = _strip_comments(content)
        lines = cleaned.splitlines()
        results: List[DangerousPattern] = []

        # Each tuple: (compiled_pattern, pattern_type_label)
        detectors: List[Tuple[re.Pattern, str]] = [  # type: ignore[type-arg]
            (_EVAL_PATTERN, "eval"),
            (_FUNCTION_CONSTRUCTOR_PATTERN, "Function_constructor"),
            (_INNERHTML_PATTERN, "innerHTML"),
            (_OUTERHTML_PATTERN, "outerHTML"),
            (_DANGEROUSLY_SET_PATTERN, "dangerouslySetInnerHTML"),
            (_DOCUMENT_WRITE_PATTERN, "document.write"),
        ]

        for pattern, pattern_type in detectors:
            for match in pattern.finditer(cleaned):
                line_num = _line_number_at_offset(cleaned, match.start())
                ctx = _context_for_line(lines, line_num)
                results.append(
                    DangerousPattern(
                        pattern_type=pattern_type,
                        line_number=line_num,
                        context=ctx,
                    )
                )

        # Sort by line number for deterministic output.
        results.sort(key=lambda dp: (dp.line_number, dp.pattern_type))
        return results

    def extract_database_queries(self, content: str) -> List[JSDBQuery]:
        """Extract database query construction patterns from JS/TS source code.

        Detects several categories of SQL query construction in common
        JavaScript ORMs and raw query approaches:

        **Sequelize raw queries:**
            ``sequelize.query("SELECT * FROM " + table)``

        **Prisma raw queries:**
            ``prisma.$queryRaw`SELECT * FROM users WHERE id = ${id}```
            ``prisma.$queryRawUnsafe(query)``

        **Knex/generic raw queries:**
            ``knex.raw("SELECT * FROM " + table)``

        **String concatenation with SQL:**
            ``"SELECT * FROM users WHERE id = " + userId``

        **Template literals with SQL and interpolation:**
            ```SELECT * FROM users WHERE id = ${userId}```

        Queries are classified as parameterized (safe) when they use
        placeholders like ``?``, ``$1``, ``$2``, ``:name``, or when the
        ORM method signature implies parameter binding.

        Comments are stripped before scanning.

        Args:
            content: JavaScript/TypeScript source code as a string.

        Returns:
            List of ``JSDBQuery`` instances. Each contains the query
            pattern (truncated to 300 characters), the 1-based line number,
            and a boolean ``is_parametrized`` flag.

        Example:
            >>> parser = JavaScriptSecurityParser()
            >>> code = 'db.query("SELECT * FROM users WHERE id = " + userId)'
            >>> queries = parser.extract_database_queries(code)
            >>> queries[0].is_parametrized
            False
        """
        if not content or not content.strip():
            return []

        cleaned = _strip_comments(content)
        # Collect findings keyed by line number. When multiple detectors
        # match the same line, keep the longest pattern text (most context)
        # and preserve the is_parametrized flag if any detector marks it safe.
        by_line: dict[int, JSDBQuery] = {}

        def _add_finding(
            match_text: str,
            offset: int,
            is_parametrized: bool,
        ) -> None:
            """Record a query finding, deduplicating by line number.

            When multiple detectors fire on the same line, the finding
            with the longest pattern text is kept. If any detector marks
            the line as parameterized, that flag is preserved.
            """
            line_num = _line_number_at_offset(cleaned, offset)
            # Truncate long patterns.
            pattern_text = match_text.strip()
            if len(pattern_text) > 300:
                pattern_text = pattern_text[:297] + "..."

            # Override: check for param placeholders in the pattern itself.
            if _PARAM_PLACEHOLDER_PATTERN.search(pattern_text):
                is_parametrized = True

            existing = by_line.get(line_num)
            if existing is None:
                by_line[line_num] = JSDBQuery(
                    query_pattern=pattern_text,
                    line_number=line_num,
                    is_parametrized=is_parametrized,
                )
            else:
                # Keep the longest pattern for better context.
                if len(pattern_text) > len(existing.query_pattern):
                    existing.query_pattern = pattern_text
                # Preserve parameterized flag if any detector marks it safe.
                if is_parametrized:
                    existing.is_parametrized = True

        # --- Detector 1: Sequelize .query() with concatenation ---
        for match in _SEQUELIZE_QUERY_PATTERN.finditer(cleaned):
            _add_finding(match.group(0), match.start(), False)

        # --- Detector 2: Prisma $queryRaw with template literal ---
        # $queryRaw`...` uses tagged template literals which ARE safe
        # (Prisma auto-parameterizes tagged templates). But $queryRaw(...)
        # with a string argument is NOT safe.
        for match in _PRISMA_QUERY_RAW_PATTERN.finditer(cleaned):
            # Tagged template literal -- Prisma parameterizes these.
            _add_finding(match.group(0), match.start(), True)

        # --- Detector 3: Prisma $queryRawUnsafe ---
        for match in _PRISMA_QUERY_RAW_UNSAFE_PATTERN.finditer(cleaned):
            _add_finding(match.group(0), match.start(), False)

        # --- Detector 4: Knex/generic .raw() with concatenation ---
        for match in _RAW_QUERY_CONCAT_PATTERN.finditer(cleaned):
            _add_finding(match.group(0), match.start(), False)

        # --- Detector 5: SQL string concatenation ---
        for match in _SQL_CONCAT_PATTERN.finditer(cleaned):
            _add_finding(match.group(0), match.start(), False)

        # --- Detector 6: SQL in template literal with interpolation ---
        for match in _SQL_TEMPLATE_LITERAL_PATTERN.finditer(cleaned):
            text = match.group(0)
            # If the template literal contains ${...} with SQL, it is
            # likely an injection risk UNLESS parameterized placeholders
            # are also present.
            _add_finding(text, match.start(), False)

        # --- Detector 7: Line-by-line scan for .query() / .execute() ---
        # Catch remaining patterns that don't match the above.
        self._scan_query_method_calls(cleaned, by_line)

        # Collect results from the line-keyed dict and sort.
        results = list(by_line.values())
        results.sort(key=lambda q: (q.line_number, q.query_pattern))
        return results

    def _scan_query_method_calls(
        self,
        content: str,
        by_line: dict[int, JSDBQuery],
    ) -> None:
        """Scan for .query() and .execute() calls containing SQL keywords.

        This is a supplementary line-by-line scanner that catches patterns
        not covered by the primary regex detectors, such as:

        - ``db.query("SELECT * FROM users WHERE id = ?", [userId])``
        - ``connection.execute(`SELECT ... WHERE id = ${id}`)``

        Args:
            content: Comment-stripped source code.
            by_line: Dict of line_number -> JSDBQuery for deduplication
                and merging (mutated in place).
        """
        # Pattern for method calls that typically execute SQL.
        query_method_pattern = re.compile(
            r"\.(?:query|execute)\s*\(",
            re.MULTILINE,
        )

        # Pre-compile the second-argument detection pattern.
        second_arg_pattern = re.compile(
            r"""\.(?:query|execute)\s*\(\s*(?:["'`].*?["'`]|[^,)]+)\s*,""",
            re.DOTALL,
        )

        lines = content.splitlines()
        for i, line in enumerate(lines):
            line_num = i + 1
            stripped = line.strip()

            # Skip lines without query/execute method calls.
            if not query_method_pattern.search(stripped):
                continue

            # Check if the line contains SQL keywords.
            if not _SQL_KEYWORDS_PATTERN.search(stripped):
                continue

            # Truncate for pattern storage.
            pattern_text = stripped
            if len(pattern_text) > 300:
                pattern_text = pattern_text[:297] + "..."

            # Determine parameterization.
            is_param = bool(_PARAM_PLACEHOLDER_PATTERN.search(stripped))

            # Also check for a second argument (array of params).
            # Pattern: .query("...", [...]) or .query("...", params)
            if second_arg_pattern.search(stripped):
                is_param = True

            existing = by_line.get(line_num)
            if existing is None:
                by_line[line_num] = JSDBQuery(
                    query_pattern=pattern_text,
                    line_number=line_num,
                    is_parametrized=is_param,
                )
            else:
                # Keep the longest pattern for better context.
                if len(pattern_text) > len(existing.query_pattern):
                    existing.query_pattern = pattern_text
                # Preserve parameterized flag.
                if is_param:
                    existing.is_parametrized = True
