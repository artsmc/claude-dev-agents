"""
Unit tests for formatter module.

Tests output formatting, progress indicators, and result creation.
"""

import json
import sys
import io
import os
from contextlib import redirect_stdout, redirect_stderr

# Add scripts directory to path for imports
test_dir = os.path.dirname(os.path.abspath(__file__))
scripts_dir = os.path.join(os.path.dirname(test_dir), 'scripts')
sys.path.insert(0, scripts_dir)

from formatter import (
    format_json,
    format_markdown,
    output_result,
    create_success_result,
    create_error_result,
    ProgressIndicator,
    init_progress,
    get_progress
)


class TestJSONFormatting:
    """Test JSON output formatting."""

    def test_format_json_basic(self):
        """Test basic JSON formatting"""
        result = {"status": "success", "answer": "Yes"}
        output = format_json(result)

        # Parse to verify valid JSON
        parsed = json.loads(output)
        assert parsed["status"] == "success"
        assert parsed["answer"] == "Yes"

        # Check pretty printing (indentation)
        assert "\n" in output, "JSON should be pretty-printed"

    def test_format_json_unicode(self):
        """Test JSON with unicode characters"""
        result = {"answer": "Да, поддерживает кластеризацию"}
        output = format_json(result)

        # Should preserve unicode (not escape)
        assert "Да" in output
        assert "поддерживает" in output


class TestMarkdownFormatting:
    """Test Markdown output formatting."""

    def test_format_markdown_success(self):
        """Test Markdown formatting for success result"""
        result = create_success_result(
            repo_url="https://github.com/redis/redis",
            query="Does this support clustering?",
            answer="Yes, Redis Cluster provides automatic sharding.",
            sources=["cluster.c", "cluster.h"],
            cached=False
        )

        markdown = format_markdown(result)

        # Check key sections present
        assert "# DeepWiki Query Result" in markdown
        assert "✅ SUCCESS" in markdown
        assert "⚡ MISS" in markdown
        assert "## Query" in markdown
        assert "## Answer" in markdown
        assert "## Sources" in markdown
        assert "cluster.c" in markdown
        assert "cluster.h" in markdown

    def test_format_markdown_cached(self):
        """Test Markdown formatting for cached result"""
        result = create_success_result(
            repo_url="https://github.com/redis/redis",
            query="Test query",
            answer="Test answer",
            sources=["test.c"],
            cached=True,
            cache_id=123
        )

        markdown = format_markdown(result)

        # Should show cache hit
        assert "🎯 HIT" in markdown
        assert "Cache ID" in markdown
        assert "123" in markdown

    def test_format_markdown_error(self):
        """Test Markdown formatting for error result"""
        result = create_error_result(
            repo_url="https://github.com/redis/redis",
            query="Test query",
            error="Query timed out after 60 seconds",
            error_type="TimeoutError"
        )

        markdown = format_markdown(result)

        # Check error formatting
        assert "❌ ERROR" in markdown
        assert "## Error Details" in markdown
        assert "Query timed out" in markdown

    def test_format_markdown_sources_string(self):
        """Test Markdown with sources as string (not list)"""
        result = create_success_result(
            repo_url="https://github.com/redis/redis",
            query="Test",
            answer="Test answer",
            sources="file1.c, file2.c, file3.c"
        )

        markdown = format_markdown(result)

        # Should parse comma-separated sources
        assert "file1.c" in markdown
        assert "file2.c" in markdown
        assert "file3.c" in markdown


class TestResultCreation:
    """Test result dictionary creation functions."""

    def test_create_success_result_basic(self):
        """Test basic success result creation"""
        result = create_success_result(
            repo_url="https://github.com/redis/redis",
            query="Test query",
            answer="Test answer",
            sources=["test.c"]
        )

        assert result["status"] == "success"
        assert result["cached"] is False
        assert result["repo"]["url"] == "https://github.com/redis/redis"
        assert result["repo"]["deepwiki_url"] == "https://deepwiki.com/github.com/redis/redis"
        assert result["query"] == "Test query"
        assert result["answer"] == "Test answer"
        assert result["sources"] == ["test.c"]
        assert "timestamp" in result

    def test_create_success_result_cached(self):
        """Test cached success result"""
        result = create_success_result(
            repo_url="https://github.com/redis/redis",
            query="Test",
            answer="Test",
            sources=["test.c"],
            cached=True,
            cache_id=456
        )

        assert result["cached"] is True
        assert result["cache_id"] == 456

    def test_create_success_result_custom_timestamp(self):
        """Test result with custom timestamp"""
        custom_time = "2026-01-31T12:00:00Z"
        result = create_success_result(
            repo_url="https://github.com/redis/redis",
            query="Test",
            answer="Test",
            sources=["test.c"],
            timestamp=custom_time
        )

        assert result["timestamp"] == custom_time

    def test_create_error_result(self):
        """Test error result creation"""
        result = create_error_result(
            repo_url="https://github.com/redis/redis",
            query="Test query",
            error="Connection timeout",
            error_type="TimeoutError"
        )

        assert result["status"] == "error"
        assert result["repo"]["url"] == "https://github.com/redis/redis"
        assert result["query"] == "Test query"
        assert result["error"] == "Connection timeout"
        assert result["error_type"] == "TimeoutError"
        assert "timestamp" in result


class TestOutputResult:
    """Test output_result function."""

    def test_output_json(self):
        """Test JSON output to stdout"""
        result = {"status": "success", "answer": "Test"}

        # Capture stdout
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            output_result(result, output_format="json", verbose=False)

        output = stdout.getvalue()
        parsed = json.loads(output)
        assert parsed["status"] == "success"

    def test_output_markdown(self):
        """Test Markdown output to stdout"""
        result = create_success_result(
            repo_url="https://github.com/redis/redis",
            query="Test",
            answer="Test answer",
            sources=["test.c"]
        )

        # Capture stdout
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            output_result(result, output_format="markdown", verbose=False)

        output = stdout.getvalue()
        assert "# DeepWiki Query Result" in output
        assert "✅" in output

    def test_output_invalid_format(self):
        """Test invalid output format raises error"""
        result = {"status": "success"}

        try:
            output_result(result, output_format="xml")
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "Unsupported output format" in str(e)


class TestProgressIndicator:
    """Test ProgressIndicator class."""

    def test_progress_indicator_verbose(self):
        """Test progress indicator with verbose=True"""
        # Capture stderr
        stderr = io.StringIO()
        with redirect_stderr(stderr):
            progress = ProgressIndicator(total_steps=3, verbose=True)

            progress.step("Step 1")
            progress.complete("Done 1")
            progress.blank_line()

            progress.step("Step 2")
            progress.substep("Substep 2.1")
            progress.error("Error in substep")
            progress.complete("Done 2")

        output = stderr.getvalue()

        # Check formatting
        assert "[1/3] Step 1..." in output
        assert "✓ Done 1" in output
        assert "[2/3] Step 2..." in output
        assert "• Substep 2.1" in output
        assert "✗ Error in substep" in output
        assert "✓ Done 2" in output

    def test_progress_indicator_silent(self):
        """Test progress indicator with verbose=False"""
        # Capture stderr
        stderr = io.StringIO()
        with redirect_stderr(stderr):
            progress = ProgressIndicator(total_steps=2, verbose=False)

            progress.step("Step 1")
            progress.complete("Done")

        output = stderr.getvalue()

        # Should be empty (verbose=False)
        assert output == ""

    def test_progress_indicator_multiple_steps(self):
        """Test progress indicator with multiple steps"""
        stderr = io.StringIO()
        with redirect_stderr(stderr):
            progress = ProgressIndicator(total_steps=5, verbose=True)

            for i in range(1, 6):
                progress.step(f"Step {i}")
                progress.complete(f"Completed {i}")

        output = stderr.getvalue()

        # Check all steps present
        assert "[1/5]" in output
        assert "[2/5]" in output
        assert "[3/5]" in output
        assert "[4/5]" in output
        assert "[5/5]" in output


class TestProgressSingleton:
    """Test module-level progress indicator functions."""

    def test_init_and_get_progress(self):
        """Test init_progress and get_progress"""
        progress = init_progress(total_steps=4, verbose=False)

        assert progress is not None
        assert progress.total_steps == 4

        # get_progress should return same instance
        retrieved = get_progress()
        assert retrieved is progress

    def test_get_progress_before_init(self):
        """Test get_progress before init returns None"""
        # Reset global state (this test might be fragile)
        import formatter as fmt
        fmt._progress = None

        assert get_progress() is None

        # Re-initialize for other tests
        init_progress(total_steps=1, verbose=False)


def run_all_tests():
    """Run all formatter tests."""
    print("=" * 60)
    print("Running Formatter Module Tests")
    print("=" * 60)

    test_classes = [
        TestJSONFormatting,
        TestMarkdownFormatting,
        TestResultCreation,
        TestOutputResult,
        TestProgressIndicator,
        TestProgressSingleton
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
        print("\n✅ All formatter tests passed!")
        return 0


if __name__ == "__main__":
    sys.exit(run_all_tests())
