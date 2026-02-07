"""Base parser interface for code analysis.

This module defines the abstract base class for all language-specific
parsers. Parsers extract structural information from source files,
including imports, class definitions, and function signatures.

References:
    - TR.md Section 2.1: Parser Architecture
    - TR.md Section 6.1: Error Handling Patterns
    - FRS.md FR-9.1: Graceful Degradation
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


logger = logging.getLogger(__name__)


@dataclass
class ImportStatement:
    """Represents a single import or dependency statement.

    Attributes:
        module: The module or package being imported (e.g., "os", "./utils").
        name: Specific symbol imported (e.g., "path" in "from os import path").
            None for wildcard or whole-module imports.
        alias: Import alias (e.g., "pd" in "import pandas as pd").
        is_relative: True for relative imports (e.g., "../utils" in JS,
            "from .utils" in Python).
        line_number: Line number where the import appears.
    """

    module: str
    name: Optional[str] = None
    alias: Optional[str] = None
    is_relative: bool = False
    line_number: int = 0


@dataclass
class FunctionDefinition:
    """Represents a function or method definition.

    Attributes:
        name: Function or method name.
        parameters: List of parameter names.
        return_type: Return type annotation (if available).
        line_number: Starting line number of the function.
        end_line_number: Ending line number of the function.
        is_async: True if the function is async/awaitable.
        is_method: True if this is a class method.
        is_static: True if this is a static method.
        docstring: Function docstring or comment.
    """

    name: str
    parameters: List[str] = field(default_factory=list)
    return_type: Optional[str] = None
    line_number: int = 0
    end_line_number: int = 0
    is_async: bool = False
    is_method: bool = False
    is_static: bool = False
    docstring: str = ""


@dataclass
class ClassDefinition:
    """Represents a class definition.

    Attributes:
        name: Class name.
        base_classes: List of parent class names.
        methods: List of method definitions in the class.
        properties: List of property/field names.
        line_number: Starting line number of the class.
        end_line_number: Ending line number of the class.
        docstring: Class docstring or comment.
        is_abstract: True if the class is abstract.
    """

    name: str
    base_classes: List[str] = field(default_factory=list)
    methods: List[FunctionDefinition] = field(default_factory=list)
    properties: List[str] = field(default_factory=list)
    line_number: int = 0
    end_line_number: int = 0
    docstring: str = ""
    is_abstract: bool = False


@dataclass
class ParseResult:
    """Result of parsing a source file.

    Attributes:
        file_path: Path to the parsed file.
        imports: List of import statements found.
        classes: List of class definitions found.
        functions: List of top-level function definitions.
        metadata: Additional parser-specific metadata.
        parse_errors: List of non-fatal parse errors encountered.
    """

    file_path: str
    imports: List[ImportStatement] = field(default_factory=list)
    classes: List[ClassDefinition] = field(default_factory=list)
    functions: List[FunctionDefinition] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    parse_errors: List[str] = field(default_factory=list)


class ParserError(Exception):
    """Base exception for parser errors.

    Raised when parsing fails in a way that prevents any useful
    information from being extracted.
    """

    pass


class BaseParser(ABC):
    """Abstract base class for language-specific code parsers.

    Subclasses must implement the abstract methods to provide
    language-specific parsing logic. The base class provides
    common utilities for error handling and file reading.

    Example:
        >>> class PythonParser(BaseParser):
        ...     def parse_file(self, file_path: Path) -> ParseResult:
        ...         # Implementation using Python's ast module
        ...         pass
        ...
        ...     def extract_imports(self, content: str) -> List[ImportStatement]:
        ...         # Extract imports from Python code
        ...         pass
    """

    def __init__(self):
        """Initialize the parser with default configuration."""
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def parse_file(self, file_path: Path) -> Optional[ParseResult]:
        """Parse a source file and extract structural information.

        Args:
            file_path: Path to the source file to parse.

        Returns:
            ParseResult containing extracted information, or None if
            the file could not be parsed at all.

        Raises:
            ParserError: If a fatal parsing error occurs.
        """
        pass

    @abstractmethod
    def extract_imports(self, content: str) -> List[ImportStatement]:
        """Extract import statements from source code.

        Args:
            content: Source code content as a string.

        Returns:
            List of import statements found in the code.
        """
        pass

    def extract_classes(self, content: str) -> List[ClassDefinition]:
        """Extract class definitions from source code.

        Args:
            content: Source code content as a string.

        Returns:
            List of class definitions found in the code.

        Note:
            Default implementation returns empty list. Subclasses
            should override for languages that support classes.
        """
        return []

    def extract_functions(self, content: str) -> List[FunctionDefinition]:
        """Extract top-level function definitions from source code.

        Args:
            content: Source code content as a string.

        Returns:
            List of function definitions found in the code.

        Note:
            Default implementation returns empty list. Subclasses
            should override this method.
        """
        return []

    def parse_file_safely(self, file_path: Path) -> Optional[ParseResult]:
        """Parse a file with comprehensive error handling.

        Wraps parse_file with error handling to ensure graceful
        degradation. Logs warnings for parse errors but does not
        raise exceptions.

        Args:
            file_path: Path to the source file to parse.

        Returns:
            ParseResult if parsing succeeded, None if parsing failed.
        """
        try:
            return self.parse_file(file_path)
        except UnicodeDecodeError as e:
            self.logger.warning(
                f"Failed to decode {file_path}: {e}. Skipping file."
            )
            return None
        except SyntaxError as e:
            self.logger.warning(
                f"Syntax error in {file_path}: {e}. Skipping file."
            )
            return None
        except ParserError as e:
            self.logger.warning(
                f"Parser error in {file_path}: {e}. Skipping file."
            )
            return None
        except Exception as e:
            self.logger.error(
                f"Unexpected error parsing {file_path}: {e}",
                exc_info=True,
            )
            return None

    def read_file_content(self, file_path: Path) -> str:
        """Read file content with encoding detection.

        Attempts to read the file with UTF-8 encoding, falling back
        to latin-1 if UTF-8 fails.

        Args:
            file_path: Path to the file to read.

        Returns:
            File content as a string.

        Raises:
            UnicodeDecodeError: If the file cannot be decoded with
                either UTF-8 or latin-1.
            IOError: If the file cannot be read.
        """
        try:
            return file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            self.logger.debug(
                f"UTF-8 decode failed for {file_path}, trying latin-1"
            )
            return file_path.read_text(encoding="latin-1")

    def is_parseable(self, file_path: Path) -> bool:
        """Check if a file can be parsed by this parser.

        Args:
            file_path: Path to check.

        Returns:
            True if this parser can handle the file.

        Note:
            Default implementation checks file extension against
            get_supported_extensions(). Subclasses can override
            for more sophisticated detection.
        """
        extensions = self.get_supported_extensions()
        return file_path.suffix in extensions

    @abstractmethod
    def get_supported_extensions(self) -> List[str]:
        """Get file extensions supported by this parser.

        Returns:
            List of file extensions including the dot (e.g., [".py", ".pyw"]).
        """
        pass

    def normalize_import_path(
        self, import_path: str, current_file: Path
    ) -> str:
        """Normalize an import path to a canonical form.

        Args:
            import_path: Raw import path from the source code.
            current_file: Path of the file containing the import.

        Returns:
            Normalized import path suitable for dependency graph.

        Note:
            Default implementation returns the import path unchanged.
            Subclasses should override to handle language-specific
            resolution (e.g., relative imports, path aliases).
        """
        return import_path
