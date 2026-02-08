"""Suppression model for security finding suppression configuration.

Suppressions allow teams to acknowledge known findings and temporarily or
permanently exclude them from reports. Each suppression targets a specific
rule and file path combination, with optional line-level granularity.

Usage:
    >>> config = SuppressionConfig.from_dict({
    ...     "version": "1.0",
    ...     "suppressions": [{
    ...         "rule_id": "hardcoded-secret",
    ...         "file_path": "config/settings.py",
    ...         "line_number": 42,
    ...         "reason": "Test fixture, not a real secret",
    ...         "expires": "2026-12-31",
    ...         "created_by": "developer@example.com"
    ...     }]
    ... })
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Optional

if TYPE_CHECKING:
    from lib.models.finding import Finding


@dataclass
class Suppression:
    """Finding suppression configuration.

    A suppression silences a specific detection rule for a given file path.
    Suppressions can target an entire file (line_number=None) or a specific
    line within that file.

    Attributes:
        rule_id: Rule to suppress (e.g., "hardcoded-secret"). Must match the
            rule_id field on a Finding exactly.
        file_path: File path relative to project root. Forward slashes are
            used for cross-platform comparison.
        line_number: Specific line to suppress. When None, the suppression
            applies to every finding in the file that matches the rule_id
            (file-level suppression).
        reason: Human-readable justification for why this suppression exists.
            Should explain why the finding is acceptable or a false positive.
        expires: Expiration date in ISO 8601 format ("YYYY-MM-DD"). After
            this date, the suppression is no longer active and the finding
            will reappear in reports.
        created_by: Identity of the person who created the suppression
            (e.g., email address or username).
        approved_by: Identity of the person who approved the suppression.
            None if approval is not required or has not yet been granted.
    """

    rule_id: str
    file_path: str
    line_number: Optional[int]
    reason: str
    expires: str  # ISO date string "YYYY-MM-DD"
    created_by: str
    approved_by: Optional[str] = None

    def is_expired(self) -> bool:
        """Check if this suppression has expired.

        Parses the ``expires`` field as an ISO 8601 date and compares it
        against the current date/time. If the date string is malformed or
        otherwise unparseable, the suppression is treated as expired as a
        safety measure (fail-closed).

        Returns:
            True if the suppression has expired or the date is invalid,
            False if the suppression is still active.
        """
        try:
            expiry_date = datetime.fromisoformat(self.expires)
            return datetime.now() > expiry_date
        except (ValueError, TypeError):
            # Invalid or missing date format -- treat as expired (fail-closed)
            return True

    def matches(self, finding: "Finding") -> bool:
        """Check if this suppression matches a given finding.

        Matching is performed in order of cheapest-to-evaluate first so that
        mismatches short-circuit quickly.

        Matching rules:
            1. ``rule_id`` must be an exact match.
            2. ``file_path`` must match after normalizing backslashes to
               forward slashes on both sides.
            3. If ``line_number`` is not None, it must equal the finding's
               line_number. If ``line_number`` is None this is a file-level
               suppression and any line in the file matches.

        Args:
            finding: A Finding instance to check against this suppression.

        Returns:
            True if all conditions match, False otherwise.
        """
        # 1. Rule ID must match exactly
        if finding.rule_id != self.rule_id:
            return False

        # 2. Normalize paths (handle Windows backslashes) and compare
        normalized_finding_path = finding.file_path.replace("\\", "/")
        normalized_suppression_path = self.file_path.replace("\\", "/")
        if normalized_finding_path != normalized_suppression_path:
            return False

        # 3. Line number check: None means file-level (matches any line)
        if self.line_number is not None:
            if finding.line_number != self.line_number:
                return False

        return True


@dataclass
class SuppressionConfig:
    """Container for all suppression rules.

    Represents the full contents of a suppression configuration file
    (typically ``.security-suppressions.json`` at the project root).

    Attributes:
        version: Schema version string for the configuration format.
            Used for forward-compatible parsing of newer config files.
        suppressions: List of individual suppression rules.
    """

    version: str
    suppressions: List[Suppression] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SuppressionConfig":
        """Create a SuppressionConfig from a dictionary.

        Intended for use with data loaded from JSON configuration files.
        Each entry in the ``suppressions`` list is unpacked as keyword
        arguments to the ``Suppression`` constructor.

        Args:
            data: Dictionary typically loaded via ``json.load()``. Expected
                keys are ``version`` (str, defaults to "1.0") and
                ``suppressions`` (list of dicts).

        Returns:
            A fully-constructed SuppressionConfig instance.

        Example:
            >>> import json
            >>> with open(".security-suppressions.json") as f:
            ...     config = SuppressionConfig.from_dict(json.load(f))
        """
        suppressions = [
            Suppression(**s) for s in data.get("suppressions", [])
        ]
        return cls(
            version=data.get("version", "1.0"),
            suppressions=suppressions,
        )
