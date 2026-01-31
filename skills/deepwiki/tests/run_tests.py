#!/usr/bin/env python3
"""
Simple test runner for validator module (doesn't require pytest).

Runs all validation tests and reports results.
"""

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


class TestRunner:
    """Simple test runner."""

    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []

    def test(self, name, func):
        """Run a single test."""
        try:
            func()
            self.passed += 1
            print(f"✅ {name}")
        except AssertionError as e:
            self.failed += 1
            self.errors.append((name, str(e)))
            print(f"❌ {name}: {e}")
        except Exception as e:
            self.failed += 1
            self.errors.append((name, f"Unexpected error: {e}"))
            print(f"❌ {name}: Unexpected error: {e}")

    def expect_error(self, name, func, error_type=ValidationError):
        """Expect a function to raise an error."""
        try:
            func()
            self.failed += 1
            self.errors.append((name, "Expected error but none was raised"))
            print(f"❌ {name}: Expected error but none was raised")
        except error_type:
            self.passed += 1
            print(f"✅ {name}")
        except Exception as e:
            self.failed += 1
            self.errors.append((name, f"Wrong error type: {type(e).__name__}"))
            print(f"❌ {name}: Wrong error type: {type(e).__name__}")

    def summary(self):
        """Print test summary."""
        total = self.passed + self.failed
        print(f"\n{'=' * 60}")
        print(f"Test Results: {self.passed}/{total} passed")
        if self.failed > 0:
            print(f"\n❌ {self.failed} test(s) failed:")
            for name, error in self.errors:
                print(f"  - {name}: {error}")
            return 1
        else:
            print("\n✅ All tests passed!")
            return 0


def run_tests():
    """Run all validation tests."""
    runner = TestRunner()

    print("Running validator tests...\n")

    # URL Validation Tests
    print("=== URL Validation Tests ===")
    runner.test(
        "Valid basic URL",
        lambda: validate_github_url("https://github.com/owner/repo") == "https://github.com/owner/repo" or (_ for _ in ()).throw(AssertionError("URL mismatch"))
    )

    runner.test(
        "URL with trailing slash normalized",
        lambda: validate_github_url("https://github.com/owner/repo/") == "https://github.com/owner/repo" or (_ for _ in ()).throw(AssertionError("Trailing slash not removed"))
    )

    runner.test(
        "URL with .git suffix normalized",
        lambda: validate_github_url("https://github.com/owner/repo.git") == "https://github.com/owner/repo" or (_ for _ in ()).throw(AssertionError(".git not removed"))
    )

    runner.test(
        "Mixed case URL normalized",
        lambda: validate_github_url("HTTPS://GitHub.com/Owner/Repo") == "https://github.com/owner/repo" or (_ for _ in ()).throw(AssertionError("Not lowercased"))
    )

    runner.test(
        "Complex URL normalized",
        lambda: validate_github_url("HTTPS://GitHub.com/Owner/Repo.git/") == "https://github.com/owner/repo" or (_ for _ in ()).throw(AssertionError("Complex normalization failed"))
    )

    runner.expect_error(
        "GitLab URL rejected",
        lambda: validate_github_url("https://gitlab.com/owner/repo")
    )

    runner.expect_error(
        "Empty URL rejected",
        lambda: validate_github_url("")
    )

    # Query Sanitization Tests
    print("\n=== Query Sanitization Tests ===")
    runner.test(
        "Basic query unchanged",
        lambda: sanitize_query("How does auth work?") == "How does auth work?" or (_ for _ in ()).throw(AssertionError("Query changed"))
    )

    runner.test(
        "Whitespace trimmed",
        lambda: sanitize_query("  query text  ") == "query text" or (_ for _ in ()).throw(AssertionError("Whitespace not trimmed"))
    )

    runner.test(
        "Multiple spaces collapsed",
        lambda: sanitize_query("multiple   spaces") == "multiple spaces" or (_ for _ in ()).throw(AssertionError("Spaces not collapsed"))
    )

    runner.test(
        "HTML tags stripped",
        lambda: sanitize_query("<script>alert(1)</script>Safe") == "alert(1)Safe" or (_ for _ in ()).throw(AssertionError("HTML not stripped"))
    )

    runner.expect_error(
        "Too long query rejected",
        lambda: sanitize_query("a" * 501)
    )

    runner.expect_error(
        "Empty query rejected",
        lambda: sanitize_query("")
    )

    # Timeout Validation Tests
    print("\n=== Timeout Validation Tests ===")
    runner.test(
        "Valid timeout accepted",
        lambda: validate_timeout(60) == 60 or (_ for _ in ()).throw(AssertionError("Valid timeout rejected"))
    )

    runner.expect_error(
        "Timeout too low rejected",
        lambda: validate_timeout(9)
    )

    runner.expect_error(
        "Timeout too high rejected",
        lambda: validate_timeout(601)
    )

    # Retry Validation Tests
    print("\n=== Retry Validation Tests ===")
    runner.test(
        "Valid retries accepted",
        lambda: validate_max_retries(3) == 3 or (_ for _ in ()).throw(AssertionError("Valid retries rejected"))
    )

    runner.expect_error(
        "Retries too low rejected",
        lambda: validate_max_retries(0)
    )

    runner.expect_error(
        "Retries too high rejected",
        lambda: validate_max_retries(6)
    )

    # Batch Query Tests
    print("\n=== Batch Query Tests ===")
    runner.test(
        "Single query parsed",
        lambda: parse_batch_queries("query1") == ["query1"] or (_ for _ in ()).throw(AssertionError("Single query failed"))
    )

    runner.test(
        "Multiple queries parsed",
        lambda: len(parse_batch_queries("query1, query2, query3")) == 3 or (_ for _ in ()).throw(AssertionError("Multiple queries failed"))
    )

    runner.test(
        "Whitespace trimmed in batch",
        lambda: parse_batch_queries("  q1  ,  q2  ") == ["q1", "q2"] or (_ for _ in ()).throw(AssertionError("Whitespace not trimmed"))
    )

    runner.expect_error(
        "Empty batch rejected",
        lambda: parse_batch_queries("")
    )

    # File Validation Tests
    print("\n=== File Validation Tests ===")

    # Create valid temp file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump({"queries": ["q1", "q2", "q3"]}, f)
        temp_valid = f.name

    runner.test(
        "Valid queries file parsed",
        lambda: len(validate_queries_file(temp_valid)) == 3 or (_ for _ in ()).throw(AssertionError("File parsing failed"))
    )

    Path(temp_valid).unlink()

    runner.expect_error(
        "Non-existent file rejected",
        lambda: validate_queries_file("/nonexistent/file.json")
    )

    # Format Validation Tests
    print("\n=== Format Validation Tests ===")
    runner.test(
        "JSON format valid",
        lambda: validate_format("json") == "json" or (_ for _ in ()).throw(AssertionError("JSON format rejected"))
    )

    runner.test(
        "Markdown format valid",
        lambda: validate_format("markdown") == "markdown" or (_ for _ in ()).throw(AssertionError("Markdown format rejected"))
    )

    runner.expect_error(
        "Invalid format rejected",
        lambda: validate_format("xml")
    )

    return runner.summary()


if __name__ == "__main__":
    sys.exit(run_tests())
