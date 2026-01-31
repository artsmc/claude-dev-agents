#!/usr/bin/env python3
"""
DeepWiki Skill - Query GitHub repositories using DeepWiki AI

This script provides a command-line interface to query GitHub repositories
through DeepWiki's AI-powered code understanding service.
"""

import argparse
import sys


def parse_arguments():
    """
    Parse and validate command-line arguments.

    Returns:
        argparse.Namespace: Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="Query GitHub repositories using DeepWiki AI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Single query
  %(prog)s https://github.com/owner/repo "How does authentication work?"

  # Batch queries (comma-separated)
  %(prog)s https://github.com/owner/repo --queries "How is auth implemented?,What is the API structure?"

  # Batch queries from file
  %(prog)s https://github.com/owner/repo --queries-file queries.json

  # Force refresh (bypass cache)
  %(prog)s https://github.com/owner/repo "query" --force-refresh

  # Markdown output
  %(prog)s https://github.com/owner/repo "query" --format markdown

  # Cache management
  %(prog)s --cache-stats
  %(prog)s --cache-clear
  %(prog)s --cache-clear https://github.com/owner/repo

For more information, see: ~/.claude/skills/deepwiki/SKILL.md
        """
    )

    # Positional arguments
    parser.add_argument(
        "github_url",
        nargs="?",
        help="GitHub repository URL (e.g., https://github.com/owner/repo)"
    )

    parser.add_argument(
        "query",
        nargs="?",
        help="Query text for single query mode"
    )

    # Query modes
    query_group = parser.add_argument_group("query modes")
    query_group.add_argument(
        "--queries",
        metavar="QUERIES",
        help="Comma-separated list of queries for batch mode"
    )

    query_group.add_argument(
        "--queries-file",
        metavar="FILE",
        help="Path to JSON file containing queries (format: {\"queries\": [\"q1\", \"q2\"]})"
    )

    # Output options
    output_group = parser.add_argument_group("output options")
    output_group.add_argument(
        "--format",
        choices=["json", "markdown"],
        default="json",
        help="Output format (default: json)"
    )

    output_group.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose output with detailed logging"
    )

    # Cache options
    cache_group = parser.add_argument_group("cache options")
    cache_group.add_argument(
        "--force-refresh",
        action="store_true",
        help="Bypass cache and fetch fresh results"
    )

    cache_group.add_argument(
        "--cache-stats",
        action="store_true",
        help="Display cache statistics and exit"
    )

    cache_group.add_argument(
        "--cache-clear",
        nargs="?",
        const="__ALL__",
        metavar="REPO_URL",
        help="Clear cache (all entries or specific repo)"
    )

    # Browser automation options
    browser_group = parser.add_argument_group("browser automation options")
    browser_group.add_argument(
        "--timeout",
        type=int,
        default=60,
        metavar="SECONDS",
        help="Query timeout in seconds (default: 60, range: 10-600)"
    )

    browser_group.add_argument(
        "--max-retries",
        type=int,
        default=3,
        metavar="N",
        help="Maximum number of retry attempts (default: 3, range: 1-5)"
    )

    browser_group.add_argument(
        "--retry-backoff",
        type=int,
        default=5,
        metavar="SECONDS",
        help="Retry backoff base in seconds (default: 5)"
    )

    # Development options
    dev_group = parser.add_argument_group("development options")
    dev_group.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode with extra diagnostics"
    )

    args = parser.parse_args()

    # Validation: Ensure cache commands don't require other arguments
    if args.cache_stats:
        return args

    if args.cache_clear is not None:
        return args

    # Validation: Require github_url for query operations
    if not args.github_url:
        parser.error("github_url is required for query operations")

    # Validation: Ensure exactly one query mode is active
    query_modes = sum([
        bool(args.query),
        bool(args.queries),
        bool(args.queries_file)
    ])

    if query_modes == 0:
        parser.error("one of the following is required: query, --queries, --queries-file")

    if query_modes > 1:
        parser.error("only one query mode can be used at a time")

    # Validation: Timeout range
    if args.timeout < 10 or args.timeout > 600:
        parser.error("timeout must be between 10 and 600 seconds")

    # Validation: Max retries range
    if args.max_retries < 1 or args.max_retries > 5:
        parser.error("max-retries must be between 1 and 5")

    # Validation: Retry backoff range
    if args.retry_backoff < 1:
        parser.error("retry-backoff must be at least 1 second")

    return args


def main():
    """Main entry point for the DeepWiki skill."""
    try:
        args = parse_arguments()

        # For now, just print parsed arguments (implementation will come in later tasks)
        if args.verbose or args.debug:
            print(f"Parsed arguments: {args}", file=sys.stderr)

        # Placeholder - actual implementation will be added in subsequent tasks
        print("DeepWiki skill argument parser ready!", file=sys.stderr)
        print("Implementation coming in Task 2.x (Browser Automation)", file=sys.stderr)

        return 0

    except KeyboardInterrupt:
        print("\n\nInterrupted by user", file=sys.stderr)
        return 130

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if args.debug if 'args' in locals() else False:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
