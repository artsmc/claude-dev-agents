"""Dependency graph construction and analysis.

This module provides the DependencyGraph class for building and
analyzing project dependency graphs. The graph is used for coupling
analysis, circular dependency detection, and transitive dependency
tracking.

References:
    - TR.md Section 2.2.2: Dependency Graph Construction
    - FRS.md FR-5.1: FAN-IN/FAN-OUT Metrics
    - FRS.md FR-5.2: Circular Dependency Detection
"""

import logging
from collections import defaultdict, deque
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple


logger = logging.getLogger(__name__)


@dataclass
class GraphNode:
    """Represents a module node in the dependency graph.

    Attributes:
        module_path: Relative path to the module file.
        dependencies: Set of module paths this module depends on.
        dependents: Set of module paths that depend on this module.
        is_external: True if this is an external dependency.
        metadata: Additional node metadata.
    """

    module_path: str
    dependencies: Set[str] = field(default_factory=set)
    dependents: Set[str] = field(default_factory=set)
    is_external: bool = False
    metadata: Dict = field(default_factory=dict)

    @property
    def fan_in(self) -> int:
        """Number of modules that depend on this module."""
        return len(self.dependents)

    @property
    def fan_out(self) -> int:
        """Number of modules this module depends on."""
        return len(self.dependencies)

    @property
    def instability(self) -> float:
        """Instability metric: fan_out / (fan_in + fan_out).

        A value of 0.0 indicates maximum stability (many dependents,
        few dependencies). A value of 1.0 indicates maximum instability
        (many dependencies, few dependents).

        Returns:
            Instability ratio between 0.0 and 1.0.
        """
        total = self.fan_in + self.fan_out
        if total == 0:
            return 0.0
        return self.fan_out / total


class DependencyGraph:
    """Dependency graph for analyzing module relationships.

    The graph stores modules as nodes and import relationships as
    directed edges. Provides methods for cycle detection, metric
    calculation, and graph traversal.

    Example:
        >>> graph = DependencyGraph()
        >>> graph.add_dependency("src/app.py", "src/utils.py")
        >>> graph.add_dependency("src/utils.py", "src/config.py")
        >>> cycles = graph.detect_cycles()
        >>> metrics = graph.calculate_fan_metrics()
    """

    def __init__(self):
        """Initialize an empty dependency graph."""
        self._nodes: Dict[str, GraphNode] = {}
        self._external_dependencies: Set[str] = set()

    def add_node(
        self,
        module_path: str,
        is_external: bool = False,
        metadata: Optional[Dict] = None,
    ) -> GraphNode:
        """Add a node to the graph or return existing node.

        Args:
            module_path: Relative path to the module.
            is_external: True if this is an external dependency.
            metadata: Additional node metadata.

        Returns:
            The GraphNode instance.
        """
        if module_path not in self._nodes:
            self._nodes[module_path] = GraphNode(
                module_path=module_path,
                is_external=is_external,
                metadata=metadata or {},
            )
            if is_external:
                self._external_dependencies.add(module_path)
            logger.debug(f"Added node: {module_path}")

        return self._nodes[module_path]

    def add_dependency(
        self,
        from_module: str,
        to_module: str,
        is_external: bool = False,
    ) -> None:
        """Add a dependency edge from one module to another.

        Args:
            from_module: Module that imports/depends on another.
            to_module: Module being imported/depended on.
            is_external: True if to_module is an external dependency.
        """
        # Ensure both nodes exist
        from_node = self.add_node(from_module, is_external=False)
        to_node = self.add_node(to_module, is_external=is_external)

        # Add edge
        from_node.dependencies.add(to_module)
        to_node.dependents.add(from_module)

        logger.debug(f"Added dependency: {from_module} -> {to_module}")

    def get_node(self, module_path: str) -> Optional[GraphNode]:
        """Get a node by module path.

        Args:
            module_path: Module path to look up.

        Returns:
            GraphNode if found, None otherwise.
        """
        return self._nodes.get(module_path)

    def get_all_nodes(self) -> List[GraphNode]:
        """Get all nodes in the graph.

        Returns:
            List of all GraphNode instances.
        """
        return list(self._nodes.values())

    def get_internal_nodes(self) -> List[GraphNode]:
        """Get only internal (non-external) nodes.

        Returns:
            List of internal GraphNode instances.
        """
        return [node for node in self._nodes.values() if not node.is_external]

    def has_cycle(self) -> bool:
        """Check if the graph contains any cycles.

        Returns:
            True if at least one cycle exists.
        """
        return len(self.detect_cycles()) > 0

    def detect_cycles(self) -> List[List[str]]:
        """Detect all circular dependencies in the graph.

        Uses depth-first search with a recursion stack to find cycles.
        Only considers internal (non-external) nodes.

        Returns:
            List of cycles, where each cycle is a list of module paths
            forming a circular dependency chain.

        Example:
            >>> cycles = graph.detect_cycles()
            >>> for cycle in cycles:
            ...     print(" -> ".join(cycle))
        """
        cycles = []
        visited = set()
        rec_stack = set()
        path = []

        def dfs(node_path: str) -> None:
            """Depth-first search helper."""
            visited.add(node_path)
            rec_stack.add(node_path)
            path.append(node_path)

            node = self.get_node(node_path)
            if node:
                for dep in node.dependencies:
                    # Skip external dependencies
                    dep_node = self.get_node(dep)
                    if dep_node and dep_node.is_external:
                        continue

                    if dep not in visited:
                        dfs(dep)
                    elif dep in rec_stack:
                        # Found a cycle
                        cycle_start = path.index(dep)
                        cycle = path[cycle_start:] + [dep]
                        cycles.append(cycle)

            path.pop()
            rec_stack.remove(node_path)

        # Run DFS from each unvisited internal node
        for node in self.get_internal_nodes():
            if node.module_path not in visited:
                dfs(node.module_path)

        return cycles

    def calculate_fan_metrics(self) -> Dict[str, Dict[str, any]]:
        """Calculate FAN-IN, FAN-OUT, and instability for all modules.

        Returns:
            Dictionary mapping module paths to metric dictionaries.
            Each metric dictionary contains:
                - fan_in: Number of dependents
                - fan_out: Number of dependencies
                - instability: Instability ratio (0.0-1.0)
                - dependencies: List of dependency paths
                - dependents: List of dependent paths

        Example:
            >>> metrics = graph.calculate_fan_metrics()
            >>> for module, data in metrics.items():
            ...     print(f"{module}: FAN-OUT={data['fan_out']}")
        """
        metrics = {}

        for node in self.get_internal_nodes():
            metrics[node.module_path] = {
                "fan_in": node.fan_in,
                "fan_out": node.fan_out,
                "instability": node.instability,
                "dependencies": list(node.dependencies),
                "dependents": list(node.dependents),
            }

        return metrics

    def get_transitive_dependencies(
        self, module_path: str, max_depth: int = 10
    ) -> Dict[int, Set[str]]:
        """Get transitive dependencies organized by depth level.

        Args:
            module_path: Starting module path.
            max_depth: Maximum depth to traverse.

        Returns:
            Dictionary mapping depth levels to sets of module paths.
            Level 0 contains direct dependencies, level 1 contains
            dependencies of dependencies, etc.

        Example:
            >>> deps = graph.get_transitive_dependencies("src/app.py")
            >>> for level, modules in deps.items():
            ...     print(f"Level {level}: {len(modules)} dependencies")
        """
        result = defaultdict(set)
        visited = set()
        queue = deque([(module_path, 0)])

        while queue:
            current, depth = queue.popleft()

            if current in visited or depth > max_depth:
                continue

            visited.add(current)
            node = self.get_node(current)

            if node and depth > 0:
                # Don't include the starting module
                result[depth - 1].add(current)

            if node:
                for dep in node.dependencies:
                    # Skip external dependencies
                    dep_node = self.get_node(dep)
                    if dep_node and not dep_node.is_external:
                        queue.append((dep, depth + 1))

        return dict(result)

    def find_deep_dependency_chains(
        self, min_depth: int = 5
    ) -> List[List[str]]:
        """Find dependency chains exceeding a minimum depth.

        Args:
            min_depth: Minimum chain length to report.

        Returns:
            List of dependency chains (paths) exceeding min_depth.

        Example:
            >>> chains = graph.find_deep_dependency_chains(min_depth=5)
            >>> for chain in chains:
            ...     print(" -> ".join(chain))
        """
        chains = []

        def dfs_paths(
            node_path: str,
            current_path: List[str],
            visited: Set[str],
        ) -> None:
            """Find all paths from a starting node."""
            if len(current_path) >= min_depth:
                chains.append(current_path.copy())

            node = self.get_node(node_path)
            if node:
                for dep in node.dependencies:
                    # Skip external and already visited
                    dep_node = self.get_node(dep)
                    if (
                        dep_node
                        and not dep_node.is_external
                        and dep not in visited
                    ):
                        dfs_paths(
                            dep,
                            current_path + [dep],
                            visited | {dep},
                        )

        # Start DFS from each internal node
        for node in self.get_internal_nodes():
            dfs_paths(node.module_path, [node.module_path], {node.module_path})

        return chains

    def get_god_modules(self, fan_in_threshold: int = 20) -> List[GraphNode]:
        """Find "God modules" with excessive incoming dependencies.

        Args:
            fan_in_threshold: Minimum FAN-IN to classify as God module.

        Returns:
            List of GraphNodes exceeding the FAN-IN threshold.

        Example:
            >>> god_modules = graph.get_god_modules(fan_in_threshold=20)
            >>> for module in god_modules:
            ...     print(f"{module.module_path}: FAN-IN={module.fan_in}")
        """
        return [
            node
            for node in self.get_internal_nodes()
            if node.fan_in >= fan_in_threshold
        ]

    def get_highly_coupled_modules(
        self, fan_out_threshold: int = 10
    ) -> List[GraphNode]:
        """Find modules with excessive outgoing dependencies.

        Args:
            fan_out_threshold: Minimum FAN-OUT to classify as highly coupled.

        Returns:
            List of GraphNodes exceeding the FAN-OUT threshold.

        Example:
            >>> coupled = graph.get_highly_coupled_modules(fan_out_threshold=10)
            >>> for module in coupled:
            ...     print(f"{module.module_path}: FAN-OUT={module.fan_out}")
        """
        return [
            node
            for node in self.get_internal_nodes()
            if node.fan_out >= fan_out_threshold
        ]

    def to_dict(self) -> Dict:
        """Export graph to dictionary format.

        Returns:
            Dictionary representation of the graph suitable for
            JSON serialization or storage.
        """
        return {
            "nodes": {
                path: {
                    "dependencies": list(node.dependencies),
                    "dependents": list(node.dependents),
                    "is_external": node.is_external,
                    "fan_in": node.fan_in,
                    "fan_out": node.fan_out,
                    "instability": node.instability,
                    "metadata": node.metadata,
                }
                for path, node in self._nodes.items()
            },
            "external_dependencies": list(self._external_dependencies),
        }

    def __len__(self) -> int:
        """Return the number of nodes in the graph."""
        return len(self._nodes)

    def __contains__(self, module_path: str) -> bool:
        """Check if a module exists in the graph."""
        return module_path in self._nodes


__all__ = [
    "DependencyGraph",
    "GraphNode",
]
