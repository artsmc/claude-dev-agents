"""Base analyzer interface for architecture quality assessment.

This module defines the abstract base class for all architecture
analyzers. Analyzers examine parsed code structures and dependency
graphs to detect violations of architectural principles.

References:
    - TR.md Section 2.1: Analyzer Architecture
    - TR.md Section 3.1: Violation Model
    - FRS.md FR-2.x through FR-6.x: Analysis Dimensions
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from ..models.config import AssessmentConfig
from ..models.violation import Violation


logger = logging.getLogger(__name__)


@dataclass
class AnalysisContext:
    """Context information for analysis execution.

    Provides analyzers with access to project structure, configuration,
    and shared state from other analyzers.

    Attributes:
        project_root: Absolute path to the project root directory.
        config: Assessment configuration including thresholds and rules.
        file_paths: List of all source file paths to analyze.
        metadata: Shared metadata dictionary for inter-analyzer communication.
        dependency_graph: Optional dependency graph if available.
            Set by the graph builder before running analyzers.
    """

    project_root: Path
    config: AssessmentConfig
    file_paths: List[Path] = field(default_factory=list)
    metadata: Dict[str, any] = field(default_factory=dict)
    dependency_graph: Optional[any] = None


class AnalyzerError(Exception):
    """Base exception for analyzer errors.

    Raised when analysis fails in a way that prevents completion.
    """

    pass


class BaseAnalyzer(ABC):
    """Abstract base class for architecture quality analyzers.

    Each analyzer focuses on a specific dimension of architecture
    quality (e.g., coupling, layer separation, SOLID principles).
    Analyzers produce violations with severity levels and
    actionable recommendations.

    Subclasses must implement:
        - analyze(): Main analysis entry point
        - get_name(): Analyzer identifier
        - get_description(): Human-readable description

    Example:
        >>> class CouplingAnalyzer(BaseAnalyzer):
        ...     def analyze(self, context: AnalysisContext) -> List[Violation]:
        ...         violations = []
        ...         # Analyze coupling and create violations
        ...         return violations
        ...
        ...     def get_name(self) -> str:
        ...         return "coupling"
        ...
        ...     def get_description(self) -> str:
        ...         return "Analyzes module coupling and dependency metrics"
    """

    def __init__(self):
        """Initialize the analyzer with default configuration."""
        self.logger = logging.getLogger(self.__class__.__name__)
        self._violations: List[Violation] = []
        self._violation_counter: Dict[str, int] = {}

    @abstractmethod
    def analyze(self, context: AnalysisContext) -> List[Violation]:
        """Perform architecture analysis and return violations.

        Args:
            context: Analysis context with project info and configuration.

        Returns:
            List of violations detected during analysis.

        Raises:
            AnalyzerError: If a fatal analysis error occurs.
        """
        pass

    @abstractmethod
    def get_name(self) -> str:
        """Get the analyzer's unique identifier.

        Returns:
            Lowercase identifier (e.g., "coupling", "layer", "solid").
        """
        pass

    @abstractmethod
    def get_description(self) -> str:
        """Get a human-readable description of what this analyzer does.

        Returns:
            Brief description suitable for help text and reports.
        """
        pass

    def is_enabled(self, config: AssessmentConfig) -> bool:
        """Check if this analyzer is enabled in the configuration.

        Args:
            config: Assessment configuration to check.

        Returns:
            True if this analyzer should run.

        Note:
            If enabled_analyzers list is empty, all analyzers are enabled.
        """
        enabled = config.analysis.enabled_analyzers
        if not enabled:
            return True
        return self.get_name() in enabled

    def create_violation(
        self,
        type_prefix: str,
        violation_type: str,
        severity: str,
        file_path: str,
        message: str,
        explanation: str = "",
        recommendation: str = "",
        line_number: Optional[int] = None,
        metadata: Optional[Dict] = None,
    ) -> Violation:
        """Create a violation with an auto-generated ID.

        Generates a unique violation ID based on the type prefix
        and an incrementing counter.

        Args:
            type_prefix: Prefix for the violation ID (e.g., "LSV", "CPL").
            violation_type: Classification string (e.g., "LayerViolation").
            severity: Severity level (CRITICAL, HIGH, MEDIUM, LOW).
            file_path: Path to the file containing the violation.
            message: Short human-readable summary.
            explanation: Detailed description of the violation.
            recommendation: Actionable guidance for fixing.
            line_number: Line number where violation occurs.
            metadata: Additional violation-specific data.

        Returns:
            Violation instance with a unique ID.

        Example:
            >>> violation = self.create_violation(
            ...     type_prefix="CPL",
            ...     violation_type="HighCoupling",
            ...     severity="HIGH",
            ...     file_path="src/app.py",
            ...     message="Module has high coupling (FAN-OUT: 15)",
            ...     recommendation="Reduce dependencies by extracting shared logic"
            ... )
        """
        # Generate unique ID
        counter = self._violation_counter.get(type_prefix, 0) + 1
        self._violation_counter[type_prefix] = counter
        violation_id = f"{type_prefix}-{counter:03d}"

        return Violation(
            id=violation_id,
            type=violation_type,
            severity=severity,
            file_path=file_path,
            line_number=line_number,
            message=message,
            explanation=explanation,
            recommendation=recommendation,
            dimension=self.get_name(),
            metadata=metadata or {},
        )

    def add_violation(self, violation: Violation) -> None:
        """Add a violation to the internal collection.

        Args:
            violation: Violation to add.
        """
        self._violations.append(violation)
        self.logger.debug(f"Added violation {violation.id}: {violation.message}")

    def get_violations(self) -> List[Violation]:
        """Get all violations collected during analysis.

        Returns:
            List of violations.
        """
        return self._violations.copy()

    def clear_violations(self) -> None:
        """Clear all collected violations.

        Useful when reusing an analyzer instance for multiple analyses.
        """
        self._violations.clear()
        self._violation_counter.clear()

    def should_analyze_file(self, file_path: Path, context: AnalysisContext) -> bool:
        """Check if a file should be analyzed.

        Args:
            file_path: Path to check.
            context: Analysis context with configuration.

        Returns:
            True if the file should be analyzed.

        Note:
            Default implementation checks excluded_paths patterns.
            Subclasses can override for analyzer-specific filtering.
        """
        # Check excluded patterns
        excluded_patterns = context.config.analysis.excluded_paths
        for pattern in excluded_patterns:
            # Simple glob-style matching
            if pattern.endswith("/"):
                # Directory pattern
                if pattern.rstrip("/") in str(file_path):
                    return False
            elif pattern.startswith("*"):
                # Extension pattern
                if str(file_path).endswith(pattern[1:]):
                    return False
            elif pattern in str(file_path):
                # Substring match
                return False

        return True

    def log_progress(self, message: str, **kwargs) -> None:
        """Log an analysis progress message.

        Args:
            message: Progress message to log.
            **kwargs: Additional context for logging.
        """
        self.logger.info(message, extra=kwargs)

    def analyze_safely(self, context: AnalysisContext) -> List[Violation]:
        """Perform analysis with comprehensive error handling.

        Wraps analyze() with error handling to ensure graceful
        degradation. Logs errors but does not raise exceptions.

        Args:
            context: Analysis context.

        Returns:
            List of violations if analysis succeeded, empty list if failed.
        """
        try:
            self.clear_violations()
            return self.analyze(context)
        except AnalyzerError as e:
            self.logger.error(
                f"Analysis failed in {self.get_name()}: {e}"
            )
            return []
        except Exception as e:
            self.logger.error(
                f"Unexpected error in {self.get_name()}: {e}",
                exc_info=True,
            )
            return []


__all__ = [
    "AnalysisContext",
    "AnalyzerError",
    "BaseAnalyzer",
]
