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
    load_suppression_config: Discover and parse .security-suppress.json
        from a project root directory.
    validate_suppression_schema: Validate the structure of parsed
        suppression JSON data.
    check_expired_suppressions: Partition suppressions into active and
        expired groups, logging warnings for expired entries.
    apply_suppressions: Filter findings against active suppression rules,
        returning filtered findings and suppressed count.
"""

from lib.utils.entropy import calculate_shannon_entropy, is_likely_secret
from lib.utils.osv_client import OSVClient
from lib.utils.patterns import SecurityPatterns
from lib.utils.suppression_loader import (
    apply_suppressions,
    check_expired_suppressions,
    load_suppression_config,
    validate_suppression_schema,
)

__all__ = [
    "OSVClient",
    "SecurityPatterns",
    "apply_suppressions",
    "calculate_shannon_entropy",
    "check_expired_suppressions",
    "is_likely_secret",
    "load_suppression_config",
    "validate_suppression_schema",
]
