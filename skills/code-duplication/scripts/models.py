#!/usr/bin/env python3
"""
Data Models for Code Duplication Analysis Skill

This module defines all core data structures used throughout the skill.
Uses Python dataclasses for clean, type-safe data models.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from pathlib import Path
from enum import Enum


class DuplicateType(Enum):
    """Type of code duplication detected."""
    EXACT = "exact"
    STRUCTURAL = "structural"
    PATTERN = "pattern"


class RefactoringTechnique(Enum):
    """Recommended refactoring technique for duplicates."""
    EXTRACT_FUNCTION = "extract_function"
    EXTRACT_CLASS = "extract_class"
    USE_INHERITANCE = "use_inheritance"
    USE_COMPOSITION = "use_composition"
    EXTRACT_UTILITY = "extract_utility"
    USE_TEMPLATE_METHOD = "use_template_method"
    PARAMETERIZE_FUNCTION = "parameterize_function"


@dataclass
class CodeLocation:
    """Represents a specific location in source code."""

    file_path: str
    start_line: int
    end_line: int
    line_count: int

    @property
    def location_string(self) -> str:
        """Format as 'file:start-end'."""
        return f"{self.file_path}:{self.start_line}-{self.end_line}"

    def __str__(self) -> str:
        return self.location_string


@dataclass
class CodeBlock:
    """Represents a block of code content."""

    location: CodeLocation
    raw_code: str
    normalized_code: str
    hash_value: str

    @property
    def file_path(self) -> str:
        """Convenience accessor for file path."""
        return self.location.file_path

    @property
    def line_count(self) -> int:
        """Convenience accessor for line count."""
        return self.location.line_count


@dataclass
class RefactoringSuggestion:
    """Represents a specific refactoring suggestion for a duplicate."""

    technique: RefactoringTechnique
    description: str
    estimated_loc_reduction: int
    implementation_steps: List[str]
    example_code: Optional[str] = None
    difficulty: str = "medium"  # easy, medium, hard

    @property
    def technique_name(self) -> str:
        """Human-readable technique name."""
        return self.technique.value.replace('_', ' ').title()


@dataclass
class DuplicateBlock:
    """Represents a block of duplicated code found across multiple locations."""

    id: int
    type: DuplicateType
    hash: str
    instances: List[CodeLocation]
    code_sample: str
    similarity_score: float = 1.0  # 1.0 for exact, <1.0 for structural
    suggestion: Optional[RefactoringSuggestion] = None

    @property
    def instance_count(self) -> int:
        """Number of duplicate instances."""
        return len(self.instances)

    @property
    def loc_per_instance(self) -> int:
        """Lines of code per instance."""
        if not self.instances:
            return 0
        return self.instances[0].line_count

    @property
    def total_duplicate_loc(self) -> int:
        """Total lines of duplicated code across all instances."""
        return sum(loc.line_count for loc in self.instances)

    @property
    def potential_loc_reduction(self) -> int:
        """Estimated lines that could be saved by refactoring."""
        # Keep one instance, remove others
        if self.instance_count <= 1:
            return 0
        return self.total_duplicate_loc - self.loc_per_instance

    @property
    def affected_files(self) -> List[str]:
        """List of unique files affected by this duplicate."""
        return sorted(set(loc.file_path for loc in self.instances))


@dataclass
class FileOffender:
    """Represents a file with duplication metrics."""

    file_path: str
    total_loc: int
    duplicate_loc: int
    duplicate_blocks: List[int]  # IDs of duplicate blocks in this file

    @property
    def duplication_percentage(self) -> float:
        """Percentage of file that is duplicated."""
        if self.total_loc == 0:
            return 0.0
        return (self.duplicate_loc / self.total_loc) * 100

    @property
    def duplicate_block_count(self) -> int:
        """Number of duplicate blocks in this file."""
        return len(self.duplicate_blocks)


@dataclass
class HeatmapEntry:
    """Represents a single entry in the duplication heatmap."""

    file_path: str
    duplication_percentage: float
    duplicate_loc: int
    total_loc: int
    block_count: int

    @property
    def heat_level(self) -> str:
        """Categorize heat level for visualization."""
        if self.duplication_percentage >= 30:
            return "critical"
        elif self.duplication_percentage >= 20:
            return "high"
        elif self.duplication_percentage >= 10:
            return "medium"
        elif self.duplication_percentage >= 5:
            return "low"
        else:
            return "minimal"


@dataclass
class HeatmapData:
    """Complete heatmap data for the codebase."""

    entries: List[HeatmapEntry]

    @property
    def sorted_by_percentage(self) -> List[HeatmapEntry]:
        """Entries sorted by duplication percentage (descending)."""
        return sorted(self.entries, key=lambda e: e.duplication_percentage, reverse=True)

    @property
    def sorted_by_loc(self) -> List[HeatmapEntry]:
        """Entries sorted by duplicate LOC (descending)."""
        return sorted(self.entries, key=lambda e: e.duplicate_loc, reverse=True)

    def top_n(self, n: int = 10) -> List[HeatmapEntry]:
        """Get top N files by duplication percentage."""
        return self.sorted_by_percentage[:n]


@dataclass
class AnalysisMetadata:
    """Metadata about the analysis execution."""

    analysis_date: str
    analysis_duration_seconds: float
    project_root: Path
    config_used: Optional[str] = None
    git_commit: Optional[str] = None

    @property
    def duration_formatted(self) -> str:
        """Human-readable duration."""
        if self.analysis_duration_seconds < 60:
            return f"{self.analysis_duration_seconds:.1f}s"
        minutes = self.analysis_duration_seconds / 60
        if minutes < 60:
            return f"{minutes:.1f}m"
        hours = minutes / 60
        return f"{hours:.1f}h"


@dataclass
class AnalysisSummary:
    """Summary statistics for the duplication analysis."""

    total_files: int
    total_loc: int
    duplicate_loc: int
    duplicate_blocks: int
    exact_blocks: int = 0
    structural_blocks: int = 0
    pattern_blocks: int = 0

    @property
    def duplication_percentage(self) -> float:
        """Overall duplication percentage."""
        if self.total_loc == 0:
            return 0.0
        return (self.duplicate_loc / self.total_loc) * 100

    @property
    def analyzed_files_count(self) -> int:
        """Alias for total_files."""
        return self.total_files


@dataclass
class AnalysisResult:
    """Complete analysis result with all findings."""

    summary: AnalysisSummary
    duplicates: List[DuplicateBlock]
    top_offenders: List[FileOffender]
    heatmap: HeatmapData
    metadata: AnalysisMetadata

    @property
    def total_potential_reduction(self) -> int:
        """Total LOC that could be saved by refactoring all duplicates."""
        return sum(dup.potential_loc_reduction for dup in self.duplicates)

    @property
    def blocks_with_suggestions(self) -> int:
        """Count of duplicate blocks with refactoring suggestions."""
        return sum(1 for dup in self.duplicates if dup.suggestion is not None)

    @property
    def suggestion_coverage(self) -> float:
        """Percentage of blocks with suggestions."""
        if len(self.duplicates) == 0:
            return 0.0
        return (self.blocks_with_suggestions / len(self.duplicates)) * 100

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "summary": {
                "total_files": self.summary.total_files,
                "total_loc": self.summary.total_loc,
                "duplicate_loc": self.summary.duplicate_loc,
                "duplication_percentage": self.summary.duplication_percentage,
                "duplicate_blocks": self.summary.duplicate_blocks,
                "exact_blocks": self.summary.exact_blocks,
                "structural_blocks": self.summary.structural_blocks,
                "pattern_blocks": self.summary.pattern_blocks,
            },
            "duplicates": [
                {
                    "id": dup.id,
                    "type": dup.type.value,
                    "instance_count": dup.instance_count,
                    "loc_per_instance": dup.loc_per_instance,
                    "total_duplicate_loc": dup.total_duplicate_loc,
                    "potential_reduction": dup.potential_loc_reduction,
                    "similarity_score": dup.similarity_score,
                    "instances": [loc.location_string for loc in dup.instances],
                    "code_sample": dup.code_sample[:200] + "..." if len(dup.code_sample) > 200 else dup.code_sample,
                    "suggestion": {
                        "technique": dup.suggestion.technique.value,
                        "description": dup.suggestion.description,
                        "estimated_reduction": dup.suggestion.estimated_loc_reduction,
                        "difficulty": dup.suggestion.difficulty,
                    } if dup.suggestion else None,
                }
                for dup in self.duplicates
            ],
            "top_offenders": [
                {
                    "file_path": off.file_path,
                    "total_loc": off.total_loc,
                    "duplicate_loc": off.duplicate_loc,
                    "duplication_percentage": off.duplication_percentage,
                    "block_count": off.duplicate_block_count,
                }
                for off in self.top_offenders
            ],
            "heatmap": [
                {
                    "file_path": entry.file_path,
                    "duplication_percentage": entry.duplication_percentage,
                    "duplicate_loc": entry.duplicate_loc,
                    "total_loc": entry.total_loc,
                    "heat_level": entry.heat_level,
                }
                for entry in self.heatmap.entries
            ],
            "metadata": {
                "analysis_date": self.metadata.analysis_date,
                "duration": self.metadata.duration_formatted,
                "project_root": str(self.metadata.project_root),
                "config_used": self.metadata.config_used,
                "git_commit": self.metadata.git_commit,
            },
            "potential_reduction": {
                "total_loc_reduction": self.total_potential_reduction,
                "percentage_of_codebase": (self.total_potential_reduction / self.summary.total_loc * 100) if self.summary.total_loc > 0 else 0,
                "blocks_with_suggestions": self.blocks_with_suggestions,
                "suggestion_coverage": self.suggestion_coverage,
            }
        }


@dataclass
class Config:
    """Configuration for duplication analysis."""

    # Detection thresholds
    min_lines: int = 7
    similarity_threshold: float = 0.85

    # File filtering
    exclude_patterns: List[str] = field(default_factory=lambda: [
        "**/node_modules/**",
        "**/__pycache__/**",
        "**/.git/**",
        "**/venv/**",
        "**/dist/**",
        "**/build/**",
    ])
    include_patterns: List[str] = field(default_factory=list)

    # Language support
    languages: List[str] = field(default_factory=lambda: [
        "python", "javascript", "typescript", "java", "go", "rust", "cpp"
    ])

    # Analysis options
    ignore_comments: bool = True
    ignore_whitespace: bool = True
    incremental_mode: bool = False

    # Output options
    output_format: str = "markdown"  # markdown or json
    output_path: Optional[Path] = None
    verbose: bool = False

    # Performance
    max_file_size_kb: int = 1024  # Skip files larger than 1MB
    parallel_processing: bool = True

    @property
    def output_file(self) -> Path:
        """Get output file path with default."""
        if self.output_path:
            return self.output_path
        ext = ".md" if self.output_format == "markdown" else ".json"
        return Path(f"./duplication-report{ext}")


# Export all models
__all__ = [
    "DuplicateType",
    "RefactoringTechnique",
    "CodeLocation",
    "CodeBlock",
    "RefactoringSuggestion",
    "DuplicateBlock",
    "FileOffender",
    "HeatmapEntry",
    "HeatmapData",
    "AnalysisMetadata",
    "AnalysisSummary",
    "AnalysisResult",
    "Config",
]
