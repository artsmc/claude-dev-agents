"""Python code parser using AST analysis.

This module provides a parser for Python source files using the built-in
ast module. It extracts imports, class definitions, function definitions,
and handles syntax errors gracefully.

References:
    - TR.md Section 2.2.2: Python Parser Implementation
    - TR.md Section 6.1: Error Handling Patterns
    - FRS.md FR-9.1: Graceful Degradation
"""

import ast
import logging
from pathlib import Path
from typing import List, Optional

from .base import (
    BaseParser,
    ClassDefinition,
    FunctionDefinition,
    ImportStatement,
    ParseResult,
    ParserError,
)


logger = logging.getLogger(__name__)


class PythonParser(BaseParser):
    """Parser for Python source files using AST analysis.

    Uses Python's built-in ast module to parse Python code and extract
    structural information including imports, classes, and functions.
    Handles syntax errors gracefully by logging warnings and returning
    partial results when possible.

    Example:
        >>> parser = PythonParser()
        >>> result = parser.parse_file(Path("example.py"))
        >>> print(f"Found {len(result.imports)} imports")
        >>> print(f"Found {len(result.classes)} classes")
    """

    def get_supported_extensions(self) -> List[str]:
        """Get file extensions supported by this parser.

        Returns:
            List of Python file extensions.
        """
        return [".py", ".pyw"]

    def parse_file(self, file_path: Path) -> Optional[ParseResult]:
        """Parse a Python source file and extract structural information.

        Args:
            file_path: Path to the Python file to parse.

        Returns:
            ParseResult containing extracted information, or None if
            the file could not be parsed.

        Raises:
            ParserError: If a fatal parsing error occurs.
        """
        if not file_path.exists():
            raise ParserError(f"File not found: {file_path}")

        if not self.is_parseable(file_path):
            raise ParserError(f"File extension not supported: {file_path.suffix}")

        try:
            content = self.read_file_content(file_path)
        except (IOError, UnicodeDecodeError) as e:
            raise ParserError(f"Failed to read file: {e}")

        try:
            tree = ast.parse(content, filename=str(file_path))
        except SyntaxError as e:
            # Syntax error - log and return None
            self.logger.warning(
                f"Syntax error in {file_path} at line {e.lineno}: {e.msg}"
            )
            raise ParserError(f"Syntax error: {e.msg} at line {e.lineno}")

        # Extract information from AST
        imports = self._extract_imports_from_ast(tree)
        classes = self._extract_classes_from_ast(tree)
        functions = self._extract_functions_from_ast(tree)

        return ParseResult(
            file_path=str(file_path),
            imports=imports,
            classes=classes,
            functions=functions,
            metadata={
                "lines_of_code": len(content.splitlines()),
                "ast_node_count": sum(1 for _ in ast.walk(tree)),
            },
        )

    def extract_imports(self, content: str) -> List[ImportStatement]:
        """Extract import statements from Python source code.

        Args:
            content: Python source code as a string.

        Returns:
            List of import statements found in the code.
        """
        try:
            tree = ast.parse(content)
            return self._extract_imports_from_ast(tree)
        except SyntaxError as e:
            self.logger.warning(f"Syntax error while extracting imports: {e}")
            return []

    def extract_classes(self, content: str) -> List[ClassDefinition]:
        """Extract class definitions from Python source code.

        Args:
            content: Python source code as a string.

        Returns:
            List of class definitions found in the code.
        """
        try:
            tree = ast.parse(content)
            return self._extract_classes_from_ast(tree)
        except SyntaxError as e:
            self.logger.warning(f"Syntax error while extracting classes: {e}")
            return []

    def extract_functions(self, content: str) -> List[FunctionDefinition]:
        """Extract top-level function definitions from Python source code.

        Args:
            content: Python source code as a string.

        Returns:
            List of function definitions found at the top level.
        """
        try:
            tree = ast.parse(content)
            return self._extract_functions_from_ast(tree)
        except SyntaxError as e:
            self.logger.warning(f"Syntax error while extracting functions: {e}")
            return []

    def _extract_imports_from_ast(self, tree: ast.AST) -> List[ImportStatement]:
        """Extract imports from an AST tree.

        Args:
            tree: Parsed AST tree.

        Returns:
            List of ImportStatement objects.
        """
        imports = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                # Handle: import module [as alias]
                for alias in node.names:
                    imports.append(
                        ImportStatement(
                            module=alias.name,
                            name=None,
                            alias=alias.asname,
                            is_relative=False,
                            line_number=node.lineno,
                        )
                    )

            elif isinstance(node, ast.ImportFrom):
                # Handle: from module import name [as alias]
                module = node.module or ""
                is_relative = node.level > 0

                # Handle relative imports
                if is_relative:
                    module = "." * node.level + module

                for alias in node.names:
                    imports.append(
                        ImportStatement(
                            module=module,
                            name=alias.name,
                            alias=alias.asname,
                            is_relative=is_relative,
                            line_number=node.lineno,
                        )
                    )

        return imports

    def _extract_classes_from_ast(self, tree: ast.AST) -> List[ClassDefinition]:
        """Extract class definitions from an AST tree.

        Args:
            tree: Parsed AST tree.

        Returns:
            List of ClassDefinition objects.
        """
        classes = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Extract base classes
                base_classes = []
                for base in node.bases:
                    if isinstance(base, ast.Name):
                        base_classes.append(base.id)
                    elif isinstance(base, ast.Attribute):
                        # Handle qualified names like abc.ABC
                        base_classes.append(ast.unparse(base))

                # Extract methods
                methods = []
                properties = []

                for item in node.body:
                    if isinstance(item, ast.FunctionDef) or isinstance(
                        item, ast.AsyncFunctionDef
                    ):
                        methods.append(
                            self._extract_function_def(item, is_method=True)
                        )
                    elif isinstance(item, ast.AnnAssign) and isinstance(
                        item.target, ast.Name
                    ):
                        # Class property with type annotation
                        properties.append(item.target.id)
                    elif isinstance(item, ast.Assign):
                        # Class property
                        for target in item.targets:
                            if isinstance(target, ast.Name):
                                properties.append(target.id)

                # Get docstring
                docstring = ast.get_docstring(node) or ""

                # Check if abstract
                is_abstract = any(
                    isinstance(decorator, ast.Name)
                    and decorator.id == "abstractmethod"
                    for decorator in node.decorator_list
                )

                classes.append(
                    ClassDefinition(
                        name=node.name,
                        base_classes=base_classes,
                        methods=methods,
                        properties=properties,
                        line_number=node.lineno,
                        end_line_number=node.end_lineno or node.lineno,
                        docstring=docstring,
                        is_abstract=is_abstract,
                    )
                )

        return classes

    def _extract_functions_from_ast(
        self, tree: ast.AST, top_level_only: bool = True
    ) -> List[FunctionDefinition]:
        """Extract function definitions from an AST tree.

        Args:
            tree: Parsed AST tree.
            top_level_only: If True, only extract top-level functions.

        Returns:
            List of FunctionDefinition objects.
        """
        functions = []

        if top_level_only:
            # Only process direct children of module
            if isinstance(tree, ast.Module):
                for node in tree.body:
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        functions.append(self._extract_function_def(node))
        else:
            # Extract all functions
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    functions.append(self._extract_function_def(node))

        return functions

    def _extract_function_def(
        self, node: ast.FunctionDef | ast.AsyncFunctionDef, is_method: bool = False
    ) -> FunctionDefinition:
        """Extract function definition from an AST node.

        Args:
            node: AST FunctionDef or AsyncFunctionDef node.
            is_method: True if this is a class method.

        Returns:
            FunctionDefinition object.
        """
        # Extract parameters
        parameters = []
        for arg in node.args.args:
            parameters.append(arg.arg)

        # Extract return type annotation
        return_type = None
        if node.returns:
            try:
                return_type = ast.unparse(node.returns)
            except Exception:
                return_type = None

        # Get docstring
        docstring = ast.get_docstring(node) or ""

        # Check if static method
        is_static = any(
            isinstance(decorator, ast.Name) and decorator.id == "staticmethod"
            for decorator in node.decorator_list
        )

        # Check if async
        is_async = isinstance(node, ast.AsyncFunctionDef)

        return FunctionDefinition(
            name=node.name,
            parameters=parameters,
            return_type=return_type,
            line_number=node.lineno,
            end_line_number=node.end_lineno or node.lineno,
            is_async=is_async,
            is_method=is_method,
            is_static=is_static,
            docstring=docstring,
        )

    def normalize_import_path(
        self, import_path: str, current_file: Path
    ) -> str:
        """Normalize a Python import path to a canonical form.

        Converts relative imports to absolute imports based on the
        project structure.

        Args:
            import_path: Raw import path from the source code.
            current_file: Path of the file containing the import.

        Returns:
            Normalized import path suitable for dependency graph.

        Note:
            This is a simplified implementation. A production version
            would need to resolve package names and handle complex
            project structures.
        """
        if not import_path.startswith("."):
            # Already absolute
            return import_path

        # Count leading dots
        level = len(import_path) - len(import_path.lstrip("."))
        module = import_path[level:]

        # Try to resolve relative to current file
        current_dir = current_file.parent
        for _ in range(level - 1):
            current_dir = current_dir.parent

        if module:
            return f"{current_dir.name}.{module}"
        else:
            return current_dir.name
