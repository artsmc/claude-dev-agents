#!/usr/bin/env python3
"""Project type detection script for architecture quality assessment.

Analyzes a project directory to determine its type (Next.js, FastAPI, Django, etc.)
and framework-specific patterns (e.g., Next.js App Router vs Pages Router).

Usage:
    python detect_project_type.py <project_path>
    python detect_project_type.py <project_path> --json

References:
    - TR.md Section 2.2.1: Project Type Detection
    - FRS.md FR-1.1: Multi-Language Support
    - FRS.md FR-1.2: Framework-Specific Patterns
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.models.project_type import ProjectType


logging.basicConfig(
    level=logging.INFO, format="%(levelname)s: %(message)s"
)
logger = logging.getLogger(__name__)


class ProjectTypeDetector:
    """Detects project type and framework-specific patterns."""

    def __init__(self, project_path: Path):
        """Initialize detector with project path.

        Args:
            project_path: Root directory of the project to analyze.
        """
        self.project_path = project_path.resolve()
        self.detected_types: List[ProjectType] = []
        self.patterns: Dict[str, Any] = {}

    def detect(self) -> Dict[str, Any]:
        """Detect project type and patterns.

        Returns:
            Dictionary containing:
                - type: Primary project type (ProjectType enum value)
                - display_name: Human-readable project type name
                - languages: List of detected languages
                - frameworks: List of detected frameworks
                - patterns: Framework-specific patterns detected
                - confidence: Confidence score (0.0-1.0)
        """
        if not self.project_path.exists():
            logger.error(f"Project path does not exist: {self.project_path}")
            return self._result(ProjectType.UNKNOWN, 0.0)

        if not self.project_path.is_dir():
            logger.error(f"Project path is not a directory: {self.project_path}")
            return self._result(ProjectType.UNKNOWN, 0.0)

        # Check for JavaScript/TypeScript frameworks
        if self._is_nextjs():
            return self._result(ProjectType.NEXTJS, 0.95)
        elif self._is_nestjs():
            return self._result(ProjectType.NODEJS_NESTJS, 0.90)
        elif self._is_express():
            return self._result(ProjectType.NODEJS_EXPRESS, 0.85)
        elif self._is_angular():
            return self._result(ProjectType.ANGULAR, 0.90)
        elif self._is_vue():
            return self._result(ProjectType.VUE, 0.85)
        elif self._is_react():
            return self._result(ProjectType.REACT, 0.80)

        # Check for Python frameworks
        elif self._is_django():
            return self._result(ProjectType.PYTHON_DJANGO, 0.95)
        elif self._is_fastapi():
            return self._result(ProjectType.PYTHON_FASTAPI, 0.90)
        elif self._is_flask():
            return self._result(ProjectType.PYTHON_FLASK, 0.85)

        # Fallback: detect generic Python or JavaScript
        elif self._has_python_files():
            return self._result(ProjectType.UNKNOWN, 0.50, languages=["python"])
        elif self._has_javascript_files():
            return self._result(ProjectType.UNKNOWN, 0.50, languages=["javascript"])

        # No recognizable pattern
        return self._result(ProjectType.UNKNOWN, 0.0)

    def _is_nextjs(self) -> bool:
        """Detect Next.js project.

        Returns:
            True if this is a Next.js project.
        """
        # Check for Next.js config files
        config_files = [
            "next.config.js",
            "next.config.mjs",
            "next.config.ts",
        ]

        for config_file in config_files:
            if (self.project_path / config_file).exists():
                # Check for App Router vs Pages Router
                app_dir = self.project_path / "app"
                pages_dir = self.project_path / "pages"

                if app_dir.exists() and app_dir.is_dir():
                    self.patterns["router_type"] = "app_router"
                    self.patterns["has_app_directory"] = True
                elif pages_dir.exists() and pages_dir.is_dir():
                    self.patterns["router_type"] = "pages_router"
                    self.patterns["has_pages_directory"] = True
                else:
                    self.patterns["router_type"] = "unknown"

                # Check for common Next.js directories
                self.patterns["has_public"] = (self.project_path / "public").exists()
                self.patterns["has_components"] = (
                    self.project_path / "components"
                ).exists()
                self.patterns["has_lib"] = (self.project_path / "lib").exists()

                return True

        # Check package.json for "next" dependency
        if self._check_package_json_dependency("next"):
            self.patterns["router_type"] = "unknown"
            return True

        return False

    def _is_react(self) -> bool:
        """Detect standalone React project (no Next.js).

        Returns:
            True if this is a React project.
        """
        # Must have package.json with React, but not Next.js
        if not self._check_package_json_dependency("react"):
            return False

        if self._check_package_json_dependency("next"):
            return False

        # Check for typical React project structure
        src_dir = self.project_path / "src"
        if src_dir.exists():
            app_files = ["App.tsx", "App.jsx", "App.js"]
            for app_file in app_files:
                if (src_dir / app_file).exists():
                    self.patterns["has_src"] = True
                    self.patterns["entry_point"] = app_file
                    return True

        # Check for CRA structure
        public_dir = self.project_path / "public"
        if public_dir.exists() and (public_dir / "index.html").exists():
            self.patterns["structure"] = "create-react-app"
            return True

        return False

    def _is_vue(self) -> bool:
        """Detect Vue.js or Nuxt.js project.

        Returns:
            True if this is a Vue/Nuxt project.
        """
        # Check for Vue config files
        config_files = ["vue.config.js", "nuxt.config.js", "nuxt.config.ts"]

        for config_file in config_files:
            if (self.project_path / config_file).exists():
                if "nuxt" in config_file:
                    self.patterns["framework"] = "nuxt"
                else:
                    self.patterns["framework"] = "vue"
                return True

        # Check package.json
        if self._check_package_json_dependency("nuxt"):
            self.patterns["framework"] = "nuxt"
            return True
        elif self._check_package_json_dependency("vue"):
            self.patterns["framework"] = "vue"
            return True

        return False

    def _is_angular(self) -> bool:
        """Detect Angular project.

        Returns:
            True if this is an Angular project.
        """
        # Angular projects must have angular.json
        if not (self.project_path / "angular.json").exists():
            return False

        # Check for typical Angular structure
        src_app = self.project_path / "src" / "app"
        if src_app.exists():
            self.patterns["has_src_app"] = True
            if (src_app / "app.module.ts").exists():
                self.patterns["has_app_module"] = True
            if (src_app / "app.component.ts").exists():
                self.patterns["has_app_component"] = True

        return True

    def _is_django(self) -> bool:
        """Detect Django project.

        Returns:
            True if this is a Django project.
        """
        # Check for manage.py
        if not (self.project_path / "manage.py").exists():
            return False

        # Look for Django-specific files
        django_files = ["settings.py", "urls.py", "wsgi.py", "asgi.py"]
        found_files = []

        for file_path in self.project_path.rglob("*.py"):
            if file_path.name in django_files:
                found_files.append(file_path.name)

        if len(found_files) >= 2:
            self.patterns["found_django_files"] = found_files
            # Check for apps structure
            self.patterns["has_apps"] = self._find_django_apps()
            return True

        return False

    def _is_fastapi(self) -> bool:
        """Detect FastAPI project.

        Returns:
            True if this is a FastAPI project.
        """
        # Check for FastAPI in requirements
        if self._check_python_dependency("fastapi"):
            # Look for typical FastAPI structure
            app_dir = self.project_path / "app"
            if app_dir.exists():
                self.patterns["has_app_dir"] = True

                # Check for routers
                if (app_dir / "routers").exists():
                    self.patterns["has_routers"] = True

                # Check for main.py
                if (app_dir / "main.py").exists():
                    self.patterns["entry_point"] = "app/main.py"

            return True

        # Check for FastAPI import in Python files
        if self._find_import_in_python_files("fastapi"):
            self.patterns["detected_via_imports"] = True
            return True

        return False

    def _is_flask(self) -> bool:
        """Detect Flask project.

        Returns:
            True if this is a Flask project.
        """
        # Check for Flask in requirements
        if self._check_python_dependency("flask"):
            # Look for typical Flask files
            if (self.project_path / "app.py").exists():
                self.patterns["entry_point"] = "app.py"
            elif (self.project_path / "app" / "__init__.py").exists():
                self.patterns["entry_point"] = "app/__init__.py"

            # Check for Flask structure
            if (self.project_path / "templates").exists():
                self.patterns["has_templates"] = True
            if (self.project_path / "static").exists():
                self.patterns["has_static"] = True

            return True

        # Check for Flask import
        if self._find_import_in_python_files("flask"):
            self.patterns["detected_via_imports"] = True
            return True

        return False

    def _is_express(self) -> bool:
        """Detect Express.js project.

        Returns:
            True if this is an Express project.
        """
        # Check for Express in package.json
        if not self._check_package_json_dependency("express"):
            return False

        # Look for typical Express structure
        entry_points = ["app.js", "server.js", "index.js"]
        for entry in entry_points:
            if (self.project_path / entry).exists():
                self.patterns["entry_point"] = entry
                break

        # Check for common directories
        if (self.project_path / "routes").exists():
            self.patterns["has_routes"] = True
        if (self.project_path / "controllers").exists():
            self.patterns["has_controllers"] = True
        if (self.project_path / "middleware").exists():
            self.patterns["has_middleware"] = True

        return True

    def _is_nestjs(self) -> bool:
        """Detect NestJS project.

        Returns:
            True if this is a NestJS project.
        """
        # NestJS projects have nest-cli.json
        if not (self.project_path / "nest-cli.json").exists():
            # Fallback: check package.json
            if not self._check_package_json_dependency("@nestjs/core"):
                return False

        # Check for typical NestJS structure
        src_dir = self.project_path / "src"
        if src_dir.exists():
            self.patterns["has_src"] = True

            if (src_dir / "main.ts").exists():
                self.patterns["entry_point"] = "src/main.ts"
            if (src_dir / "app.module.ts").exists():
                self.patterns["has_app_module"] = True
            if (src_dir / "app.controller.ts").exists():
                self.patterns["has_app_controller"] = True
            if (src_dir / "app.service.ts").exists():
                self.patterns["has_app_service"] = True

        return True

    def _check_package_json_dependency(self, dependency: str) -> bool:
        """Check if a dependency exists in package.json.

        Args:
            dependency: Name of the npm package to check.

        Returns:
            True if the dependency is found in dependencies or devDependencies.
        """
        package_json = self.project_path / "package.json"
        if not package_json.exists():
            return False

        try:
            import json as json_lib

            with package_json.open() as f:
                data = json_lib.load(f)

            dependencies = data.get("dependencies", {})
            dev_dependencies = data.get("devDependencies", {})

            return dependency in dependencies or dependency in dev_dependencies
        except (json.JSONDecodeError, KeyError):
            return False

    def _check_python_dependency(self, dependency: str) -> bool:
        """Check if a Python dependency exists in requirements.txt or pyproject.toml.

        Args:
            dependency: Name of the Python package to check.

        Returns:
            True if the dependency is found.
        """
        # Check requirements.txt
        requirements = self.project_path / "requirements.txt"
        if requirements.exists():
            try:
                content = requirements.read_text()
                if dependency.lower() in content.lower():
                    return True
            except (IOError, UnicodeDecodeError):
                pass

        # Check pyproject.toml
        pyproject = self.project_path / "pyproject.toml"
        if pyproject.exists():
            try:
                content = pyproject.read_text()
                if dependency.lower() in content.lower():
                    return True
            except (IOError, UnicodeDecodeError):
                pass

        return False

    def _find_import_in_python_files(self, module_name: str) -> bool:
        """Search for import statement in Python files.

        Args:
            module_name: Module name to search for.

        Returns:
            True if the import is found in any Python file.
        """
        # Search top-level Python files only (performance)
        for py_file in self.project_path.glob("*.py"):
            try:
                content = py_file.read_text()
                if f"import {module_name}" in content or f"from {module_name}" in content:
                    return True
            except (IOError, UnicodeDecodeError):
                continue

        # Also check app/ directory if it exists
        app_dir = self.project_path / "app"
        if app_dir.exists():
            for py_file in app_dir.glob("*.py"):
                try:
                    content = py_file.read_text()
                    if f"import {module_name}" in content or f"from {module_name}" in content:
                        return True
                except (IOError, UnicodeDecodeError):
                    continue

        return False

    def _find_django_apps(self) -> List[str]:
        """Find Django apps in the project.

        Returns:
            List of app directory names.
        """
        apps = []
        for item in self.project_path.iterdir():
            if item.is_dir() and not item.name.startswith("."):
                # Django apps typically have models.py or apps.py
                if (item / "models.py").exists() or (item / "apps.py").exists():
                    apps.append(item.name)
        return apps

    def _has_python_files(self) -> bool:
        """Check if project contains Python files.

        Returns:
            True if .py files are found.
        """
        for _ in self.project_path.rglob("*.py"):
            return True
        return False

    def _has_javascript_files(self) -> bool:
        """Check if project contains JavaScript/TypeScript files.

        Returns:
            True if .js, .jsx, .ts, or .tsx files are found.
        """
        for ext in ["*.js", "*.jsx", "*.ts", "*.tsx"]:
            for _ in self.project_path.rglob(ext):
                return True
        return False

    def _result(
        self,
        project_type: ProjectType,
        confidence: float,
        languages: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Build result dictionary.

        Args:
            project_type: Detected project type.
            confidence: Confidence score (0.0-1.0).
            languages: List of detected languages (optional).

        Returns:
            Result dictionary.
        """
        if languages is None:
            if project_type.is_python():
                languages = ["python"]
            elif project_type.is_javascript():
                languages = ["javascript", "typescript"]
            else:
                languages = []

        frameworks = []
        if project_type != ProjectType.UNKNOWN:
            frameworks = [project_type.value]

        return {
            "type": project_type.value,
            "display_name": project_type.get_display_name(),
            "languages": languages,
            "frameworks": frameworks,
            "patterns": self.patterns,
            "confidence": confidence,
            "project_path": str(self.project_path),
        }


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Detect project type and framework patterns"
    )
    parser.add_argument(
        "project_path",
        type=Path,
        help="Path to the project directory to analyze",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results in JSON format",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging",
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    detector = ProjectTypeDetector(args.project_path)
    result = detector.detect()

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"Project Type: {result['display_name']}")
        print(f"Confidence: {result['confidence']:.0%}")
        print(f"Languages: {', '.join(result['languages'])}")
        if result["frameworks"]:
            print(f"Frameworks: {', '.join(result['frameworks'])}")
        if result["patterns"]:
            print("\nDetected Patterns:")
            for key, value in result["patterns"].items():
                print(f"  {key}: {value}")

    sys.exit(0)


def detect_project_type(project_path: str) -> Dict[str, Any]:
    """Convenience function for programmatic usage.

    Args:
        project_path: Path to project directory (string).

    Returns:
        Detection result dictionary.
    """
    detector = ProjectTypeDetector(Path(project_path))
    return detector.detect()


if __name__ == "__main__":
    main()
