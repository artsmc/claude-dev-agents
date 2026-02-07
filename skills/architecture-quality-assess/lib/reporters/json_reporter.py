"""JSON reporter for architecture quality assessment.

Generates structured JSON output suitable for CI/CD integration,
automated processing, and programmatic consumption. The JSON format
matches the schema defined in SKILL.md and TR.md.

JSON reports include:
- Assessment metadata
- Project detection information
- Comprehensive metrics
- Full violation list with all details
- Summary statistics
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from ..models.assessment import AssessmentResult


class JSONReporter:
    """Generate structured JSON reports from assessment results.

    Produces JSON output compatible with CI/CD pipelines, build tools,
    and automated quality gates. The output format is stable and
    versioned to support reliable parsing.
    """

    def __init__(self, result: AssessmentResult, pretty: bool = True):
        """Initialize the JSON reporter.

        Args:
            result: Complete assessment result to generate report from.
            pretty: If True, generate formatted JSON with indentation.
                If False, generate compact single-line JSON.
        """
        self.result = result
        self.pretty = pretty

    def generate(self) -> str:
        """Generate the complete JSON report.

        Returns:
            JSON string (formatted or compact based on pretty flag).
        """
        report_dict = self._build_report_dict()

        if self.pretty:
            return json.dumps(report_dict, indent=2, ensure_ascii=False)
        else:
            return json.dumps(report_dict, ensure_ascii=False)

    def _build_report_dict(self) -> Dict[str, Any]:
        """Build the complete report dictionary structure.

        Returns:
            Dictionary matching the JSON schema defined in SKILL.md.
        """
        return {
            "schema_version": "1.0.0",
            "metadata": self._build_metadata(),
            "project_info": self.result.project_info.to_dict(),
            "summary": self._build_summary(),
            "metrics": self._build_metrics(),
            "violations": self._build_violations(),
            "recommended_actions": self._build_recommended_actions(),
        }

    def _build_metadata(self) -> Dict[str, Any]:
        """Build metadata section with generation info.

        Returns:
            Metadata dictionary with timestamps, versions, and analysis info.
        """
        metadata = dict(self.result.metadata)

        # Ensure required fields
        if 'generated_at' not in metadata:
            metadata['generated_at'] = datetime.now().isoformat()

        if 'tool_name' not in metadata:
            metadata['tool_name'] = "architecture-quality-assess"

        if 'tool_version' not in metadata:
            metadata['tool_version'] = "1.0.0"

        return metadata

    def _build_summary(self) -> Dict[str, Any]:
        """Build summary section with key statistics.

        Returns:
            Summary dictionary with violation counts and scores.
        """
        # Calculate severity counts
        severity_counts = {
            'critical': 0,
            'high': 0,
            'medium': 0,
            'low': 0,
        }

        for violation in self.result.violations:
            severity_key = violation.severity.lower()
            if severity_key in severity_counts:
                severity_counts[severity_key] += 1

        # Calculate overall score
        score = 100
        score -= severity_counts['critical'] * 15
        score -= severity_counts['high'] * 8
        score -= severity_counts['medium'] * 3
        score -= severity_counts['low'] * 1
        score = max(0, score)

        # Determine quality rating
        if score >= 90:
            rating = "excellent"
        elif score >= 75:
            rating = "good"
        elif score >= 60:
            rating = "fair"
        else:
            rating = "needs_improvement"

        return {
            "total_violations": len(self.result.violations),
            "critical_count": severity_counts['critical'],
            "high_count": severity_counts['high'],
            "medium_count": severity_counts['medium'],
            "low_count": severity_counts['low'],
            "overall_score": score,
            "quality_rating": rating,
        }

    def _build_metrics(self) -> Dict[str, Any]:
        """Build metrics section with all calculated metrics.

        Returns:
            Metrics dictionary with nested metric categories.
        """
        metrics = self.result.metrics

        # Convert metrics to dictionary
        if hasattr(metrics, 'to_dict'):
            metrics_dict = metrics.to_dict()
        else:
            # Fallback: manual conversion
            metrics_dict = {}

            # SOLID metrics
            if hasattr(metrics, 'solid') and metrics.solid:
                metrics_dict['solid'] = {
                    'overall_score': metrics.solid.overall_score,
                    'srp_score': metrics.solid.srp_score,
                    'ocp_score': metrics.solid.ocp_score,
                    'lsp_score': metrics.solid.lsp_score,
                    'isp_score': metrics.solid.isp_score,
                    'dip_score': metrics.solid.dip_score,
                    'violations_by_principle': {
                        'srp': metrics.solid.srp_violations,
                        'ocp': metrics.solid.ocp_violations,
                        'lsp': metrics.solid.lsp_violations,
                        'isp': metrics.solid.isp_violations,
                        'dip': metrics.solid.dip_violations,
                    },
                }

            # Coupling metrics
            if hasattr(metrics, 'coupling') and metrics.coupling:
                metrics_dict['coupling'] = {
                    'avg_fan_out': metrics.coupling.avg_fan_out,
                    'max_fan_out': metrics.coupling.max_fan_out,
                    'avg_fan_in': metrics.coupling.avg_fan_in,
                    'max_fan_in': metrics.coupling.max_fan_in,
                    'circular_dependency_count': metrics.coupling.circular_dependency_count,
                    'most_coupled_modules': metrics.coupling.most_coupled_modules,
                }

            # General metrics
            if hasattr(metrics, 'total_files'):
                metrics_dict['code_organization'] = {
                    'total_files': metrics.total_files,
                    'total_lines': getattr(metrics, 'total_lines', 0),
                    'avg_file_size': getattr(metrics, 'avg_file_size', 0),
                }

        return metrics_dict

    def _build_violations(self) -> list:
        """Build violations array with full details.

        Returns:
            List of violation dictionaries.
        """
        return [v.to_dict() for v in self.result.violations]

    def _build_recommended_actions(self) -> list:
        """Build recommended actions based on violations.

        Returns:
            List of action dictionaries prioritized by severity.
        """
        actions = []

        # Group violations by severity
        critical = [v for v in self.result.violations if v.severity == "CRITICAL"]
        high = [v for v in self.result.violations if v.severity == "HIGH"]
        medium = [v for v in self.result.violations if v.severity == "MEDIUM"]

        # Generate actions for critical issues
        for i, violation in enumerate(critical, 1):
            actions.append({
                "priority": "P0",
                "action_id": f"ACTION-CRIT-{i:03d}",
                "title": f"Fix Critical: {violation.message}",
                "category": violation.dimension or "unknown",
                "related_violation_id": violation.id,
                "files": [violation.file_path],
                "recommendation": violation.recommendation or "Address immediately",
                "estimated_effort": "1-4 hours",
            })

        # Generate actions for high-priority issues
        for i, violation in enumerate(high, 1):
            actions.append({
                "priority": "P1",
                "action_id": f"ACTION-HIGH-{i:03d}",
                "title": f"Resolve: {violation.message}",
                "category": violation.dimension or "unknown",
                "related_violation_id": violation.id,
                "files": [violation.file_path],
                "recommendation": violation.recommendation or "Address in next sprint",
                "estimated_effort": "2-8 hours",
            })

        # Generate summary actions for medium issues
        if medium:
            dimension_groups = {}
            for v in medium:
                dim = v.dimension or "other"
                if dim not in dimension_groups:
                    dimension_groups[dim] = []
                dimension_groups[dim].append(v)

            for dim, violations in dimension_groups.items():
                actions.append({
                    "priority": "P2",
                    "action_id": f"ACTION-MED-{dim.upper()}",
                    "title": f"Improve {dim.replace('_', ' ').title()}",
                    "category": dim,
                    "related_violation_ids": [v.id for v in violations],
                    "files": [v.file_path for v in violations],
                    "recommendation": f"Address {len(violations)} medium-priority issues",
                    "estimated_effort": "1-2 days",
                })

        return actions


def generate_json_report(
    result: AssessmentResult,
    output_path: Optional[Path] = None,
    pretty: bool = True
) -> str:
    """Generate and optionally save a JSON report.

    Convenience function for generating JSON reports. If an output
    path is provided, the report will be written to that file.

    Args:
        result: Assessment result to generate report from.
        output_path: Optional path to save report to. If None, report
            is only returned as a string.
        pretty: If True, generate formatted JSON. If False, compact JSON.

    Returns:
        Generated JSON report as a string.

    Example:
        >>> report = generate_json_report(result, Path("report.json"))
        >>> data = json.loads(report)
        >>> print(f"Found {data['summary']['total_violations']} violations")
    """
    reporter = JSONReporter(result, pretty=pretty)
    json_output = reporter.generate()

    if output_path:
        output_path.write_text(json_output, encoding='utf-8')

    return json_output


def generate_ci_summary(result: AssessmentResult) -> Dict[str, Any]:
    """Generate a minimal summary for CI/CD display.

    Produces a compact summary suitable for CI/CD status messages,
    PR comments, or build notifications.

    Args:
        result: Assessment result to summarize.

    Returns:
        Dictionary with summary statistics and pass/fail status.

    Example:
        >>> summary = generate_ci_summary(result)
        >>> if not summary['passed']:
        ...     print(f"Quality gate failed: {summary['message']}")
        ...     sys.exit(1)
    """
    # Calculate severity counts
    critical = sum(1 for v in result.violations if v.severity == "CRITICAL")
    high = sum(1 for v in result.violations if v.severity == "HIGH")
    medium = sum(1 for v in result.violations if v.severity == "MEDIUM")
    low = sum(1 for v in result.violations if v.severity == "LOW")

    # Calculate overall score
    score = 100
    score -= critical * 15
    score -= high * 8
    score -= medium * 3
    score -= low * 1
    score = max(0, score)

    # Determine pass/fail (fail if critical issues exist)
    passed = critical == 0

    # Build message
    if critical > 0:
        message = f"Quality gate failed: {critical} critical issue(s) detected"
    elif high > 0:
        message = f"Quality gate passed with warnings: {high} high-priority issue(s)"
    elif medium > 0 or low > 0:
        message = f"Quality gate passed: minor improvements suggested"
    else:
        message = "Quality gate passed: no issues detected"

    return {
        "passed": passed,
        "score": score,
        "message": message,
        "violations": {
            "critical": critical,
            "high": high,
            "medium": medium,
            "low": low,
            "total": len(result.violations),
        },
        "project": {
            "name": result.project_info.name,
            "type": result.project_info.project_type,
        },
    }
