"""Secrets and weak cryptography analyzer.

Detects hardcoded secrets, high-entropy strings, and weak cryptographic
algorithm usage in Python and JavaScript/TypeScript source code. This is one
of the core analyzers in the security quality assessment skill and maps
primarily to OWASP A02:2021 (Cryptographic Failures).

Detection strategies:
    1. **Pattern matching** -- regex-based detection of known secret formats
       (AWS keys, GitHub tokens, Slack tokens, JWTs, private key headers,
       generic API key assignments).
    2. **Shannon entropy** -- flags string literals with entropy above 4.5
       bits/char as potential embedded secrets, after excluding common
       false-positive categories (URLs, file paths, ordinary words).
    3. **Weak cryptography** -- detects usage of MD5, SHA1, and DES in both
       Python (hashlib, PyCryptodome) and JavaScript (crypto module) code.

All detections produce :class:`Finding` objects categorized under
:attr:`OWASPCategory.A02_CRYPTOGRAPHIC_FAILURES` with appropriate CWE
references:
    - CWE-798: Use of Hard-coded Credentials (secrets)
    - CWE-327: Use of a Broken or Risky Cryptographic Algorithm (weak crypto)

This module uses only the Python standard library and has no external
dependencies.

Classes:
    SecretsAnalyzer: Main analyzer class with analyze() entry point.

References:
    - TR.md Section 4.2: SecretsAnalyzer
    - OWASP A02:2021 Cryptographic Failures
    - CWE-798: Use of Hard-coded Credentials
    - CWE-327: Use of a Broken or Risky Cryptographic Algorithm
"""

import logging
import math
import re
from collections import Counter
from typing import Any, Dict, List, Optional, Tuple

from lib.models.finding import Finding, OWASPCategory, Severity
from lib.models.parse_result import ParseResult

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Secret pattern definitions
# ---------------------------------------------------------------------------

# Each entry: (compiled_regex, rule_id, title, description, severity,
#               confidence, cwe_id, remediation)

_SECRET_PATTERNS: List[
    Tuple[re.Pattern, str, str, str, Severity, float, str, str]  # type: ignore[type-arg]
] = [
    (
        re.compile(r"AKIA[0-9A-Z]{16}"),
        "hardcoded-aws-key",
        "Hardcoded AWS access key detected",
        (
            "An AWS access key ID (beginning with 'AKIA') is embedded directly "
            "in source code. If this key is committed to version control, "
            "anyone with repository access can use it to authenticate against "
            "AWS services. Automated scanners on public repositories actively "
            "harvest such keys within minutes of a push."
        ),
        Severity.CRITICAL,
        0.95,
        "CWE-798",
        (
            "Remove the key from source code immediately and rotate it in the "
            "AWS IAM console. Store credentials in environment variables, "
            "AWS Secrets Manager, or an IAM instance profile. Never commit "
            "AWS keys to version control."
        ),
    ),
    (
        re.compile(r"ghp_[a-zA-Z0-9]{36}"),
        "hardcoded-github-token",
        "Hardcoded GitHub personal access token detected",
        (
            "A GitHub personal access token (beginning with 'ghp_') is embedded "
            "in source code. This token grants access to the owner's GitHub "
            "resources with whatever scopes were granted at creation time."
        ),
        Severity.CRITICAL,
        0.95,
        "CWE-798",
        (
            "Revoke the token immediately via GitHub Settings > Developer "
            "settings > Personal access tokens. Use environment variables "
            "or GitHub Apps with short-lived installation tokens instead."
        ),
    ),
    (
        re.compile(r"gho_[a-zA-Z0-9]{36}"),
        "hardcoded-github-oauth-token",
        "Hardcoded GitHub OAuth token detected",
        (
            "A GitHub OAuth access token (beginning with 'gho_') is embedded "
            "in source code. This token can impersonate the authorizing user."
        ),
        Severity.CRITICAL,
        0.95,
        "CWE-798",
        (
            "Revoke the token immediately. Use proper OAuth flow with secure "
            "token storage. Never embed OAuth tokens in source code."
        ),
    ),
    (
        re.compile(
            r"""api[_-]?key['\"]?\s*[:=]\s*['\"]([a-zA-Z0-9]{32,})['\"]""",
            re.IGNORECASE,
        ),
        "hardcoded-api-key",
        "Generic API key pattern detected",
        (
            "A string assignment matching the pattern 'api_key = \"...\"' or "
            "'apiKey: \"...\"' was found with a value of 32 or more "
            "alphanumeric characters. This strongly suggests a hardcoded API "
            "key or secret token."
        ),
        Severity.HIGH,
        0.80,
        "CWE-798",
        (
            "Move the API key to an environment variable or a secrets "
            "management service. Use a .env file (excluded from version "
            "control via .gitignore) for local development."
        ),
    ),
    (
        re.compile(r"xox[baprs]-[0-9a-zA-Z]{10,48}"),
        "hardcoded-slack-token",
        "Hardcoded Slack token detected",
        (
            "A Slack API token (beginning with 'xoxb-', 'xoxa-', 'xoxp-', "
            "'xoxr-', or 'xoxs-') is embedded in source code. These tokens "
            "grant access to Slack workspaces and channels."
        ),
        Severity.CRITICAL,
        0.90,
        "CWE-798",
        (
            "Revoke the token immediately in Slack's app management settings. "
            "Store Slack tokens in environment variables or a secrets vault. "
            "Use Slack's OAuth flow for production applications."
        ),
    ),
    (
        re.compile(
            r"eyJ[A-Za-z0-9-_]+\.eyJ[A-Za-z0-9-_]+\.[A-Za-z0-9-_.+/]+"
        ),
        "hardcoded-jwt-token",
        "Hardcoded JWT token detected",
        (
            "A JSON Web Token (JWT) is embedded in source code. JWTs often "
            "contain authentication claims and may grant access to protected "
            "resources. Even expired tokens leak information about the "
            "token structure and claims."
        ),
        Severity.HIGH,
        0.85,
        "CWE-798",
        (
            "Remove the JWT from source code. If used for testing, move it "
            "to a test fixture file excluded from production builds. "
            "Generate tokens dynamically at runtime using proper signing keys "
            "stored in environment variables."
        ),
    ),
    (
        re.compile(r"-----BEGIN[\s]+(RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----"),
        "hardcoded-private-key",
        "Private key detected in source code",
        (
            "A PEM-encoded private key header was found in source code. "
            "Private keys must never be stored in version control as they "
            "provide the ability to impersonate servers, sign tokens, or "
            "decrypt sensitive data."
        ),
        Severity.CRITICAL,
        0.95,
        "CWE-798",
        (
            "Remove the private key from source code and rotate it immediately. "
            "Store private keys in a secrets management service, an HSM, or "
            "encrypted key files outside of version control. Use file-based "
            "references (e.g., KEY_FILE=/path/to/key.pem) instead."
        ),
    ),
]


# ---------------------------------------------------------------------------
# Weak cryptography pattern definitions
# ---------------------------------------------------------------------------

# Each entry: (compiled_regex, rule_id, title, description, severity,
#               confidence, cwe_id, remediation, language_filter)
# language_filter: "python", "javascript", or None for any language.

_WeakCryptoEntry = Tuple[
    re.Pattern, str, str, str, Severity, float, str, str, Optional[str]  # type: ignore[type-arg]
]

_WEAK_CRYPTO_PATTERNS: List[_WeakCryptoEntry] = [
    # Python hashlib.md5
    (
        re.compile(r"\bhashlib\.md5\b"),
        "weak-crypto-md5",
        "Weak hash algorithm: MD5",
        (
            "MD5 is used via hashlib.md5(). MD5 is cryptographically broken "
            "and should not be used for security purposes such as password "
            "hashing, integrity verification, or digital signatures. "
            "Collision attacks against MD5 are practical and well-documented."
        ),
        Severity.MEDIUM,
        0.90,
        "CWE-327",
        (
            "Replace MD5 with SHA-256 or SHA-3 for integrity checks. "
            "For password hashing, use bcrypt, scrypt, or argon2 instead. "
            "Example: hashlib.sha256(data).hexdigest()"
        ),
        "python",
    ),
    # Python hashlib.sha1
    (
        re.compile(r"\bhashlib\.sha1\b"),
        "weak-crypto-sha1",
        "Weak hash algorithm: SHA-1",
        (
            "SHA-1 is used via hashlib.sha1(). SHA-1 is considered "
            "cryptographically weak since practical collision attacks have "
            "been demonstrated (SHAttered, 2017). It should not be used for "
            "security-sensitive operations."
        ),
        Severity.MEDIUM,
        0.85,
        "CWE-327",
        (
            "Replace SHA-1 with SHA-256 or SHA-3. "
            "Example: hashlib.sha256(data).hexdigest()"
        ),
        "python",
    ),
    # PyCryptodome MD5
    (
        re.compile(r"\bCrypto\.Hash\.MD5\b"),
        "weak-crypto-md5-pycrypto",
        "Weak hash algorithm: MD5 (PyCryptodome)",
        (
            "MD5 is used via PyCryptodome's Crypto.Hash.MD5. MD5 is "
            "cryptographically broken and should not be used for any "
            "security-sensitive purpose."
        ),
        Severity.MEDIUM,
        0.90,
        "CWE-327",
        (
            "Replace with Crypto.Hash.SHA256 or Crypto.Hash.SHA3_256."
        ),
        "python",
    ),
    # PyCryptodome SHA1
    (
        re.compile(r"\bCrypto\.Hash\.SHA1\b"),
        "weak-crypto-sha1-pycrypto",
        "Weak hash algorithm: SHA-1 (PyCryptodome)",
        (
            "SHA-1 is used via PyCryptodome's Crypto.Hash.SHA1. SHA-1 is "
            "cryptographically weak and should not be used for "
            "security-sensitive operations."
        ),
        Severity.MEDIUM,
        0.85,
        "CWE-327",
        (
            "Replace with Crypto.Hash.SHA256 or Crypto.Hash.SHA3_256."
        ),
        "python",
    ),
    # PyCryptodome DES
    (
        re.compile(r"\bCrypto\.Cipher\.DES\b"),
        "weak-crypto-des",
        "Weak encryption algorithm: DES",
        (
            "DES is used via PyCryptodome's Crypto.Cipher.DES. DES uses a "
            "56-bit key which can be brute-forced in hours on modern "
            "hardware. DES has been superseded by AES since 2001."
        ),
        Severity.MEDIUM,
        0.90,
        "CWE-327",
        (
            "Replace DES with AES-256 (Crypto.Cipher.AES with a 256-bit key). "
            "Use authenticated encryption modes such as GCM or CCM."
        ),
        "python",
    ),
    # JavaScript crypto.createHash('md5')
    (
        re.compile(
            r"""(?:crypto|require\s*\(\s*['"]crypto['"]\s*\))"""
            r"""\.createHash\s*\(\s*['"]md5['"]\s*\)""",
        ),
        "weak-crypto-md5-js",
        "Weak hash algorithm: MD5 (Node.js)",
        (
            "MD5 is used via Node.js crypto.createHash('md5'). MD5 is "
            "cryptographically broken and should not be used for security "
            "purposes."
        ),
        Severity.MEDIUM,
        0.90,
        "CWE-327",
        (
            "Replace with crypto.createHash('sha256'). For password hashing, "
            "use bcrypt or scrypt via the 'bcrypt' or 'scrypt' npm packages."
        ),
        "javascript",
    ),
    # JavaScript crypto.createHash('sha1')
    (
        re.compile(
            r"""(?:crypto|require\s*\(\s*['"]crypto['"]\s*\))"""
            r"""\.createHash\s*\(\s*['"]sha1['"]\s*\)""",
        ),
        "weak-crypto-sha1-js",
        "Weak hash algorithm: SHA-1 (Node.js)",
        (
            "SHA-1 is used via Node.js crypto.createHash('sha1'). SHA-1 is "
            "cryptographically weak and should not be used for "
            "security-sensitive operations."
        ),
        Severity.MEDIUM,
        0.85,
        "CWE-327",
        (
            "Replace with crypto.createHash('sha256')."
        ),
        "javascript",
    ),
    # JavaScript createCipheriv with des
    (
        re.compile(
            r"""\.createCipheriv\s*\(\s*['"]des[^'"]*['"]\s*""",
            re.IGNORECASE,
        ),
        "weak-crypto-des-js",
        "Weak encryption algorithm: DES (Node.js)",
        (
            "DES is used via Node.js crypto.createCipheriv('des-...'). "
            "DES uses a 56-bit key and is insecure against brute-force "
            "attacks on modern hardware."
        ),
        Severity.MEDIUM,
        0.90,
        "CWE-327",
        (
            "Replace with 'aes-256-gcm' or 'aes-256-cbc'. Example: "
            "crypto.createCipheriv('aes-256-gcm', key, iv)"
        ),
        "javascript",
    ),
]


# ---------------------------------------------------------------------------
# Entropy calculation
# ---------------------------------------------------------------------------


def _shannon_entropy(data: str) -> float:
    """Calculate the Shannon entropy of a string in bits per character.

    Shannon entropy measures the average information content per character.
    Random strings (like cryptographic keys) typically have entropy > 4.5
    bits/char, while natural language text is usually below 4.0.

    Args:
        data: The string to analyze. Must contain at least one character.

    Returns:
        Entropy value in bits per character. Returns 0.0 for empty strings.
    """
    if not data:
        return 0.0

    length = len(data)
    counts = Counter(data)
    entropy = 0.0

    for count in counts.values():
        probability = count / length
        if probability > 0:
            entropy -= probability * math.log2(probability)

    return entropy


# ---------------------------------------------------------------------------
# False positive reduction for entropy detection
# ---------------------------------------------------------------------------

# Common file extensions that appear in paths (not secrets).
_FILE_EXTENSION_PATTERN = re.compile(
    r"\.\w{1,6}$"
)

# URL pattern -- strings starting with http(s):// or containing ://
_URL_PATTERN = re.compile(
    r"^https?://|^\w+://"
)

# File path pattern -- strings with path separators
_FILE_PATH_PATTERN = re.compile(
    r"^[/\\.]|[/\\][\w.-]+[/\\]"
)

# Common base64-like padding at the end
_BASE64_PADDING_PATTERN = re.compile(
    r"^[A-Za-z0-9+/]+={0,2}$"
)

# UUID pattern
_UUID_PATTERN = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
    re.IGNORECASE,
)

# Common English words and code tokens that happen to have high entropy
# when they are long enough. We skip strings that consist primarily of
# common words.
_COMMON_WORD_PATTERN = re.compile(
    r"^[\w\s.,;:!?'\"-]+$"
)

# Hex string pattern (common for hashes, not necessarily secrets)
_HEX_STRING_PATTERN = re.compile(
    r"^[0-9a-fA-F]+$"
)

# Import/require path pattern
_IMPORT_PATH_PATTERN = re.compile(
    r"^[@\w][\w./-]*$"
)

# CSS/HTML-like content
_MARKUP_PATTERN = re.compile(
    r"<[a-zA-Z/]|{[\s\w:;-]+}|\bclass=|#[0-9a-fA-F]{3,8}\b"
)

# Placeholder / template variable patterns
_PLACEHOLDER_PATTERN = re.compile(
    r"\$\{|\{\{|\%\(|__\w+__"
)

# Repeated character pattern (not a real secret)
_REPEATED_CHAR_PATTERN = re.compile(
    r"^(.)\1{9,}$"
)

# Logging format strings / SQL-like content
_LOG_FORMAT_PATTERN = re.compile(
    r"%(s|d|f|r)|SELECT\s|INSERT\s|UPDATE\s|DELETE\s",
    re.IGNORECASE,
)


def _is_likely_false_positive(value: str) -> bool:
    """Determine if a high-entropy string is likely a false positive.

    Applies multiple heuristics to filter out strings that have high
    Shannon entropy but are not secrets. This reduces the false positive
    rate for entropy-based detection.

    Args:
        value: The string value to evaluate.

    Returns:
        True if the string is likely a false positive (not a secret),
        False if it should still be flagged.
    """
    # URLs are not secrets (they may contain tokens, but pattern detection
    # handles those separately).
    if _URL_PATTERN.search(value):
        return True

    # File paths
    if _FILE_PATH_PATTERN.search(value):
        return True

    # UUIDs are identifiers, not secrets
    if _UUID_PATTERN.match(value):
        return True

    # Strings with whitespace that look like natural language
    if " " in value:
        words = value.split()
        if len(words) >= 3:
            # Multiple words is probably prose, not a secret
            return True

    # Import/require paths (e.g., "@angular/core", "lodash/fp")
    if _IMPORT_PATH_PATTERN.match(value) and "/" in value:
        return True

    # HTML/CSS/markup content
    if _MARKUP_PATTERN.search(value):
        return True

    # Template / placeholder strings
    if _PLACEHOLDER_PATTERN.search(value):
        return True

    # Repeated characters (e.g., "aaaaaaaaaaaaa")
    if _REPEATED_CHAR_PATTERN.match(value):
        return True

    # Logging format strings or SQL fragments
    if _LOG_FORMAT_PATTERN.search(value):
        return True

    # Pure hex strings shorter than 40 chars are common hashes, not secrets
    # (longer ones might be private keys or tokens)
    if _HEX_STRING_PATTERN.match(value) and len(value) < 40:
        return True

    return False


# ---------------------------------------------------------------------------
# Finding ID generator
# ---------------------------------------------------------------------------


class _FindingIDGenerator:
    """Thread-unsafe sequential ID generator for findings.

    Produces IDs in the format "SEC-001", "SEC-002", etc. A new generator
    is created for each analyze() invocation so IDs start from 1.
    """

    def __init__(self) -> None:
        self._counter = 0

    def next_id(self) -> str:
        """Return the next sequential finding ID."""
        self._counter += 1
        return f"SEC-{self._counter:03d}"


# ---------------------------------------------------------------------------
# Main analyzer class
# ---------------------------------------------------------------------------


class SecretsAnalyzer:
    """Detect hardcoded secrets, high-entropy strings, and weak cryptography.

    This analyzer implements three complementary detection strategies that
    together provide broad coverage of secret exposure and cryptographic
    weakness patterns:

    1. **Pattern matching** (``_detect_patterns``): Searches all string
       literals for known secret formats using compiled regular expressions.
       This is the highest-confidence detection with the fewest false
       positives.

    2. **Shannon entropy** (``_detect_high_entropy``): Calculates the
       information entropy of string literals and flags those exceeding
       the threshold (4.5 bits/char by default) as potential secrets.
       Multiple heuristics are applied to reduce false positives from
       URLs, file paths, natural language text, and markup.

    3. **Weak cryptography** (``_detect_weak_crypto``): Scans raw source
       code for usage of deprecated or broken cryptographic algorithms
       (MD5, SHA-1, DES) across both Python and JavaScript ecosystems.

    All findings are categorized under OWASP A02:2021 (Cryptographic
    Failures) with CWE-798 (hardcoded credentials) or CWE-327 (weak
    cryptography) references.

    Attributes:
        ENTROPY_THRESHOLD: Minimum Shannon entropy (bits/char) to flag a
            string as a potential secret. Default: 4.5.
        MIN_STRING_LENGTH: Minimum string length for entropy analysis.
            Shorter strings are skipped as they rarely contain meaningful
            secrets and produce many false positives. Default: 20.
        VERSION: Analyzer version string for AssessmentResult tracking.

    Usage::

        analyzer = SecretsAnalyzer()
        findings = analyzer.analyze(parsed_files, config={})

    Configuration:
        The ``config`` dict passed to ``analyze()`` supports these optional
        keys:

        - ``entropy_threshold`` (float): Override the default entropy
          threshold.
        - ``min_string_length`` (int): Override the minimum string length
          for entropy analysis.
        - ``skip_entropy`` (bool): Disable entropy-based detection entirely.
        - ``skip_weak_crypto`` (bool): Disable weak cryptography detection.
    """

    ENTROPY_THRESHOLD: float = 4.5
    MIN_STRING_LENGTH: int = 20
    VERSION: str = "1.0.0"

    def analyze(
        self,
        parsed_files: List[ParseResult],
        config: Dict[str, Any],
    ) -> List[Finding]:
        """Run all secrets detection strategies on the parsed files.

        Iterates over each parsed file and applies pattern matching, entropy
        analysis, and weak cryptography detection. Results from all three
        strategies are combined into a single list of findings.

        Args:
            parsed_files: List of ParseResult objects from the parsing phase.
                Each represents one source file with extracted string literals
                and raw source content.
            config: Optional configuration overrides. Supported keys:
                ``entropy_threshold`` (float), ``min_string_length`` (int),
                ``skip_entropy`` (bool), ``skip_weak_crypto`` (bool).

        Returns:
            List of Finding objects, one per detected issue. Findings are
            ordered by file path and then by line number within each file.
        """
        findings: List[Finding] = []
        id_gen = _FindingIDGenerator()

        # Apply config overrides
        entropy_threshold = config.get(
            "entropy_threshold", self.ENTROPY_THRESHOLD
        )
        min_string_length = config.get(
            "min_string_length", self.MIN_STRING_LENGTH
        )
        skip_entropy = config.get("skip_entropy", False)
        skip_weak_crypto = config.get("skip_weak_crypto", False)

        for parsed_file in parsed_files:
            # Skip lockfiles -- they contain version strings, not secrets
            if parsed_file.language == "lockfile":
                continue

            # 1. Pattern matching on string literals
            findings.extend(
                self._detect_patterns(parsed_file, id_gen)
            )

            # 2. Entropy analysis on string literals
            if not skip_entropy:
                findings.extend(
                    self._detect_high_entropy(
                        parsed_file, id_gen,
                        entropy_threshold, min_string_length,
                    )
                )

            # 3. Weak cryptography in raw source
            if not skip_weak_crypto:
                findings.extend(
                    self._detect_weak_crypto(parsed_file, id_gen)
                )

        return findings

    # -----------------------------------------------------------------
    # Strategy 1: Pattern-based detection
    # -----------------------------------------------------------------

    def _detect_patterns(
        self,
        parsed_file: ParseResult,
        id_gen: _FindingIDGenerator,
    ) -> List[Finding]:
        """Detect secrets by matching string literals against known patterns.

        Iterates over all string literals extracted by the language parser
        and tests each against compiled regex patterns for AWS keys, GitHub
        tokens, Slack tokens, JWTs, private keys, and generic API keys.

        Args:
            parsed_file: A single parsed file result containing string
                literals and file metadata.
            id_gen: Sequential ID generator for creating finding IDs.

        Returns:
            List of Finding objects for each pattern match. A single string
            literal may match multiple patterns (e.g., a string containing
            both an AWS key and a JWT), in which case separate findings are
            created for each match.
        """
        findings: List[Finding] = []

        # Collect all string values with their line numbers and context
        string_entries = self._collect_string_entries(parsed_file)

        # Also scan raw source lines for patterns that might span across
        # non-string contexts (e.g., private key headers in heredocs)
        raw_entries = self._collect_raw_line_entries(parsed_file)

        # Deduplicate: track (rule_id, line_number) to avoid duplicate
        # findings when the same secret appears in both string literals
        # and raw source scanning.
        seen: set[Tuple[str, int]] = set()

        for value, line_number, context in string_entries + raw_entries:
            for (
                pattern,
                rule_id,
                title,
                description,
                severity,
                confidence,
                cwe_id,
                remediation,
            ) in _SECRET_PATTERNS:
                if pattern.search(value):
                    key = (rule_id, line_number)
                    if key in seen:
                        continue
                    seen.add(key)

                    # Build a sanitized code sample (mask the middle of
                    # the matched secret)
                    code_sample = self._build_code_sample(
                        parsed_file.source_lines, line_number
                    )

                    findings.append(
                        Finding(
                            id=id_gen.next_id(),
                            rule_id=rule_id,
                            category=OWASPCategory.A02_CRYPTOGRAPHIC_FAILURES,
                            severity=severity,
                            title=title,
                            description=description,
                            file_path=parsed_file.file_path,
                            line_number=line_number,
                            code_sample=code_sample,
                            remediation=remediation,
                            cwe_id=cwe_id,
                            confidence=confidence,
                            metadata={
                                "matched_pattern": rule_id,
                                "string_length": len(value),
                            },
                        )
                    )

        return findings

    # -----------------------------------------------------------------
    # Strategy 2: High-entropy string detection
    # -----------------------------------------------------------------

    def _detect_high_entropy(
        self,
        parsed_file: ParseResult,
        id_gen: _FindingIDGenerator,
        entropy_threshold: float,
        min_string_length: int,
    ) -> List[Finding]:
        """Detect potential secrets by measuring Shannon entropy of strings.

        Calculates the information entropy for each string literal that
        meets the minimum length requirement. Strings with entropy above
        the threshold are flagged as potential secrets, unless they match
        one of several false-positive heuristics (URLs, file paths, natural
        language, markup, etc.).

        Args:
            parsed_file: A single parsed file result containing string
                literals and file metadata.
            id_gen: Sequential ID generator for creating finding IDs.
            entropy_threshold: Minimum entropy (bits/char) to flag a string.
            min_string_length: Minimum string length to consider.

        Returns:
            List of Finding objects for high-entropy strings that passed
            all false-positive filters. Each finding includes the calculated
            entropy value in its metadata.
        """
        findings: List[Finding] = []

        # Track which lines already have pattern-match findings to avoid
        # double-reporting. We rely on the caller running _detect_patterns
        # first (which it does), but since findings are appended to a
        # shared list outside this method, we cannot check them here.
        # Instead, we accept a small risk of overlap and deduplicate at
        # the report level if needed.

        string_entries = self._collect_string_entries(parsed_file)

        for value, line_number, _context in string_entries:
            # Skip short strings
            if len(value) < min_string_length:
                continue

            # Calculate entropy
            entropy = _shannon_entropy(value)
            if entropy < entropy_threshold:
                continue

            # Apply false positive filters
            if _is_likely_false_positive(value):
                continue

            # Check if the string already matched a specific pattern
            # (avoid duplicate with pattern detection)
            if self._matches_known_pattern(value):
                continue

            code_sample = self._build_code_sample(
                parsed_file.source_lines, line_number
            )

            # Determine confidence based on entropy level
            confidence = self._entropy_confidence(entropy)

            findings.append(
                Finding(
                    id=id_gen.next_id(),
                    rule_id="high-entropy-string",
                    category=OWASPCategory.A02_CRYPTOGRAPHIC_FAILURES,
                    severity=Severity.HIGH,
                    title="High-entropy string detected (potential secret)",
                    description=(
                        f"A string literal with Shannon entropy of "
                        f"{entropy:.2f} bits/char was detected. High-entropy "
                        f"strings often indicate embedded secrets, API keys, "
                        f"or cryptographic material. The threshold is "
                        f"{entropy_threshold} bits/char."
                    ),
                    file_path=parsed_file.file_path,
                    line_number=line_number,
                    code_sample=code_sample,
                    remediation=(
                        "If this is a secret, move it to an environment "
                        "variable or a secrets management service. If it is "
                        "a legitimate high-entropy string (e.g., a test "
                        "fixture or hash constant), add a suppression entry "
                        "with an explanation."
                    ),
                    cwe_id="CWE-798",
                    confidence=confidence,
                    metadata={
                        "entropy": round(entropy, 4),
                        "string_length": len(value),
                        "threshold": entropy_threshold,
                    },
                )
            )

        return findings

    # -----------------------------------------------------------------
    # Strategy 3: Weak cryptography detection
    # -----------------------------------------------------------------

    def _detect_weak_crypto(
        self,
        parsed_file: ParseResult,
        id_gen: _FindingIDGenerator,
    ) -> List[Finding]:
        """Detect usage of weak or broken cryptographic algorithms.

        Scans raw source code (not just string literals) for references to
        MD5, SHA-1, and DES in both Python and JavaScript contexts. Each
        detection pattern is associated with a specific language filter to
        reduce false positives.

        Args:
            parsed_file: A single parsed file result containing raw source
                code and file metadata.
            id_gen: Sequential ID generator for creating finding IDs.

        Returns:
            List of Finding objects for each weak cryptography usage found.
            Each finding includes the matched line content in its metadata.
        """
        findings: List[Finding] = []

        if not parsed_file.raw_source:
            return findings

        # Track (rule_id, line_number) to avoid duplicates
        seen: set[Tuple[str, int]] = set()

        for (
            pattern,
            rule_id,
            title,
            description,
            severity,
            confidence,
            cwe_id,
            remediation,
            language_filter,
        ) in _WEAK_CRYPTO_PATTERNS:
            # Skip patterns that do not apply to this file's language
            if (
                language_filter is not None
                and parsed_file.language != language_filter
            ):
                continue

            for match in pattern.finditer(parsed_file.raw_source):
                # Determine the line number from the match offset
                line_number = (
                    parsed_file.raw_source[: match.start()].count("\n") + 1
                )

                key = (rule_id, line_number)
                if key in seen:
                    continue
                seen.add(key)

                code_sample = self._build_code_sample(
                    parsed_file.source_lines, line_number
                )

                findings.append(
                    Finding(
                        id=id_gen.next_id(),
                        rule_id=rule_id,
                        category=OWASPCategory.A02_CRYPTOGRAPHIC_FAILURES,
                        severity=severity,
                        title=title,
                        description=description,
                        file_path=parsed_file.file_path,
                        line_number=line_number,
                        code_sample=code_sample,
                        remediation=remediation,
                        cwe_id=cwe_id,
                        confidence=confidence,
                        metadata={
                            "matched_text": match.group(0),
                            "algorithm": rule_id.replace("weak-crypto-", ""),
                        },
                    )
                )

        return findings

    # -----------------------------------------------------------------
    # Helper methods
    # -----------------------------------------------------------------

    def _collect_string_entries(
        self, parsed_file: ParseResult
    ) -> List[Tuple[str, int, str]]:
        """Collect all string literals from a parsed file into a uniform list.

        Merges Python StringLiteral and JavaScript JSStringLiteral objects
        into a list of (value, line_number, context) tuples for uniform
        processing by detection strategies.

        Args:
            parsed_file: A single parsed file result.

        Returns:
            List of (value, line_number, context) tuples. Context is the
            surrounding source lines for Python strings, or an empty string
            for JavaScript strings.
        """
        entries: List[Tuple[str, int, str]] = []

        # Python string literals
        for sl in parsed_file.string_literals:
            entries.append((sl.value, sl.line_number, sl.context))

        # JavaScript string literals
        for jsl in parsed_file.js_string_literals:
            entries.append((jsl.value, jsl.line_number, ""))

        return entries

    def _collect_raw_line_entries(
        self, parsed_file: ParseResult
    ) -> List[Tuple[str, int, str]]:
        """Collect raw source lines as string entries for pattern scanning.

        Some secrets (like private key headers) might not appear as parsed
        string literals if they are in multiline strings or heredocs. This
        method provides a fallback scan over raw source lines.

        Only includes lines that contain characters suggesting they might
        hold a secret (hyphens for PEM headers, long alphanumeric runs).

        Args:
            parsed_file: A single parsed file result.

        Returns:
            List of (line_content, line_number, "") tuples for lines that
            pass the pre-filter.
        """
        entries: List[Tuple[str, int, str]] = []

        for i, line in enumerate(parsed_file.source_lines):
            stripped = line.strip()
            # Only scan lines that look promising (contain PEM markers
            # or long alphanumeric sequences)
            if "-----BEGIN" in stripped or "-----END" in stripped:
                entries.append((stripped, i + 1, ""))
            elif len(stripped) >= 30:
                # Check for long alphanumeric sequences that could be tokens
                if re.search(r"[A-Za-z0-9+/=_-]{30,}", stripped):
                    entries.append((stripped, i + 1, ""))

        return entries

    @staticmethod
    def _build_code_sample(source_lines: List[str], line_number: int) -> str:
        """Build a 3-line code sample centered on the given line number.

        Returns up to 3 lines of source code (the target line plus one
        line above and one below) for inclusion in the finding's
        code_sample field.

        Args:
            source_lines: The source file split into lines.
            line_number: 1-based line number of the finding.

        Returns:
            A string containing the code sample with lines joined by
            newlines. Returns "<source unavailable>" if source lines
            are empty or the line number is out of range.
        """
        if not source_lines or line_number < 1:
            return "<source unavailable>"

        idx = line_number - 1
        start = max(0, idx - 1)
        end = min(len(source_lines), idx + 2)

        if start >= len(source_lines):
            return "<source unavailable>"

        return "\n".join(source_lines[start:end])

    @staticmethod
    def _matches_known_pattern(value: str) -> bool:
        """Check if a string matches any of the known secret patterns.

        Used by entropy detection to skip strings that will already be
        caught by pattern-based detection, avoiding duplicate findings.

        Args:
            value: The string value to check.

        Returns:
            True if the string matches at least one known pattern.
        """
        for pattern, *_rest in _SECRET_PATTERNS:
            if pattern.search(value):
                return True
        return False

    @staticmethod
    def _entropy_confidence(entropy: float) -> float:
        """Calculate detection confidence based on entropy value.

        Higher entropy values produce higher confidence scores. The
        mapping is:

        - entropy >= 6.0: confidence 0.85 (very likely a secret)
        - entropy >= 5.5: confidence 0.75
        - entropy >= 5.0: confidence 0.65
        - entropy >= 4.5: confidence 0.55 (borderline)
        - below 4.5: confidence 0.40 (should not reach here normally)

        Args:
            entropy: Shannon entropy value in bits per character.

        Returns:
            Confidence score between 0.0 and 1.0.
        """
        if entropy >= 6.0:
            return 0.85
        if entropy >= 5.5:
            return 0.75
        if entropy >= 5.0:
            return 0.65
        if entropy >= 4.5:
            return 0.55
        return 0.40
