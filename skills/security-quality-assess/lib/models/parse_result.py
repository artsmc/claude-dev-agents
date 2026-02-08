"""Unified parse result model for security analyzers.

Defines the ParseResult dataclass that bridges parser output to analyzer input.
Each ParseResult represents the security-relevant data extracted from a single
source file by the appropriate language parser.

Analyzers receive a list of ParseResult objects and iterate over them to detect
vulnerabilities without needing to know which parser produced the data.

Classes:
    ParseResult: Unified container for parsed file data.
"""

from dataclasses import dataclass, field
from typing import List, Optional

from lib.parsers.python_parser import DangerousCall, SQLQuery, StringLiteral
from lib.parsers.javascript_parser import (
    DangerousPattern,
    JSDBQuery,
    JSStringLiteral,
)
from lib.parsers.dependency_parser import Dependency


@dataclass
class ParseResult:
    """Unified container for parsed file data.

    Aggregates all security-relevant extractions from a single source file
    into a single object that analyzers can consume uniformly. Not every
    field is populated for every file -- only the fields relevant to the
    file's language will contain data.

    For Python files, ``string_literals``, ``dangerous_calls``, and
    ``sql_queries`` are populated by :class:`PythonSecurityParser`.

    For JavaScript/TypeScript files, ``js_string_literals``,
    ``dangerous_patterns``, and ``js_db_queries`` are populated by
    :class:`JavaScriptSecurityParser`.

    For lockfiles, ``dependencies`` is populated by
    :class:`DependencyParser`.

    Attributes:
        file_path: Relative path to the source file from the project root.
        language: Language identifier: ``"python"``, ``"javascript"``, or
            ``"lockfile"``.
        source_lines: The original source code split into lines. Used by
            analyzers to extract code context for findings. Empty list for
            lockfiles.
        string_literals: String literals extracted from Python source code
            by :class:`PythonSecurityParser`.
        js_string_literals: String literals extracted from JS/TS source code
            by :class:`JavaScriptSecurityParser`.
        dangerous_calls: Dangerous function calls detected in Python source
            by :class:`PythonSecurityParser`.
        dangerous_patterns: Dangerous API patterns detected in JS/TS source
            by :class:`JavaScriptSecurityParser`.
        sql_queries: SQL construction patterns detected in Python source
            by :class:`PythonSecurityParser`.
        js_db_queries: Database query patterns detected in JS/TS source
            by :class:`JavaScriptSecurityParser`.
        dependencies: Third-party dependencies extracted from lockfiles
            by :class:`DependencyParser`.
        raw_source: The complete raw source code as a single string.
            Retained for analyzers that need to perform their own regex
            scanning (e.g., weak crypto detection). Empty string for
            lockfiles.
    """

    file_path: str
    language: str  # "python", "javascript", "lockfile"
    source_lines: List[str] = field(default_factory=list)
    raw_source: str = ""

    # Python parser outputs
    string_literals: List[StringLiteral] = field(default_factory=list)
    dangerous_calls: List[DangerousCall] = field(default_factory=list)
    sql_queries: List[SQLQuery] = field(default_factory=list)

    # JavaScript parser outputs
    js_string_literals: List[JSStringLiteral] = field(default_factory=list)
    dangerous_patterns: List[DangerousPattern] = field(default_factory=list)
    js_db_queries: List[JSDBQuery] = field(default_factory=list)

    # Dependency parser outputs
    dependencies: List[Dependency] = field(default_factory=list)

    # Optional: function decorators for auth analysis
    function_decorators: Optional[List] = field(default_factory=list)
