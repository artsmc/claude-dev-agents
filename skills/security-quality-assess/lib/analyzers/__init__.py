"""Security analyzers for vulnerability detection.

Provides specialized analyzers that scan parsed source code for different
categories of security vulnerabilities. Each analyzer implements a specific
detection strategy and produces Finding objects.

Exports:
    SecretsAnalyzer: Detects hardcoded secrets, high-entropy strings, and
        weak cryptographic algorithm usage.
    InjectionAnalyzer: Detects SQL injection, command injection, code
        injection, and XSS vulnerabilities.
    AuthAnalyzer: Detects hardcoded passwords, weak JWT configurations,
        insecure session cookies, and missing authentication on routes.
    DependencyAnalyzer: Detects known vulnerabilities in third-party
        dependencies via the OSV database API.
    ConfigAnalyzer: Detects CORS misconfigurations, debug mode enabled,
        missing security headers, and verbose error disclosure.
    SensitiveDataAnalyzer: Detects PII in logs, unencrypted storage of
        sensitive data, and secrets leaked through logging statements.
"""

from lib.analyzers.auth_analyzer import AuthAnalyzer
from lib.analyzers.config_analyzer import ConfigAnalyzer
from lib.analyzers.dependency_analyzer import DependencyAnalyzer
from lib.analyzers.injection_analyzer import InjectionAnalyzer
from lib.analyzers.secrets_analyzer import SecretsAnalyzer
from lib.analyzers.sensitive_data_analyzer import SensitiveDataAnalyzer

__all__ = [
    "AuthAnalyzer",
    "ConfigAnalyzer",
    "DependencyAnalyzer",
    "InjectionAnalyzer",
    "SecretsAnalyzer",
    "SensitiveDataAnalyzer",
]
