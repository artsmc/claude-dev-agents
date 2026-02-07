"""Violation model for architecture quality assessment.

Defines the Violation dataclass representing a single architectural violation
detected during code analysis. Violations are categorized by type and severity,
and include contextual information for generating actionable reports.

References:
    - TR.md Section 3.1: Core Data Structures
    - FRS.md FR-2.x through FR-6.x: Violation categories
    - SKILL.md: JSON output format
"""

from dataclasses import dataclass, field
from typing import Any, Dict, Optional


# Valid severity levels in descending order of importance.
VALID_SEVERITIES = frozenset({"CRITICAL", "HIGH", "MEDIUM", "LOW"})

# Valid violation dimension categories.
VALID_DIMENSIONS = frozenset({
    "layer",
    "solid",
    "patterns",
    "coupling",
    "organization",
    "drift",
})


def validate_severity(severity: str) -> str:
    """Validate and normalize a severity string.

    Args:
        severity: Severity level string (case-insensitive).

    Returns:
        Uppercase severity string.

    Raises:
        ValueError: If severity is not one of CRITICAL, HIGH, MEDIUM, LOW.
    """
    normalized = severity.upper()
    if normalized not in VALID_SEVERITIES:
        raise ValueError(
            f"Invalid severity '{severity}'. "
            f"Must be one of: {', '.join(sorted(VALID_SEVERITIES))}"
        )
    return normalized


@dataclass
class Violation:
    """Represents a single architectural violation detected during analysis.

    A Violation captures a specific architecture quality issue found in the
    codebase, including its location, severity, and a recommendation for
    how to resolve it.

    Attributes:
        id: Unique identifier for the violation (e.g., "LSV-001", "SRP-003").
        type: Classification of the violation (e.g., "LayerViolation",
            "CircularDependency", "HighCoupling", "SRPViolation").
        severity: Severity level -- one of CRITICAL, HIGH, MEDIUM, LOW.
        file_path: Relative path to the file containing the violation.
        line_number: Line number where the violation occurs (None if not
            applicable to a specific line).
        message: Short human-readable summary of the violation.
        explanation: Detailed description of why this is a violation and
            what architectural principle it breaks.
        recommendation: Actionable guidance on how to fix the violation.
        dimension: The analysis dimension that detected this violation
            (e.g., "layer", "solid", "patterns", "coupling").
        metadata: Additional key-value data specific to the violation type
            (e.g., fan_out count, dependency cycle path).

    Example:
        >>> v = Violation(
        ...     id="LSV-001",
        ...     type="LayerViolation",
        ...     severity="CRITICAL",
        ...     file_path="src/app/api/users/route.ts",
        ...     line_number=12,
        ...     message="SQL in API Route",
        ...     explanation="Direct SQL query found in route handler, "
        ...                 "violating layer separation.",
        ...     recommendation="Move database access to a service layer.",
        ...     dimension="layer",
        ... )
        >>> v.severity
        'CRITICAL'
    """

    id: str
    type: str
    severity: str
    file_path: str
    line_number: Optional[int] = None
    message: str = ""
    explanation: str = ""
    recommendation: str = ""
    dimension: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate fields after initialization."""
        self.severity = validate_severity(self.severity)

    def to_dict(self) -> Dict[str, Any]:
        """Convert the violation to a plain dictionary for JSON serialization.

        Returns:
            Dictionary with all violation fields. The structure matches the
            JSON output format defined in SKILL.md and TR.md Section 3.1.
        """
        return {
            "id": self.id,
            "type": self.type,
            "severity": self.severity,
            "file_path": self.file_path,
            "line_number": self.line_number,
            "message": self.message,
            "explanation": self.explanation,
            "recommendation": self.recommendation,
            "dimension": self.dimension,
            "metadata": self.metadata,
        }

    def __str__(self) -> str:
        """Return a human-readable summary of the violation.

        Format: [SEVERITY] id: message (file_path:line_number)
        """
        location = self.file_path
        if self.line_number is not None:
            location = f"{self.file_path}:{self.line_number}"
        return f"[{self.severity}] {self.id}: {self.message} ({location})"

    def __repr__(self) -> str:
        """Return an unambiguous string representation for debugging."""
        return (
            f"Violation("
            f"id={self.id!r}, "
            f"type={self.type!r}, "
            f"severity={self.severity!r}, "
            f"file_path={self.file_path!r}, "
            f"line_number={self.line_number!r}, "
            f"message={self.message!r}, "
            f"dimension={self.dimension!r}"
            f")"
        )
