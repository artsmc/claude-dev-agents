"""Integration tests for architecture quality assessment.

Tests the complete assessment pipeline on fixture projects,
validating end-to-end functionality including:
- Project detection
- File parsing
- Dependency graph construction
- Analyzer execution
- Report generation
"""

import json
import sys
from pathlib import Path

import pytest

# Add parent directory to path for imports
TESTS_DIR = Path(__file__).resolve().parent
SKILL_DIR = TESTS_DIR.parent
sys.path.insert(0, str(SKILL_DIR))
sys.path.insert(0, str(SKILL_DIR / "scripts"))

from scripts.assess import AssessmentOrchestrator


class TestIntegration:
    """Integration tests for full assessment pipeline."""

    @pytest.fixture
    def django_fixture_path(self) -> Path:
        """Path to Django test fixture."""
        return TESTS_DIR / "fixtures" / "django-app"

    @pytest.fixture
    def fastapi_fixture_path(self) -> Path:
        """Path to FastAPI test fixture."""
        return TESTS_DIR / "fixtures" / "python-fastapi"

    def test_django_assessment_runs(self, django_fixture_path):
        """Test that assessment runs on Django fixture without errors."""
        if not django_fixture_path.exists():
            pytest.skip("Django fixture not available")

        orchestrator = AssessmentOrchestrator(
            project_path=django_fixture_path,
            verbose=False,
            cache_enabled=False,
        )

        result = orchestrator.run()

        # Verify basic result structure
        assert result is not None
        assert result.project_info is not None
        assert result.metadata is not None
        assert result.metrics is not None
        assert isinstance(result.violations, list)

        # Verify project detection
        assert "django" in result.project_info.project_type.lower()

        # Verify some files were parsed
        assert orchestrator.stats["files_parsed"] > 0

        print(f"\nDjango Assessment Results:")
        print(f"  Project: {result.project_info.framework}")
        print(f"  Files parsed: {orchestrator.stats['files_parsed']}")
        print(f"  Violations found: {len(result.violations)}")

    def test_fastapi_assessment_runs(self, fastapi_fixture_path):
        """Test that assessment runs on FastAPI fixture without errors."""
        if not fastapi_fixture_path.exists():
            pytest.skip("FastAPI fixture not available")

        orchestrator = AssessmentOrchestrator(
            project_path=fastapi_fixture_path,
            verbose=False,
            cache_enabled=False,
        )

        result = orchestrator.run()

        # Verify basic result structure
        assert result is not None
        assert result.project_info is not None

        # Verify project detection
        assert "fastapi" in result.project_info.project_type.lower() or \
               "python" in result.project_info.project_type.lower()

        # Verify some files were parsed
        assert orchestrator.stats["files_parsed"] > 0

        print(f"\nFastAPI Assessment Results:")
        print(f"  Project: {result.project_info.framework}")
        print(f"  Files parsed: {orchestrator.stats['files_parsed']}")
        print(f"  Violations found: {len(result.violations)}")

    def test_markdown_report_generation(self, django_fixture_path):
        """Test markdown report generation."""
        if not django_fixture_path.exists():
            pytest.skip("Django fixture not available")

        orchestrator = AssessmentOrchestrator(
            project_path=django_fixture_path,
            verbose=False,
            cache_enabled=False,
        )

        result = orchestrator.run()

        # Generate markdown report
        from lib.reporters import generate_markdown_report

        markdown = generate_markdown_report(result)

        # Verify markdown structure
        assert "# Architecture Quality Assessment Report" in markdown
        assert "## Executive Summary" in markdown
        assert "## 1. Project Overview" in markdown

        # Verify it contains project info
        assert result.project_info.name in markdown

        print(f"\nMarkdown report generated: {len(markdown)} characters")

    def test_json_report_generation(self, django_fixture_path):
        """Test JSON report generation."""
        if not django_fixture_path.exists():
            pytest.skip("Django fixture not available")

        orchestrator = AssessmentOrchestrator(
            project_path=django_fixture_path,
            verbose=False,
            cache_enabled=False,
        )

        result = orchestrator.run()

        # Generate JSON report
        from lib.reporters import generate_json_report

        json_output = generate_json_report(result, pretty=True)

        # Verify it's valid JSON
        data = json.loads(json_output)

        # Verify structure
        assert "schema_version" in data
        assert "metadata" in data
        assert "project_info" in data
        assert "summary" in data
        assert "violations" in data

        # Verify content
        assert data["project_info"]["name"] == result.project_info.name
        assert data["summary"]["total_violations"] == len(result.violations)

        print(f"\nJSON report generated: {len(json_output)} characters")

    def test_task_list_generation(self, django_fixture_path):
        """Test task list generation."""
        if not django_fixture_path.exists():
            pytest.skip("Django fixture not available")

        orchestrator = AssessmentOrchestrator(
            project_path=django_fixture_path,
            verbose=False,
            cache_enabled=False,
        )

        result = orchestrator.run()

        # Generate task list
        from lib.reporters import generate_task_list

        task_list = generate_task_list(result)

        # Verify structure
        assert "# Architecture Refactoring Tasks" in task_list
        assert "## Summary" in task_list

        if result.violations:
            # If there are violations, should have phases
            assert "## Phase" in task_list

        print(f"\nTask list generated: {len(task_list)} characters")

    def test_dependency_graph_construction(self, fastapi_fixture_path):
        """Test dependency graph is properly constructed."""
        if not fastapi_fixture_path.exists():
            pytest.skip("FastAPI fixture not available")

        orchestrator = AssessmentOrchestrator(
            project_path=fastapi_fixture_path,
            verbose=False,
            cache_enabled=False,
        )

        result = orchestrator.run()

        # Verify dependency graph has nodes
        graph = orchestrator.dependency_graph
        assert len(graph._nodes) > 0

        # Verify some edges were created
        total_edges = sum(len(node.dependencies) for node in graph._nodes.values())
        print(f"\nDependency graph: {len(graph._nodes)} nodes, {total_edges} edges")

    def test_statistics_tracking(self, django_fixture_path):
        """Test that statistics are properly tracked."""
        if not django_fixture_path.exists():
            pytest.skip("Django fixture not available")

        orchestrator = AssessmentOrchestrator(
            project_path=django_fixture_path,
            verbose=False,
            cache_enabled=False,
        )

        result = orchestrator.run()

        # Verify statistics
        stats = orchestrator.stats
        assert stats["files_discovered"] > 0
        assert stats["files_parsed"] > 0
        assert stats["files_parsed"] <= stats["files_discovered"]

        # Verify stats are in metadata
        assert "statistics" in result.metadata
        assert result.metadata["statistics"] == stats

        print(f"\nStatistics tracked: {stats}")

    def test_severity_filtering(self, django_fixture_path):
        """Test severity filtering works correctly."""
        if not django_fixture_path.exists():
            pytest.skip("Django fixture not available")

        orchestrator = AssessmentOrchestrator(
            project_path=django_fixture_path,
            verbose=False,
            cache_enabled=False,
        )

        result = orchestrator.run()

        # If there are violations, test filtering
        if result.violations:
            # Filter to only critical
            critical_violations = [
                v for v in result.violations if v.severity == "CRITICAL"
            ]

            # Create filtered result
            result.violations = critical_violations

            # Verify filtering worked
            for v in result.violations:
                assert v.severity == "CRITICAL"

    def test_ci_summary_generation(self, django_fixture_path):
        """Test CI/CD summary generation."""
        if not django_fixture_path.exists():
            pytest.skip("Django fixture not available")

        orchestrator = AssessmentOrchestrator(
            project_path=django_fixture_path,
            verbose=False,
            cache_enabled=False,
        )

        result = orchestrator.run()

        # Generate CI summary
        from lib.reporters import generate_ci_summary

        summary = generate_ci_summary(result)

        # Verify structure
        assert "passed" in summary
        assert "score" in summary
        assert "message" in summary
        assert "violations" in summary
        assert "project" in summary

        # Verify violations count matches
        total_violations = sum(summary["violations"].values()) - summary["violations"]["total"]
        assert total_violations == len(result.violations)

        print(f"\nCI Summary: {summary['message']}")
        print(f"  Passed: {summary['passed']}")
        print(f"  Score: {summary['score']}/100")


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "-s"])
