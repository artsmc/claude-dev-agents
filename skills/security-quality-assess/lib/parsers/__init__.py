"""Security-focused code parsers.

Provides language-specific parsers that extract security-relevant patterns
from source code using AST analysis (Python) or regex patterns (other
languages), as well as dependency lockfile parsers for vulnerability scanning.

Exports:
    PythonSecurityParser: AST-based Python parser for security analysis.
    StringLiteral: Data class for extracted string constants.
    DangerousCall: Data class for detected dangerous function calls.
    SQLQuery: Data class for detected SQL construction patterns.
    JavaScriptSecurityParser: Regex-based JS/TS parser for security analysis.
    JSStringLiteral: Data class for JS/TS string literals with quote type.
    DangerousPattern: Data class for dangerous JS/TS API usage patterns.
    JSDBQuery: Data class for JS/TS database query construction patterns.
    DependencyParser: Lockfile parser for npm and Python dependencies.
    Dependency: Data class for a third-party package dependency.
"""

from lib.parsers.dependency_parser import (
    Dependency,
    DependencyParser,
)
from lib.parsers.javascript_parser import (
    DangerousPattern,
    JSDBQuery,
    JSStringLiteral,
    JavaScriptSecurityParser,
)
from lib.parsers.python_parser import (
    DangerousCall,
    PythonSecurityParser,
    SQLQuery,
    StringLiteral,
)

__all__ = [
    "DangerousCall",
    "DangerousPattern",
    "Dependency",
    "DependencyParser",
    "JSDBQuery",
    "JSStringLiteral",
    "JavaScriptSecurityParser",
    "PythonSecurityParser",
    "SQLQuery",
    "StringLiteral",
]
