#!/usr/bin/env python3
"""Main CLI for architecture quality assessment.

This is the primary entry point for running architecture quality analysis.
It orchestrates:
1. Project detection
2. File parsing
3. Dependency graph construction
4. Analyzer execution
5. Report generation

Usage:
    python assess.py [PROJECT_PATH] [OPTIONS]

Examples:
    # Analyze current directory
    python assess.py

    # Analyze specific project
    python assess.py /path/to/project

    # Generate JSON output for CI/CD
    python assess.py --format json --output assessment.json

    # Show verbose progress
    python assess.py --verbose

    # Only show critical issues
    python assess.py --severity critical
"""

import argparse
import hashlib
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set

# Add parent directory to path for imports
SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
sys.path.insert(0, str(SKILL_DIR))

from lib.analyzers import (
    AnalysisContext,
    get_enabled_analyzers,
    list_analyzer_info,
    run_all_analyzers,
)
from lib.analyzers.base import AnalysisContext
from lib.graph.dependency_graph import DependencyGraph
from lib.models.assessment import AssessmentResult, ProjectInfo
from lib.models.config import AssessmentConfig
from lib.models.metrics import CouplingMetrics, ProjectMetrics, SOLIDMetrics
from lib.models.violation import Violation
from lib.parsers import get_parser_for_file, get_supported_extensions, is_parseable
from lib.parsers.base import ParseResult
from lib.reporters import (
    generate_all_reports,
    generate_ci_summary,
    generate_json_report,
    generate_markdown_report,
    generate_task_list,
)

# Import project detection
sys.path.insert(0, str(SCRIPT_DIR))
from detect_project_type import detect_project_type


# Configure logging
def setup_logging(verbose: bool = False) -> None:
    """Configure logging based on verbosity level."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
    )


logger = logging.getLogger(__name__)


class AssessmentOrchestrator:
    """Main orchestrator for architecture quality assessment.

    Coordinates the full analysis pipeline from file discovery
    through report generation.
    """

    def __init__(
        self,
        project_path: Path,
        config: Optional[AssessmentConfig] = None,
        verbose: bool = False,
        cache_enabled: bool = True,
    ):
        """Initialize the orchestrator.

        Args:
            project_path: Root directory of project to analyze.
            config: Assessment configuration (uses defaults if None).
            verbose: Enable verbose logging.
            cache_enabled: Enable parsing cache.
        """
        self.project_path = project_path.resolve()
        self.config = config or AssessmentConfig()
        self.verbose = verbose
        self.cache_enabled = cache_enabled

        # Initialize components
        self.dependency_graph = DependencyGraph()
        self.parse_results: Dict[str, ParseResult] = {}
        self.cache_dir = self.project_path / ".architecture-assess-cache"

        # Statistics
        self.stats = {
            "files_discovered": 0,
            "files_parsed": 0,
            "files_skipped": 0,
            "parse_errors": 0,
            "cache_hits": 0,
        }

    def run(self) -> AssessmentResult:
        """Run the complete assessment pipeline.

        Returns:
            Complete assessment result with metrics and violations.
        """
        start_time = datetime.now()

        try:
            logger.info("=" * 60)
            logger.info("Architecture Quality Assessment")
            logger.info("=" * 60)

            # Phase 1: Project Detection
            logger.info("Phase 1: Detecting project type...")
            project_info = self._detect_project()

            # Phase 2: File Discovery
            logger.info("Phase 2: Discovering source files...")
            source_files = self._discover_files()

            # Phase 3: Parse Files
            logger.info(f"Phase 3: Parsing {len(source_files)} files...")
            self._parse_files(source_files)

            # Phase 4: Build Dependency Graph
            logger.info("Phase 4: Building dependency graph...")
            self._build_dependency_graph()

            # Phase 5: Run Analyzers
            logger.info("Phase 5: Running analyzers...")
            violations = self._run_analyzers(project_info)

            # Phase 6: Calculate Metrics
            logger.info("Phase 6: Calculating metrics...")
            metrics = self._calculate_metrics()

            # Build result
            duration = (datetime.now() - start_time).total_seconds()

            metadata = {
                "generated_at": datetime.now().isoformat(),
                "duration_seconds": round(duration, 2),
                "tool_name": "architecture-quality-assess",
                "tool_version": "1.0.0",
                "statistics": self.stats,
            }

            result = AssessmentResult(
                metadata=metadata,
                project_info=project_info,
                metrics=metrics,
                violations=violations,
            )

            logger.info("=" * 60)
            logger.info(f"Assessment completed in {duration:.2f}s")
            logger.info(f"Found {len(violations)} violation(s)")
            logger.info("=" * 60)

            return result

        except Exception as e:
            logger.error(f"Assessment failed: {e}", exc_info=True)
            raise

    def _detect_project(self) -> ProjectInfo:
        """Detect project type and framework.

        Returns:
            ProjectInfo with detection results.
        """
        detection = detect_project_type(str(self.project_path))

        project_name = self.project_path.name

        return ProjectInfo(
            name=project_name,
            path=str(self.project_path),
            project_type=detection.get("type", "unknown"),
            framework=detection.get("framework", "Unknown"),
            framework_version=detection.get("version"),
            architecture_pattern=detection.get("architecture_pattern"),
        )

    def _discover_files(self) -> List[Path]:
        """Discover all source files in the project.

        Returns:
            List of source file paths.
        """
        source_files = []
        supported_extensions = set(get_supported_extensions())

        # Common directories to exclude
        exclude_dirs = {
            "node_modules",
            ".next",
            "dist",
            "build",
            "__pycache__",
            ".git",
            ".venv",
            "venv",
            "env",
            ".tox",
            "htmlcov",
            ".pytest_cache",
            "coverage",
            ".mypy_cache",
        }

        # Additional patterns from config
        if hasattr(self.config, "exclude_paths"):
            for pattern in self.config.exclude_paths:
                exclude_dirs.add(pattern.strip("/"))

        logger.debug(f"Searching in: {self.project_path}")
        logger.debug(f"Supported extensions: {supported_extensions}")
        logger.debug(f"Excluding directories: {exclude_dirs}")

        # Recursively find source files
        for file_path in self.project_path.rglob("*"):
            # Skip if not a file
            if not file_path.is_file():
                continue

            # Skip if extension not supported
            if file_path.suffix not in supported_extensions:
                continue

            # Skip if in excluded directory
            relative_path = file_path.relative_to(self.project_path)
            parts = relative_path.parts
            if any(part in exclude_dirs for part in parts):
                continue

            # Skip test files if configured
            if hasattr(self.config, "skip_tests") and self.config.skip_tests:
                if any(part in str(file_path) for part in ["test_", ".test.", ".spec.", "__tests__"]):
                    continue

            source_files.append(file_path)

        self.stats["files_discovered"] = len(source_files)
        logger.info(f"Discovered {len(source_files)} source file(s)")

        return source_files

    def _parse_files(self, source_files: List[Path]) -> None:
        """Parse all source files.

        Args:
            source_files: List of files to parse.
        """
        total = len(source_files)

        for i, file_path in enumerate(source_files, 1):
            if self.verbose or i % 10 == 0:
                logger.info(f"Parsing {i}/{total}: {file_path.name}")

            # Check cache
            if self.cache_enabled:
                cached_result = self._load_from_cache(file_path)
                if cached_result:
                    relative_path = str(file_path.relative_to(self.project_path))
                    self.parse_results[relative_path] = cached_result
                    self.stats["cache_hits"] += 1
                    self.stats["files_parsed"] += 1
                    continue

            # Parse file
            parser = get_parser_for_file(file_path)
            if not parser:
                logger.warning(f"No parser available for {file_path}")
                self.stats["files_skipped"] += 1
                continue

            try:
                result = parser.parse_file(file_path)

                # Store result with relative path as key
                relative_path = str(file_path.relative_to(self.project_path))
                self.parse_results[relative_path] = result

                # Cache result
                if self.cache_enabled:
                    self._save_to_cache(file_path, result)

                self.stats["files_parsed"] += 1

            except Exception as e:
                logger.error(f"Error parsing {file_path}: {e}")
                self.stats["parse_errors"] += 1

        logger.info(
            f"Parsing complete: {self.stats['files_parsed']} parsed, "
            f"{self.stats['parse_errors']} errors, "
            f"{self.stats['cache_hits']} cache hits"
        )

    def _build_dependency_graph(self) -> None:
        """Build dependency graph from parse results."""
        for module_path, result in self.parse_results.items():
            # Add node for this module
            self.dependency_graph.add_node(module_path)

            # Add edges for each import
            for import_stmt in result.imports:
                # Try to resolve import to project file
                dependency_path = self._resolve_import(
                    module_path, import_stmt.module
                )

                if dependency_path:
                    # Internal dependency
                    self.dependency_graph.add_dependency(
                        module_path, dependency_path, is_external=False
                    )
                else:
                    # External dependency
                    self.dependency_graph.add_dependency(
                        module_path, import_stmt.module, is_external=True
                    )

        logger.info(
            f"Dependency graph built: "
            f"{len(self.dependency_graph._nodes)} nodes, "
            f"{sum(len(n.dependencies) for n in self.dependency_graph._nodes.values())} edges"
        )

    def _resolve_import(
        self, source_module: str, import_name: str
    ) -> Optional[str]:
        """Resolve an import to a project file path.

        Args:
            source_module: Module containing the import.
            import_name: Imported module name.

        Returns:
            Resolved file path, or None if external.
        """
        # Simple heuristic: check if any parsed file matches
        # This is a simplified version - production would need more sophisticated resolution

        # Try direct match
        for module_path in self.parse_results.keys():
            module_name = module_path.replace("/", ".").replace("\\", ".")
            if module_name.endswith(".py"):
                module_name = module_name[:-3]

            if import_name in module_name or module_name in import_name:
                return module_path

        return None

    def _run_analyzers(self, project_info: ProjectInfo) -> List[Violation]:
        """Run all enabled analyzers.

        Args:
            project_info: Project detection information.

        Returns:
            List of all violations found.
        """
        # Build file paths list
        file_paths = [
            self.project_path / path
            for path in self.parse_results.keys()
        ]

        # Build analysis context
        context = AnalysisContext(
            project_root=self.project_path,
            config=self.config,
            file_paths=file_paths,
            metadata={
                "parse_results": self.parse_results,
                "project_info": project_info,
            },
            dependency_graph=self.dependency_graph,
        )

        # Run analyzers
        results = run_all_analyzers(context)

        # Flatten violations from all analyzers
        all_violations: List[Violation] = []
        for analyzer_name, violations in results.items():
            logger.info(f"{analyzer_name}: {len(violations)} violation(s)")
            all_violations.extend(violations)

        # Sort by severity (critical first)
        severity_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
        all_violations.sort(
            key=lambda v: (
                severity_order.get(v.severity, 99),
                v.file_path,
                v.line_number or 0,
            )
        )

        return all_violations

    def _calculate_metrics(self) -> ProjectMetrics:
        """Calculate project-wide metrics.

        Returns:
            ProjectMetrics with all calculated values.
        """
        # Calculate basic file metrics
        total_files = len(self.parse_results)

        # Build per-module coupling metrics
        coupling_dict = {}
        for module_path, node in self.dependency_graph._nodes.items():
            if not node.is_external:
                coupling_metrics = CouplingMetrics(
                    module_path=module_path,
                    fan_in=node.fan_in,
                    fan_out=node.fan_out,
                    instability=node.instability,
                    dependencies=list(node.dependencies),
                    dependents=list(node.dependents),
                )
                coupling_dict[module_path] = coupling_metrics

        # SOLID metrics would be calculated by SOLID analyzer
        # For now, use defaults
        solid_metrics = SOLIDMetrics(
            overall_score=100,
            srp_score=100,
            ocp_score=100,
            lsp_score=100,
            isp_score=100,
            dip_score=100,
            violations_count=0,
        )

        return ProjectMetrics(
            overall_score=100,
            total_files=total_files,
            total_modules=len(coupling_dict),
            total_violations=0,
            critical_count=0,
            high_count=0,
            medium_count=0,
            low_count=0,
            coupling=coupling_dict,
            solid=solid_metrics,
        )

    def _load_from_cache(self, file_path: Path) -> Optional[ParseResult]:
        """Load parse result from cache if available and valid.

        Args:
            file_path: File to load cache for.

        Returns:
            Cached ParseResult or None if cache miss.
        """
        if not self.cache_dir.exists():
            return None

        # Calculate cache key from file content hash
        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
        except Exception:
            return None

        cache_file = self.cache_dir / f"{file_path.name}_{content_hash}.json"

        if not cache_file.exists():
            return None

        try:
            cache_data = json.loads(cache_file.read_text())
            # Reconstruct ParseResult (simplified - actual implementation
            # would need proper deserialization)
            return None  # For now, disable cache loading
        except Exception:
            return None

    def _save_to_cache(self, file_path: Path, result: ParseResult) -> None:
        """Save parse result to cache.

        Args:
            file_path: File being cached.
            result: Parse result to cache.
        """
        try:
            self.cache_dir.mkdir(exist_ok=True)

            # Calculate cache key
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]

            cache_file = self.cache_dir / f"{file_path.name}_{content_hash}.json"

            # Serialize result (simplified)
            cache_data = {
                "file_path": str(file_path),
                "hash": content_hash,
                "timestamp": datetime.now().isoformat(),
            }

            cache_file.write_text(json.dumps(cache_data, indent=2))

        except Exception as e:
            logger.debug(f"Cache save failed: {e}")


def main() -> int:
    """Main entry point for CLI.

    Returns:
        Exit code (0 for success, 1 for failure).
    """
    parser = argparse.ArgumentParser(
        description="Architecture Quality Assessment Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                          # Analyze current directory
  %(prog)s /path/to/project        # Analyze specific project
  %(prog)s --format json           # Output JSON format
  %(prog)s --severity critical     # Only show critical issues
  %(prog)s --verbose               # Show detailed progress
        """,
    )

    parser.add_argument(
        "project_path",
        nargs="?",
        default=".",
        help="Project root directory to analyze (default: current directory)",
    )

    parser.add_argument(
        "--format",
        choices=["markdown", "json", "tasks", "all"],
        default="markdown",
        help="Output format (default: markdown)",
    )

    parser.add_argument(
        "--output",
        "-o",
        help="Output file path (default: architecture-assessment.{format})",
    )

    parser.add_argument(
        "--severity",
        choices=["critical", "high", "medium", "low"],
        help="Minimum severity level to report",
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose output",
    )

    parser.add_argument(
        "--no-cache",
        action="store_true",
        help="Disable parsing cache",
    )

    parser.add_argument(
        "--list-analyzers",
        action="store_true",
        help="List available analyzers and exit",
    )

    args = parser.parse_args()

    # Setup logging
    setup_logging(args.verbose)

    # Handle list analyzers
    if args.list_analyzers:
        print("\nAvailable Analyzers:")
        print("-" * 60)
        for info in list_analyzer_info():
            print(f"{info['name']:<15} {info['description']}")
        print()
        return 0

    # Resolve project path
    project_path = Path(args.project_path).resolve()

    if not project_path.exists():
        logger.error(f"Project path does not exist: {project_path}")
        return 1

    if not project_path.is_dir():
        logger.error(f"Project path is not a directory: {project_path}")
        return 1

    try:
        # Run assessment
        orchestrator = AssessmentOrchestrator(
            project_path=project_path,
            verbose=args.verbose,
            cache_enabled=not args.no_cache,
        )

        result = orchestrator.run()

        # Filter by severity if requested
        if args.severity:
            severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
            min_severity = severity_order[args.severity]

            result.violations = [
                v
                for v in result.violations
                if severity_order.get(v.severity.lower(), 99) <= min_severity
            ]

        # Determine output path
        if args.output:
            output_path = Path(args.output)
        elif args.format == "markdown":
            output_path = project_path / "architecture-assessment.md"
        elif args.format == "json":
            output_path = project_path / "architecture-assessment.json"
        elif args.format == "tasks":
            output_path = project_path / "architecture-refactoring-tasks.md"
        else:  # all
            output_path = None

        # Generate report(s)
        if args.format == "all":
            paths = generate_all_reports(result, project_path)
            print("\nReports generated:")
            for fmt, path in paths.items():
                print(f"  {fmt}: {path}")
        elif args.format == "markdown":
            generate_markdown_report(result, output_path)
            print(f"\nReport saved to: {output_path}")
        elif args.format == "json":
            generate_json_report(result, output_path, pretty=True)
            print(f"\nReport saved to: {output_path}")
        elif args.format == "tasks":
            generate_task_list(result, output_path)
            print(f"\nTask list saved to: {output_path}")

        # Print summary to console
        summary = generate_ci_summary(result)
        print(f"\nSummary: {summary['message']}")
        print(f"Score: {summary['score']}/100")
        print(
            f"Violations: {summary['violations']['critical']} critical, "
            f"{summary['violations']['high']} high, "
            f"{summary['violations']['medium']} medium, "
            f"{summary['violations']['low']} low"
        )

        # Exit with error code if critical issues found
        if summary["violations"]["critical"] > 0:
            return 1

        return 0

    except KeyboardInterrupt:
        logger.info("\nAssessment cancelled by user")
        return 1
    except Exception as e:
        logger.error(f"Assessment failed: {e}", exc_info=args.verbose)
        return 1


if __name__ == "__main__":
    sys.exit(main())
