"""
Cache system for DeepWiki queries.

This module provides a SQLite-based caching layer for DeepWiki query results.
Caching reduces API calls, improves response times, and provides offline access
to previously fetched results.

Architecture:
- SQLite database for persistence
- SHA-256 hashing for query deduplication
- URL normalization for consistent cache keys
- JSON serialization for sources array
"""

import sqlite3
import json
import hashlib
import os
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone

# Import normalize_url from validator module
import sys
sys.path.insert(0, str(Path(__file__).parent))
from validator import normalize_url


class CacheError(Exception):
    """Base exception for cache operations."""
    pass


class CacheInitializationError(CacheError):
    """Raised when cache initialization fails."""
    pass


class CacheLookupError(CacheError):
    """Raised when cache lookup fails."""
    pass


class CacheStoreError(CacheError):
    """Raised when cache storage fails."""
    pass


def get_cache_dir() -> Path:
    """
    Get the cache directory path.

    Returns:
        Path to cache directory (~/.claude/cache/deepwiki/)
    """
    return Path.home() / ".claude" / "cache" / "deepwiki"


def get_cache_db_path() -> Path:
    """
    Get the cache database file path.

    Returns:
        Path to cache.db file
    """
    return get_cache_dir() / "cache.db"


def init_cache() -> sqlite3.Connection:
    """
    Initialize the cache system.

    Creates cache directory, sets permissions, creates database,
    and initializes schema.

    Returns:
        SQLite connection object

    Raises:
        CacheInitializationError: If initialization fails

    Schema:
        query_cache table:
        - id: INTEGER PRIMARY KEY AUTOINCREMENT
        - repo_url: TEXT (normalized GitHub URL)
        - query_hash: TEXT (SHA-256 hash of normalized query)
        - query_text: TEXT (original query for reference)
        - answer: TEXT (DeepWiki answer)
        - sources: TEXT (JSON array of source URLs)
        - timestamp: INTEGER (Unix timestamp)
        - created_at: TEXT (ISO 8601 timestamp)

        Indexes:
        - idx_repo_query: (repo_url, query_hash) for fast lookups
        - idx_timestamp: (timestamp) for TTL queries
    """
    try:
        # Create cache directory
        cache_dir = get_cache_dir()
        cache_dir.mkdir(parents=True, exist_ok=True)

        # Set directory permissions to 700 (owner only)
        os.chmod(cache_dir, 0o700)

        # Get database path
        db_path = get_cache_db_path()

        # Connect to database (creates if not exists)
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row  # Enable column access by name

        # Create query_cache table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS query_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                repo_url TEXT NOT NULL,
                query_hash TEXT NOT NULL,
                query_text TEXT NOT NULL,
                answer TEXT NOT NULL,
                sources TEXT NOT NULL,
                timestamp INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                UNIQUE(repo_url, query_hash)
            )
        """)

        # Create indexes for fast lookups
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_repo_query
            ON query_cache(repo_url, query_hash)
        """)

        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_timestamp
            ON query_cache(timestamp)
        """)

        conn.commit()

        # Set database file permissions to 600 (owner read/write)
        os.chmod(db_path, 0o600)

        return conn

    except Exception as e:
        raise CacheInitializationError(f"Failed to initialize cache: {e}")


def hash_query(query_text: str) -> str:
    """
    Hash query text for consistent cache keys.

    Normalization:
    - Convert to lowercase
    - Strip whitespace
    - Collapse multiple spaces

    Args:
        query_text: Query text to hash

    Returns:
        SHA-256 hash (hex digest)

    Examples:
        >>> hash_query("How does auth work?")
        'a1b2c3d4...'
        >>> hash_query("  How  does   auth   work?  ")
        'a1b2c3d4...'  # Same hash (normalized)
    """
    # Normalize query text
    normalized = query_text.lower().strip()
    normalized = ' '.join(normalized.split())  # Collapse spaces

    # Hash with SHA-256
    return hashlib.sha256(normalized.encode('utf-8')).hexdigest()


def cache_lookup(
    conn: sqlite3.Connection,
    repo_url: str,
    query_text: str
) -> Optional[Dict[str, Any]]:
    """
    Look up a cached query result.

    Args:
        conn: SQLite connection
        repo_url: GitHub repository URL
        query_text: Query text

    Returns:
        Cached result dict or None if not found

    Result structure:
        {
            "id": int,
            "repo_url": str,
            "query_hash": str,
            "query_text": str,
            "answer": str,
            "sources": List[str],  # Parsed from JSON
            "timestamp": int,
            "created_at": str
        }

    Raises:
        CacheLookupError: If lookup fails

    Examples:
        >>> conn = init_cache()
        >>> result = cache_lookup(conn, "https://github.com/owner/repo", "query")
        >>> if result:
        ...     print(result["answer"])
    """
    try:
        # Normalize inputs
        normalized_url = normalize_url(repo_url)
        query_hash_value = hash_query(query_text)

        # Query database with parameterized SQL (prevents SQL injection)
        cursor = conn.execute(
            """
            SELECT id, repo_url, query_hash, query_text, answer, sources,
                   timestamp, created_at
            FROM query_cache
            WHERE repo_url = ? AND query_hash = ?
            """,
            (normalized_url, query_hash_value)
        )

        row = cursor.fetchone()

        if row is None:
            return None

        # Parse sources from JSON
        sources = json.loads(row["sources"])

        # Convert row to dict
        result = {
            "id": row["id"],
            "repo_url": row["repo_url"],
            "query_hash": row["query_hash"],
            "query_text": row["query_text"],
            "answer": row["answer"],
            "sources": sources,
            "timestamp": row["timestamp"],
            "created_at": row["created_at"]
        }

        return result

    except json.JSONDecodeError as e:
        raise CacheLookupError(f"Failed to parse cached sources: {e}")
    except Exception as e:
        raise CacheLookupError(f"Cache lookup failed: {e}")


def cache_store(
    conn: sqlite3.Connection,
    repo_url: str,
    query_text: str,
    answer: str,
    sources: List[str],
    timestamp: Optional[int] = None
) -> int:
    """
    Store a query result in the cache.

    Uses INSERT OR REPLACE for idempotency - if the same repo+query
    exists, it will be updated with the new result.

    Args:
        conn: SQLite connection
        repo_url: GitHub repository URL
        query_text: Query text
        answer: DeepWiki answer text
        sources: List of source URLs
        timestamp: Unix timestamp (defaults to current time)

    Returns:
        Row ID of stored entry

    Raises:
        CacheStoreError: If storage fails

    Examples:
        >>> conn = init_cache()
        >>> row_id = cache_store(
        ...     conn,
        ...     "https://github.com/owner/repo",
        ...     "How does auth work?",
        ...     "Authentication is handled by...",
        ...     ["https://github.com/owner/repo/blob/main/auth.py"]
        ... )
    """
    try:
        # Normalize inputs
        normalized_url = normalize_url(repo_url)
        query_hash_value = hash_query(query_text)
        sources_json = json.dumps(sources)

        # Use current timestamp if not provided
        if timestamp is None:
            timestamp = int(datetime.now(timezone.utc).timestamp())

        # ISO 8601 timestamp for created_at
        created_at = datetime.now(timezone.utc).isoformat()

        # Insert or replace (idempotent)
        cursor = conn.execute(
            """
            INSERT OR REPLACE INTO query_cache
            (repo_url, query_hash, query_text, answer, sources, timestamp, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (normalized_url, query_hash_value, query_text, answer,
             sources_json, timestamp, created_at)
        )

        conn.commit()

        return cursor.lastrowid

    except json.JSONEncodeError as e:
        raise CacheStoreError(f"Failed to serialize sources: {e}")
    except Exception as e:
        raise CacheStoreError(f"Cache store failed: {e}")


def cache_stats(conn: sqlite3.Connection) -> Dict[str, Any]:
    """
    Get cache statistics.

    Args:
        conn: SQLite connection

    Returns:
        Statistics dictionary

    Structure:
        {
            "total_entries": int,
            "unique_repos": int,
            "oldest_entry": str (ISO 8601) or None,
            "newest_entry": str (ISO 8601) or None,
            "total_size_bytes": int,
            "total_size_human": str,
            "top_repos": [
                {"repo": str, "queries": int},
                ...
            ]
        }

    Examples:
        >>> conn = init_cache()
        >>> stats = cache_stats(conn)
        >>> print(f"Total cached queries: {stats['total_entries']}")
    """
    try:
        # Get overall stats
        cursor = conn.execute("""
            SELECT
                COUNT(*) as total_entries,
                COUNT(DISTINCT repo_url) as unique_repos,
                MIN(timestamp) as oldest_ts,
                MAX(timestamp) as newest_ts,
                SUM(LENGTH(answer) + LENGTH(sources)) as total_size
            FROM query_cache
        """)
        row = cursor.fetchone()

        # Convert timestamps to ISO 8601
        oldest_entry = None
        newest_entry = None
        if row["oldest_ts"]:
            oldest_entry = datetime.fromtimestamp(
                row["oldest_ts"], tz=timezone.utc
            ).isoformat()
        if row["newest_ts"]:
            newest_entry = datetime.fromtimestamp(
                row["newest_ts"], tz=timezone.utc
            ).isoformat()

        # Format size
        total_size = row["total_size"] or 0
        total_size_human = format_bytes(total_size)

        # Get top repos by query count
        cursor = conn.execute("""
            SELECT repo_url, COUNT(*) as query_count
            FROM query_cache
            GROUP BY repo_url
            ORDER BY query_count DESC
            LIMIT 3
        """)
        top_repos = [
            {"repo": row["repo_url"], "queries": row["query_count"]}
            for row in cursor.fetchall()
        ]

        return {
            "total_entries": row["total_entries"],
            "unique_repos": row["unique_repos"],
            "oldest_entry": oldest_entry,
            "newest_entry": newest_entry,
            "total_size_bytes": total_size,
            "total_size_human": total_size_human,
            "top_repos": top_repos
        }

    except Exception as e:
        raise CacheLookupError(f"Failed to get cache stats: {e}")


def cache_clear(
    conn: sqlite3.Connection,
    repo_url: Optional[str] = None
) -> int:
    """
    Clear cache entries.

    Args:
        conn: SQLite connection
        repo_url: Optional repository URL to clear (clears all if None)

    Returns:
        Number of entries deleted

    Examples:
        >>> conn = init_cache()
        >>> # Clear specific repo
        >>> deleted = cache_clear(conn, "https://github.com/owner/repo")
        >>> # Clear all
        >>> deleted = cache_clear(conn)
    """
    try:
        if repo_url:
            # Clear specific repo
            normalized_url = normalize_url(repo_url)
            cursor = conn.execute(
                "DELETE FROM query_cache WHERE repo_url = ?",
                (normalized_url,)
            )
        else:
            # Clear all entries
            cursor = conn.execute("DELETE FROM query_cache")

        conn.commit()
        return cursor.rowcount

    except Exception as e:
        raise CacheStoreError(f"Cache clear failed: {e}")


def format_bytes(size_bytes: int) -> str:
    """
    Format byte size in human-readable format.

    Args:
        size_bytes: Size in bytes

    Returns:
        Formatted string (e.g., "1.5 KB", "2.3 MB")

    Examples:
        >>> format_bytes(1024)
        '1.0 KB'
        >>> format_bytes(1536)
        '1.5 KB'
        >>> format_bytes(1048576)
        '1.0 MB'
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


# Convenience function for getting connection
def get_cache_connection() -> sqlite3.Connection:
    """
    Get or create cache connection.

    This is a convenience wrapper around init_cache() that
    ensures cache is initialized and returns a connection.

    Returns:
        SQLite connection object

    Examples:
        >>> conn = get_cache_connection()
        >>> result = cache_lookup(conn, repo_url, query)
    """
    return init_cache()
