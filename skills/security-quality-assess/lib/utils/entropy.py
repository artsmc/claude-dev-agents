"""Shannon entropy calculation utilities for secret detection.

Provides functions to calculate the Shannon entropy of strings and to
determine whether a string is likely a secret based on its entropy value
and additional heuristics. These utilities are used by the SecretsAnalyzer
to flag high-entropy string literals as potential hardcoded credentials.

Shannon entropy measures the average information content per character in
a string.  Random strings (such as cryptographic keys and tokens) typically
have entropy above 4.5 bits/char, while natural language text is usually
below 4.0 bits/char.

This module uses only the Python standard library (``math``,
``collections``, ``re``) and has **no external dependencies**.

Functions:
    calculate_shannon_entropy: Calculate Shannon entropy in bits per
        character.
    is_likely_secret: Determine whether a string is likely a secret based
        on entropy and heuristics.

References:
    - TR.md Section 6.1: Shannon Entropy Calculator
    - OWASP A02:2021 Cryptographic Failures
    - CWE-798: Use of Hard-coded Credentials

Examples:
    >>> from lib.utils.entropy import calculate_shannon_entropy, is_likely_secret
    >>> calculate_shannon_entropy("aaaaa")
    0.0
    >>> round(calculate_shannon_entropy("abcd"), 2)
    2.0
    >>> is_likely_secret("hello")
    False
    >>> is_likely_secret("sK7hF9gL2mN4pQ8rT1vX3zA5cB6dE0fG")
    True
"""

import math
import re
from collections import Counter


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def calculate_shannon_entropy(text: str) -> float:
    """Calculate the Shannon entropy of a string in bits per character.

    Shannon entropy formula::

        H(X) = -SUM( P(x) * log2(P(x)) )  for each unique character x

    where ``P(x)`` is the probability (relative frequency) of character
    ``x`` in the string.

    The result represents the average number of bits needed to encode
    each character.  A perfectly uniform random string over *n* distinct
    characters yields ``log2(n)`` bits/char (the theoretical maximum for
    that alphabet size).  A string consisting of a single repeated
    character yields 0.0.

    Args:
        text: The string to analyze.  May be empty.

    Returns:
        Entropy in bits per character.  Returns 0.0 for empty strings
        and for strings of length 1 (a single character carries no
        uncertainty).  The practical upper bound for printable ASCII
        strings is ~6.6 bits/char; for the full 8-bit byte range it is
        8.0 bits/char.

    Examples:
        >>> calculate_shannon_entropy("")
        0.0
        >>> calculate_shannon_entropy("a")
        0.0
        >>> calculate_shannon_entropy("aaaaa")
        0.0
        >>> round(calculate_shannon_entropy("ab"), 2)
        1.0
        >>> round(calculate_shannon_entropy("abcd"), 2)
        2.0
        >>> round(calculate_shannon_entropy("abcdefgh"), 2)
        3.0
        >>> e = calculate_shannon_entropy("sK7hF9gL2mN4pQ8rT1vX3zA5cB6dE0fG")
        >>> e > 4.0
        True
    """
    if not text:
        return 0.0

    length = len(text)
    if length == 1:
        return 0.0

    counts = Counter(text)
    entropy = 0.0

    for count in counts.values():
        probability = count / length
        if probability > 0.0:
            entropy -= probability * math.log2(probability)

    return entropy


# ---------------------------------------------------------------------------
# Heuristic helpers (false-positive reduction)
# ---------------------------------------------------------------------------

# URL pattern -- strings starting with a scheme
_URL_PATTERN: re.Pattern[str] = re.compile(
    r"^https?://|^\w+://"
)

# File path pattern -- strings with directory separators
_FILE_PATH_PATTERN: re.Pattern[str] = re.compile(
    r"^[/\\.]|[/\\][\w.-]+[/\\]"
)

# UUID pattern (v1-v5)
_UUID_PATTERN: re.Pattern[str] = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
    re.IGNORECASE,
)

# Import / require path (e.g. "@angular/core", "lodash/fp")
_IMPORT_PATH_PATTERN: re.Pattern[str] = re.compile(
    r"^[@\w][\w./-]*$"
)

# HTML/CSS/markup content
_MARKUP_PATTERN: re.Pattern[str] = re.compile(
    r"<[a-zA-Z/]|{[\s\w:;-]+}|\bclass=|#[0-9a-fA-F]{3,8}\b"
)

# Template / placeholder strings
_PLACEHOLDER_PATTERN: re.Pattern[str] = re.compile(
    r"\$\{|\{\{|\%\(|__\w+__"
)

# Repeated single character (e.g. "aaaaaaaaaaaaa")
_REPEATED_CHAR_PATTERN: re.Pattern[str] = re.compile(
    r"^(.)\1{9,}$"
)

# Logging format strings or SQL fragments
_LOG_FORMAT_PATTERN: re.Pattern[str] = re.compile(
    r"%(s|d|f|r)|SELECT\s|INSERT\s|UPDATE\s|DELETE\s",
    re.IGNORECASE,
)

# Pure hex strings shorter than 40 chars (common commit SHAs, checksums)
_HEX_STRING_PATTERN: re.Pattern[str] = re.compile(
    r"^[0-9a-fA-F]+$"
)


def _is_likely_false_positive(value: str) -> bool:
    """Determine whether a high-entropy string is a likely false positive.

    Applies a battery of heuristics to filter out strings that have high
    Shannon entropy but are **not** secrets.  Each heuristic targets a
    common false-positive category.

    Args:
        value: The string to evaluate.

    Returns:
        ``True`` if the string is likely *not* a secret (i.e. it is a
        false positive); ``False`` if it should still be flagged.
    """
    # URLs (may contain query tokens, but those are caught by patterns)
    if _URL_PATTERN.search(value):
        return True

    # File system paths
    if _FILE_PATH_PATTERN.search(value):
        return True

    # UUIDs are identifiers, not secrets
    if _UUID_PATTERN.match(value):
        return True

    # Multi-word natural language
    if " " in value:
        words = value.split()
        if len(words) >= 3:
            return True

    # Import / require paths
    if _IMPORT_PATH_PATTERN.match(value) and "/" in value:
        return True

    # Markup / CSS
    if _MARKUP_PATTERN.search(value):
        return True

    # Template / placeholder variables
    if _PLACEHOLDER_PATTERN.search(value):
        return True

    # Single repeated character
    if _REPEATED_CHAR_PATTERN.match(value):
        return True

    # Log format strings or SQL
    if _LOG_FORMAT_PATTERN.search(value):
        return True

    # Short pure hex strings (commit SHAs, checksums)
    if _HEX_STRING_PATTERN.match(value) and len(value) < 40:
        return True

    return False


# ---------------------------------------------------------------------------
# Public secret likelihood check
# ---------------------------------------------------------------------------


def is_likely_secret(
    text: str,
    threshold: float = 4.5,
    min_length: int = 12,
) -> bool:
    """Determine whether a string is likely a secret based on entropy.

    Combines Shannon entropy measurement with a set of heuristics to
    reduce false positives.  A string is considered a likely secret when
    **all** of the following conditions hold:

    1. Its length meets or exceeds ``min_length``.
    2. Its Shannon entropy meets or exceeds ``threshold``.
    3. It does not match any false-positive heuristic (URLs, file paths,
       UUIDs, natural language, markup, template placeholders, repeated
       characters, log format strings, or short hex strings).

    Args:
        text: The string to evaluate.
        threshold: Minimum Shannon entropy in bits per character to
            consider the string a potential secret.  The default of 4.5
            bits/char balances detection rate against false positives.
            Raise the threshold to reduce false positives at the cost
            of missing some secrets; lower it to catch more secrets at
            the cost of more false positives.
        min_length: Minimum string length.  Strings shorter than this
            are never considered secrets regardless of entropy.  The
            default of 12 characters filters out short identifiers and
            variable names.

    Returns:
        ``True`` if the string is likely a secret; ``False`` otherwise.

    Examples:
        >>> is_likely_secret("")
        False
        >>> is_likely_secret("hello")
        False
        >>> is_likely_secret("short")
        False
        >>> is_likely_secret("aaaaaaaaaaaaaaaa")
        False
        >>> is_likely_secret("sK7hF9gL2mN4pQ8rT1vX3zA5cB6dE0fG")
        True
        >>> is_likely_secret("AKIAZXQR1234ABCD5678")  # entropy ~4.08, below 4.5
        False
        >>> is_likely_secret("AKIAZXQR1234ABCD5678", threshold=4.0)
        True
        >>> is_likely_secret("https://example.com/path?q=abc123def456ghi")
        False
        >>> is_likely_secret("/usr/local/bin/some-long-path-name")
        False
        >>> is_likely_secret("The quick brown fox jumps over the lazy dog")
        False
    """
    # Short strings are never secrets
    if len(text) < min_length:
        return False

    # Calculate entropy
    entropy = calculate_shannon_entropy(text)
    if entropy < threshold:
        return False

    # Apply false-positive heuristics
    if _is_likely_false_positive(text):
        return False

    return True
