"""
Input validation module for DeepWiki skill.

This module provides validation functions for user inputs to prevent
security vulnerabilities and ensure data integrity.
"""

import re
import json
from pathlib import Path
from typing import List, Dict, Any


class ValidationError(Exception):
    """Raised when input validation fails."""
    pass


def validate_github_url(url: str) -> str:
    """
    Validate and normalize a GitHub repository URL.

    Args:
        url: GitHub repository URL to validate

    Returns:
        Normalized URL (lowercase, no trailing slash, no .git)

    Raises:
        ValidationError: If URL format is invalid

    Examples:
        >>> validate_github_url("https://github.com/owner/repo")
        'https://github.com/owner/repo'
        >>> validate_github_url("https://github.com/owner/repo/")
        'https://github.com/owner/repo'
        >>> validate_github_url("https://github.com/Owner/Repo")
        'https://github.com/owner/repo'
    """
    if not url or not isinstance(url, str):
        raise ValidationError("GitHub URL cannot be empty")

    # Normalize URL first
    normalized = normalize_url(url)

    # GitHub URL pattern: https://github.com/owner/repo
    # Owner: alphanumeric, hyphens, underscores
    # Repo: alphanumeric, hyphens, underscores, dots
    # Note: Pattern is case-insensitive because we normalize to lowercase first
    pattern = r'^https://github\.com/[a-z0-9_-]+/[a-z0-9_.-]+$'

    if not re.match(pattern, normalized):
        raise ValidationError(
            "Invalid GitHub URL format. "
            "Expected: https://github.com/owner/repo"
        )

    return normalized


def normalize_url(url: str) -> str:
    """
    Normalize a GitHub URL for consistent comparison.

    Normalization rules:
    - Remove trailing slashes
    - Remove .git suffix
    - Convert to lowercase
    - Ensure https:// prefix

    Args:
        url: URL to normalize

    Returns:
        Normalized URL

    Examples:
        >>> normalize_url("https://github.com/Owner/Repo.git/")
        'https://github.com/owner/repo'
        >>> normalize_url("github.com/owner/repo")
        'https://github.com/owner/repo'
    """
    # Strip whitespace
    url = url.strip()

    # Convert to lowercase first (before checking prefix)
    url = url.lower()

    # Add https:// if missing
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "https://" + url

    # Remove trailing slash first
    url = url.rstrip("/")

    # Then remove .git suffix (after removing slash)
    if url.endswith(".git"):
        url = url[:-4]

    return url


def sanitize_query(query: str, max_length: int = 500) -> str:
    """
    Sanitize query text to prevent XSS and ensure reasonable length.

    Sanitization rules:
    - Strip leading/trailing whitespace
    - Remove HTML tags
    - Collapse multiple spaces
    - Enforce maximum length
    - Prevent empty queries

    Args:
        query: Query text to sanitize
        max_length: Maximum allowed length (default: 500)

    Returns:
        Sanitized query text

    Raises:
        ValidationError: If query is empty or too long

    Examples:
        >>> sanitize_query("How does auth work?")
        'How does auth work?'
        >>> sanitize_query("  Multiple   spaces  ")
        'Multiple spaces'
        >>> sanitize_query("<script>alert('xss')</script>Safe text")
        "alert('xss')Safe text"
    """
    if not query or not isinstance(query, str):
        raise ValidationError("Query text cannot be empty")

    # Strip whitespace
    query = query.strip()

    # Remove HTML tags (simple approach - strips all < > content)
    # This prevents XSS attacks via HTML injection
    query = re.sub(r'<[^>]+>', '', query)

    # Collapse multiple spaces
    query = ' '.join(query.split())

    # Check if empty after sanitization
    if not query:
        raise ValidationError("Query is empty after sanitization")

    # Enforce max length
    if len(query) > max_length:
        raise ValidationError(
            f"Query too long ({len(query)} characters). "
            f"Maximum allowed: {max_length}"
        )

    return query


def validate_timeout(timeout: int) -> int:
    """
    Validate timeout value is within acceptable range.

    Args:
        timeout: Timeout in seconds

    Returns:
        Validated timeout

    Raises:
        ValidationError: If timeout is out of range

    Examples:
        >>> validate_timeout(60)
        60
        >>> validate_timeout(700)  # doctest: +IGNORE_EXCEPTION_DETAIL
        Traceback (most recent call last):
        ValidationError: Timeout must be between 10 and 600 seconds
    """
    if not isinstance(timeout, int):
        raise ValidationError("Timeout must be an integer")

    if timeout < 10 or timeout > 600:
        raise ValidationError(
            f"Timeout must be between 10 and 600 seconds (got: {timeout})"
        )

    return timeout


def validate_max_retries(retries: int) -> int:
    """
    Validate max retries value is within acceptable range.

    Args:
        retries: Maximum number of retry attempts

    Returns:
        Validated retries

    Raises:
        ValidationError: If retries is out of range

    Examples:
        >>> validate_max_retries(3)
        3
        >>> validate_max_retries(10)  # doctest: +IGNORE_EXCEPTION_DETAIL
        Traceback (most recent call last):
        ValidationError: Max retries must be between 1 and 5
    """
    if not isinstance(retries, int):
        raise ValidationError("Max retries must be an integer")

    if retries < 1 or retries > 5:
        raise ValidationError(
            f"Max retries must be between 1 and 5 (got: {retries})"
        )

    return retries


def validate_queries_file(file_path: str) -> List[str]:
    """
    Validate and parse a queries file.

    Expected JSON format:
    {
        "queries": ["query1", "query2", "query3"]
    }

    Args:
        file_path: Path to JSON file containing queries

    Returns:
        List of query strings

    Raises:
        ValidationError: If file doesn't exist, is invalid JSON, or has wrong schema

    Examples:
        >>> # Assuming valid file exists
        >>> validate_queries_file("queries.json")
        ['query1', 'query2', 'query3']
    """
    # Check file exists
    path = Path(file_path)
    if not path.exists():
        raise ValidationError(f"Queries file not found: {file_path}")

    if not path.is_file():
        raise ValidationError(f"Path is not a file: {file_path}")

    # Read and parse JSON
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise ValidationError(f"Invalid JSON in queries file: {e}")
    except IOError as e:
        raise ValidationError(f"Error reading queries file: {e}")

    # Validate schema
    if not isinstance(data, dict):
        raise ValidationError(
            "Queries file must contain a JSON object (got: {})".format(type(data).__name__)
        )

    if "queries" not in data:
        raise ValidationError(
            'Queries file must have a "queries" key. '
            'Expected format: {"queries": ["q1", "q2"]}'
        )

    queries = data["queries"]

    if not isinstance(queries, list):
        raise ValidationError(
            '"queries" value must be an array (got: {})'.format(type(queries).__name__)
        )

    if len(queries) == 0:
        raise ValidationError("Queries array cannot be empty")

    # Validate each query
    validated_queries = []
    for i, query in enumerate(queries):
        if not isinstance(query, str):
            raise ValidationError(
                f"Query at index {i} must be a string (got: {type(query).__name__})"
            )

        try:
            validated = sanitize_query(query)
            validated_queries.append(validated)
        except ValidationError as e:
            raise ValidationError(f"Invalid query at index {i}: {e}")

    return validated_queries


def parse_batch_queries(queries_string: str) -> List[str]:
    """
    Parse comma-separated batch queries.

    Args:
        queries_string: Comma-separated query strings

    Returns:
        List of sanitized query strings

    Raises:
        ValidationError: If any query is invalid

    Examples:
        >>> parse_batch_queries("query1, query2, query3")
        ['query1', 'query2', 'query3']
        >>> parse_batch_queries("How does auth work?, What is the API?")
        ['How does auth work?', 'What is the API?']
    """
    if not queries_string or not isinstance(queries_string, str):
        raise ValidationError("Batch queries string cannot be empty")

    # Split by comma
    queries = [q.strip() for q in queries_string.split(",")]

    # Filter out empty queries
    queries = [q for q in queries if q]

    if len(queries) == 0:
        raise ValidationError("No valid queries found in batch string")

    # Sanitize each query
    validated_queries = []
    for i, query in enumerate(queries):
        try:
            validated = sanitize_query(query)
            validated_queries.append(validated)
        except ValidationError as e:
            raise ValidationError(f"Invalid query at position {i+1}: {e}")

    return validated_queries


def validate_format(format_type: str) -> str:
    """
    Validate output format type.

    Args:
        format_type: Output format ("json" or "markdown")

    Returns:
        Validated format type

    Raises:
        ValidationError: If format is invalid

    Examples:
        >>> validate_format("json")
        'json'
        >>> validate_format("markdown")
        'markdown'
        >>> validate_format("xml")  # doctest: +IGNORE_EXCEPTION_DETAIL
        Traceback (most recent call last):
        ValidationError: Invalid format
    """
    valid_formats = ["json", "markdown"]

    if format_type not in valid_formats:
        raise ValidationError(
            f"Invalid format: {format_type}. "
            f"Valid options: {', '.join(valid_formats)}"
        )

    return format_type
