"""
Unit tests for cache.py module.

Tests cover cache initialization, lookup, storage, statistics,
and management functions.
"""

import sys
from pathlib import Path
import tempfile
import sqlite3

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.cache import (
    CacheError,
    CacheInitializationError,
    CacheLookupError,
    CacheStoreError,
    init_cache,
    hash_query,
    cache_lookup,
    cache_store,
    cache_stats,
    cache_clear,
    format_bytes,
    get_cache_dir,
    get_cache_db_path,
    get_cache_connection
)


class TestCacheInitialization:
    """Tests for cache initialization."""

    def test_init_cache_creates_directory(self):
        """Test cache directory is created."""
        conn = init_cache()
        assert get_cache_dir().exists()
        conn.close()
        print("✅ test_init_cache_creates_directory")

    def test_init_cache_creates_database(self):
        """Test database file is created."""
        conn = init_cache()
        assert get_cache_db_path().exists()
        conn.close()
        print("✅ test_init_cache_creates_database")

    def test_init_cache_creates_table(self):
        """Test query_cache table is created."""
        conn = init_cache()
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='query_cache'"
        )
        assert cursor.fetchone() is not None
        conn.close()
        print("✅ test_init_cache_creates_table")

    def test_init_cache_creates_indexes(self):
        """Test indexes are created."""
        conn = init_cache()
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='index' AND name LIKE 'idx_%'"
        )
        indexes = cursor.fetchall()
        assert len(indexes) >= 2  # idx_repo_query and idx_timestamp
        conn.close()
        print("✅ test_init_cache_creates_indexes")

    def test_get_cache_connection(self):
        """Test convenience connection function."""
        conn = get_cache_connection()
        assert conn is not None
        assert isinstance(conn, sqlite3.Connection)
        conn.close()
        print("✅ test_get_cache_connection")


class TestQueryHashing:
    """Tests for query hashing function."""

    def test_hash_query_basic(self):
        """Test basic query hashing."""
        hash1 = hash_query("How does auth work?")
        assert len(hash1) == 64  # SHA-256 produces 64 hex chars
        print("✅ test_hash_query_basic")

    def test_hash_query_consistency(self):
        """Test same query produces same hash."""
        hash1 = hash_query("Test query")
        hash2 = hash_query("Test query")
        assert hash1 == hash2
        print("✅ test_hash_query_consistency")

    def test_hash_query_case_insensitive(self):
        """Test hashing is case-insensitive."""
        hash1 = hash_query("Test Query")
        hash2 = hash_query("test query")
        assert hash1 == hash2
        print("✅ test_hash_query_case_insensitive")

    def test_hash_query_whitespace_normalization(self):
        """Test whitespace is normalized."""
        hash1 = hash_query("  Test   Query  ")
        hash2 = hash_query("Test Query")
        assert hash1 == hash2
        print("✅ test_hash_query_whitespace_normalization")

    def test_hash_query_different_queries(self):
        """Test different queries produce different hashes."""
        hash1 = hash_query("Query 1")
        hash2 = hash_query("Query 2")
        assert hash1 != hash2
        print("✅ test_hash_query_different_queries")


class TestCacheLookup:
    """Tests for cache lookup function."""

    def test_cache_lookup_miss(self):
        """Test lookup returns None when not found."""
        conn = init_cache()
        result = cache_lookup(conn, "https://github.com/test/repo", "nonexistent query")
        assert result is None
        conn.close()
        print("✅ test_cache_lookup_miss")

    def test_cache_lookup_hit(self):
        """Test lookup returns result when found."""
        conn = init_cache()

        # Store a result
        cache_store(
            conn,
            "https://github.com/test/repo",
            "test query",
            "test answer",
            ["https://source.com"],
            1234567890
        )

        # Lookup should find it
        result = cache_lookup(conn, "https://github.com/test/repo", "test query")
        assert result is not None
        assert result["answer"] == "test answer"
        assert result["sources"] == ["https://source.com"]

        conn.close()
        print("✅ test_cache_lookup_hit")

    def test_cache_lookup_url_normalization(self):
        """Test lookup normalizes URL."""
        conn = init_cache()

        # Store with one URL format
        cache_store(
            conn,
            "https://github.com/owner/repo",
            "query",
            "answer",
            [],
            1234567890
        )

        # Lookup with different format (should still find it)
        result = cache_lookup(conn, "HTTPS://GitHub.com/Owner/Repo/", "query")
        assert result is not None

        conn.close()
        print("✅ test_cache_lookup_url_normalization")

    def test_cache_lookup_query_normalization(self):
        """Test lookup normalizes query."""
        conn = init_cache()

        # Store with one query format
        cache_store(
            conn,
            "https://github.com/test/repo",
            "How does auth work?",
            "answer",
            [],
            1234567890
        )

        # Lookup with different formatting (should still find it)
        result = cache_lookup(conn, "https://github.com/test/repo", "  HOW  DOES  AUTH  WORK?  ")
        assert result is not None

        conn.close()
        print("✅ test_cache_lookup_query_normalization")


class TestCacheStore:
    """Tests for cache storage function."""

    def test_cache_store_basic(self):
        """Test basic cache storage."""
        conn = init_cache()

        row_id = cache_store(
            conn,
            "https://github.com/test/repo",
            "query",
            "answer",
            ["source1", "source2"],
            1234567890
        )

        assert row_id > 0
        conn.close()
        print("✅ test_cache_store_basic")

    def test_cache_store_retrieval(self):
        """Test stored entry can be retrieved."""
        conn = init_cache()

        cache_store(
            conn,
            "https://github.com/test/repo",
            "query",
            "answer",
            ["source1", "source2"],
            1234567890
        )

        result = cache_lookup(conn, "https://github.com/test/repo", "query")
        assert result is not None
        assert result["answer"] == "answer"
        assert result["sources"] == ["source1", "source2"]
        assert result["timestamp"] == 1234567890

        conn.close()
        print("✅ test_cache_store_retrieval")

    def test_cache_store_idempotent(self):
        """Test storing same entry twice updates instead of duplicating."""
        conn = init_cache()
        cache_clear(conn)  # Start clean

        # Store first time
        cache_store(
            conn,
            "https://github.com/test/repo",
            "query",
            "answer1",
            ["source1"],
            1234567890
        )

        # Store second time (same repo+query, different answer)
        cache_store(
            conn,
            "https://github.com/test/repo",
            "query",
            "answer2",
            ["source2"],
            1234567891
        )

        # Should have only one entry with latest answer
        result = cache_lookup(conn, "https://github.com/test/repo", "query")
        assert result is not None, "Result should not be None"
        assert result["answer"] == "answer2", f"Expected answer2, got {result['answer']}"
        assert result["sources"] == ["source2"], f"Expected ['source2'], got {result['sources']}"
        assert result["timestamp"] == 1234567891, f"Expected 1234567891, got {result['timestamp']}"

        # Count entries to verify no duplicate
        cursor = conn.execute("SELECT COUNT(*) FROM query_cache WHERE repo_url = 'https://github.com/test/repo'")
        count = cursor.fetchone()[0]
        assert count == 1, f"Expected 1 entry, found {count}"

        conn.close()
        print("✅ test_cache_store_idempotent")

    def test_cache_store_multiple_repos(self):
        """Test storing entries for different repos."""
        conn = init_cache()

        cache_store(conn, "https://github.com/repo1/test", "query", "answer1", [], 1)
        cache_store(conn, "https://github.com/repo2/test", "query", "answer2", [], 2)

        result1 = cache_lookup(conn, "https://github.com/repo1/test", "query")
        result2 = cache_lookup(conn, "https://github.com/repo2/test", "query")

        assert result1["answer"] == "answer1"
        assert result2["answer"] == "answer2"

        conn.close()
        print("✅ test_cache_store_multiple_repos")


class TestCacheStats:
    """Tests for cache statistics function."""

    def test_cache_stats_empty(self):
        """Test stats on empty cache."""
        conn = init_cache()
        cache_clear(conn)  # Ensure empty

        stats = cache_stats(conn)
        assert stats["total_entries"] == 0
        assert stats["unique_repos"] == 0
        assert stats["oldest_entry"] is None
        assert stats["newest_entry"] is None

        conn.close()
        print("✅ test_cache_stats_empty")

    def test_cache_stats_with_entries(self):
        """Test stats with entries."""
        conn = init_cache()
        cache_clear(conn)

        # Add some entries
        cache_store(conn, "https://github.com/repo1/test", "q1", "a1", [], 1000)
        cache_store(conn, "https://github.com/repo1/test", "q2", "a2", [], 2000)
        cache_store(conn, "https://github.com/repo2/test", "q1", "a3", [], 3000)

        stats = cache_stats(conn)
        assert stats["total_entries"] == 3
        assert stats["unique_repos"] == 2
        assert stats["oldest_entry"] is not None
        assert stats["newest_entry"] is not None
        assert stats["total_size_bytes"] > 0

        conn.close()
        print("✅ test_cache_stats_with_entries")

    def test_cache_stats_top_repos(self):
        """Test top repos in stats."""
        conn = init_cache()
        cache_clear(conn)

        # Add entries (repo1 has 2 queries, repo2 has 1)
        cache_store(conn, "https://github.com/repo1/test", "q1", "a", [], 1)
        cache_store(conn, "https://github.com/repo1/test", "q2", "a", [], 2)
        cache_store(conn, "https://github.com/repo2/test", "q1", "a", [], 3)

        stats = cache_stats(conn)
        assert len(stats["top_repos"]) > 0
        assert stats["top_repos"][0]["queries"] == 2  # repo1 is first

        conn.close()
        print("✅ test_cache_stats_top_repos")


class TestCacheClear:
    """Tests for cache clear function."""

    def test_cache_clear_all(self):
        """Test clearing all entries."""
        conn = init_cache()
        cache_clear(conn)  # Start clean

        # Add some entries
        cache_store(conn, "https://github.com/repo1/test", "q1", "a", [], 1)
        cache_store(conn, "https://github.com/repo2/test", "q2", "a", [], 2)

        # Verify we have 2 entries
        stats_before = cache_stats(conn)
        assert stats_before["total_entries"] == 2, f"Expected 2 entries before clear, got {stats_before['total_entries']}"

        # Clear all
        deleted = cache_clear(conn)
        assert deleted == 2, f"Expected 2 deleted, got {deleted}"

        # Verify empty
        stats = cache_stats(conn)
        assert stats["total_entries"] == 0, f"Expected 0 entries after clear, got {stats['total_entries']}"

        conn.close()
        print("✅ test_cache_clear_all")

    def test_cache_clear_specific_repo(self):
        """Test clearing specific repo."""
        conn = init_cache()
        cache_clear(conn)

        # Add entries for different repos
        cache_store(conn, "https://github.com/repo1/test", "q1", "a", [], 1)
        cache_store(conn, "https://github.com/repo1/test", "q2", "a", [], 2)
        cache_store(conn, "https://github.com/repo2/test", "q1", "a", [], 3)

        # Clear only repo1
        deleted = cache_clear(conn, "https://github.com/repo1/test")
        assert deleted == 2

        # Verify repo1 entries gone, repo2 remains
        result1 = cache_lookup(conn, "https://github.com/repo1/test", "q1")
        result2 = cache_lookup(conn, "https://github.com/repo2/test", "q1")
        assert result1 is None
        assert result2 is not None

        conn.close()
        print("✅ test_cache_clear_specific_repo")


class TestHelperFunctions:
    """Tests for helper utility functions."""

    def test_format_bytes_small(self):
        """Test byte formatting for small sizes."""
        assert format_bytes(0) == "0.0 B"
        assert format_bytes(512) == "512.0 B"
        print("✅ test_format_bytes_small")

    def test_format_bytes_kb(self):
        """Test byte formatting for KB."""
        assert format_bytes(1024) == "1.0 KB"
        assert format_bytes(1536) == "1.5 KB"
        print("✅ test_format_bytes_kb")

    def test_format_bytes_mb(self):
        """Test byte formatting for MB."""
        assert format_bytes(1048576) == "1.0 MB"
        assert format_bytes(1572864) == "1.5 MB"
        print("✅ test_format_bytes_mb")

    def test_format_bytes_gb(self):
        """Test byte formatting for GB."""
        assert format_bytes(1073741824) == "1.0 GB"
        print("✅ test_format_bytes_gb")

    def test_get_cache_dir(self):
        """Test cache directory path."""
        cache_dir = get_cache_dir()
        assert cache_dir.name == "deepwiki"
        assert "cache" in str(cache_dir)
        print("✅ test_get_cache_dir")

    def test_get_cache_db_path(self):
        """Test cache database path."""
        db_path = get_cache_db_path()
        assert db_path.name == "cache.db"
        assert "deepwiki" in str(db_path)
        print("✅ test_get_cache_db_path")


def run_all_tests():
    """Run all cache tests."""
    print("\n" + "="*60)
    print("Running Cache Module Tests")
    print("="*60 + "\n")

    # Initialize test classes
    init_tests = TestCacheInitialization()
    hash_tests = TestQueryHashing()
    lookup_tests = TestCacheLookup()
    store_tests = TestCacheStore()
    stats_tests = TestCacheStats()
    clear_tests = TestCacheClear()
    helper_tests = TestHelperFunctions()

    # Run all tests
    tests_passed = 0
    tests_failed = 0

    test_methods = [
        # Initialization
        init_tests.test_init_cache_creates_directory,
        init_tests.test_init_cache_creates_database,
        init_tests.test_init_cache_creates_table,
        init_tests.test_init_cache_creates_indexes,
        init_tests.test_get_cache_connection,
        # Hashing
        hash_tests.test_hash_query_basic,
        hash_tests.test_hash_query_consistency,
        hash_tests.test_hash_query_case_insensitive,
        hash_tests.test_hash_query_whitespace_normalization,
        hash_tests.test_hash_query_different_queries,
        # Lookup
        lookup_tests.test_cache_lookup_miss,
        lookup_tests.test_cache_lookup_hit,
        lookup_tests.test_cache_lookup_url_normalization,
        lookup_tests.test_cache_lookup_query_normalization,
        # Store
        store_tests.test_cache_store_basic,
        store_tests.test_cache_store_retrieval,
        store_tests.test_cache_store_idempotent,
        store_tests.test_cache_store_multiple_repos,
        # Stats
        stats_tests.test_cache_stats_empty,
        stats_tests.test_cache_stats_with_entries,
        stats_tests.test_cache_stats_top_repos,
        # Clear
        clear_tests.test_cache_clear_all,
        clear_tests.test_cache_clear_specific_repo,
        # Helpers
        helper_tests.test_format_bytes_small,
        helper_tests.test_format_bytes_kb,
        helper_tests.test_format_bytes_mb,
        helper_tests.test_format_bytes_gb,
        helper_tests.test_get_cache_dir,
        helper_tests.test_get_cache_db_path,
    ]

    for test_method in test_methods:
        try:
            test_method()
            tests_passed += 1
        except Exception as e:
            print(f"❌ {test_method.__name__}: {e}")
            tests_failed += 1

    # Summary
    total = tests_passed + tests_failed
    print("\n" + "="*60)
    print(f"Test Results: {tests_passed}/{total} passed")
    if tests_failed > 0:
        print(f"❌ {tests_failed} test(s) failed")
        return 1
    else:
        print("\n✅ All cache tests passed!")
        return 0


if __name__ == "__main__":
    sys.exit(run_all_tests())
