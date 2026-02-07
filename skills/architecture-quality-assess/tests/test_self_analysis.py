"""Self-analysis test - eating our own dog food.

This test runs the architecture quality assessment skill on itself,
demonstrating that the tool works on a real Python project and
validating its functionality in a practical scenario.

The self-analysis serves multiple purposes:
1. Integration test with a known codebase
2. Demonstration of the skill's capabilities
3. Validation that the skill can analyze itself
4. Practical example for documentation
"""

import sys
from pathlib import Path

import pytest

# Add parent directory to path for imports
TESTS_DIR = Path(__file__).resolve().parent
SKILL_DIR = TESTS_DIR.parent
sys.path.insert(0, str(SKILL_DIR))
sys.path.insert(0, str(SKILL_DIR / "scripts"))

from scripts.assess import AssessmentOrchestrator
from lib.reporters import generate_all_reports


class TestSelfAnalysis:
    """Test the skill by analyzing itself."""

    @pytest.fixture
    def skill_path(self) -> Path:
        """Path to the skill directory (analyzing ourselves)."""
        return SKILL_DIR

    @pytest.fixture
    def output_dir(self, tmp_path) -> Path:
        """Temporary directory for test outputs."""
        return tmp_path / "self-analysis-reports"

    def test_self_analysis_runs_successfully(self, skill_path):
        """Test that the skill can analyze its own codebase."""
        orchestrator = AssessmentOrchestrator(
            project_path=skill_path,
            verbose=True,
            cache_enabled=False,
        )

        # Run assessment
        result = orchestrator.run()

        # Verify assessment completed
        assert result is not None
        assert result.project_info is not None
        assert result.metadata is not None

        # Verify project detection identified this as Python
        assert "python" in result.project_info.project_type.lower()

        # Verify files were parsed
        assert orchestrator.stats["files_parsed"] > 0

        # Print summary
        print("\n" + "=" * 60)
        print("SELF-ANALYSIS RESULTS")
        print("=" * 60)
        print(f"Project: {result.project_info.name}")
        print(f"Framework: {result.project_info.framework}")
        print(f"Files discovered: {orchestrator.stats['files_discovered']}")
        print(f"Files parsed: {orchestrator.stats['files_parsed']}")
        print(f"Parse errors: {orchestrator.stats['parse_errors']}")
        print(f"Total violations: {len(result.violations)}")

        # Break down by severity
        severity_counts = {
            "CRITICAL": 0,
            "HIGH": 0,
            "MEDIUM": 0,
            "LOW": 0,
        }
        for v in result.violations:
            severity_counts[v.severity] = severity_counts.get(v.severity, 0) + 1

        print(f"\nViolations by severity:")
        print(f"  Critical: {severity_counts['CRITICAL']}")
        print(f"  High:     {severity_counts['HIGH']}")
        print(f"  Medium:   {severity_counts['MEDIUM']}")
        print(f"  Low:      {severity_counts['LOW']}")

        # Show sample violations
        if result.violations:
            print(f"\nSample violations (showing first 5):")
            for i, v in enumerate(result.violations[:5], 1):
                print(f"  {i}. [{v.severity}] {v.message}")
                print(f"     File: {v.file_path}")
                if v.line_number:
                    print(f"     Line: {v.line_number}")

        print("=" * 60)

    def test_generate_self_analysis_reports(self, skill_path, output_dir):
        """Generate all report formats for self-analysis."""
        orchestrator = AssessmentOrchestrator(
            project_path=skill_path,
            verbose=False,
            cache_enabled=False,
        )

        result = orchestrator.run()

        # Generate all reports
        output_dir.mkdir(parents=True, exist_ok=True)
        paths = generate_all_reports(
            result,
            output_dir,
            base_name="self-analysis"
        )

        # Verify reports were created
        assert "markdown" in paths
        assert "json" in paths
        assert paths["markdown"].exists()
        assert paths["json"].exists()

        # Read and verify markdown report
        markdown_content = paths["markdown"].read_text()
        assert "# Architecture Quality Assessment Report" in markdown_content
        assert result.project_info.name in markdown_content

        # Read and verify JSON report
        json_content = paths["json"].read_text()
        import json
        json_data = json.loads(json_content)
        assert json_data["project_info"]["name"] == result.project_info.name

        print(f"\nReports generated in: {output_dir}")
        for fmt, path in paths.items():
            size = path.stat().st_size
            print(f"  {fmt}: {path.name} ({size:,} bytes)")

    def test_dependency_graph_for_self(self, skill_path):
        """Verify dependency graph construction on skill codebase."""
        orchestrator = AssessmentOrchestrator(
            project_path=skill_path,
            verbose=False,
            cache_enabled=False,
        )

        result = orchestrator.run()

        # Check dependency graph
        graph = orchestrator.dependency_graph
        assert len(graph._nodes) > 0

        # Count edges
        total_edges = sum(len(node.dependencies) for node in graph._nodes.values())

        print(f"\nDependency Graph Analysis:")
        print(f"  Nodes (modules): {len(graph._nodes)}")
        print(f"  Edges (dependencies): {total_edges}")

        # Check for circular dependencies
        cycles = graph.detect_cycles()
        if cycles:
            print(f"  Circular dependencies: {len(cycles)}")
            for i, cycle in enumerate(cycles[:3], 1):
                print(f"    {i}. {' → '.join(cycle)}")
        else:
            print(f"  Circular dependencies: None (excellent!)")

        # Show most coupled modules
        fan_metrics = graph.calculate_fan_metrics()
        if "most_coupled" in fan_metrics:
            print(f"\n  Most coupled modules:")
            for module_info in fan_metrics["most_coupled"][:5]:
                print(f"    - {module_info['path']} (FAN-OUT: {module_info['fan_out']})")

    def test_metrics_calculation(self, skill_path):
        """Verify metrics are calculated correctly."""
        orchestrator = AssessmentOrchestrator(
            project_path=skill_path,
            verbose=False,
            cache_enabled=False,
        )

        result = orchestrator.run()

        # Verify metrics exist
        metrics = result.metrics
        assert metrics is not None

        # Verify basic metrics
        assert hasattr(metrics, "total_files")
        assert metrics.total_files > 0

        print(f"\nMetrics:")
        print(f"  Total files: {metrics.total_files}")

        if hasattr(metrics, "total_lines"):
            print(f"  Total lines: {metrics.total_lines}")

        if hasattr(metrics, "avg_file_size"):
            print(f"  Average file size: {metrics.avg_file_size:.0f} LOC")

        # Check coupling metrics
        if hasattr(metrics, "coupling") and metrics.coupling:
            print(f"\n  Coupling metrics:")
            print(f"    Average FAN-OUT: {metrics.coupling.avg_fan_out:.2f}")
            print(f"    Max FAN-OUT: {metrics.coupling.max_fan_out}")
            print(f"    Circular dependencies: {metrics.coupling.circular_dependency_count}")

    def test_save_permanent_self_analysis(self, skill_path):
        """Generate and save permanent self-analysis report.

        This creates a permanent report in the skill's tests directory
        that can be reviewed and used as documentation.
        """
        orchestrator = AssessmentOrchestrator(
            project_path=skill_path,
            verbose=False,
            cache_enabled=False,
        )

        result = orchestrator.run()

        # Save to tests directory
        reports_dir = TESTS_DIR / "self-analysis-reports"
        reports_dir.mkdir(exist_ok=True)

        paths = generate_all_reports(
            result,
            reports_dir,
            base_name="skill-self-assessment"
        )

        print(f"\nPermanent self-analysis reports saved:")
        for fmt, path in paths.items():
            print(f"  {path}")

        # Verify files exist and have content
        for path in paths.values():
            assert path.exists()
            assert path.stat().st_size > 0


def run_self_analysis_standalone():
    """Run self-analysis as a standalone script.

    This can be called directly to generate a self-analysis report
    without pytest.
    """
    print("Running self-analysis...")

    orchestrator = AssessmentOrchestrator(
        project_path=SKILL_DIR,
        verbose=True,
        cache_enabled=False,
    )

    result = orchestrator.run()

    # Save reports
    reports_dir = TESTS_DIR / "self-analysis-reports"
    reports_dir.mkdir(exist_ok=True)

    paths = generate_all_reports(
        result,
        reports_dir,
        base_name="skill-self-assessment"
    )

    print("\n" + "=" * 60)
    print("Self-analysis complete!")
    print("=" * 60)
    print(f"\nReports saved to: {reports_dir}")
    for fmt, path in paths.items():
        print(f"  {fmt}: {path.name}")
    print()


if __name__ == "__main__":
    # Can be run as standalone script or via pytest
    if len(sys.argv) > 1 and sys.argv[1] == "--standalone":
        run_self_analysis_standalone()
    else:
        pytest.main([__file__, "-v", "-s"])
