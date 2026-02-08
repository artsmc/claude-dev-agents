"""Security-focused code parsers.

Provides language-specific parsers that extract security-relevant patterns
from source code using AST analysis (Python) or regex patterns (other
languages).

Exports:
    PythonSecurityParser: AST-based Python parser for security analysis.
    StringLiteral: Data class for extracted string constants.
    DangerousCall: Data class for detected dangerous function calls.
    SQLQuery: Data class for detected SQL construction patterns.
"""

from lib.parsers.python_parser import (
    DangerousCall,
    PythonSecurityParser,
    SQLQuery,
    StringLiteral,
)

__all__ = [
    "DangerousCall",
    "PythonSecurityParser",
    "SQLQuery",
    "StringLiteral",
]
