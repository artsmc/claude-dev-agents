"""Utility modules for the security quality assessment skill.

Exports:
    OSVClient: HTTP client for the OSV (Open Source Vulnerabilities) API
        with local 24-hour filesystem caching.
    SecurityPatterns: Centralized regex pattern library for security
        detection, organized by category (secrets, PII, injection,
        JavaScript, weak cryptography, configuration, auth).
    calculate_shannon_entropy: Calculate Shannon entropy (bits/char) of a
        string.
    is_likely_secret: Determine whether a string is likely a hardcoded
        secret based on entropy and heuristics.
"""

from lib.utils.entropy import calculate_shannon_entropy, is_likely_secret
from lib.utils.osv_client import OSVClient
from lib.utils.patterns import SecurityPatterns

__all__ = [
    "OSVClient",
    "SecurityPatterns",
    "calculate_shannon_entropy",
    "is_likely_secret",
]
