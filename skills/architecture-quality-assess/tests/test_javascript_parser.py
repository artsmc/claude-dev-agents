"""Unit tests for JavaScript/TypeScript parser.

Tests the regex-based JavaScript/TypeScript parser for import extraction,
class detection, function detection, and error handling.

Run with: python -m pytest tests/test_javascript_parser.py -v
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from lib.parsers.javascript_parser import JavaScriptParser
from lib.parsers.base import ParserError


class TestJavaScriptParser:
    """Test suite for JavaScriptParser."""

    @pytest.fixture
    def parser(self):
        """Create a JavaScriptParser instance."""
        return JavaScriptParser()

    @pytest.fixture
    def fixtures_dir(self):
        """Get fixtures directory path."""
        return Path(__file__).parent / "fixtures"

    def test_supported_extensions(self, parser):
        """Test that supported extensions are correct."""
        extensions = parser.get_supported_extensions()
        assert ".js" in extensions
        assert ".jsx" in extensions
        assert ".ts" in extensions
        assert ".tsx" in extensions
        assert ".mjs" in extensions
        assert ".cjs" in extensions

    def test_extract_imports_es6_default(self, parser):
        """Test extraction of ES6 default imports."""
        code = """
import React from 'react';
import express from 'express';
"""
        imports = parser.extract_imports(code)

        assert len(imports) == 2

        react_import = next(imp for imp in imports if imp.module == "react")
        assert react_import.name == "default"
        assert react_import.alias == "React"

    def test_extract_imports_es6_named(self, parser):
        """Test extraction of ES6 named imports."""
        code = """
import { useState, useEffect } from 'react';
import { Router, Route } from 'express';
"""
        imports = parser.extract_imports(code)

        # Should have at least 4 imports (2 from each statement)
        assert len(imports) >= 4

        react_imports = [imp for imp in imports if imp.module == "react"]
        import_names = [imp.name for imp in react_imports]
        assert "useState" in import_names
        assert "useEffect" in import_names

    def test_extract_imports_es6_named_with_alias(self, parser):
        """Test extraction of ES6 named imports with aliases."""
        code = """
import { Component as Comp, useState as useS } from 'react';
"""
        imports = parser.extract_imports(code)

        comp_import = next(imp for imp in imports if imp.name == "Component")
        assert comp_import.alias == "Comp"

        state_import = next(imp for imp in imports if imp.name == "useState")
        assert state_import.alias == "useS"

    def test_extract_imports_es6_namespace(self, parser):
        """Test extraction of ES6 namespace imports."""
        code = """
import * as React from 'react';
import * as _ from 'lodash';
"""
        imports = parser.extract_imports(code)

        react_import = next(imp for imp in imports if imp.module == "react")
        assert react_import.name == "*"
        assert react_import.alias == "React"

    def test_extract_imports_commonjs(self, parser):
        """Test extraction of CommonJS require statements."""
        code = """
const express = require('express');
const { Router } = require('express');
const path = require('path');
"""
        imports = parser.extract_imports(code)

        assert len(imports) >= 3

        express_import = next(imp for imp in imports if imp.module == "express" and imp.name == "default")
        assert express_import.alias == "express"

    def test_extract_imports_relative(self, parser):
        """Test extraction of relative imports."""
        code = """
import Button from './components/Button';
import utils from '../utils';
import config from '../../config';
"""
        imports = parser.extract_imports(code)

        assert len(imports) == 3
        assert all(imp.is_relative for imp in imports)

    def test_extract_imports_dynamic(self, parser):
        """Test extraction of dynamic imports."""
        code = """
const module = await import('./module');
import('./lazy-component');
"""
        imports = parser.extract_imports(code)

        dynamic_imports = [imp for imp in imports if imp.name == "*"]
        assert len(dynamic_imports) >= 2

    def test_extract_classes_simple(self, parser):
        """Test extraction of simple class definitions."""
        code = """
class MyClass {
  constructor() {
    this.value = 0;
  }

  method() {
    return this.value;
  }
}
"""
        classes = parser.extract_classes(code)

        assert len(classes) == 1
        assert classes[0].name == "MyClass"
        assert len(classes[0].methods) >= 1

    def test_extract_classes_with_extends(self, parser):
        """Test extraction of classes with inheritance."""
        code = """
class Base {
  baseMethod() {}
}

class Child extends Base {
  childMethod() {}
}
"""
        classes = parser.extract_classes(code)

        assert len(classes) == 2

        child_class = next(c for c in classes if c.name == "Child")
        assert "Base" in child_class.base_classes

    def test_extract_classes_exported(self, parser):
        """Test extraction of exported classes."""
        code = """
export class ExportedClass {
  method() {}
}

export default class DefaultClass {
  method() {}
}
"""
        classes = parser.extract_classes(code)

        assert len(classes) == 2
        class_names = [c.name for c in classes]
        assert "ExportedClass" in class_names
        assert "DefaultClass" in class_names

    def test_extract_functions_regular(self, parser):
        """Test extraction of regular function declarations."""
        code = """
function myFunction() {
  return true;
}

export function exportedFunction() {
  return false;
}

async function asyncFunction() {
  await something();
}
"""
        functions = parser.extract_functions(code)

        assert len(functions) >= 3
        function_names = [f.name for f in functions]
        assert "myFunction" in function_names
        assert "exportedFunction" in function_names
        assert "asyncFunction" in function_names

    def test_extract_functions_arrow(self, parser):
        """Test extraction of arrow functions."""
        code = """
const arrowFunc = () => {};
const arrowWithParams = (a, b) => a + b;
const asyncArrow = async (x) => await x;
"""
        functions = parser.extract_functions(code)

        assert len(functions) >= 3
        function_names = [f.name for f in functions]
        assert "arrowFunc" in function_names
        assert "arrowWithParams" in function_names
        assert "asyncArrow" in function_names

    def test_extract_functions_with_params(self, parser):
        """Test extraction of function parameters."""
        code = """
function withParams(a, b, c) {
  return a + b + c;
}

const arrow = (x, y) => x + y;
"""
        functions = parser.extract_functions(code)

        with_params = next(f for f in functions if f.name == "withParams")
        assert len(with_params.parameters) == 3
        assert "a" in with_params.parameters

        arrow = next(f for f in functions if f.name == "arrow")
        assert len(arrow.parameters) == 2

    def test_remove_comments_single_line(self, parser):
        """Test removal of single-line comments."""
        code = """
// This is a comment
const x = 1; // inline comment
"""
        cleaned = parser._remove_comments(code)

        assert "// This is a comment" not in cleaned
        assert "const x = 1;" in cleaned

    def test_remove_comments_multi_line(self, parser):
        """Test removal of multi-line comments."""
        code = """
/* This is a
   multi-line
   comment */
const x = 1;
"""
        cleaned = parser._remove_comments(code)

        assert "/*" not in cleaned
        assert "*/" not in cleaned
        assert "const x = 1;" in cleaned

    def test_parse_file_success(self, parser, tmp_path):
        """Test successful parsing of a valid JavaScript file."""
        test_file = tmp_path / "test.js"
        test_file.write_text("""
import React from 'react';

class MyComponent {
  render() {
    return <div>Hello</div>;
  }
}

export default MyComponent;
""")

        result = parser.parse_file(test_file)

        assert result is not None
        assert result.file_path == str(test_file)
        assert len(result.imports) >= 1
        assert len(result.classes) >= 1

    def test_parse_file_typescript(self, parser, tmp_path):
        """Test parsing of TypeScript file."""
        test_file = tmp_path / "test.ts"
        test_file.write_text("""
interface User {
  name: string;
  age: number;
}

function greet(user: User): string {
  return `Hello, ${user.name}`;
}
""")

        result = parser.parse_file(test_file)

        assert result is not None
        assert result.metadata["is_typescript"] is True

    def test_parse_file_nonexistent(self, parser):
        """Test parsing of nonexistent file."""
        with pytest.raises(ParserError):
            parser.parse_file(Path("/nonexistent/file.js"))

    def test_parse_fixture_nextjs(self, parser, fixtures_dir):
        """Test parsing of Next.js fixture files."""
        nextjs_dir = fixtures_dir / "nextjs-app-router"
        if not nextjs_dir.exists():
            pytest.skip("Next.js fixture not found")

        # Parse a component
        component_file = nextjs_dir / "components" / "Button.tsx"
        if component_file.exists():
            result = parser.parse_file(component_file)
            assert result is not None
            assert result.metadata["is_typescript"] is True

    def test_parse_fixture_express(self, parser, fixtures_dir):
        """Test parsing of Express fixture files."""
        express_dir = fixtures_dir / "express-api"
        if not express_dir.exists():
            pytest.skip("Express fixture not found")

        # Parse app.js
        app_file = express_dir / "app.js"
        result = parser.parse_file(app_file)

        assert result is not None
        assert len(result.imports) > 0

        # Check for express import
        import_modules = [imp.module for imp in result.imports]
        assert "express" in import_modules

    def test_is_parseable(self, parser):
        """Test file parseability check."""
        assert parser.is_parseable(Path("test.js")) is True
        assert parser.is_parseable(Path("test.jsx")) is True
        assert parser.is_parseable(Path("test.ts")) is True
        assert parser.is_parseable(Path("test.tsx")) is True
        assert parser.is_parseable(Path("test.py")) is False
        assert parser.is_parseable(Path("test.txt")) is False

    def test_parse_parameters_simple(self, parser):
        """Test parameter parsing."""
        params = parser._parse_parameters("a, b, c")
        assert params == ["a", "b", "c"]

    def test_parse_parameters_with_types(self, parser):
        """Test parameter parsing with TypeScript types."""
        params = parser._parse_parameters("a: string, b: number")
        assert params == ["a", "b"]

    def test_parse_parameters_with_defaults(self, parser):
        """Test parameter parsing with default values."""
        params = parser._parse_parameters("a = 1, b = 'hello'")
        assert params == ["a", "b"]

    def test_parse_parameters_rest(self, parser):
        """Test parameter parsing with rest parameters."""
        params = parser._parse_parameters("a, ...rest")
        assert "a" in params
        assert "rest" in params

    def test_extract_methods_from_class(self, parser):
        """Test extraction of class methods."""
        class_body = """
  constructor(name) {
    this.name = name;
  }

  async fetchData() {
    return await fetch('/api');
  }

  static create() {
    return new MyClass();
  }
"""
        methods = parser._extract_methods_from_class(class_body, 1)

        assert len(methods) >= 2
        method_names = [m.name for m in methods]
        assert "fetchData" in method_names
        assert "create" in method_names

        # Check async
        fetch_method = next(m for m in methods if m.name == "fetchData")
        assert fetch_method.is_async is True

    def test_line_numbers(self, parser):
        """Test that line numbers are captured correctly."""
        code = """
import React from 'react';

class MyClass {
  method() {}
}

function myFunction() {}
"""
        imports = parser.extract_imports(code)
        assert imports[0].line_number == 2

        classes = parser.extract_classes(code)
        assert classes[0].line_number == 4

        functions = parser.extract_functions(code)
        assert functions[0].line_number == 8


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
