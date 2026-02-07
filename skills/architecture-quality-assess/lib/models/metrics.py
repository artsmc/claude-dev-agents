"""Metrics data models for architecture quality assessment.

This module defines the core metric dataclasses used throughout the
assessment pipeline to represent coupling analysis results, SOLID
principles compliance scores, and aggregated project-level metrics.
"""

from dataclasses import dataclass, field
from typing import Dict, List


# -- Score interpretation thresholds --
_SCORE_EXCELLENT = 90
_SCORE_GOOD = 75
_SCORE_FAIR = 60


def _interpret_score(score: int) -> str:
    """Return a human-readable label for a 0-100 quality score.

    Args:
        score: An integer between 0 and 100 inclusive.

    Returns:
        One of 'Excellent', 'Good', 'Fair', or 'Poor'.
    """
    if score >= _SCORE_EXCELLENT:
        return "Excellent"
    if score >= _SCORE_GOOD:
        return "Good"
    if score >= _SCORE_FAIR:
        return "Fair"
    return "Poor"


@dataclass
class CouplingMetrics:
    """Coupling metrics for a single module.

    Attributes:
        module_path: Relative path to the module being measured.
        fan_in: Count of modules that depend on this module.
        fan_out: Count of modules this module depends on.
        instability: Ratio ``fan_out / (fan_in + fan_out)``.
            A value of 0.0 indicates maximum stability (many dependents,
            few dependencies).  A value of 1.0 indicates maximum
            instability (many dependencies, few dependents).
        dependencies: Module paths this module directly imports/uses.
        dependents: Module paths that directly import/use this module.
    """

    module_path: str
    fan_in: int
    fan_out: int
    instability: float
    dependencies: List[str] = field(default_factory=list)
    dependents: List[str] = field(default_factory=list)

    # -- helpers -------------------------------------------------------

    @property
    def is_highly_coupled(self) -> bool:
        """Return ``True`` when fan-out exceeds the recommended limit of 15."""
        return self.fan_out > 15

    @property
    def is_stable(self) -> bool:
        """Return ``True`` when instability is below 0.5."""
        return self.instability < 0.5


@dataclass
class SOLIDMetrics:
    """SOLID principles compliance metrics.

    Each individual principle is scored on a 0-100 scale.  The
    ``overall_score`` is a weighted composite of the five sub-scores.

    Attributes:
        overall_score: Aggregate SOLID compliance score (0-100).
        srp_score: Single Responsibility Principle score.
        ocp_score: Open/Closed Principle score.
        lsp_score: Liskov Substitution Principle score.
        isp_score: Interface Segregation Principle score.
        dip_score: Dependency Inversion Principle score.
        violations_count: Total number of SOLID violations detected.
    """

    overall_score: int
    srp_score: int
    ocp_score: int
    lsp_score: int
    isp_score: int
    dip_score: int
    violations_count: int

    # -- helpers -------------------------------------------------------

    @property
    def rating(self) -> str:
        """Return a human-readable rating for the overall SOLID score."""
        return _interpret_score(self.overall_score)

    def per_principle_scores(self) -> Dict[str, int]:
        """Return a mapping of principle abbreviation to its score.

        Useful for iteration and reporting.
        """
        return {
            "SRP": self.srp_score,
            "OCP": self.ocp_score,
            "LSP": self.lsp_score,
            "ISP": self.isp_score,
            "DIP": self.dip_score,
        }

    @property
    def weakest_principle(self) -> str:
        """Return the abbreviation of the principle with the lowest score."""
        scores = self.per_principle_scores()
        return min(scores, key=scores.get)  # type: ignore[arg-type]


@dataclass
class ProjectMetrics:
    """Aggregated project-level architecture quality metrics.

    This is the top-level metrics container produced by a full
    assessment run.  It holds severity counts, per-module coupling
    data, and the SOLID compliance summary.

    Attributes:
        overall_score: Overall architecture quality score (0-100).
        total_files: Number of source files analysed.
        total_modules: Number of logical modules detected.
        total_violations: Sum of all violations across categories.
        critical_count: Violations at *critical* severity.
        high_count: Violations at *high* severity.
        medium_count: Violations at *medium* severity.
        low_count: Violations at *low* severity.
        coupling: Per-module coupling metrics keyed by module path.
        solid: Aggregated SOLID principles compliance metrics.
    """

    overall_score: int
    total_files: int
    total_modules: int
    total_violations: int
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int
    coupling: Dict[str, CouplingMetrics] = field(default_factory=dict)
    solid: SOLIDMetrics = field(
        default_factory=lambda: SOLIDMetrics(
            overall_score=0,
            srp_score=0,
            ocp_score=0,
            lsp_score=0,
            isp_score=0,
            dip_score=0,
            violations_count=0,
        )
    )

    # -- helpers -------------------------------------------------------

    @property
    def rating(self) -> str:
        """Return a human-readable rating for the overall project score."""
        return _interpret_score(self.overall_score)

    @property
    def has_critical_issues(self) -> bool:
        """Return ``True`` when at least one critical violation exists."""
        return self.critical_count > 0

    def severity_summary(self) -> Dict[str, int]:
        """Return a mapping of severity label to its count.

        Useful for iteration, serialisation, and report generation.
        """
        return {
            "critical": self.critical_count,
            "high": self.high_count,
            "medium": self.medium_count,
            "low": self.low_count,
        }

    def most_coupled_modules(self, limit: int = 5) -> List[CouplingMetrics]:
        """Return the top *limit* modules sorted by fan-out descending.

        Args:
            limit: Maximum number of modules to return.

        Returns:
            A list of :class:`CouplingMetrics` ordered by ``fan_out``
            from highest to lowest.
        """
        sorted_modules = sorted(
            self.coupling.values(),
            key=lambda m: m.fan_out,
            reverse=True,
        )
        return sorted_modules[:limit]
