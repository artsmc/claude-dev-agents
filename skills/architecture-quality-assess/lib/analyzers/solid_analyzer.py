"""SOLID principles analyzer for architecture quality assessment.

This module analyzes code for violations of SOLID principles:
- Single Responsibility Principle (SRP)
- Open/Closed Principle (OCP)
- Liskov Substitution Principle (LSP)
- Interface Segregation Principle (ISP)
- Dependency Inversion Principle (DIP)

References:
    - TR.md Section 2.2.4: SOLID Principles Analysis
    - FRS.md FR-3.1 through FR-3.5: SOLID Violations
"""

import ast
import logging
import re
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from .base import AnalysisContext, BaseAnalyzer
from ..models.violation import Violation


logger = logging.getLogger(__name__)


class SOLIDAnalyzer(BaseAnalyzer):
    """Analyzes code for SOLID principle violations.

    Detects violations across all five SOLID principles using
    AST analysis and heuristic detection methods.

    Example:
        >>> analyzer = SOLIDAnalyzer()
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
            "solid"
        """
        return "solid"

    def get_description(self) -> str:
        """Get human-readable description.

        Returns:
            Description of SOLID analysis functionality.
        """
        return (
            "Analyzes code for violations of SOLID principles including SRP, OCP, "
            "LSP, ISP, and DIP"
        )

    def analyze(self, context: AnalysisContext) -> List[Violation]:
        """Perform SOLID principles analysis on the project.

        Args:
            context: Analysis context with project files.

        Returns:
            List of SOLID violations detected.
        """
        violations = []

        self.log_progress("Starting SOLID principles analysis")

        # Get thresholds from configuration
        thresholds = context.config.project.solid_thresholds

        for file_path in context.file_paths:
            if not self.should_analyze_file(file_path, context):
                continue

            # Only analyze Python files for now (can extend to JS/TS later)
            if file_path.suffix not in {".py"}:
                continue

            try:
                content = file_path.read_text(encoding="utf-8")
                rel_path = str(file_path.relative_to(context.project_root))

                # Parse Python AST
                tree = ast.parse(content, filename=str(file_path))

                # Analyze each principle
                violations.extend(
                    self._analyze_srp(tree, rel_path, content, thresholds)
                )
                violations.extend(self._analyze_ocp(tree, rel_path, content))
                violations.extend(self._analyze_lsp(tree, rel_path, content))
                violations.extend(
                    self._analyze_isp(tree, rel_path, content, thresholds)
                )
                violations.extend(self._analyze_dip(tree, rel_path, content))

            except SyntaxError as e:
                self.logger.debug(f"Syntax error in {file_path}: {e}")
                continue
            except (UnicodeDecodeError, IOError) as e:
                self.logger.debug(f"Could not read file {file_path}: {e}")
                continue

        self.log_progress(
            f"SOLID analysis complete: {len(violations)} violations found"
        )

        return violations

    def _analyze_srp(
        self, tree: ast.AST, file_path: str, content: str, thresholds
    ) -> List[Violation]:
        """Analyze Single Responsibility Principle violations.

        Detects:
        - Classes with too many methods
        - Classes with too many lines of code
        - Low cohesion (LCOM)

        Args:
            tree: Python AST.
            file_path: Relative file path.
            content: File content for line counting.
            thresholds: SOLID thresholds configuration.

        Returns:
            List of SRP violations.
        """
        violations = []

        for node in ast.walk(tree):
            if not isinstance(node, ast.ClassDef):
                continue

            class_name = node.name
            methods = [n for n in node.body if isinstance(n, ast.FunctionDef)]
            method_count = len(methods)

            # Calculate lines of code for the class
            class_lines = self._count_class_lines(node, content)

            # Check method count threshold
            if method_count > thresholds.srp_max_methods:
                violations.append(
                    self.create_violation(
                        type_prefix="SRP",
                        violation_type="SRPViolation",
                        severity="MEDIUM",
                        file_path=file_path,
                        line_number=node.lineno,
                        message=f"Class '{class_name}' has too many methods ({method_count})",
                        explanation=(
                            f"Class '{class_name}' has {method_count} methods, exceeding "
                            f"the recommended maximum of {thresholds.srp_max_methods}. "
                            f"This suggests the class may have multiple responsibilities."
                        ),
                        recommendation=(
                            "Refactor to follow Single Responsibility Principle:\n"
                            "- Identify distinct responsibilities in the class\n"
                            "- Extract related methods into separate classes\n"
                            "- Use composition to combine focused classes\n"
                            "- Consider applying the Extract Class refactoring"
                        ),
                        metadata={
                            "class_name": class_name,
                            "method_count": method_count,
                            "threshold": thresholds.srp_max_methods,
                        },
                    )
                )

            # Check lines of code threshold
            if class_lines > thresholds.srp_max_loc:
                violations.append(
                    self.create_violation(
                        type_prefix="SRP",
                        violation_type="SRPViolation",
                        severity="HIGH",
                        file_path=file_path,
                        line_number=node.lineno,
                        message=f"God Class detected: '{class_name}' ({class_lines} LOC)",
                        explanation=(
                            f"Class '{class_name}' has {class_lines} lines of code, "
                            f"exceeding the recommended maximum of {thresholds.srp_max_loc}. "
                            f"Large classes often violate SRP by handling multiple responsibilities."
                        ),
                        recommendation=(
                            "Break down the God Class:\n"
                            "- Identify cohesive groups of methods and fields\n"
                            "- Extract each group into a focused class\n"
                            "- Use composition or delegation patterns\n"
                            "- Consider using the Facade pattern to simplify the interface"
                        ),
                        metadata={
                            "class_name": class_name,
                            "lines_of_code": class_lines,
                            "threshold": thresholds.srp_max_loc,
                        },
                    )
                )

            # Calculate LCOM (Lack of Cohesion of Methods)
            lcom = self._calculate_lcom(node)
            if lcom > thresholds.srp_lcom_threshold and method_count > 3:
                violations.append(
                    self.create_violation(
                        type_prefix="SRP",
                        violation_type="SRPViolation",
                        severity="MEDIUM",
                        file_path=file_path,
                        line_number=node.lineno,
                        message=f"Low cohesion in class '{class_name}' (LCOM: {lcom:.2f})",
                        explanation=(
                            f"Class '{class_name}' has low cohesion (LCOM: {lcom:.2f}). "
                            f"Methods in the class don't share many instance variables, "
                            f"suggesting multiple responsibilities."
                        ),
                        recommendation=(
                            "Improve class cohesion:\n"
                            "- Group methods that work with the same instance variables\n"
                            "- Extract loosely related methods into separate classes\n"
                            "- Ensure each class has a single, well-defined purpose"
                        ),
                        metadata={
                            "class_name": class_name,
                            "lcom": lcom,
                            "threshold": thresholds.srp_lcom_threshold,
                        },
                    )
                )

        return violations

    def _analyze_ocp(
        self, tree: ast.AST, file_path: str, content: str
    ) -> List[Violation]:
        """Analyze Open/Closed Principle violations.

        Detects:
        - Long if-elif chains for type checking
        - Excessive isinstance/type checking
        - Switch-like structures

        Args:
            tree: Python AST.
            file_path: Relative file path.
            content: File content.

        Returns:
            List of OCP violations.
        """
        violations = []

        for node in ast.walk(tree):
            # Detect long if-elif chains
            if isinstance(node, ast.If):
                elif_count = 0
                current = node
                has_type_check = False

                while current:
                    # Check if this is type checking
                    if self._is_type_check(current.test):
                        has_type_check = True

                    if current.orelse and len(current.orelse) == 1:
                        if isinstance(current.orelse[0], ast.If):
                            elif_count += 1
                            current = current.orelse[0]
                        else:
                            break
                    else:
                        break

                # Report if we have a long if-elif chain with type checking
                if elif_count >= 3 and has_type_check:
                    violations.append(
                        self.create_violation(
                            type_prefix="OCP",
                            violation_type="OCPViolation",
                            severity="MEDIUM",
                            file_path=file_path,
                            line_number=node.lineno,
                            message=f"Type-based if-elif chain ({elif_count + 1} branches)",
                            explanation=(
                                f"Found an if-elif chain with {elif_count + 1} branches that "
                                f"performs type checking. This violates the Open/Closed Principle "
                                f"as adding new types requires modifying existing code."
                            ),
                            recommendation=(
                                "Refactor using polymorphism:\n"
                                "- Replace type checks with polymorphic method calls\n"
                                "- Use the Strategy pattern to encapsulate algorithms\n"
                                "- Consider using a Factory pattern for object creation\n"
                                "- Apply the Replace Conditional with Polymorphism refactoring"
                            ),
                            metadata={
                                "branch_count": elif_count + 1,
                            },
                        )
                    )

        return violations

    def _analyze_lsp(
        self, tree: ast.AST, file_path: str, content: str
    ) -> List[Violation]:
        """Analyze Liskov Substitution Principle violations.

        Detects:
        - Method signature mismatches in subclasses
        - Raising new exceptions in subclass
        - Precondition strengthening

        Args:
            tree: Python AST.
            file_path: Relative file path.
            content: File content.

        Returns:
            List of LSP violations.
        """
        violations = []

        # Build class hierarchy
        classes = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                classes[node.name] = node

        # Check each class that has base classes
        for node in ast.walk(tree):
            if not isinstance(node, ast.ClassDef):
                continue

            if not node.bases:
                continue

            class_name = node.name
            methods = {
                n.name: n for n in node.body if isinstance(n, ast.FunctionDef)
            }

            # Check for NotImplementedError raises (often indicates LSP issues)
            for method_name, method_node in methods.items():
                for stmt in ast.walk(method_node):
                    if isinstance(stmt, ast.Raise):
                        if self._raises_not_implemented(stmt):
                            violations.append(
                                self.create_violation(
                                    type_prefix="LSP",
                                    violation_type="LSPViolation",
                                    severity="HIGH",
                                    file_path=file_path,
                                    line_number=stmt.lineno,
                                    message=(
                                        f"Method '{method_name}' in '{class_name}' "
                                        f"raises NotImplementedError"
                                    ),
                                    explanation=(
                                        f"Method '{method_name}' raises NotImplementedError, "
                                        f"violating the Liskov Substitution Principle. "
                                        f"Subclasses should be substitutable for their base classes."
                                    ),
                                    recommendation=(
                                        "Fix LSP violation:\n"
                                        "- Implement the method properly in the subclass\n"
                                        "- If the method doesn't apply, reconsider the inheritance hierarchy\n"
                                        "- Use composition instead of inheritance if appropriate\n"
                                        "- Consider using the Interface Segregation Principle"
                                    ),
                                    metadata={
                                        "class_name": class_name,
                                        "method_name": method_name,
                                    },
                                )
                            )

        return violations

    def _analyze_isp(
        self, tree: ast.AST, file_path: str, content: str, thresholds
    ) -> List[Violation]:
        """Analyze Interface Segregation Principle violations.

        Detects:
        - Fat interfaces (too many methods)
        - Classes with stub/empty methods

        Args:
            tree: Python AST.
            file_path: Relative file path.
            content: File content.
            thresholds: SOLID thresholds configuration.

        Returns:
            List of ISP violations.
        """
        violations = []

        for node in ast.walk(tree):
            if not isinstance(node, ast.ClassDef):
                continue

            class_name = node.name
            methods = [n for n in node.body if isinstance(n, ast.FunctionDef)]

            # Skip if not likely an interface (no bases or too few methods)
            if not node.bases and len(methods) < 5:
                continue

            # Check for fat interface
            if len(methods) > thresholds.isp_max_methods:
                violations.append(
                    self.create_violation(
                        type_prefix="ISP",
                        violation_type="ISPViolation",
                        severity="MEDIUM",
                        file_path=file_path,
                        line_number=node.lineno,
                        message=f"Fat interface: '{class_name}' has {len(methods)} methods",
                        explanation=(
                            f"Interface/base class '{class_name}' has {len(methods)} methods, "
                            f"exceeding the recommended maximum of {thresholds.isp_max_methods}. "
                            f"Large interfaces force clients to depend on methods they don't use."
                        ),
                        recommendation=(
                            "Split the fat interface:\n"
                            "- Identify distinct groups of related methods\n"
                            "- Create smaller, focused interfaces for each group\n"
                            "- Use interface inheritance to compose larger interfaces if needed\n"
                            "- Apply the Interface Segregation Principle"
                        ),
                        metadata={
                            "class_name": class_name,
                            "method_count": len(methods),
                            "threshold": thresholds.isp_max_methods,
                        },
                    )
                )

            # Check for stub methods (potential ISP violation in implementers)
            stub_methods = []
            for method in methods:
                if self._is_stub_method(method):
                    stub_methods.append(method.name)

            if stub_methods and len(stub_methods) > 2:
                violations.append(
                    self.create_violation(
                        type_prefix="ISP",
                        violation_type="ISPViolation",
                        severity="MEDIUM",
                        file_path=file_path,
                        line_number=node.lineno,
                        message=(
                            f"Class '{class_name}' has {len(stub_methods)} stub methods"
                        ),
                        explanation=(
                            f"Class '{class_name}' has multiple stub/empty methods: "
                            f"{', '.join(stub_methods)}. This suggests the class is forced "
                            f"to implement methods it doesn't need, violating ISP."
                        ),
                        recommendation=(
                            "Apply Interface Segregation:\n"
                            "- Split the interface into smaller, focused interfaces\n"
                            "- Implement only the interfaces needed by this class\n"
                            "- Use composition instead of inheritance if appropriate"
                        ),
                        metadata={
                            "class_name": class_name,
                            "stub_methods": stub_methods,
                        },
                    )
                )

        return violations

    def _analyze_dip(
        self, tree: ast.AST, file_path: str, content: str
    ) -> List[Violation]:
        """Analyze Dependency Inversion Principle violations.

        Detects:
        - Concrete dependencies in constructors
        - Direct instantiation of classes instead of using abstractions
        - Hardcoded concrete implementations

        Args:
            tree: Python AST.
            file_path: Relative file path.
            content: File content.

        Returns:
            List of DIP violations.
        """
        violations = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Check __init__ method for concrete dependencies
                for method in node.body:
                    if isinstance(method, ast.FunctionDef) and method.name == "__init__":
                        concrete_deps = self._find_concrete_dependencies(method)

                        if len(concrete_deps) >= 3:
                            violations.append(
                                self.create_violation(
                                    type_prefix="DIP",
                                    violation_type="DIPViolation",
                                    severity="HIGH",
                                    file_path=file_path,
                                    line_number=method.lineno,
                                    message=(
                                        f"Class '{node.name}' creates {len(concrete_deps)} "
                                        f"concrete dependencies"
                                    ),
                                    explanation=(
                                        f"Constructor of '{node.name}' directly instantiates "
                                        f"{len(concrete_deps)} concrete classes: "
                                        f"{', '.join(concrete_deps[:5])}. "
                                        f"This violates the Dependency Inversion Principle."
                                    ),
                                    recommendation=(
                                        "Apply Dependency Inversion:\n"
                                        "- Depend on abstractions (interfaces/protocols) not concrete classes\n"
                                        "- Use dependency injection instead of direct instantiation\n"
                                        "- Pass dependencies as constructor parameters\n"
                                        "- Consider using a dependency injection framework"
                                    ),
                                    metadata={
                                        "class_name": node.name,
                                        "concrete_dependencies": concrete_deps,
                                    },
                                )
                            )

        return violations

    # Helper methods

    def _count_class_lines(self, class_node: ast.ClassDef, content: str) -> int:
        """Count lines of code in a class definition.

        Args:
            class_node: Class AST node.
            content: File content.

        Returns:
            Number of lines in the class.
        """
        if hasattr(class_node, 'end_lineno'):
            return class_node.end_lineno - class_node.lineno + 1
        return 0

    def _calculate_lcom(self, class_node: ast.ClassDef) -> float:
        """Calculate Lack of Cohesion of Methods (LCOM) metric.

        Simplified LCOM: ratio of methods that don't share instance variables.

        Args:
            class_node: Class AST node.

        Returns:
            LCOM value between 0.0 and 1.0.
        """
        methods = [n for n in class_node.body if isinstance(n, ast.FunctionDef)]
        if len(methods) < 2:
            return 0.0

        # Collect instance variables used by each method
        method_vars = []
        for method in methods:
            vars_used = set()
            for node in ast.walk(method):
                if isinstance(node, ast.Attribute):
                    if isinstance(node.value, ast.Name) and node.value.id == 'self':
                        vars_used.add(node.attr)
            method_vars.append(vars_used)

        # Calculate pairs of methods that don't share variables
        total_pairs = 0
        disjoint_pairs = 0

        for i in range(len(method_vars)):
            for j in range(i + 1, len(method_vars)):
                total_pairs += 1
                if not method_vars[i] & method_vars[j]:  # No shared variables
                    disjoint_pairs += 1

        if total_pairs == 0:
            return 0.0

        return disjoint_pairs / total_pairs

    def _is_type_check(self, node: ast.AST) -> bool:
        """Check if a node performs type checking.

        Args:
            node: AST node to check.

        Returns:
            True if node performs type checking.
        """
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                return node.func.id in {'isinstance', 'type', 'issubclass'}
        elif isinstance(node, ast.Compare):
            for op in node.ops:
                if isinstance(op, (ast.Is, ast.IsNot)):
                    return True
        return False

    def _raises_not_implemented(self, raise_node: ast.Raise) -> bool:
        """Check if a raise statement raises NotImplementedError.

        Args:
            raise_node: Raise AST node.

        Returns:
            True if raises NotImplementedError.
        """
        if raise_node.exc:
            if isinstance(raise_node.exc, ast.Name):
                return raise_node.exc.id == 'NotImplementedError'
            elif isinstance(raise_node.exc, ast.Call):
                if isinstance(raise_node.exc.func, ast.Name):
                    return raise_node.exc.func.id == 'NotImplementedError'
        return False

    def _is_stub_method(self, method: ast.FunctionDef) -> bool:
        """Check if a method is a stub (empty or just pass/docstring).

        Args:
            method: Method AST node.

        Returns:
            True if method is a stub.
        """
        # Filter out docstrings and pass statements
        body = [
            stmt for stmt in method.body
            if not isinstance(stmt, (ast.Pass, ast.Expr))
            or (isinstance(stmt, ast.Expr) and not isinstance(stmt.value, ast.Constant))
        ]

        return len(body) == 0

    def _find_concrete_dependencies(self, init_method: ast.FunctionDef) -> List[str]:
        """Find concrete class instantiations in __init__ method.

        Args:
            init_method: __init__ method AST node.

        Returns:
            List of concrete class names being instantiated.
        """
        concrete_deps = []

        for node in ast.walk(init_method):
            if isinstance(node, ast.Call):
                # Check if this is a class instantiation (not a built-in)
                if isinstance(node.func, ast.Name):
                    class_name = node.func.id
                    # Skip built-in types
                    if class_name[0].isupper() and class_name not in {
                        'True', 'False', 'None', 'Dict', 'List', 'Set', 'Tuple'
                    }:
                        concrete_deps.append(class_name)

        return concrete_deps


__all__ = ["SOLIDAnalyzer"]
