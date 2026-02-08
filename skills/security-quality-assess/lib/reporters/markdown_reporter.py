"""Markdown reporter for security quality assessment.

Generates comprehensive, human-readable security assessment reports in
Markdown format.  The output is structured for both quick executive review
and detailed remediation work by security teams.

Report sections (in order):
    1. Header -- title, project metadata, scan timestamp.
    2. Executive Summary -- risk score, severity breakdown, posture statement.
    3. Risk Breakdown -- severity distribution table with visual bar chart.
    4. OWASP Top 10 Coverage -- per-category finding counts.
    5. Detailed Findings -- full finding list grouped by severity.
    6. Footer -- suppressed count, analyzer versions, generation time.

Classes:
    SecurityMarkdownReporter: Stateless reporter that accepts an
        ``AssessmentResult`` and produces a Markdown string.

Usage:
    >>> from lib.reporters.markdown_reporter import SecurityMarkdownReporter
    >>> reporter = SecurityMarkdownReporter()
    >>> markdown = reporter.generate(result)
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, List

from lib.models.assessment import AssessmentResult
from lib.models.finding import Finding, OWASPCategory, Severity


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_SEVERITY_ORDER: List[str] = ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
"""Presentation order for severity levels (most severe first)."""

_SEVERITY_INDICATORS: Dict[str, str] = {
    "CRITICAL": "CRITICAL",
    "HIGH": "HIGH",
    "MEDIUM": "MEDIUM",
    "LOW": "LOW",
}

_SEVERITY_RISK_LABELS: Dict[str, str] = {
    "CRITICAL": "Critical",
    "HIGH": "High",
    "MEDIUM": "Medium",
    "LOW": "Low",
}

_OWASP_NAMES: Dict[str, str] = {
    "A01": "A01: Broken Access Control",
    "A02": "A02: Cryptographic Failures",
    "A03": "A03: Injection",
    "A04": "A04: Insecure Design",
    "A05": "A05: Security Misconfiguration",
    "A06": "A06: Vulnerable and Outdated Components",
    "A07": "A07: Identification and Authentication Failures",
    "A08": "A08: Software and Data Integrity Failures",
    "A09": "A09: Security Logging and Monitoring Failures",
    "A10": "A10: Server-Side Request Forgery",
}
"""Human-readable names for each OWASP Top 10 (2021) category."""

_BAR_CHAR_FILLED = "\u2588"
"""Unicode full block character used to draw filled portions of bar charts."""

_BAR_CHAR_EMPTY = "\u2591"
"""Unicode light shade character used to draw empty portions of bar charts."""

_BAR_MAX_WIDTH = 20
"""Maximum character width for a single bar in the severity chart."""

_TOOL_NAME = "Security Quality Assessment Skill"
"""Branding string for the report footer."""


# ---------------------------------------------------------------------------
# SecurityMarkdownReporter
# ---------------------------------------------------------------------------

class SecurityMarkdownReporter:
    """Generate security assessment Markdown reports.

    This reporter is **stateless** -- it holds no mutable data between calls
    to ``generate()``.  All information is drawn from the ``AssessmentResult``
    passed to each invocation.

    The report is built by concatenating individually-rendered sections.  Each
    section is produced by a private method that returns a Markdown fragment
    (a plain ``str``).  Sections are joined with double newlines to create
    proper paragraph separation.

    Example:
        >>> from lib.models.assessment import AssessmentResult, ProjectInfo
        >>> project = ProjectInfo(
        ...     name="demo",
        ...     path="/tmp/demo",
        ...     files_analyzed=10,
        ...     scan_duration=1.5,
        ...     timestamp="2026-02-08T12:00:00+00:00",
        ... )
        >>> result = AssessmentResult(project=project)
        >>> reporter = SecurityMarkdownReporter()
        >>> md = reporter.generate(result)
        >>> "Security Assessment Report" in md
        True
    """

    # -----------------------------------------------------------------------
    # Public API
    # -----------------------------------------------------------------------

    def generate(self, result: AssessmentResult) -> str:
        """Generate a complete Markdown security assessment report.

        Assembles all report sections in presentation order and joins them
        with double newlines for proper Markdown paragraph separation.

        Args:
            result: A fully-populated ``AssessmentResult`` containing project
                metadata, findings, suppression counts, and analyzer versions.

        Returns:
            A single Markdown-formatted string ready for file output or
            terminal display.
        """
        sections: List[str] = [
            self._header(result),
            self._executive_summary(result),
            self._risk_breakdown(result),
            self._owasp_coverage(result),
            self._detailed_findings(result),
        ]

        # Include the error summary section only when errors were collected.
        if result.errors:
            sections.append(self._error_summary(result))

        sections.append(self._footer(result))

        return "\n\n".join(sections)

    # -----------------------------------------------------------------------
    # Section: Header
    # -----------------------------------------------------------------------

    def _header(self, result: AssessmentResult) -> str:
        """Render the report title and project metadata.

        Includes project name, filesystem path, scan timestamp, scan
        duration, and number of files analyzed.

        Args:
            result: Assessment result with project metadata.

        Returns:
            Markdown string for the header section.
        """
        project = result.project
        duration_str = f"{project.scan_duration:.2f}" if project.scan_duration else "N/A"

        lines: List[str] = [
            "# Security Assessment Report",
            "",
            f"**Project**: {project.name}",
            f"**Path**: `{project.path}`",
            f"**Scan Timestamp**: {project.timestamp}",
            f"**Scan Duration**: {duration_str} seconds",
            f"**Files Analyzed**: {project.files_analyzed}",
        ]
        return "\n".join(lines)

    # -----------------------------------------------------------------------
    # Section: Executive Summary
    # -----------------------------------------------------------------------

    def _executive_summary(self, result: AssessmentResult) -> str:
        """Render the high-level executive summary.

        Presents the weighted risk score, total findings, a severity
        breakdown, and a qualitative posture assessment.

        Args:
            result: Assessment result with findings.

        Returns:
            Markdown string for the executive summary section.
        """
        risk_score = result.calculate_risk_score()
        severity_counts = result.get_severity_counts()
        total_findings = sum(severity_counts.values())
        critical_count = severity_counts.get("CRITICAL", 0)

        posture = self._assess_posture(risk_score, critical_count)

        lines: List[str] = [
            "---",
            "",
            "## Executive Summary",
            "",
            f"**Risk Score**: {risk_score} "
            f"({self._risk_score_label(risk_score)})",
            "",
            f"**Total Findings**: {total_findings}",
            "",
            "| Severity | Count |",
            "|----------|-------|",
            f"| CRITICAL | {severity_counts.get('CRITICAL', 0)} |",
            f"| HIGH | {severity_counts.get('HIGH', 0)} |",
            f"| MEDIUM | {severity_counts.get('MEDIUM', 0)} |",
            f"| LOW | {severity_counts.get('LOW', 0)} |",
        ]

        if critical_count > 0:
            lines.extend([
                "",
                f"**!! {critical_count} CRITICAL finding(s) require "
                f"immediate attention !!**",
            ])

        if result.suppressed_count > 0:
            lines.extend([
                "",
                f"*{result.suppressed_count} finding(s) suppressed by "
                f"configuration.*",
            ])

        lines.extend([
            "",
            f"**Security Posture**: {posture}",
        ])

        return "\n".join(lines)

    # -----------------------------------------------------------------------
    # Section: Risk Breakdown
    # -----------------------------------------------------------------------

    def _risk_breakdown(self, result: AssessmentResult) -> str:
        """Render the severity distribution with a visual bar chart.

        Shows a Markdown table of findings per severity with percentage,
        followed by a Unicode block-character bar chart for quick visual
        assessment.

        Args:
            result: Assessment result with findings.

        Returns:
            Markdown string for the risk breakdown section.
        """
        severity_counts = result.get_severity_counts()
        total = sum(severity_counts.values())

        lines: List[str] = [
            "---",
            "",
            "## Risk Breakdown",
            "",
            "| Severity | Count | Percentage | Distribution |",
            "|----------|------:|-----------:|--------------|",
        ]

        for severity in _SEVERITY_ORDER:
            count = severity_counts.get(severity, 0)
            pct = (count / total * 100) if total > 0 else 0.0
            bar = self._render_bar(count, total)
            lines.append(
                f"| {severity} | {count} | {pct:.1f}% | `{bar}` |"
            )

        # Add a fenced block with the visual chart for terminals
        lines.extend([
            "",
            "```",
        ])
        for severity in _SEVERITY_ORDER:
            count = severity_counts.get(severity, 0)
            pct = (count / total * 100) if total > 0 else 0.0
            bar = self._render_bar(count, total)
            label = f"{severity:<8s}"
            lines.append(f"  {label} {bar} {count} ({pct:.1f}%)")
        lines.append("```")

        return "\n".join(lines)

    # -----------------------------------------------------------------------
    # Section: OWASP Top 10 Coverage
    # -----------------------------------------------------------------------

    def _owasp_coverage(self, result: AssessmentResult) -> str:
        """Render the OWASP Top 10 (2021) coverage table.

        Maps each finding to its OWASP category and presents a table
        showing which categories have findings and which have none.

        Args:
            result: Assessment result with findings.

        Returns:
            Markdown string for the OWASP coverage section.
        """
        # Build per-category counts
        category_counts: Dict[str, int] = {}
        for member in OWASPCategory:
            category_counts[member.value] = 0
        for finding in result.findings:
            cat_value = finding.category.value
            if cat_value in category_counts:
                category_counts[cat_value] += 1

        lines: List[str] = [
            "---",
            "",
            "## OWASP Top 10 Coverage",
            "",
        ]

        for cat_code in sorted(_OWASP_NAMES.keys()):
            count = category_counts.get(cat_code, 0)
            name = _OWASP_NAMES[cat_code]
            if count > 0:
                indicator = "!!"
                suffix = f"({count} finding{'s' if count != 1 else ''})"
            else:
                indicator = "--"
                suffix = "(0 findings)"
            lines.append(f"- [{indicator}] {name} {suffix}")

        return "\n".join(lines)

    # -----------------------------------------------------------------------
    # Section: Detailed Findings
    # -----------------------------------------------------------------------

    def _detailed_findings(self, result: AssessmentResult) -> str:
        """Render the full list of findings grouped by severity.

        Findings within each severity group are listed in the order they
        appear in the result.  Each finding includes title, location,
        code sample, description, CWE reference, remediation guidance,
        and confidence score.

        Args:
            result: Assessment result with findings.

        Returns:
            Markdown string for the detailed findings section.
        """
        lines: List[str] = [
            "---",
            "",
            "## Detailed Findings",
            "",
        ]

        if not result.findings:
            lines.append("No security findings detected. Good work!")
            return "\n".join(lines)

        # Group by severity in presentation order
        grouped = self._group_by_severity(result.findings)
        finding_number = 0

        for severity in _SEVERITY_ORDER:
            findings_in_group = grouped.get(severity, [])
            if not findings_in_group:
                continue

            label = _SEVERITY_RISK_LABELS.get(severity, severity)
            lines.extend([
                f"### {severity} Severity ({len(findings_in_group)} "
                f"finding{'s' if len(findings_in_group) != 1 else ''})",
                "",
            ])

            for finding in findings_in_group:
                finding_number += 1
                lines.extend(
                    self._render_single_finding(finding, finding_number)
                )

        return "\n".join(lines)

    def _render_single_finding(
        self, finding: Finding, number: int
    ) -> List[str]:
        """Render a single finding as a Markdown subsection.

        Produces a fourth-level heading (####) with the finding title,
        followed by structured metadata, a fenced code sample, description,
        and remediation guidance.

        Args:
            finding: The ``Finding`` object to render.
            number: Sequential finding number across the whole report.

        Returns:
            A list of Markdown lines (without trailing newline) for the
            finding.
        """
        lines: List[str] = []

        # Title line
        lines.append(
            f"#### {number}. [{finding.severity.value}] {finding.title}"
        )
        lines.append("")

        # Metadata table
        lines.append("| Field | Value |")
        lines.append("|-------|-------|")
        lines.append(f"| **ID** | `{finding.id}` |")
        lines.append(f"| **Rule** | `{finding.rule_id}` |")
        lines.append(
            f"| **OWASP** | {self._owasp_label(finding.category)} |"
        )
        if finding.cwe_id:
            lines.append(f"| **CWE** | {finding.cwe_id} |")
        lines.append(
            f"| **Confidence** | {self._format_confidence(finding.confidence)} |"
        )
        lines.append(
            f"| **Location** | `{finding.file_path}:{finding.line_number}` |"
        )
        lines.append("")

        # Code sample
        if finding.code_sample and finding.code_sample.strip():
            # Determine language hint from file extension
            lang_hint = self._detect_language_hint(finding.file_path)
            lines.append(f"**Code Sample**:")
            lines.append("")
            lines.append(f"```{lang_hint}")
            lines.append(finding.code_sample)
            lines.append("```")
            lines.append("")

        # Description
        lines.append(f"**Description**: {finding.description}")
        lines.append("")

        # Remediation
        lines.append(f"**Remediation**: {finding.remediation}")
        lines.append("")

        return lines

    # -----------------------------------------------------------------------
    # Section: Error Summary
    # -----------------------------------------------------------------------

    def _error_summary(self, result: AssessmentResult) -> str:
        """Render the error summary section.

        Lists all non-fatal errors that occurred during the assessment.
        These are situations where the tool encountered a problem (file
        unreadable, parser failure, API timeout, etc.) but continued
        running. The section alerts the reader that the assessment may
        be incomplete.

        Args:
            result: Assessment result containing the errors list.

        Returns:
            Markdown string for the error summary section. Returns an
            empty string if no errors were collected.
        """
        if not result.errors:
            return ""

        lines: List[str] = [
            "---",
            "",
            "## Errors and Warnings",
            "",
            (
                f"**{len(result.errors)} non-fatal error(s)** occurred "
                "during the assessment. Some results may be incomplete."
            ),
            "",
        ]

        for idx, error in enumerate(result.errors, start=1):
            lines.append(f"{idx}. {error}")

        return "\n".join(lines)

    # -----------------------------------------------------------------------
    # Section: Footer
    # -----------------------------------------------------------------------

    def _footer(self, result: AssessmentResult) -> str:
        """Render the report footer with metadata.

        Includes suppressed findings count, analyzer versions, and the
        report generation timestamp.

        Args:
            result: Assessment result with suppression and version data.

        Returns:
            Markdown string for the footer section.
        """
        now_utc = datetime.now(timezone.utc).isoformat()

        lines: List[str] = [
            "---",
            "",
            "## Report Metadata",
            "",
            f"**Suppressed Findings**: {result.suppressed_count}",
        ]

        # Analyzer versions
        if result.analyzer_versions:
            lines.append("")
            lines.append("**Analyzer Versions**:")
            lines.append("")
            for analyzer_name, version in sorted(
                result.analyzer_versions.items()
            ):
                lines.append(f"- {analyzer_name}: {version}")

        lines.extend([
            "",
            f"**Report Generated**: {now_utc}",
            "",
            "---",
            "",
            f"*Generated by {_TOOL_NAME}*",
        ])

        return "\n".join(lines)

    # -----------------------------------------------------------------------
    # Formatting Helpers
    # -----------------------------------------------------------------------

    @staticmethod
    def _risk_score_label(score: int) -> str:
        """Map a numeric risk score to a qualitative label.

        The scoring model in ``AssessmentResult.calculate_risk_score()``
        produces an additive score where 0 means no findings and higher
        values mean more risk. The label thresholds are calibrated to
        match the weighting scheme.

        Args:
            score: Weighted risk score (0 or positive).

        Returns:
            A short qualitative label string.
        """
        if score == 0:
            return "No Risk Detected"
        if score <= 5:
            return "Minimal Risk"
        if score <= 15:
            return "Low Risk"
        if score <= 40:
            return "Moderate Risk"
        if score <= 80:
            return "High Risk"
        return "Critical Risk"

    @staticmethod
    def _assess_posture(risk_score: int, critical_count: int) -> str:
        """Produce a one-sentence security posture assessment.

        Takes the risk score and critical finding count into account to
        produce a concise statement suitable for the executive summary.

        Args:
            risk_score: Weighted risk score from ``calculate_risk_score()``.
            critical_count: Number of CRITICAL-severity findings.

        Returns:
            A concise posture assessment string.
        """
        if critical_count > 0:
            return (
                "CRITICAL vulnerabilities present. Immediate remediation "
                "required before deployment."
            )
        if risk_score == 0:
            return (
                "No security issues detected. The codebase appears to "
                "follow secure coding practices."
            )
        if risk_score <= 10:
            return (
                "Minor security improvements recommended. No immediate "
                "risk to production."
            )
        if risk_score <= 40:
            return (
                "Several security issues identified. Review and "
                "remediate before next release."
            )
        return (
            "Significant security concerns detected. Prioritize "
            "remediation of high-severity findings."
        )

    @staticmethod
    def _render_bar(count: int, total: int) -> str:
        """Render a horizontal bar using Unicode block characters.

        Produces a fixed-width string of ``_BAR_MAX_WIDTH`` characters
        where filled blocks represent the proportion of ``count`` to
        ``total``.

        Args:
            count: Value for this bar segment.
            total: Total across all segments (denominator).

        Returns:
            A string of Unicode block characters representing the bar.
        """
        if total <= 0:
            return _BAR_CHAR_EMPTY * _BAR_MAX_WIDTH

        filled = round(count / total * _BAR_MAX_WIDTH)
        filled = max(0, min(filled, _BAR_MAX_WIDTH))
        empty = _BAR_MAX_WIDTH - filled
        return (_BAR_CHAR_FILLED * filled) + (_BAR_CHAR_EMPTY * empty)

    @staticmethod
    def _format_confidence(confidence: float) -> str:
        """Format a 0.0-1.0 confidence score as a percentage string.

        Args:
            confidence: Confidence value between 0.0 and 1.0.

        Returns:
            A string like "85%".
        """
        pct = int(round(confidence * 100))
        return f"{pct}%"

    @staticmethod
    def _owasp_label(category: OWASPCategory) -> str:
        """Get the human-readable OWASP label for a category enum value.

        Falls back to the raw enum value if the category code is not
        found in the lookup table.

        Args:
            category: An ``OWASPCategory`` enum member.

        Returns:
            A descriptive string like "A03: Injection".
        """
        return _OWASP_NAMES.get(category.value, category.value)

    @staticmethod
    def _detect_language_hint(file_path: str) -> str:
        """Infer a Markdown fenced-code-block language hint from a file path.

        Uses the file extension to determine the appropriate syntax
        highlighting language for fenced code blocks.

        Args:
            file_path: Relative or absolute path to the source file.

        Returns:
            A short language identifier (e.g., "python", "javascript"),
            or an empty string if the language cannot be inferred.
        """
        lower = file_path.lower()
        if lower.endswith(".py"):
            return "python"
        if lower.endswith((".js", ".jsx", ".mjs", ".cjs")):
            return "javascript"
        if lower.endswith((".ts", ".tsx")):
            return "typescript"
        if lower.endswith(".json"):
            return "json"
        if lower.endswith((".yml", ".yaml")):
            return "yaml"
        if lower.endswith(".toml"):
            return "toml"
        return ""

    @staticmethod
    def _group_by_severity(findings: List[Finding]) -> Dict[str, List[Finding]]:
        """Group a list of findings by their severity level.

        Findings within each group retain their original order.

        Args:
            findings: Flat list of ``Finding`` objects.

        Returns:
            A dictionary mapping severity name strings (e.g., "CRITICAL")
            to lists of findings with that severity.
        """
        grouped: Dict[str, List[Finding]] = {}
        for finding in findings:
            key = finding.severity.value
            if key not in grouped:
                grouped[key] = []
            grouped[key].append(finding)
        return grouped
