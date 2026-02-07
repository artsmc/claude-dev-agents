"""Task generator for PM-DB integration.

Converts architecture assessment violations into actionable task lists
compatible with PM-DB and /start-phase-execute workflows. Tasks are
organized by priority, include verification criteria, and estimate effort.

Generated tasks follow the format used by the code-duplication skill
and other PM-DB-integrated tools.
"""

from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from ..models.assessment import AssessmentResult
from ..models.violation import Violation


class TaskGenerator:
    """Generate PM-DB compatible task lists from assessment results.

    Converts violations into structured refactoring tasks with:
    - Priority-based organization (P0/P1/P2/P3)
    - Clear action items
    - Verification criteria
    - Estimated effort
    - File references
    """

    def __init__(self, result: AssessmentResult):
        """Initialize the task generator.

        Args:
            result: Complete assessment result to generate tasks from.
        """
        self.result = result

    def generate(self) -> str:
        """Generate the complete task list document.

        Returns:
            Markdown-formatted task list ready for PM-DB import.
        """
        sections = [
            self._header(),
            self._critical_tasks(),
            self._high_priority_tasks(),
            self._medium_priority_tasks(),
            self._low_priority_tasks(),
            self._footer(),
        ]

        # Filter out empty sections
        sections = [s for s in sections if s.strip()]

        return "\n\n".join(sections)

    def _header(self) -> str:
        """Generate task list header."""
        lines = [
            "# Architecture Refactoring Tasks",
            "",
            f"**Generated**: {self.result.metadata.get('generated_at', 'N/A')}",
            f"**Project**: {self.result.project_info.name}",
            f"**Source**: Architecture Quality Assessment",
            "",
            "This document contains prioritized refactoring tasks to address",
            "architecture quality issues detected during automated analysis.",
            "",
            "## Summary",
            "",
        ]

        # Calculate counts by severity
        critical = sum(1 for v in self.result.violations if v.severity == "CRITICAL")
        high = sum(1 for v in self.result.violations if v.severity == "HIGH")
        medium = sum(1 for v in self.result.violations if v.severity == "MEDIUM")
        low = sum(1 for v in self.result.violations if v.severity == "LOW")

        lines.extend([
            f"- **Priority 0 (Critical)**: {critical} task(s) - Address immediately",
            f"- **Priority 1 (High)**: {high} task(s) - Complete in next sprint",
            f"- **Priority 2 (Medium)**: {medium} task(s) - Plan for next quarter",
            f"- **Priority 3 (Low)**: {low} task(s) - Nice to have improvements",
            "",
            f"**Total Tasks**: {len(self.result.violations)}",
        ])

        return "\n".join(lines)

    def _critical_tasks(self) -> str:
        """Generate critical (P0) tasks section."""
        violations = [v for v in self.result.violations if v.severity == "CRITICAL"]
        if not violations:
            return ""

        lines = [
            "---",
            "",
            "## Phase 1: Critical Fixes (Priority P0)",
            "",
            "**Timeline**: Immediate (within 1-2 days)",
            "",
            "These issues significantly impact code quality and maintainability.",
            "Address them before continuing with new features.",
            "",
        ]

        for i, violation in enumerate(violations, 1):
            lines.extend(self._format_task(i, violation, "P0", "1-4 hours"))

        return "\n".join(lines)

    def _high_priority_tasks(self) -> str:
        """Generate high-priority (P1) tasks section."""
        violations = [v for v in self.result.violations if v.severity == "HIGH"]
        if not violations:
            return ""

        lines = [
            "---",
            "",
            "## Phase 2: High Priority Refactoring (Priority P1)",
            "",
            "**Timeline**: Next sprint (1-2 weeks)",
            "",
            "These issues should be addressed soon to prevent technical debt accumulation.",
            "",
        ]

        for i, violation in enumerate(violations, 1):
            lines.extend(self._format_task(i, violation, "P1", "2-8 hours"))

        return "\n".join(lines)

    def _medium_priority_tasks(self) -> str:
        """Generate medium-priority (P2) tasks section."""
        violations = [v for v in self.result.violations if v.severity == "MEDIUM"]
        if not violations:
            return ""

        lines = [
            "---",
            "",
            "## Phase 3: Medium Priority Improvements (Priority P2)",
            "",
            "**Timeline**: Next quarter (1-3 months)",
            "",
            "These improvements will enhance code quality and maintainability.",
            "",
        ]

        # Group medium tasks by dimension to reduce clutter
        dimension_groups = self._group_by_dimension(violations)

        task_num = 1
        for dimension, dimension_violations in dimension_groups.items():
            if len(dimension_violations) == 1:
                # Single task - show full details
                lines.extend(self._format_task(
                    task_num,
                    dimension_violations[0],
                    "P2",
                    "4-16 hours"
                ))
                task_num += 1
            else:
                # Multiple tasks - create grouped task
                lines.extend(self._format_grouped_task(
                    task_num,
                    dimension,
                    dimension_violations,
                    "P2",
                    "1-2 days"
                ))
                task_num += 1

        return "\n".join(lines)

    def _low_priority_tasks(self) -> str:
        """Generate low-priority (P3) tasks section."""
        violations = [v for v in self.result.violations if v.severity == "LOW"]
        if not violations:
            return ""

        lines = [
            "---",
            "",
            "## Phase 4: Low Priority Enhancements (Priority P3)",
            "",
            "**Timeline**: As time permits",
            "",
            "These are optional improvements that provide minor benefits.",
            "",
        ]

        # Group all low-priority tasks by dimension
        dimension_groups = self._group_by_dimension(violations)

        task_num = 1
        for dimension, dimension_violations in dimension_groups.items():
            lines.extend(self._format_grouped_task(
                task_num,
                dimension,
                dimension_violations,
                "P3",
                "1-4 hours"
            ))
            task_num += 1

        return "\n".join(lines)

    def _footer(self) -> str:
        """Generate task list footer."""
        return "\n".join([
            "---",
            "",
            "## Execution Instructions",
            "",
            "### Using PM-DB",
            "",
            "```bash",
            "# Import this task list into PM-DB",
            "/pm-db import architecture-refactoring-tasks.md",
            "",
            "# Track progress",
            "/start-phase execute architecture-refactoring-tasks.md",
            "```",
            "",
            "### Manual Execution",
            "",
            "1. Start with Phase 1 (Critical) tasks",
            "2. Complete each task and verify the fix",
            "3. Run tests after each change",
            "4. Re-run architecture assessment to confirm resolution",
            "",
            "### Verification",
            "",
            "After completing tasks, re-run the assessment:",
            "",
            "```bash",
            "/architecture-quality-assess",
            "```",
            "",
            "Verify that the violations have been resolved and the quality score has improved.",
            "",
            "---",
            "",
            "*Generated by Architecture Quality Assessment Skill*",
        ])

    def _format_task(
        self,
        task_num: int,
        violation: Violation,
        priority: str,
        effort: str
    ) -> List[str]:
        """Format a single task from a violation.

        Args:
            task_num: Task number in section.
            violation: Violation to convert to task.
            priority: Priority level (P0/P1/P2/P3).
            effort: Estimated effort string.

        Returns:
            List of formatted lines for the task.
        """
        lines = [
            f"### Task {task_num}: {violation.message}",
            "",
            f"**Priority**: {priority}",
            f"**Violation ID**: {violation.id}",
            f"**Type**: {violation.type}",
            f"**File**: `{violation.file_path}`",
        ]

        if violation.line_number:
            lines.append(f"**Line**: {violation.line_number}")

        lines.extend([
            f"**Estimated Effort**: {effort}",
            "",
        ])

        if violation.explanation:
            lines.extend([
                "**Issue**:",
                violation.explanation,
                "",
            ])

        if violation.recommendation:
            lines.extend([
                "**Action**:",
                violation.recommendation,
                "",
            ])

        # Add verification criteria
        lines.extend([
            "**Verification**:",
            "- [ ] Code changes implemented",
            "- [ ] Unit tests pass",
            "- [ ] Architecture assessment confirms fix",
        ])

        # Add dimension-specific verification
        if violation.dimension == "layer":
            lines.append("- [ ] Layer separation validated")
        elif violation.dimension == "solid":
            lines.append("- [ ] SOLID principle compliance verified")
        elif violation.dimension == "coupling":
            lines.append("- [ ] Coupling metrics improved")
        elif violation.dimension == "patterns":
            lines.append("- [ ] Design pattern correctly implemented")

        lines.append("")

        return lines

    def _format_grouped_task(
        self,
        task_num: int,
        dimension: str,
        violations: List[Violation],
        priority: str,
        effort: str
    ) -> List[str]:
        """Format a grouped task for multiple related violations.

        Args:
            task_num: Task number in section.
            dimension: Analysis dimension (layer, solid, etc.).
            violations: List of related violations.
            priority: Priority level (P0/P1/P2/P3).
            effort: Estimated effort string.

        Returns:
            List of formatted lines for the grouped task.
        """
        dimension_names = {
            "layer": "Layer Separation",
            "solid": "SOLID Principles",
            "patterns": "Design Patterns",
            "coupling": "Coupling & Dependencies",
            "organization": "Code Organization",
            "drift": "Architecture Drift",
            "other": "General Quality",
        }

        dimension_name = dimension_names.get(dimension, dimension.title())

        lines = [
            f"### Task {task_num}: Improve {dimension_name}",
            "",
            f"**Priority**: {priority}",
            f"**Type**: Multiple {dimension_name} issues",
            f"**Issue Count**: {len(violations)}",
            f"**Estimated Effort**: {effort}",
            "",
            "**Issues to Address**:",
            "",
        ]

        # List all violations in the group
        for i, violation in enumerate(violations, 1):
            location = violation.file_path
            if violation.line_number:
                location = f"{location}:{violation.line_number}"

            lines.append(f"{i}. **{violation.message}** - `{location}`")
            if violation.recommendation:
                lines.append(f"   - {violation.recommendation}")

        lines.extend([
            "",
            "**Verification**:",
            f"- [ ] All {len(violations)} issues resolved",
            "- [ ] Unit tests pass",
            "- [ ] Architecture assessment confirms fixes",
            "",
        ])

        return lines

    def _group_by_dimension(self, violations: List[Violation]) -> Dict[str, List[Violation]]:
        """Group violations by analysis dimension.

        Args:
            violations: List of violations to group.

        Returns:
            Dictionary mapping dimension to list of violations.
        """
        groups: Dict[str, List[Violation]] = {}

        for violation in violations:
            dimension = violation.dimension or "other"
            if dimension not in groups:
                groups[dimension] = []
            groups[dimension].append(violation)

        return groups


def generate_task_list(
    result: AssessmentResult,
    output_path: Optional[Path] = None
) -> str:
    """Generate and optionally save a task list.

    Convenience function for generating task lists. If an output
    path is provided, the task list will be written to that file.

    Args:
        result: Assessment result to generate tasks from.
        output_path: Optional path to save task list to. If None,
            task list is only returned as a string.

    Returns:
        Generated task list as a markdown string.

    Example:
        >>> tasks = generate_task_list(result, Path("tasks.md"))
        >>> print(f"Generated {tasks.count('### Task')} tasks")
    """
    generator = TaskGenerator(result)
    task_list = generator.generate()

    if output_path:
        output_path.write_text(task_list, encoding='utf-8')

    return task_list
