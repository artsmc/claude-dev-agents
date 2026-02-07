"""Layer separation analyzer for architecture quality assessment.

This module analyzes architectural layer separation, detecting violations
of clean architecture principles, wrong-direction dependencies, and
database access in inappropriate layers.

References:
    - TR.md Section 2.2.3: Layer Separation Analysis
    - FRS.md FR-2.1: Database Access Detection
    - FRS.md FR-2.2: Clean Architecture Dependency Rules
    - FRS.md FR-2.3: Module Boundary Detection
"""

import logging
import re
from pathlib import Path
from typing import Dict, List, Optional, Set

from ..graph.dependency_graph import DependencyGraph
from ..models.config import AssessmentConfig, LayerDefinition
from .base import AnalysisContext, BaseAnalyzer
from ..models.violation import Violation


logger = logging.getLogger(__name__)


# Standard layer definitions for different project types
NEXTJS_LAYERS = [
    LayerDefinition(
        name="presentation",
        patterns=["app/", "pages/", "components/"],
        allowed_dependencies=["business", "infrastructure"],
        description="UI components, API routes, and page handlers",
    ),
    LayerDefinition(
        name="business",
        patterns=["lib/services/", "lib/use-cases/", "services/"],
        allowed_dependencies=["data", "infrastructure"],
        description="Business logic and application services",
    ),
    LayerDefinition(
        name="data",
        patterns=["lib/repositories/", "repositories/", "lib/data/"],
        allowed_dependencies=["infrastructure"],
        description="Data access layer and repository pattern",
    ),
    LayerDefinition(
        name="infrastructure",
        patterns=["lib/db/", "lib/config/", "lib/utils/", "config/", "utils/"],
        allowed_dependencies=[],
        description="Database clients, configuration, utilities",
    ),
]

PYTHON_FASTAPI_LAYERS = [
    LayerDefinition(
        name="presentation",
        patterns=["routers/", "api/", "routes/"],
        allowed_dependencies=["business", "infrastructure"],
        description="API route handlers and request/response models",
    ),
    LayerDefinition(
        name="business",
        patterns=["services/", "use_cases/", "domain/"],
        allowed_dependencies=["data", "infrastructure"],
        description="Business logic and domain models",
    ),
    LayerDefinition(
        name="data",
        patterns=["repositories/", "models/", "db/models/"],
        allowed_dependencies=["infrastructure"],
        description="Data access layer and ORM models",
    ),
    LayerDefinition(
        name="infrastructure",
        patterns=["db/", "config/", "utils/", "core/"],
        allowed_dependencies=[],
        description="Database setup, configuration, utilities",
    ),
]

# Database-related patterns for detection
DATABASE_PATTERNS = {
    "sql_queries": [
        r"SELECT\s+.*\s+FROM\s+",
        r"INSERT\s+INTO\s+",
        r"UPDATE\s+.*\s+SET\s+",
        r"DELETE\s+FROM\s+",
        r"CREATE\s+TABLE\s+",
        r"ALTER\s+TABLE\s+",
    ],
    "orm_usage": [
        r"\.query\(",
        r"\.filter\(",
        r"\.all\(\)",
        r"\.first\(\)",
        r"\.session\.",
        r"session\.query",
        r"db\.execute",
        r"prisma\.",
        r"\.findMany\(",
        r"\.findUnique\(",
        r"\.create\(",
        r"\.update\(",
        r"\.delete\(",
    ],
    "db_imports": [
        r"from\s+.*database.*\s+import",
        r"from\s+.*db.*\s+import",
        r"from\s+.*prisma.*\s+import",
        r"from\s+.*sqlalchemy.*\s+import",
        r"import\s+.*database",
        r"import\s+.*prisma",
        r"import\s+mysql",
        r"import\s+psycopg",
        r"import\s+pymongo",
    ],
}


class LayerAnalyzer(BaseAnalyzer):
    """Analyzes architectural layer separation and boundaries.

    Detects violations of layer separation principles including:
    - Wrong-direction dependencies (inner layers depending on outer)
    - Direct database access in presentation/business layers
    - Cross-module boundary violations
    - Missing layer separation in general

    The analyzer supports both framework-specific layer definitions
    and custom user-defined layers.

    Example:
        >>> analyzer = LayerAnalyzer()
        >>> context = AnalysisContext(
        ...     project_root=Path("/path/to/project"),
        ...     config=config,
        ...     file_paths=all_files
        ... )
        >>> violations = analyzer.analyze(context)
    """

    def __init__(self):
        """Initialize the layer analyzer."""
        super().__init__()
        self._file_layers: Dict[str, str] = {}
        self._layer_definitions: List[LayerDefinition] = []

    def get_name(self) -> str:
        """Get analyzer identifier.

        Returns:
            "layer"
        """
        return "layer"

    def get_description(self) -> str:
        """Get human-readable description.

        Returns:
            Description of layer analysis functionality.
        """
        return (
            "Analyzes architectural layer separation, validates clean architecture "
            "dependency rules, and detects database access in inappropriate layers"
        )

    def analyze(self, context: AnalysisContext) -> List[Violation]:
        """Perform layer separation analysis on the project.

        Args:
            context: Analysis context with project files and configuration.

        Returns:
            List of layer separation violations detected.
        """
        violations = []

        self.log_progress("Starting layer separation analysis")

        # Determine layer definitions to use
        self._layer_definitions = self._get_layer_definitions(context)

        # Classify all files into layers
        self._classify_files(context)

        # Detect database access violations
        violations.extend(self._analyze_database_access(context))

        # Analyze layer dependency violations
        if context.dependency_graph:
            violations.extend(
                self._analyze_layer_dependencies(context.dependency_graph, context)
            )

        self.log_progress(
            f"Layer analysis complete: {len(violations)} violations found"
        )

        return violations

    def _get_layer_definitions(
        self, context: AnalysisContext
    ) -> List[LayerDefinition]:
        """Get layer definitions based on project type or custom config.

        Args:
            context: Analysis context with configuration.

        Returns:
            List of layer definitions to use for analysis.
        """
        # Use custom layers if defined
        if context.config.project.custom_layers:
            self.log_progress("Using custom layer definitions")
            return context.config.project.custom_layers

        # Otherwise use framework-specific defaults
        project_type = context.config.project.project_type.lower()

        if "nextjs" in project_type or "next.js" in project_type:
            self.log_progress("Using Next.js layer definitions")
            return NEXTJS_LAYERS
        elif "fastapi" in project_type or "python" in project_type:
            self.log_progress("Using Python/FastAPI layer definitions")
            return PYTHON_FASTAPI_LAYERS
        else:
            # Generic layers for unknown project types
            self.log_progress("Using generic layer definitions")
            return [
                LayerDefinition(
                    name="presentation",
                    patterns=["routes/", "handlers/", "controllers/", "views/"],
                    allowed_dependencies=["business", "infrastructure"],
                ),
                LayerDefinition(
                    name="business",
                    patterns=["services/", "domain/", "logic/"],
                    allowed_dependencies=["data", "infrastructure"],
                ),
                LayerDefinition(
                    name="data",
                    patterns=["repositories/", "models/", "data/"],
                    allowed_dependencies=["infrastructure"],
                ),
                LayerDefinition(
                    name="infrastructure",
                    patterns=["config/", "utils/", "lib/"],
                    allowed_dependencies=[],
                ),
            ]

    def _classify_files(self, context: AnalysisContext) -> None:
        """Classify all project files into layers.

        Args:
            context: Analysis context with file paths.
        """
        for file_path in context.file_paths:
            if not self.should_analyze_file(file_path, context):
                continue

            # Get relative path for pattern matching
            rel_path = str(file_path.relative_to(context.project_root))

            # Find matching layer
            layer = self._classify_file(rel_path)
            if layer:
                self._file_layers[rel_path] = layer

    def _classify_file(self, file_path: str) -> Optional[str]:
        """Classify a single file into a layer.

        Args:
            file_path: Relative file path to classify.

        Returns:
            Layer name if matched, None otherwise.
        """
        for layer_def in self._layer_definitions:
            for pattern in layer_def.patterns:
                if pattern in file_path:
                    return layer_def.name

        return None

    def _analyze_database_access(
        self, context: AnalysisContext
    ) -> List[Violation]:
        """Detect direct database access in inappropriate layers.

        Args:
            context: Analysis context.

        Returns:
            List of database access violations.
        """
        violations = []

        # Only check presentation and business layers
        forbidden_layers = {"presentation", "business"}

        for file_path in context.file_paths:
            if not self.should_analyze_file(file_path, context):
                continue

            rel_path = str(file_path.relative_to(context.project_root))
            layer = self._file_layers.get(rel_path)

            if layer not in forbidden_layers:
                continue

            # Check file contents for database patterns
            try:
                content = file_path.read_text(encoding="utf-8")
                violations.extend(
                    self._check_database_patterns(
                        file_path, rel_path, layer, content
                    )
                )
            except (UnicodeDecodeError, IOError) as e:
                self.logger.debug(f"Could not read file {file_path}: {e}")
                continue

        return violations

    def _check_database_patterns(
        self, file_path: Path, rel_path: str, layer: str, content: str
    ) -> List[Violation]:
        """Check file content for database access patterns.

        Args:
            file_path: Absolute file path.
            rel_path: Relative file path.
            layer: Layer the file belongs to.
            content: File content to check.

        Returns:
            List of violations found.
        """
        violations = []

        # Check for SQL queries
        for pattern in DATABASE_PATTERNS["sql_queries"]:
            matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                line_number = content[:match.start()].count('\n') + 1
                violation = self.create_violation(
                    type_prefix="LSV",
                    violation_type="DirectDatabaseAccess",
                    severity="CRITICAL",
                    file_path=rel_path,
                    line_number=line_number,
                    message=f"Direct SQL query in {layer} layer",
                    explanation=(
                        f"A SQL query was detected in the {layer} layer. "
                        f"Direct database access violates layer separation principles "
                        f"and makes code harder to test and maintain."
                    ),
                    recommendation=(
                        "Move database access to the data layer:\n"
                        "- Create a repository class in the data layer\n"
                        "- Inject the repository into this service/handler\n"
                        "- Keep business/presentation layers database-agnostic"
                    ),
                    metadata={
                        "layer": layer,
                        "pattern_type": "sql_query",
                        "matched_text": match.group(0)[:50],
                    },
                )
                violations.append(violation)
                # Only report first occurrence per file
                break

        # Check for ORM usage
        if not violations:  # Only check if we haven't found SQL
            for pattern in DATABASE_PATTERNS["orm_usage"]:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    line_number = content[:match.start()].count('\n') + 1
                    violation = self.create_violation(
                        type_prefix="LSV",
                        violation_type="DirectDatabaseAccess",
                        severity="HIGH",
                        file_path=rel_path,
                        line_number=line_number,
                        message=f"Direct ORM usage in {layer} layer",
                        explanation=(
                            f"Direct ORM usage was detected in the {layer} layer. "
                            f"Database operations should be encapsulated in the data layer "
                            f"following the Repository pattern."
                        ),
                        recommendation=(
                            "Refactor database access:\n"
                            "- Create repository methods for data operations\n"
                            "- Use dependency injection to provide repositories\n"
                            "- Keep ORM models and queries in the data layer only"
                        ),
                        metadata={
                            "layer": layer,
                            "pattern_type": "orm_usage",
                            "matched_text": match.group(0),
                        },
                    )
                    violations.append(violation)
                    break

        # Check for database imports
        if not violations:  # Only check if we haven't found direct access
            for pattern in DATABASE_PATTERNS["db_imports"]:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    line_number = content[:match.start()].count('\n') + 1
                    violation = self.create_violation(
                        type_prefix="LSV",
                        violation_type="DirectDatabaseAccess",
                        severity="MEDIUM",
                        file_path=rel_path,
                        line_number=line_number,
                        message=f"Database import in {layer} layer",
                        explanation=(
                            f"A database-related import was found in the {layer} layer. "
                            f"This suggests potential direct database access and layer violation."
                        ),
                        recommendation=(
                            "Remove direct database dependencies:\n"
                            "- Import only repository interfaces, not database clients\n"
                            "- Use dependency injection for data access\n"
                            "- Keep database imports in the data/infrastructure layers"
                        ),
                        metadata={
                            "layer": layer,
                            "pattern_type": "db_import",
                            "matched_text": match.group(0),
                        },
                    )
                    violations.append(violation)
                    break

        return violations

    def _analyze_layer_dependencies(
        self,
        graph: DependencyGraph,
        context: AnalysisContext,
    ) -> List[Violation]:
        """Analyze dependencies between layers for violations.

        Args:
            graph: Dependency graph.
            context: Analysis context.

        Returns:
            List of layer dependency violations.
        """
        violations = []

        # Create a mapping of layer names to allowed dependencies
        layer_rules = {
            layer_def.name: set(layer_def.allowed_dependencies)
            for layer_def in self._layer_definitions
        }

        # Check each dependency edge
        for node in graph.get_internal_nodes():
            from_file = node.module_path
            from_layer = self._file_layers.get(from_file)

            if not from_layer:
                continue

            allowed_deps = layer_rules.get(from_layer, set())

            for dep in node.dependencies:
                to_layer = self._file_layers.get(dep)

                if not to_layer:
                    continue

                # Check if this dependency is allowed
                if to_layer not in allowed_deps and to_layer != from_layer:
                    violation = self.create_violation(
                        type_prefix="LSV",
                        violation_type="LayerViolation",
                        severity="HIGH",
                        file_path=from_file,
                        message=(
                            f"Invalid layer dependency: {from_layer} -> {to_layer}"
                        ),
                        explanation=(
                            f"File in {from_layer} layer depends on file in {to_layer} layer, "
                            f"violating clean architecture dependency rules. "
                            f"The {from_layer} layer is only allowed to depend on: "
                            f"{', '.join(sorted(allowed_deps)) if allowed_deps else 'none'}."
                        ),
                        recommendation=(
                            "Fix the layer dependency violation:\n"
                            f"- Move shared code from {to_layer} to an allowed layer\n"
                            "- Invert the dependency using interfaces/abstractions\n"
                            "- Refactor to follow clean architecture principles\n"
                            "- Consider if the file is in the wrong layer"
                        ),
                        metadata={
                            "from_layer": from_layer,
                            "to_layer": to_layer,
                            "from_file": from_file,
                            "to_file": dep,
                            "allowed_dependencies": list(allowed_deps),
                        },
                    )
                    violations.append(violation)

        return violations


__all__ = ["LayerAnalyzer"]
