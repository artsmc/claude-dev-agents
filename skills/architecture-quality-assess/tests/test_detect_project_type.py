"""Unit tests for project type detection.

Tests the project type detection script across multiple frameworks
and project structures.

Run with: python -m pytest tests/test_detect_project_type.py -v
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from scripts.detect_project_type import ProjectTypeDetector
from lib.models.project_type import ProjectType


class TestProjectTypeDetector:
    """Test suite for ProjectTypeDetector."""

    @pytest.fixture
    def fixtures_dir(self):
        """Get fixtures directory path."""
        return Path(__file__).parent / "fixtures"

    def test_detect_nextjs_app_router(self, fixtures_dir):
        """Test detection of Next.js App Router project."""
        project_path = fixtures_dir / "nextjs-app-router"
        detector = ProjectTypeDetector(project_path)
        result = detector.detect()

        assert result["type"] == ProjectType.NEXTJS.value
        assert result["display_name"] == "Next.js"
        assert "javascript" in result["languages"] or "typescript" in result["languages"]
        assert result["confidence"] >= 0.9
        assert result["patterns"]["router_type"] == "app_router"
        assert result["patterns"]["has_app_directory"] is True

    def test_detect_fastapi(self, fixtures_dir):
        """Test detection of FastAPI project."""
        project_path = fixtures_dir / "python-fastapi"
        detector = ProjectTypeDetector(project_path)
        result = detector.detect()

        assert result["type"] == ProjectType.PYTHON_FASTAPI.value
        assert result["display_name"] == "FastAPI"
        assert "python" in result["languages"]
        assert result["confidence"] >= 0.85
        assert result["patterns"]["has_app_dir"] is True
        assert result["patterns"]["has_routers"] is True

    def test_detect_express(self, fixtures_dir):
        """Test detection of Express.js project."""
        project_path = fixtures_dir / "express-api"
        detector = ProjectTypeDetector(project_path)
        result = detector.detect()

        assert result["type"] == ProjectType.NODEJS_EXPRESS.value
        assert result["display_name"] == "Express.js"
        assert "javascript" in result["languages"] or "typescript" in result["languages"]
        assert result["confidence"] >= 0.8
        assert "entry_point" in result["patterns"]
        assert result["patterns"]["has_routes"] is True

    def test_detect_django(self, fixtures_dir):
        """Test detection of Django project."""
        project_path = fixtures_dir / "django-app"
        detector = ProjectTypeDetector(project_path)
        result = detector.detect()

        assert result["type"] == ProjectType.PYTHON_DJANGO.value
        assert result["display_name"] == "Django"
        assert "python" in result["languages"]
        assert result["confidence"] >= 0.9

    def test_detect_nonexistent_project(self, tmp_path):
        """Test detection of nonexistent project path."""
        project_path = tmp_path / "nonexistent"
        detector = ProjectTypeDetector(project_path)
        result = detector.detect()

        assert result["type"] == ProjectType.UNKNOWN.value
        assert result["confidence"] == 0.0

    def test_detect_empty_directory(self, tmp_path):
        """Test detection of empty directory."""
        detector = ProjectTypeDetector(tmp_path)
        result = detector.detect()

        assert result["type"] == ProjectType.UNKNOWN.value
        assert result["confidence"] == 0.0

    def test_check_package_json_dependency(self, tmp_path):
        """Test package.json dependency checking."""
        # Create a package.json
        package_json = tmp_path / "package.json"
        package_json.write_text(
            '{"dependencies": {"express": "^4.0.0"}, "devDependencies": {"jest": "^29.0.0"}}'
        )

        detector = ProjectTypeDetector(tmp_path)

        assert detector._check_package_json_dependency("express") is True
        assert detector._check_package_json_dependency("jest") is True
        assert detector._check_package_json_dependency("react") is False

    def test_check_python_dependency(self, tmp_path):
        """Test Python dependency checking."""
        # Create requirements.txt
        requirements = tmp_path / "requirements.txt"
        requirements.write_text("fastapi==0.104.1\nuvicorn==0.24.0\n")

        detector = ProjectTypeDetector(tmp_path)

        assert detector._check_python_dependency("fastapi") is True
        assert detector._check_python_dependency("uvicorn") is True
        assert detector._check_python_dependency("django") is False

    def test_has_python_files(self, tmp_path):
        """Test Python file detection."""
        # Create a Python file
        (tmp_path / "test.py").write_text("print('hello')")

        detector = ProjectTypeDetector(tmp_path)
        assert detector._has_python_files() is True

    def test_has_javascript_files(self, tmp_path):
        """Test JavaScript file detection."""
        # Create a JavaScript file
        (tmp_path / "test.js").write_text("console.log('hello');")

        detector = ProjectTypeDetector(tmp_path)
        assert detector._has_javascript_files() is True

    def test_nextjs_without_router_dirs(self, tmp_path):
        """Test Next.js detection when app/ and pages/ are missing."""
        # Create next.config.js
        (tmp_path / "next.config.js").write_text("module.exports = {}")

        detector = ProjectTypeDetector(tmp_path)
        result = detector.detect()

        assert result["type"] == ProjectType.NEXTJS.value
        assert result["patterns"]["router_type"] == "unknown"

    def test_react_not_nextjs(self, tmp_path):
        """Test that React projects without Next.js are detected correctly."""
        # Create package.json with React but not Next.js
        package_json = tmp_path / "package.json"
        package_json.write_text('{"dependencies": {"react": "^18.0.0"}}')

        # Create React structure
        src = tmp_path / "src"
        src.mkdir()
        (src / "App.jsx").write_text("export default function App() { return <div>App</div>; }")

        detector = ProjectTypeDetector(tmp_path)
        result = detector.detect()

        assert result["type"] == ProjectType.REACT.value
        assert result["display_name"] == "React"


class TestProjectTypeIntegration:
    """Integration tests using real fixture projects."""

    @pytest.fixture
    def fixtures_dir(self):
        """Get fixtures directory path."""
        return Path(__file__).parent / "fixtures"

    def test_all_fixtures_detected(self, fixtures_dir):
        """Test that all fixture projects are detected correctly."""
        expected_types = {
            "nextjs-app-router": ProjectType.NEXTJS,
            "python-fastapi": ProjectType.PYTHON_FASTAPI,
            "express-api": ProjectType.NODEJS_EXPRESS,
            "django-app": ProjectType.PYTHON_DJANGO,
        }

        for fixture_name, expected_type in expected_types.items():
            project_path = fixtures_dir / fixture_name
            if not project_path.exists():
                pytest.skip(f"Fixture {fixture_name} not found")

            detector = ProjectTypeDetector(project_path)
            result = detector.detect()

            assert result["type"] == expected_type.value, (
                f"Expected {expected_type.value} for {fixture_name}, "
                f"got {result['type']}"
            )

    def test_confidence_scores(self, fixtures_dir):
        """Test that confidence scores are reasonable."""
        for fixture_dir in fixtures_dir.iterdir():
            if not fixture_dir.is_dir():
                continue

            detector = ProjectTypeDetector(fixture_dir)
            result = detector.detect()

            # Confidence should be between 0 and 1
            assert 0.0 <= result["confidence"] <= 1.0

            # Known projects should have high confidence
            if result["type"] != ProjectType.UNKNOWN.value:
                assert result["confidence"] >= 0.8


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
