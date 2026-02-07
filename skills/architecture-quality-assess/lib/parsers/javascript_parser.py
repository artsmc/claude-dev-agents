"""JavaScript/TypeScript code parser using regex-based analysis.

This module provides a parser for JavaScript and TypeScript files using
regex patterns. While not as complete as an AST-based parser, it provides
sufficient information for dependency analysis and architectural assessment.

References:
    - TR.md Section 2.1: Parser Architecture
    - TR.md Section 6.1: Error Handling Patterns
    - FRS.md FR-9.1: Graceful Degradation
"""

import logging
import re
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


class JavaScriptParser(BaseParser):
    """Parser for JavaScript and TypeScript source files.

    Uses regex-based parsing to extract imports, classes, and functions.
    Handles both JavaScript and TypeScript syntax, including JSX/TSX.
    While not as accurate as a full AST parser, it provides sufficient
    information for architectural analysis.

    Example:
        >>> parser = JavaScriptParser()
        >>> result = parser.parse_file(Path("example.ts"))
        >>> print(f"Found {len(result.imports)} imports")
        >>> print(f"Found {len(result.classes)} classes")
    """

    # Regex patterns for parsing
    IMPORT_ES6_PATTERN = re.compile(
        r"^\s*import\s+"
        r"(?:"
        r"(?P<default>\w+)|"  # default import
        r"\*\s+as\s+(?P<namespace>\w+)|"  # namespace import
        r"\{(?P<named>[^}]+)\}|"  # named imports
        r"(?P<default2>\w+)\s*,\s*\{(?P<named2>[^}]+)\}"  # default + named
        r")"
        r"\s+from\s+['\"](?P<module>[^'\"]+)['\"]",
        re.MULTILINE,
    )

    IMPORT_REQUIRE_PATTERN = re.compile(
        r"^\s*(?:const|let|var)\s+"
        r"(?:\{(?P<named>[^}]+)\}|(?P<default>\w+))"
        r"\s*=\s*require\s*\(['\"](?P<module>[^'\"]+)['\"]\)",
        re.MULTILINE,
    )

    DYNAMIC_IMPORT_PATTERN = re.compile(
        r"import\s*\(['\"](?P<module>[^'\"]+)['\"]\)", re.MULTILINE
    )

    CLASS_PATTERN = re.compile(
        r"^\s*(?:export\s+)?(?:default\s+)?class\s+"
        r"(?P<name>\w+)"
        r"(?:\s+extends\s+(?P<extends>\w+))?"
        r"\s*\{",
        re.MULTILINE,
    )

    FUNCTION_PATTERN = re.compile(
        r"^\s*(?:export\s+)?(?:async\s+)?function\s+"
        r"(?P<name>\w+)"
        r"\s*\((?P<params>[^)]*)\)",
        re.MULTILINE,
    )

    ARROW_FUNCTION_PATTERN = re.compile(
        r"^\s*(?:export\s+)?(?:const|let|var)\s+"
        r"(?P<name>\w+)"
        r"\s*=\s*(?:async\s+)?\((?P<params>[^)]*)\)\s*=>",
        re.MULTILINE,
    )

    METHOD_PATTERN = re.compile(
        r"^\s*(?:async\s+)?(?P<name>\w+)"
        r"\s*\((?P<params>[^)]*)\)"
        r"\s*(?::\s*[^{]+)?\s*\{",
        re.MULTILINE,
    )

    def get_supported_extensions(self) -> List[str]:
        """Get file extensions supported by this parser.

        Returns:
            List of JavaScript/TypeScript file extensions.
        """
        return [".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs"]

    def parse_file(self, file_path: Path) -> Optional[ParseResult]:
        """Parse a JavaScript/TypeScript source file.

        Args:
            file_path: Path to the file to parse.

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

        # Remove comments to simplify parsing
        content_without_comments = self._remove_comments(content)

        # Extract information
        imports = self.extract_imports(content_without_comments)
        classes = self.extract_classes(content_without_comments)
        functions = self.extract_functions(content_without_comments)

        return ParseResult(
            file_path=str(file_path),
            imports=imports,
            classes=classes,
            functions=functions,
            metadata={
                "lines_of_code": len(content.splitlines()),
                "is_typescript": file_path.suffix in [".ts", ".tsx"],
                "is_jsx": file_path.suffix in [".jsx", ".tsx"],
            },
        )

    def extract_imports(self, content: str) -> List[ImportStatement]:
        """Extract import statements from JavaScript/TypeScript code.

        Supports:
            - ES6 imports: import X from 'module'
            - ES6 named imports: import { X, Y } from 'module'
            - ES6 namespace imports: import * as X from 'module'
            - CommonJS: const X = require('module')
            - Dynamic imports: import('module')

        Args:
            content: Source code as a string.

        Returns:
            List of import statements found in the code.
        """
        imports = []

        # Extract ES6 imports
        for match in self.IMPORT_ES6_PATTERN.finditer(content):
            module = match.group("module")
            is_relative = module.startswith(".") or module.startswith("/")
            line_number = content[: match.start()].count("\n") + 1

            # Default import
            default_import = match.group("default") or match.group("default2")
            if default_import:
                imports.append(
                    ImportStatement(
                        module=module,
                        name="default",
                        alias=default_import,
                        is_relative=is_relative,
                        line_number=line_number,
                    )
                )

            # Namespace import
            namespace = match.group("namespace")
            if namespace:
                imports.append(
                    ImportStatement(
                        module=module,
                        name="*",
                        alias=namespace,
                        is_relative=is_relative,
                        line_number=line_number,
                    )
                )

            # Named imports
            named = match.group("named") or match.group("named2")
            if named:
                for name_part in named.split(","):
                    name_part = name_part.strip()
                    if not name_part:
                        continue

                    # Handle "name as alias"
                    if " as " in name_part:
                        name, alias = name_part.split(" as ", 1)
                        name = name.strip()
                        alias = alias.strip()
                    else:
                        name = name_part
                        alias = None

                    imports.append(
                        ImportStatement(
                            module=module,
                            name=name,
                            alias=alias,
                            is_relative=is_relative,
                            line_number=line_number,
                        )
                    )

        # Extract CommonJS requires
        for match in self.IMPORT_REQUIRE_PATTERN.finditer(content):
            module = match.group("module")
            is_relative = module.startswith(".") or module.startswith("/")
            line_number = content[: match.start()].count("\n") + 1

            default_import = match.group("default")
            if default_import:
                imports.append(
                    ImportStatement(
                        module=module,
                        name="default",
                        alias=default_import,
                        is_relative=is_relative,
                        line_number=line_number,
                    )
                )

            named = match.group("named")
            if named:
                for name_part in named.split(","):
                    name = name_part.strip()
                    if name:
                        imports.append(
                            ImportStatement(
                                module=module,
                                name=name,
                                alias=None,
                                is_relative=is_relative,
                                line_number=line_number,
                            )
                        )

        # Extract dynamic imports
        for match in self.DYNAMIC_IMPORT_PATTERN.finditer(content):
            module = match.group("module")
            is_relative = module.startswith(".") or module.startswith("/")
            line_number = content[: match.start()].count("\n") + 1

            imports.append(
                ImportStatement(
                    module=module,
                    name="*",
                    alias=None,
                    is_relative=is_relative,
                    line_number=line_number,
                )
            )

        return imports

    def extract_classes(self, content: str) -> List[ClassDefinition]:
        """Extract class definitions from JavaScript/TypeScript code.

        Args:
            content: Source code as a string.

        Returns:
            List of class definitions found in the code.
        """
        classes = []

        for match in self.CLASS_PATTERN.finditer(content):
            name = match.group("name")
            extends = match.group("extends")
            base_classes = [extends] if extends else []
            line_number = content[: match.start()].count("\n") + 1

            # Try to find methods within the class
            # This is a simplified approach - we look for patterns after the class declaration
            class_start = match.end()
            brace_count = 1
            class_end = class_start

            # Find the end of the class by counting braces
            for i in range(class_start, len(content)):
                if content[i] == "{":
                    brace_count += 1
                elif content[i] == "}":
                    brace_count -= 1
                    if brace_count == 0:
                        class_end = i
                        break

            class_body = content[class_start:class_end]
            methods = self._extract_methods_from_class(class_body, line_number)

            end_line_number = content[:class_end].count("\n") + 1

            classes.append(
                ClassDefinition(
                    name=name,
                    base_classes=base_classes,
                    methods=methods,
                    properties=[],  # Property extraction is complex in JS/TS
                    line_number=line_number,
                    end_line_number=end_line_number,
                    docstring="",
                    is_abstract=False,
                )
            )

        return classes

    def extract_functions(self, content: str) -> List[FunctionDefinition]:
        """Extract top-level function definitions from JavaScript/TypeScript code.

        Args:
            content: Source code as a string.

        Returns:
            List of function definitions found at the top level.
        """
        functions = []

        # Extract regular function declarations
        for match in self.FUNCTION_PATTERN.finditer(content):
            name = match.group("name")
            params_str = match.group("params")
            parameters = self._parse_parameters(params_str)
            line_number = content[: match.start()].count("\n") + 1

            functions.append(
                FunctionDefinition(
                    name=name,
                    parameters=parameters,
                    return_type=None,
                    line_number=line_number,
                    end_line_number=line_number,  # End line is hard to determine
                    is_async="async" in content[
                        max(0, match.start() - 20) : match.start()
                    ],
                    is_method=False,
                    is_static=False,
                    docstring="",
                )
            )

        # Extract arrow functions
        for match in self.ARROW_FUNCTION_PATTERN.finditer(content):
            name = match.group("name")
            params_str = match.group("params")
            parameters = self._parse_parameters(params_str)
            line_number = content[: match.start()].count("\n") + 1

            functions.append(
                FunctionDefinition(
                    name=name,
                    parameters=parameters,
                    return_type=None,
                    line_number=line_number,
                    end_line_number=line_number,
                    is_async="async" in match.group(0),
                    is_method=False,
                    is_static=False,
                    docstring="",
                )
            )

        return functions

    def _extract_methods_from_class(
        self, class_body: str, class_line_number: int
    ) -> List[FunctionDefinition]:
        """Extract methods from a class body.

        Args:
            class_body: String content of the class body.
            class_line_number: Starting line number of the class.

        Returns:
            List of method definitions.
        """
        methods = []

        for match in self.METHOD_PATTERN.finditer(class_body):
            name = match.group("name")

            # Skip constructor and common non-methods
            if name in ["if", "for", "while", "switch", "catch"]:
                continue

            params_str = match.group("params")
            parameters = self._parse_parameters(params_str)
            line_number = class_line_number + class_body[: match.start()].count("\n")

            methods.append(
                FunctionDefinition(
                    name=name,
                    parameters=parameters,
                    return_type=None,
                    line_number=line_number,
                    end_line_number=line_number,
                    is_async="async" in class_body[
                        max(0, match.start() - 20) : match.start()
                    ],
                    is_method=True,
                    is_static="static" in class_body[
                        max(0, match.start() - 30) : match.start()
                    ],
                    docstring="",
                )
            )

        return methods

    def _parse_parameters(self, params_str: str) -> List[str]:
        """Parse parameter string into list of parameter names.

        Args:
            params_str: String containing function parameters.

        Returns:
            List of parameter names.
        """
        if not params_str or not params_str.strip():
            return []

        parameters = []
        for param in params_str.split(","):
            param = param.strip()
            if not param:
                continue

            # Remove type annotations (TypeScript)
            if ":" in param:
                param = param.split(":")[0].strip()

            # Remove default values
            if "=" in param:
                param = param.split("=")[0].strip()

            # Handle destructuring (simplified)
            if param.startswith("{") or param.startswith("["):
                param = param.strip("{}[]")

            # Handle rest parameters
            if param.startswith("..."):
                param = param[3:]

            if param:
                parameters.append(param)

        return parameters

    def _remove_comments(self, content: str) -> str:
        """Remove single-line and multi-line comments from code.

        Args:
            content: Source code with comments.

        Returns:
            Source code with comments removed.

        Note:
            This is a simplified implementation that may not handle
            all edge cases (e.g., comments within strings).
        """
        # Remove single-line comments
        content = re.sub(r"//.*?$", "", content, flags=re.MULTILINE)

        # Remove multi-line comments
        content = re.sub(r"/\*.*?\*/", "", content, flags=re.DOTALL)

        return content

    def normalize_import_path(
        self, import_path: str, current_file: Path
    ) -> str:
        """Normalize a JavaScript/TypeScript import path.

        Handles:
            - Relative imports (./module, ../module)
            - Absolute imports from node_modules
            - Path aliases (would need project configuration)

        Args:
            import_path: Raw import path from the source code.
            current_file: Path of the file containing the import.

        Returns:
            Normalized import path suitable for dependency graph.

        Note:
            This is a simplified implementation. A production version
            would need to resolve path aliases from tsconfig.json or
            webpack configuration.
        """
        if not import_path.startswith("."):
            # Absolute import (from node_modules or alias)
            return import_path

        # Resolve relative import
        current_dir = current_file.parent
        resolved_path = (current_dir / import_path).resolve()

        # Try to make it relative to project root
        # For now, just return the import path as-is
        return import_path
