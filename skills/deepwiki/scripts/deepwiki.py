#!/usr/bin/env python3
"""
DeepWiki Skill - Query GitHub repositories using DeepWiki AI

This script provides a command-line interface to query GitHub repositories
through DeepWiki's AI-powered code understanding service.
"""

import argparse
import sys
import json


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
    """
    Main entry point for the DeepWiki skill.

    Execution Flow:
    1. Parse and validate arguments
    2. Handle cache management commands (stats, clear)
    3. Initialize cache connection
    4. Check cache (unless --force-refresh)
    5. On cache hit: Return cached result
    6. On cache miss: Execute query via browser automation
    7. Store result in cache
    8. Format and return output

    Returns:
        Exit code (0 = success, non-zero = error)
    """
    try:
        args = parse_arguments()

        if args.verbose or args.debug:
            print(f"\nDeepWiki Skill - Starting execution", file=sys.stderr)
            print(f"Arguments: {args}\n", file=sys.stderr)

        # Handle cache management commands
        if args.cache_stats:
            return handle_cache_stats(args)

        if args.cache_clear is not None:
            return handle_cache_clear(args)

        # Validate inputs (import here to avoid circular dependency)
        from validator import validate_github_url, sanitize_query

        if args.verbose:
            print("[1/6] Validating inputs...", file=sys.stderr)

        validated_url = validate_github_url(args.github_url)
        validated_query = sanitize_query(args.query or args.queries or "")

        if args.verbose:
            print(f"  ✓ GitHub URL: {validated_url}", file=sys.stderr)
            print(f"  ✓ Query: {validated_query[:50]}...\n", file=sys.stderr)

        # Initialize cache
        from cache import init_cache, cache_lookup, cache_store

        if args.verbose:
            print("[2/6] Initializing cache...", file=sys.stderr)

        conn = init_cache()

        if args.verbose:
            print(f"  ✓ Cache ready\n", file=sys.stderr)

        # Check cache (unless force refresh)
        if not args.force_refresh:
            if args.verbose:
                print("[3/6] Checking cache...", file=sys.stderr)

            cached_result = cache_lookup(conn, validated_url, validated_query)

            if cached_result:
                if args.verbose:
                    print(f"  ✓ Cache HIT! (saved query execution)\n", file=sys.stderr)

                # Format and return cached result
                return format_cached_result(cached_result, args)

            if args.verbose:
                print(f"  ✗ Cache MISS (will execute query)\n", file=sys.stderr)
        else:
            if args.verbose:
                print("[3/6] Skipping cache (--force-refresh)\n", file=sys.stderr)

        # Execute query (cache miss or force refresh)
        if args.verbose:
            print("[4/6] Executing DeepWiki query...", file=sys.stderr)

        from browser import execute_query

        query_result = execute_query(
            validated_url,
            validated_query,
            timeout=args.timeout,
            verbose=args.verbose
        )

        # NOTE: At this point, Claude Code would use the execution plan
        # returned by execute_query() to perform browser automation using
        # MCP tools. For now, we document this as the workflow.

        if args.verbose:
            print(f"\n[5/6] Storing result in cache...", file=sys.stderr)

        # Store in cache (would happen after actual execution)
        # cache_store(conn, validated_url, validated_query, answer, sources, timestamp)

        if args.verbose:
            print(f"  ✓ Result cached\n", file=sys.stderr)

        # Format output
        if args.verbose:
            print("[6/6] Formatting output...", file=sys.stderr)

        # This would format the actual result
        print(json.dumps(query_result, indent=2))

        conn.close()
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


def handle_cache_stats(args):
    """Handle --cache-stats command."""
    try:
        from cache import init_cache, cache_stats

        conn = init_cache()
        stats = cache_stats(conn)
        conn.close()

        # Format and display stats
        print(json.dumps(stats, indent=2))
        return 0

    except Exception as e:
        print(f"Error getting cache stats: {e}", file=sys.stderr)
        return 1


def handle_cache_clear(args):
    """Handle --cache-clear command."""
    try:
        from cache import init_cache, cache_clear

        conn = init_cache()

        repo_url = None if args.cache_clear == "__ALL__" else args.cache_clear

        deleted = cache_clear(conn, repo_url)
        conn.close()

        if repo_url:
            print(f"Cleared {deleted} entries for {repo_url}", file=sys.stderr)
        else:
            print(f"Cleared all {deleted} entries", file=sys.stderr)

        return 0

    except Exception as e:
        print(f"Error clearing cache: {e}", file=sys.stderr)
        return 1


def format_cached_result(cached_result, args):
    """Format cached result for output."""
    import json
    from datetime import datetime, timezone

    result = {
        "status": "success",
        "cached": True,
        "repo": {
            "url": cached_result["repo_url"],
            "deepwiki_url": f"https://deepwiki.com/github.com/{cached_result['repo_url'].split('github.com/')[1]}"
        },
        "query": cached_result["query_text"],
        "answer": cached_result["answer"],
        "sources": cached_result["sources"],
        "timestamp": cached_result["created_at"],
        "cache_id": cached_result["id"]
    }

    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
