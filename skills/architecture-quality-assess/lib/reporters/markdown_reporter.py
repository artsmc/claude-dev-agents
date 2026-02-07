"""Markdown reporter for architecture quality assessment.

Generates comprehensive markdown reports with executive summary,
violation details organized by severity and dimension, code samples,
metrics visualization, and actionable recommendations.

The markdown format follows the structure defined in SKILL.md and
provides a human-readable output suitable for review meetings,
documentation, and code review comments.
"""

from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from ..models.assessment import AssessmentResult
from ..models.violation import Violation


class MarkdownReporter:
    """Generate comprehensive markdown reports from assessment results.

    Produces structured markdown documents with:
    - Executive summary with overall scores
    - Project detection information
    - Metrics dashboard
    - Violations organized by severity and dimension
    - Actionable recommendations
    - Detailed appendix with code samples
    """

    def __init__(self, result: AssessmentResult):
        """Initialize the markdown reporter.

        Args:
            result: Complete assessment result to generate report from.
        """
        self.result = result

    def generate(self) -> str:
        """Generate the complete markdown report.

        Returns:
            Formatted markdown string ready for file output or display.
        """
        sections = [
            self._header(),
            self._executive_summary(),
            self._project_overview(),
            self._metrics_dashboard(),
            self._violations_by_severity(),
            self._violations_by_dimension(),
            self._recommended_actions(),
            self._appendix(),
            self._footer(),
        ]

        return "\n\n".join(sections)

    def _header(self) -> str:
        """Generate report header with metadata."""
        lines = [
            "# Architecture Quality Assessment Report",
            "",
            f"**Generated**: {self.result.metadata.get('generated_at', 'N/A')}",
            f"**Project**: {self.result.project_info.name}",
            f"**Path**: {self.result.project_info.path}",
        ]

        duration = self.result.metadata.get('duration_seconds')
        if duration is not None:
            lines.append(f"**Analysis Duration**: {duration:.2f} seconds")

        return "\n".join(lines)

    def _executive_summary(self) -> str:
        """Generate executive summary with key metrics."""
        lines = [
            "---",
            "",
            "## Executive Summary",
        ]

        # Calculate severity counts
        severity_counts = self._calculate_severity_counts()
        total = severity_counts['total']
        critical = severity_counts['critical']
        high = severity_counts['high']
        medium = severity_counts['medium']
        low = severity_counts['low']

        # Calculate overall score based on violations
        # Perfect score: 100, deduct points based on severity
        score = 100
        score -= critical * 15  # Critical: -15 points each
        score -= high * 8       # High: -8 points each
        score -= medium * 3     # Medium: -3 points each
        score -= low * 1        # Low: -1 point each
        score = max(0, score)   # Floor at 0

        # Determine quality rating
        if score >= 90:
            rating = "Excellent"
            emoji = "✅"
        elif score >= 75:
            rating = "Good"
            emoji = "👍"
        elif score >= 60:
            rating = "Fair"
            emoji = "⚠️"
        else:
            rating = "Needs Improvement"
            emoji = "❌"

        lines.extend([
            "",
            f"**Overall Score**: {score}/100 ({rating} {emoji})",
            "",
            f"**Total Issues**: {total}",
            f"- **Critical**: {critical} 🔴",
            f"- **High**: {high} 🟠",
            f"- **Medium**: {medium} 🟡",
            f"- **Low**: {low} 🔵",
        ])

        # Add quick summary based on severity
        if critical > 0:
            lines.extend([
                "",
                f"⚠️ **Action Required**: {critical} critical issue(s) detected that should be addressed immediately.",
            ])
        elif high > 0:
            lines.extend([
                "",
                f"📋 **Recommended**: {high} high-priority issue(s) should be addressed in the next sprint.",
            ])
        elif total == 0:
            lines.extend([
                "",
                "✨ **Excellent**: No architecture quality issues detected!",
            ])

        return "\n".join(lines)

    def _project_overview(self) -> str:
        """Generate project detection information section."""
        lines = [
            "---",
            "",
            "## 1. Project Overview",
            "",
            f"**Project Type**: {self.result.project_info.project_type}",
            f"**Framework**: {self.result.project_info.framework}",
        ]

        if self.result.project_info.framework_version:
            lines.append(f"**Framework Version**: {self.result.project_info.framework_version}")

        if self.result.project_info.architecture_pattern:
            lines.append(f"**Architecture Pattern**: {self.result.project_info.architecture_pattern}")

        return "\n".join(lines)

    def _metrics_dashboard(self) -> str:
        """Generate metrics dashboard section."""
        lines = [
            "---",
            "",
            "## 2. Quality Metrics",
            "",
        ]

        metrics = self.result.metrics

        # SOLID metrics if available
        if hasattr(metrics, 'solid') and metrics.solid:
            lines.extend([
                "### SOLID Principles Compliance",
                "",
                f"**Overall Score**: {metrics.solid.overall_score}/100",
                "",
                f"- **Single Responsibility (SRP)**: {metrics.solid.srp_score}/100",
                f"- **Open/Closed (OCP)**: {metrics.solid.ocp_score}/100",
                f"- **Liskov Substitution (LSP)**: {metrics.solid.lsp_score}/100",
                f"- **Interface Segregation (ISP)**: {metrics.solid.isp_score}/100",
                f"- **Dependency Inversion (DIP)**: {metrics.solid.dip_score}/100",
                "",
            ])

        # Coupling metrics if available
        if hasattr(metrics, 'coupling') and metrics.coupling:
            # Coupling is a dict of module -> CouplingMetrics
            if isinstance(metrics.coupling, dict):
                # Calculate aggregates
                if metrics.coupling:
                    avg_fan_out = sum(m.fan_out for m in metrics.coupling.values()) / len(metrics.coupling)
                    max_fan_out = max(m.fan_out for m in metrics.coupling.values())

                    lines.extend([
                        "### Coupling & Dependencies",
                        "",
                        f"- **Average FAN-OUT**: {avg_fan_out:.2f}",
                        f"- **Max FAN-OUT**: {max_fan_out}",
                        f"- **Total Modules Analyzed**: {len(metrics.coupling)}",
                        "",
                    ])

                    # Show most coupled modules
                    most_coupled = sorted(metrics.coupling.values(), key=lambda m: m.fan_out, reverse=True)[:5]
                    if most_coupled:
                        lines.append("**Most Coupled Modules**:")
                        lines.append("")
                        for m in most_coupled:
                            lines.append(f"- `{m.module_path}` (FAN-OUT: {m.fan_out})")
                        lines.append("")

        # General metrics
        if hasattr(metrics, 'total_files'):
            lines.extend([
                "### Code Organization",
                "",
                f"- **Total Files Analyzed**: {metrics.total_files}",
            ])

            if hasattr(metrics, 'total_lines'):
                lines.append(f"- **Total Lines of Code**: {metrics.total_lines}")

            if hasattr(metrics, 'avg_file_size'):
                lines.append(f"- **Average File Size**: {metrics.avg_file_size:.0f} LOC")

            lines.append("")

        return "\n".join(lines)

    def _violations_by_severity(self) -> str:
        """Generate violations organized by severity."""
        lines = [
            "---",
            "",
            "## 3. Violations by Severity",
            "",
        ]

        if not self.result.violations:
            lines.append("✅ No violations detected.")
            return "\n".join(lines)

        # Group by severity
        severity_order = ["CRITICAL", "HIGH", "MEDIUM", "LOW"]

        for severity in severity_order:
            violations = [v for v in self.result.violations if v.severity == severity]
            if not violations:
                continue

            # Severity header
            emoji_map = {
                "CRITICAL": "🔴",
                "HIGH": "🟠",
                "MEDIUM": "🟡",
                "LOW": "🔵",
            }
            emoji = emoji_map.get(severity, "")

            lines.extend([
                f"### {emoji} {severity} ({len(violations)} issue{'s' if len(violations) != 1 else ''})",
                "",
            ])

            # List violations
            for i, violation in enumerate(violations, 1):
                lines.extend([
                    f"#### {i}. {violation.message}",
                    "",
                    f"**Type**: {violation.type}",
                    f"**File**: `{violation.file_path}`",
                ])

                if violation.line_number:
                    lines.append(f"**Line**: {violation.line_number}")

                if violation.explanation:
                    lines.extend([
                        "",
                        f"**Issue**: {violation.explanation}",
                    ])

                if violation.recommendation:
                    lines.extend([
                        "",
                        f"**Recommendation**: {violation.recommendation}",
                    ])

                # Add metadata if available
                if violation.metadata:
                    self._add_metadata_section(lines, violation.metadata)

                lines.append("")

        return "\n".join(lines)

    def _violations_by_dimension(self) -> str:
        """Generate violations organized by analysis dimension."""
        lines = [
            "---",
            "",
            "## 4. Violations by Analysis Dimension",
            "",
        ]

        if not self.result.violations:
            lines.append("✅ No violations detected.")
            return "\n".join(lines)

        # Group by dimension
        dimension_map: Dict[str, List[Violation]] = {}
        for violation in self.result.violations:
            dimension = violation.dimension or "other"
            if dimension not in dimension_map:
                dimension_map[dimension] = []
            dimension_map[dimension].append(violation)

        # Sort dimensions
        dimension_order = ["layer", "solid", "patterns", "coupling", "organization", "drift", "other"]
        dimension_names = {
            "layer": "Layer Separation",
            "solid": "SOLID Principles",
            "patterns": "Design Patterns",
            "coupling": "Coupling & Dependencies",
            "organization": "Code Organization",
            "drift": "Architecture Drift",
            "other": "Other Issues",
        }

        for dimension in dimension_order:
            if dimension not in dimension_map:
                continue

            violations = dimension_map[dimension]
            dimension_name = dimension_names.get(dimension, dimension.title())

            lines.extend([
                f"### {dimension_name} ({len(violations)} issue{'s' if len(violations) != 1 else ''})",
                "",
            ])

            # List violations concisely
            for violation in violations:
                severity_emoji = {
                    "CRITICAL": "🔴",
                    "HIGH": "🟠",
                    "MEDIUM": "🟡",
                    "LOW": "🔵",
                }.get(violation.severity, "")

                location = violation.file_path
                if violation.line_number:
                    location = f"{location}:{violation.line_number}"

                lines.append(f"- {severity_emoji} **{violation.message}** - `{location}`")

            lines.append("")

        return "\n".join(lines)

    def _recommended_actions(self) -> str:
        """Generate prioritized list of recommended actions."""
        lines = [
            "---",
            "",
            "## 5. Recommended Actions",
            "",
        ]

        if not self.result.violations:
            lines.extend([
                "✅ No actions required. Your architecture is in excellent shape!",
                "",
                "**Maintenance Recommendations**:",
                "- Continue following current architectural patterns",
                "- Run periodic assessments to catch drift early",
                "- Document new patterns in systemPatterns.md",
            ])
            return "\n".join(lines)

        # Group by priority
        critical = [v for v in self.result.violations if v.severity == "CRITICAL"]
        high = [v for v in self.result.violations if v.severity == "HIGH"]
        medium = [v for v in self.result.violations if v.severity == "MEDIUM"]
        low = [v for v in self.result.violations if v.severity == "LOW"]

        # Priority 0: Critical issues
        if critical:
            lines.extend([
                "### 🔴 Priority 0: Immediate Action Required",
                "",
                f"Address these {len(critical)} critical issue(s) immediately:",
                "",
            ])
            for i, v in enumerate(critical, 1):
                lines.append(f"{i}. **{v.message}** in `{v.file_path}`")
                if v.recommendation:
                    lines.append(f"   - {v.recommendation}")
            lines.append("")

        # Priority 1: High priority
        if high:
            lines.extend([
                "### 🟠 Priority 1: Address in Next Sprint",
                "",
                f"Plan to resolve these {len(high)} high-priority issue(s):",
                "",
            ])
            for i, v in enumerate(high[:5], 1):  # Show top 5
                lines.append(f"{i}. **{v.message}** in `{v.file_path}`")
            if len(high) > 5:
                lines.append(f"   ... and {len(high) - 5} more")
            lines.append("")

        # Priority 2: Medium priority
        if medium:
            lines.extend([
                "### 🟡 Priority 2: Plan for Next Quarter",
                "",
                f"Consider addressing these {len(medium)} medium-priority improvement(s).",
                "",
            ])

        # Priority 3: Low priority
        if low:
            lines.extend([
                "### 🔵 Priority 3: Nice to Have",
                "",
                f"Optional improvements: {len(low)} low-priority suggestion(s).",
                "",
            ])

        return "\n".join(lines)

    def _appendix(self) -> str:
        """Generate detailed appendix with full violation list."""
        lines = [
            "---",
            "",
            "## Appendix: Detailed Violation List",
            "",
        ]

        if not self.result.violations:
            lines.append("No violations detected.")
            return "\n".join(lines)

        lines.append(f"Total violations: {len(self.result.violations)}")
        lines.append("")
        lines.append("| ID | Type | Severity | File | Line | Message |")
        lines.append("|---|---|---|---|---|---|")

        for violation in self.result.violations:
            line_num = str(violation.line_number) if violation.line_number else "-"
            # Truncate long file paths and messages for table
            file_path = violation.file_path
            if len(file_path) > 40:
                file_path = "..." + file_path[-37:]
            message = violation.message
            if len(message) > 50:
                message = message[:47] + "..."

            lines.append(
                f"| {violation.id} | {violation.type} | {violation.severity} | "
                f"`{file_path}` | {line_num} | {message} |"
            )

        return "\n".join(lines)

    def _footer(self) -> str:
        """Generate report footer."""
        return "\n".join([
            "---",
            "",
            "*Report generated by Architecture Quality Assessment Skill*",
            f"*Tool Version: {self.result.metadata.get('tool_version', 'unknown')}*",
        ])

    def _calculate_severity_counts(self) -> Dict[str, int]:
        """Calculate violation counts by severity.

        Returns:
            Dictionary with total and per-severity counts.
        """
        counts = {
            'total': len(self.result.violations),
            'critical': 0,
            'high': 0,
            'medium': 0,
            'low': 0,
        }

        for violation in self.result.violations:
            severity_key = violation.severity.lower()
            if severity_key in counts:
                counts[severity_key] += 1

        return counts

    def _add_metadata_section(self, lines: List[str], metadata: Dict) -> None:
        """Add metadata section to violation details.

        Args:
            lines: List to append lines to.
            metadata: Violation metadata dictionary.
        """
        if not metadata:
            return

        lines.extend([
            "",
            "**Additional Details**:",
        ])

        for key, value in metadata.items():
            # Format key nicely
            formatted_key = key.replace('_', ' ').title()

            # Format value based on type
            if isinstance(value, list):
                lines.append(f"- {formatted_key}:")
                for item in value:
                    lines.append(f"  - {item}")
            elif isinstance(value, dict):
                lines.append(f"- {formatted_key}:")
                for k, v in value.items():
                    lines.append(f"  - {k}: {v}")
            else:
                lines.append(f"- {formatted_key}: {value}")


def generate_markdown_report(result: AssessmentResult, output_path: Optional[Path] = None) -> str:
    """Generate and optionally save a markdown report.

    Convenience function for generating markdown reports. If an output
    path is provided, the report will be written to that file.

    Args:
        result: Assessment result to generate report from.
        output_path: Optional path to save report to. If None, report
            is only returned as a string.

    Returns:
        Generated markdown report as a string.

    Example:
        >>> report = generate_markdown_report(result, Path("report.md"))
        >>> print(f"Report saved to report.md ({len(report)} chars)")
    """
    reporter = MarkdownReporter(result)
    markdown = reporter.generate()

    if output_path:
        output_path.write_text(markdown, encoding='utf-8')

    return markdown
