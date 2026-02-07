"""Assessment data models for architecture quality analysis.

This module defines the core data structures used to represent
a complete architecture quality assessment result, including
project detection information and the full assessment output.

Classes:
    ProjectInfo: Project detection and identification data.
    AssessmentResult: Complete assessment result with metrics,
        violations, and serialization methods.
"""

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional

from .metrics import ProjectMetrics
from .violation import Violation


@dataclass
class ProjectInfo:
    """Project detection information.

    Captures the detected project type, framework, and architecture
    pattern for the analyzed codebase. Populated during the project
    detection phase of assessment.

    Attributes:
        name: Human-readable project name (typically directory name).
        path: Absolute filesystem path to the project root.
        project_type: Detected project type identifier
            (e.g., ``nextjs``, ``python-fastapi``, ``react``).
        framework: Human-readable framework name
            (e.g., ``Next.js``, ``FastAPI``, ``Express``).
        framework_version: Detected framework version string,
            or ``None`` if version could not be determined.
        architecture_pattern: Detected architecture pattern
            (e.g., ``app_router``, ``three-tier``, ``mvc``),
            or ``None`` if no pattern was identified.
    """

    name: str
    path: str
    project_type: str
    framework: str
    framework_version: Optional[str] = None
    architecture_pattern: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization.

        Returns:
            Dictionary with all project info fields. ``None`` values
            are included as ``null`` in the output.
        """
        return {
            "name": self.name,
            "path": self.path,
            "project_type": self.project_type,
            "framework": self.framework,
            "framework_version": self.framework_version,
            "architecture_pattern": self.architecture_pattern,
        }


@dataclass
class AssessmentResult:
    """Complete assessment result for a project.

    Aggregates all analysis outputs into a single result object.
    Provides serialization to both dictionary (for JSON output) and
    markdown (for human-readable reports).

    Attributes:
        metadata: Assessment metadata including generation timestamp,
            analysis duration in seconds, tool version, and any other
            contextual information about the assessment run.
        project_info: Detected project identification and type info.
        metrics: Calculated project quality metrics (coupling,
            cohesion, module counts, etc.).
        violations: Ordered list of detected architecture violations,
            typically sorted by severity (critical first).
    """

    metadata: Dict[str, Any]
    project_info: ProjectInfo
    metrics: ProjectMetrics
    violations: List[Violation] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization.

        Recursively converts all nested dataclasses to dictionaries.
        The output structure matches the JSON report schema defined
        in the technical requirements.

        Uses ``dataclasses.asdict`` for metrics serialization to
        ensure deep conversion of nested dataclass fields (e.g.,
        ``CouplingMetrics``, ``SOLIDMetrics``).

        Returns:
            Fully serializable dictionary suitable for ``json.dumps``.
        """
        # Use asdict for metrics to handle nested dataclass fields
        # (CouplingMetrics, SOLIDMetrics) that need recursive conversion.
        metrics_dict = (
            self.metrics.to_dict()
            if hasattr(self.metrics, "to_dict")
            else asdict(self.metrics)
        )

        return {
            "metadata": dict(self.metadata),
            "project_info": self.project_info.to_dict(),
            "metrics": metrics_dict,
            "summary": self._build_summary(),
            "violations": [v.to_dict() for v in self.violations],
        }

    def to_markdown(self) -> str:
        """Generate a markdown report of the assessment.

        Produces a structured markdown document containing an
        executive summary, project overview, metrics breakdown,
        and a detailed violations listing organized by severity.

        Returns:
            Complete markdown string ready for file output.
        """
        lines: List[str] = []

        # Header
        lines.append("# Architecture Quality Assessment Report")
        lines.append("")

        # Metadata
        generated_at = self.metadata.get("generated_at", "N/A")
        duration = self.metadata.get("duration_seconds", "N/A")
        lines.append(f"**Generated**: {generated_at}")
        lines.append(f"**Duration**: {duration}s")
        lines.append("")

        # Project info
        lines.append("---")
        lines.append("")
        lines.append("## 1. Project Overview")
        lines.append("")
        lines.append(f"**Project**: {self.project_info.name}")
        lines.append(f"**Path**: {self.project_info.path}")
        lines.append(f"**Type**: {self.project_info.project_type}")
        lines.append(f"**Framework**: {self.project_info.framework}")
        if self.project_info.framework_version:
            lines.append(
                f"**Framework Version**: {self.project_info.framework_version}"
            )
        if self.project_info.architecture_pattern:
            lines.append(
                f"**Architecture Pattern**: "
                f"{self.project_info.architecture_pattern}"
            )
        lines.append("")

        # Executive summary
        summary = self._build_summary()
        lines.append("---")
        lines.append("")
        lines.append("## 2. Executive Summary")
        lines.append("")
        lines.append(
            f"**Total Violations**: {summary['total_violations']}"
        )
        lines.append(f"**Critical**: {summary['critical']}")
        lines.append(f"**High**: {summary['high']}")
        lines.append(f"**Medium**: {summary['medium']}")
        lines.append(f"**Low**: {summary['low']}")
        lines.append("")

        # Metrics
        lines.append("---")
        lines.append("")
        lines.append("## 3. Metrics")
        lines.append("")
        metrics_dict = (
            self.metrics.to_dict()
            if hasattr(self.metrics, "to_dict")
            else asdict(self.metrics)
        )
        for key, value in metrics_dict.items():
            label = key.replace("_", " ").title()
            lines.append(f"- **{label}**: {value}")
        lines.append("")

        # Violations by severity
        lines.append("---")
        lines.append("")
        lines.append("## 4. Violations")
        lines.append("")

        if not self.violations:
            lines.append("No violations detected.")
            lines.append("")
        else:
            severity_order = ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
            for severity in severity_order:
                severity_violations = [
                    v for v in self.violations
                    if v.severity.upper() == severity
                ]
                if severity_violations:
                    lines.append(
                        f"### {severity} ({len(severity_violations)})"
                    )
                    lines.append("")
                    for violation in severity_violations:
                        lines.append(
                            f"- **{violation.type}**: "
                            f"{violation.message}"
                        )
                        lines.append(
                            f"  - File: `{violation.file_path}`"
                        )
                        if violation.line_number is not None:
                            lines.append(
                                f"  - Line: {violation.line_number}"
                            )
                        if violation.recommendation:
                            lines.append(
                                f"  - Recommendation: "
                                f"{violation.recommendation}"
                            )
                        lines.append("")

        # Footer
        lines.append("---")
        lines.append("")
        lines.append(
            "*Report generated by Architecture Quality Assessment Skill*"
        )
        lines.append("")

        return "\n".join(lines)

    def _build_summary(self) -> Dict[str, int]:
        """Build violation summary counts by severity.

        Returns:
            Dictionary with total and per-severity violation counts.
        """
        counts: Dict[str, int] = {
            "total_violations": len(self.violations),
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0,
        }
        for violation in self.violations:
            severity_key = violation.severity.lower()
            if severity_key in counts:
                counts[severity_key] += 1
        return counts
