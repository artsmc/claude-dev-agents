"""Unit tests for Python parser.

Tests the Python AST-based parser for import extraction, class detection,
function detection, and error handling.

Run with: python -m pytest tests/test_python_parser.py -v
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from lib.parsers.python_parser import PythonParser
from lib.parsers.base import ParserError


class TestPythonParser:
    """Test suite for PythonParser."""

    @pytest.fixture
    def parser(self):
        """Create a PythonParser instance."""
        return PythonParser()

    @pytest.fixture
    def fixtures_dir(self):
        """Get fixtures directory path."""
        return Path(__file__).parent / "fixtures"

    def test_supported_extensions(self, parser):
        """Test that supported extensions are correct."""
        extensions = parser.get_supported_extensions()
        assert ".py" in extensions
        assert ".pyw" in extensions

    def test_extract_imports_simple(self, parser):
        """Test extraction of simple imports."""
        code = """
import os
import sys
from pathlib import Path
from typing import List, Dict
"""
        imports = parser.extract_imports(code)

        assert len(imports) >= 4

        # Check for specific imports
        import_modules = [imp.module for imp in imports]
        assert "os" in import_modules
        assert "sys" in import_modules
        assert "pathlib" in import_modules
        assert "typing" in import_modules

    def test_extract_imports_with_aliases(self, parser):
        """Test extraction of imports with aliases."""
        code = """
import numpy as np
import pandas as pd
from datetime import datetime as dt
"""
        imports = parser.extract_imports(code)

        # Find numpy import
        numpy_import = next(imp for imp in imports if imp.module == "numpy")
        assert numpy_import.alias == "np"

        # Find pandas import
        pandas_import = next(imp for imp in imports if imp.module == "pandas")
        assert pandas_import.alias == "pd"

        # Find datetime import
        dt_import = next(imp for imp in imports if imp.module == "datetime" and imp.name == "datetime")
        assert dt_import.alias == "dt"

    def test_extract_relative_imports(self, parser):
        """Test extraction of relative imports."""
        code = """
from . import utils
from .. import config
from ...package import module
"""
        imports = parser.extract_imports(code)

        assert len(imports) == 3
        assert all(imp.is_relative for imp in imports)

    def test_extract_classes_simple(self, parser):
        """Test extraction of simple class definitions."""
        code = """
class MyClass:
    def __init__(self):
        self.value = 0

    def method(self):
        pass
"""
        classes = parser.extract_classes(code)

        assert len(classes) == 1
        assert classes[0].name == "MyClass"
        assert len(classes[0].methods) == 2
        assert classes[0].methods[0].name == "__init__"
        assert classes[0].methods[1].name == "method"

    def test_extract_classes_with_inheritance(self, parser):
        """Test extraction of classes with base classes."""
        code = """
class Base:
    pass

class Child(Base):
    pass

class MultiChild(Base, object):
    pass
"""
        classes = parser.extract_classes(code)

        assert len(classes) == 3

        child_class = next(c for c in classes if c.name == "Child")
        assert "Base" in child_class.base_classes

        multi_class = next(c for c in classes if c.name == "MultiChild")
        assert "Base" in multi_class.base_classes

    def test_extract_classes_with_docstring(self, parser):
        """Test extraction of class docstrings."""
        code = '''
class MyClass:
    """This is a docstring."""

    def method(self):
        """Method docstring."""
        pass
'''
        classes = parser.extract_classes(code)

        assert len(classes) == 1
        assert classes[0].docstring == "This is a docstring."
        assert classes[0].methods[0].docstring == "Method docstring."

    def test_extract_functions_simple(self, parser):
        """Test extraction of top-level functions."""
        code = """
def function1():
    pass

def function2(a, b):
    return a + b

async def async_function():
    pass
"""
        functions = parser.extract_functions(code)

        assert len(functions) == 3
        assert functions[0].name == "function1"
        assert functions[1].name == "function2"
        assert len(functions[1].parameters) == 2
        assert functions[2].name == "async_function"
        assert functions[2].is_async is True

    def test_extract_functions_with_type_hints(self, parser):
        """Test extraction of functions with type hints."""
        code = """
def typed_function(a: int, b: str) -> bool:
    return True
"""
        functions = parser.extract_functions(code)

        assert len(functions) == 1
        assert functions[0].name == "typed_function"
        assert functions[0].return_type == "bool"
        assert "a" in functions[0].parameters
        assert "b" in functions[0].parameters

    def test_parse_file_success(self, parser, tmp_path):
        """Test successful parsing of a valid Python file."""
        # Create a test file
        test_file = tmp_path / "test.py"
        test_file.write_text("""
import os
from typing import List

class TestClass:
    def method(self):
        pass

def test_function():
    pass
""")

        result = parser.parse_file(test_file)

        assert result is not None
        assert result.file_path == str(test_file)
        assert len(result.imports) >= 2
        assert len(result.classes) == 1
        assert len(result.functions) == 1
        assert result.metadata["lines_of_code"] > 0

    def test_parse_file_syntax_error(self, parser, tmp_path):
        """Test parsing of file with syntax error."""
        # Create a file with syntax error
        test_file = tmp_path / "bad.py"
        test_file.write_text("def incomplete_function(")

        with pytest.raises(ParserError):
            parser.parse_file(test_file)

    def test_parse_file_safely_syntax_error(self, parser, tmp_path):
        """Test safe parsing of file with syntax error."""
        # Create a file with syntax error
        test_file = tmp_path / "bad.py"
        test_file.write_text("def incomplete_function(")

        result = parser.parse_file_safely(test_file)
        assert result is None

    def test_parse_file_nonexistent(self, parser):
        """Test parsing of nonexistent file."""
        with pytest.raises(ParserError):
            parser.parse_file(Path("/nonexistent/file.py"))

    def test_parse_fixture_fastapi(self, parser, fixtures_dir):
        """Test parsing of FastAPI fixture files."""
        fastapi_dir = fixtures_dir / "python-fastapi" / "app"
        if not fastapi_dir.exists():
            pytest.skip("FastAPI fixture not found")

        # Parse main.py
        main_file = fastapi_dir / "main.py"
        result = parser.parse_file(main_file)

        assert result is not None
        assert len(result.imports) > 0

        # Check for FastAPI import
        import_modules = [imp.module for imp in result.imports]
        assert "fastapi" in import_modules

    def test_parse_fixture_django(self, parser, fixtures_dir):
        """Test parsing of Django fixture files."""
        django_dir = fixtures_dir / "django-app" / "users"
        if not django_dir.exists():
            pytest.skip("Django fixture not found")

        # Parse models.py
        models_file = django_dir / "models.py"
        result = parser.parse_file(models_file)

        assert result is not None
        assert len(result.classes) > 0

        # Check for User class
        class_names = [cls.name for cls in result.classes]
        assert "User" in class_names

    def test_is_parseable(self, parser):
        """Test file parseability check."""
        assert parser.is_parseable(Path("test.py")) is True
        assert parser.is_parseable(Path("test.pyw")) is True
        assert parser.is_parseable(Path("test.js")) is False
        assert parser.is_parseable(Path("test.txt")) is False

    def test_extract_classes_with_properties(self, parser):
        """Test extraction of class properties."""
        code = """
class MyClass:
    class_var = 10

    def __init__(self):
        self.instance_var = 20

    name: str
    age: int = 30
"""
        classes = parser.extract_classes(code)

        assert len(classes) == 1
        # Should find annotated properties
        assert len(classes[0].properties) >= 1

    def test_extract_static_methods(self, parser):
        """Test extraction of static methods."""
        code = """
class MyClass:
    @staticmethod
    def static_method():
        pass

    def normal_method(self):
        pass
"""
        classes = parser.extract_classes(code)

        assert len(classes) == 1
        assert len(classes[0].methods) == 2

        static = next(m for m in classes[0].methods if m.name == "static_method")
        assert static.is_static is True

        normal = next(m for m in classes[0].methods if m.name == "normal_method")
        assert normal.is_static is False

    def test_line_numbers(self, parser):
        """Test that line numbers are captured correctly."""
        code = """import os

class MyClass:
    def method(self):
        pass

def my_function():
    pass
"""
        result = parser.extract_imports(code)
        assert result[0].line_number == 1

        classes = parser.extract_classes(code)
        assert classes[0].line_number == 3

        functions = parser.extract_functions(code)
        assert functions[0].line_number == 7


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
