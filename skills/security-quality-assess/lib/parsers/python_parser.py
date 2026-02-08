"""Python security parser using AST analysis.

Provides an AST-based parser specialized for security vulnerability detection
in Python source code. Extracts string literals (for secrets detection),
dangerous function calls (eval/exec/subprocess/os.system/pickle), SQL query
construction patterns (for injection detection), and function decorators
(for authentication gap analysis).

This module uses only the Python standard library (ast module) and has no
external dependencies.

Data structures:
    StringLiteral: A string constant found in source code with context.
    DangerousCall: A call to a known-dangerous function.
    SQLQuery: A SQL query construction pattern with injection risk flag.

Classes:
    PythonSecurityParser: Main parser class orchestrating all extractions.

References:
    - TR.md Section 3.1: PythonParser Extensions
    - OWASP A03:2021 Injection
    - OWASP A02:2021 Cryptographic Failures (secrets in code)
    - CWE-78: OS Command Injection
    - CWE-89: SQL Injection
    - CWE-798: Use of Hard-coded Credentials
"""

import ast
import logging
import re
from dataclasses import dataclass
from typing import List, Optional, Sequence, Tuple

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------


@dataclass
class StringLiteral:
    """A string literal extracted from Python source code.

    Used by the secrets analyzer to scan for hardcoded credentials, API keys,
    and other sensitive values embedded directly in source code.

    Attributes:
        value: The raw string value as it appears in the source code.
        line_number: 1-based line number where the string appears.
        context: Surrounding source lines (typically the line itself plus
            one line above and below) to help classify the string. Empty
            string when source lines are unavailable.
    """

    value: str
    line_number: int
    context: str = ""


@dataclass
class DangerousCall:
    """A call to a function known to be dangerous from a security perspective.

    Captures calls to functions such as ``eval``, ``exec``, ``os.system``,
    ``subprocess.call`` with ``shell=True``, and ``pickle.loads``. These
    represent potential command injection, code injection, or deserialization
    vulnerabilities.

    Attributes:
        function_name: Fully qualified function name as it appears in the
            source code (e.g., "eval", "subprocess.call", "os.system").
        line_number: 1-based line number where the call appears.
        arguments: String representation of the call arguments. Truncated
            to a reasonable length for reporting purposes.
        has_shell_true: True if the call includes ``shell=True`` as a
            keyword argument. Only relevant for subprocess calls.
    """

    function_name: str
    line_number: int
    arguments: str = ""
    has_shell_true: bool = False


@dataclass
class SQLQuery:
    """A SQL query construction pattern detected in source code.

    Identifies how SQL queries are built, distinguishing between safe
    parameterized queries and unsafe string-concatenation or formatting
    approaches that are vulnerable to SQL injection.

    Attributes:
        query_pattern: The SQL-containing expression as it appears in
            source code. May be truncated for very long expressions.
        line_number: 1-based line number where the SQL construction appears.
        is_parametrized: True if the query uses parameterized placeholders
            (``?``, ``%s``, ``:name``). False if the query is built via
            string concatenation, f-strings, or ``.format()`` calls.
    """

    query_pattern: str
    line_number: int
    is_parametrized: bool = False


# ---------------------------------------------------------------------------
# Internal AST visitors
# ---------------------------------------------------------------------------

# SQL keywords that indicate a query is being constructed.
_SQL_KEYWORDS_PATTERN = re.compile(
    r"\b(SELECT|INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|TRUNCATE|REPLACE|MERGE)\b",
    re.IGNORECASE,
)

# Parameterized query placeholders indicating safe usage.
_PARAM_PLACEHOLDER_PATTERN = re.compile(
    r"(\?\s*[,)]|%s\b|:\w+)",
)

# Set of built-in dangerous function names (unqualified).
_DANGEROUS_BUILTINS = frozenset({"eval", "exec", "compile"})

# Mapping of module-qualified dangerous function names.
# Key is (module_attr_chain), e.g. ("subprocess", "call").
_DANGEROUS_QUALIFIED: dict[Tuple[str, ...], str] = {
    ("subprocess", "call"): "subprocess.call",
    ("subprocess", "run"): "subprocess.run",
    ("subprocess", "Popen"): "subprocess.Popen",
    ("os", "system"): "os.system",
    ("os", "popen"): "os.popen",
    ("pickle", "loads"): "pickle.loads",
    ("pickle", "load"): "pickle.load",
}


class _StringLiteralVisitor(ast.NodeVisitor):
    """AST visitor that collects all string literal nodes.

    Handles both ``ast.Constant`` (Python 3.8+) and the deprecated
    ``ast.Str`` (Python < 3.12) for broad compatibility.
    """

    def __init__(self, source_lines: Sequence[str]) -> None:
        self.source_lines = source_lines
        self.literals: List[StringLiteral] = []

    # -- helpers --

    def _context_for_line(self, lineno: int) -> str:
        """Return up to 3 lines of context centered on *lineno* (1-based)."""
        if not self.source_lines:
            return ""
        idx = lineno - 1  # Convert to 0-based.
        start = max(0, idx - 1)
        end = min(len(self.source_lines), idx + 2)
        return "\n".join(self.source_lines[start:end])

    def _record(self, value: str, lineno: int) -> None:
        """Store a string literal if it has a usable line number."""
        if lineno < 1:
            return
        self.literals.append(
            StringLiteral(
                value=value,
                line_number=lineno,
                context=self._context_for_line(lineno),
            )
        )

    # -- visitor methods --

    def visit_Constant(self, node: ast.Constant) -> None:
        """Visit ast.Constant nodes (Python 3.8+).

        Only records nodes whose value is a ``str`` instance, skipping
        numeric constants, bytes, booleans, and None.
        """
        if isinstance(node.value, str):
            lineno = getattr(node, "lineno", 0) or 0
            self._record(node.value, lineno)
        self.generic_visit(node)

    # Python < 3.12 compatibility: ast.Str is deprecated but may still
    # appear when parsing with older AST versions.
    def visit_Str(self, node: ast.Str) -> None:  # type: ignore[attr-defined]
        """Visit deprecated ast.Str nodes for backward compatibility."""
        lineno = getattr(node, "lineno", 0) or 0
        self._record(node.s, lineno)
        self.generic_visit(node)


class _DangerousCallVisitor(ast.NodeVisitor):
    """AST visitor that detects calls to dangerous functions.

    Dangerous functions fall into four categories:
    1. Code execution: ``eval``, ``exec``, ``compile``
    2. OS command execution: ``os.system``, ``os.popen``
    3. Subprocess with shell: ``subprocess.call/run/Popen`` (especially
       with ``shell=True``)
    4. Unsafe deserialization: ``pickle.load``, ``pickle.loads``
    """

    def __init__(self) -> None:
        self.calls: List[DangerousCall] = []

    @staticmethod
    def _unparse_safe(node: ast.AST) -> str:
        """Unparse an AST node to source, returning '<complex>' on failure."""
        try:
            return ast.unparse(node)
        except Exception:
            return "<complex>"

    @staticmethod
    def _resolve_attribute_chain(node: ast.Attribute) -> Optional[Tuple[str, ...]]:
        """Resolve a dotted attribute chain like ``subprocess.call``.

        Returns a tuple of name parts, e.g. ``("subprocess", "call")``,
        or ``None`` if the chain cannot be fully resolved (e.g., it
        involves function calls or subscripts).
        """
        parts: list[str] = []
        current: ast.expr = node
        while isinstance(current, ast.Attribute):
            parts.append(current.attr)
            current = current.value
        if isinstance(current, ast.Name):
            parts.append(current.id)
            parts.reverse()
            return tuple(parts)
        return None

    @staticmethod
    def _has_shell_true(call_node: ast.Call) -> bool:
        """Check if a Call node includes the keyword argument ``shell=True``."""
        for kw in call_node.keywords:
            if kw.arg == "shell":
                if isinstance(kw.value, ast.Constant) and kw.value.value is True:
                    return True
                # Also handle ast.NameConstant for older Python ASTs
                if isinstance(kw.value, ast.NameConstant):  # type: ignore[attr-defined]
                    return kw.value.value is True  # type: ignore[attr-defined]
        return False

    def _format_arguments(self, call_node: ast.Call) -> str:
        """Build a human-readable argument summary for a call, truncated."""
        parts: list[str] = []
        for arg in call_node.args:
            parts.append(self._unparse_safe(arg))
        for kw in call_node.keywords:
            key = kw.arg if kw.arg else "**"
            parts.append(f"{key}={self._unparse_safe(kw.value)}")
        text = ", ".join(parts)
        if len(text) > 200:
            text = text[:197] + "..."
        return text

    def visit_Call(self, node: ast.Call) -> None:
        """Visit every Call node and check against dangerous function lists."""
        lineno = getattr(node, "lineno", 0) or 0

        # -- Case 1: simple name calls (eval, exec, compile) --
        if isinstance(node.func, ast.Name):
            if node.func.id in _DANGEROUS_BUILTINS:
                self.calls.append(
                    DangerousCall(
                        function_name=node.func.id,
                        line_number=lineno,
                        arguments=self._format_arguments(node),
                        has_shell_true=False,
                    )
                )

        # -- Case 2: dotted attribute calls (os.system, subprocess.call, ...) --
        elif isinstance(node.func, ast.Attribute):
            chain = self._resolve_attribute_chain(node.func)
            if chain is not None:
                # Check the last 2 elements (module.func) against registry.
                if len(chain) >= 2:
                    key = (chain[-2], chain[-1])
                    if key in _DANGEROUS_QUALIFIED:
                        func_name = _DANGEROUS_QUALIFIED[key]
                        shell_true = self._has_shell_true(node)
                        self.calls.append(
                            DangerousCall(
                                function_name=func_name,
                                line_number=lineno,
                                arguments=self._format_arguments(node),
                                has_shell_true=shell_true,
                            )
                        )

        self.generic_visit(node)


class _SQLQueryVisitor(ast.NodeVisitor):
    """AST visitor that detects SQL query construction patterns.

    Identifies three dangerous patterns:
    1. String concatenation: ``"SELECT * FROM " + table_name``
    2. F-strings: ``f"SELECT * FROM {table}"``
    3. Format calls: ``"SELECT ... {}".format(table)``

    Also identifies safe parameterized usage when placeholders like
    ``?``, ``%s``, or ``:name`` are present.
    """

    def __init__(self) -> None:
        self.queries: List[SQLQuery] = []

    @staticmethod
    def _contains_sql(text: str) -> bool:
        """Check if text contains SQL keywords."""
        return bool(_SQL_KEYWORDS_PATTERN.search(text))

    @staticmethod
    def _is_parametrized(text: str) -> bool:
        """Check if text uses parameterized query placeholders."""
        return bool(_PARAM_PLACEHOLDER_PATTERN.search(text))

    @staticmethod
    def _unparse_safe(node: ast.AST) -> str:
        """Unparse an AST node to source, returning '' on failure."""
        try:
            return ast.unparse(node)
        except Exception:
            return ""

    def _extract_string_value(self, node: ast.expr) -> Optional[str]:
        """Extract a plain string value from a Constant or Str node."""
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            return node.value
        # Backward compatibility
        if isinstance(node, ast.Str):  # type: ignore[attr-defined]
            return node.s  # type: ignore[attr-defined]
        return None

    def _check_and_record(
        self,
        text: str,
        lineno: int,
        is_parametrized: bool,
    ) -> bool:
        """Record a SQLQuery if *text* contains SQL keywords. Returns True if recorded."""
        if self._contains_sql(text):
            # Override: if the string itself has param placeholders, mark safe.
            if self._is_parametrized(text):
                is_parametrized = True
            self.queries.append(
                SQLQuery(
                    query_pattern=text[:300] if len(text) > 300 else text,
                    line_number=lineno,
                    is_parametrized=is_parametrized,
                )
            )
            return True
        return False

    # -- Visitor methods --

    def visit_BinOp(self, node: ast.BinOp) -> None:
        """Detect string concatenation with SQL keywords.

        Matches patterns like::

            "SELECT * FROM " + table_name
            query = base + " WHERE id = " + str(user_id)
        """
        if isinstance(node.op, ast.Add):
            lineno = getattr(node, "lineno", 0) or 0
            # Try to get string value from either side of the +
            left_str = self._extract_string_value(node.left)
            right_str = self._extract_string_value(node.right)

            if left_str is not None and self._contains_sql(left_str):
                pattern = self._unparse_safe(node)
                self._check_and_record(pattern or left_str, lineno, False)
            elif right_str is not None and self._contains_sql(right_str):
                pattern = self._unparse_safe(node)
                self._check_and_record(pattern or right_str, lineno, False)

        self.generic_visit(node)

    def visit_JoinedStr(self, node: ast.JoinedStr) -> None:
        """Detect f-strings containing SQL keywords.

        Matches patterns like::

            f"SELECT * FROM {table} WHERE id = {user_id}"
        """
        lineno = getattr(node, "lineno", 0) or 0
        # Reconstruct the f-string content from its values.
        parts: list[str] = []
        has_expressions = False
        for value in node.values:
            s = self._extract_string_value(value)
            if s is not None:
                parts.append(s)
            elif isinstance(value, ast.FormattedValue):
                has_expressions = True
                parts.append("{...}")
            else:
                parts.append("{...}")

        combined = "".join(parts)
        if self._contains_sql(combined) and has_expressions:
            # F-string with SQL and interpolated expressions => not parametrized
            self._check_and_record(combined, lineno, False)

        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        """Detect ``.format()`` calls on strings containing SQL keywords.

        Matches patterns like::

            "SELECT * FROM {} WHERE id = {}".format(table, user_id)
            query_template.format(table_name=table)
        """
        if isinstance(node.func, ast.Attribute) and node.func.attr == "format":
            # Check if the object being formatted is a string with SQL.
            obj = node.func.value
            obj_str = self._extract_string_value(obj)
            if obj_str is not None and self._contains_sql(obj_str):
                lineno = getattr(node, "lineno", 0) or 0
                self._check_and_record(obj_str, lineno, False)

        # Also detect cursor.execute("SELECT " + ...) style calls where
        # the first argument is a string with SQL and parameterized placeholders.
        if isinstance(node.func, ast.Attribute) and node.func.attr == "execute":
            if node.args:
                first_arg = node.args[0]
                first_str = self._extract_string_value(first_arg)
                if first_str is not None and self._contains_sql(first_str):
                    lineno = getattr(node, "lineno", 0) or 0
                    # If there are additional args (params tuple), it is likely
                    # parametrized. Also check for placeholders in the string.
                    is_param = (
                        len(node.args) > 1 or self._is_parametrized(first_str)
                    )
                    self._check_and_record(first_str, lineno, is_param)

        self.generic_visit(node)

    def visit_Constant(self, node: ast.Constant) -> None:
        """Detect standalone string constants containing SQL keywords.

        Catches simple assignments like::

            query = "SELECT * FROM users WHERE id = " + user_id

        The concatenation case is handled by visit_BinOp; this catches
        standalone parametrized queries that are not concatenated, such as::

            cursor.execute("SELECT * FROM users WHERE id = ?", (uid,))

        We do NOT flag standalone SQL strings as findings here since they
        are typically safe (parametrized or template literals). They are
        flagged only if they appear in a concatenation, f-string, or
        .format() context (handled by other visitors).
        """
        # No action for standalone constants -- handled by other visitors.
        self.generic_visit(node)


# ---------------------------------------------------------------------------
# Main parser class
# ---------------------------------------------------------------------------


class PythonSecurityParser:
    """Python source code parser specialized for security analysis.

    Uses Python's built-in ``ast`` module to parse source code into an
    abstract syntax tree, then applies specialized AST visitors to extract
    security-relevant patterns including string literals, dangerous function
    calls, SQL query constructions, and function decorators.

    This parser is intentionally independent of the architecture-quality-assess
    PythonParser to avoid cross-skill dependencies. It operates on raw source
    code strings and parsed AST trees.

    Usage::

        parser = PythonSecurityParser()
        tree, lines = parser.parse("source code here")
        if tree is not None:
            strings = parser.extract_string_literals(tree, lines)
            dangerous = parser.extract_dangerous_calls(tree)
            sql = parser.extract_sql_queries(tree)

    All extraction methods are safe to call independently and will not raise
    exceptions for valid AST trees.
    """

    def __init__(self) -> None:
        """Initialize the security parser."""
        self.logger = logging.getLogger(self.__class__.__name__)

    def parse(
        self, source: str, filename: str = "<string>"
    ) -> Tuple[Optional[ast.AST], List[str]]:
        """Parse Python source code into an AST and source line list.

        Args:
            source: Python source code as a string.
            filename: Optional filename for error messages. Defaults to
                ``"<string>"``.

        Returns:
            A 2-tuple of ``(tree, source_lines)`` where *tree* is the parsed
            ``ast.Module`` node (or ``None`` if parsing failed) and
            *source_lines* is the list of individual source lines.

        Note:
            This method never raises exceptions. Syntax errors are logged
            as warnings and result in a ``None`` tree.
        """
        source_lines = source.splitlines()
        try:
            tree = ast.parse(source, filename=filename)
            return tree, source_lines
        except SyntaxError as exc:
            self.logger.warning(
                "Syntax error in %s at line %s: %s",
                filename,
                exc.lineno,
                exc.msg,
            )
            return None, source_lines

    def extract_string_literals(
        self,
        tree: ast.AST,
        source_lines: Optional[Sequence[str]] = None,
    ) -> List[StringLiteral]:
        """Extract all string literals from a parsed AST.

        Walks the AST to find every string constant, recording its value,
        line number, and surrounding source context. Used by the secrets
        analyzer to scan for hardcoded credentials.

        Handles both ``ast.Constant`` (Python 3.8+) and the deprecated
        ``ast.Str`` node type for backward compatibility.

        Args:
            tree: A parsed AST tree (typically from ``ast.parse()`` or
                ``self.parse()``).
            source_lines: Optional sequence of source code lines for context
                extraction. When provided, each ``StringLiteral.context``
                will contain up to 3 lines centered on the string's location.

        Returns:
            List of ``StringLiteral`` instances, one per string constant
            found in the source code. Strings without valid line numbers
            (lineno < 1) are silently excluded.

        Example:
            >>> parser = PythonSecurityParser()
            >>> tree, lines = parser.parse('API_KEY = "sk-live-abc123"')
            >>> literals = parser.extract_string_literals(tree, lines)
            >>> literals[0].value
            'sk-live-abc123'
        """
        visitor = _StringLiteralVisitor(source_lines or [])
        visitor.visit(tree)
        return visitor.literals

    def extract_dangerous_calls(self, tree: ast.AST) -> List[DangerousCall]:
        """Extract calls to dangerous functions from a parsed AST.

        Detects the following categories of dangerous calls:

        **Code execution:**
            ``eval()``, ``exec()``, ``compile()``

        **OS command execution:**
            ``os.system()``, ``os.popen()``

        **Subprocess with shell:**
            ``subprocess.call()``, ``subprocess.run()``,
            ``subprocess.Popen()`` -- especially when ``shell=True``

        **Unsafe deserialization:**
            ``pickle.load()``, ``pickle.loads()``

        Args:
            tree: A parsed AST tree.

        Returns:
            List of ``DangerousCall`` instances. Each entry includes the
            fully qualified function name, line number, a string summary
            of the arguments (truncated to 200 characters), and whether
            ``shell=True`` was detected as a keyword argument.

        Example:
            >>> parser = PythonSecurityParser()
            >>> tree, _ = parser.parse('import os; os.system("rm -rf /")')
            >>> calls = parser.extract_dangerous_calls(tree)
            >>> calls[0].function_name
            'os.system'
        """
        visitor = _DangerousCallVisitor()
        visitor.visit(tree)
        return visitor.calls

    def extract_sql_queries(self, tree: ast.AST) -> List[SQLQuery]:
        """Extract SQL query construction patterns from a parsed AST.

        Detects three categories of SQL construction that may indicate
        injection vulnerabilities:

        **String concatenation:**
            ``"SELECT * FROM " + table_name``

        **F-strings:**
            ``f"SELECT * FROM {table}"``

        **Format strings:**
            ``"SELECT * FROM {}".format(table)``

        Also detects safe parameterized queries when placeholders such as
        ``?``, ``%s``, or ``:name`` are present.

        Args:
            tree: A parsed AST tree.

        Returns:
            List of ``SQLQuery`` instances. Each entry includes the query
            pattern (truncated to 300 characters), the line number, and
            a boolean ``is_parametrized`` flag indicating whether safe
            parameterization was detected.

        Example:
            >>> parser = PythonSecurityParser()
            >>> code = 'query = "SELECT * FROM " + table'
            >>> tree, _ = parser.parse(code)
            >>> queries = parser.extract_sql_queries(tree)
            >>> queries[0].is_parametrized
            False
        """
        visitor = _SQLQueryVisitor()
        visitor.visit(tree)
        return visitor.queries

    def extract_decorators(
        self, func_node: ast.FunctionDef
    ) -> List[str]:
        """Extract decorator names from a function definition node.

        Resolves both simple decorators (``@login_required``) and dotted
        decorators (``@auth.requires_login``). Decorators that are call
        expressions (``@app.route("/path")``) are resolved to the callable
        name, discarding arguments.

        Used by the authentication analyzer to detect functions missing
        required decorators such as ``@login_required``, ``@authenticated``,
        or ``@permission_required``.

        Args:
            func_node: An ``ast.FunctionDef`` or ``ast.AsyncFunctionDef``
                AST node.

        Returns:
            List of decorator name strings. Dotted names are preserved as-is
            (e.g., ``"auth.requires_login"``). Decorators that cannot be
            resolved to a name (e.g., complex expressions) are represented
            as ``"<complex>"``.

        Example:
            >>> import ast
            >>> code = '''
            ... @login_required
            ... @app.route("/api/data")
            ... def get_data():
            ...     pass
            ... '''
            >>> tree = ast.parse(code)
            >>> func = tree.body[0]
            >>> parser = PythonSecurityParser()
            >>> parser.extract_decorators(func)
            ['login_required', 'app.route']
        """
        decorators: List[str] = []

        for decorator in func_node.decorator_list:
            name = self._resolve_decorator_name(decorator)
            decorators.append(name)

        return decorators

    def extract_all_function_decorators(
        self, tree: ast.AST
    ) -> List[Tuple[str, int, List[str]]]:
        """Extract decorators from all function definitions in the AST.

        Convenience method that walks the entire AST and returns decorator
        information for every function and method definition.

        Args:
            tree: A parsed AST tree.

        Returns:
            List of 3-tuples ``(function_name, line_number, decorators)``
            where *decorators* is the list of decorator name strings.

        Example:
            >>> parser = PythonSecurityParser()
            >>> code = '''
            ... @login_required
            ... def view(): pass
            ...
            ... def unprotected(): pass
            ... '''
            >>> tree, _ = parser.parse(code)
            >>> results = parser.extract_all_function_decorators(tree)
            >>> results[0]
            ('view', 2, ['login_required'])
            >>> results[1]
            ('unprotected', 4, [])
        """
        results: List[Tuple[str, int, List[str]]] = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                lineno = getattr(node, "lineno", 0) or 0
                decorators = self.extract_decorators(node)
                results.append((node.name, lineno, decorators))
        return results

    def extract_all_security_data(
        self,
        tree: ast.AST,
        source_lines: Optional[Sequence[str]] = None,
    ) -> Tuple[
        List[StringLiteral],
        List[DangerousCall],
        List[SQLQuery],
        List[Tuple[str, int, List[str]]],
    ]:
        """Extract all security-relevant data in a single AST walk.

        Performance optimization that combines the work of
        :meth:`extract_string_literals`, :meth:`extract_dangerous_calls`,
        :meth:`extract_sql_queries`, and :meth:`extract_all_function_decorators`
        into one traversal of the AST. This avoids the overhead of four
        separate ``ast.walk`` or ``ast.NodeVisitor.visit`` passes.

        Args:
            tree: A parsed AST tree (typically from :meth:`parse`).
            source_lines: Optional sequence of source code lines for context
                extraction in string literals.

        Returns:
            A 4-tuple of::

                (string_literals, dangerous_calls, sql_queries, function_decorators)

            Each element matches the return type of the corresponding
            individual extraction method.
        """
        str_visitor = _StringLiteralVisitor(source_lines or [])
        call_visitor = _DangerousCallVisitor()
        sql_visitor = _SQLQueryVisitor()
        func_decorators: List[Tuple[str, int, List[str]]] = []

        # Walk the AST once and dispatch each node to the relevant visitors.
        for node in ast.walk(tree):
            # String literals
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                lineno = getattr(node, "lineno", 0) or 0
                str_visitor._record(node.value, lineno)
            elif isinstance(node, ast.Str):  # type: ignore[attr-defined]
                lineno = getattr(node, "lineno", 0) or 0
                str_visitor._record(node.s, lineno)  # type: ignore[attr-defined]

            # Dangerous calls and SQL .format()/.execute() detection
            if isinstance(node, ast.Call):
                call_visitor.visit_Call(node)
                sql_visitor.visit_Call(node)

            # SQL string concatenation
            if isinstance(node, ast.BinOp):
                sql_visitor.visit_BinOp(node)

            # SQL f-strings
            if isinstance(node, ast.JoinedStr):
                sql_visitor.visit_JoinedStr(node)

            # Function decorators
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                lineno = getattr(node, "lineno", 0) or 0
                decorators = self.extract_decorators(node)
                func_decorators.append((node.name, lineno, decorators))

        return (
            str_visitor.literals,
            call_visitor.calls,
            sql_visitor.queries,
            func_decorators,
        )

    # -- Private helpers --

    @staticmethod
    def _resolve_decorator_name(decorator_node: ast.expr) -> str:
        """Resolve a decorator AST node to its name string.

        Args:
            decorator_node: An AST expression node from a decorator list.

        Returns:
            The decorator name as a string. For simple names like
            ``@login_required`` returns ``"login_required"``. For attribute
            access like ``@app.route`` returns ``"app.route"``. For call
            expressions like ``@app.route("/path")`` returns ``"app.route"``.
            Falls back to ``"<complex>"`` for unresolvable expressions.
        """
        # Simple name: @decorator
        if isinstance(decorator_node, ast.Name):
            return decorator_node.id

        # Attribute: @module.decorator
        if isinstance(decorator_node, ast.Attribute):
            return _unparse_attribute(decorator_node)

        # Call: @decorator(...) or @module.decorator(...)
        if isinstance(decorator_node, ast.Call):
            return PythonSecurityParser._resolve_decorator_name(
                decorator_node.func
            )

        return "<complex>"


# ---------------------------------------------------------------------------
# Module-level helpers
# ---------------------------------------------------------------------------


def _unparse_attribute(node: ast.Attribute) -> str:
    """Unparse a dotted attribute chain to a string like ``a.b.c``.

    Falls back to ``"<complex>"`` if the chain contains non-Name/Attribute
    nodes (e.g., subscripts or function calls in the chain).

    Args:
        node: An ``ast.Attribute`` AST node.

    Returns:
        Dotted name string or ``"<complex>"``.
    """
    parts: list[str] = []
    current: ast.expr = node
    while isinstance(current, ast.Attribute):
        parts.append(current.attr)
        current = current.value
    if isinstance(current, ast.Name):
        parts.append(current.id)
        parts.reverse()
        return ".".join(parts)
    return "<complex>"
