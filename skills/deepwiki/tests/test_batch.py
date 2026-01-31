"""
Unit tests for batch query processing module.

Tests query parsing, batch execution, and result formatting.
"""

import json
import sys
import os
import tempfile
from unittest.mock import Mock

# Add scripts directory to path for imports
test_dir = os.path.dirname(os.path.abspath(__file__))
scripts_dir = os.path.join(os.path.dirname(test_dir), 'scripts')
sys.path.insert(0, scripts_dir)

from batch import (
    parse_queries,
    _parse_queries_from_string,
    _parse_queries_from_file,
    execute_batch_queries,
    format_batch_results,
    _format_batch_markdown
)


class TestQueryParsing:
    """Test query parsing functions."""

    def test_parse_queries_single(self):
        """Test parsing single query"""
        args = Mock()
        args.query = "How does auth work?"
        args.queries = None
        args.queries_file = None

        queries = parse_queries(args)

        assert len(queries) == 1
        assert queries[0] == "How does auth work?"

    def test_parse_queries_comma_separated(self):
        """Test parsing comma-separated queries"""
        args = Mock()
        args.query = None
        args.queries = "query1, query2, query3"
        args.queries_file = None

        queries = parse_queries(args)

        assert len(queries) == 3
        assert queries == ["query1", "query2", "query3"]

    def test_parse_queries_from_string_strips_whitespace(self):
        """Test that query parsing strips whitespace"""
        queries = _parse_queries_from_string("  q1  ,  q2  ,  q3  ")

        assert queries == ["q1", "q2", "q3"]

    def test_parse_queries_from_string_filters_empty(self):
        """Test that empty queries are filtered out"""
        queries = _parse_queries_from_string("q1, , q2, , q3")

        assert len(queries) == 3
        assert queries == ["q1", "q2", "q3"]

    def test_parse_queries_from_string_empty_raises_error(self):
        """Test that all-empty queries raise error"""
        try:
            _parse_queries_from_string(", , ,")
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "No valid queries" in str(e)

    def test_parse_queries_from_file_valid(self):
        """Test parsing from valid JSON file"""
        # Create temp file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            json.dump({"queries": ["q1", "q2", "q3"]}, f)
            temp_file = f.name

        try:
            queries = _parse_queries_from_file(temp_file)
            assert len(queries) == 3
            assert queries == ["q1", "q2", "q3"]
        finally:
            os.unlink(temp_file)

    def test_parse_queries_from_file_not_found(self):
        """Test that missing file raises FileNotFoundError"""
        try:
            _parse_queries_from_file("/nonexistent/file.json")
            assert False, "Should have raised FileNotFoundError"
        except FileNotFoundError as e:
            assert "not found" in str(e)

    def test_parse_queries_from_file_invalid_json(self):
        """Test that invalid JSON raises error"""
        # Create temp file with invalid JSON
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            f.write("{invalid json")
            temp_file = f.name

        try:
            _parse_queries_from_file(temp_file)
            assert False, "Should have raised JSONDecodeError"
        except json.JSONDecodeError:
            pass
        finally:
            os.unlink(temp_file)

    def test_parse_queries_from_file_missing_queries_field(self):
        """Test that file without 'queries' field raises error"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            json.dump({"data": ["q1", "q2"]}, f)  # Wrong field name
            temp_file = f.name

        try:
            _parse_queries_from_file(temp_file)
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "queries" in str(e)
        finally:
            os.unlink(temp_file)

    def test_parse_queries_from_file_not_array(self):
        """Test that queries field must be array"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            json.dump({"queries": "not an array"}, f)
            temp_file = f.name

        try:
            _parse_queries_from_file(temp_file)
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "array" in str(e)
        finally:
            os.unlink(temp_file)

    def test_parse_queries_from_file_non_string_query(self):
        """Test that all queries must be strings"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            json.dump({"queries": ["q1", 123, "q3"]}, f)  # 123 is not a string
            temp_file = f.name

        try:
            _parse_queries_from_file(temp_file)
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "string" in str(e)
        finally:
            os.unlink(temp_file)


class TestBatchExecution:
    """Test batch query execution."""

    def test_execute_batch_all_cache_hits(self):
        """Test batch execution with all cache hits"""
        queries = ["q1", "q2", "q3"]

        # Mock cache with hits
        mock_conn = Mock()

        def mock_cache_lookup(conn, repo_url, query):
            return {
                "repo_url": repo_url,
                "query_text": query,
                "answer": f"Answer for {query}",
                "sources": f"[\"source_{query}.c\"]",
                "created_at": "2026-01-31T12:00:00Z",
                "id": 123
            }

        # Mock execute_query (should not be called)
        def mock_execute_query(repo_url, query, timeout, verbose):
            assert False, "execute_query should not be called for cache hits"

        # Inject mocks
        import cache
        old_lookup = cache.cache_lookup
        cache.cache_lookup = mock_cache_lookup

        try:
            result = execute_batch_queries(
                repo_url="https://github.com/redis/redis",
                queries=queries,
                conn=mock_conn,
                execute_query_func=mock_execute_query,
                timeout=60,
                inter_query_delay=0.1,  # Short delay for tests
                verbose=False
            )

            assert result["status"] == "success"
            assert result["total_queries"] == 3
            assert result["successful"] == 3
            assert result["failed"] == 0
            assert result["cache_hits"] == 3
            assert result["cache_misses"] == 0
            assert len(result["results"]) == 3
        finally:
            cache.cache_lookup = old_lookup

    def test_execute_batch_all_cache_misses(self):
        """Test batch execution with all cache misses"""
        queries = ["q1", "q2"]

        mock_conn = Mock()

        # Mock cache with misses
        def mock_cache_lookup(conn, repo_url, query):
            return None  # Cache miss

        # Mock cache store
        def mock_cache_store(conn, repo_url, query, answer, sources, timestamp):
            pass  # No-op

        # Mock execute_query
        def mock_execute_query(repo_url, query, timeout, verbose):
            return {
                "answer": f"Fresh answer for {query}",
                "sources": [f"source_{query}.c"]
            }

        # Inject mocks
        import cache
        old_lookup = cache.cache_lookup
        old_store = cache.cache_store
        cache.cache_lookup = mock_cache_lookup
        cache.cache_store = mock_cache_store

        try:
            result = execute_batch_queries(
                repo_url="https://github.com/redis/redis",
                queries=queries,
                conn=mock_conn,
                execute_query_func=mock_execute_query,
                timeout=60,
                inter_query_delay=0.1,
                verbose=False
            )

            assert result["status"] == "success"
            assert result["total_queries"] == 2
            assert result["successful"] == 2
            assert result["failed"] == 0
            assert result["cache_hits"] == 0
            assert result["cache_misses"] == 2
        finally:
            cache.cache_lookup = old_lookup
            cache.cache_store = old_store

    def test_execute_batch_partial_failure(self):
        """Test batch with some queries failing"""
        queries = ["q1", "q2", "q3"]

        mock_conn = Mock()

        # Mock cache
        def mock_cache_lookup(conn, repo_url, query):
            return None  # All cache misses

        def mock_cache_store(conn, repo_url, query, answer, sources, timestamp):
            pass

        # Mock execute_query that fails on q2
        def mock_execute_query(repo_url, query, timeout, verbose):
            if query == "q2":
                raise Exception("Query timeout")
            return {
                "answer": f"Answer for {query}",
                "sources": [f"{query}.c"]
            }

        # Inject mocks
        import cache
        old_lookup = cache.cache_lookup
        old_store = cache.cache_store
        cache.cache_lookup = mock_cache_lookup
        cache.cache_store = mock_cache_store

        try:
            result = execute_batch_queries(
                repo_url="https://github.com/redis/redis",
                queries=queries,
                conn=mock_conn,
                execute_query_func=mock_execute_query,
                timeout=60,
                inter_query_delay=0.1,
                verbose=False
            )

            assert result["status"] == "partial"
            assert result["total_queries"] == 3
            assert result["successful"] == 2
            assert result["failed"] == 1
            assert result["cache_misses"] == 3  # All 3 attempted execution (cache miss counted before error)

            # Check results
            assert result["results"][0]["status"] == "success"
            assert result["results"][1]["status"] == "error"
            assert result["results"][2]["status"] == "success"
        finally:
            cache.cache_lookup = old_lookup
            cache.cache_store = old_store


class TestResultFormatting:
    """Test batch result formatting."""

    def test_format_batch_results_json(self):
        """Test JSON formatting"""
        batch_summary = {
            "status": "success",
            "total_queries": 2,
            "successful": 2,
            "failed": 0,
            "cache_hits": 1,
            "cache_misses": 1,
            "results": []
        }

        formatted = format_batch_results(batch_summary, output_format="json")

        # Should be valid JSON
        parsed = json.loads(formatted)
        assert parsed["status"] == "success"
        assert parsed["total_queries"] == 2

    def test_format_batch_results_markdown(self):
        """Test Markdown formatting"""
        batch_summary = {
            "status": "success",
            "total_queries": 2,
            "successful": 2,
            "failed": 0,
            "cache_hits": 1,
            "cache_misses": 1,
            "results": [
                {
                    "query": "Test query",
                    "status": "success",
                    "cached": True,
                    "answer": "Test answer",
                    "sources": ["test.c"]
                }
            ]
        }

        formatted = format_batch_results(batch_summary, output_format="markdown")

        # Check key sections
        assert "# DeepWiki Batch Query Results" in formatted, "Missing header"
        assert "✅ SUCCESS" in formatted, "Missing success indicator"
        assert "## Summary" in formatted, "Missing summary section"
        assert "Total Queries:**" in formatted, "Missing total queries stat"  # Match actual format with **
        assert "## Query Results" in formatted, "Missing query results section"

    def test_format_batch_markdown_success(self):
        """Test Markdown with success status"""
        summary = {"status": "success", "total_queries": 1, "successful": 1, "failed": 0, "cache_hits": 0, "cache_misses": 1, "results": []}
        markdown = _format_batch_markdown(summary)
        assert "✅ SUCCESS" in markdown

    def test_format_batch_markdown_partial(self):
        """Test Markdown with partial status"""
        summary = {"status": "partial", "total_queries": 2, "successful": 1, "failed": 1, "cache_hits": 0, "cache_misses": 1, "results": []}
        markdown = _format_batch_markdown(summary)
        assert "⚠️ PARTIAL" in markdown

    def test_format_batch_markdown_error(self):
        """Test Markdown with error status"""
        summary = {"status": "error", "total_queries": 1, "successful": 0, "failed": 1, "cache_hits": 0, "cache_misses": 0, "results": []}
        markdown = _format_batch_markdown(summary)
        assert "❌ ERROR" in markdown


def run_all_tests():
    """Run all batch tests."""
    print("=" * 60)
    print("Running Batch Module Tests")
    print("=" * 60)

    test_classes = [
        TestQueryParsing,
        TestBatchExecution,
        TestResultFormatting
    ]

    total_tests = 0
    passed_tests = 0
    failed_tests = []

    for test_class in test_classes:
        print(f"\n{test_class.__name__}")
        print("-" * 60)

        test_instance = test_class()
        test_methods = [method for method in dir(test_instance) if method.startswith("test_")]

        for test_method in test_methods:
            total_tests += 1
            method = getattr(test_instance, test_method)

            try:
                method()
                print(f"✅ {test_method}")
                passed_tests += 1
            except AssertionError as e:
                print(f"❌ {test_method}")
                print(f"   Error: {e}")
                failed_tests.append((test_class.__name__, test_method, str(e)))
            except Exception as e:
                print(f"❌ {test_method}")
                print(f"   Unexpected error: {e}")
                failed_tests.append((test_class.__name__, test_method, str(e)))

    print("\n" + "=" * 60)
    print(f"Test Results: {passed_tests}/{total_tests} passed")

    if failed_tests:
        print("\nFailed tests:")
        for class_name, method_name, error in failed_tests:
            print(f"  - {class_name}.{method_name}: {error}")
        print("\n❌ Some tests failed")
        return 1
    else:
        print("\n✅ All batch tests passed!")
        return 0


if __name__ == "__main__":
    sys.exit(run_all_tests())
