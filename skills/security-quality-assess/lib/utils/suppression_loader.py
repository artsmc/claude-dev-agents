"""Suppression configuration loader and applicator.

Loads ``.security-suppress.json`` files from a project root, validates their
schema, checks for expired entries, and applies suppression rules to filter
findings produced by the security analyzers.

This module is the bridge between the raw JSON configuration on disk and the
``Suppression`` / ``SuppressionConfig`` model objects consumed by the rest of
the assessment pipeline.

Functions:
    load_suppression_config: Discover and parse the suppression config file.
    validate_suppression_schema: Validate the structure of parsed JSON data.
    check_expired_suppressions: Identify and warn about expired entries.
    apply_suppressions: Filter a list of findings against active suppressions.

Usage:
    >>> from pathlib import Path
    >>> from lib.utils.suppression_loader import (
    ...     load_suppression_config,
    ...     apply_suppressions,
    ... )
    >>> config = load_suppression_config(Path("/path/to/project"))
    >>> if config is not None:
    ...     filtered, count = apply_suppressions(findings, config)
"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from lib.models.finding import Finding
from lib.models.suppression import Suppression, SuppressionConfig

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SUPPRESSION_FILENAME = ".security-suppress.json"
"""Default filename for the suppression configuration file."""

SUPPORTED_VERSIONS = ("1.0",)
"""Schema versions that this loader understands."""

_REQUIRED_TOP_LEVEL_KEYS = ("version", "suppressions")
"""Keys that must be present at the top level of the config JSON."""

_REQUIRED_SUPPRESSION_KEYS = ("rule_id", "file_path", "reason", "expires", "created_by")
"""Keys that must be present on each individual suppression entry."""

_OPTIONAL_SUPPRESSION_KEYS = ("line_number", "approved_by")
"""Keys that may be present on a suppression entry but are not required."""

_ALL_KNOWN_SUPPRESSION_KEYS = _REQUIRED_SUPPRESSION_KEYS + _OPTIONAL_SUPPRESSION_KEYS
"""Union of required and optional keys, used for unknown-key warnings."""


# ---------------------------------------------------------------------------
# Schema validation
# ---------------------------------------------------------------------------

def validate_suppression_schema(data: Any) -> List[str]:
    """Validate the structure of a parsed suppression configuration.

    Performs lenient validation: collects warnings rather than raising
    exceptions. Callers decide whether to proceed or abort based on the
    returned warning list.

    Checks performed:
        1. Top-level value must be a ``dict``.
        2. Required top-level keys (``version``, ``suppressions``) present.
        3. ``version`` value is a known version string.
        4. ``suppressions`` value is a ``list``.
        5. Each suppression entry is a ``dict`` with required keys.
        6. ``expires`` values are valid ISO 8601 date strings.
        7. ``line_number``, when present, is a positive integer.
        8. Unknown keys on suppression entries generate warnings.

    Args:
        data: The raw value returned by ``json.load()``.  Expected to be a
            ``dict`` but any type is accepted for validation purposes.

    Returns:
        A list of human-readable warning strings.  An empty list means the
        schema is fully valid.

    Example:
        >>> warnings = validate_suppression_schema({"version": "1.0", "suppressions": []})
        >>> len(warnings)
        0
    """
    warnings: List[str] = []

    # 1. Top-level type check
    if not isinstance(data, dict):
        warnings.append(
            f"Config must be a JSON object, got {type(data).__name__}"
        )
        return warnings  # Cannot validate further

    # 2. Required top-level keys
    for key in _REQUIRED_TOP_LEVEL_KEYS:
        if key not in data:
            warnings.append(f"Missing required top-level key: '{key}'")

    # 3. Version value
    version = data.get("version")
    if version is not None and version not in SUPPORTED_VERSIONS:
        warnings.append(
            f"Unsupported config version '{version}'; "
            f"supported versions: {', '.join(SUPPORTED_VERSIONS)}"
        )

    # 4. Suppressions list type
    suppressions_raw = data.get("suppressions")
    if suppressions_raw is not None and not isinstance(suppressions_raw, list):
        warnings.append(
            f"'suppressions' must be a list, got {type(suppressions_raw).__name__}"
        )
        return warnings  # Cannot iterate

    if suppressions_raw is None:
        return warnings  # Already warned about missing key

    # 5-8. Per-entry validation
    for idx, entry in enumerate(suppressions_raw):
        prefix = f"suppressions[{idx}]"

        if not isinstance(entry, dict):
            warnings.append(f"{prefix}: entry must be a JSON object, got {type(entry).__name__}")
            continue

        # 5. Required keys
        for key in _REQUIRED_SUPPRESSION_KEYS:
            if key not in entry:
                warnings.append(f"{prefix}: missing required key '{key}'")

        # 6. Date format
        expires_value = entry.get("expires")
        if expires_value is not None:
            if not isinstance(expires_value, str):
                warnings.append(
                    f"{prefix}: 'expires' must be a string, got {type(expires_value).__name__}"
                )
            else:
                try:
                    datetime.fromisoformat(expires_value)
                except ValueError:
                    warnings.append(
                        f"{prefix}: 'expires' is not a valid ISO 8601 date: '{expires_value}'"
                    )

        # 7. line_number type
        line_number = entry.get("line_number")
        if line_number is not None:
            if not isinstance(line_number, int) or isinstance(line_number, bool):
                warnings.append(
                    f"{prefix}: 'line_number' must be a positive integer, "
                    f"got {type(line_number).__name__}"
                )
            elif line_number < 1:
                warnings.append(
                    f"{prefix}: 'line_number' must be positive, got {line_number}"
                )

        # 8. Unknown keys
        unknown_keys = set(entry.keys()) - set(_ALL_KNOWN_SUPPRESSION_KEYS)
        if unknown_keys:
            warnings.append(
                f"{prefix}: unknown keys will be ignored: {sorted(unknown_keys)}"
            )

    return warnings


# ---------------------------------------------------------------------------
# Expiration checking
# ---------------------------------------------------------------------------

def check_expired_suppressions(
    config: SuppressionConfig,
) -> Tuple[List[Suppression], List[Suppression]]:
    """Partition suppressions into active and expired groups.

    Iterates through every suppression in the configuration and calls
    ``Suppression.is_expired()`` on each.  Expired entries are logged as
    warnings so that teams are reminded to clean up stale suppressions.

    Args:
        config: A fully-loaded ``SuppressionConfig`` instance.

    Returns:
        A 2-tuple of ``(active, expired)`` where each element is a list of
        ``Suppression`` objects.  The union of both lists equals the original
        ``config.suppressions``.

    Example:
        >>> active, expired = check_expired_suppressions(config)
        >>> print(f"{len(expired)} expired suppressions found")
    """
    active: List[Suppression] = []
    expired: List[Suppression] = []

    for suppression in config.suppressions:
        if suppression.is_expired():
            expired.append(suppression)
            logger.warning(
                "Expired suppression: rule_id='%s', file_path='%s', "
                "expires='%s' -- this suppression will not be applied",
                suppression.rule_id,
                suppression.file_path,
                suppression.expires,
            )
        else:
            active.append(suppression)

    if expired:
        logger.warning(
            "%d of %d suppression(s) have expired and will not be applied",
            len(expired),
            len(config.suppressions),
        )

    return active, expired


# ---------------------------------------------------------------------------
# Config loading
# ---------------------------------------------------------------------------

def _sanitize_suppression_entry(entry: Dict[str, Any]) -> Dict[str, Any]:
    """Strip unknown keys and apply defaults for a suppression entry.

    The ``Suppression`` dataclass constructor will raise ``TypeError`` if
    unexpected keyword arguments are passed.  This function keeps only the
    keys that the dataclass accepts so that forward-compatible config files
    with extra fields do not break loading.

    It also ensures that ``line_number`` defaults to ``None`` when absent,
    because the ``Suppression`` dataclass declares ``line_number`` as
    ``Optional[int]`` without a default value (it appears before fields that
    have defaults, per dataclass ordering rules).

    Args:
        entry: Raw dictionary from the JSON ``suppressions`` list.

    Returns:
        A new dictionary containing only the keys accepted by ``Suppression``,
        with ``line_number`` defaulting to ``None`` if not present.
    """
    sanitized = {k: v for k, v in entry.items() if k in _ALL_KNOWN_SUPPRESSION_KEYS}
    # Ensure line_number is present (defaults to None for file-level suppression)
    if "line_number" not in sanitized:
        sanitized["line_number"] = None
    return sanitized


def load_suppression_config(project_path: Path) -> Optional[SuppressionConfig]:
    """Load and validate the suppression configuration from a project root.

    Searches for ``SUPPRESSION_FILENAME`` (default: ``.security-suppress.json``)
    in the given ``project_path`` directory.  If the file is found, it is parsed
    as JSON, validated against the expected schema, and converted into a
    ``SuppressionConfig`` instance.

    The function is intentionally lenient:

    * If the config file does not exist, ``None`` is returned silently (this
      is the normal case for projects without suppressions).
    * If the file is unreadable or contains invalid JSON, a warning is logged
      and ``None`` is returned.
    * If schema validation produces warnings, they are logged but loading
      continues.  Only structural failures that prevent construction of the
      model cause ``None`` to be returned.

    Args:
        project_path: Absolute or relative ``Path`` to the project root
            directory.  The suppression file is expected to be a direct child
            of this directory.

    Returns:
        A ``SuppressionConfig`` instance if the file was found and parsed
        successfully, or ``None`` if the file does not exist or is fatally
        malformed.

    Example:
        >>> from pathlib import Path
        >>> config = load_suppression_config(Path("/home/user/my-project"))
        >>> if config is not None:
        ...     print(f"Loaded {len(config.suppressions)} suppressions")
    """
    config_path = Path(project_path) / SUPPRESSION_FILENAME

    # ------------------------------------------------------------------
    # 1. File existence check
    # ------------------------------------------------------------------
    if not config_path.exists():
        logger.debug(
            "No suppression config found at %s -- continuing without suppressions",
            config_path,
        )
        return None

    if not config_path.is_file():
        logger.warning(
            "Suppression config path exists but is not a file: %s",
            config_path,
        )
        return None

    # ------------------------------------------------------------------
    # 2. Read and parse JSON
    # ------------------------------------------------------------------
    try:
        raw_text = config_path.read_text(encoding="utf-8")
    except OSError as exc:
        logger.warning(
            "Could not read suppression config at %s: %s",
            config_path,
            exc,
        )
        return None

    try:
        data = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        logger.warning(
            "Invalid JSON in suppression config at %s: %s",
            config_path,
            exc,
        )
        return None

    # ------------------------------------------------------------------
    # 3. Schema validation (lenient -- log warnings, don't fail)
    # ------------------------------------------------------------------
    schema_warnings = validate_suppression_schema(data)
    for warning in schema_warnings:
        logger.warning("Suppression config validation: %s", warning)

    # If the data is not even a dict or has no suppressions list, bail out
    if not isinstance(data, dict):
        return None

    suppressions_raw = data.get("suppressions")
    if suppressions_raw is not None and not isinstance(suppressions_raw, list):
        return None

    # ------------------------------------------------------------------
    # 4. Construct model objects
    # ------------------------------------------------------------------
    suppressions: List[Suppression] = []
    entries = suppressions_raw if suppressions_raw is not None else []

    for idx, entry in enumerate(entries):
        if not isinstance(entry, dict):
            logger.warning(
                "Skipping suppressions[%d]: not a JSON object", idx
            )
            continue

        # Check that minimum required keys are present
        missing_keys = [
            k for k in _REQUIRED_SUPPRESSION_KEYS if k not in entry
        ]
        if missing_keys:
            logger.warning(
                "Skipping suppressions[%d]: missing required keys %s",
                idx,
                missing_keys,
            )
            continue

        # Sanitize entry to strip unknown keys before dataclass construction
        sanitized = _sanitize_suppression_entry(entry)

        try:
            suppression = Suppression(**sanitized)
            suppressions.append(suppression)
        except TypeError as exc:
            logger.warning(
                "Skipping suppressions[%d]: construction error: %s",
                idx,
                exc,
            )
            continue

    config = SuppressionConfig(
        version=data.get("version", "1.0"),
        suppressions=suppressions,
    )

    logger.info(
        "Loaded suppression config from %s: version=%s, %d suppression(s)",
        config_path,
        config.version,
        len(config.suppressions),
    )

    return config


# ---------------------------------------------------------------------------
# Suppression application
# ---------------------------------------------------------------------------

def apply_suppressions(
    findings: List[Finding],
    config: SuppressionConfig,
) -> Tuple[List[Finding], int]:
    """Filter findings by applying active (non-expired) suppression rules.

    For each finding, checks whether any **active** suppression matches it
    using ``Suppression.matches()``.  Expired suppressions are excluded from
    matching and logged as warnings.

    The function does not mutate the input list; it returns a new list of
    findings that were not suppressed.

    Args:
        findings: List of ``Finding`` objects produced by the analyzers.
        config: A ``SuppressionConfig`` loaded by ``load_suppression_config()``.

    Returns:
        A 2-tuple of ``(filtered_findings, suppressed_count)`` where:
            - ``filtered_findings`` contains only findings that did **not**
              match any active suppression.
            - ``suppressed_count`` is the number of findings that were removed.

    Example:
        >>> filtered, suppressed = apply_suppressions(findings, config)
        >>> print(f"{suppressed} finding(s) suppressed, {len(filtered)} remaining")
    """
    # Partition into active and expired
    active_suppressions, expired_suppressions = check_expired_suppressions(config)

    if not active_suppressions:
        if expired_suppressions:
            logger.info(
                "All %d suppression(s) are expired -- no findings will be suppressed",
                len(expired_suppressions),
            )
        return list(findings), 0

    filtered: List[Finding] = []
    suppressed_count = 0

    for finding in findings:
        matched = False
        for suppression in active_suppressions:
            if suppression.matches(finding):
                matched = True
                logger.info(
                    "Suppressed finding: rule_id='%s', file='%s', line=%d "
                    "(reason: %s)",
                    finding.rule_id,
                    finding.file_path,
                    finding.line_number,
                    suppression.reason,
                )
                break

        if matched:
            suppressed_count += 1
        else:
            filtered.append(finding)

    logger.info(
        "Suppression summary: %d finding(s) suppressed, %d remaining "
        "(%d active rule(s), %d expired rule(s))",
        suppressed_count,
        len(filtered),
        len(active_suppressions),
        len(expired_suppressions),
    )

    return filtered, suppressed_count
