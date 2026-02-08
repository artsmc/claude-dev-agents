"""Security analyzers for vulnerability detection.

Provides specialized analyzers that scan parsed source code for different
categories of security vulnerabilities. Each analyzer implements a specific
detection strategy and produces Finding objects.

Exports:
    SecretsAnalyzer: Detects hardcoded secrets, high-entropy strings, and
        weak cryptographic algorithm usage.
    InjectionAnalyzer: Detects SQL injection, command injection, code
        injection, and XSS vulnerabilities.
"""

from lib.analyzers.secrets_analyzer import SecretsAnalyzer
from lib.analyzers.injection_analyzer import InjectionAnalyzer

__all__ = [
    "SecretsAnalyzer",
    "InjectionAnalyzer",
]
