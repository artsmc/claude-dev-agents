"""Security vulnerability finding model.

Defines the core Finding dataclass and supporting enumerations used
throughout the security quality assessment skill. Findings represent
individual security vulnerabilities detected during code analysis.

Enumerations:
    Severity: Risk severity levels (CRITICAL, HIGH, MEDIUM, LOW).
    OWASPCategory: OWASP Top 10 (2021) vulnerability categories (A01-A10).

Classes:
    Finding: Immutable data record for a single security vulnerability.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional


class Severity(str, Enum):
    """Finding severity levels.

    Inherits from str to enable direct JSON serialization of enum values.
    Ordered from most to least severe for sorting purposes.

    Members:
        CRITICAL: Exploitable vulnerability with severe impact.
        HIGH: Significant security risk requiring prompt remediation.
        MEDIUM: Moderate risk that should be addressed in normal cycle.
        LOW: Minor issue or informational finding.
    """

    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class OWASPCategory(str, Enum):
    """OWASP Top 10 (2021) categories.

    Maps each OWASP Top 10 2021 risk category to its standard identifier
    (A01 through A10). Inherits from str for JSON-friendly serialization.

    Reference: https://owasp.org/Top10/

    Members:
        A01_ACCESS_CONTROL: Broken Access Control.
        A02_CRYPTOGRAPHIC_FAILURES: Cryptographic Failures.
        A03_INJECTION: Injection (SQL, NoSQL, OS, LDAP).
        A04_INSECURE_DESIGN: Insecure Design.
        A05_SECURITY_MISCONFIGURATION: Security Misconfiguration.
        A06_VULNERABLE_COMPONENTS: Vulnerable and Outdated Components.
        A07_AUTH_FAILURES: Identification and Authentication Failures.
        A08_INTEGRITY_FAILURES: Software and Data Integrity Failures.
        A09_LOGGING_FAILURES: Security Logging and Monitoring Failures.
        A10_SSRF: Server-Side Request Forgery.
    """

    A01_ACCESS_CONTROL = "A01"
    A02_CRYPTOGRAPHIC_FAILURES = "A02"
    A03_INJECTION = "A03"
    A04_INSECURE_DESIGN = "A04"
    A05_SECURITY_MISCONFIGURATION = "A05"
    A06_VULNERABLE_COMPONENTS = "A06"
    A07_AUTH_FAILURES = "A07"
    A08_INTEGRITY_FAILURES = "A08"
    A09_LOGGING_FAILURES = "A09"
    A10_SSRF = "A10"


@dataclass
class Finding:
    """Security vulnerability finding.

    Represents a single security issue detected during code analysis.
    Each finding ties a detected vulnerability to a specific location
    in the codebase, along with classification metadata and remediation
    guidance.

    Attributes:
        id: Unique finding identifier (e.g., "SEC-001"). Generated
            sequentially per analysis run.
        rule_id: Detection rule identifier (e.g., "hardcoded-secret").
            Maps back to the rule definition that triggered this finding.
        category: OWASP Top 10 (2021) category classification.
        severity: Risk severity level of the finding.
        title: Short human-readable title summarizing the vulnerability.
        description: Detailed description of the security issue, including
            why it is dangerous and under what conditions it is exploitable.
        file_path: Relative path to the file containing the vulnerability.
        line_number: Line number in the file where the issue occurs.
        code_sample: Vulnerable code snippet with surrounding context
            (typically 3 lines).
        remediation: Actionable guidance on how to fix the vulnerability.
        cwe_id: Optional CWE identifier (e.g., "CWE-798") linking to the
            Common Weakness Enumeration database.
        confidence: Detection confidence score from 0.0 (lowest) to 1.0
            (highest). Defaults to 1.0 for deterministic pattern matches.
        metadata: Optional dictionary for additional analyzer-specific data
            such as matched patterns, dependency versions, or risk scores.

    Example:
        >>> finding = Finding(
        ...     id="SEC-001",
        ...     rule_id="hardcoded-secret",
        ...     category=OWASPCategory.A02_CRYPTOGRAPHIC_FAILURES,
        ...     severity=Severity.CRITICAL,
        ...     title="Hardcoded API key detected",
        ...     description="An API key is hardcoded in source code.",
        ...     file_path="src/config.py",
        ...     line_number=42,
        ...     code_sample='API_KEY = "sk-live-abc123..."',
        ...     remediation="Move secrets to environment variables.",
        ...     cwe_id="CWE-798",
        ... )
        >>> finding.to_dict()["severity"]
        'CRITICAL'
    """

    id: str
    rule_id: str
    category: OWASPCategory
    severity: Severity
    title: str
    description: str
    file_path: str
    line_number: int
    code_sample: str
    remediation: str
    cwe_id: Optional[str] = None
    confidence: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert the finding to a plain dictionary for JSON serialization.

        Enum fields are serialized to their string values. The metadata
        field is guaranteed to be a dictionary (never None).

        Returns:
            Dict[str, Any]: Dictionary representation of the finding with
                all enum values resolved to their string form.
        """
        return {
            "id": self.id,
            "rule_id": self.rule_id,
            "category": self.category.value,
            "severity": self.severity.value,
            "title": self.title,
            "description": self.description,
            "file_path": self.file_path,
            "line_number": self.line_number,
            "code_sample": self.code_sample,
            "remediation": self.remediation,
            "cwe_id": self.cwe_id,
            "confidence": self.confidence,
            "metadata": self.metadata,
        }
