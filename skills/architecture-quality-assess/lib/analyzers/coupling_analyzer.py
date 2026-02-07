"""Coupling analyzer for architecture quality assessment.

This module analyzes module coupling through FAN-IN and FAN-OUT metrics,
detecting tightly coupled modules, God modules, and excessive dependency
violations.

References:
    - TR.md Section 2.2.5: Coupling Analysis
    - FRS.md FR-5.1: FAN-IN/FAN-OUT Metrics
    - FRS.md FR-5.2: Circular Dependency Detection
    - FRS.md FR-5.4: Transitive Dependency Tracking
"""

import logging
from pathlib import Path
from typing import List

from ..graph.dependency_graph import DependencyGraph
from ..models.config import AssessmentConfig
from .base import AnalysisContext, BaseAnalyzer
from ..models.violation import Violation


logger = logging.getLogger(__name__)


class CouplingAnalyzer(BaseAnalyzer):
    """Analyzes module coupling and dependency metrics.

    Detects violations related to:
    - High FAN-OUT (too many dependencies)
    - God modules (excessive FAN-IN)
    - Circular dependencies
    - Deep dependency chains

    The analyzer uses the DependencyGraph from the analysis context
    to calculate metrics and detect violations.

    Example:
        >>> analyzer = CouplingAnalyzer()
        >>> context = AnalysisContext(
        ...     project_root=Path("/path/to/project"),
        ...     config=config,
        ...     dependency_graph=graph
        ... )
        >>> violations = analyzer.analyze(context)
    """

    def get_name(self) -> str:
        """Get analyzer identifier.

        Returns:
            "coupling"
        """
        return "coupling"

    def get_description(self) -> str:
        """Get human-readable description.

        Returns:
            Description of coupling analysis functionality.
        """
        return (
            "Analyzes module coupling through FAN-IN/FAN-OUT metrics, "
            "detects tightly coupled modules, God modules, and circular dependencies"
        )

    def analyze(self, context: AnalysisContext) -> List[Violation]:
        """Perform coupling analysis on the project.

        Args:
            context: Analysis context with dependency graph.

        Returns:
            List of coupling violations detected.

        Raises:
            AnalyzerError: If dependency graph is not available.
        """
        from .base import AnalyzerError

        if context.dependency_graph is None:
            raise AnalyzerError("Dependency graph is required for coupling analysis")

        graph: DependencyGraph = context.dependency_graph
        violations = []

        self.log_progress("Starting coupling analysis")

        # Get thresholds from configuration
        thresholds = context.config.project.coupling_thresholds

        # Analyze FAN-OUT violations (high coupling)
        violations.extend(self._analyze_fan_out(graph, thresholds, context))

        # Analyze FAN-IN violations (God modules)
        violations.extend(self._analyze_fan_in(graph, thresholds, context))

        # Detect circular dependencies
        violations.extend(self._analyze_circular_dependencies(graph, context))

        # Detect deep dependency chains
        violations.extend(self._analyze_deep_chains(graph, context))

        self.log_progress(
            f"Coupling analysis complete: {len(violations)} violations found"
        )

        return violations

    def _analyze_fan_out(
        self,
        graph: DependencyGraph,
        thresholds,
        context: AnalysisContext,
    ) -> List[Violation]:
        """Analyze FAN-OUT metrics and detect high coupling.

        Args:
            graph: Dependency graph to analyze.
            thresholds: Coupling thresholds configuration.
            context: Analysis context.

        Returns:
            List of FAN-OUT violations.
        """
        violations = []
        highly_coupled = graph.get_highly_coupled_modules(
            fan_out_threshold=thresholds.fan_out_medium
        )

        for node in highly_coupled:
            fan_out = node.fan_out

            # Determine severity based on threshold
            if fan_out >= thresholds.fan_out_high:
                severity = "HIGH"
                message = f"Excessive coupling detected (FAN-OUT: {fan_out})"
            else:
                severity = "MEDIUM"
                message = f"High coupling detected (FAN-OUT: {fan_out})"

            # Build dependency list for explanation
            dep_list = "\n".join(f"  - {dep}" for dep in sorted(node.dependencies)[:10])
            if len(node.dependencies) > 10:
                dep_list += f"\n  ... and {len(node.dependencies) - 10} more"

            violation = self.create_violation(
                type_prefix="CPL",
                violation_type="HighCoupling",
                severity=severity,
                file_path=node.module_path,
                message=message,
                explanation=(
                    f"Module '{node.module_path}' depends on {fan_out} other modules, "
                    f"indicating tight coupling. High FAN-OUT makes the module fragile "
                    f"and difficult to maintain, as changes in dependencies may require "
                    f"changes here.\n\n"
                    f"Dependencies:\n{dep_list}"
                ),
                recommendation=(
                    "Consider refactoring to reduce dependencies:\n"
                    "- Extract shared logic to dedicated utility modules\n"
                    "- Apply Dependency Inversion Principle (depend on abstractions)\n"
                    "- Use dependency injection to reduce direct coupling\n"
                    "- Break down large module into smaller, focused modules"
                ),
                metadata={
                    "fan_out": fan_out,
                    "fan_in": node.fan_in,
                    "instability": node.instability,
                    "dependencies": list(node.dependencies),
                },
            )
            violations.append(violation)

        return violations

    def _analyze_fan_in(
        self,
        graph: DependencyGraph,
        thresholds,
        context: AnalysisContext,
    ) -> List[Violation]:
        """Analyze FAN-IN metrics and detect God modules.

        Args:
            graph: Dependency graph to analyze.
            thresholds: Coupling thresholds configuration.
            context: Analysis context.

        Returns:
            List of God module violations.
        """
        violations = []
        god_modules = graph.get_god_modules(
            fan_in_threshold=thresholds.fan_in_god_module
        )

        for node in god_modules:
            fan_in = node.fan_in

            # God modules are always HIGH severity
            severity = "HIGH"
            message = f"God Module detected (FAN-IN: {fan_in})"

            # Build dependent list for explanation
            dep_list = "\n".join(f"  - {dep}" for dep in sorted(node.dependents)[:10])
            if len(node.dependents) > 10:
                dep_list += f"\n  ... and {len(node.dependents) - 10} more"

            violation = self.create_violation(
                type_prefix="CPL",
                violation_type="GodModule",
                severity=severity,
                file_path=node.module_path,
                message=message,
                explanation=(
                    f"Module '{node.module_path}' is depended upon by {fan_in} other modules, "
                    f"indicating a 'God Module' anti-pattern. This creates a central point of "
                    f"failure and makes changes risky, as they affect many dependents.\n\n"
                    f"Dependents:\n{dep_list}"
                ),
                recommendation=(
                    "Consider splitting this module:\n"
                    "- Identify distinct responsibilities and extract them to separate modules\n"
                    "- Use the Facade pattern to provide simplified interfaces\n"
                    "- Apply the Single Responsibility Principle\n"
                    "- Create smaller, domain-specific modules instead of one large utility module"
                ),
                metadata={
                    "fan_in": fan_in,
                    "fan_out": node.fan_out,
                    "instability": node.instability,
                    "dependents": list(node.dependents),
                },
            )
            violations.append(violation)

        return violations

    def _analyze_circular_dependencies(
        self,
        graph: DependencyGraph,
        context: AnalysisContext,
    ) -> List[Violation]:
        """Detect circular dependencies in the dependency graph.

        Args:
            graph: Dependency graph to analyze.
            context: Analysis context.

        Returns:
            List of circular dependency violations.
        """
        violations = []
        cycles = graph.detect_cycles()

        # Track unique cycles (cycles can be detected from multiple entry points)
        seen_cycles = set()

        for cycle in cycles:
            # Create a normalized representation of the cycle for deduplication
            # Sort cycle to handle different starting points
            normalized = tuple(sorted(cycle))
            if normalized in seen_cycles:
                continue
            seen_cycles.add(normalized)

            # Create cycle path visualization
            cycle_path = " -> ".join(cycle)

            # Circular dependencies are always CRITICAL
            violation = self.create_violation(
                type_prefix="CPL",
                violation_type="CircularDependency",
                severity="CRITICAL",
                file_path=cycle[0],  # First file in the cycle
                message=f"Circular dependency detected involving {len(cycle)} modules",
                explanation=(
                    f"A circular dependency cycle was detected:\n\n"
                    f"{cycle_path}\n\n"
                    f"Circular dependencies make code harder to understand, test, and maintain. "
                    f"They can cause initialization issues and make refactoring difficult."
                ),
                recommendation=(
                    "Break the circular dependency by:\n"
                    "- Extracting shared code to a new module that both can depend on\n"
                    "- Using dependency injection to invert one of the dependencies\n"
                    "- Applying the Dependency Inversion Principle\n"
                    "- Refactoring to establish a clear dependency hierarchy"
                ),
                metadata={
                    "cycle": cycle,
                    "cycle_length": len(cycle),
                },
            )
            violations.append(violation)

        return violations

    def _analyze_deep_chains(
        self,
        graph: DependencyGraph,
        context: AnalysisContext,
    ) -> List[Violation]:
        """Detect deep dependency chains that indicate complexity.

        Args:
            graph: Dependency graph to analyze.
            context: Analysis context.

        Returns:
            List of deep dependency chain violations.
        """
        violations = []

        # Find chains deeper than 5 levels
        deep_chains = graph.find_deep_dependency_chains(min_depth=6)

        # Track unique chains to avoid duplicates
        seen_chains = set()

        for chain in deep_chains:
            # Create normalized representation
            normalized = tuple(chain)
            if normalized in seen_chains:
                continue
            seen_chains.add(normalized)

            chain_path = " -> ".join(chain)
            depth = len(chain)

            # Deep chains are MEDIUM severity
            violation = self.create_violation(
                type_prefix="CPL",
                violation_type="DeepDependencyChain",
                severity="MEDIUM",
                file_path=chain[0],
                message=f"Deep dependency chain detected (depth: {depth})",
                explanation=(
                    f"A dependency chain of {depth} levels was detected:\n\n"
                    f"{chain_path}\n\n"
                    f"Deep dependency chains increase complexity and make the codebase "
                    f"harder to understand and maintain. Changes at the end of the chain "
                    f"can have ripple effects throughout."
                ),
                recommendation=(
                    "Consider refactoring to reduce dependency depth:\n"
                    "- Flatten the dependency hierarchy where possible\n"
                    "- Extract common dependencies to reduce chain length\n"
                    "- Review if all intermediate dependencies are necessary\n"
                    "- Consider using dependency injection to simplify dependencies"
                ),
                metadata={
                    "chain": chain,
                    "depth": depth,
                },
            )
            violations.append(violation)

            # Limit the number of deep chain violations to avoid overwhelming output
            if len(violations) >= 10:
                break

        return violations


__all__ = ["CouplingAnalyzer"]
