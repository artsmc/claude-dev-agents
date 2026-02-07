"""Tests for layer analyzer.

Validates layer classification, database access detection,
and clean architecture dependency rule enforcement.
"""

import pytest
from pathlib import Path
from tempfile import TemporaryDirectory

from lib.analyzers.layer_analyzer import LayerAnalyzer
from lib.analyzers.base import AnalysisContext
from lib.graph.dependency_graph import DependencyGraph
from lib.models.config import AssessmentConfig, LayerDefinition


@pytest.fixture
def config():
    """Create test configuration."""
    config = AssessmentConfig()
    config.project.project_type = "nextjs"
    return config


@pytest.fixture
def analyzer():
    """Create layer analyzer instance."""
    return LayerAnalyzer()


def test_analyzer_metadata(analyzer):
    """Test analyzer metadata."""
    assert analyzer.get_name() == "layer"
    assert "layer" in analyzer.get_description().lower()


def test_nextjs_layer_classification(analyzer, config):
    """Test file classification for Next.js projects."""
    with TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)

        # Create test files
        (project_root / "app").mkdir()
        (project_root / "app" / "api").mkdir(parents=True)
        (project_root / "lib").mkdir()
        (project_root / "lib" / "services").mkdir(parents=True)
        (project_root / "lib" / "repositories").mkdir(parents=True)

        api_file = project_root / "app" / "api" / "users" / "route.ts"
        api_file.parent.mkdir(parents=True)
        api_file.write_text("export async function GET() {}")

        service_file = project_root / "lib" / "services" / "user_service.ts"
        service_file.write_text("export class UserService {}")

        context = AnalysisContext(
            project_root=project_root,
            config=config,
            file_paths=[api_file, service_file],
        )

        # Run analysis to classify files
        analyzer.analyze(context)

        # Check classifications
        assert "app/api/users/route.ts" in analyzer._file_layers
        assert analyzer._file_layers["app/api/users/route.ts"] == "presentation"

        assert "lib/services/user_service.ts" in analyzer._file_layers
        assert analyzer._file_layers["lib/services/user_service.ts"] == "business"


def test_sql_in_api_route_detection(analyzer, config):
    """Test detection of SQL queries in API routes."""
    with TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)
        (project_root / "app" / "api" / "users").mkdir(parents=True)

        # Create API route with SQL
        route_file = project_root / "app" / "api" / "users" / "route.ts"
        route_file.write_text("""
export async function GET() {
    const users = await db.query('SELECT * FROM users WHERE active = true');
    return Response.json(users);
}
""")

        context = AnalysisContext(
            project_root=project_root,
            config=config,
            file_paths=[route_file],
        )

        violations = analyzer.analyze(context)

        # Should detect SQL in presentation layer
        db_violations = [v for v in violations if v.type == "DirectDatabaseAccess"]
        assert len(db_violations) > 0
        assert db_violations[0].severity == "CRITICAL"
        assert "SQL" in db_violations[0].message


def test_orm_usage_detection(analyzer, config):
    """Test detection of ORM usage in business layer."""
    with TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)
        (project_root / "lib" / "services").mkdir(parents=True)

        # Create service with ORM usage
        service_file = project_root / "lib" / "services" / "user_service.py"
        service_file.write_text("""
class UserService:
    def get_users(self):
        return User.query.filter(active=True).all()
""")

        context = AnalysisContext(
            project_root=project_root,
            config=config,
            file_paths=[service_file],
        )

        violations = analyzer.analyze(context)

        # Should detect ORM usage in business layer
        db_violations = [v for v in violations if v.type == "DirectDatabaseAccess"]
        assert len(db_violations) > 0
        assert db_violations[0].severity == "HIGH"


def test_database_import_detection(analyzer, config):
    """Test detection of database imports in presentation layer."""
    with TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)
        (project_root / "app" / "api").mkdir(parents=True)

        # Create route with database import
        route_file = project_root / "app" / "api" / "route.py"
        route_file.write_text("""
from database import db_client
from models import User

def get_users():
    return []
""")

        context = AnalysisContext(
            project_root=project_root,
            config=config,
            file_paths=[route_file],
        )

        violations = analyzer.analyze(context)

        # Should detect database import
        db_violations = [v for v in violations if v.type == "DirectDatabaseAccess"]
        assert len(db_violations) > 0
        assert db_violations[0].severity == "MEDIUM"


def test_layer_dependency_violation(analyzer, config):
    """Test detection of wrong-direction layer dependencies."""
    with TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)
        (project_root / "lib" / "services").mkdir(parents=True)
        (project_root / "app" / "components").mkdir(parents=True)

        # Create files
        service_file = project_root / "lib" / "services" / "service.py"
        service_file.write_text("class Service: pass")

        component_file = project_root / "app" / "components" / "component.py"
        component_file.write_text("class Component: pass")

        # Create graph with wrong-direction dependency
        # business -> presentation (not allowed)
        graph = DependencyGraph()
        graph.add_dependency(
            "lib/services/service.py",
            "app/components/component.py"
        )

        context = AnalysisContext(
            project_root=project_root,
            config=config,
            file_paths=[service_file, component_file],
            dependency_graph=graph,
        )

        violations = analyzer.analyze(context)

        # Should detect layer violation
        layer_violations = [v for v in violations if v.type == "LayerViolation"]
        assert len(layer_violations) > 0
        assert layer_violations[0].severity == "HIGH"
        assert "business -> presentation" in layer_violations[0].message


def test_custom_layer_definitions(analyzer):
    """Test analyzer with custom layer definitions."""
    config = AssessmentConfig()

    # Define custom layers
    config.project.custom_layers = [
        LayerDefinition(
            name="api",
            patterns=["api/"],
            allowed_dependencies=["core"],
        ),
        LayerDefinition(
            name="core",
            patterns=["core/"],
            allowed_dependencies=[],
        ),
    ]

    with TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)
        (project_root / "api").mkdir()
        (project_root / "core").mkdir()

        api_file = project_root / "api" / "routes.py"
        api_file.write_text("from core import utils")

        core_file = project_root / "core" / "utils.py"
        core_file.write_text("def helper(): pass")

        context = AnalysisContext(
            project_root=project_root,
            config=config,
            file_paths=[api_file, core_file],
        )

        # Run analysis
        analyzer.analyze(context)

        # Check custom layer classification
        assert "api/routes.py" in analyzer._file_layers
        assert analyzer._file_layers["api/routes.py"] == "api"


def test_python_fastapi_layers(analyzer):
    """Test layer classification for Python/FastAPI projects."""
    config = AssessmentConfig()
    config.project.project_type = "fastapi"

    with TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)
        (project_root / "routers").mkdir()
        (project_root / "services").mkdir()
        (project_root / "repositories").mkdir()

        router_file = project_root / "routers" / "users.py"
        router_file.write_text("from fastapi import APIRouter")

        service_file = project_root / "services" / "user_service.py"
        service_file.write_text("class UserService: pass")

        context = AnalysisContext(
            project_root=project_root,
            config=config,
            file_paths=[router_file, service_file],
        )

        analyzer.analyze(context)

        # Check FastAPI-specific layers
        assert analyzer._file_layers.get("routers/users.py") == "presentation"
        assert analyzer._file_layers.get("services/user_service.py") == "business"


def test_no_violations_clean_architecture(analyzer, config):
    """Test analyzer with clean architecture (no violations)."""
    with TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)
        (project_root / "app" / "api").mkdir(parents=True)
        (project_root / "lib" / "repositories").mkdir(parents=True)

        # Create clean files
        route_file = project_root / "app" / "api" / "route.py"
        route_file.write_text("""
from lib.services import UserService

def get_users():
    service = UserService()
    return service.get_all()
""")

        repo_file = project_root / "lib" / "repositories" / "user_repo.py"
        repo_file.write_text("""
class UserRepository:
    def find_all(self):
        return db.query('SELECT * FROM users')
""")

        context = AnalysisContext(
            project_root=project_root,
            config=config,
            file_paths=[route_file, repo_file],
        )

        violations = analyzer.analyze(context)

        # No database violations in presentation layer
        # (SQL is in data layer, which is allowed)
        db_in_presentation = [
            v for v in violations
            if v.type == "DirectDatabaseAccess"
            and "app/" in v.file_path
        ]
        assert len(db_in_presentation) == 0


def test_violation_metadata(analyzer, config):
    """Test that violations include proper metadata."""
    with TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)
        (project_root / "app" / "api").mkdir(parents=True)

        route_file = project_root / "app" / "api" / "route.py"
        route_file.write_text("result = db.execute('SELECT * FROM users')")

        context = AnalysisContext(
            project_root=project_root,
            config=config,
            file_paths=[route_file],
        )

        violations = analyzer.analyze(context)

        assert len(violations) > 0
        violation = violations[0]

        # Check metadata
        assert "layer" in violation.metadata
        assert "pattern_type" in violation.metadata

        # Check violation structure
        assert violation.dimension == "layer"
        assert violation.id.startswith("LSV-")
        assert violation.line_number is not None
        assert violation.recommendation != ""
