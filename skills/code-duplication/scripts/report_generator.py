#!/usr/bin/env python3
"""
Report Generator for Code Duplication Analysis Skill

Generates comprehensive markdown reports with duplicate listings,
metrics, and refactoring suggestions.
"""

from typing import List, Tuple, Optional, Dict
from pathlib import Path
from datetime import datetime

from models import (
    DuplicateBlock,
    AnalysisSummary,
    FileOffender,
    HeatmapData,
    DuplicateType,
    AnalysisIssue,
    ErrorCategory
)
from heatmap_renderer import render_heatmap_text


def format_duplicate_block(
    duplicate: DuplicateBlock,
    index: int,
    total: int
) -> str:
    """
    Format a single duplicate block for report.

    Args:
        duplicate: DuplicateBlock to format
        index: Current index (1-based)
        total: Total number of duplicates

    Returns:
        Formatted markdown string

    Example:
        >>> block = DuplicateBlock(...)
        >>> formatted = format_duplicate_block(block, 1, 10)
        >>> "### Duplicate #1" in formatted
        True
    """
    lines = []

    # Header
    type_emoji = {
        DuplicateType.EXACT: "🔴",
        DuplicateType.STRUCTURAL: "🟡",
        DuplicateType.PATTERN: "🔵"
    }
    emoji = type_emoji.get(duplicate.type, "⚪")

    lines.append(f"### {emoji} Duplicate #{index}/{total} - {duplicate.type.value.upper()}")
    lines.append("")

    # Metadata
    lines.append(f"**Type:** {duplicate.type.value}")
    lines.append(f"**Instances:** {len(duplicate.instances)}")
    lines.append(f"**Similarity:** {duplicate.similarity_score * 100:.1f}%")
    lines.append(f"**Hash:** `{duplicate.hash[:12]}...`")
    lines.append("")

    # Locations
    lines.append("**Found in:**")
    for instance in duplicate.instances:
        loc_lines = f"L{instance.start_line}-{instance.end_line}"
        lines.append(f"- `{instance.file_path}:{loc_lines}` ({instance.line_count} lines)")
    lines.append("")

    # Code sample
    if duplicate.code_sample:
        lines.append("**Code Sample:**")
        lines.append("```python")
        # Truncate long samples
        sample_lines = duplicate.code_sample.split('\n')
        if len(sample_lines) > 15:
            lines.extend(sample_lines[:15])
            lines.append("... (truncated)")
        else:
            lines.extend(sample_lines)
        lines.append("```")
        lines.append("")

    # Refactoring suggestion
    if duplicate.suggestion:
        lines.append("**💡 Refactoring Suggestion:**")
        lines.append(f"- **Technique:** {duplicate.suggestion.technique.value}")
        lines.append(f"- **Difficulty:** {duplicate.suggestion.difficulty}")
        lines.append(f"- **Estimated LOC Reduction:** {duplicate.suggestion.estimated_loc_reduction} lines")
        lines.append("")
        lines.append(f"**Description:** {duplicate.suggestion.description}")
        lines.append("")

        if duplicate.suggestion.implementation_steps:
            lines.append("**Implementation Steps:**")
            for step_num, step in enumerate(duplicate.suggestion.implementation_steps, 1):
                lines.append(f"{step_num}. {step}")
            lines.append("")

        if duplicate.suggestion.example_code:
            lines.append("**Example Refactored Code:**")
            lines.append("```python")
            lines.append(duplicate.suggestion.example_code)
            lines.append("```")
            lines.append("")

    lines.append("---")
    lines.append("")

    return '\n'.join(lines)


def format_duplicate_listings(
    duplicates: List[DuplicateBlock],
    max_duplicates: Optional[int] = None
) -> str:
    """
    Format all duplicates for report with optional limit.

    Args:
        duplicates: List of duplicates to format
        max_duplicates: Maximum number to include (None = all)

    Returns:
        Formatted markdown string

    Example:
        >>> duplicates = [DuplicateBlock(...), DuplicateBlock(...)]
        >>> report = format_duplicate_listings(duplicates, max_duplicates=10)
        >>> "## Duplicate Blocks" in report
        True
    """
    lines = []

    # Header
    total = len(duplicates)
    showing = min(total, max_duplicates) if max_duplicates else total

    lines.append("## 📋 Duplicate Blocks")
    lines.append("")
    lines.append(f"Found **{total} duplicate blocks** across the codebase.")

    if max_duplicates and total > max_duplicates:
        lines.append(f"Showing top **{showing}** by severity.")

    lines.append("")

    # Format each duplicate
    duplicates_to_show = duplicates[:max_duplicates] if max_duplicates else duplicates

    for idx, duplicate in enumerate(duplicates_to_show, 1):
        formatted = format_duplicate_block(duplicate, idx, showing)
        lines.append(formatted)

    # Note about truncation
    if max_duplicates and total > max_duplicates:
        remaining = total - max_duplicates
        lines.append(f"_... and {remaining} more duplicates not shown._")
        lines.append("")

    return '\n'.join(lines)


def create_summary_section(
    summary: AnalysisSummary,
    offenders: List[FileOffender],
    heatmap: Optional[HeatmapData] = None
) -> str:
    """
    Create executive summary section.

    Args:
        summary: AnalysisSummary with metrics
        offenders: List of top file offenders
        heatmap: Optional heatmap data

    Returns:
        Formatted markdown summary

    Example:
        >>> summary = AnalysisSummary(...)
        >>> section = create_summary_section(summary, [], None)
        >>> "## Summary" in section
        True
    """
    lines = []

    # Header
    lines.append("## 📊 Executive Summary")
    lines.append("")

    # Overall metrics
    duplication_pct = (summary.duplicate_loc / summary.total_loc * 100) if summary.total_loc > 0 else 0

    lines.append("### Overall Metrics")
    lines.append("")
    lines.append(f"- **Files Analyzed:** {summary.total_files}")
    lines.append(f"- **Total Lines of Code:** {summary.total_loc:,}")
    lines.append(f"- **Duplicate Lines:** {summary.duplicate_loc:,}")
    lines.append(f"- **Duplication Percentage:** {duplication_pct:.2f}%")
    lines.append(f"- **Duplicate Blocks Found:** {summary.duplicate_blocks}")
    lines.append("")

    # Breakdown by type
    lines.append("### Breakdown by Type")
    lines.append("")
    lines.append(f"- **🔴 Exact Duplicates:** {summary.exact_blocks}")
    lines.append(f"- **🟡 Structural Duplicates:** {summary.structural_blocks}")
    lines.append(f"- **🔵 Pattern Duplicates:** {summary.pattern_blocks}")
    lines.append("")

    # Assessment
    lines.append("### Assessment")
    lines.append("")
    if duplication_pct < 5:
        assessment = "✅ **Excellent** - Minimal duplication detected"
    elif duplication_pct < 10:
        assessment = "✅ **Good** - Low duplication, minor cleanup opportunities"
    elif duplication_pct < 20:
        assessment = "⚠️ **Moderate** - Noticeable duplication, refactoring recommended"
    elif duplication_pct < 30:
        assessment = "⚠️ **High** - Significant duplication, refactoring needed"
    else:
        assessment = "🔴 **Critical** - Excessive duplication, immediate action required"

    lines.append(assessment)
    lines.append("")

    # Top offenders
    if offenders:
        lines.append("### 🎯 Top File Offenders")
        lines.append("")
        lines.append("Files with the most duplicate code:")
        lines.append("")

        for rank, offender in enumerate(offenders[:10], 1):
            file_dup_pct = (offender.duplicate_loc / offender.total_loc * 100) if offender.total_loc > 0 else 0
            blocks = len(offender.duplicate_blocks)

            lines.append(f"{rank}. `{offender.file_path}` - {offender.duplicate_loc}/{offender.total_loc} LOC ({file_dup_pct:.1f}%, {blocks} blocks)")

        lines.append("")

    # Heatmap
    if heatmap:
        lines.append("### 🗺️ Duplication Heatmap")
        lines.append("")
        heatmap_text = render_heatmap_text(heatmap, max_width=80)
        lines.append("```")
        lines.append(heatmap_text)
        lines.append("```")
        lines.append("")

    return '\n'.join(lines)


def create_issues_section(summary: AnalysisSummary) -> str:
    """
    Create analysis issues section showing errors and warnings.

    Args:
        summary: Analysis summary with issues

    Returns:
        Formatted markdown section

    Example:
        >>> section = create_issues_section(summary)
        >>> "## Analysis Issues" in section
        True
    """
    if not summary.issues:
        return ""

    lines = []

    lines.append("## Analysis Issues")
    lines.append("")

    # Summary counts
    error_count = summary.error_count
    warning_count = summary.warning_count

    lines.append(f"**Total Issues:** {len(summary.issues)} ({error_count} errors, {warning_count} warnings)")
    lines.append("")

    if summary.skipped_files > 0:
        lines.append(f"**Files Skipped:** {summary.skipped_files}")
        lines.append("")

    # Group by category
    issues_by_category = summary.issues_by_category()

    if issues_by_category:
        lines.append("### Issues by Category")
        lines.append("")

        for category, count in sorted(issues_by_category.items(), key=lambda x: x[1], reverse=True):
            lines.append(f"- **{category.value}**: {count}")

        lines.append("")

    # List errors first, then warnings
    errors = [i for i in summary.issues if i.severity == "error"]
    warnings = [i for i in summary.issues if i.severity == "warning"]

    if errors:
        lines.append("### Errors")
        lines.append("")
        for issue in errors[:20]:  # Limit to first 20
            if issue.file_path:
                lines.append(f"- `{issue.file_path}`: {issue.message}")
            else:
                lines.append(f"- {issue.message}")

        if len(errors) > 20:
            lines.append(f"- _... and {len(errors) - 20} more errors_")

        lines.append("")

    if warnings:
        lines.append("### Warnings")
        lines.append("")
        for issue in warnings[:20]:  # Limit to first 20
            if issue.file_path:
                lines.append(f"- `{issue.file_path}`: {issue.message}")
            else:
                lines.append(f"- {issue.message}")

        if len(warnings) > 20:
            lines.append(f"- _... and {len(warnings) - 20} more warnings_")

        lines.append("")

    lines.append("---")
    lines.append("")

    return '\n'.join(lines)


def create_recommendations_section(
    duplicates: List[DuplicateBlock],
    summary: AnalysisSummary
) -> str:
    """
    Create recommendations section with prioritized actions.

    Args:
        duplicates: All detected duplicates
        summary: Analysis summary

    Returns:
        Formatted markdown recommendations

    Example:
        >>> recs = create_recommendations_section([], AnalysisSummary(...))
        >>> "## Recommendations" in recs
        True
    """
    lines = []

    lines.append("## 💡 Recommendations")
    lines.append("")

    # Calculate potential LOC reduction
    total_reduction = sum(
        dup.suggestion.estimated_loc_reduction
        for dup in duplicates
        if dup.suggestion
    )

    if total_reduction > 0:
        lines.append(f"**Potential LOC Reduction:** ~{total_reduction:,} lines")
        lines.append("")

    # Priority recommendations
    lines.append("### Priority Actions")
    lines.append("")

    # Group by difficulty
    easy_count = sum(1 for d in duplicates if d.suggestion and d.suggestion.difficulty == 'easy')
    medium_count = sum(1 for d in duplicates if d.suggestion and d.suggestion.difficulty == 'medium')
    hard_count = sum(1 for d in duplicates if d.suggestion and d.suggestion.difficulty == 'hard')

    if easy_count > 0:
        lines.append(f"**🟢 Quick Wins ({easy_count} easy tasks):**")
        lines.append("- Start with exact duplicates and simple patterns")
        lines.append("- Low risk, immediate impact")
        lines.append("- Estimated time: 1-2 hours")
        lines.append("")

    if medium_count > 0:
        lines.append(f"**🟡 Moderate Refactoring ({medium_count} medium tasks):**")
        lines.append("- Tackle structural duplicates")
        lines.append("- Extract common utilities")
        lines.append("- Estimated time: 4-8 hours")
        lines.append("")

    if hard_count > 0:
        lines.append(f"**🔴 Complex Refactoring ({hard_count} hard tasks):**")
        lines.append("- Major architectural improvements")
        lines.append("- Design pattern implementations")
        lines.append("- Estimated time: 8-16 hours")
        lines.append("")

    # General best practices
    lines.append("### Best Practices Going Forward")
    lines.append("")
    lines.append("1. **Extract Common Utilities:** Create shared functions for repeated logic")
    lines.append("2. **Use Design Patterns:** Apply appropriate patterns (Factory, Strategy, Template Method)")
    lines.append("3. **Code Reviews:** Flag duplication during reviews")
    lines.append("4. **Automated Detection:** Run this analysis regularly (CI/CD integration)")
    lines.append("5. **Documentation:** Document shared utilities and patterns")
    lines.append("")

    return '\n'.join(lines)


def generate_report(
    duplicates: List[DuplicateBlock],
    summary: AnalysisSummary,
    offenders: List[FileOffender],
    heatmap: Optional[HeatmapData] = None,
    output_path: Optional[Path] = None,
    max_duplicates: Optional[int] = 50
) -> str:
    """
    Generate comprehensive markdown report.

    Args:
        duplicates: List of all duplicates
        summary: Analysis summary metrics
        offenders: Top file offenders
        heatmap: Optional heatmap data
        output_path: Optional path to write report
        max_duplicates: Maximum duplicates to include in detail

    Returns:
        Complete markdown report string

    Example:
        >>> report = generate_report(duplicates, summary, offenders)
        >>> "# Code Duplication Analysis Report" in report
        True
    """
    lines = []

    # Title
    lines.append("# Code Duplication Analysis Report")
    lines.append("")
    lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Table of contents
    lines.append("## Table of Contents")
    lines.append("")
    lines.append("1. [Executive Summary](#executive-summary)")

    # Include Analysis Issues in TOC if there are any
    toc_index = 2
    if summary.issues:
        lines.append(f"{toc_index}. [Analysis Issues](#analysis-issues)")
        toc_index += 1

    lines.append(f"{toc_index}. [Duplicate Blocks](#duplicate-blocks)")
    toc_index += 1
    lines.append(f"{toc_index}. [Recommendations](#recommendations)")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Summary section
    summary_section = create_summary_section(summary, offenders, heatmap)
    lines.append(summary_section)

    # Issues section (if any)
    if summary.issues:
        issues_section = create_issues_section(summary)
        lines.append(issues_section)

    # Duplicates section
    duplicates_section = format_duplicate_listings(duplicates, max_duplicates)
    lines.append(duplicates_section)

    # Recommendations section
    recommendations_section = create_recommendations_section(duplicates, summary)
    lines.append(recommendations_section)

    # Footer
    lines.append("---")
    lines.append("")
    lines.append("*Report generated by Code Duplication Analysis Skill*")
    lines.append("")

    # Combine all sections
    report = '\n'.join(lines)

    # Write to file if path provided
    if output_path:
        try:
            # Ensure parent directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)
            # Write report
            output_path.write_text(report, encoding='utf-8')
        except PermissionError as e:
            raise PermissionError(f"Cannot write to {output_path}: Permission denied")
        except OSError as e:
            # Re-raise OSError (includes disk full, etc.)
            raise
        except Exception as e:
            raise IOError(f"Failed to write report to {output_path}: {str(e)}")

    return report


def generate_csv_export(
    duplicates: List[DuplicateBlock],
    output_path: Path
) -> None:
    """
    Export duplicates to CSV format for data analysis.

    Args:
        duplicates: List of duplicates to export
        output_path: Path to write CSV file

    Raises:
        PermissionError: If cannot write to output path
        OSError: If disk full or other OS error
        IOError: If other write error occurs

    Example:
        >>> generate_csv_export(duplicates, Path("duplicates.csv"))
    """
    import csv

    try:
        # Ensure parent directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Write CSV file
        with output_path.open('w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)

            # Header
            writer.writerow([
                'duplicate_id',
                'type',
                'instances',
                'similarity',
                'file_path',
                'start_line',
                'end_line',
                'line_count'
            ])

            # Data rows
            for dup in duplicates:
                for instance in dup.instances:
                    writer.writerow([
                        dup.id,
                        dup.type.value,
                        len(dup.instances),
                        dup.similarity_score,
                        str(instance.file_path),
                        instance.start_line,
                        instance.end_line,
                        instance.line_count
                    ])

    except PermissionError as e:
        raise PermissionError(f"Cannot write to {output_path}: Permission denied")
    except OSError as e:
        # Re-raise OSError (includes disk full, etc.)
        raise
    except Exception as e:
        raise IOError(f"Failed to write CSV to {output_path}: {str(e)}")


# Export public API
__all__ = [
    'format_duplicate_block',
    'format_duplicate_listings',
    'create_summary_section',
    'create_issues_section',
    'create_recommendations_section',
    'generate_report',
    'generate_csv_export',
]
