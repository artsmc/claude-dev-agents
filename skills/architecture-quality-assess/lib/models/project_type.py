"""Project type enumeration for architecture quality assessment.

Defines supported project types and provides helper methods for
framework-specific detection patterns and display names.

References:
    - FRS.md FR-1.1: Multi-Language Support
    - FRS.md FR-1.2: Framework-Specific Patterns
    - TR.md Section 3.1: Core Data Structures
"""

from enum import Enum


class ProjectType(str, Enum):
    """Supported project types for architecture analysis.

    Uses str mixin to enable direct JSON serialization of enum values.
    Each member's value is a lowercase, hyphenated identifier suitable
    for use in configuration files and CLI arguments.

    Attributes:
        NEXTJS: Next.js (App Router or Pages Router)
        REACT: React (standalone, no Next.js)
        VUE: Vue.js or Nuxt.js
        ANGULAR: Angular framework
        PYTHON_FASTAPI: Python with FastAPI framework
        PYTHON_DJANGO: Python with Django framework
        PYTHON_FLASK: Python with Flask framework
        NODEJS_EXPRESS: Node.js with Express framework
        NODEJS_NESTJS: Node.js with NestJS framework
        UNKNOWN: Unrecognized or generic project type
    """

    NEXTJS = "nextjs"
    REACT = "react"
    VUE = "vue"
    ANGULAR = "angular"
    PYTHON_FASTAPI = "python-fastapi"
    PYTHON_DJANGO = "python-django"
    PYTHON_FLASK = "python-flask"
    NODEJS_EXPRESS = "nodejs-express"
    NODEJS_NESTJS = "nodejs-nestjs"
    UNKNOWN = "unknown"

    def get_display_name(self) -> str:
        """Get human-readable display name for this project type.

        Returns:
            A formatted string suitable for display in reports and CLI output.

        Examples:
            >>> ProjectType.NEXTJS.get_display_name()
            'Next.js'
            >>> ProjectType.PYTHON_FASTAPI.get_display_name()
            'FastAPI'
        """
        display_names: dict["ProjectType", str] = {
            ProjectType.NEXTJS: "Next.js",
            ProjectType.REACT: "React",
            ProjectType.VUE: "Vue",
            ProjectType.ANGULAR: "Angular",
            ProjectType.PYTHON_FASTAPI: "FastAPI",
            ProjectType.PYTHON_DJANGO: "Django",
            ProjectType.PYTHON_FLASK: "Flask",
            ProjectType.NODEJS_EXPRESS: "Express.js",
            ProjectType.NODEJS_NESTJS: "NestJS",
            ProjectType.UNKNOWN: "Unknown",
        }
        return display_names[self]

    def get_expected_patterns(self) -> list[str]:
        """Get expected file and directory patterns for this project type.

        Returns a list of glob-style patterns that are characteristic of
        this project type. Used by the project type detector to identify
        frameworks and by the directory structure validator (FR-6.1) to
        verify conventional layouts.

        Returns:
            List of file/directory patterns (glob-style strings).
            Returns an empty list for UNKNOWN project type.

        Examples:
            >>> ProjectType.NEXTJS.get_expected_patterns()
            ['next.config.js', 'next.config.mjs', 'next.config.ts', 'app/', 'pages/', 'public/']
        """
        patterns: dict["ProjectType", list[str]] = {
            ProjectType.NEXTJS: [
                "next.config.js",
                "next.config.mjs",
                "next.config.ts",
                "app/",
                "pages/",
                "public/",
                "components/",
                "lib/",
            ],
            ProjectType.REACT: [
                "package.json",
                "src/",
                "src/App.tsx",
                "src/App.jsx",
                "src/index.tsx",
                "src/index.jsx",
                "public/index.html",
            ],
            ProjectType.VUE: [
                "package.json",
                "vue.config.js",
                "nuxt.config.js",
                "nuxt.config.ts",
                "src/",
                "src/App.vue",
                "src/main.ts",
                "src/main.js",
                "components/",
            ],
            ProjectType.ANGULAR: [
                "angular.json",
                "package.json",
                "tsconfig.json",
                "src/app/",
                "src/app/app.module.ts",
                "src/app/app.component.ts",
                "src/environments/",
            ],
            ProjectType.PYTHON_FASTAPI: [
                "requirements.txt",
                "pyproject.toml",
                "app/",
                "app/main.py",
                "app/routers/",
                "app/services/",
                "app/models/",
                "app/schemas/",
            ],
            ProjectType.PYTHON_DJANGO: [
                "requirements.txt",
                "pyproject.toml",
                "manage.py",
                "settings.py",
                "urls.py",
                "wsgi.py",
                "asgi.py",
            ],
            ProjectType.PYTHON_FLASK: [
                "requirements.txt",
                "pyproject.toml",
                "app.py",
                "app/__init__.py",
                "templates/",
                "static/",
            ],
            ProjectType.NODEJS_EXPRESS: [
                "package.json",
                "app.js",
                "server.js",
                "routes/",
                "controllers/",
                "middleware/",
                "models/",
            ],
            ProjectType.NODEJS_NESTJS: [
                "package.json",
                "nest-cli.json",
                "tsconfig.json",
                "src/main.ts",
                "src/app.module.ts",
                "src/app.controller.ts",
                "src/app.service.ts",
            ],
            ProjectType.UNKNOWN: [],
        }
        return patterns[self]

    def is_python(self) -> bool:
        """Check if this project type uses Python as its primary language.

        Returns:
            True if the project type is a Python-based framework.

        Examples:
            >>> ProjectType.PYTHON_FASTAPI.is_python()
            True
            >>> ProjectType.NEXTJS.is_python()
            False
        """
        return self in (
            ProjectType.PYTHON_FASTAPI,
            ProjectType.PYTHON_DJANGO,
            ProjectType.PYTHON_FLASK,
        )

    def is_javascript(self) -> bool:
        """Check if this project type uses JavaScript/TypeScript as its primary language.

        Returns:
            True if the project type is a JavaScript/TypeScript-based framework.

        Examples:
            >>> ProjectType.NEXTJS.is_javascript()
            True
            >>> ProjectType.PYTHON_FASTAPI.is_javascript()
            False
        """
        return self in (
            ProjectType.NEXTJS,
            ProjectType.REACT,
            ProjectType.VUE,
            ProjectType.ANGULAR,
            ProjectType.NODEJS_EXPRESS,
            ProjectType.NODEJS_NESTJS,
        )
