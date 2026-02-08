"""OSV (Open Source Vulnerabilities) API client.

Provides a client for querying the OSV vulnerability database to identify
known security vulnerabilities in third-party dependencies. Results are
cached locally for 24 hours to reduce API calls and improve performance
across repeated assessment runs.

API Documentation: https://osv.dev/docs/

Classes:
    OSVClient: HTTP client for the OSV v1 query endpoint with local
        filesystem caching.

Example:
    >>> client = OSVClient(cache_enabled=True)
    >>> vulns = client.query(
    ...     package_name="lodash",
    ...     version="4.17.15",
    ...     ecosystem="npm",
    ... )
    >>> for v in vulns:
    ...     print(v.get("id"), v.get("summary"))
"""

import hashlib
import json
import logging
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Cache TTL in seconds (24 hours).
_CACHE_TTL_SECONDS: int = 24 * 60 * 60


class OSVClient:
    """Client for the OSV vulnerability database API.

    Queries the OSV v1/query endpoint to retrieve known vulnerabilities
    for a specific package version within a given ecosystem. Implements
    a transparent 24-hour filesystem cache keyed on the SHA-256 hash of
    the query parameters.

    Attributes:
        API_URL: Base URL for the OSV query endpoint.
        CACHE_DIR: Default directory for cached responses.
        TIMEOUT_SECONDS: HTTP request timeout in seconds.
    """

    API_URL: str = "https://api.osv.dev/v1/query"
    CACHE_DIR: Path = Path.home() / ".cache" / "security-quality-assess" / "osv"
    TIMEOUT_SECONDS: int = 10

    def __init__(self, cache_enabled: bool = True) -> None:
        """Initialize the OSV client.

        When caching is enabled, the cache directory is created (including
        parent directories) if it does not already exist.

        Args:
            cache_enabled: If True, query results are cached locally for
                24 hours. Set to False to bypass the cache entirely.
        """
        self.cache_enabled: bool = cache_enabled
        if self.cache_enabled:
            try:
                self.CACHE_DIR.mkdir(parents=True, exist_ok=True)
            except OSError as exc:
                logger.warning(
                    "Failed to create OSV cache directory %s: %s",
                    self.CACHE_DIR,
                    exc,
                )
                self.cache_enabled = False

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def query(
        self,
        package_name: str,
        version: str,
        ecosystem: str,
    ) -> List[Dict[str, Any]]:
        """Query OSV for known vulnerabilities of a package version.

        Checks the local cache first (if caching is enabled). On a cache
        miss, sends a POST request to the OSV v1/query endpoint, caches
        the result, and returns the list of vulnerability records.

        All network and parsing errors are handled gracefully: the method
        logs a warning and returns an empty list so that a single failed
        lookup never crashes the overall assessment.

        Args:
            package_name: Package name as registered in its ecosystem
                (e.g., ``"lodash"`` for npm, ``"requests"`` for PyPI).
            version: Exact version string (e.g., ``"4.17.15"``).
            ecosystem: Package ecosystem identifier. Common values are
                ``"npm"``, ``"PyPI"``, ``"Go"``, ``"Maven"``, ``"crates.io"``.

        Returns:
            A list of vulnerability dictionaries as returned by the OSV
            API. Each dictionary typically contains:

            - ``id``: Vulnerability identifier (e.g., ``"CVE-2020-8203"``).
            - ``summary``: Human-readable description.
            - ``severity``: List of CVSS severity objects.
            - ``affected``: Affected version ranges and fixed versions.

            Returns an empty list when no vulnerabilities are found, or
            when any error prevents a successful lookup.
        """
        cache_key = self._get_cache_key(package_name, version, ecosystem)

        # Check cache first.
        if self.cache_enabled:
            cached = self._get_cached(cache_key)
            if cached is not None:
                logger.debug(
                    "OSV cache hit for %s:%s@%s",
                    ecosystem,
                    package_name,
                    version,
                )
                return cached

        # Build the JSON request body.
        request_body: Dict[str, Any] = {
            "package": {
                "name": package_name,
                "ecosystem": ecosystem,
            },
            "version": version,
        }

        try:
            vulnerabilities = self._send_request(request_body)
        except Exception:  # noqa: BLE001 -- intentional broad catch for graceful degradation
            # _send_request already logs the specific warning; return
            # empty to satisfy graceful-degradation contract.
            return []

        # Cache the successful result.
        if self.cache_enabled:
            self._cache_result(cache_key, vulnerabilities)

        return vulnerabilities

    # ------------------------------------------------------------------
    # Cache helpers
    # ------------------------------------------------------------------

    def _get_cache_key(
        self,
        package_name: str,
        version: str,
        ecosystem: str,
    ) -> str:
        """Generate a deterministic cache key from query parameters.

        The key is the hex-encoded SHA-256 digest of the string
        ``"{ecosystem}:{package_name}:{version}"``.

        Args:
            package_name: Package name.
            version: Package version.
            ecosystem: Package ecosystem.

        Returns:
            A 64-character lowercase hex string suitable for use as a
            cache filename stem.
        """
        key_string = f"{ecosystem}:{package_name}:{version}"
        return hashlib.sha256(key_string.encode("utf-8")).hexdigest()

    def _get_cached(self, cache_key: str) -> Optional[List[Dict[str, Any]]]:
        """Retrieve a cached response if it exists and has not expired.

        A cached entry is considered valid when:
        1. The cache file exists on disk.
        2. The file's modification time is within the 24-hour TTL window.
        3. The file contents are valid JSON that deserializes to a list.

        Args:
            cache_key: The SHA-256 hex digest returned by
                :meth:`_get_cache_key`.

        Returns:
            The cached list of vulnerability dicts, or ``None`` if the
            cache entry is missing, expired, or corrupt.
        """
        cache_file = self.CACHE_DIR / f"{cache_key}.json"

        if not cache_file.exists():
            return None

        # Check TTL based on file modification time.
        try:
            mtime = cache_file.stat().st_mtime
        except OSError:
            return None

        age_seconds = time.time() - mtime
        if age_seconds > _CACHE_TTL_SECONDS:
            logger.debug(
                "OSV cache expired for key %s (age=%.0fs)",
                cache_key[:12],
                age_seconds,
            )
            return None

        # Read and parse the cached JSON.
        try:
            raw = cache_file.read_text(encoding="utf-8")
            data = json.loads(raw)
            if isinstance(data, list):
                return data
            logger.warning(
                "OSV cache file %s contains unexpected JSON type; ignoring",
                cache_file,
            )
            return None
        except (json.JSONDecodeError, OSError) as exc:
            logger.warning(
                "Failed to read OSV cache file %s: %s",
                cache_file,
                exc,
            )
            return None

    def _cache_result(
        self,
        cache_key: str,
        data: List[Dict[str, Any]],
    ) -> None:
        """Write a query result to the local cache.

        The file is written atomically (write then flush) and errors are
        logged but never propagated -- caching is best-effort.

        Args:
            cache_key: The SHA-256 hex digest returned by
                :meth:`_get_cache_key`.
            data: The list of vulnerability dicts to persist.
        """
        cache_file = self.CACHE_DIR / f"{cache_key}.json"
        try:
            cache_file.write_text(
                json.dumps(data, indent=2),
                encoding="utf-8",
            )
        except OSError as exc:
            logger.warning(
                "Failed to write OSV cache file %s: %s",
                cache_file,
                exc,
            )

    # ------------------------------------------------------------------
    # HTTP transport
    # ------------------------------------------------------------------

    def _send_request(
        self,
        request_body: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """Send a POST request to the OSV API and return vulnerabilities.

        Handles the full HTTP lifecycle: serialization, request construction,
        timeout enforcement, response parsing, and error classification.

        Args:
            request_body: The JSON-serializable request payload.

        Returns:
            A list of vulnerability dictionaries from the ``"vulns"`` key
            of the response.

        Raises:
            Exception: Re-raised after logging when the request fails due
                to a network error, timeout, server error (5xx), or
                unparseable response body.
        """
        encoded_body = json.dumps(request_body).encode("utf-8")

        req = urllib.request.Request(
            self.API_URL,
            data=encoded_body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=self.TIMEOUT_SECONDS) as response:
                response_bytes = response.read()
        except urllib.error.HTTPError as exc:
            status = exc.code
            if 500 <= status < 600:
                logger.warning(
                    "OSV API returned server error %d for query %s",
                    status,
                    request_body.get("package", {}).get("name", "unknown"),
                )
            else:
                logger.warning(
                    "OSV API returned HTTP %d for query %s",
                    status,
                    request_body.get("package", {}).get("name", "unknown"),
                )
            raise
        except urllib.error.URLError as exc:
            logger.warning(
                "OSV API network error for query %s: %s",
                request_body.get("package", {}).get("name", "unknown"),
                exc.reason,
            )
            raise
        except TimeoutError:
            logger.warning(
                "OSV API request timed out after %ds for query %s",
                self.TIMEOUT_SECONDS,
                request_body.get("package", {}).get("name", "unknown"),
            )
            raise
        except OSError as exc:
            logger.warning(
                "OSV API request failed with OS error for query %s: %s",
                request_body.get("package", {}).get("name", "unknown"),
                exc,
            )
            raise

        # Parse the response JSON.
        try:
            data = json.loads(response_bytes.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            logger.warning(
                "Failed to parse OSV API response for query %s: %s",
                request_body.get("package", {}).get("name", "unknown"),
                exc,
            )
            raise

        if not isinstance(data, dict):
            logger.warning(
                "OSV API returned unexpected response type for query %s",
                request_body.get("package", {}).get("name", "unknown"),
            )
            return []

        vulns = data.get("vulns", [])
        if not isinstance(vulns, list):
            logger.warning(
                "OSV API 'vulns' field is not a list for query %s",
                request_body.get("package", {}).get("name", "unknown"),
            )
            return []

        return vulns
