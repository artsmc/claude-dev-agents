"""Security assessment result model.

Defines the ProjectInfo and AssessmentResult dataclasses that represent
the complete output of a security quality assessment run. ProjectInfo
captures metadata about the scanned project, while AssessmentResult
aggregates all findings, suppression counts, and analyzer version
information into a single result object.

Classes:
    ProjectInfo: Metadata about the assessed project.
    AssessmentResult: Complete assessment output with findings and scoring.

Example:
    >>> from lib.models.finding import Finding, Severity, OWASPCategory
    >>> project = ProjectInfo(
    ...     name="my-app",
    ...     path="/home/user/my-app",
    ...     files_analyzed=150,
    ...     scan_duration=3.45,
    ...     timestamp="2026-02-08T12:00:00",
    ... )
    >>> result = AssessmentResult(
    ...     project=project,
    ...     findings=[],
    ...     analyzer_versions={"secrets": "1.0", "injection": "1.0"},
    ... )
    >>> result.calculate_risk_score()
    0
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from .finding import Finding, Severity


@dataclass
class ProjectInfo:
    """Metadata about the project being assessed.

    Captures identification and performance metrics for the scan target.
    All fields are set at the start or end of an assessment run and remain
    immutable for the lifetime of the result.

    Attributes:
        name: Human-readable project name (e.g., "my-web-app"). Typically
            derived from the directory name or a configuration file.
        path: Absolute filesystem path to the project root directory.
        files_analyzed: Total count of source files that were scanned
            during the assessment.
        scan_duration: Wall-clock duration of the assessment in seconds,
            measured from scan start to scan completion.
        timestamp: ISO 8601 formatted string recording when the assessment
            was initiated (e.g., "2026-02-08T14:30:00+00:00").

    Example:
        >>> info = ProjectInfo(
        ...     name="backend-api",
        ...     path="/opt/projects/backend-api",
        ...     files_analyzed=87,
        ...     scan_duration=2.31,
        ...     timestamp="2026-02-08T14:30:00+00:00",
        ... )
    """

    name: str
    path: str
    files_analyzed: int
    scan_duration: float
    timestamp: str

    @staticmethod
    def make_timestamp() -> str:
        """Generate a UTC ISO 8601 timestamp for the current moment.

        Returns:
            str: Current UTC time in ISO 8601 format, e.g.
                "2026-02-08T14:30:00+00:00".
        """
        return datetime.now(timezone.utc).isoformat()


@dataclass
class AssessmentResult:
    """Complete security assessment result.

    Aggregates all findings produced by the security analyzers along with
    project metadata, suppression statistics, and analyzer version
    information. Provides convenience methods for severity-based
    aggregation and risk scoring.

    Attributes:
        project: Metadata about the assessed project.
        findings: List of security findings detected during the scan.
            Defaults to an empty list.
        suppressed_count: Number of findings that matched a suppression
            rule and were excluded from the findings list. Defaults to 0.
        analyzer_versions: Mapping of analyzer name to its version string.
            For example: {"secrets": "1.0", "injection": "1.0"}.
            Defaults to an empty dict.
        errors: List of non-fatal error messages collected during the
            assessment run. Each entry is a human-readable string
            describing a file that could not be read, a parser that
            failed, an API call that timed out, etc. These errors did
            not prevent the assessment from completing but indicate
            that some results may be incomplete. Defaults to an empty
            list.

    Example:
        >>> from lib.models.finding import Finding, Severity, OWASPCategory
        >>> project = ProjectInfo(
        ...     name="demo",
        ...     path="/tmp/demo",
        ...     files_analyzed=10,
        ...     scan_duration=0.5,
        ...     timestamp="2026-02-08T12:00:00",
        ... )
        >>> result = AssessmentResult(project=project)
        >>> result.get_severity_counts()
        {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}
        >>> result.calculate_risk_score()
        0
    """

    project: ProjectInfo
    findings: List[Finding] = field(default_factory=list)
    suppressed_count: int = 0
    analyzer_versions: Dict[str, str] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)

    def get_severity_counts(self) -> Dict[str, int]:
        """Count findings grouped by severity level.

        Iterates through all findings and tallies them into four severity
        buckets. The returned dictionary always contains all four keys,
        even when counts are zero.

        Returns:
            Dict[str, int]: Mapping of severity name to finding count.
                Keys are always "CRITICAL", "HIGH", "MEDIUM", and "LOW".

        Example:
            >>> result.get_severity_counts()
            {'CRITICAL': 2, 'HIGH': 5, 'MEDIUM': 10, 'LOW': 3}
        """
        counts: Dict[str, int] = {
            "CRITICAL": 0,
            "HIGH": 0,
            "MEDIUM": 0,
            "LOW": 0,
        }
        for finding in self.findings:
            severity_key = finding.severity.value
            if severity_key in counts:
                counts[severity_key] += 1
        return counts

    def calculate_risk_score(self) -> int:
        """Calculate a weighted risk score based on finding severities.

        Each finding contributes to the total score according to its
        severity level:
            - CRITICAL: 10 points per finding
            - HIGH: 5 points per finding
            - MEDIUM: 2 points per finding
            - LOW: 1 point per finding

        A score of 0 indicates no findings were detected. Higher scores
        indicate greater overall security risk.

        Returns:
            int: Total weighted risk score (0 or greater).

        Example:
            >>> # 2 CRITICAL + 3 HIGH + 1 MEDIUM + 4 LOW
            >>> # (2 * 10) + (3 * 5) + (1 * 2) + (4 * 1) = 41
            >>> result.calculate_risk_score()
            41
        """
        weights: Dict[str, int] = {
            "CRITICAL": 10,
            "HIGH": 5,
            "MEDIUM": 2,
            "LOW": 1,
        }
        counts = self.get_severity_counts()
        score = 0
        for severity, count in counts.items():
            score += count * weights[severity]
        return score

    def to_dict(self) -> Dict[str, Any]:
        """Convert the assessment result to a plain dictionary.

        Produces a JSON-serializable representation of the entire
        assessment. ProjectInfo fields are inlined under the "project"
        key, and each Finding is serialized via its own ``to_dict()``
        method.

        Returns:
            Dict[str, Any]: Complete dictionary representation of the
                assessment result, suitable for ``json.dumps()``.
        """
        return {
            "project": {
                "name": self.project.name,
                "path": self.project.path,
                "files_analyzed": self.project.files_analyzed,
                "scan_duration": self.project.scan_duration,
                "timestamp": self.project.timestamp,
            },
            "findings": [f.to_dict() for f in self.findings],
            "suppressed_count": self.suppressed_count,
            "analyzer_versions": dict(self.analyzer_versions),
            "severity_counts": self.get_severity_counts(),
            "risk_score": self.calculate_risk_score(),
            "errors": list(self.errors),
        }
