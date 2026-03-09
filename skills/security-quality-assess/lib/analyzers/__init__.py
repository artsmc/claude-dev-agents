"""Security analyzers for vulnerability detection.

Provides specialized analyzers that scan parsed source code for different
categories of security vulnerabilities. Each analyzer implements a specific
detection strategy and produces Finding objects.

Exports:
    SecretsAnalyzer: Detects hardcoded secrets, high-entropy strings, and
        weak cryptographic algorithm usage.
    InjectionAnalyzer: Detects SQL injection, command injection, code
        injection, XSS, NoSQL injection, unsafe YAML loading, XXE, and
        JavaScript child_process command injection vulnerabilities.
    AuthAnalyzer: Detects hardcoded passwords, weak JWT configurations,
        insecure session cookies, and missing authentication on routes.
    DependencyAnalyzer: Detects known vulnerabilities in third-party
        dependencies via the OSV database API.
    ConfigAnalyzer: Detects CORS misconfigurations, debug mode enabled,
        missing security headers, and verbose error disclosure.
    SensitiveDataAnalyzer: Detects PII in logs, unencrypted storage of
        sensitive data, and secrets leaked through logging statements.
    SSRFAnalyzer: Detects Server-Side Request Forgery (SSRF) vulnerabilities
        where user-controlled input is passed to HTTP request functions.
    AdvancedAnalyzer: Detects advanced vulnerabilities including unsafe
        deserialization (marshal, shelve), extended JS command injection,
        extended weak cryptography, path traversal, unsafe file permissions,
        prototype pollution, HTTP credential transmission, Python NoSQL
        injection, and xml.dom.minidom XXE.
"""

from lib.analyzers.advanced_analyzer import AdvancedAnalyzer
from lib.analyzers.auth_analyzer import AuthAnalyzer
from lib.analyzers.config_analyzer import ConfigAnalyzer
from lib.analyzers.dependency_analyzer import DependencyAnalyzer
from lib.analyzers.injection_analyzer import InjectionAnalyzer
from lib.analyzers.secrets_analyzer import SecretsAnalyzer
from lib.analyzers.sensitive_data_analyzer import SensitiveDataAnalyzer
from lib.analyzers.ssrf_analyzer import SSRFAnalyzer

__all__ = [
    "AdvancedAnalyzer",
    "AuthAnalyzer",
    "ConfigAnalyzer",
    "DependencyAnalyzer",
    "InjectionAnalyzer",
    "SecretsAnalyzer",
    "SensitiveDataAnalyzer",
    "SSRFAnalyzer",
]
