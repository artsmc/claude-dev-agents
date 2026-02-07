"""Anti-pattern and design pattern analyzer for architecture quality assessment.

This module detects common anti-patterns and missing design patterns
that indicate code quality issues.

References:
    - TR.md Section 2.1: Pattern Detection
    - FRS.md FR-4.1 through FR-4.4: Design Pattern Detection
"""

import ast
import logging
import re
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Set

from .base import AnalysisContext, BaseAnalyzer
from ..models.violation import Violation


logger = logging.getLogger(__name__)


class PatternAnalyzer(BaseAnalyzer):
    """Analyzes code for anti-patterns and missing design patterns.

    Detects anti-patterns:
    - God classes (already covered by SOLID but worth noting)
    - Magic numbers
    - Long methods
    - Nested loops (complexity)
    - Dead code (unused imports, variables)

    Detects missing patterns:
    - Repository pattern opportunities
    - Factory pattern opportunities
    - Strategy pattern opportunities
    - Singleton misuse

    Example:
        >>> analyzer = PatternAnalyzer()
        >>> context = AnalysisContext(
        ...     project_root=Path("/path/to/project"),
        ...     config=config,
        ...     file_paths=all_files
        ... )
        >>> violations = analyzer.analyze(context)
    """

    def get_name(self) -> str:
        """Get analyzer identifier.

        Returns:
            "patterns"
        """
        return "patterns"

    def get_description(self) -> str:
        """Get human-readable description.

        Returns:
            Description of pattern analysis functionality.
        """
        return (
            "Detects common anti-patterns and missing design patterns including "
            "magic numbers, long methods, and opportunities for Repository, Factory, "
            "and Strategy patterns"
        )

    def analyze(self, context: AnalysisContext) -> List[Violation]:
        """Perform pattern analysis on the project.

        Args:
            context: Analysis context with project files.

        Returns:
            List of pattern violations detected.
        """
        violations = []

        self.log_progress("Starting anti-pattern and design pattern analysis")

        for file_path in context.file_paths:
            if not self.should_analyze_file(file_path, context):
                continue

            # Only analyze Python files for now
            if file_path.suffix not in {".py"}:
                continue

            try:
                content = file_path.read_text(encoding="utf-8")
                rel_path = str(file_path.relative_to(context.project_root))

                # Parse Python AST
                tree = ast.parse(content, filename=str(file_path))

                # Detect anti-patterns
                violations.extend(self._detect_magic_numbers(tree, rel_path))
                violations.extend(self._detect_long_methods(tree, rel_path, content))
                violations.extend(self._detect_complex_methods(tree, rel_path))
                violations.extend(self._detect_dead_code(tree, rel_path))

                # Detect missing patterns
                violations.extend(
                    self._detect_factory_opportunities(tree, rel_path)
                )
                violations.extend(
                    self._detect_strategy_opportunities(tree, rel_path)
                )
                violations.extend(
                    self._detect_singleton_misuse(tree, rel_path, content)
                )

            except SyntaxError as e:
                self.logger.debug(f"Syntax error in {file_path}: {e}")
                continue
            except (UnicodeDecodeError, IOError) as e:
                self.logger.debug(f"Could not read file {file_path}: {e}")
                continue

        self.log_progress(
            f"Pattern analysis complete: {len(violations)} violations found"
        )

        return violations

    def _detect_magic_numbers(
        self, tree: ast.AST, file_path: str
    ) -> List[Violation]:
        """Detect magic numbers in code.

        Args:
            tree: Python AST.
            file_path: Relative file path.

        Returns:
            List of magic number violations.
        """
        violations = []
        magic_numbers = []

        # Acceptable numbers that aren't magic
        acceptable = {0, 1, -1, 2, 10, 100, 1000}

        for node in ast.walk(tree):
            # Look for numeric constants
            if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
                # Skip if it's an acceptable value
                if node.value in acceptable:
                    continue

                # Skip if it's in a default argument or constant definition
                parent = self._get_parent_node(tree, node)
                if isinstance(parent, (ast.Assign, ast.AnnAssign)):
                    # This might be a named constant, which is fine
                    continue

                magic_numbers.append((node.lineno, node.value))

        # Report if we found multiple magic numbers
        if len(magic_numbers) >= 5:
            sample = magic_numbers[:3]
            sample_text = ", ".join(f"{val} (line {line})" for line, val in sample)

            violations.append(
                self.create_violation(
                    type_prefix="PAT",
                    violation_type="MagicNumbers",
                    severity="LOW",
                    file_path=file_path,
                    line_number=magic_numbers[0][0],
                    message=f"Multiple magic numbers detected ({len(magic_numbers)} found)",
                    explanation=(
                        f"Found {len(magic_numbers)} magic numbers (unexplained numeric constants) "
                        f"in the code. Examples: {sample_text}. Magic numbers make code harder "
                        f"to understand and maintain."
                    ),
                    recommendation=(
                        "Replace magic numbers with named constants:\n"
                        "- Define constants at module or class level with descriptive names\n"
                        "- Use enums for related constant values\n"
                        "- Add comments explaining the significance of values"
                    ),
                    metadata={
                        "count": len(magic_numbers),
                        "examples": [val for _, val in sample],
                    },
                )
            )

        return violations

    def _detect_long_methods(
        self, tree: ast.AST, file_path: str, content: str
    ) -> List[Violation]:
        """Detect methods that are too long.

        Args:
            tree: Python AST.
            file_path: Relative file path.
            content: File content.

        Returns:
            List of long method violations.
        """
        violations = []

        for node in ast.walk(tree):
            if not isinstance(node, ast.FunctionDef):
                continue

            # Calculate method length
            if hasattr(node, 'end_lineno'):
                method_length = node.end_lineno - node.lineno + 1
            else:
                continue

            # Long method threshold: 50 lines
            if method_length > 50:
                severity = "HIGH" if method_length > 100 else "MEDIUM"

                violations.append(
                    self.create_violation(
                        type_prefix="PAT",
                        violation_type="LongMethod",
                        severity=severity,
                        file_path=file_path,
                        line_number=node.lineno,
                        message=f"Long method detected: '{node.name}' ({method_length} lines)",
                        explanation=(
                            f"Method '{node.name}' is {method_length} lines long. "
                            f"Long methods are hard to understand, test, and maintain."
                        ),
                        recommendation=(
                            "Refactor the long method:\n"
                            "- Extract logical sections into smaller helper methods\n"
                            "- Use the Extract Method refactoring pattern\n"
                            "- Each method should do one thing and do it well\n"
                            "- Aim for methods under 30 lines"
                        ),
                        metadata={
                            "method_name": node.name,
                            "line_count": method_length,
                        },
                    )
                )

        return violations

    def _detect_complex_methods(
        self, tree: ast.AST, file_path: str
    ) -> List[Violation]:
        """Detect overly complex methods with nested loops or conditionals.

        Args:
            tree: Python AST.
            file_path: Relative file path.

        Returns:
            List of complexity violations.
        """
        violations = []

        for node in ast.walk(tree):
            if not isinstance(node, ast.FunctionDef):
                continue

            # Calculate cyclomatic complexity (simplified)
            complexity = self._calculate_complexity(node)

            if complexity > 10:
                severity = "HIGH" if complexity > 15 else "MEDIUM"

                violations.append(
                    self.create_violation(
                        type_prefix="PAT",
                        violation_type="ComplexMethod",
                        severity=severity,
                        file_path=file_path,
                        line_number=node.lineno,
                        message=(
                            f"Complex method detected: '{node.name}' "
                            f"(complexity: {complexity})"
                        ),
                        explanation=(
                            f"Method '{node.name}' has high cyclomatic complexity ({complexity}). "
                            f"Complex methods with many branches are hard to test and maintain."
                        ),
                        recommendation=(
                            "Reduce method complexity:\n"
                            "- Extract complex conditions into well-named methods\n"
                            "- Use early returns to reduce nesting\n"
                            "- Consider using the Strategy pattern for complex conditionals\n"
                            "- Split the method into smaller, focused methods"
                        ),
                        metadata={
                            "method_name": node.name,
                            "complexity": complexity,
                        },
                    )
                )

        return violations

    def _detect_dead_code(
        self, tree: ast.AST, file_path: str
    ) -> List[Violation]:
        """Detect unused imports and potential dead code.

        Args:
            tree: Python AST.
            file_path: Relative file path.

        Returns:
            List of dead code violations.
        """
        violations = []

        # Collect all imports
        imports = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.asname if alias.asname else alias.name)
            elif isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    imports.add(alias.asname if alias.asname else alias.name)

        # Collect all name usages
        names_used = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                names_used.add(node.id)

        # Find unused imports
        unused_imports = imports - names_used

        # Ignore common false positives
        unused_imports = {
            imp for imp in unused_imports
            if not imp.startswith('_') and imp not in {'annotations'}
        }

        if len(unused_imports) >= 3:
            violations.append(
                self.create_violation(
                    type_prefix="PAT",
                    violation_type="UnusedImports",
                    severity="LOW",
                    file_path=file_path,
                    message=f"{len(unused_imports)} unused imports detected",
                    explanation=(
                        f"Found {len(unused_imports)} unused imports: "
                        f"{', '.join(sorted(list(unused_imports)[:5]))}. "
                        f"Unused imports clutter code and may indicate dead code."
                    ),
                    recommendation=(
                        "Remove unused imports:\n"
                        "- Delete imports that aren't being used\n"
                        "- Use tools like autoflake or ruff to clean up imports\n"
                        "- Configure your IDE to highlight unused imports"
                    ),
                    metadata={
                        "unused_imports": list(unused_imports),
                    },
                )
            )

        return violations

    def _detect_factory_opportunities(
        self, tree: ast.AST, file_path: str
    ) -> List[Violation]:
        """Detect opportunities for Factory pattern.

        Looks for scattered object creation with complex parameters.

        Args:
            tree: Python AST.
            file_path: Relative file path.

        Returns:
            List of factory opportunity violations.
        """
        violations = []

        # Track class instantiations
        instantiations = defaultdict(list)

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    # Track constructor calls
                    if node.func.id[0].isupper():  # Likely a class name
                        # Check if it has many arguments
                        arg_count = len(node.args) + len(node.keywords)
                        if arg_count >= 5:
                            instantiations[node.func.id].append(
                                (node.lineno, arg_count)
                            )

        # Report if we find many instantiations of the same complex class
        for class_name, instances in instantiations.items():
            if len(instances) >= 3:
                violations.append(
                    self.create_violation(
                        type_prefix="PAT",
                        violation_type="FactoryOpportunity",
                        severity="MEDIUM",
                        file_path=file_path,
                        line_number=instances[0][0],
                        message=(
                            f"Factory pattern opportunity: '{class_name}' "
                            f"instantiated {len(instances)} times"
                        ),
                        explanation=(
                            f"Class '{class_name}' is instantiated {len(instances)} times "
                            f"with complex parameters (5+ arguments). This scattered object "
                            f"creation makes code harder to maintain."
                        ),
                        recommendation=(
                            "Consider using Factory pattern:\n"
                            "- Create a factory class or method to encapsulate object creation\n"
                            "- Centralize complex initialization logic\n"
                            "- Make it easier to change object creation strategy\n"
                            "- Improve testability through dependency injection"
                        ),
                        metadata={
                            "class_name": class_name,
                            "instantiation_count": len(instances),
                        },
                    )
                )

        return violations

    def _detect_strategy_opportunities(
        self, tree: ast.AST, file_path: str
    ) -> List[Violation]:
        """Detect opportunities for Strategy pattern.

        Looks for if-elif chains that select algorithms.

        Args:
            tree: Python AST.
            file_path: Relative file path.

        Returns:
            List of strategy opportunity violations.
        """
        violations = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Look for long if-elif chains in methods
                for child in ast.walk(node):
                    if isinstance(child, ast.If):
                        elif_count = 0
                        current = child

                        while current:
                            if current.orelse and len(current.orelse) == 1:
                                if isinstance(current.orelse[0], ast.If):
                                    elif_count += 1
                                    current = current.orelse[0]
                                else:
                                    break
                            else:
                                break

                        # Report if we have a very long if-elif chain
                        if elif_count >= 4:
                            violations.append(
                                self.create_violation(
                                    type_prefix="PAT",
                                    violation_type="StrategyOpportunity",
                                    severity="MEDIUM",
                                    file_path=file_path,
                                    line_number=child.lineno,
                                    message=(
                                        f"Strategy pattern opportunity in '{node.name}' "
                                        f"({elif_count + 1} branches)"
                                    ),
                                    explanation=(
                                        f"Method '{node.name}' has a long if-elif chain with "
                                        f"{elif_count + 1} branches. This suggests different "
                                        f"algorithms being selected at runtime."
                                    ),
                                    recommendation=(
                                        "Consider using Strategy pattern:\n"
                                        "- Create a strategy interface with an execute method\n"
                                        "- Implement each branch as a concrete strategy class\n"
                                        "- Use a dictionary or factory to select strategies\n"
                                        "- Makes adding new strategies easier (Open/Closed Principle)"
                                    ),
                                    metadata={
                                        "method_name": node.name,
                                        "branch_count": elif_count + 1,
                                    },
                                )
                            )

        return violations

    def _detect_singleton_misuse(
        self, tree: ast.AST, file_path: str, content: str
    ) -> List[Violation]:
        """Detect Singleton pattern misuse.

        Args:
            tree: Python AST.
            file_path: Relative file path.
            content: File content.

        Returns:
            List of singleton misuse violations.
        """
        violations = []

        # Look for singleton pattern implementation
        singleton_patterns = [
            r'def\s+__new__\s*\(',
            r'_instance\s*=\s*None',
            r'class\s+\w+\s*\(.*Singleton.*\)',
        ]

        has_singleton = any(
            re.search(pattern, content, re.MULTILINE)
            for pattern in singleton_patterns
        )

        if has_singleton:
            # Look for mutable state in the class
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Check for class-level mutable attributes
                    has_mutable_state = False
                    for item in node.body:
                        if isinstance(item, ast.Assign):
                            for target in item.targets:
                                if isinstance(target, ast.Name):
                                    # Check if it's a mutable type
                                    if isinstance(item.value, (ast.List, ast.Dict, ast.Set)):
                                        has_mutable_state = True
                                        break

                    if has_mutable_state:
                        violations.append(
                            self.create_violation(
                                type_prefix="PAT",
                                violation_type="SingletonMisuse",
                                severity="MEDIUM",
                                file_path=file_path,
                                line_number=node.lineno,
                                message=f"Singleton with mutable state: '{node.name}'",
                                explanation=(
                                    f"Class '{node.name}' implements Singleton pattern with "
                                    f"mutable state. Singletons with mutable state create "
                                    f"global state, making testing difficult and introducing "
                                    f"coupling."
                                ),
                                recommendation=(
                                    "Avoid Singleton with mutable state:\n"
                                    "- Use dependency injection instead of Singleton\n"
                                    "- Make the class stateless if possible\n"
                                    "- Consider using composition over inheritance\n"
                                    "- Use configuration objects instead of global state"
                                ),
                                metadata={
                                    "class_name": node.name,
                                },
                            )
                        )

        return violations

    # Helper methods

    def _get_parent_node(self, tree: ast.AST, target: ast.AST) -> ast.AST:
        """Get the parent node of a target node.

        Args:
            tree: Root AST.
            target: Target node.

        Returns:
            Parent node or None.
        """
        for node in ast.walk(tree):
            for child in ast.iter_child_nodes(node):
                if child == target:
                    return node
        return None

    def _calculate_complexity(self, func_node: ast.FunctionDef) -> int:
        """Calculate cyclomatic complexity of a function.

        Simplified calculation: count decision points.

        Args:
            func_node: Function AST node.

        Returns:
            Complexity score.
        """
        complexity = 1  # Base complexity

        for node in ast.walk(func_node):
            # Each decision point increases complexity
            if isinstance(node, (ast.If, ast.For, ast.While, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                # Each boolean operator adds a path
                complexity += len(node.values) - 1

        return complexity


__all__ = ["PatternAnalyzer"]
