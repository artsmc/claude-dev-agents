"""Tests for coupling analyzer.

Validates FAN-IN/FAN-OUT metrics, circular dependency detection,
God module detection, and deep dependency chain detection.
"""

import pytest
from pathlib import Path

from lib.analyzers.coupling_analyzer import CouplingAnalyzer
from lib.analyzers.base import AnalysisContext
from lib.graph.dependency_graph import DependencyGraph
from lib.models.config import AssessmentConfig, CouplingThresholds


@pytest.fixture
def config():
    """Create test configuration."""
    return AssessmentConfig()


@pytest.fixture
def analyzer():
    """Create coupling analyzer instance."""
    return CouplingAnalyzer()


def test_analyzer_metadata(analyzer):
    """Test analyzer metadata."""
    assert analyzer.get_name() == "coupling"
    assert "coupling" in analyzer.get_description().lower()


def test_high_fan_out_detection(analyzer, config):
    """Test detection of high FAN-OUT violations."""
    # Create graph with high coupling
    graph = DependencyGraph()
    graph.add_node("src/app.py")

    # Add 12 dependencies (exceeds HIGH threshold of 10)
    for i in range(12):
        graph.add_dependency("src/app.py", f"src/dep{i}.py")

    context = AnalysisContext(
        project_root=Path("/tmp/test"),
        config=config,
        dependency_graph=graph,
    )

    violations = analyzer.analyze(context)

    # Should detect high coupling
    assert len(violations) > 0
    high_coupling = [v for v in violations if v.type == "HighCoupling"]
    assert len(high_coupling) == 1
    assert high_coupling[0].severity == "HIGH"
    assert "FAN-OUT: 12" in high_coupling[0].message


def test_medium_fan_out_detection(analyzer, config):
    """Test detection of medium FAN-OUT violations."""
    graph = DependencyGraph()
    graph.add_node("src/service.py")

    # Add 8 dependencies (exceeds MEDIUM threshold of 7)
    for i in range(8):
        graph.add_dependency("src/service.py", f"src/util{i}.py")

    context = AnalysisContext(
        project_root=Path("/tmp/test"),
        config=config,
        dependency_graph=graph,
    )

    violations = analyzer.analyze(context)

    # Should detect medium coupling
    high_coupling = [v for v in violations if v.type == "HighCoupling"]
    assert len(high_coupling) == 1
    assert high_coupling[0].severity == "MEDIUM"


def test_god_module_detection(analyzer, config):
    """Test detection of God modules with high FAN-IN."""
    graph = DependencyGraph()
    graph.add_node("src/utils.py")

    # Add 25 dependents (exceeds threshold of 20)
    for i in range(25):
        graph.add_dependency(f"src/module{i}.py", "src/utils.py")

    context = AnalysisContext(
        project_root=Path("/tmp/test"),
        config=config,
        dependency_graph=graph,
    )

    violations = analyzer.analyze(context)

    # Should detect God module
    god_modules = [v for v in violations if v.type == "GodModule"]
    assert len(god_modules) == 1
    assert god_modules[0].severity == "HIGH"
    assert "FAN-IN: 25" in god_modules[0].message


def test_circular_dependency_detection(analyzer, config):
    """Test detection of circular dependencies."""
    graph = DependencyGraph()

    # Create circular dependency: A -> B -> C -> A
    graph.add_dependency("src/a.py", "src/b.py")
    graph.add_dependency("src/b.py", "src/c.py")
    graph.add_dependency("src/c.py", "src/a.py")

    context = AnalysisContext(
        project_root=Path("/tmp/test"),
        config=config,
        dependency_graph=graph,
    )

    violations = analyzer.analyze(context)

    # Should detect circular dependency
    circular = [v for v in violations if v.type == "CircularDependency"]
    assert len(circular) > 0
    assert circular[0].severity == "CRITICAL"
    assert circular[0].metadata["cycle_length"] == 4  # A -> B -> C -> A (4 nodes)


def test_deep_dependency_chain_detection(analyzer, config):
    """Test detection of deep dependency chains."""
    graph = DependencyGraph()

    # Create deep chain: A -> B -> C -> D -> E -> F -> G (7 levels)
    chain = ["src/a.py", "src/b.py", "src/c.py", "src/d.py",
             "src/e.py", "src/f.py", "src/g.py"]

    for i in range(len(chain) - 1):
        graph.add_dependency(chain[i], chain[i + 1])

    context = AnalysisContext(
        project_root=Path("/tmp/test"),
        config=config,
        dependency_graph=graph,
    )

    violations = analyzer.analyze(context)

    # Should detect deep chain
    deep_chains = [v for v in violations if v.type == "DeepDependencyChain"]
    assert len(deep_chains) > 0
    assert deep_chains[0].severity == "MEDIUM"
    assert deep_chains[0].metadata["depth"] >= 6


def test_custom_thresholds(analyzer):
    """Test coupling analyzer with custom thresholds."""
    # Create config with custom thresholds
    config = AssessmentConfig()
    config.project.coupling_thresholds = CouplingThresholds(
        fan_out_medium=5,
        fan_out_high=8,
        fan_in_god_module=15,
    )

    graph = DependencyGraph()
    graph.add_node("src/custom.py")

    # Add 6 dependencies (exceeds custom MEDIUM threshold of 5)
    for i in range(6):
        graph.add_dependency("src/custom.py", f"src/dep{i}.py")

    context = AnalysisContext(
        project_root=Path("/tmp/test"),
        config=config,
        dependency_graph=graph,
    )

    violations = analyzer.analyze(context)

    # Should detect with custom threshold
    assert len(violations) > 0


def test_no_violations(analyzer, config):
    """Test analyzer with well-structured code (no violations)."""
    graph = DependencyGraph()

    # Add modules with low coupling
    graph.add_dependency("src/app.py", "src/service.py")
    graph.add_dependency("src/app.py", "src/config.py")
    graph.add_dependency("src/service.py", "src/repository.py")

    context = AnalysisContext(
        project_root=Path("/tmp/test"),
        config=config,
        dependency_graph=graph,
    )

    violations = analyzer.analyze(context)

    # Should have no violations
    assert len(violations) == 0


def test_external_dependencies_ignored(analyzer, config):
    """Test that external dependencies don't count toward FAN-OUT."""
    graph = DependencyGraph()
    graph.add_node("src/app.py")

    # Add many external dependencies
    for i in range(15):
        graph.add_dependency("src/app.py", f"external/lib{i}", is_external=True)

    # Add few internal dependencies
    graph.add_dependency("src/app.py", "src/utils.py")

    context = AnalysisContext(
        project_root=Path("/tmp/test"),
        config=config,
        dependency_graph=graph,
    )

    violations = analyzer.analyze(context)

    # Should not flag external dependencies
    high_coupling = [v for v in violations if v.type == "HighCoupling"]
    assert len(high_coupling) == 0


def test_violation_metadata(analyzer, config):
    """Test that violations include proper metadata."""
    graph = DependencyGraph()
    graph.add_node("src/app.py")

    for i in range(12):
        graph.add_dependency("src/app.py", f"src/dep{i}.py")

    context = AnalysisContext(
        project_root=Path("/tmp/test"),
        config=config,
        dependency_graph=graph,
    )

    violations = analyzer.analyze(context)

    assert len(violations) > 0
    violation = violations[0]

    # Check metadata
    assert "fan_out" in violation.metadata
    assert "fan_in" in violation.metadata
    assert "instability" in violation.metadata
    assert "dependencies" in violation.metadata

    # Check violation structure
    assert violation.dimension == "coupling"
    assert violation.id.startswith("CPL-")
    assert violation.recommendation != ""
    assert violation.explanation != ""
