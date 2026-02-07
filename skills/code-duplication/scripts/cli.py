#!/usr/bin/env python3
"""
CLI Entry Point for Code Duplication Analysis Skill

Main orchestration of duplicate detection, analysis, and reporting.
"""

import argparse
import sys
import logging
from pathlib import Path
from typing import List, Tuple, Optional
import time

# Import all detection engines
from models import Config, AnalysisIssue, ErrorCategory
from file_discovery import discover_files, LANGUAGE_EXTENSIONS
from exact_detector import find_exact_duplicates
from structural_detector import find_structural_duplicates
from pattern_detector import detect_pattern_duplicates
from metrics_calculator import (
    calculate_metrics,
    rank_offenders,
    analyze_duplication_trends
)
from heatmap_renderer import generate_heatmap_data
from report_generator import generate_report, generate_csv_export


# Exit codes
EXIT_SUCCESS = 0
EXIT_USER_ERROR = 1
EXIT_PARTIAL_SUCCESS = 2
EXIT_FAILURE = 3


def setup_logging(verbose: bool = False, quiet: bool = False) -> logging.Logger:
    """
    Configure logging for the application.

    Args:
        verbose: Enable DEBUG level logging
        quiet: Suppress INFO level (only WARNING and ERROR)

    Returns:
        Configured logger instance

    Example:
        >>> logger = setup_logging(verbose=True)
        >>> logger.info("Analysis started")
    """
    logger = logging.getLogger('code_duplication')
    logger.setLevel(logging.DEBUG if verbose else logging.INFO)

    # Remove existing handlers
    logger.handlers.clear()

    # Console handler
    console_handler = logging.StreamHandler()

    if quiet:
        console_handler.setLevel(logging.WARNING)
    elif verbose:
        console_handler.setLevel(logging.DEBUG)
    else:
        console_handler.setLevel(logging.INFO)

    # Formatter
    formatter = logging.Formatter(
        '%(levelname)s: %(message)s'
    )
    console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)

    return logger


def get_file_language(file_path: Path) -> str:
    """
    Determine programming language from file extension.

    Args:
        file_path: Path to file

    Returns:
        Language name or 'unknown'

    Example:
        >>> get_file_language(Path("test.py"))
        'python'
    """
    suffix = file_path.suffix.lower()

    for lang, extensions in LANGUAGE_EXTENSIONS.items():
        if suffix in extensions:
            return lang

    return 'unknown'


class ProgressIndicator:
    """
    Simple progress indicator for CLI feedback.

    Example:
        >>> progress = ProgressIndicator("Scanning files")
        >>> progress.start()
        >>> progress.update(50, 100)
        >>> progress.complete()
    """

    def __init__(self, task: str):
        """
        Initialize progress indicator.

        Args:
            task: Task description
        """
        self.task = task
        self.start_time = None

    def start(self):
        """Start progress tracking."""
        self.start_time = time.time()
        print(f"⏳ {self.task}...", end='', flush=True)

    def update(self, current: int, total: int):
        """
        Update progress with current/total.

        Args:
            current: Current progress
            total: Total items
        """
        percentage = (current / total * 100) if total > 0 else 0
        print(f"\r⏳ {self.task}... {current}/{total} ({percentage:.0f}%)", end='', flush=True)

    def complete(self, count: Optional[int] = None):
        """
        Mark task as complete.

        Args:
            count: Optional count to display
        """
        elapsed = time.time() - self.start_time if self.start_time else 0
        count_str = f" ({count} found)" if count is not None else ""
        print(f"\r✅ {self.task}{count_str} - {elapsed:.1f}s")


def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments.

    Returns:
        Parsed arguments namespace

    Example:
        >>> args = parse_arguments()
        >>> args.path  # Path to analyze
    """
    parser = argparse.ArgumentParser(
        description="Code Duplication Analysis Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze current directory
  python cli.py .

  # Analyze specific directory with Python only
  python cli.py /path/to/code --language python

  # Generate report with custom output
  python cli.py /path/to/code --output report.md

  # Run only exact duplicate detection
  python cli.py /path/to/code --exact-only

  # Limit report to top 20 duplicates
  python cli.py /path/to/code --max-duplicates 20
        """
    )

    # Required arguments
    parser.add_argument(
        'path',
        type=Path,
        help='Path to codebase to analyze'
    )

    # Filter options
    parser.add_argument(
        '--language',
        type=str,
        nargs='+',
        choices=['python', 'javascript', 'typescript', 'java', 'rust', 'go'],
        help='Filter by language(s)'
    )

    parser.add_argument(
        '--exclude',
        type=str,
        nargs='+',
        default=[],
        help='Patterns to exclude (e.g., "**/test_*.py", "**/__pycache__/**")'
    )

    # Detection options
    parser.add_argument(
        '--exact-only',
        action='store_true',
        help='Run only exact duplicate detection (faster)'
    )

    parser.add_argument(
        '--structural-only',
        action='store_true',
        help='Run only structural duplicate detection'
    )

    parser.add_argument(
        '--pattern-only',
        action='store_true',
        help='Run only pattern duplicate detection'
    )

    parser.add_argument(
        '--min-lines',
        type=int,
        default=5,
        help='Minimum lines for duplicate detection (default: 5)'
    )

    parser.add_argument(
        '--min-chars',
        type=int,
        default=50,
        help='Minimum characters for exact duplicates (default: 50)'
    )

    # Output options
    parser.add_argument(
        '--output',
        type=Path,
        default=Path('duplication-report.md'),
        help='Output path for markdown report (default: duplication-report.md)'
    )

    parser.add_argument(
        '--csv',
        type=Path,
        help='Optional path for CSV export'
    )

    parser.add_argument(
        '--max-duplicates',
        type=int,
        default=50,
        help='Maximum duplicates to include in report (default: 50)'
    )

    parser.add_argument(
        '--quiet',
        action='store_true',
        help='Suppress progress indicators'
    )

    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging (DEBUG level)'
    )

    return parser.parse_args()


def run_analysis(args: argparse.Namespace) -> int:
    """
    Main analysis orchestration.

    Args:
        args: Parsed command-line arguments

    Returns:
        Exit code:
        - 0 = success
        - 1 = user error (invalid input)
        - 2 = partial success (warnings but completed)
        - 3 = failure (errors prevented completion)

    Example:
        >>> args = parse_arguments()
        >>> exit_code = run_analysis(args)
    """
    # Setup logging
    logger = setup_logging(verbose=getattr(args, 'verbose', False), quiet=args.quiet)
    logger.info("Code Duplication Analysis starting")

    # Track issues encountered
    issues: List[AnalysisIssue] = []

    # Validate path
    try:
        if not args.path.exists():
            logger.error(f"Path does not exist: {args.path}")
            print(f"❌ Error: Path does not exist: {args.path}", file=sys.stderr)
            return EXIT_USER_ERROR

        if not args.path.is_dir():
            logger.error(f"Path is not a directory: {args.path}")
            print(f"❌ Error: Path is not a directory: {args.path}", file=sys.stderr)
            return EXIT_USER_ERROR
    except PermissionError as e:
        logger.error(f"Permission denied accessing path: {args.path}")
        print(f"❌ Error: Permission denied: {args.path}", file=sys.stderr)
        return EXIT_USER_ERROR
    except Exception as e:
        logger.error(f"Unexpected error validating path: {e}")
        print(f"❌ Error: Cannot access path: {e}", file=sys.stderr)
        return EXIT_FAILURE

    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🔍 Code Duplication Analysis")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"Path: {args.path.absolute()}")
    print()

    # Step 1: Create configuration
    config = Config(
        min_lines=args.min_lines,
        languages=args.language if args.language else [
            "python", "javascript", "typescript", "java", "go", "rust", "cpp"
        ],
        exclude_patterns=args.exclude if args.exclude else [
            "**/node_modules/**",
            "**/__pycache__/**",
            "**/.git/**",
            "**/venv/**",
            "**/dist/**",
            "**/build/**",
        ]
    )

    # Step 2: File discovery
    progress = ProgressIndicator("Scanning files")
    if not args.quiet:
        progress.start()

    file_paths = discover_files(config, root_path=args.path)

    if not args.quiet:
        progress.complete(count=len(file_paths))

    if len(file_paths) == 0:
        print("⚠️  No files found to analyze")
        return 0

    # Read file contents
    progress = ProgressIndicator("Reading files")
    if not args.quiet:
        progress.start()

    files_content: List[Tuple[Path, str, str]] = []
    skipped_files = 0

    for idx, file_path in enumerate(file_paths):
        try:
            # Try UTF-8 first
            try:
                content = file_path.read_text(encoding='utf-8')
            except UnicodeDecodeError:
                # Fallback to latin-1
                logger.warning(f"UTF-8 decode failed for {file_path}, trying latin-1")
                try:
                    content = file_path.read_text(encoding='latin-1')
                    issues.append(AnalysisIssue(
                        category=ErrorCategory.ENCODING_ERROR,
                        severity="warning",
                        file_path=str(file_path),
                        message="UTF-8 decode failed, used latin-1 fallback"
                    ))
                except UnicodeDecodeError as e:
                    logger.error(f"Cannot decode {file_path}: {e}")
                    issues.append(AnalysisIssue(
                        category=ErrorCategory.ENCODING_ERROR,
                        severity="error",
                        file_path=str(file_path),
                        message=f"Cannot decode file: {str(e)}"
                    ))
                    skipped_files += 1
                    continue

            language = get_file_language(file_path)
            files_content.append((file_path, content, language))

            if not args.quiet:
                progress.update(idx + 1, len(file_paths))

        except PermissionError as e:
            logger.warning(f"Permission denied: {file_path}")
            issues.append(AnalysisIssue(
                category=ErrorCategory.PERMISSION_ERROR,
                severity="warning",
                file_path=str(file_path),
                message="Permission denied"
            ))
            skipped_files += 1
            continue

        except OSError as e:
            # Handle disk full, file too large, etc.
            logger.error(f"OS error reading {file_path}: {e}")
            if "No space left on device" in str(e):
                issues.append(AnalysisIssue(
                    category=ErrorCategory.DISK_FULL,
                    severity="error",
                    file_path=str(file_path),
                    message="No space left on device"
                ))
            else:
                issues.append(AnalysisIssue(
                    category=ErrorCategory.IO_ERROR,
                    severity="error",
                    file_path=str(file_path),
                    message=f"OS error: {str(e)}"
                ))
            skipped_files += 1
            continue

        except MemoryError as e:
            logger.error(f"Memory error reading {file_path} (file too large)")
            issues.append(AnalysisIssue(
                category=ErrorCategory.MEMORY_ERROR,
                severity="error",
                file_path=str(file_path),
                message="File too large to fit in memory"
            ))
            skipped_files += 1
            continue

        except Exception as e:
            logger.error(f"Unexpected error reading {file_path}: {e}")
            issues.append(AnalysisIssue(
                category=ErrorCategory.GENERAL_ERROR,
                severity="error",
                file_path=str(file_path),
                message=f"Unexpected error: {str(e)}"
            ))
            skipped_files += 1
            continue

    if not args.quiet:
        progress.complete(count=len(files_content))

    logger.info(f"Successfully read {len(files_content)} files, skipped {skipped_files}")

    # Step 2: Duplicate detection
    all_duplicates = []

    # Determine which detection engines to run
    run_exact = args.exact_only or not (args.structural_only or args.pattern_only)
    run_structural = args.structural_only or not (args.exact_only or args.pattern_only)
    run_pattern = args.pattern_only or not (args.exact_only or args.structural_only)

    # Run exact duplicate detection
    if run_exact:
        progress = ProgressIndicator("Detecting exact duplicates")
        if not args.quiet:
            progress.start()

        try:
            exact_dups = find_exact_duplicates(
                files_content,
                min_lines=args.min_lines,
                min_chars=args.min_chars
            )
            all_duplicates.extend(exact_dups)
            logger.info(f"Found {len(exact_dups)} exact duplicates")

            if not args.quiet:
                progress.complete(count=len(exact_dups))
        except Exception as e:
            logger.error(f"Error in exact duplicate detection: {e}")
            issues.append(AnalysisIssue(
                category=ErrorCategory.GENERAL_ERROR,
                severity="error",
                file_path=None,
                message=f"Exact duplicate detection failed: {str(e)}"
            ))
            if not args.quiet:
                progress.complete(count=0)
                print(f"\n⚠️  Exact duplicate detection failed: {e}")

    # Run structural duplicate detection
    if run_structural:
        progress = ProgressIndicator("Detecting structural duplicates")
        if not args.quiet:
            progress.start()

        try:
            structural_dups = find_structural_duplicates(
                files_content,
                similarity_threshold=0.85,
                min_lines=args.min_lines
            )
            all_duplicates.extend(structural_dups)
            logger.info(f"Found {len(structural_dups)} structural duplicates")

            if not args.quiet:
                progress.complete(count=len(structural_dups))
        except Exception as e:
            logger.error(f"Error in structural duplicate detection: {e}")
            issues.append(AnalysisIssue(
                category=ErrorCategory.GENERAL_ERROR,
                severity="error",
                file_path=None,
                message=f"Structural duplicate detection failed: {str(e)}"
            ))
            if not args.quiet:
                progress.complete(count=0)
                print(f"\n⚠️  Structural duplicate detection failed: {e}")

    # Run pattern duplicate detection
    if run_pattern:
        progress = ProgressIndicator("Detecting pattern duplicates")
        if not args.quiet:
            progress.start()

        try:
            pattern_dups = detect_pattern_duplicates(
                files_content,
                patterns=None,  # Use default pattern catalog
                min_occurrences=3
            )
            all_duplicates.extend(pattern_dups)
            logger.info(f"Found {len(pattern_dups)} pattern duplicates")

            if not args.quiet:
                progress.complete(count=len(pattern_dups))
        except Exception as e:
            logger.error(f"Error in pattern duplicate detection: {e}")
            issues.append(AnalysisIssue(
                category=ErrorCategory.GENERAL_ERROR,
                severity="error",
                file_path=None,
                message=f"Pattern duplicate detection failed: {str(e)}"
            ))
            if not args.quiet:
                progress.complete(count=0)
                print(f"\n⚠️  Pattern duplicate detection failed: {e}")

    # Step 3: Metrics calculation
    progress = ProgressIndicator("Calculating metrics")
    if not args.quiet:
        progress.start()

    try:
        summary = calculate_metrics(all_duplicates, files_content)
        # Add issues and skipped files to summary
        summary.issues = issues
        summary.skipped_files = skipped_files

        offenders = rank_offenders(all_duplicates, files_content, top_n=20)
        heatmap = generate_heatmap_data(files_content, all_duplicates)
        trends = analyze_duplication_trends(all_duplicates)
        logger.info("Metrics calculation completed")

        if not args.quiet:
            progress.complete()
    except Exception as e:
        logger.error(f"Error calculating metrics: {e}")
        print(f"\n❌ Error: Failed to calculate metrics: {e}", file=sys.stderr)
        return EXIT_FAILURE

    # Step 4: Report generation
    progress = ProgressIndicator("Generating report")
    if not args.quiet:
        progress.start()

    try:
        report = generate_report(
            duplicates=all_duplicates,
            summary=summary,
            offenders=offenders,
            heatmap=heatmap,
            output_path=args.output,
            max_duplicates=args.max_duplicates
        )
        logger.info(f"Report generated: {args.output}")

        if not args.quiet:
            progress.complete()
    except OSError as e:
        logger.error(f"Error writing report: {e}")
        if "No space left on device" in str(e):
            print(f"\n❌ Error: Cannot write report - disk full", file=sys.stderr)
        else:
            print(f"\n❌ Error: Cannot write report: {e}", file=sys.stderr)
        return EXIT_FAILURE
    except Exception as e:
        logger.error(f"Error generating report: {e}")
        print(f"\n❌ Error: Failed to generate report: {e}", file=sys.stderr)
        return EXIT_FAILURE

    # CSV export (optional)
    if args.csv:
        progress = ProgressIndicator("Exporting CSV")
        if not args.quiet:
            progress.start()

        try:
            generate_csv_export(all_duplicates, args.csv)
            logger.info(f"CSV exported: {args.csv}")

            if not args.quiet:
                progress.complete()
        except Exception as e:
            logger.error(f"Error exporting CSV: {e}")
            print(f"\n⚠️  Warning: Failed to export CSV: {e}")
            # Continue anyway - CSV export is optional

    # Step 5: Display summary
    print()
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("📊 Analysis Complete")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print()
    print(f"Files analyzed: {summary.total_files}")
    print(f"Total LOC: {summary.total_loc:,}")
    print(f"Duplicate LOC: {summary.duplicate_loc:,}")

    duplication_pct = (summary.duplicate_loc / summary.total_loc * 100) if summary.total_loc > 0 else 0
    print(f"Duplication: {duplication_pct:.2f}%")
    print()

    print(f"Duplicate blocks found: {summary.duplicate_blocks}")
    print(f"  - Exact: {summary.exact_blocks}")
    print(f"  - Structural: {summary.structural_blocks}")
    print(f"  - Pattern: {summary.pattern_blocks}")
    print()

    if trends['most_duplicated_type']:
        print(f"Most common type: {trends['most_duplicated_type']}")
        print(f"Avg instances per duplicate: {trends['avg_instances_per_duplicate']}")
        print(f"Largest duplicate block: {trends['largest_duplicate_block']} lines")
        print()

    print(f"📄 Report: {args.output.absolute()}")

    if args.csv:
        print(f"📊 CSV Export: {args.csv.absolute()}")

    print()

    # Assessment
    if duplication_pct < 5:
        print("✅ Excellent - Minimal duplication detected")
    elif duplication_pct < 10:
        print("✅ Good - Low duplication, minor cleanup opportunities")
    elif duplication_pct < 20:
        print("⚠️  Moderate - Noticeable duplication, refactoring recommended")
    elif duplication_pct < 30:
        print("⚠️  High - Significant duplication, refactoring needed")
    else:
        print("🔴 Critical - Excessive duplication, immediate action required")

    print()

    # Report issues if any
    if issues:
        error_count = sum(1 for i in issues if i.severity == "error")
        warning_count = sum(1 for i in issues if i.severity == "warning")

        if error_count > 0:
            print(f"⚠️  Analysis completed with {error_count} error(s) and {warning_count} warning(s)")
            print(f"   See report for details: {args.output}")
            logger.warning(f"Analysis had {error_count} errors, {warning_count} warnings")
        elif warning_count > 0:
            print(f"⚠️  Analysis completed with {warning_count} warning(s)")
            logger.info(f"Analysis had {warning_count} warnings")

    # Determine exit code
    if summary.error_count > 0:
        # Had errors but completed
        logger.info("Analysis completed with errors")
        return EXIT_PARTIAL_SUCCESS
    elif summary.warning_count > 0:
        # Had warnings but completed successfully
        logger.info("Analysis completed with warnings")
        return EXIT_PARTIAL_SUCCESS
    else:
        # Clean success
        logger.info("Analysis completed successfully")
        return EXIT_SUCCESS


def main():
    """
    Main entry point.

    Exit codes:
        0 = Success
        1 = User error (invalid input)
        2 = Partial success (warnings but completed)
        3 = Failure (errors prevented completion)
        130 = Interrupted by user

    Example:
        >>> # From command line:
        >>> # python cli.py /path/to/code
    """
    try:
        args = parse_arguments()
        exit_code = run_analysis(args)
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️  Analysis interrupted by user", file=sys.stderr)
        sys.exit(130)
    except MemoryError:
        print("\n❌ Error: Out of memory - codebase too large", file=sys.stderr)
        print("   Try analyzing a smaller directory or increasing system memory", file=sys.stderr)
        sys.exit(EXIT_FAILURE)
    except Exception as e:
        print(f"\n❌ Fatal Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(EXIT_FAILURE)


if __name__ == '__main__':
    main()
