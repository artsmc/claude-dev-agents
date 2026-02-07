"""Dependency graph utilities for architecture analysis.

This module provides graph-based analysis tools for understanding
module relationships, coupling metrics, and dependency patterns.

References:
    - TR.md Section 2.2.2: Dependency Graph Construction
    - FRS.md FR-5.x: Coupling and Dependency Analysis
"""

from .dependency_graph import DependencyGraph, GraphNode


__all__ = [
    "DependencyGraph",
    "GraphNode",
]
