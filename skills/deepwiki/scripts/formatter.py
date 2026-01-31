"""
Output formatters for DeepWiki query results.

Supports two output formats:
- JSON: Structured data for programmatic consumption
- Markdown: Human-readable format for documentation
"""

import json
import sys
from typing import Dict, Any, Optional
from datetime import datetime


def format_json(result: Dict[str, Any], indent: int = 2) -> str:
    """
    Format result as JSON.

    Args:
        result: Query result dictionary
        indent: Indentation level (default: 2)

    Returns:
        JSON string

    Example:
        >>> result = {"status": "success", "answer": "Yes"}
        >>> print(format_json(result))
        {
          "status": "success",
          "answer": "Yes"
        }
    """
    return json.dumps(result, indent=indent, ensure_ascii=False)


def format_markdown(result: Dict[str, Any]) -> str:
    """
    Format result as Markdown.

    Args:
        result: Query result dictionary

    Returns:
        Markdown-formatted string

    Example:
        >>> result = {
        ...     "status": "success",
        ...     "repo": {"url": "https://github.com/redis/redis"},
        ...     "query": "Does this support persistence?",
        ...     "answer": "Yes, Redis supports RDB and AOF.",
        ...     "sources": ["src/rdb.c", "src/aof.c"]
        ... }
        >>> print(format_markdown(result))
        # DeepWiki Query Result
        ...
    """
    lines = []

    # Header
    lines.append("# DeepWiki Query Result\n")

    # Status indicator
    status = result.get("status", "unknown")
    if status == "success":
        status_emoji = "✅"
    elif status == "error":
        status_emoji = "❌"
    else:
        status_emoji = "ℹ️"

    lines.append(f"**Status:** {status_emoji} {status.upper()}\n")

    # Cache indicator
    if result.get("cached"):
        lines.append(f"**Cache:** 🎯 HIT (from cache)\n")
    else:
        lines.append(f"**Cache:** ⚡ MISS (fresh query)\n")

    # Repository info
    repo = result.get("repo", {})
    if repo:
        lines.append(f"**Repository:** {repo.get('url', 'N/A')}\n")
        if "deepwiki_url" in repo:
            lines.append(f"**DeepWiki URL:** {repo['deepwiki_url']}\n")

    lines.append("")  # Blank line

    # Query
    query = result.get("query", "N/A")
    lines.append("## Query\n")
    lines.append(f"> {query}\n")
    lines.append("")

    # Answer
    answer = result.get("answer", "N/A")
    lines.append("## Answer\n")
    lines.append(f"{answer}\n")
    lines.append("")

    # Sources
    sources = result.get("sources", [])
    if sources:
        lines.append("## Sources\n")

        # Parse sources (could be list or string)
        if isinstance(sources, str):
            # Try to parse as JSON array
            try:
                sources = json.loads(sources)
            except (json.JSONDecodeError, TypeError):
                # Split by common delimiters
                sources = [s.strip() for s in sources.replace(",", "\n").split("\n") if s.strip()]

        if isinstance(sources, list):
            for i, source in enumerate(sources, 1):
                lines.append(f"{i}. `{source}`")
        else:
            lines.append(f"- {sources}")

        lines.append("")

    # Timestamp
    timestamp = result.get("timestamp", "N/A")
    if timestamp != "N/A":
        lines.append(f"**Timestamp:** {timestamp}\n")

    # Cache ID (if cached)
    if result.get("cached") and "cache_id" in result:
        lines.append(f"**Cache ID:** {result['cache_id']}\n")

    # Error details (if error)
    if status == "error" and "error" in result:
        lines.append("## Error Details\n")
        lines.append(f"```\n{result['error']}\n```\n")

    return "\n".join(lines)


def output_result(result: Dict[str, Any], output_format: str = "json", verbose: bool = False) -> None:
    """
    Output result in the specified format.

    Args:
        result: Query result dictionary
        output_format: Output format ("json" or "markdown")
        verbose: Enable verbose logging to stderr

    Example:
        >>> result = {"status": "success", "answer": "Yes"}
        >>> output_result(result, output_format="json")
        {
          "status": "success",
          "answer": "Yes"
        }
    """
    if verbose:
        print(f"\n[Output] Formatting as {output_format.upper()}...", file=sys.stderr)

    if output_format == "json":
        formatted = format_json(result)
    elif output_format == "markdown":
        formatted = format_markdown(result)
    else:
        raise ValueError(f"Unsupported output format: {output_format}. Use 'json' or 'markdown'.")

    print(formatted)

    if verbose:
        print(f"[Output] ✓ Output complete\n", file=sys.stderr)


def create_success_result(
    repo_url: str,
    query: str,
    answer: str,
    sources: Any,
    cached: bool = False,
    timestamp: Optional[str] = None,
    cache_id: Optional[int] = None
) -> Dict[str, Any]:
    """
    Create a success result dictionary.

    Args:
        repo_url: GitHub repository URL
        query: Query text
        answer: Answer text
        sources: List of source files or JSON string
        cached: Whether result is from cache
        timestamp: ISO timestamp string
        cache_id: Cache entry ID (if cached)

    Returns:
        Structured result dictionary

    Example:
        >>> result = create_success_result(
        ...     "https://github.com/redis/redis",
        ...     "Does this support clustering?",
        ...     "Yes, Redis Cluster provides automatic sharding.",
        ...     ["cluster.c", "cluster.h"],
        ...     cached=False
        ... )
        >>> result["status"]
        'success'
    """
    # Extract owner/repo from GitHub URL
    github_path = repo_url.split("github.com/", 1)[-1]
    deepwiki_url = f"https://deepwiki.com/github.com/{github_path}"

    result = {
        "status": "success",
        "cached": cached,
        "repo": {
            "url": repo_url,
            "deepwiki_url": deepwiki_url
        },
        "query": query,
        "answer": answer,
        "sources": sources,
        "timestamp": timestamp or datetime.utcnow().isoformat() + "Z"
    }

    if cached and cache_id is not None:
        result["cache_id"] = cache_id

    return result


def create_error_result(
    repo_url: str,
    query: str,
    error: str,
    error_type: str = "Error"
) -> Dict[str, Any]:
    """
    Create an error result dictionary.

    Args:
        repo_url: GitHub repository URL
        query: Query text
        error: Error message
        error_type: Error type (e.g., "TimeoutError", "NavigationError")

    Returns:
        Structured error dictionary

    Example:
        >>> result = create_error_result(
        ...     "https://github.com/redis/redis",
        ...     "Does this work?",
        ...     "Query timed out after 60 seconds",
        ...     error_type="TimeoutError"
        ... )
        >>> result["status"]
        'error'
    """
    # Extract owner/repo from GitHub URL
    github_path = repo_url.split("github.com/", 1)[-1]
    deepwiki_url = f"https://deepwiki.com/github.com/{github_path}"

    return {
        "status": "error",
        "repo": {
            "url": repo_url,
            "deepwiki_url": deepwiki_url
        },
        "query": query,
        "error": error,
        "error_type": error_type,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }


class ProgressIndicator:
    """
    Progress indicator for multi-step operations.

    Example:
        >>> progress = ProgressIndicator(total_steps=6, verbose=True)
        >>> progress.step("Validating inputs")
        [1/6] Validating inputs...
        >>> progress.complete("Inputs validated")
        [1/6] ✓ Inputs validated
    """

    def __init__(self, total_steps: int, verbose: bool = False):
        """
        Initialize progress indicator.

        Args:
            total_steps: Total number of steps
            verbose: Enable progress output to stderr
        """
        self.total_steps = total_steps
        self.current_step = 0
        self.verbose = verbose

    def step(self, message: str) -> None:
        """
        Start a new step.

        Args:
            message: Step description
        """
        if not self.verbose:
            return

        self.current_step += 1
        print(f"[{self.current_step}/{self.total_steps}] {message}...", file=sys.stderr)

    def complete(self, message: str) -> None:
        """
        Mark current step as complete.

        Args:
            message: Completion message
        """
        if not self.verbose:
            return

        print(f"  ✓ {message}", file=sys.stderr)

    def substep(self, message: str) -> None:
        """
        Show a substep within the current step.

        Args:
            message: Substep description
        """
        if not self.verbose:
            return

        print(f"  • {message}", file=sys.stderr)

    def error(self, message: str) -> None:
        """
        Show an error message.

        Args:
            message: Error description
        """
        if not self.verbose:
            return

        print(f"  ✗ {message}", file=sys.stderr)

    def blank_line(self) -> None:
        """Print a blank line to stderr."""
        if self.verbose:
            print("", file=sys.stderr)


# Module-level progress indicator (singleton pattern)
_progress: Optional[ProgressIndicator] = None


def init_progress(total_steps: int, verbose: bool = False) -> ProgressIndicator:
    """
    Initialize the module-level progress indicator.

    Args:
        total_steps: Total number of steps
        verbose: Enable progress output

    Returns:
        ProgressIndicator instance
    """
    global _progress
    _progress = ProgressIndicator(total_steps, verbose)
    return _progress


def get_progress() -> Optional[ProgressIndicator]:
    """
    Get the current progress indicator.

    Returns:
        ProgressIndicator instance or None
    """
    return _progress
