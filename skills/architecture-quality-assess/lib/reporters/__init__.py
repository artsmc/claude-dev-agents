"""Reporters module for architecture quality assessment.

Provides multiple output formats for assessment results:
- Markdown: Human-readable reports for documentation and review
- JSON: Structured data for CI/CD and programmatic consumption
- Task List: Actionable refactoring tasks for PM-DB integration

The reporter registry provides a unified interface for generating
reports in any supported format.
"""

from pathlib import Path
from typing import Any, Dict, Optional

from ..models.assessment import AssessmentResult
from .json_reporter import JSONReporter, generate_json_report, generate_ci_summary
from .markdown_reporter import MarkdownReporter, generate_markdown_report
from .task_generator import TaskGenerator, generate_task_list


# Reporter registry mapping format names to reporter classes
REPORTER_REGISTRY = {
    'markdown': MarkdownReporter,
    'json': JSONReporter,
    'tasks': TaskGenerator,
}


class ReporterFactory:
    """Factory for creating and managing reporters.

    Provides a unified interface for generating reports in multiple
    formats without needing to know about specific reporter classes.
    """

    @staticmethod
    def create_reporter(
        format_name: str,
        result: AssessmentResult,
        **kwargs: Any
    ):
        """Create a reporter instance for the specified format.

        Args:
            format_name: Report format ('markdown', 'json', or 'tasks').
            result: Assessment result to generate report from.
            **kwargs: Additional arguments passed to reporter constructor.

        Returns:
            Reporter instance ready to generate output.

        Raises:
            ValueError: If format_name is not supported.

        Example:
            >>> reporter = ReporterFactory.create_reporter('markdown', result)
            >>> report = reporter.generate()
        """
        if format_name not in REPORTER_REGISTRY:
            supported = ', '.join(REPORTER_REGISTRY.keys())
            raise ValueError(
                f"Unsupported report format '{format_name}'. "
                f"Supported formats: {supported}"
            )

        reporter_class = REPORTER_REGISTRY[format_name]
        return reporter_class(result, **kwargs)

    @staticmethod
    def generate_report(
        format_name: str,
        result: AssessmentResult,
        output_path: Optional[Path] = None,
        **kwargs: Any
    ) -> str:
        """Generate a report in the specified format.

        Convenience method that creates a reporter and generates output
        in a single call. Optionally saves to file.

        Args:
            format_name: Report format ('markdown', 'json', or 'tasks').
            result: Assessment result to generate report from.
            output_path: Optional path to save report to.
            **kwargs: Additional arguments passed to reporter constructor.

        Returns:
            Generated report as a string.

        Raises:
            ValueError: If format_name is not supported.

        Example:
            >>> report = ReporterFactory.generate_report(
            ...     'json',
            ...     result,
            ...     Path('report.json'),
            ...     pretty=True
            ... )
        """
        reporter = ReporterFactory.create_reporter(format_name, result, **kwargs)
        report_content = reporter.generate()

        if output_path:
            output_path.write_text(report_content, encoding='utf-8')

        return report_content

    @staticmethod
    def list_formats() -> list:
        """List all supported report formats.

        Returns:
            List of format name strings.
        """
        return list(REPORTER_REGISTRY.keys())


def generate_all_reports(
    result: AssessmentResult,
    output_dir: Path,
    base_name: str = "architecture-assessment"
) -> Dict[str, Path]:
    """Generate all report formats and save to directory.

    Convenience function that generates markdown, JSON, and task list
    reports in a single call.

    Args:
        result: Assessment result to generate reports from.
        output_dir: Directory to save reports to (will be created if needed).
        base_name: Base filename for reports (default: "architecture-assessment").

    Returns:
        Dictionary mapping format name to output file path.

    Example:
        >>> paths = generate_all_reports(result, Path("./reports"))
        >>> print(f"Reports saved:")
        >>> for fmt, path in paths.items():
        ...     print(f"  {fmt}: {path}")
    """
    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)

    paths = {}

    # Generate markdown report
    markdown_path = output_dir / f"{base_name}.md"
    generate_markdown_report(result, markdown_path)
    paths['markdown'] = markdown_path

    # Generate JSON report
    json_path = output_dir / f"{base_name}.json"
    generate_json_report(result, json_path, pretty=True)
    paths['json'] = json_path

    # Generate task list (only if there are violations)
    if result.violations:
        tasks_path = output_dir / f"{base_name}-tasks.md"
        generate_task_list(result, tasks_path)
        paths['tasks'] = tasks_path

    return paths


# Export all public API components
__all__ = [
    # Reporter classes
    'MarkdownReporter',
    'JSONReporter',
    'TaskGenerator',

    # Factory
    'ReporterFactory',

    # Convenience functions
    'generate_markdown_report',
    'generate_json_report',
    'generate_task_list',
    'generate_ci_summary',
    'generate_all_reports',

    # Registry
    'REPORTER_REGISTRY',
]
