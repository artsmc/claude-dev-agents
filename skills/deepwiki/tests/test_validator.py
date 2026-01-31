"""
Unit tests for validator.py module.

Tests cover all validation functions with positive and negative test cases,
edge cases, and security considerations.
"""

import pytest
import sys
from pathlib import Path
import tempfile
import json

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.validator import (
    ValidationError,
    validate_github_url,
    normalize_url,
    sanitize_query,
    validate_timeout,
    validate_max_retries,
    validate_queries_file,
    parse_batch_queries,
    validate_format
)


class TestValidateGithubUrl:
    """Tests for validate_github_url function."""

    def test_valid_url_basic(self):
        """Test basic valid GitHub URL."""
        url = validate_github_url("https://github.com/owner/repo")
        assert url == "https://github.com/owner/repo"

    def test_valid_url_with_trailing_slash(self):
        """Test URL with trailing slash is normalized."""
        url = validate_github_url("https://github.com/owner/repo/")
        assert url == "https://github.com/owner/repo"

    def test_valid_url_with_git_suffix(self):
        """Test URL with .git suffix is normalized."""
        url = validate_github_url("https://github.com/owner/repo.git")
        assert url == "https://github.com/owner/repo"

    def test_valid_url_mixed_case(self):
        """Test mixed case URL is normalized to lowercase."""
        url = validate_github_url("HTTPS://GitHub.com/Owner/Repo")
        assert url == "https://github.com/owner/repo"

    def test_valid_url_complex(self):
        """Test complex URL with all normalization needed."""
        url = validate_github_url("HTTPS://GitHub.com/Owner/Repo.git/")
        assert url == "https://github.com/owner/repo"

    def test_valid_url_with_hyphens(self):
        """Test owner and repo names with hyphens."""
        url = validate_github_url("https://github.com/my-owner/my-repo")
        assert url == "https://github.com/my-owner/my-repo"

    def test_valid_url_with_underscores(self):
        """Test owner and repo names with underscores."""
        url = validate_github_url("https://github.com/my_owner/my_repo")
        assert url == "https://github.com/my_owner/my_repo"

    def test_valid_url_with_dots_in_repo(self):
        """Test repo name with dots."""
        url = validate_github_url("https://github.com/owner/repo.js")
        assert url == "https://github.com/owner/repo.js"

    def test_invalid_url_gitlab(self):
        """Test GitLab URL is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            validate_github_url("https://gitlab.com/owner/repo")
        assert "Invalid GitHub URL format" in str(exc_info.value)

    def test_invalid_url_bitbucket(self):
        """Test Bitbucket URL is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            validate_github_url("https://bitbucket.org/owner/repo")
        assert "Invalid GitHub URL format" in str(exc_info.value)

    def test_invalid_url_missing_owner(self):
        """Test URL missing owner is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            validate_github_url("https://github.com/repo")
        assert "Invalid GitHub URL format" in str(exc_info.value)

    def test_invalid_url_missing_repo(self):
        """Test URL missing repo is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            validate_github_url("https://github.com/owner/")
        assert "Invalid GitHub URL format" in str(exc_info.value)

    def test_invalid_url_extra_path(self):
        """Test URL with extra path segments is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            validate_github_url("https://github.com/owner/repo/issues")
        assert "Invalid GitHub URL format" in str(exc_info.value)

    def test_invalid_url_empty(self):
        """Test empty URL is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            validate_github_url("")
        assert "cannot be empty" in str(exc_info.value)

    def test_invalid_url_none(self):
        """Test None URL is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            validate_github_url(None)
        assert "cannot be empty" in str(exc_info.value)

    def test_invalid_url_whitespace_only(self):
        """Test whitespace-only URL is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            validate_github_url("   ")
        assert "cannot be empty" in str(exc_info.value)


class TestNormalizeUrl:
    """Tests for normalize_url function."""

    def test_normalize_trailing_slash(self):
        """Test trailing slash removal."""
        url = normalize_url("https://github.com/owner/repo/")
        assert url == "https://github.com/owner/repo"

    def test_normalize_git_suffix(self):
        """Test .git suffix removal."""
        url = normalize_url("https://github.com/owner/repo.git")
        assert url == "https://github.com/owner/repo"

    def test_normalize_lowercase(self):
        """Test lowercase conversion."""
        url = normalize_url("HTTPS://GitHub.com/Owner/Repo")
        assert url == "https://github.com/owner/repo"

    def test_normalize_add_https(self):
        """Test https:// prefix added if missing."""
        url = normalize_url("github.com/owner/repo")
        assert url == "https://github.com/owner/repo"

    def test_normalize_all_transformations(self):
        """Test all normalizations combined."""
        url = normalize_url("GitHub.com/Owner/Repo.git/")
        assert url == "https://github.com/owner/repo"


class TestSanitizeQuery:
    """Tests for sanitize_query function."""

    def test_sanitize_basic_query(self):
        """Test basic query passes through unchanged."""
        query = sanitize_query("How does authentication work?")
        assert query == "How does authentication work?"

    def test_sanitize_trim_whitespace(self):
        """Test leading/trailing whitespace is removed."""
        query = sanitize_query("  query text  ")
        assert query == "query text"

    def test_sanitize_collapse_spaces(self):
        """Test multiple spaces are collapsed."""
        query = sanitize_query("multiple   spaces    here")
        assert query == "multiple spaces here"

    def test_sanitize_remove_html_tags(self):
        """Test HTML tags are stripped."""
        query = sanitize_query("<script>alert('xss')</script>Safe text")
        assert query == "alert('xss')Safe text"

    def test_sanitize_remove_complex_html(self):
        """Test complex HTML structure is stripped."""
        query = sanitize_query("<div><p>nested</p></div>text")
        assert query == "nestedtext"

    def test_sanitize_remove_self_closing_tags(self):
        """Test self-closing tags are stripped."""
        query = sanitize_query("text<br/>more<img src='x'/>end")
        assert query == "textmoreend"

    def test_sanitize_max_length_ok(self):
        """Test query under max length is accepted."""
        query = sanitize_query("a" * 500)
        assert len(query) == 500

    def test_sanitize_max_length_exceeded(self):
        """Test query over max length is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            sanitize_query("a" * 501)
        assert "too long" in str(exc_info.value)
        assert "500" in str(exc_info.value)

    def test_sanitize_custom_max_length(self):
        """Test custom max length parameter."""
        query = sanitize_query("a" * 100, max_length=100)
        assert len(query) == 100

        with pytest.raises(ValidationError):
            sanitize_query("a" * 101, max_length=100)

    def test_sanitize_empty_query(self):
        """Test empty query is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            sanitize_query("")
        assert "cannot be empty" in str(exc_info.value)

    def test_sanitize_whitespace_only(self):
        """Test whitespace-only query is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            sanitize_query("   ")
        assert "cannot be empty" in str(exc_info.value)

    def test_sanitize_only_html_tags(self):
        """Test query with only HTML tags is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            sanitize_query("<div></div><p></p>")
        assert "empty after sanitization" in str(exc_info.value)

    def test_sanitize_none(self):
        """Test None query is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            sanitize_query(None)
        assert "cannot be empty" in str(exc_info.value)


class TestValidateTimeout:
    """Tests for validate_timeout function."""

    def test_timeout_minimum_valid(self):
        """Test minimum valid timeout (10 seconds)."""
        result = validate_timeout(10)
        assert result == 10

    def test_timeout_maximum_valid(self):
        """Test maximum valid timeout (600 seconds)."""
        result = validate_timeout(600)
        assert result == 600

    def test_timeout_middle_range(self):
        """Test timeout in middle of valid range."""
        result = validate_timeout(60)
        assert result == 60

    def test_timeout_too_low(self):
        """Test timeout below minimum is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            validate_timeout(9)
        assert "between 10 and 600" in str(exc_info.value)

    def test_timeout_too_high(self):
        """Test timeout above maximum is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            validate_timeout(601)
        assert "between 10 and 600" in str(exc_info.value)

    def test_timeout_zero(self):
        """Test timeout of zero is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            validate_timeout(0)
        assert "between 10 and 600" in str(exc_info.value)

    def test_timeout_negative(self):
        """Test negative timeout is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            validate_timeout(-1)
        assert "between 10 and 600" in str(exc_info.value)

    def test_timeout_not_integer(self):
        """Test non-integer timeout is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            validate_timeout("60")
        assert "must be an integer" in str(exc_info.value)


class TestValidateMaxRetries:
    """Tests for validate_max_retries function."""

    def test_retries_minimum_valid(self):
        """Test minimum valid retries (1)."""
        result = validate_max_retries(1)
        assert result == 1

    def test_retries_maximum_valid(self):
        """Test maximum valid retries (5)."""
        result = validate_max_retries(5)
        assert result == 5

    def test_retries_middle_range(self):
        """Test retries in middle of valid range."""
        result = validate_max_retries(3)
        assert result == 3

    def test_retries_too_low(self):
        """Test retries below minimum is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            validate_max_retries(0)
        assert "between 1 and 5" in str(exc_info.value)

    def test_retries_too_high(self):
        """Test retries above maximum is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            validate_max_retries(6)
        assert "between 1 and 5" in str(exc_info.value)

    def test_retries_not_integer(self):
        """Test non-integer retries is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            validate_max_retries("3")
        assert "must be an integer" in str(exc_info.value)


class TestParseBatchQueries:
    """Tests for parse_batch_queries function."""

    def test_parse_single_query(self):
        """Test parsing single query."""
        queries = parse_batch_queries("query1")
        assert queries == ["query1"]

    def test_parse_multiple_queries(self):
        """Test parsing multiple comma-separated queries."""
        queries = parse_batch_queries("query1, query2, query3")
        assert queries == ["query1", "query2", "query3"]

    def test_parse_trim_whitespace(self):
        """Test whitespace around queries is trimmed."""
        queries = parse_batch_queries("  query1  ,  query2  ,  query3  ")
        assert queries == ["query1", "query2", "query3"]

    def test_parse_with_commas_in_query(self):
        """Test queries containing natural commas are handled correctly."""
        # Note: This will split on ALL commas - users should use file mode for complex queries
        queries = parse_batch_queries("What is auth?, How does routing work?")
        assert len(queries) == 2

    def test_parse_empty_string(self):
        """Test empty string is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            parse_batch_queries("")
        assert "cannot be empty" in str(exc_info.value)

    def test_parse_only_commas(self):
        """Test string with only commas is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            parse_batch_queries(",,,")
        assert "No valid queries" in str(exc_info.value)

    def test_parse_with_empty_segments(self):
        """Test empty segments between commas are filtered out."""
        queries = parse_batch_queries("query1,,query2,,,query3")
        assert queries == ["query1", "query2", "query3"]

    def test_parse_with_invalid_query(self):
        """Test batch with invalid query is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            parse_batch_queries("valid query, " + "x" * 501)
        assert "Invalid query at position" in str(exc_info.value)


class TestValidateQueriesFile:
    """Tests for validate_queries_file function."""

    def test_valid_queries_file(self):
        """Test valid queries JSON file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"queries": ["query1", "query2", "query3"]}, f)
            temp_path = f.name

        try:
            queries = validate_queries_file(temp_path)
            assert queries == ["query1", "query2", "query3"]
        finally:
            Path(temp_path).unlink()

    def test_queries_file_not_found(self):
        """Test non-existent file is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            validate_queries_file("/nonexistent/file.json")
        assert "not found" in str(exc_info.value)

    def test_queries_file_invalid_json(self):
        """Test invalid JSON is rejected."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("invalid json {")
            temp_path = f.name

        try:
            with pytest.raises(ValidationError) as exc_info:
                validate_queries_file(temp_path)
            assert "Invalid JSON" in str(exc_info.value)
        finally:
            Path(temp_path).unlink()

    def test_queries_file_not_object(self):
        """Test JSON array instead of object is rejected."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(["query1", "query2"], f)
            temp_path = f.name

        try:
            with pytest.raises(ValidationError) as exc_info:
                validate_queries_file(temp_path)
            assert "must contain a JSON object" in str(exc_info.value)
        finally:
            Path(temp_path).unlink()

    def test_queries_file_missing_queries_key(self):
        """Test JSON missing 'queries' key is rejected."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"data": ["query1", "query2"]}, f)
            temp_path = f.name

        try:
            with pytest.raises(ValidationError) as exc_info:
                validate_queries_file(temp_path)
            assert 'must have a "queries" key' in str(exc_info.value)
        finally:
            Path(temp_path).unlink()

    def test_queries_file_queries_not_array(self):
        """Test 'queries' value not an array is rejected."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"queries": "not an array"}, f)
            temp_path = f.name

        try:
            with pytest.raises(ValidationError) as exc_info:
                validate_queries_file(temp_path)
            assert "must be an array" in str(exc_info.value)
        finally:
            Path(temp_path).unlink()

    def test_queries_file_empty_array(self):
        """Test empty queries array is rejected."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"queries": []}, f)
            temp_path = f.name

        try:
            with pytest.raises(ValidationError) as exc_info:
                validate_queries_file(temp_path)
            assert "cannot be empty" in str(exc_info.value)
        finally:
            Path(temp_path).unlink()

    def test_queries_file_non_string_query(self):
        """Test non-string query in array is rejected."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"queries": ["query1", 123, "query3"]}, f)
            temp_path = f.name

        try:
            with pytest.raises(ValidationError) as exc_info:
                validate_queries_file(temp_path)
            assert "must be a string" in str(exc_info.value)
        finally:
            Path(temp_path).unlink()

    def test_queries_file_sanitizes_queries(self):
        """Test queries are sanitized during validation."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"queries": ["  query1  ", "query2<script>", "   query3   "]}, f)
            temp_path = f.name

        try:
            queries = validate_queries_file(temp_path)
            assert queries[0] == "query1"  # Trimmed
            assert queries[1] == "query2"  # HTML stripped
            assert queries[2] == "query3"  # Trimmed
        finally:
            Path(temp_path).unlink()


class TestValidateFormat:
    """Tests for validate_format function."""

    def test_format_json(self):
        """Test 'json' format is valid."""
        result = validate_format("json")
        assert result == "json"

    def test_format_markdown(self):
        """Test 'markdown' format is valid."""
        result = validate_format("markdown")
        assert result == "markdown"

    def test_format_invalid(self):
        """Test invalid format is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            validate_format("xml")
        assert "Invalid format" in str(exc_info.value)
        assert "json" in str(exc_info.value)
        assert "markdown" in str(exc_info.value)

    def test_format_case_sensitive(self):
        """Test format validation is case-sensitive."""
        with pytest.raises(ValidationError):
            validate_format("JSON")


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
