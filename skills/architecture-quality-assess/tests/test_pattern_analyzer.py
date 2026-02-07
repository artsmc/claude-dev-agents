"""Tests for pattern analyzer.

Validates detection of anti-patterns and opportunities for
design pattern improvements.
"""

import pytest
from pathlib import Path
from tempfile import TemporaryDirectory

from lib.analyzers.pattern_analyzer import PatternAnalyzer
from lib.analyzers.base import AnalysisContext
from lib.models.config import AssessmentConfig


@pytest.fixture
def config():
    """Create test configuration."""
    return AssessmentConfig()


@pytest.fixture
def analyzer():
    """Create pattern analyzer instance."""
    return PatternAnalyzer()


def test_analyzer_metadata(analyzer):
    """Test analyzer metadata."""
    assert analyzer.get_name() == "patterns"
    assert "pattern" in analyzer.get_description().lower()


def test_magic_numbers_detection(analyzer, config):
    """Test detection of magic numbers."""
    with TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)
        test_file = project_root / "test.py"

        # Create code with magic numbers
        test_file.write_text("""
def calculate_price(quantity):
    base_price = quantity * 29.99
    if quantity > 100:
        discount = base_price * 0.15
    elif quantity > 50:
        discount = base_price * 0.10
    elif quantity > 20:
        discount = base_price * 0.05
    else:
        discount = 0

    tax = base_price * 0.08
    shipping = 5.99 if base_price < 50 else 0

    return base_price - discount + tax + shipping
""")

        context = AnalysisContext(
            project_root=project_root,
            config=config,
            file_paths=[test_file],
        )

        violations = analyzer.analyze(context)

        # Should detect magic numbers
        magic_violations = [v for v in violations if v.type == "MagicNumbers"]
        assert len(magic_violations) > 0
        assert magic_violations[0].severity == "LOW"


def test_long_method_detection(analyzer, config):
    """Test detection of long methods."""
    with TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)
        test_file = project_root / "test.py"

        # Create very long method (>50 lines)
        lines = "\n".join(f"    x{i} = {i}" for i in range(60))
        test_file.write_text(f"""
def very_long_method():
{lines}
    return sum
""")

        context = AnalysisContext(
            project_root=project_root,
            config=config,
            file_paths=[test_file],
        )

        violations = analyzer.analyze(context)

        # Should detect long method
        long_methods = [v for v in violations if v.type == "LongMethod"]
        assert len(long_methods) > 0
        assert "very_long_method" in long_methods[0].message


def test_complex_method_detection(analyzer, config):
    """Test detection of overly complex methods."""
    with TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)
        test_file = project_root / "test.py"

        # Create complex method with high cyclomatic complexity
        test_file.write_text("""
def complex_method(a, b, c, d, e):
    if a > 0:
        if b > 0:
            if c > 0:
                if d > 0:
                    if e > 0:
                        for i in range(10):
                            for j in range(10):
                                while True:
                                    if i == j:
                                        break
                                    elif i > j:
                                        continue
                                    else:
                                        pass
    return result
""")

        context = AnalysisContext(
            project_root=project_root,
            config=config,
            file_paths=[test_file],
        )

        violations = analyzer.analyze(context)

        # Should detect complexity
        complex_violations = [v for v in violations if v.type == "ComplexMethod"]
        assert len(complex_violations) > 0


def test_unused_imports_detection(analyzer, config):
    """Test detection of unused imports."""
    with TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)
        test_file = project_root / "test.py"

        # Create file with many unused imports
        test_file.write_text("""
import os
import sys
import json
import re
import datetime
from pathlib import Path
from typing import List

def simple_function():
    return 42
""")

        context = AnalysisContext(
            project_root=project_root,
            config=config,
            file_paths=[test_file],
        )

        violations = analyzer.analyze(context)

        # Should detect unused imports
        unused_violations = [v for v in violations if v.type == "UnusedImports"]
        assert len(unused_violations) > 0


def test_factory_opportunity_detection(analyzer, config):
    """Test detection of Factory pattern opportunities."""
    with TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)
        test_file = project_root / "test.py"

        # Create code with scattered complex object creation
        test_file.write_text("""
def create_user_1():
    return User('John', 'Doe', 'john@example.com', 30, 'admin', True)

def create_user_2():
    return User('Jane', 'Smith', 'jane@example.com', 25, 'user', False)

def create_user_3():
    return User('Bob', 'Johnson', 'bob@example.com', 35, 'moderator', True)

def create_user_4():
    return User('Alice', 'Williams', 'alice@example.com', 28, 'user', False)
""")

        context = AnalysisContext(
            project_root=project_root,
            config=config,
            file_paths=[test_file],
        )

        violations = analyzer.analyze(context)

        # Should detect Factory opportunity
        factory_violations = [
            v for v in violations if v.type == "FactoryOpportunity"
        ]
        assert len(factory_violations) > 0


def test_strategy_opportunity_detection(analyzer, config):
    """Test detection of Strategy pattern opportunities."""
    with TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)
        test_file = project_root / "test.py"

        # Create code with long if-elif chain
        test_file.write_text("""
def calculate_discount(customer_type):
    if customer_type == 'premium':
        return 0.20
    elif customer_type == 'gold':
        return 0.15
    elif customer_type == 'silver':
        return 0.10
    elif customer_type == 'bronze':
        return 0.05
    elif customer_type == 'new':
        return 0.0
    else:
        return 0.0
""")

        context = AnalysisContext(
            project_root=project_root,
            config=config,
            file_paths=[test_file],
        )

        violations = analyzer.analyze(context)

        # Should detect Strategy opportunity
        strategy_violations = [
            v for v in violations if v.type == "StrategyOpportunity"
        ]
        assert len(strategy_violations) > 0


def test_singleton_misuse_detection(analyzer, config):
    """Test detection of Singleton pattern misuse."""
    with TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)
        test_file = project_root / "test.py"

        # Create Singleton with mutable state
        test_file.write_text("""
class ConfigManager:
    _instance = None
    settings = {}  # Mutable class variable

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def set_config(self, key, value):
        self.settings[key] = value
""")

        context = AnalysisContext(
            project_root=project_root,
            config=config,
            file_paths=[test_file],
        )

        violations = analyzer.analyze(context)

        # Should detect Singleton misuse
        singleton_violations = [
            v for v in violations if v.type == "SingletonMisuse"
        ]
        assert len(singleton_violations) > 0


def test_no_violations_clean_code(analyzer, config):
    """Test analyzer with clean code (no anti-patterns)."""
    with TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)
        test_file = project_root / "test.py"

        # Create clean, well-structured code
        test_file.write_text("""
MAX_RETRIES = 3
TIMEOUT_SECONDS = 30

class UserService:
    def __init__(self, repository):
        self.repository = repository

    def get_user(self, user_id):
        return self.repository.find_by_id(user_id)

    def create_user(self, user_data):
        user = User(**user_data)
        return self.repository.save(user)
""")

        context = AnalysisContext(
            project_root=project_root,
            config=config,
            file_paths=[test_file],
        )

        violations = analyzer.analyze(context)

        # Should have minimal or no violations
        # (might have some minor ones, but no major anti-patterns)
        assert len([v for v in violations if v.severity in ["HIGH", "CRITICAL"]]) == 0


def test_violation_metadata(analyzer, config):
    """Test that violations include proper metadata."""
    with TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)
        test_file = project_root / "test.py"

        # Create long method
        lines = "\n".join(f"    x{i} = {i}" for i in range(60))
        test_file.write_text(f"""
def long_method():
{lines}
    return x
""")

        context = AnalysisContext(
            project_root=project_root,
            config=config,
            file_paths=[test_file],
        )

        violations = analyzer.analyze(context)

        assert len(violations) > 0
        violation = violations[0]

        # Check violation structure
        assert violation.dimension == "patterns"
        assert violation.id.startswith("PAT-")
        assert violation.recommendation != ""
        assert violation.explanation != ""
        assert len(violation.metadata) > 0


def test_multiple_pattern_detection(analyzer, config):
    """Test that multiple pattern issues are detected in one file."""
    with TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)
        test_file = project_root / "test.py"

        # Create file with multiple issues
        test_file.write_text("""
import os
import sys
import json

# Magic numbers
def calculate(x):
    result = x * 3.14159 + 42.5 - 7.8

    # Long if-elif chain
    if x == 1:
        return 1
    elif x == 2:
        return 2
    elif x == 3:
        return 3
    elif x == 4:
        return 4
    elif x == 5:
        return 5
    elif x == 6:
        return 6
    else:
        return 0
""")

        context = AnalysisContext(
            project_root=project_root,
            config=config,
            file_paths=[test_file],
        )

        violations = analyzer.analyze(context)

        # Should detect multiple types of violations
        violation_types = {v.type for v in violations}
        assert len(violation_types) >= 2  # At least 2 different types


def test_only_python_files_analyzed(analyzer, config):
    """Test that only Python files are analyzed."""
    with TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)

        # Create Python file with issues
        py_file = project_root / "test.py"
        lines = "\n".join(f"    x{i} = {i}" for i in range(60))
        py_file.write_text(f"def long_method():\n{lines}")

        # Create JavaScript file
        js_file = project_root / "test.js"
        js_file.write_text("function longMethod() { /* very long */ }")

        context = AnalysisContext(
            project_root=project_root,
            config=config,
            file_paths=[py_file, js_file],
        )

        violations = analyzer.analyze(context)

        # Should only analyze Python file
        assert all("test.py" in v.file_path for v in violations)
