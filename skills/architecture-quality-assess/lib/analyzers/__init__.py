"""Analyzer registry and factory for architecture quality assessment.

This module provides a registry system for architecture analyzers
and utilities for running multiple analyzers in sequence. Analyzers
are lazily loaded to avoid import overhead.

References:
    - TR.md Section 2.1: Analyzer Architecture
    - TR.md Section 4.1: Main Orchestrator Design
"""

import logging
from typing import Dict, List, Optional, Type

from .base import AnalysisContext, AnalyzerError, BaseAnalyzer


logger = logging.getLogger(__name__)


# Registry mapping analyzer names to analyzer classes
_ANALYZER_REGISTRY: Dict[str, Type[BaseAnalyzer]] = {}
_ANALYZER_INSTANCES: Dict[str, BaseAnalyzer] = {}


def register_analyzer(analyzer_class: Type[BaseAnalyzer]) -> None:
    """Register an analyzer class.

    Args:
        analyzer_class: Analyzer class to register.

    Example:
        >>> register_analyzer(CouplingAnalyzer)
    """
    # Instantiate temporarily to get name
    temp_instance = analyzer_class()
    name = temp_instance.get_name()

    _ANALYZER_REGISTRY[name] = analyzer_class
    logger.debug(f"Registered {analyzer_class.__name__} as '{name}'")


def get_analyzer(name: str) -> Optional[BaseAnalyzer]:
    """Get an analyzer instance by name.

    Analyzers are instantiated once and cached for reuse.

    Args:
        name: Analyzer name (e.g., "coupling", "layer", "solid").

    Returns:
        Analyzer instance, or None if not registered.

    Example:
        >>> analyzer = get_analyzer("coupling")
        >>> if analyzer:
        ...     violations = analyzer.analyze(context)
    """
    if name not in _ANALYZER_REGISTRY:
        logger.warning(f"Analyzer '{name}' not found in registry")
        return None

    # Return cached instance if available
    if name in _ANALYZER_INSTANCES:
        return _ANALYZER_INSTANCES[name]

    # Instantiate and cache the analyzer
    analyzer_class = _ANALYZER_REGISTRY[name]
    analyzer_instance = analyzer_class()
    _ANALYZER_INSTANCES[name] = analyzer_instance

    logger.debug(f"Instantiated {analyzer_class.__name__}")
    return analyzer_instance


def get_all_analyzers() -> List[BaseAnalyzer]:
    """Get all registered analyzer instances.

    Returns:
        List of all registered analyzers.
    """
    return [get_analyzer(name) for name in _ANALYZER_REGISTRY.keys()]


def get_enabled_analyzers(context: AnalysisContext) -> List[BaseAnalyzer]:
    """Get analyzers that are enabled in the configuration.

    Args:
        context: Analysis context with configuration.

    Returns:
        List of enabled analyzers.

    Example:
        >>> analyzers = get_enabled_analyzers(context)
        >>> for analyzer in analyzers:
        ...     violations = analyzer.analyze(context)
    """
    all_analyzers = get_all_analyzers()
    return [
        analyzer
        for analyzer in all_analyzers
        if analyzer.is_enabled(context.config)
    ]


def list_analyzer_names() -> List[str]:
    """Get names of all registered analyzers.

    Returns:
        List of analyzer names.
    """
    return list(_ANALYZER_REGISTRY.keys())


def list_analyzer_info() -> List[Dict[str, str]]:
    """Get information about all registered analyzers.

    Returns:
        List of dictionaries with name, class, and description.

    Example:
        >>> for info in list_analyzer_info():
        ...     print(f"{info['name']}: {info['description']}")
    """
    info_list = []
    for name, analyzer_class in _ANALYZER_REGISTRY.items():
        # Get or create instance
        analyzer = get_analyzer(name)
        if analyzer:
            info_list.append({
                "name": name,
                "class": analyzer_class.__name__,
                "description": analyzer.get_description(),
            })
    return info_list


def clear_registry() -> None:
    """Clear the analyzer registry and cached instances.

    Useful for testing or when dynamically reloading analyzers.
    """
    _ANALYZER_REGISTRY.clear()
    _ANALYZER_INSTANCES.clear()
    logger.debug("Analyzer registry cleared")


def run_all_analyzers(context: AnalysisContext) -> Dict[str, List]:
    """Run all enabled analyzers and collect results.

    Args:
        context: Analysis context.

    Returns:
        Dictionary mapping analyzer names to their violation lists.

    Example:
        >>> results = run_all_analyzers(context)
        >>> for analyzer_name, violations in results.items():
        ...     print(f"{analyzer_name}: {len(violations)} violations")
    """
    results = {}
    analyzers = get_enabled_analyzers(context)

    logger.info(f"Running {len(analyzers)} analyzers")

    for analyzer in analyzers:
        name = analyzer.get_name()
        logger.info(f"Running {name} analyzer...")

        try:
            violations = analyzer.analyze_safely(context)
            results[name] = violations
            logger.info(
                f"{name} analyzer completed: {len(violations)} violations"
            )
        except Exception as e:
            logger.error(
                f"Failed to run {name} analyzer: {e}",
                exc_info=True,
            )
            results[name] = []

    return results


def _register_builtin_analyzers() -> None:
    """Register built-in analyzers.

    Called automatically on module import. Attempts to import
    and register available analyzers.
    """
    # Try to register coupling analyzer
    try:
        from .coupling_analyzer import CouplingAnalyzer

        register_analyzer(CouplingAnalyzer)
    except ImportError:
        logger.debug("CouplingAnalyzer not available")

    # Try to register layer analyzer
    try:
        from .layer_analyzer import LayerAnalyzer

        register_analyzer(LayerAnalyzer)
    except ImportError:
        logger.debug("LayerAnalyzer not available")

    # Try to register SOLID analyzer
    try:
        from .solid_analyzer import SOLIDAnalyzer

        register_analyzer(SOLIDAnalyzer)
    except ImportError:
        logger.debug("SOLIDAnalyzer not available")

    # Try to register pattern analyzer
    try:
        from .pattern_analyzer import PatternAnalyzer

        register_analyzer(PatternAnalyzer)
    except ImportError:
        logger.debug("PatternAnalyzer not available")

    # Try to register drift analyzer
    try:
        from .drift_analyzer import DriftAnalyzer

        register_analyzer(DriftAnalyzer)
    except ImportError:
        logger.debug("DriftAnalyzer not available")


# Auto-register built-in analyzers on import
_register_builtin_analyzers()


__all__ = [
    "AnalysisContext",
    "AnalyzerError",
    "BaseAnalyzer",
    "clear_registry",
    "get_all_analyzers",
    "get_analyzer",
    "get_enabled_analyzers",
    "list_analyzer_info",
    "list_analyzer_names",
    "register_analyzer",
    "run_all_analyzers",
]
