"""Advanced vulnerability analyzer.

Detects security vulnerabilities that complement the existing analyzers:
unsafe deserialization (marshal, shelve), extended JS command injection
(spawn with shell:true, execFile), extended weak cryptography (DES3,
deprecated createCipher, Blowfish in JS), path traversal, unsafe file
permissions, prototype pollution, HTTP credential transmission in
JavaScript, Python NoSQL injection (pymongo), and xml.dom.minidom XXE.

Detection strategies:
    1. **Unsafe deserialization** -- regex-based detection of Python
       ``marshal.loads()``, ``shelve.open()`` which can execute arbitrary
       code during deserialization. CWE-502, OWASP A08.

    2. **Extended JS command injection** -- regex-based detection of
       ``child_process.spawn()`` with ``shell: true`` option and
       ``child_process.execFile()`` calls. CWE-78, OWASP A03.

    3. **Extended weak cryptography** -- detection of ``DES3.new()``
       (Triple DES), deprecated Node.js ``createCipher()`` (no IV),
       and ``createCipheriv`` with ``blowfish``. CWE-327, OWASP A02.

    4. **Path traversal** -- detection of Python ``open()`` calls with
       f-string or format-string user-controlled path variables, and
       ``os.path.join()`` with user input. CWE-22, OWASP A01.

    5. **Unsafe file permissions** -- detection of ``os.chmod()`` with
       world-writable modes (0o777, 0o666). CWE-732, OWASP A05.

    6. **Prototype pollution (JS)** -- detection of ``Object.assign()``
       and ``_.merge()`` / ``lodash.merge()`` with user input from
       ``req.body``, ``req.query``, ``req.params``. CWE-1321, OWASP A03.

    7. **HTTP credential transmission (JS)** -- detection of
       ``fetch()``/``axios`` with ``http://`` URLs targeting auth-related
       endpoints (/login, /auth, /token, /api-key). CWE-319, OWASP A02.

    8. **Python NoSQL injection (pymongo)** -- detection of pymongo
       ``find()``, ``find_one()``, ``update_one()`` etc. with unsanitized
       ``request.json``/``request.form`` input. CWE-943, OWASP A03.

    9. **XML DOM minidom XXE** -- detection of
       ``xml.dom.minidom.parseString()``/``xml.dom.minidom.parse()``
       usage. CWE-611, OWASP A03.

All detections produce :class:`Finding` objects with appropriate OWASP
category, CWE reference, severity, and remediation guidance.

This module uses only the Python standard library and has no external
dependencies.

Classes:
    AdvancedAnalyzer: Main analyzer class with analyze() entry point.

References:
    - OWASP A01:2021 Broken Access Control
    - OWASP A02:2021 Cryptographic Failures
    - OWASP A03:2021 Injection
    - OWASP A05:2021 Security Misconfiguration
    - OWASP A08:2021 Software and Data Integrity Failures
    - CWE-22: Improper Limitation of a Pathname to a Restricted Directory
    - CWE-78: Improper Neutralization of Special Elements in OS Command
    - CWE-319: Cleartext Transmission of Sensitive Information
    - CWE-327: Use of a Broken or Risky Cryptographic Algorithm
    - CWE-502: Deserialization of Untrusted Data
    - CWE-611: Improper Restriction of XML External Entity Reference
    - CWE-732: Incorrect Permission Assignment for Critical Resource
    - CWE-943: Improper Neutralization of Special Elements in Data Query Logic
    - CWE-1321: Improperly Controlled Modification of Object Prototype Attributes
"""

import logging
import re
from typing import Any, Dict, List

from lib.models.finding import Finding, OWASPCategory, Severity
from lib.models.parse_result import ParseResult

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Unsafe deserialization patterns (Python)
# ---------------------------------------------------------------------------

# marshal.loads() -- can execute arbitrary code via crafted bytecode.
_UNSAFE_MARSHAL_LOADS = re.compile(
    r"""\bmarshal\.loads?\s*\(""",
)

# shelve.open() -- uses pickle internally, same code execution risk.
_UNSAFE_SHELVE_OPEN = re.compile(
    r"""\bshelve\.open\s*\(""",
)


# ---------------------------------------------------------------------------
# Extended JS command injection patterns
# ---------------------------------------------------------------------------

# spawn() with shell: true -- runs via shell, enabling injection.
_JS_SPAWN_SHELL_TRUE = re.compile(
    r"""\bspawn\s*\([^)]*\{[^}]*shell\s*:\s*true""",
    re.DOTALL,
)

# execFile() -- no shell but still runs external programs.
_JS_EXEC_FILE = re.compile(
    r"""\bexecFile(?:Sync)?\s*\(""",
)


# ---------------------------------------------------------------------------
# Extended weak cryptography patterns
# ---------------------------------------------------------------------------

# PyCryptodome DES3 (Triple DES) -- 64-bit block, Sweet32 vulnerable.
_WEAK_CRYPTO_DES3 = re.compile(
    r"""\bDES3\.new\s*\(""",
)

# Node.js deprecated createCipher() (no IV -- deterministic encryption).
_JS_CREATE_CIPHER_DEPRECATED = re.compile(
    r"""\.createCipher\s*\(\s*['"]""",
)

# Exclude createCipheriv (which is the safe variant with IV).
_JS_CREATE_CIPHERIV = re.compile(
    r"""\.createCipheriv\s*\(""",
)

# Node.js createCipheriv with blowfish algorithm.
_JS_CIPHERIV_BLOWFISH = re.compile(
    r"""\.createCipheriv\s*\(\s*['"](?:bf|blowfish)[^'"]*['"]\s*""",
    re.IGNORECASE,
)


# ---------------------------------------------------------------------------
# Path traversal patterns (Python)
# ---------------------------------------------------------------------------

# open() with f-string containing a variable from common user input names.
_PY_OPEN_FSTRING = re.compile(
    r"""\bopen\s*\(\s*f['"](.*?\{.*?\}.*?)['"]\s*""",
)

# open() with .format() containing user-controlled variable.
_PY_OPEN_FORMAT = re.compile(
    r"""\bopen\s*\([^)]*\.format\s*\(""",
)

# os.path.join() with user input variables (Flask/Django patterns).
_PY_PATH_JOIN_USER_INPUT = re.compile(
    r"""\bos\.path\.join\s*\([^)]*(?:request\.(?:args|form|json|data|values)"""
    r"""|request\.GET|request\.POST|request\.query_params)""",
)

# Variable assigned from request, then used in open() within ~10 lines.
_PY_USER_INPUT_VAR = re.compile(
    r"""^\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*(?:"""
    r"""request\.(?:args|form|json|data|values)\.get\s*\(|"""
    r"""request\.(?:args|form|json|data|values)\[|"""
    r"""request\.(?:GET|POST)\.get\s*\(|"""
    r"""request\.(?:GET|POST)\[|"""
    r"""request\.query_params\.get\s*\()""",
    re.MULTILINE,
)

# open() call with a variable argument (not a string literal).
_PY_OPEN_VARIABLE = re.compile(
    r"""\bopen\s*\(\s*(?!['"])([a-zA-Z_][a-zA-Z0-9_.]*)""",
)


# ---------------------------------------------------------------------------
# Unsafe file permissions patterns (Python)
# ---------------------------------------------------------------------------

# os.chmod() with world-writable modes (0o777, 0o666).
_UNSAFE_CHMOD = re.compile(
    r"""\bos\.chmod\s*\([^)]*0o(?:777|666)\s*\)""",
)


# ---------------------------------------------------------------------------
# Prototype pollution patterns (JavaScript)
# ---------------------------------------------------------------------------

# Object.assign(target, req.body/req.query/req.params)
_JS_OBJECT_ASSIGN_USER_INPUT = re.compile(
    r"""\bObject\.assign\s*\([^,]+,\s*req\.(?:body|query|params)""",
)

# _.merge(target, req.body/req.query/req.params) or lodash.merge(...)
_JS_LODASH_MERGE_USER_INPUT = re.compile(
    r"""(?:_|lodash)\.merge\s*\([^,]+,\s*req\.(?:body|query|params)""",
)

# Spread operator with req.body in object literal: { ...req.body }
_JS_SPREAD_USER_INPUT = re.compile(
    r"""\{\s*\.\.\.req\.(?:body|query|params)""",
)


# ---------------------------------------------------------------------------
# HTTP credential transmission patterns (JavaScript)
# ---------------------------------------------------------------------------

# fetch() or axios with http:// URL targeting auth-like endpoints.
_JS_HTTP_AUTH_ENDPOINT = re.compile(
    r"""(?:fetch|axios\.(?:get|post|put|patch))\s*\(\s*['"`]http://[^'"`]*"""
    r"""(?:/login|/auth|/token|/api-key|/signin|/signup|/register|/password)""",
    re.IGNORECASE,
)

# http.request/http.get with auth-like paths.
_JS_HTTP_MODULE_AUTH = re.compile(
    r"""\bhttp\.(?:request|get)\s*\([^)]*(?:/login|/auth|/token|/api-key|"""
    r"""/signin|/signup|/register|/password)""",
    re.IGNORECASE,
)


# ---------------------------------------------------------------------------
# Python NoSQL injection patterns (pymongo)
# ---------------------------------------------------------------------------

# pymongo collection methods receiving unsanitized Flask/Django input.
_PY_PYMONGO_METHODS = re.compile(
    r"""\.(?:find|find_one|update_one|update_many|delete_one|delete_many|"""
    r"""find_one_and_update|find_one_and_delete|find_one_and_replace|"""
    r"""count_documents|aggregate)\s*\(""",
)

# Python user input sources for NoSQL context.
_PY_NOSQL_USER_INPUT = re.compile(
    r"""request\.(?:json|form|data|args|values|GET|POST)""",
)


# ---------------------------------------------------------------------------
# XML DOM minidom XXE pattern
# ---------------------------------------------------------------------------

# xml.dom.minidom.parseString() / xml.dom.minidom.parse()
_XXE_MINIDOM = re.compile(
    r"""\b(?:xml\.dom\.)?minidom\.(?:parseString|parse)\s*\(""",
)

# Safe defusing: defusedxml usage means XXE is mitigated.
_XXE_DEFUSED = re.compile(
    r"""\bdefusedxml\b|\bdefused\b""",
)


# ---------------------------------------------------------------------------
# Finding ID generator
# ---------------------------------------------------------------------------


class _FindingIDGenerator:
    """Thread-unsafe sequential ID generator for advanced findings.

    Produces IDs in the format "ADV-001", "ADV-002", etc. A new generator
    is created for each analyze() invocation so IDs start from 1.
    """

    def __init__(self) -> None:
        self._counter = 0

    def next_id(self) -> str:
        """Return the next sequential finding ID."""
        self._counter += 1
        return f"ADV-{self._counter:03d}"


# ---------------------------------------------------------------------------
# Main analyzer class
# ---------------------------------------------------------------------------


class AdvancedAnalyzer:
    """Detect advanced vulnerabilities that complement existing analyzers.

    This analyzer implements detection strategies for vulnerability classes
    that are not covered by the existing SecretsAnalyzer, InjectionAnalyzer,
    SSRFAnalyzer, AuthAnalyzer, ConfigAnalyzer, or SensitiveDataAnalyzer.

    Detection categories:
        1. Unsafe deserialization (marshal, shelve) -- OWASP A08
        2. Extended JS command injection (spawn shell:true, execFile) -- A03
        3. Extended weak cryptography (DES3, deprecated createCipher) -- A02
        4. Path traversal (file ops with user input) -- A01
        5. Unsafe file permissions (os.chmod 0o777/0o666) -- A05
        6. Prototype pollution (Object.assign, _.merge with user input) -- A03
        7. HTTP credential transmission in JS (http:// auth endpoints) -- A02
        8. Python NoSQL injection (pymongo with request input) -- A03
        9. XML DOM minidom XXE -- A03

    Attributes:
        VERSION: Analyzer version string for AssessmentResult tracking.

    Usage::

        analyzer = AdvancedAnalyzer()
        findings = analyzer.analyze(parsed_files, config={})

    Configuration:
        The ``config`` dict passed to ``analyze()`` supports these optional
        keys:

        - ``skip_advanced_deserialization`` (bool): Disable deserialization detection.
        - ``skip_advanced_js_command`` (bool): Disable JS command injection detection.
        - ``skip_advanced_crypto`` (bool): Disable weak crypto detection.
        - ``skip_advanced_path_traversal`` (bool): Disable path traversal detection.
        - ``skip_advanced_permissions`` (bool): Disable file permission detection.
        - ``skip_advanced_prototype_pollution`` (bool): Disable prototype pollution detection.
        - ``skip_advanced_http_cred`` (bool): Disable HTTP credential detection.
        - ``skip_advanced_nosql`` (bool): Disable Python NoSQL injection detection.
        - ``skip_advanced_xxe`` (bool): Disable minidom XXE detection.
    """

    VERSION: str = "1.0.0"

    def analyze(
        self,
        parsed_files: List[ParseResult],
        config: Dict[str, Any],
    ) -> List[Finding]:
        """Run all advanced detection strategies on the parsed files.

        Iterates over each parsed file and applies all detection strategies
        based on the file language. Results from all strategies are combined
        into a single list of findings.

        Args:
            parsed_files: List of ParseResult objects from the parsing phase.
                Each represents one source file with extracted data.
            config: Optional configuration overrides. See class docstring
                for supported keys.

        Returns:
            List of Finding objects, one per detected issue. Findings are
            ordered by file path and then by line number within each file.
        """
        findings: List[Finding] = []
        id_gen = _FindingIDGenerator()

        skip_deser = config.get("skip_advanced_deserialization", False)
        skip_js_cmd = config.get("skip_advanced_js_command", False)
        skip_crypto = config.get("skip_advanced_crypto", False)
        skip_path = config.get("skip_advanced_path_traversal", False)
        skip_perms = config.get("skip_advanced_permissions", False)
        skip_proto = config.get("skip_advanced_prototype_pollution", False)
        skip_http_cred = config.get("skip_advanced_http_cred", False)
        skip_nosql = config.get("skip_advanced_nosql", False)
        skip_xxe = config.get("skip_advanced_xxe", False)

        for parsed_file in parsed_files:
            # Skip lockfiles -- they do not contain executable code.
            if parsed_file.language == "lockfile":
                continue

            # --- Python-specific detections ---
            if parsed_file.language == "python":
                if not skip_deser:
                    findings.extend(
                        self._detect_unsafe_deserialization(parsed_file, id_gen)
                    )

                if not skip_crypto:
                    findings.extend(
                        self._detect_extended_weak_crypto_python(
                            parsed_file, id_gen
                        )
                    )

                if not skip_path:
                    findings.extend(
                        self._detect_path_traversal(parsed_file, id_gen)
                    )

                if not skip_perms:
                    findings.extend(
                        self._detect_unsafe_permissions(parsed_file, id_gen)
                    )

                if not skip_nosql:
                    findings.extend(
                        self._detect_python_nosql_injection(
                            parsed_file, id_gen
                        )
                    )

                if not skip_xxe:
                    findings.extend(
                        self._detect_minidom_xxe(parsed_file, id_gen)
                    )

            # --- JavaScript-specific detections ---
            if parsed_file.language == "javascript":
                if not skip_js_cmd:
                    findings.extend(
                        self._detect_js_extended_command_injection(
                            parsed_file, id_gen
                        )
                    )

                if not skip_crypto:
                    findings.extend(
                        self._detect_extended_weak_crypto_js(
                            parsed_file, id_gen
                        )
                    )

                if not skip_proto:
                    findings.extend(
                        self._detect_prototype_pollution(parsed_file, id_gen)
                    )

                if not skip_http_cred:
                    findings.extend(
                        self._detect_js_http_credential_transmission(
                            parsed_file, id_gen
                        )
                    )

        return findings

    # -----------------------------------------------------------------
    # Strategy 1: Unsafe deserialization (Python)
    # -----------------------------------------------------------------

    def _detect_unsafe_deserialization(
        self,
        parsed_file: ParseResult,
        id_gen: _FindingIDGenerator,
    ) -> List[Finding]:
        """Detect unsafe deserialization via marshal and shelve in Python.

        Scans Python source for ``marshal.loads()`` and ``shelve.open()``
        calls, which can execute arbitrary code during deserialization.

        Note: ``pickle.load/loads`` and ``yaml.load`` are already detected
        by InjectionAnalyzer; this method handles the remaining unsafe
        deserialization functions.

        Args:
            parsed_file: A single parsed file result.
            id_gen: Sequential ID generator for creating finding IDs.

        Returns:
            List of Finding objects for each unsafe deserialization found.
        """
        findings: List[Finding] = []

        if not parsed_file.raw_source:
            return findings

        raw = parsed_file.raw_source
        seen_lines: set[int] = set()

        # --- marshal.loads() detection ---
        if "marshal" in raw:
            for match in _UNSAFE_MARSHAL_LOADS.finditer(raw):
                line_number = raw[: match.start()].count("\n") + 1

                if line_number in seen_lines:
                    continue

                line_text = self._get_source_line(
                    parsed_file.source_lines, line_number
                )
                if line_text.strip().startswith("#"):
                    continue

                seen_lines.add(line_number)

                code_sample = self._build_code_sample(
                    parsed_file.source_lines, line_number
                )

                findings.append(
                    Finding(
                        id=id_gen.next_id(),
                        rule_id="unsafe-deserialization",
                        category=OWASPCategory.A08_INTEGRITY_FAILURES,
                        severity=Severity.HIGH,
                        title=(
                            "Unsafe deserialization: marshal.loads() can "
                            "execute arbitrary code"
                        ),
                        description=(
                            "The marshal module is used to deserialize data. "
                            "marshal is intended only for internal Python use "
                            "and can execute arbitrary code when loading "
                            "crafted bytecode objects. Unlike pickle, marshal "
                            "provides no safety mechanisms. If the data comes "
                            "from an untrusted source, an attacker can achieve "
                            "remote code execution."
                        ),
                        file_path=parsed_file.file_path,
                        line_number=line_number,
                        code_sample=code_sample,
                        remediation=(
                            "Never use marshal to deserialize data from "
                            "untrusted sources. Use JSON, MessagePack, or "
                            "Protocol Buffers for data interchange. The "
                            "marshal module is meant only for reading/writing "
                            "Python .pyc files and internal interpreter data."
                        ),
                        cwe_id="CWE-502",
                        confidence=0.90,
                        metadata={
                            "detection_type": "unsafe_marshal",
                            "language": parsed_file.language,
                        },
                    )
                )

        # --- shelve.open() detection ---
        if "shelve" in raw:
            for match in _UNSAFE_SHELVE_OPEN.finditer(raw):
                line_number = raw[: match.start()].count("\n") + 1

                if line_number in seen_lines:
                    continue

                line_text = self._get_source_line(
                    parsed_file.source_lines, line_number
                )
                if line_text.strip().startswith("#"):
                    continue

                seen_lines.add(line_number)

                code_sample = self._build_code_sample(
                    parsed_file.source_lines, line_number
                )

                findings.append(
                    Finding(
                        id=id_gen.next_id(),
                        rule_id="unsafe-deserialization",
                        category=OWASPCategory.A08_INTEGRITY_FAILURES,
                        severity=Severity.HIGH,
                        title=(
                            "Unsafe deserialization: shelve.open() uses "
                            "pickle internally"
                        ),
                        description=(
                            "The shelve module is used to open a persistent "
                            "dictionary. shelve uses pickle for serialization "
                            "internally, which means it inherits all of "
                            "pickle's code execution risks. A maliciously "
                            "crafted shelve database file can execute "
                            "arbitrary Python code when opened."
                        ),
                        file_path=parsed_file.file_path,
                        line_number=line_number,
                        code_sample=code_sample,
                        remediation=(
                            "Never use shelve to load data from untrusted "
                            "sources. Use a proper database (SQLite, "
                            "PostgreSQL) or JSON-based storage for persistent "
                            "data. If shelve is required for internal use, "
                            "ensure the database file is protected from "
                            "tampering with file permissions and integrity "
                            "checks."
                        ),
                        cwe_id="CWE-502",
                        confidence=0.85,
                        metadata={
                            "detection_type": "unsafe_shelve",
                            "language": parsed_file.language,
                        },
                    )
                )

        return findings

    # -----------------------------------------------------------------
    # Strategy 2: Extended JS command injection
    # -----------------------------------------------------------------

    def _detect_js_extended_command_injection(
        self,
        parsed_file: ParseResult,
        id_gen: _FindingIDGenerator,
    ) -> List[Finding]:
        """Detect extended command injection patterns in JavaScript.

        Scans JavaScript source for ``spawn()`` with ``shell: true`` and
        ``execFile()``/``execFileSync()``. These complement the existing
        InjectionAnalyzer which covers ``exec()`` and ``execSync()``.

        Args:
            parsed_file: A single parsed file result.
            id_gen: Sequential ID generator for creating finding IDs.

        Returns:
            List of Finding objects for each JS command injection found.
        """
        findings: List[Finding] = []

        if not parsed_file.raw_source:
            return findings

        raw = parsed_file.raw_source
        seen_lines: set[int] = set()

        # --- spawn() with shell: true ---
        if "spawn" in raw and "shell" in raw:
            for match in _JS_SPAWN_SHELL_TRUE.finditer(raw):
                line_number = raw[: match.start()].count("\n") + 1

                if line_number in seen_lines:
                    continue

                line_text = self._get_source_line(
                    parsed_file.source_lines, line_number
                )
                if line_text.strip().startswith("//"):
                    continue

                seen_lines.add(line_number)

                code_sample = self._build_code_sample(
                    parsed_file.source_lines, line_number
                )

                findings.append(
                    Finding(
                        id=id_gen.next_id(),
                        rule_id="command-injection",
                        category=OWASPCategory.A03_INJECTION,
                        severity=Severity.CRITICAL,
                        title=(
                            "Command injection risk: spawn() called with "
                            "shell: true"
                        ),
                        description=(
                            "The child_process.spawn() function is called "
                            "with the { shell: true } option, which causes "
                            "the command to be executed through the system "
                            "shell. This enables command injection via shell "
                            "metacharacters (; | && ` $()) if any part of "
                            "the command or arguments is derived from user "
                            "input. spawn() with shell: true is as dangerous "
                            "as exec()/execSync()."
                        ),
                        file_path=parsed_file.file_path,
                        line_number=line_number,
                        code_sample=code_sample,
                        remediation=(
                            "Remove the { shell: true } option from spawn(). "
                            "Without shell: true, spawn() passes arguments "
                            "directly to the program as an array, preventing "
                            "shell injection: spawn('cmd', ['arg1', 'arg2']). "
                            "If shell features are required, validate input "
                            "against a strict allowlist of permitted values."
                        ),
                        cwe_id="CWE-78",
                        confidence=0.90,
                        metadata={
                            "detection_type": "js_spawn_shell_true",
                            "language": parsed_file.language,
                        },
                    )
                )

        # --- execFile() / execFileSync() ---
        if "execFile" in raw:
            for match in _JS_EXEC_FILE.finditer(raw):
                line_number = raw[: match.start()].count("\n") + 1

                if line_number in seen_lines:
                    continue

                line_text = self._get_source_line(
                    parsed_file.source_lines, line_number
                )
                if line_text.strip().startswith("//"):
                    continue

                seen_lines.add(line_number)

                code_sample = self._build_code_sample(
                    parsed_file.source_lines, line_number
                )

                findings.append(
                    Finding(
                        id=id_gen.next_id(),
                        rule_id="command-injection",
                        category=OWASPCategory.A03_INJECTION,
                        severity=Severity.MEDIUM,
                        title=(
                            "Potential command injection: execFile() "
                            "executes external program"
                        ),
                        description=(
                            "The child_process.execFile() or execFileSync() "
                            "function is called. While execFile() does not "
                            "invoke a shell (making it safer than exec()), "
                            "it still executes an external program. If the "
                            "program path or arguments are derived from user "
                            "input, an attacker may be able to execute "
                            "unintended programs or pass malicious arguments."
                        ),
                        file_path=parsed_file.file_path,
                        line_number=line_number,
                        code_sample=code_sample,
                        remediation=(
                            "Validate the program path against an allowlist "
                            "of permitted executables. Validate and sanitize "
                            "all arguments. Never allow user input to control "
                            "the executable path. If possible, use a "
                            "purpose-built library instead of executing "
                            "external programs."
                        ),
                        cwe_id="CWE-78",
                        confidence=0.70,
                        metadata={
                            "detection_type": "js_exec_file",
                            "language": parsed_file.language,
                        },
                    )
                )

        return findings

    # -----------------------------------------------------------------
    # Strategy 3a: Extended weak crypto (Python)
    # -----------------------------------------------------------------

    def _detect_extended_weak_crypto_python(
        self,
        parsed_file: ParseResult,
        id_gen: _FindingIDGenerator,
    ) -> List[Finding]:
        """Detect extended weak cryptography patterns in Python.

        Scans for ``DES3.new()`` (Triple DES) which has a 64-bit block
        size vulnerable to Sweet32 birthday attacks.

        Note: DES.new(), ARC4.new(), Blowfish.new(), and MODE_ECB are
        already detected by SecretsAnalyzer.

        Args:
            parsed_file: A single parsed file result.
            id_gen: Sequential ID generator for creating finding IDs.

        Returns:
            List of Finding objects for each weak crypto usage found.
        """
        findings: List[Finding] = []

        if not parsed_file.raw_source:
            return findings

        raw = parsed_file.raw_source
        seen_lines: set[int] = set()

        # --- DES3.new() (Triple DES) ---
        if "DES3" in raw:
            for match in _WEAK_CRYPTO_DES3.finditer(raw):
                line_number = raw[: match.start()].count("\n") + 1

                if line_number in seen_lines:
                    continue

                line_text = self._get_source_line(
                    parsed_file.source_lines, line_number
                )
                if line_text.strip().startswith("#"):
                    continue

                seen_lines.add(line_number)

                code_sample = self._build_code_sample(
                    parsed_file.source_lines, line_number
                )

                findings.append(
                    Finding(
                        id=id_gen.next_id(),
                        rule_id="weak-crypto-3des",
                        category=OWASPCategory.A02_CRYPTOGRAPHIC_FAILURES,
                        severity=Severity.MEDIUM,
                        title=(
                            "Weak encryption algorithm: Triple DES (3DES)"
                        ),
                        description=(
                            "Triple DES (3DES) is used via PyCryptodome's "
                            "DES3.new(). While 3DES provides adequate key "
                            "strength (168-bit effective), it uses a 64-bit "
                            "block size which makes it vulnerable to the "
                            "Sweet32 birthday attack when encrypting large "
                            "amounts of data. NIST deprecated 3DES in 2017 "
                            "and disallowed it after 2023."
                        ),
                        file_path=parsed_file.file_path,
                        line_number=line_number,
                        code_sample=code_sample,
                        remediation=(
                            "Replace Triple DES with AES-256-GCM for "
                            "symmetric encryption. AES has a 128-bit block "
                            "size and is not vulnerable to Sweet32. Example: "
                            "from Crypto.Cipher import AES; cipher = "
                            "AES.new(key, AES.MODE_GCM)."
                        ),
                        cwe_id="CWE-327",
                        confidence=0.90,
                        metadata={
                            "detection_type": "weak_crypto_3des",
                            "language": parsed_file.language,
                        },
                    )
                )

        return findings

    # -----------------------------------------------------------------
    # Strategy 3b: Extended weak crypto (JavaScript)
    # -----------------------------------------------------------------

    def _detect_extended_weak_crypto_js(
        self,
        parsed_file: ParseResult,
        id_gen: _FindingIDGenerator,
    ) -> List[Finding]:
        """Detect extended weak cryptography patterns in JavaScript.

        Scans for:
        - Deprecated ``crypto.createCipher()`` (no IV, deterministic).
        - ``createCipheriv`` with blowfish algorithm.

        Note: createCipheriv with 'des', 'rc4', and '-ecb' are already
        detected by SecretsAnalyzer.

        Args:
            parsed_file: A single parsed file result.
            id_gen: Sequential ID generator for creating finding IDs.

        Returns:
            List of Finding objects for each weak crypto usage found.
        """
        findings: List[Finding] = []

        if not parsed_file.raw_source:
            return findings

        raw = parsed_file.raw_source
        seen_lines: set[int] = set()

        # --- Deprecated createCipher() (no IV) ---
        if "createCipher" in raw:
            for match in _JS_CREATE_CIPHER_DEPRECATED.finditer(raw):
                line_number = raw[: match.start()].count("\n") + 1

                if line_number in seen_lines:
                    continue

                line_text = self._get_source_line(
                    parsed_file.source_lines, line_number
                )
                if line_text.strip().startswith("//"):
                    continue

                # Skip if it is actually createCipheriv (safe variant).
                if _JS_CREATE_CIPHERIV.search(line_text):
                    continue

                seen_lines.add(line_number)

                code_sample = self._build_code_sample(
                    parsed_file.source_lines, line_number
                )

                findings.append(
                    Finding(
                        id=id_gen.next_id(),
                        rule_id="weak-crypto-no-iv",
                        category=OWASPCategory.A02_CRYPTOGRAPHIC_FAILURES,
                        severity=Severity.HIGH,
                        title=(
                            "Weak encryption: deprecated createCipher() "
                            "uses no initialization vector"
                        ),
                        description=(
                            "The deprecated crypto.createCipher() function "
                            "is used. This function derives the encryption "
                            "key using a simple MD5 hash and does not use an "
                            "initialization vector (IV), making the "
                            "encryption deterministic. Identical plaintexts "
                            "always produce identical ciphertexts, which "
                            "leaks information. createCipher() was deprecated "
                            "in Node.js 10 and should never be used."
                        ),
                        file_path=parsed_file.file_path,
                        line_number=line_number,
                        code_sample=code_sample,
                        remediation=(
                            "Replace createCipher() with createCipheriv() "
                            "using AES-256-GCM and a random IV: "
                            "const iv = crypto.randomBytes(16); "
                            "const cipher = crypto.createCipheriv("
                            "'aes-256-gcm', key, iv). Always generate a "
                            "fresh random IV for each encryption operation."
                        ),
                        cwe_id="CWE-327",
                        confidence=0.90,
                        metadata={
                            "detection_type": "deprecated_createCipher",
                            "language": parsed_file.language,
                        },
                    )
                )

        # --- createCipheriv with blowfish ---
        if "blowfish" in raw.lower() or "bf" in raw.lower():
            for match in _JS_CIPHERIV_BLOWFISH.finditer(raw):
                line_number = raw[: match.start()].count("\n") + 1

                if line_number in seen_lines:
                    continue

                line_text = self._get_source_line(
                    parsed_file.source_lines, line_number
                )
                if line_text.strip().startswith("//"):
                    continue

                seen_lines.add(line_number)

                code_sample = self._build_code_sample(
                    parsed_file.source_lines, line_number
                )

                findings.append(
                    Finding(
                        id=id_gen.next_id(),
                        rule_id="weak-crypto-blowfish-js",
                        category=OWASPCategory.A02_CRYPTOGRAPHIC_FAILURES,
                        severity=Severity.MEDIUM,
                        title=(
                            "Weak encryption algorithm: Blowfish (Node.js)"
                        ),
                        description=(
                            "Blowfish (bf) is used via Node.js "
                            "crypto.createCipheriv(). Blowfish has a 64-bit "
                            "block size which makes it vulnerable to birthday "
                            "attacks (Sweet32) when encrypting large amounts "
                            "of data. While not fully broken, modern "
                            "alternatives with 128-bit blocks are strongly "
                            "recommended."
                        ),
                        file_path=parsed_file.file_path,
                        line_number=line_number,
                        code_sample=code_sample,
                        remediation=(
                            "Replace Blowfish with AES-256-GCM: "
                            "crypto.createCipheriv('aes-256-gcm', key, iv). "
                            "AES has a 128-bit block size and is not "
                            "vulnerable to Sweet32 attacks."
                        ),
                        cwe_id="CWE-327",
                        confidence=0.85,
                        metadata={
                            "detection_type": "weak_crypto_blowfish_js",
                            "language": parsed_file.language,
                        },
                    )
                )

        return findings

    # -----------------------------------------------------------------
    # Strategy 4: Path traversal detection (Python)
    # -----------------------------------------------------------------

    def _detect_path_traversal(
        self,
        parsed_file: ParseResult,
        id_gen: _FindingIDGenerator,
    ) -> List[Finding]:
        """Detect path traversal vulnerabilities in Python source code.

        Scans for ``open()`` calls with f-string or .format() interpolation,
        ``os.path.join()`` with user input, and ``open()`` with variables
        that were assigned from request input.

        Args:
            parsed_file: A single parsed file result.
            id_gen: Sequential ID generator for creating finding IDs.

        Returns:
            List of Finding objects for each path traversal found.
        """
        findings: List[Finding] = []

        if not parsed_file.raw_source:
            return findings

        raw = parsed_file.raw_source
        source_lines = parsed_file.source_lines
        seen_lines: set[int] = set()

        # --- open() with f-string ---
        if "open" in raw:
            for match in _PY_OPEN_FSTRING.finditer(raw):
                line_number = raw[: match.start()].count("\n") + 1

                if line_number in seen_lines:
                    continue

                line_text = self._get_source_line(source_lines, line_number)
                if line_text.strip().startswith("#"):
                    continue

                seen_lines.add(line_number)

                code_sample = self._build_code_sample(
                    source_lines, line_number
                )

                findings.append(
                    Finding(
                        id=id_gen.next_id(),
                        rule_id="path-traversal",
                        category=OWASPCategory.A01_ACCESS_CONTROL,
                        severity=Severity.HIGH,
                        title=(
                            "Path traversal risk: open() with interpolated "
                            "path variable"
                        ),
                        description=(
                            "The open() function is called with an f-string "
                            "that interpolates a variable into the file path. "
                            "If the variable is derived from user input, an "
                            "attacker can use directory traversal sequences "
                            "(../) to read or write files outside the "
                            "intended directory, potentially accessing "
                            "sensitive system files like /etc/passwd or "
                            "application configuration files."
                        ),
                        file_path=parsed_file.file_path,
                        line_number=line_number,
                        code_sample=code_sample,
                        remediation=(
                            "Validate and sanitize user-provided file paths. "
                            "Use os.path.realpath() to resolve the path and "
                            "verify it falls within the expected base "
                            "directory: resolved = os.path.realpath(path); "
                            "assert resolved.startswith(BASE_DIR). Use "
                            "pathlib.Path.resolve() for modern Python. "
                            "Never use user input directly in file paths."
                        ),
                        cwe_id="CWE-22",
                        confidence=0.80,
                        metadata={
                            "detection_type": "open_fstring",
                            "language": parsed_file.language,
                        },
                    )
                )

            # --- open() with .format() ---
            for match in _PY_OPEN_FORMAT.finditer(raw):
                line_number = raw[: match.start()].count("\n") + 1

                if line_number in seen_lines:
                    continue

                line_text = self._get_source_line(source_lines, line_number)
                if line_text.strip().startswith("#"):
                    continue

                seen_lines.add(line_number)

                code_sample = self._build_code_sample(
                    source_lines, line_number
                )

                findings.append(
                    Finding(
                        id=id_gen.next_id(),
                        rule_id="path-traversal",
                        category=OWASPCategory.A01_ACCESS_CONTROL,
                        severity=Severity.HIGH,
                        title=(
                            "Path traversal risk: open() with .format() "
                            "path construction"
                        ),
                        description=(
                            "The open() function is called with a path "
                            "constructed using .format(). If the formatted "
                            "values include user input, an attacker can use "
                            "directory traversal sequences (../) to access "
                            "files outside the intended directory."
                        ),
                        file_path=parsed_file.file_path,
                        line_number=line_number,
                        code_sample=code_sample,
                        remediation=(
                            "Validate and sanitize user-provided file paths. "
                            "Use os.path.realpath() to resolve the path and "
                            "verify it falls within the expected base "
                            "directory. Use pathlib.Path.resolve() for "
                            "modern Python. Never use user input directly "
                            "in file paths."
                        ),
                        cwe_id="CWE-22",
                        confidence=0.75,
                        metadata={
                            "detection_type": "open_format",
                            "language": parsed_file.language,
                        },
                    )
                )

        # --- os.path.join() with user input ---
        if "os.path.join" in raw:
            for match in _PY_PATH_JOIN_USER_INPUT.finditer(raw):
                line_number = raw[: match.start()].count("\n") + 1

                if line_number in seen_lines:
                    continue

                line_text = self._get_source_line(source_lines, line_number)
                if line_text.strip().startswith("#"):
                    continue

                seen_lines.add(line_number)

                code_sample = self._build_code_sample(
                    source_lines, line_number
                )

                findings.append(
                    Finding(
                        id=id_gen.next_id(),
                        rule_id="path-traversal",
                        category=OWASPCategory.A01_ACCESS_CONTROL,
                        severity=Severity.HIGH,
                        title=(
                            "Path traversal risk: os.path.join() with "
                            "user input"
                        ),
                        description=(
                            "os.path.join() is called with user-supplied "
                            "input from request parameters. Note that "
                            "os.path.join() does NOT prevent path traversal "
                            "-- if any component is an absolute path (e.g., "
                            "'/etc/passwd'), os.path.join discards all "
                            "previous components. An attacker can use this "
                            "to access arbitrary files on the system."
                        ),
                        file_path=parsed_file.file_path,
                        line_number=line_number,
                        code_sample=code_sample,
                        remediation=(
                            "After joining paths, use os.path.realpath() to "
                            "resolve symlinks and '..' sequences, then "
                            "verify the result starts with the expected base "
                            "directory. Example: resolved = "
                            "os.path.realpath(os.path.join(base, filename)); "
                            "if not resolved.startswith(os.path.realpath("
                            "base)): raise ValueError('Invalid path')."
                        ),
                        cwe_id="CWE-22",
                        confidence=0.90,
                        metadata={
                            "detection_type": "path_join_user_input",
                            "language": parsed_file.language,
                        },
                    )
                )

        # --- open() with variable from user input (proximity check) ---
        if "open" in raw and "request" in raw:
            user_input_vars: Dict[str, int] = {}
            for var_match in _PY_USER_INPUT_VAR.finditer(raw):
                var_name = var_match.group(1)
                line_num = raw[: var_match.start()].count("\n") + 1
                user_input_vars[var_name] = line_num

            if user_input_vars:
                for open_match in _PY_OPEN_VARIABLE.finditer(raw):
                    line_number = raw[: open_match.start()].count("\n") + 1

                    if line_number in seen_lines:
                        continue

                    var_name = open_match.group(1)

                    # Check if this variable was assigned from user input
                    # within ~10 lines before.
                    if var_name in user_input_vars:
                        assign_line = user_input_vars[var_name]
                        if (
                            assign_line < line_number
                            and (line_number - assign_line) <= 10
                        ):
                            line_text = self._get_source_line(
                                source_lines, line_number
                            )
                            if line_text.strip().startswith("#"):
                                continue

                            seen_lines.add(line_number)

                            code_sample = self._build_code_sample(
                                source_lines, line_number
                            )

                            findings.append(
                                Finding(
                                    id=id_gen.next_id(),
                                    rule_id="path-traversal",
                                    category=OWASPCategory.A01_ACCESS_CONTROL,
                                    severity=Severity.HIGH,
                                    title=(
                                        "Path traversal risk: open() with "
                                        "user-controlled path variable"
                                    ),
                                    description=(
                                        f"The open() function is called with "
                                        f"the variable '{var_name}' which "
                                        f"appears to be assigned from user "
                                        f"input. An attacker can supply "
                                        f"directory traversal sequences "
                                        f"(../) to access files outside the "
                                        f"intended directory."
                                    ),
                                    file_path=parsed_file.file_path,
                                    line_number=line_number,
                                    code_sample=code_sample,
                                    remediation=(
                                        "Validate and sanitize user-provided "
                                        "file paths. Use os.path.realpath() "
                                        "to resolve the path and verify it "
                                        "falls within the expected base "
                                        "directory. Never pass user input "
                                        "directly to open()."
                                    ),
                                    cwe_id="CWE-22",
                                    confidence=0.85,
                                    metadata={
                                        "detection_type": (
                                            "open_user_input_variable"
                                        ),
                                        "variable_name": var_name,
                                        "language": parsed_file.language,
                                    },
                                )
                            )

        return findings

    # -----------------------------------------------------------------
    # Strategy 5: Unsafe file permissions (Python)
    # -----------------------------------------------------------------

    def _detect_unsafe_permissions(
        self,
        parsed_file: ParseResult,
        id_gen: _FindingIDGenerator,
    ) -> List[Finding]:
        """Detect unsafe file permission settings in Python.

        Scans for ``os.chmod()`` calls with world-writable modes (0o777,
        0o666) which allow any user on the system to read, write, and
        potentially execute the file.

        Args:
            parsed_file: A single parsed file result.
            id_gen: Sequential ID generator for creating finding IDs.

        Returns:
            List of Finding objects for each unsafe permission found.
        """
        findings: List[Finding] = []

        if not parsed_file.raw_source:
            return findings

        raw = parsed_file.raw_source

        if "os.chmod" not in raw:
            return findings

        seen_lines: set[int] = set()

        for match in _UNSAFE_CHMOD.finditer(raw):
            line_number = raw[: match.start()].count("\n") + 1

            if line_number in seen_lines:
                continue

            line_text = self._get_source_line(
                parsed_file.source_lines, line_number
            )
            if line_text.strip().startswith("#"):
                continue

            seen_lines.add(line_number)

            code_sample = self._build_code_sample(
                parsed_file.source_lines, line_number
            )

            # Determine which mode was used.
            mode = "0o777" if "0o777" in line_text else "0o666"
            mode_desc = (
                "read, write, and execute" if mode == "0o777"
                else "read and write"
            )

            findings.append(
                Finding(
                    id=id_gen.next_id(),
                    rule_id="unsafe-file-permissions",
                    category=OWASPCategory.A05_SECURITY_MISCONFIGURATION,
                    severity=Severity.MEDIUM,
                    title=(
                        f"Unsafe file permissions: os.chmod() with "
                        f"world-writable mode {mode}"
                    ),
                    description=(
                        f"The file permissions are set to {mode}, which "
                        f"grants {mode_desc} access to ALL users on the "
                        f"system. This violates the principle of least "
                        f"privilege and can allow unauthorized users to "
                        f"read sensitive data, modify configuration files, "
                        f"or inject malicious code."
                    ),
                    file_path=parsed_file.file_path,
                    line_number=line_number,
                    code_sample=code_sample,
                    remediation=(
                        "Use the most restrictive permissions possible. "
                        "For files that only the owner needs to access, "
                        "use 0o600 (owner read/write). For files that a "
                        "group needs to read, use 0o640. For executable "
                        "files, use 0o750 (owner rwx, group rx). Never "
                        "use 0o777 or 0o666 in production code."
                    ),
                    cwe_id="CWE-732",
                    confidence=0.90,
                    metadata={
                        "detection_type": "unsafe_chmod",
                        "mode": mode,
                        "language": parsed_file.language,
                    },
                )
            )

        return findings

    # -----------------------------------------------------------------
    # Strategy 6: Prototype pollution (JavaScript)
    # -----------------------------------------------------------------

    def _detect_prototype_pollution(
        self,
        parsed_file: ParseResult,
        id_gen: _FindingIDGenerator,
    ) -> List[Finding]:
        """Detect prototype pollution vulnerabilities in JavaScript.

        Scans for ``Object.assign()``, ``_.merge()``, and spread operators
        used with direct user input from ``req.body``, ``req.query``, or
        ``req.params``. These patterns allow attackers to inject properties
        like ``__proto__`` or ``constructor.prototype`` to pollute the
        Object prototype and affect all objects in the application.

        Args:
            parsed_file: A single parsed file result.
            id_gen: Sequential ID generator for creating finding IDs.

        Returns:
            List of Finding objects for each prototype pollution found.
        """
        findings: List[Finding] = []

        if not parsed_file.raw_source:
            return findings

        raw = parsed_file.raw_source
        seen_lines: set[int] = set()

        proto_patterns = [
            (
                _JS_OBJECT_ASSIGN_USER_INPUT,
                "Object.assign() with user input",
                "Object.assign() merges properties from req.body/req.query/"
                "req.params directly into a target object. An attacker can "
                "send a payload containing __proto__ or constructor."
                "prototype properties to pollute the Object prototype, "
                "affecting all objects in the application. This can lead "
                "to denial of service, property injection, or in some "
                "cases remote code execution.",
                0.85,
            ),
            (
                _JS_LODASH_MERGE_USER_INPUT,
                "_.merge() / lodash.merge() with user input",
                "lodash's _.merge() is used with user input from req.body/"
                "req.query/req.params. _.merge() performs a deep merge "
                "which recursively assigns properties, including prototype "
                "chain properties like __proto__. This is a well-known "
                "prototype pollution vector that has been assigned multiple "
                "CVEs (e.g., CVE-2018-3721, CVE-2019-10744).",
                0.90,
            ),
            (
                _JS_SPREAD_USER_INPUT,
                "Spread operator with user input",
                "The spread operator (...) is used with req.body/req.query/"
                "req.params directly in an object literal. While the spread "
                "operator in object literals does not pollute the prototype "
                "chain in modern engines, it copies all enumerable "
                "properties from user input into the target object, which "
                "can lead to mass assignment vulnerabilities where "
                "attackers inject unexpected properties.",
                0.70,
            ),
        ]

        for pattern, detail, description, confidence in proto_patterns:
            for match in pattern.finditer(raw):
                line_number = raw[: match.start()].count("\n") + 1

                if line_number in seen_lines:
                    continue

                line_text = self._get_source_line(
                    parsed_file.source_lines, line_number
                )
                if line_text.strip().startswith("//"):
                    continue

                seen_lines.add(line_number)

                code_sample = self._build_code_sample(
                    parsed_file.source_lines, line_number
                )

                findings.append(
                    Finding(
                        id=id_gen.next_id(),
                        rule_id="prototype-pollution",
                        category=OWASPCategory.A03_INJECTION,
                        severity=Severity.HIGH,
                        title=(
                            f"Prototype pollution risk: {detail}"
                        ),
                        description=description,
                        file_path=parsed_file.file_path,
                        line_number=line_number,
                        code_sample=code_sample,
                        remediation=(
                            "Never merge user input directly into objects. "
                            "Validate input against an explicit schema using "
                            "Joi, Zod, or express-validator. Extract only "
                            "expected fields: const { name, email } = "
                            "req.body. For deep merging, use a library with "
                            "prototype pollution protection or filter out "
                            "__proto__, constructor, and prototype keys "
                            "before merging. Consider using Object.create("
                            "null) for the target object to prevent "
                            "prototype chain access."
                        ),
                        cwe_id="CWE-1321",
                        confidence=confidence,
                        metadata={
                            "detection_type": "prototype_pollution",
                            "language": parsed_file.language,
                        },
                    )
                )

        return findings

    # -----------------------------------------------------------------
    # Strategy 7: HTTP credential transmission (JavaScript)
    # -----------------------------------------------------------------

    def _detect_js_http_credential_transmission(
        self,
        parsed_file: ParseResult,
        id_gen: _FindingIDGenerator,
    ) -> List[Finding]:
        """Detect credentials transmitted over HTTP in JavaScript.

        Scans for ``fetch()`` and ``axios`` calls using ``http://`` URLs
        that target authentication-related endpoints (/login, /auth,
        /token, /api-key, etc.), and ``http.request()``/``http.get()``
        targeting similar paths.

        Note: Python cleartext credential transmission is already detected
        by SecretsAnalyzer; this method covers JavaScript patterns.

        Args:
            parsed_file: A single parsed file result.
            id_gen: Sequential ID generator for creating finding IDs.

        Returns:
            List of Finding objects for each HTTP credential transmission.
        """
        findings: List[Finding] = []

        if not parsed_file.raw_source:
            return findings

        raw = parsed_file.raw_source

        if "http://" not in raw:
            return findings

        seen_lines: set[int] = set()

        http_patterns = [
            (
                _JS_HTTP_AUTH_ENDPOINT,
                "fetch/axios with HTTP URL to auth endpoint",
                0.85,
            ),
            (
                _JS_HTTP_MODULE_AUTH,
                "http module request to auth endpoint",
                0.80,
            ),
        ]

        for pattern, detail, confidence in http_patterns:
            for match in pattern.finditer(raw):
                line_number = raw[: match.start()].count("\n") + 1

                if line_number in seen_lines:
                    continue

                line_text = self._get_source_line(
                    parsed_file.source_lines, line_number
                )
                if line_text.strip().startswith("//"):
                    continue

                seen_lines.add(line_number)

                code_sample = self._build_code_sample(
                    parsed_file.source_lines, line_number
                )

                findings.append(
                    Finding(
                        id=id_gen.next_id(),
                        rule_id="cleartext-credential-transmission",
                        category=OWASPCategory.A02_CRYPTOGRAPHIC_FAILURES,
                        severity=Severity.HIGH,
                        title=(
                            "Credentials transmitted over cleartext HTTP "
                            "(JavaScript)"
                        ),
                        description=(
                            f"An HTTP request ({detail}) targets an "
                            "authentication-related endpoint over an "
                            "unencrypted HTTP connection. Credentials, "
                            "tokens, and session data sent over HTTP can "
                            "be intercepted by any network observer via "
                            "passive eavesdropping, man-in-the-middle "
                            "attacks, or network sniffing."
                        ),
                        file_path=parsed_file.file_path,
                        line_number=line_number,
                        code_sample=code_sample,
                        remediation=(
                            "Always use HTTPS (https://) for authentication "
                            "and sensitive data endpoints. Enforce TLS for "
                            "all API endpoints that accept credentials. "
                            "Configure HSTS headers to prevent protocol "
                            "downgrade attacks. Use environment variables "
                            "for base URLs so they can be configured to "
                            "use HTTPS in production."
                        ),
                        cwe_id="CWE-319",
                        confidence=confidence,
                        metadata={
                            "detection_type": "js_http_credential",
                            "language": parsed_file.language,
                        },
                    )
                )

        return findings

    # -----------------------------------------------------------------
    # Strategy 8: Python NoSQL injection (pymongo)
    # -----------------------------------------------------------------

    def _detect_python_nosql_injection(
        self,
        parsed_file: ParseResult,
        id_gen: _FindingIDGenerator,
    ) -> List[Finding]:
        """Detect NoSQL injection in Python pymongo queries.

        Scans Python source for pymongo collection methods (``find()``,
        ``find_one()``, ``update_one()``, etc.) used with unsanitized
        Flask/Django request input within approximately 10 lines.

        Note: JavaScript NoSQL injection (Mongoose) is already detected
        by InjectionAnalyzer; this method covers the Python/pymongo case.

        Args:
            parsed_file: A single parsed file result.
            id_gen: Sequential ID generator for creating finding IDs.

        Returns:
            List of Finding objects for each Python NoSQL injection found.
        """
        findings: List[Finding] = []

        if not parsed_file.raw_source:
            return findings

        raw = parsed_file.raw_source
        source_lines = parsed_file.source_lines

        # Quick check: skip files that don't use both pymongo-like
        # methods and request input.
        if not _PY_NOSQL_USER_INPUT.search(raw):
            return findings

        seen_lines: set[int] = set()

        for match in _PY_PYMONGO_METHODS.finditer(raw):
            line_number = raw[: match.start()].count("\n") + 1

            if line_number in seen_lines:
                continue

            # Check if user input appears within ~5 lines before/after.
            context_start = max(0, line_number - 6)
            context_end = min(len(source_lines), line_number + 5)
            context_block = "\n".join(source_lines[context_start:context_end])

            if not _PY_NOSQL_USER_INPUT.search(context_block):
                continue

            line_text = self._get_source_line(source_lines, line_number)
            if line_text.strip().startswith("#"):
                continue

            seen_lines.add(line_number)

            code_sample = self._build_code_sample(source_lines, line_number)

            findings.append(
                Finding(
                    id=id_gen.next_id(),
                    rule_id="nosql-injection",
                    category=OWASPCategory.A03_INJECTION,
                    severity=Severity.HIGH,
                    title=(
                        "NoSQL injection: pymongo query with unsanitized "
                        "user input"
                    ),
                    description=(
                        "A pymongo collection method receives values that "
                        "appear to come from Flask/Django request input "
                        "(request.json, request.form, etc.) without "
                        "sanitization. An attacker can send MongoDB query "
                        "operators like {\"$gt\": \"\"}, {\"$ne\": null}, "
                        "or {\"$regex\": \".*\"} to manipulate query logic, "
                        "bypass authentication, or extract data. For example, "
                        "sending {\"password\": {\"$ne\": null}} would match "
                        "any document with a non-null password."
                    ),
                    file_path=parsed_file.file_path,
                    line_number=line_number,
                    code_sample=code_sample,
                    remediation=(
                        "Validate and sanitize user input before passing it "
                        "to pymongo queries. Use explicit type casting: "
                        "{'username': str(request.json.get('username'))}. "
                        "Validate input schema with Marshmallow, Pydantic, "
                        "or WTForms. Strip MongoDB operators from input by "
                        "rejecting keys starting with '$'. For "
                        "authentication queries, always hash passwords "
                        "before comparing."
                    ),
                    cwe_id="CWE-943",
                    confidence=0.85,
                    metadata={
                        "detection_type": "pymongo_user_input",
                        "language": parsed_file.language,
                    },
                )
            )

        return findings

    # -----------------------------------------------------------------
    # Strategy 9: XML DOM minidom XXE detection
    # -----------------------------------------------------------------

    def _detect_minidom_xxe(
        self,
        parsed_file: ParseResult,
        id_gen: _FindingIDGenerator,
    ) -> List[Finding]:
        """Detect XXE vulnerabilities via xml.dom.minidom in Python.

        Scans for ``xml.dom.minidom.parseString()`` and
        ``xml.dom.minidom.parse()`` calls. The minidom parser may be
        vulnerable to XXE attacks in older Python versions.

        Note: ET.fromstring/parse, lxml, and xml.sax are already detected
        by InjectionAnalyzer; this covers the minidom case.

        Args:
            parsed_file: A single parsed file result.
            id_gen: Sequential ID generator for creating finding IDs.

        Returns:
            List of Finding objects for each minidom XXE found.
        """
        findings: List[Finding] = []

        if not parsed_file.raw_source:
            return findings

        raw = parsed_file.raw_source

        if "minidom" not in raw:
            return findings

        # Skip files using defusedxml.
        if _XXE_DEFUSED.search(raw):
            return findings

        seen_lines: set[int] = set()

        for match in _XXE_MINIDOM.finditer(raw):
            line_number = raw[: match.start()].count("\n") + 1

            if line_number in seen_lines:
                continue

            line_text = self._get_source_line(
                parsed_file.source_lines, line_number
            )
            if line_text.strip().startswith("#"):
                continue

            seen_lines.add(line_number)

            code_sample = self._build_code_sample(
                parsed_file.source_lines, line_number
            )

            findings.append(
                Finding(
                    id=id_gen.next_id(),
                    rule_id="xxe-vulnerability",
                    category=OWASPCategory.A03_INJECTION,
                    severity=Severity.MEDIUM,
                    title=(
                        "XXE risk: xml.dom.minidom parsing may allow "
                        "external entity expansion"
                    ),
                    description=(
                        "The xml.dom.minidom module is used to parse XML "
                        "data. In older Python versions, minidom may resolve "
                        "external entities, enabling XXE attacks that can "
                        "read local files (e.g., /etc/passwd), perform SSRF "
                        "against internal services, or cause denial of "
                        "service via recursive entity expansion (billion "
                        "laughs attack)."
                    ),
                    file_path=parsed_file.file_path,
                    line_number=line_number,
                    code_sample=code_sample,
                    remediation=(
                        "Use defusedxml instead of the stdlib XML parsers: "
                        "from defusedxml.minidom import parseString, parse. "
                        "defusedxml disables external entity resolution, DTD "
                        "processing, and other dangerous features by default. "
                        "Install with: pip install defusedxml."
                    ),
                    cwe_id="CWE-611",
                    confidence=0.75,
                    metadata={
                        "detection_type": "minidom_xxe",
                        "language": parsed_file.language,
                    },
                )
            )

        return findings

    # -----------------------------------------------------------------
    # Helper methods
    # -----------------------------------------------------------------

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
    def _get_source_line(source_lines: List[str], line_number: int) -> str:
        """Get a single source line by 1-based line number.

        Args:
            source_lines: The source file split into lines.
            line_number: 1-based line number.

        Returns:
            The source line content, or an empty string if out of range.
        """
        idx = line_number - 1
        if 0 <= idx < len(source_lines):
            return source_lines[idx]
        return ""
