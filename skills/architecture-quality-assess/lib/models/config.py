"""Configuration models for architecture quality assessment.

This module defines configuration dataclasses used to customize
assessment behavior, including thresholds, rules, and reporting
preferences. Configuration can be loaded from .arch-quality.json
files or programmatically constructed.

References:
    - TR.md Section 9.3: Configuration File Schema
    - TR.md Appendix B: Configuration Template
    - FRS.md FR-10.4: Configuration Override Support
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class CouplingThresholds:
    """Thresholds for coupling metrics violations.

    Attributes:
        fan_out_medium: FAN-OUT threshold for MEDIUM severity.
        fan_out_high: FAN-OUT threshold for HIGH severity.
        fan_in_god_module: FAN-IN threshold for God Module detection.
        instability_stable: Maximum instability for "stable" classification.
    """

    fan_out_medium: int = 7
    fan_out_high: int = 10
    fan_in_god_module: int = 20
    instability_stable: float = 0.5


@dataclass
class SOLIDThresholds:
    """Thresholds for SOLID principles analysis.

    Attributes:
        srp_max_methods: Maximum methods per class (SRP).
        srp_max_loc: Maximum lines of code per class (SRP).
        srp_lcom_threshold: LCOM (Lack of Cohesion) threshold.
        isp_max_methods: Maximum interface methods (ISP).
        isp_usage_ratio: Minimum method usage ratio (ISP).
    """

    srp_max_methods: int = 10
    srp_max_loc: int = 500
    srp_lcom_threshold: float = 0.8
    isp_max_methods: int = 10
    isp_usage_ratio: float = 0.5


@dataclass
class AnalysisConfig:
    """Configuration for analysis behavior and scope.

    Attributes:
        enabled_analyzers: List of analyzer names to run.
            Valid values: "coupling", "layer", "solid", "patterns", "drift".
            Empty list means run all analyzers.
        excluded_paths: Glob patterns for paths to exclude from analysis.
        incremental: Enable incremental analysis using git diff.
        cache_enabled: Enable result caching for faster repeated runs.
        timeout_seconds: Maximum analysis duration before timeout.
    """

    enabled_analyzers: List[str] = field(default_factory=list)
    excluded_paths: List[str] = field(
        default_factory=lambda: [
            "node_modules/",
            ".git/",
            "__pycache__/",
            "*.test.js",
            "*.test.ts",
            "*.spec.py",
            "test_*.py",
            "venv/",
            ".venv/",
            "build/",
            "dist/",
        ]
    )
    incremental: bool = False
    cache_enabled: bool = True
    timeout_seconds: int = 300


@dataclass
class ReportingConfig:
    """Configuration for report generation.

    Attributes:
        format: Output format ("markdown", "json", or "both").
        output_dir: Directory for generated reports.
        include_metadata: Include analysis metadata in output.
        severity_filter: Minimum severity to include in report.
            Valid values: "CRITICAL", "HIGH", "MEDIUM", "LOW".
            None means include all severities.
        group_by: Grouping strategy for violations in report.
            Valid values: "severity", "dimension", "file".
    """

    format: str = "markdown"
    output_dir: str = "."
    include_metadata: bool = True
    severity_filter: Optional[str] = None
    group_by: str = "severity"


@dataclass
class LayerDefinition:
    """Definition of an architectural layer for a project type.

    Attributes:
        name: Layer name (e.g., "presentation", "business", "data").
        patterns: File path patterns that identify files in this layer.
        allowed_dependencies: Names of layers this layer may depend on.
        description: Human-readable description of the layer's purpose.
    """

    name: str
    patterns: List[str]
    allowed_dependencies: List[str] = field(default_factory=list)
    description: str = ""


@dataclass
class ProjectConfig:
    """Project-specific configuration and architecture rules.

    Attributes:
        project_name: Human-readable project name.
        project_type: Detected or manually specified project type.
        custom_layers: User-defined layer definitions.
            If empty, framework-specific defaults are used.
        documented_patterns: Expected design patterns (from Memory Bank).
        coupling_thresholds: Custom coupling thresholds.
        solid_thresholds: Custom SOLID thresholds.
    """

    project_name: str = ""
    project_type: str = "unknown"
    custom_layers: List[LayerDefinition] = field(default_factory=list)
    documented_patterns: Dict[str, str] = field(default_factory=dict)
    coupling_thresholds: CouplingThresholds = field(
        default_factory=CouplingThresholds
    )
    solid_thresholds: SOLIDThresholds = field(
        default_factory=SOLIDThresholds
    )


@dataclass
class AssessmentConfig:
    """Complete configuration for an architecture quality assessment.

    Top-level configuration container that combines all configuration
    categories. Can be loaded from .arch-quality.json or constructed
    programmatically.

    Attributes:
        version: Configuration schema version.
        project: Project-specific configuration.
        analysis: Analysis behavior configuration.
        reporting: Report generation configuration.
    """

    version: str = "1.0"
    project: ProjectConfig = field(default_factory=ProjectConfig)
    analysis: AnalysisConfig = field(default_factory=AnalysisConfig)
    reporting: ReportingConfig = field(default_factory=ReportingConfig)

    def to_dict(self) -> Dict:
        """Convert configuration to dictionary for JSON serialization.

        Returns:
            Dictionary representation of the complete configuration.
        """
        from dataclasses import asdict
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> "AssessmentConfig":
        """Create configuration from dictionary.

        Args:
            data: Dictionary representation of configuration,
                typically loaded from JSON file.

        Returns:
            AssessmentConfig instance with values from dictionary.

        Note:
            Missing fields will use default values defined in dataclasses.
        """
        # Extract nested configurations
        project_data = data.get("project", {})
        analysis_data = data.get("analysis", {})
        reporting_data = data.get("reporting", {})

        # Build nested dataclasses
        coupling_thresholds = CouplingThresholds(
            **project_data.get("coupling_thresholds", {})
        )
        solid_thresholds = SOLIDThresholds(
            **project_data.get("solid_thresholds", {})
        )

        # Handle custom layers
        custom_layers = []
        for layer_data in project_data.get("custom_layers", []):
            custom_layers.append(LayerDefinition(**layer_data))

        project = ProjectConfig(
            project_name=project_data.get("project_name", ""),
            project_type=project_data.get("project_type", "unknown"),
            custom_layers=custom_layers,
            documented_patterns=project_data.get("documented_patterns", {}),
            coupling_thresholds=coupling_thresholds,
            solid_thresholds=solid_thresholds,
        )

        analysis = AnalysisConfig(**analysis_data)
        reporting = ReportingConfig(**reporting_data)

        return cls(
            version=data.get("version", "1.0"),
            project=project,
            analysis=analysis,
            reporting=reporting,
        )

    def validate(self) -> List[str]:
        """Validate configuration for common errors.

        Returns:
            List of validation error messages. Empty list if valid.
        """
        errors = []

        # Validate reporting format
        valid_formats = {"markdown", "json", "both"}
        if self.reporting.format not in valid_formats:
            errors.append(
                f"Invalid reporting format '{self.reporting.format}'. "
                f"Must be one of: {', '.join(valid_formats)}"
            )

        # Validate severity filter
        if self.reporting.severity_filter is not None:
            valid_severities = {"CRITICAL", "HIGH", "MEDIUM", "LOW"}
            if self.reporting.severity_filter not in valid_severities:
                errors.append(
                    f"Invalid severity filter '{self.reporting.severity_filter}'. "
                    f"Must be one of: {', '.join(valid_severities)}"
                )

        # Validate grouping strategy
        valid_groupings = {"severity", "dimension", "file"}
        if self.reporting.group_by not in valid_groupings:
            errors.append(
                f"Invalid group_by '{self.reporting.group_by}'. "
                f"Must be one of: {', '.join(valid_groupings)}"
            )

        # Validate timeout
        if self.analysis.timeout_seconds <= 0:
            errors.append("timeout_seconds must be positive")

        # Validate threshold values
        if self.project.coupling_thresholds.fan_out_medium < 1:
            errors.append("fan_out_medium must be >= 1")
        if (
            self.project.coupling_thresholds.fan_out_high
            < self.project.coupling_thresholds.fan_out_medium
        ):
            errors.append("fan_out_high must be >= fan_out_medium")

        return errors
