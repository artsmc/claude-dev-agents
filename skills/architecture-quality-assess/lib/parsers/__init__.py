"""Parser registry and factory for code analysis.

This module provides a registry system for language-specific parsers
and a factory function to select the appropriate parser for a given
file. Parsers are lazily loaded to avoid import overhead.

References:
    - TR.md Section 2.1: Parser Architecture
    - TR.md Section 2.2.2: Parser Selection Strategy
"""

import logging
from pathlib import Path
from typing import Dict, Optional, Type

from .base import (
    BaseParser,
    ClassDefinition,
    FunctionDefinition,
    ImportStatement,
    ParseResult,
    ParserError,
)


logger = logging.getLogger(__name__)


# Registry mapping file extensions to parser class names
# Populated lazily as parsers are requested
_PARSER_REGISTRY: Dict[str, Type[BaseParser]] = {}
_PARSER_INSTANCES: Dict[str, BaseParser] = {}


def register_parser(
    parser_class: Type[BaseParser],
    extensions: Optional[list[str]] = None,
) -> None:
    """Register a parser class for specific file extensions.

    Args:
        parser_class: Parser class to register.
        extensions: List of file extensions (e.g., [".py", ".pyw"]).
            If None, uses parser_class.get_supported_extensions().
    """
    if extensions is None:
        # Instantiate temporarily to get extensions
        temp_instance = parser_class()
        extensions = temp_instance.get_supported_extensions()

    for ext in extensions:
        _PARSER_REGISTRY[ext] = parser_class
        logger.debug(f"Registered {parser_class.__name__} for {ext}")


def get_parser_for_file(file_path: Path) -> Optional[BaseParser]:
    """Get the appropriate parser for a file.

    Uses the file extension to select a parser from the registry.
    Parsers are instantiated once and cached for reuse.

    Args:
        file_path: Path to the file to parse.

    Returns:
        Parser instance capable of parsing the file, or None if
        no parser is registered for the file extension.

    Example:
        >>> parser = get_parser_for_file(Path("example.py"))
        >>> if parser:
        ...     result = parser.parse_file(Path("example.py"))
    """
    extension = file_path.suffix

    # Check if we have a parser registered for this extension
    if extension not in _PARSER_REGISTRY:
        return None

    # Return cached instance if available
    if extension in _PARSER_INSTANCES:
        return _PARSER_INSTANCES[extension]

    # Instantiate and cache the parser
    parser_class = _PARSER_REGISTRY[extension]
    parser_instance = parser_class()
    _PARSER_INSTANCES[extension] = parser_instance

    logger.debug(
        f"Instantiated {parser_class.__name__} for {extension} files"
    )
    return parser_instance


def get_parser_by_name(parser_name: str) -> Optional[BaseParser]:
    """Get a parser instance by its class name.

    Args:
        parser_name: Name of the parser class (e.g., "PythonParser").

    Returns:
        Parser instance, or None if not found.

    Example:
        >>> parser = get_parser_by_name("PythonParser")
    """
    for parser_class in _PARSER_REGISTRY.values():
        if parser_class.__name__ == parser_name:
            # Check if already instantiated
            for instance in _PARSER_INSTANCES.values():
                if isinstance(instance, parser_class):
                    return instance
            # Create new instance
            return parser_class()
    return None


def is_parseable(file_path: Path) -> bool:
    """Check if a file can be parsed by any registered parser.

    Args:
        file_path: Path to check.

    Returns:
        True if a parser is available for this file type.

    Example:
        >>> is_parseable(Path("example.py"))
        True
        >>> is_parseable(Path("image.png"))
        False
    """
    return file_path.suffix in _PARSER_REGISTRY


def get_supported_extensions() -> list[str]:
    """Get all file extensions supported by registered parsers.

    Returns:
        List of file extensions with dots (e.g., [".py", ".js", ".ts"]).
    """
    return list(_PARSER_REGISTRY.keys())


def clear_registry() -> None:
    """Clear the parser registry and cached instances.

    Useful for testing or when dynamically reloading parsers.
    """
    _PARSER_REGISTRY.clear()
    _PARSER_INSTANCES.clear()
    logger.debug("Parser registry cleared")


def _register_builtin_parsers() -> None:
    """Register built-in parsers.

    Called automatically on module import. Attempts to import
    and register Python and JavaScript parsers if available.
    """
    # Try to register Python parser
    try:
        from .python_parser import PythonParser

        register_parser(PythonParser)
    except ImportError:
        logger.debug("PythonParser not available")

    # Try to register JavaScript/TypeScript parser
    try:
        from .javascript_parser import JavaScriptParser

        register_parser(JavaScriptParser)
    except ImportError:
        logger.debug("JavaScriptParser not available")


# Auto-register built-in parsers on import
_register_builtin_parsers()


__all__ = [
    "BaseParser",
    "ClassDefinition",
    "FunctionDefinition",
    "ImportStatement",
    "ParseResult",
    "ParserError",
    "clear_registry",
    "get_parser_by_name",
    "get_parser_for_file",
    "get_supported_extensions",
    "is_parseable",
    "register_parser",
]
