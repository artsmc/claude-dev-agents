"""
Batch query processing for DeepWiki skill.

This module provides functions for parsing and executing multiple queries
in batch mode with cache-aware execution.
"""

import json
import sys
import time
from typing import List, Dict, Any, Optional


def parse_queries(args) -> List[str]:
    """
    Parse queries from command-line arguments.

    Supports three input modes:
    1. Single query: args.query
    2. Comma-separated queries: args.queries
    3. JSON file with queries: args.queries_file

    Args:
        args: Command-line arguments (argparse.Namespace)

    Returns:
        List of query strings

    Raises:
        ValueError: If no query provided or invalid format
        FileNotFoundError: If queries file doesn't exist
        json.JSONDecodeError: If queries file is invalid JSON

    Examples:
        # Single query
        >>> args = argparse.Namespace(query="How does auth work?", queries=None, queries_file=None)
        >>> parse_queries(args)
        ['How does auth work?']

        # Comma-separated
        >>> args = argparse.Namespace(query=None, queries="q1,q2,q3", queries_file=None)
        >>> parse_queries(args)
        ['q1', 'q2', 'q3']

        # From JSON file
        >>> args = argparse.Namespace(query=None, queries=None, queries_file="queries.json")
        >>> parse_queries(args)  # Assuming file contains {"queries": ["q1", "q2"]}
        ['q1', 'q2']
    """
    # Priority: queries-file > queries > query
    if args.queries_file:
        return _parse_queries_from_file(args.queries_file)
    elif args.queries:
        return _parse_queries_from_string(args.queries)
    elif args.query:
        return [args.query]
    else:
        raise ValueError("No query provided. Use positional query, --queries, or --queries-file")


def _parse_queries_from_string(queries_str: str) -> List[str]:
    """
    Parse comma-separated queries.

    Args:
        queries_str: Comma-separated query string

    Returns:
        List of query strings (stripped)

    Examples:
        >>> _parse_queries_from_string("q1, q2, q3")
        ['q1', 'q2', 'q3']
    """
    queries = [q.strip() for q in queries_str.split(",")]

    # Filter out empty queries
    queries = [q for q in queries if q]

    if not queries:
        raise ValueError("No valid queries found in comma-separated list")

    return queries


def _parse_queries_from_file(file_path: str) -> List[str]:
    """
    Parse queries from JSON file.

    Expected format:
    {
      "queries": ["query1", "query2", "query3"]
    }

    Args:
        file_path: Path to JSON file

    Returns:
        List of query strings

    Raises:
        FileNotFoundError: If file doesn't exist
        json.JSONDecodeError: If file is invalid JSON
        ValueError: If file format is invalid

    Examples:
        >>> _parse_queries_from_file("queries.json")
        ['query1', 'query2', 'query3']
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Queries file not found: {file_path}")
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(
            f"Invalid JSON in queries file: {file_path}",
            e.doc,
            e.pos
        )

    # Validate schema
    if not isinstance(data, dict):
        raise ValueError(f"Queries file must contain a JSON object, got {type(data).__name__}")

    if "queries" not in data:
        raise ValueError("Queries file must have a 'queries' field")

    if not isinstance(data["queries"], list):
        raise ValueError(f"'queries' field must be an array, got {type(data['queries']).__name__}")

    queries = data["queries"]

    # Validate each query is a string
    for i, query in enumerate(queries):
        if not isinstance(query, str):
            raise ValueError(f"Query at index {i} must be a string, got {type(query).__name__}")

    # Filter out empty queries
    queries = [q.strip() for q in queries if q.strip()]

    if not queries:
        raise ValueError("No valid queries found in file")

    return queries


def execute_batch_queries(
    repo_url: str,
    queries: List[str],
    conn,
    execute_query_func,
    timeout: int = 60,
    inter_query_delay: float = 2.0,
    verbose: bool = False
) -> Dict[str, Any]:
    """
    Execute multiple queries in batch mode.

    Queries are executed sequentially with cache checking:
    1. Check cache for each query
    2. If cache hit: Use cached result (fast)
    3. If cache miss: Execute query and cache result
    4. Add delay between uncached queries (rate limiting)
    5. Continue on error (collect partial results)

    Args:
        repo_url: GitHub repository URL
        queries: List of query strings
        conn: SQLite database connection
        execute_query_func: Function to execute a single query
        timeout: Query timeout in seconds
        inter_query_delay: Delay between uncached queries (seconds)
        verbose: Enable verbose logging

    Returns:
        Dictionary with batch results:
        {
            "status": "success"|"partial"|"error",
            "total_queries": int,
            "successful": int,
            "failed": int,
            "cache_hits": int,
            "cache_misses": int,
            "results": [
                {
                    "query": str,
                    "status": "success"|"error",
                    "cached": bool,
                    "answer": str,  # if success
                    "sources": list,  # if success
                    "error": str,  # if error
                    "error_type": str  # if error
                }
            ]
        }

    Examples:
        >>> results = execute_batch_queries(
        ...     "https://github.com/redis/redis",
        ...     ["query1", "query2", "query3"],
        ...     conn,
        ...     execute_query,
        ...     timeout=60
        ... )
        >>> results["total_queries"]
        3
    """
    from cache import cache_lookup, cache_store, hash_query
    from formatter import create_success_result, create_error_result

    if verbose:
        print(f"\n[Batch] Executing {len(queries)} queries...", file=sys.stderr)

    results = []
    successful = 0
    failed = 0
    cache_hits = 0
    cache_misses = 0

    for i, query in enumerate(queries, 1):
        if verbose:
            print(f"[Batch] Query {i}/{len(queries)}: {query[:50]}...", file=sys.stderr)

        try:
            # Check cache first
            cached_result = cache_lookup(conn, repo_url, query)

            if cached_result:
                # Cache hit
                cache_hits += 1
                successful += 1

                if verbose:
                    print(f"[Batch] ✓ Cache HIT", file=sys.stderr)

                result = create_success_result(
                    repo_url=repo_url,
                    query=query,
                    answer=cached_result["answer"],
                    sources=cached_result["sources"],
                    cached=True,
                    timestamp=cached_result["created_at"],
                    cache_id=cached_result["id"]
                )

            else:
                # Cache miss - execute query
                cache_misses += 1

                if verbose:
                    print(f"[Batch] ✗ Cache MISS - Executing query...", file=sys.stderr)

                # Execute query
                query_result = execute_query_func(
                    repo_url,
                    query,
                    timeout=timeout,
                    verbose=False  # Don't nest verbose output
                )

                # Store in cache
                cache_store(
                    conn,
                    repo_url,
                    query,
                    query_result["answer"],
                    query_result["sources"],
                    int(time.time())
                )

                successful += 1

                if verbose:
                    print(f"[Batch] ✓ Query completed", file=sys.stderr)

                result = create_success_result(
                    repo_url=repo_url,
                    query=query,
                    answer=query_result["answer"],
                    sources=query_result["sources"],
                    cached=False
                )

                # Add delay between uncached queries (rate limiting)
                if i < len(queries):  # Don't delay after last query
                    if verbose:
                        print(f"[Batch] Waiting {inter_query_delay}s before next query...", file=sys.stderr)
                    time.sleep(inter_query_delay)

            results.append(result)

        except Exception as e:
            # Query failed - log and continue
            failed += 1

            if verbose:
                print(f"[Batch] ✗ Query failed: {type(e).__name__}: {e}", file=sys.stderr)

            error_result = create_error_result(
                repo_url=repo_url,
                query=query,
                error=str(e),
                error_type=type(e).__name__
            )

            results.append(error_result)

    # Determine overall status
    if failed == 0:
        status = "success"
    elif successful == 0:
        status = "error"
    else:
        status = "partial"

    batch_summary = {
        "status": status,
        "total_queries": len(queries),
        "successful": successful,
        "failed": failed,
        "cache_hits": cache_hits,
        "cache_misses": cache_misses,
        "results": results
    }

    if verbose:
        print(f"\n[Batch] Complete: {successful}/{len(queries)} successful, {cache_hits} cache hits", file=sys.stderr)

    return batch_summary


def format_batch_results(batch_summary: Dict[str, Any], output_format: str = "json") -> str:
    """
    Format batch query results for output.

    Args:
        batch_summary: Batch summary from execute_batch_queries()
        output_format: "json" or "markdown"

    Returns:
        Formatted string

    Examples:
        >>> summary = {"status": "success", "total_queries": 3, ...}
        >>> formatted = format_batch_results(summary, output_format="json")
        >>> formatted.startswith("{")
        True
    """
    if output_format == "json":
        return json.dumps(batch_summary, indent=2, ensure_ascii=False)
    elif output_format == "markdown":
        return _format_batch_markdown(batch_summary)
    else:
        raise ValueError(f"Unsupported output format: {output_format}")


def _format_batch_markdown(batch_summary: Dict[str, Any]) -> str:
    """Format batch results as Markdown."""
    lines = []

    # Header
    lines.append("# DeepWiki Batch Query Results\n")

    # Status
    status = batch_summary["status"]
    if status == "success":
        status_emoji = "✅"
    elif status == "partial":
        status_emoji = "⚠️"
    else:
        status_emoji = "❌"

    lines.append(f"**Status:** {status_emoji} {status.upper()}\n")

    # Summary statistics
    lines.append("## Summary\n")
    lines.append(f"- **Total Queries:** {batch_summary['total_queries']}")
    lines.append(f"- **Successful:** {batch_summary['successful']} ✅")
    lines.append(f"- **Failed:** {batch_summary['failed']} ❌")
    lines.append(f"- **Cache Hits:** {batch_summary['cache_hits']} 🎯")
    lines.append(f"- **Cache Misses:** {batch_summary['cache_misses']} ⚡\n")

    # Individual results
    lines.append("## Query Results\n")

    for i, result in enumerate(batch_summary["results"], 1):
        # Query header
        query = result["query"]
        status = result["status"]
        cached = result.get("cached", False)

        if status == "success":
            icon = "✅"
            cache_icon = "🎯" if cached else "⚡"
        else:
            icon = "❌"
            cache_icon = ""

        lines.append(f"### {i}. {icon} {cache_icon} Query\n")
        lines.append(f"> {query}\n")

        if status == "success":
            # Answer
            lines.append(f"**Answer:** {result['answer']}\n")

            # Sources
            sources = result.get("sources", [])
            if sources:
                if isinstance(sources, str):
                    try:
                        sources = json.loads(sources)
                    except (json.JSONDecodeError, TypeError):
                        sources = [s.strip() for s in sources.replace(",", "\n").split("\n") if s.strip()]

                if isinstance(sources, list) and sources:
                    lines.append("**Sources:**")
                    for source in sources:
                        lines.append(f"  - `{source}`")
                    lines.append("")
        else:
            # Error
            lines.append(f"**Error:** {result.get('error', 'Unknown error')}\n")
            lines.append(f"**Error Type:** {result.get('error_type', 'Error')}\n")

        lines.append("---\n")

    return "\n".join(lines)
