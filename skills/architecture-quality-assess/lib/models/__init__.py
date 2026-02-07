"""Data models for architecture quality assessment."""

from .assessment import AssessmentResult, ProjectInfo
from .config import (
    AnalysisConfig,
    AssessmentConfig,
    CouplingThresholds,
    LayerDefinition,
    ProjectConfig,
    ReportingConfig,
    SOLIDThresholds,
)
from .metrics import CouplingMetrics, ProjectMetrics, SOLIDMetrics
from .project_type import ProjectType
from .violation import Violation

__all__ = [
    "AnalysisConfig",
    "AssessmentConfig",
    "AssessmentResult",
    "CouplingMetrics",
    "CouplingThresholds",
    "LayerDefinition",
    "ProjectConfig",
    "ProjectInfo",
    "ProjectMetrics",
    "ProjectType",
    "ReportingConfig",
    "SOLIDMetrics",
    "SOLIDThresholds",
    "Violation",
]
