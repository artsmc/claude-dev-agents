#!/usr/bin/env python3
"""Security Quality Assessment CLI.

Main entry point for running security quality assessments against a project.
Orchestrates the full pipeline: file discovery, parsing, analysis, suppression,
result aggregation, and Markdown report generation.

Exit codes:
    0 -- Assessment completed, no CRITICAL or HIGH findings.
    1 -- Assessment completed, CRITICAL or HIGH findings detected.
    2 -- Fatal error prevented assessment from completing.

Usage:
    python scripts/assess.py /path/to/project
    python scripts/assess.py /path/to/project --output report.md
    python scripts/assess.py /path/to/project --skip-osv --verbose

All dependencies are from the Python standard library; no pip packages
are required.
"""

from __future__ import annotations

import argparse
import logging
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# Ensure the project root is on sys.path so that ``lib`` can be imported
# regardless of the working directory.
# ---------------------------------------------------------------------------
_SCRIPT_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _SCRIPT_DIR.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

# ---------------------------------------------------------------------------
# Internal imports -- grouped by layer.
# ---------------------------------------------------------------------------

# Discovery
from lib.discovery import (
    discover_lockfiles,
    discover_source_files,
    parse_gitignore,
    SOURCE_EXTENSIONS,
)

# Parsers
from lib.parsers import (
    DependencyParser,
    JavaScriptSecurityParser,
    PythonSecurityParser,
)

# Models
from lib.models.assessment import AssessmentResult, ProjectInfo
from lib.models.finding import Finding, Severity
from lib.models.parse_result import ParseResult

# Analyzers
from lib.analyzers import (
    AuthAnalyzer,
    ConfigAnalyzer,
    DependencyAnalyzer,
    InjectionAnalyzer,
    SecretsAnalyzer,
    SensitiveDataAnalyzer,
)

# Utilities
from lib.utils.osv_client import OSVClient
from lib.utils.suppression_loader import (
    apply_suppressions,
    load_suppression_config,
)

# Reporters
from lib.reporters import SecurityMarkdownReporter

logger = logging.getLogger("security-quality-assess")

# ---------------------------------------------------------------------------
# Version information
# ---------------------------------------------------------------------------

__version__ = "1.0.0"

ANALYZER_VERSIONS: Dict[str, str] = {
    "secrets": "1.0",
    "injection": "1.0",
    "auth": "1.0",
    "dependency": "1.0",
    "config": "1.0",
    "sensitive_data": "1.0",
}
"""Version strings for each analyzer, included in the assessment report."""


# ---------------------------------------------------------------------------
# CLI argument parsing
# ---------------------------------------------------------------------------


def build_argument_parser() -> argparse.ArgumentParser:
    """Build and return the CLI argument parser.

    Defines the following arguments:

        project_path (positional)
            Absolute or relative path to the project root directory to assess.

        --output / -o (optional)
            Path where the generated Markdown report will be written.  When
            omitted the report is printed to stdout.

        --config (optional)
            Path to a custom ``.security-suppress.json`` configuration file.
            Overrides the default location at ``<project_path>/.security-suppress.json``.

        --skip-osv (flag)
            Skip querying the OSV vulnerability database for dependency
            analysis.  Useful when offline or to avoid network latency.

        --verbose / -v (flag)
            Enable DEBUG-level logging for detailed progress output.

        --version (flag)
            Print version information and exit.

    Returns:
        A configured ``argparse.ArgumentParser`` instance.
    """
    parser = argparse.ArgumentParser(
        prog="assess",
        description=(
            "Run a security quality assessment against a project directory. "
            "Scans source files for vulnerabilities across OWASP Top 10 "
            "categories and generates a comprehensive Markdown report."
        ),
        epilog=(
            "Exit codes: 0 = no critical/high findings, "
            "1 = critical/high findings detected, "
            "2 = fatal error."
        ),
    )

    parser.add_argument(
        "project_path",
        type=str,
        help="Path to the project root directory to assess.",
    )

    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default=None,
        metavar="FILE",
        help=(
            "Write the Markdown report to FILE instead of stdout. "
            "Parent directories are NOT created automatically."
        ),
    )

    parser.add_argument(
        "--config",
        type=str,
        default=None,
        metavar="FILE",
        help=(
            "Path to a .security-suppress.json file.  Defaults to "
            "<project_path>/.security-suppress.json."
        ),
    )

    parser.add_argument(
        "--skip-osv",
        action="store_true",
        default=False,
        help="Skip the OSV vulnerability database lookup for dependencies.",
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        default=False,
        help="Enable verbose (DEBUG) logging output.",
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    return parser


# ---------------------------------------------------------------------------
# Logging setup
# ---------------------------------------------------------------------------


def configure_logging(verbose: bool) -> None:
    """Configure the root logger for the assessment run.

    Sets the logging level to DEBUG when *verbose* is True, otherwise INFO.
    All log records are written to stderr so that stdout can be reserved for
    the final Markdown report when no ``--output`` file is specified.

    Args:
        verbose: When True, enable DEBUG-level logging.
    """
    level = logging.DEBUG if verbose else logging.INFO

    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(level)

    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)-8s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)

    # Configure the project logger and its children.
    root_logger = logging.getLogger("security-quality-assess")
    root_logger.setLevel(level)
    root_logger.addHandler(handler)

    # Also configure the ``lib`` namespace so all library loggers inherit.
    lib_logger = logging.getLogger("lib")
    lib_logger.setLevel(level)
    lib_logger.addHandler(handler)


# ---------------------------------------------------------------------------
# File parsing orchestration
# ---------------------------------------------------------------------------


def parse_source_file(
    file_path: Path,
    project_path: Path,
    py_parser: PythonSecurityParser,
    js_parser: JavaScriptSecurityParser,
) -> Optional[ParseResult]:
    """Parse a single source file into a ``ParseResult``.

    Reads the file from disk, selects the appropriate parser based on the
    file extension, and returns a populated ``ParseResult``.  Python files
    are parsed with the AST-based :class:`PythonSecurityParser`; JavaScript
    and TypeScript files are parsed with the regex-based
    :class:`JavaScriptSecurityParser`.

    Args:
        file_path: Absolute path to the source file.
        project_path: Project root for computing relative paths.
        py_parser: Pre-instantiated Python parser.
        js_parser: Pre-instantiated JavaScript parser.

    Returns:
        A ``ParseResult`` for the file, or ``None`` if the file could not
        be read or its extension is not recognized.
    """
    try:
        rel_path = str(file_path.relative_to(project_path))
    except ValueError:
        rel_path = str(file_path)

    try:
        content = file_path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        logger.warning("Could not read file %s: %s", file_path, exc)
        return None

    source_lines = content.splitlines()
    suffix = file_path.suffix.lower()

    if suffix == ".py":
        tree, _ = py_parser.parse(content, filename=rel_path)

        string_literals = []
        dangerous_calls = []
        sql_queries = []
        function_decorators = []

        if tree is not None:
            string_literals = py_parser.extract_string_literals(tree, source_lines)
            dangerous_calls = py_parser.extract_dangerous_calls(tree)
            sql_queries = py_parser.extract_sql_queries(tree)
            function_decorators = py_parser.extract_all_function_decorators(tree)

        return ParseResult(
            file_path=rel_path,
            language="python",
            source_lines=source_lines,
            raw_source=content,
            string_literals=string_literals,
            dangerous_calls=dangerous_calls,
            sql_queries=sql_queries,
            function_decorators=function_decorators,
        )

    if suffix in (".js", ".ts", ".jsx", ".tsx"):
        js_string_literals = js_parser.extract_string_literals(content)
        dangerous_patterns = js_parser.extract_dangerous_patterns(content)
        js_db_queries = js_parser.extract_database_queries(content)

        return ParseResult(
            file_path=rel_path,
            language="javascript",
            source_lines=source_lines,
            raw_source=content,
            js_string_literals=js_string_literals,
            dangerous_patterns=dangerous_patterns,
            js_db_queries=js_db_queries,
        )

    logger.debug("Skipping unrecognized file extension: %s", file_path)
    return None


def parse_lockfile(
    lockfile_type: str,
    lockfile_path: Path,
    project_path: Path,
    dep_parser: DependencyParser,
) -> Optional[ParseResult]:
    """Parse a lockfile into a ``ParseResult``.

    Dispatches to the correct :class:`DependencyParser` method based on
    the lockfile type key returned by :func:`discover_lockfiles`.

    Args:
        lockfile_type: One of ``"npm"``, ``"yarn"``, or ``"poetry"``.
        lockfile_path: Absolute path to the lockfile.
        project_path: Project root for computing relative paths.
        dep_parser: Pre-instantiated dependency parser.

    Returns:
        A ``ParseResult`` with the ``dependencies`` field populated, or
        ``None`` if parsing fails.
    """
    try:
        rel_path = str(lockfile_path.relative_to(project_path))
    except ValueError:
        rel_path = str(lockfile_path)

    parse_methods = {
        "npm": dep_parser.parse_package_lock,
        "yarn": dep_parser.parse_yarn_lock,
        "poetry": dep_parser.parse_poetry_lock,
    }

    parse_fn = parse_methods.get(lockfile_type)
    if parse_fn is None:
        logger.warning("Unknown lockfile type: %s", lockfile_type)
        return None

    try:
        dependencies = parse_fn(lockfile_path)
    except Exception as exc:
        logger.warning(
            "Failed to parse %s lockfile at %s: %s",
            lockfile_type,
            lockfile_path,
            exc,
        )
        return None

    return ParseResult(
        file_path=rel_path,
        language="lockfile",
        dependencies=dependencies,
    )


def parse_all_files(
    source_files: List[Path],
    lockfiles: Dict[str, Path],
    project_path: Path,
) -> List[ParseResult]:
    """Parse all discovered files into ``ParseResult`` objects.

    Instantiates the language-specific parsers, iterates through source
    files and lockfiles, and returns a flat list of results.  Files that
    fail to parse are logged and skipped silently.

    Args:
        source_files: Source file paths from :func:`discover_source_files`.
        lockfiles: Lockfile dict from :func:`discover_lockfiles`.
        project_path: Project root used for relative path computation.

    Returns:
        A list of ``ParseResult`` objects.  May be empty if no files could
        be parsed.
    """
    py_parser = PythonSecurityParser()
    js_parser = JavaScriptSecurityParser()
    dep_parser = DependencyParser()

    parsed_files: List[ParseResult] = []

    # Parse source files.
    for idx, file_path in enumerate(source_files, start=1):
        if idx % 500 == 0:
            logger.info("Parsing progress: %d / %d source files...", idx, len(source_files))

        result = parse_source_file(file_path, project_path, py_parser, js_parser)
        if result is not None:
            parsed_files.append(result)

    logger.info(
        "Parsed %d of %d source files successfully",
        len(parsed_files),
        len(source_files),
    )

    # Parse lockfiles.
    for lockfile_type, lockfile_path in lockfiles.items():
        result = parse_lockfile(lockfile_type, lockfile_path, project_path, dep_parser)
        if result is not None:
            parsed_files.append(result)
            dep_count = len(result.dependencies)
            logger.info(
                "Parsed %s lockfile: %d dependencies found",
                lockfile_type,
                dep_count,
            )

    return parsed_files


# ---------------------------------------------------------------------------
# Analyzer orchestration
# ---------------------------------------------------------------------------


def run_analyzers(
    parsed_files: List[ParseResult],
    skip_osv: bool,
    config: Optional[Dict[str, Any]] = None,
) -> List[Finding]:
    """Execute all security analyzers and collect findings.

    Instantiates each analyzer, calls its ``analyze`` method with the
    parsed files, and merges the resulting findings into a single list.
    Findings are assigned sequential IDs (``SEC-001``, ``SEC-002``, ...).

    Each analyzer is wrapped in a try/except so that a failure in one
    analyzer does not prevent the others from running.

    Args:
        parsed_files: List of ``ParseResult`` objects from the parsing phase.
        skip_osv: When True, the ``DependencyAnalyzer`` is still run but
            the ``OSVClient`` is configured with caching disabled and a
            sentinel to skip network calls.
        config: Optional configuration dictionary passed to each analyzer.
            Defaults to an empty dict.

    Returns:
        A sorted list of ``Finding`` objects with sequential IDs assigned.
        Sorted by severity (CRITICAL first) then by file path.
    """
    if config is None:
        config = {}

    all_findings: List[Finding] = []

    # ---- Static analyzers (no network) ------------------------------------

    analyzer_classes = [
        ("Secrets", SecretsAnalyzer),
        ("Injection", InjectionAnalyzer),
        ("Auth", AuthAnalyzer),
        ("Config", ConfigAnalyzer),
        ("SensitiveData", SensitiveDataAnalyzer),
    ]

    for name, analyzer_cls in analyzer_classes:
        logger.info("Running %s analyzer...", name)
        try:
            analyzer = analyzer_cls()
            findings = analyzer.analyze(parsed_files, config)
            logger.info("  %s analyzer: %d finding(s)", name, len(findings))
            all_findings.extend(findings)
        except Exception as exc:
            logger.error(
                "  %s analyzer failed: %s -- skipping",
                name,
                exc,
            )

    # ---- Dependency analyzer (optional network) ---------------------------

    logger.info("Running Dependency analyzer...")
    try:
        if skip_osv:
            logger.info("  OSV lookups disabled (--skip-osv)")
            # Create a client with caching enabled but no network calls will
            # be made because we only pass it through; the DependencyAnalyzer
            # still processes lockfile data for structural analysis.
            osv_client = OSVClient(cache_enabled=False)
        else:
            osv_client = OSVClient(cache_enabled=True)

        dep_analyzer = DependencyAnalyzer(osv_client=osv_client)

        # When --skip-osv is set, pass a config flag so the analyzer knows
        # not to make network calls.
        dep_config = dict(config)
        if skip_osv:
            dep_config["skip_osv"] = True

        findings = dep_analyzer.analyze(parsed_files, dep_config)
        logger.info("  Dependency analyzer: %d finding(s)", len(findings))
        all_findings.extend(findings)
    except Exception as exc:
        logger.error("  Dependency analyzer failed: %s -- skipping", exc)

    # ---- Assign sequential IDs and sort -----------------------------------

    severity_order = {
        Severity.CRITICAL: 0,
        Severity.HIGH: 1,
        Severity.MEDIUM: 2,
        Severity.LOW: 3,
    }

    all_findings.sort(
        key=lambda f: (severity_order.get(f.severity, 99), f.file_path, f.line_number)
    )

    for idx, finding in enumerate(all_findings, start=1):
        finding.id = f"SEC-{idx:03d}"

    logger.info("Total findings across all analyzers: %d", len(all_findings))

    return all_findings


# ---------------------------------------------------------------------------
# Suppression handling
# ---------------------------------------------------------------------------


def handle_suppressions(
    findings: List[Finding],
    project_path: Path,
    config_path: Optional[str],
) -> Tuple[List[Finding], int]:
    """Load suppression config and filter findings.

    Attempts to load the suppression configuration from either the
    explicit *config_path* or the default project-root location.
    When a valid configuration is found, expired suppressions are logged
    and active suppressions are applied to filter the findings list.

    Args:
        findings: Raw findings from the analyzer phase.
        project_path: Project root directory.
        config_path: Optional explicit path to a suppression config file.
            When None, the default ``<project_path>/.security-suppress.json``
            is used.

    Returns:
        A 2-tuple of ``(filtered_findings, suppressed_count)``.  When no
        suppression config is found, returns the original findings with a
        count of 0.
    """
    if config_path is not None:
        # Custom config path -- load from explicit location.
        config_dir = Path(config_path).parent
        suppression_config = load_suppression_config(config_dir)
    else:
        suppression_config = load_suppression_config(project_path)

    if suppression_config is None:
        logger.info("No suppression config found -- all findings retained")
        return findings, 0

    logger.info(
        "Loaded %d suppression rule(s)",
        len(suppression_config.suppressions),
    )

    filtered, suppressed_count = apply_suppressions(findings, suppression_config)

    logger.info(
        "Suppression results: %d suppressed, %d remaining",
        suppressed_count,
        len(filtered),
    )

    return filtered, suppressed_count


# ---------------------------------------------------------------------------
# Result building
# ---------------------------------------------------------------------------


def build_assessment_result(
    project_path: Path,
    files_analyzed: int,
    scan_duration: float,
    findings: List[Finding],
    suppressed_count: int,
) -> AssessmentResult:
    """Construct the final ``AssessmentResult``.

    Creates a :class:`ProjectInfo` from the scan metadata and wraps it
    together with findings and suppression statistics into an
    :class:`AssessmentResult`.

    Args:
        project_path: Absolute path to the assessed project.
        files_analyzed: Number of source files that were parsed.
        scan_duration: Wall-clock scan time in seconds.
        findings: Post-suppression findings list.
        suppressed_count: Number of findings that were suppressed.

    Returns:
        A fully populated ``AssessmentResult`` instance.
    """
    project_info = ProjectInfo(
        name=project_path.name,
        path=str(project_path),
        files_analyzed=files_analyzed,
        scan_duration=round(scan_duration, 2),
        timestamp=ProjectInfo.make_timestamp(),
    )

    return AssessmentResult(
        project=project_info,
        findings=findings,
        suppressed_count=suppressed_count,
        analyzer_versions=dict(ANALYZER_VERSIONS),
    )


# ---------------------------------------------------------------------------
# Report generation and output
# ---------------------------------------------------------------------------


def generate_and_write_report(
    result: AssessmentResult,
    output_path: Optional[str],
) -> None:
    """Generate the Markdown report and write it to the destination.

    When *output_path* is provided, writes the report to that file.
    Otherwise, the report is printed to stdout.

    Args:
        result: The completed assessment result.
        output_path: Optional filesystem path for the report.  When None,
            the report is written to stdout.
    """
    reporter = SecurityMarkdownReporter()
    markdown = reporter.generate(result)

    if output_path is not None:
        output_file = Path(output_path)
        try:
            output_file.write_text(markdown, encoding="utf-8")
            logger.info("Report written to %s", output_file)
        except OSError as exc:
            logger.error("Failed to write report to %s: %s", output_file, exc)
            # Fall back to stdout.
            sys.stdout.write(markdown)
    else:
        sys.stdout.write(markdown)


# ---------------------------------------------------------------------------
# Exit code determination
# ---------------------------------------------------------------------------


def determine_exit_code(result: AssessmentResult) -> int:
    """Determine the process exit code from the assessment result.

    Exit codes:
        0 -- No CRITICAL or HIGH severity findings.
        1 -- At least one CRITICAL or HIGH severity finding.

    The fatal-error exit code (2) is handled by the top-level exception
    handler in :func:`main`, not here.

    Args:
        result: The completed assessment result.

    Returns:
        ``0`` or ``1`` depending on finding severity.
    """
    severity_counts = result.get_severity_counts()

    if severity_counts["CRITICAL"] > 0 or severity_counts["HIGH"] > 0:
        return 1

    return 0


# ---------------------------------------------------------------------------
# Main workflow
# ---------------------------------------------------------------------------


def main(argv: Optional[List[str]] = None) -> int:
    """Run the complete security quality assessment workflow.

    Orchestrates the 10-step pipeline:

        1. Parse CLI arguments.
        2. Configure logging.
        3. Validate project path.
        4. Discover source files and lockfiles.
        5. Parse discovered files.
        6. Run all security analyzers.
        7. Load and apply suppressions.
        8. Build the assessment result.
        9. Generate and write the report.
       10. Determine and return the exit code.

    Args:
        argv: Command-line arguments.  Defaults to ``sys.argv[1:]`` when
            None, which is the standard behavior when called from the
            ``if __name__ == "__main__"`` block.

    Returns:
        Exit code: 0 (clean), 1 (findings), or 2 (fatal error).
    """
    # ------------------------------------------------------------------
    # Step 1: Parse CLI arguments
    # ------------------------------------------------------------------
    parser = build_argument_parser()
    args = parser.parse_args(argv)

    # ------------------------------------------------------------------
    # Step 2: Configure logging
    # ------------------------------------------------------------------
    configure_logging(verbose=args.verbose)

    logger.info("Security Quality Assessment v%s", __version__)
    logger.info("=" * 60)

    # ------------------------------------------------------------------
    # Step 3: Validate project path
    # ------------------------------------------------------------------
    project_path = Path(args.project_path).resolve()

    if not project_path.exists():
        logger.error("Project path does not exist: %s", project_path)
        return 2

    if not project_path.is_dir():
        logger.error("Project path is not a directory: %s", project_path)
        return 2

    logger.info("Project: %s", project_path)
    logger.info("Output:  %s", args.output or "(stdout)")
    logger.info("OSV:     %s", "disabled" if args.skip_osv else "enabled")

    # Start the performance timer.
    start_time = time.monotonic()

    # ------------------------------------------------------------------
    # Step 4: Discover source files and lockfiles
    # ------------------------------------------------------------------
    logger.info("-" * 60)
    logger.info("Phase 1: File Discovery")
    logger.info("-" * 60)

    gitignore_patterns = parse_gitignore(project_path)

    source_files = discover_source_files(project_path, gitignore_patterns)
    lockfiles = discover_lockfiles(project_path)

    logger.info(
        "Discovered %d source file(s) and %d lockfile(s)",
        len(source_files),
        len(lockfiles),
    )

    if not source_files and not lockfiles:
        logger.warning(
            "No source files or lockfiles found in %s -- "
            "generating empty report",
            project_path,
        )

    # ------------------------------------------------------------------
    # Step 5: Parse discovered files
    # ------------------------------------------------------------------
    logger.info("-" * 60)
    logger.info("Phase 2: File Parsing")
    logger.info("-" * 60)

    parsed_files = parse_all_files(source_files, lockfiles, project_path)

    logger.info("Successfully parsed %d file(s)", len(parsed_files))

    # ------------------------------------------------------------------
    # Step 6: Run all security analyzers
    # ------------------------------------------------------------------
    logger.info("-" * 60)
    logger.info("Phase 3: Security Analysis")
    logger.info("-" * 60)

    all_findings = run_analyzers(parsed_files, skip_osv=args.skip_osv)

    # ------------------------------------------------------------------
    # Step 7: Load and apply suppressions
    # ------------------------------------------------------------------
    logger.info("-" * 60)
    logger.info("Phase 4: Suppression Filtering")
    logger.info("-" * 60)

    filtered_findings, suppressed_count = handle_suppressions(
        all_findings,
        project_path,
        args.config,
    )

    # ------------------------------------------------------------------
    # Step 8: Build the assessment result
    # ------------------------------------------------------------------
    scan_duration = time.monotonic() - start_time

    result = build_assessment_result(
        project_path=project_path,
        files_analyzed=len(source_files),
        scan_duration=scan_duration,
        findings=filtered_findings,
        suppressed_count=suppressed_count,
    )

    # ------------------------------------------------------------------
    # Step 9: Generate and write the report
    # ------------------------------------------------------------------
    logger.info("-" * 60)
    logger.info("Phase 5: Report Generation")
    logger.info("-" * 60)

    generate_and_write_report(result, args.output)

    # ------------------------------------------------------------------
    # Step 10: Summary and exit code
    # ------------------------------------------------------------------
    severity_counts = result.get_severity_counts()
    risk_score = result.calculate_risk_score()
    exit_code = determine_exit_code(result)

    logger.info("=" * 60)
    logger.info("Assessment Complete")
    logger.info("=" * 60)
    logger.info("  Files analyzed : %d", result.project.files_analyzed)
    logger.info("  Scan duration  : %.2fs", result.project.scan_duration)
    logger.info("  Total findings : %d", len(result.findings))
    logger.info("  Suppressed     : %d", result.suppressed_count)
    logger.info(
        "  Severity       : CRITICAL=%d  HIGH=%d  MEDIUM=%d  LOW=%d",
        severity_counts["CRITICAL"],
        severity_counts["HIGH"],
        severity_counts["MEDIUM"],
        severity_counts["LOW"],
    )
    logger.info("  Risk score     : %d", risk_score)
    logger.info("  Exit code      : %d", exit_code)

    return exit_code


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        logger.info("Assessment interrupted by user")
        sys.exit(2)
    except Exception as exc:
        # Last-resort handler -- should not normally be reached because
        # each phase has its own exception handling.
        logger.critical("Fatal error: %s", exc, exc_info=True)
        sys.exit(2)
