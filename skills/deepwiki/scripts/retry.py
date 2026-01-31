"""
Retry logic with exponential backoff for DeepWiki queries.

This module provides retry functionality for handling transient failures
in browser automation and network operations.
"""

import time
import sys
from typing import Callable, Any, Optional, Dict
from datetime import datetime, timezone


# Retryable error types (by class name)
RETRYABLE_ERRORS = [
    "TimeoutError",
    "NavigationError",
    "NetworkError",
    "RateLimitError",
    "ConnectionError",
    "BrowserError"  # Generic browser errors may be transient
]

# Non-retryable error types
NON_RETRYABLE_ERRORS = [
    "ValidationError",
    "ElementNotFoundError",  # DOM structure issue (won't fix on retry)
    "ResponseExtractionError",  # Data format issue (won't fix on retry)
    "CacheError"
]


class RetryExhaustedError(Exception):
    """Raised when all retry attempts are exhausted."""
    pass


class RateLimitError(Exception):
    """Raised when rate limited by service."""
    pass


def is_retryable_error(error: Exception) -> bool:
    """
    Determine if an error is retryable.

    Args:
        error: Exception to check

    Returns:
        True if error should be retried, False otherwise

    Examples:
        >>> is_retryable_error(TimeoutError("timeout"))
        True
        >>> is_retryable_error(ValueError("bad input"))
        False
    """
    error_type = type(error).__name__

    # Explicitly non-retryable
    if error_type in NON_RETRYABLE_ERRORS:
        return False

    # Explicitly retryable
    if error_type in RETRYABLE_ERRORS:
        return True

    # Default: don't retry unknown errors
    return False


def calculate_backoff_delay(
    attempt: int,
    base_delay: int = 5,
    max_delay: int = 60,
    error: Optional[Exception] = None
) -> int:
    """
    Calculate backoff delay for retry attempt.

    Uses exponential backoff: base * (2 ^ (attempt - 1))
    Special case: RateLimitError uses fixed 60s delay

    Args:
        attempt: Current attempt number (1-indexed)
        base_delay: Base delay in seconds (default: 5)
        max_delay: Maximum delay in seconds (default: 60)
        error: Optional error that triggered retry

    Returns:
        Delay in seconds

    Examples:
        >>> calculate_backoff_delay(1)  # First retry
        5
        >>> calculate_backoff_delay(2)  # Second retry
        10
        >>> calculate_backoff_delay(3)  # Third retry
        20
        >>> calculate_backoff_delay(4)  # Fourth retry (capped)
        40
    """
    # Special handling for rate limits
    if error and isinstance(error, RateLimitError):
        return 60

    # Exponential backoff: 5s, 10s, 20s, 40s, ...
    delay = base_delay * (2 ** (attempt - 1))

    # Cap at max delay
    return min(delay, max_delay)


def execute_with_retry(
    func: Callable[[], Any],
    max_attempts: int = 3,
    backoff_base: int = 5,
    verbose: bool = False,
    retry_metadata: Optional[Dict] = None
) -> Any:
    """
    Execute a function with retry logic and exponential backoff.

    Args:
        func: Function to execute (should take no arguments)
        max_attempts: Maximum number of attempts (default: 3)
        backoff_base: Base delay for exponential backoff (default: 5 seconds)
        verbose: Enable verbose logging to stderr
        retry_metadata: Optional dict to store retry statistics

    Returns:
        Result from successful function execution

    Raises:
        RetryExhaustedError: If all attempts fail with retryable errors
        Exception: If non-retryable error occurs

    Examples:
        >>> def flaky_function():
        ...     # May fail sometimes
        ...     return "success"
        >>> result = execute_with_retry(flaky_function, max_attempts=3)
    """
    last_error = None
    retry_attempts = []

    for attempt in range(1, max_attempts + 1):
        attempt_start = time.time()

        try:
            if verbose and attempt > 1:
                print(f"\n[Retry] Attempt {attempt}/{max_attempts}", file=sys.stderr)

            # Execute function
            result = func()

            # Success - record metadata and return
            if retry_metadata is not None:
                retry_metadata["attempts"] = attempt
                retry_metadata["retry_history"] = retry_attempts
                retry_metadata["succeeded"] = True

            if verbose and attempt > 1:
                print(f"[Retry] ✅ Success on attempt {attempt}", file=sys.stderr)

            return result

        except Exception as e:
            last_error = e
            attempt_duration = time.time() - attempt_start

            # Record attempt
            retry_attempts.append({
                "attempt": attempt,
                "error_type": type(e).__name__,
                "error_message": str(e),
                "duration_seconds": round(attempt_duration, 2),
                "timestamp": datetime.now(timezone.utc).isoformat()
            })

            # Check if error is retryable
            if not is_retryable_error(e):
                if verbose:
                    print(f"\n[Retry] ❌ Non-retryable error: {type(e).__name__}", file=sys.stderr)
                    print(f"[Retry] Error: {e}", file=sys.stderr)

                # Record metadata and re-raise
                if retry_metadata is not None:
                    retry_metadata["attempts"] = attempt
                    retry_metadata["retry_history"] = retry_attempts
                    retry_metadata["succeeded"] = False
                    retry_metadata["final_error"] = {
                        "type": type(e).__name__,
                        "message": str(e),
                        "retryable": False
                    }

                raise

            # Last attempt - no more retries
            if attempt == max_attempts:
                if verbose:
                    print(f"\n[Retry] ❌ All {max_attempts} attempts exhausted", file=sys.stderr)
                    print(f"[Retry] Final error: {type(e).__name__}: {e}", file=sys.stderr)

                # Record metadata
                if retry_metadata is not None:
                    retry_metadata["attempts"] = attempt
                    retry_metadata["retry_history"] = retry_attempts
                    retry_metadata["succeeded"] = False
                    retry_metadata["final_error"] = {
                        "type": type(e).__name__,
                        "message": str(e),
                        "retryable": True
                    }

                # Wrap in RetryExhaustedError
                raise RetryExhaustedError(
                    f"Failed after {max_attempts} attempts. "
                    f"Last error: {type(e).__name__}: {e}"
                ) from e

            # Calculate backoff delay
            delay = calculate_backoff_delay(attempt, backoff_base, error=e)

            # Log retry
            if verbose:
                print(f"\n[Retry] ⚠️  Attempt {attempt} failed: {type(e).__name__}", file=sys.stderr)
                print(f"[Retry] Error: {e}", file=sys.stderr)
                print(f"[Retry] Waiting {delay}s before retry...", file=sys.stderr)

            # Wait before retry
            time.sleep(delay)

    # Should never reach here, but just in case
    raise RetryExhaustedError(f"Unexpected retry exhaustion") from last_error


def retry_with_context(
    func: Callable[[], Any],
    context: str,
    max_attempts: int = 3,
    backoff_base: int = 5,
    verbose: bool = False
) -> Any:
    """
    Execute function with retry and context logging.

    This is a wrapper around execute_with_retry() that adds context
    to retry messages (e.g., "Querying DeepWiki").

    Args:
        func: Function to execute
        context: Context string for logging (e.g., "Executing query")
        max_attempts: Maximum attempts
        backoff_base: Base backoff delay
        verbose: Enable verbose logging

    Returns:
        Result from successful execution

    Raises:
        RetryExhaustedError: If all attempts fail
        Exception: If non-retryable error occurs

    Examples:
        >>> result = retry_with_context(
        ...     lambda: query_deepwiki(),
        ...     context="Querying DeepWiki",
        ...     max_attempts=3
        ... )
    """
    if verbose:
        print(f"\n[Retry] {context}", file=sys.stderr)
        if max_attempts > 1:
            print(f"[Retry] Retry policy: {max_attempts} attempts, {backoff_base}s base backoff", file=sys.stderr)

    return execute_with_retry(func, max_attempts, backoff_base, verbose)


# Convenience function for common retry scenarios
def retry_browser_operation(
    func: Callable[[], Any],
    operation_name: str = "Browser operation",
    verbose: bool = False
) -> Any:
    """
    Retry browser automation operation with sensible defaults.

    Default policy:
    - 3 attempts
    - 5 second base backoff
    - Exponential backoff (5s, 10s, 20s)

    Args:
        func: Browser operation to execute
        operation_name: Name of operation for logging
        verbose: Enable verbose logging

    Returns:
        Result from successful execution

    Examples:
        >>> result = retry_browser_operation(
        ...     lambda: navigate_to_page(url),
        ...     operation_name="Navigate to DeepWiki",
        ...     verbose=True
        ... )
    """
    return retry_with_context(
        func,
        context=operation_name,
        max_attempts=3,
        backoff_base=5,
        verbose=verbose
    )
