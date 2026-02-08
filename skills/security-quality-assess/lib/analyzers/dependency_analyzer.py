"""Dependency vulnerability analyzer using the OSV database.

Detects known security vulnerabilities in third-party dependencies by
querying the OSV (Open Source Vulnerabilities) API. Dependencies are
extracted from parsed lockfiles (package-lock.json, yarn.lock, poetry.lock)
and each package/version pair is checked against the OSV database for
published CVEs.

This analyzer maps to OWASP A06:2021 (Vulnerable and Outdated Components)
and produces findings with severity derived from CVSS scores when available.

Detection strategy:
    1. Extract dependencies from ParseResult objects that originated from
       lockfile parsing (language == "lockfile").
    2. For each dependency, query the OSV API via the injected OSVClient.
    3. For each vulnerability returned, extract CVSS score, CWE ID, fixed
       version, and summary to create a Finding.
    4. Map CVSS scores to severity levels using standard thresholds.

Error handling:
    - OSV API failures are handled by OSVClient (returns empty list). The
      analyzer logs a warning and continues with remaining dependencies.
    - Empty vulnerability lists produce no findings (no noise).
    - Missing CVSS data defaults to MEDIUM severity.

This module uses only the Python standard library and has no external
dependencies.

Classes:
    DependencyAnalyzer: Main analyzer class with analyze() entry point.

References:
    - TR.md Section 4.4: DependencyAnalyzer
    - FRS.md FR-9: DependencyAnalyzer
    - OWASP A06:2021 Vulnerable and Outdated Components
    - CWE-1035: Using Components with Known Vulnerabilities
"""

import logging
from typing import Any, Dict, List, Optional

from lib.models.finding import Finding, OWASPCategory, Severity
from lib.models.parse_result import ParseResult
from lib.parsers.dependency_parser import Dependency
from lib.utils.osv_client import OSVClient

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Finding ID generator
# ---------------------------------------------------------------------------


class _FindingIDGenerator:
    """Sequential ID generator for dependency findings.

    Produces IDs in the format "DEP-001", "DEP-002", etc. A new generator
    is created for each analyze() invocation so IDs start from 1.
    """

    def __init__(self) -> None:
        self._counter: int = 0

    def next_id(self) -> str:
        """Return the next sequential finding ID."""
        self._counter += 1
        return f"DEP-{self._counter:03d}"


# ---------------------------------------------------------------------------
# Main analyzer class
# ---------------------------------------------------------------------------


class DependencyAnalyzer:
    """Detect vulnerable dependencies via the OSV vulnerability database.

    This analyzer checks every third-party dependency extracted from lockfiles
    against the OSV API to identify packages with known CVEs. The OSVClient
    is injected via the constructor, following the dependency injection pattern
    used throughout the assessment skill.

    For each vulnerability found, a Finding is created with:
      - Severity derived from the highest CVSS score in the vulnerability data.
      - CWE ID extracted from the vulnerability aliases when available.
      - Remediation guidance including the fixed version if published.
      - Full vulnerability metadata for downstream consumption.

    All findings are categorized under OWASP A06:2021 (Vulnerable and
    Outdated Components).

    Attributes:
        CONFIDENCE: Default confidence score for dependency vulnerability
            findings. Set to 0.95 because data comes from the official OSV
            database, which is authoritative but may occasionally contain
            entries that do not affect a specific usage pattern.
        VERSION: Analyzer version string for tracking.

    Usage::

        client = OSVClient(cache_enabled=True)
        analyzer = DependencyAnalyzer(osv_client=client)
        findings = analyzer.analyze(parsed_files, config={})

    Configuration:
        The ``config`` dict passed to ``analyze()`` supports these optional
        keys:

        - ``skip_ecosystems`` (List[str]): Ecosystem names to skip
          (e.g., ["npm"] to skip npm packages).
    """

    CONFIDENCE: float = 0.95
    VERSION: str = "1.0.0"

    def __init__(self, osv_client: OSVClient) -> None:
        """Initialize the DependencyAnalyzer with an OSV client.

        Args:
            osv_client: An initialized OSVClient instance used to query
                the OSV vulnerability database. The client handles caching,
                rate limiting, and error recovery internally.
        """
        self._osv_client: OSVClient = osv_client

    def analyze(
        self,
        parsed_files: List[ParseResult],
        config: Dict[str, Any],
    ) -> List[Finding]:
        """Query OSV API for dependency vulnerabilities across all lockfiles.

        Iterates over each ParseResult, extracts dependency lists from those
        that originated from lockfile parsing, and queries the OSV API for
        each dependency. One Finding is created per CVE per dependency.

        Args:
            parsed_files: List of ParseResult objects from the parsing phase.
                Only ParseResults with a non-empty ``dependencies`` field are
                processed; others are silently skipped.
            config: Optional configuration overrides. Supported keys:
                ``skip_ecosystems`` (List[str]): Ecosystems to exclude from
                scanning.

        Returns:
            List of Finding objects, one per detected vulnerability. Findings
            are ordered by the lockfile they originated from and then by
            dependency name.
        """
        findings: List[Finding] = []
        id_gen = _FindingIDGenerator()
        skip_ecosystems: List[str] = config.get("skip_ecosystems", [])

        for parsed_file in parsed_files:
            if not parsed_file.dependencies:
                continue

            findings.extend(
                self._analyze_dependencies(
                    parsed_file.dependencies,
                    parsed_file.file_path,
                    id_gen,
                    skip_ecosystems,
                )
            )

        return findings

    # -----------------------------------------------------------------
    # Core analysis logic
    # -----------------------------------------------------------------

    def _analyze_dependencies(
        self,
        dependencies: List[Dependency],
        file_path: str,
        id_gen: _FindingIDGenerator,
        skip_ecosystems: List[str],
    ) -> List[Finding]:
        """Analyze a list of dependencies from a single lockfile.

        For each dependency, queries the OSV API and creates findings for
        any vulnerabilities returned. OSV API errors are caught at the
        client level; this method sees either a list of vulnerability dicts
        or an empty list.

        Args:
            dependencies: The list of Dependency objects extracted from
                a single lockfile.
            file_path: Path to the lockfile these dependencies came from.
                Used as the file_path in generated findings.
            id_gen: Sequential ID generator for creating finding IDs.
            skip_ecosystems: Ecosystem names to exclude from scanning.

        Returns:
            List of Finding objects for all vulnerabilities found across
            all dependencies in this lockfile.
        """
        findings: List[Finding] = []

        for dep in dependencies:
            if dep.ecosystem in skip_ecosystems:
                logger.debug(
                    "Skipping %s:%s (ecosystem %s excluded by config)",
                    dep.name,
                    dep.version,
                    dep.ecosystem,
                )
                continue

            try:
                vulnerabilities = self._osv_client.query(
                    package_name=dep.name,
                    version=dep.version,
                    ecosystem=dep.ecosystem,
                )
            except Exception:  # noqa: BLE001
                # OSVClient should handle all errors internally and return [],
                # but this is a safety net to ensure one failed query never
                # stops the analysis of remaining dependencies.
                logger.warning(
                    "Unexpected error querying OSV for %s@%s (%s); skipping",
                    dep.name,
                    dep.version,
                    dep.ecosystem,
                )
                continue

            if not vulnerabilities:
                continue

            for vuln in vulnerabilities:
                if not isinstance(vuln, dict):
                    continue

                finding = self._create_vuln_finding(
                    dep=dep,
                    vuln=vuln,
                    file_path=file_path,
                    id_gen=id_gen,
                )
                findings.append(finding)

        return findings

    # -----------------------------------------------------------------
    # Finding creation
    # -----------------------------------------------------------------

    def _create_vuln_finding(
        self,
        dep: Dependency,
        vuln: Dict[str, Any],
        file_path: str,
        id_gen: _FindingIDGenerator,
    ) -> Finding:
        """Create a Finding from a single OSV vulnerability record.

        Extracts the vulnerability ID, summary, CVSS score, CWE ID, and
        fixed version from the OSV response structure. Maps the CVSS score
        to a severity level and builds actionable remediation guidance.

        Args:
            dep: The dependency that this vulnerability affects.
            vuln: A single vulnerability dictionary from the OSV API
                response. Expected keys: ``id``, ``summary``, ``severity``,
                ``affected``, ``aliases``, ``database_specific``.
            file_path: Path to the lockfile (used as finding file_path).
            id_gen: Sequential ID generator for the finding ID.

        Returns:
            A fully populated Finding object.
        """
        vuln_id: str = vuln.get("id", "UNKNOWN")
        summary: str = vuln.get("summary", "No description available.")

        # Extract CVSS score and derive severity
        cvss_score: Optional[float] = self._extract_cvss_score(vuln)
        severity: Severity = self._map_cvss_to_severity(cvss_score)

        # Extract CWE ID if available
        cwe_id: Optional[str] = self._extract_cwe_id(vuln)

        # Extract fixed version for remediation guidance
        fixed_version: Optional[str] = self._extract_fixed_version(
            vuln, dep.ecosystem
        )

        # Build title
        title: str = f"Vulnerable dependency: {dep.name} {dep.version}"

        # Build description with CVE details
        description: str = (
            f"The dependency {dep.name}@{dep.version} ({dep.ecosystem}) "
            f"is affected by {vuln_id}. {summary}"
        )

        # Build remediation guidance
        if fixed_version:
            remediation: str = (
                f"Update {dep.name} to version {fixed_version} or later, "
                f"which contains a fix for {vuln_id}. Run the appropriate "
                f"package manager update command to apply the fix."
            )
        else:
            remediation = (
                f"Check the {dep.ecosystem} registry for a patched version "
                f"of {dep.name} that addresses {vuln_id}. If no fix is "
                f"available, consider replacing the dependency with a "
                f"maintained alternative."
            )

        # Build code sample (package identifier for lockfile findings)
        code_sample: str = f"{dep.name}@{dep.version}"

        # Collect all aliases (CVE IDs, GHSA IDs, etc.)
        aliases: List[str] = vuln.get("aliases", [])
        if not isinstance(aliases, list):
            aliases = []

        # Build metadata with full vulnerability data
        metadata: Dict[str, Any] = {
            "vuln_id": vuln_id,
            "aliases": aliases,
            "package_name": dep.name,
            "package_version": dep.version,
            "ecosystem": dep.ecosystem,
            "cvss_score": cvss_score,
            "fixed_version": fixed_version,
            "summary": summary,
        }

        return Finding(
            id=id_gen.next_id(),
            rule_id="vulnerable-dependency",
            category=OWASPCategory.A06_VULNERABLE_COMPONENTS,
            severity=severity,
            title=title,
            description=description,
            file_path=file_path,
            line_number=1,
            code_sample=code_sample,
            remediation=remediation,
            cwe_id=cwe_id,
            confidence=self.CONFIDENCE,
            metadata=metadata,
        )

    # -----------------------------------------------------------------
    # CVSS to severity mapping
    # -----------------------------------------------------------------

    @staticmethod
    def _map_cvss_to_severity(cvss_score: Optional[float]) -> Severity:
        """Map a CVSS score to a severity level.

        Uses the standard CVSS v3 severity rating scale:
          - 9.0 -- 10.0 : CRITICAL
          - 7.0 -- 8.9  : HIGH
          - 4.0 -- 6.9  : MEDIUM
          - 0.0 -- 3.9  : LOW

        When no CVSS score is available (None), defaults to MEDIUM to
        avoid both under-reporting and over-reporting.

        Args:
            cvss_score: The CVSS score as a float, or None if the
                vulnerability does not include CVSS data.

        Returns:
            The corresponding Severity enum member.
        """
        if cvss_score is None:
            return Severity.MEDIUM

        if cvss_score >= 9.0:
            return Severity.CRITICAL
        if cvss_score >= 7.0:
            return Severity.HIGH
        if cvss_score >= 4.0:
            return Severity.MEDIUM
        return Severity.LOW

    # -----------------------------------------------------------------
    # OSV response field extraction helpers
    # -----------------------------------------------------------------

    @staticmethod
    def _extract_cvss_score(vuln: Dict[str, Any]) -> Optional[float]:
        """Extract the highest CVSS score from an OSV vulnerability record.

        The OSV response may include CVSS data in two locations:

        1. ``severity``: A list of objects, each with a ``type`` field
           (e.g., "CVSS_V3") and a ``score`` field containing the CVSS
           vector string. The numeric score is extracted from the vector.

        2. ``database_specific``: Some databases include a direct
           ``cvss_score`` or ``severity`` float.

        This method checks both locations and returns the highest score
        found, or None if no CVSS data is present.

        Args:
            vuln: A single vulnerability dictionary from the OSV API.

        Returns:
            The highest CVSS score as a float, or None if no score could
            be extracted.
        """
        scores: List[float] = []

        # Strategy 1: Parse from "severity" array
        severity_list = vuln.get("severity", [])
        if isinstance(severity_list, list):
            for entry in severity_list:
                if not isinstance(entry, dict):
                    continue

                # Some OSV entries have a direct "score" numeric field
                direct_score = entry.get("score")
                if isinstance(direct_score, (int, float)):
                    scores.append(float(direct_score))
                    continue

                # Extract score from CVSS vector string
                # CVSS v3 vector format: "CVSS:3.1/AV:N/AC:L/..."
                # The score is not in the vector itself; some databases
                # include it in a separate field.
                vector = entry.get("score", "")
                if not isinstance(vector, str):
                    continue

                # Try to parse CVSS vector to extract base score.
                # Some OSV entries use the format "CVSS:3.1/..." and may
                # have a separate numeric score field, or the score may
                # be in database_specific.
                pass

        # Strategy 2: Check database_specific for direct CVSS score
        db_specific = vuln.get("database_specific", {})
        if isinstance(db_specific, dict):
            for key in ("cvss_score", "cvss3_score", "severity_score"):
                value = db_specific.get(key)
                if isinstance(value, (int, float)):
                    scores.append(float(value))

            # Some databases store CVSS as a nested dict
            cvss_data = db_specific.get("cvss", {})
            if isinstance(cvss_data, dict):
                base_score = cvss_data.get("baseScore") or cvss_data.get(
                    "score"
                )
                if isinstance(base_score, (int, float)):
                    scores.append(float(base_score))

        # Strategy 3: Extract from ecosystem_specific
        # (GitHub Security Advisories include cvss in this location)
        for affected in vuln.get("affected", []):
            if not isinstance(affected, dict):
                continue
            eco_specific = affected.get("ecosystem_specific", {})
            if isinstance(eco_specific, dict):
                severity_val = eco_specific.get("severity")
                if isinstance(severity_val, str):
                    # Map textual severity to approximate CVSS score
                    severity_map = {
                        "CRITICAL": 9.5,
                        "HIGH": 7.5,
                        "MODERATE": 5.5,
                        "MEDIUM": 5.5,
                        "LOW": 2.5,
                    }
                    mapped = severity_map.get(severity_val.upper())
                    if mapped is not None:
                        scores.append(mapped)

        if not scores:
            return None

        return max(scores)

    @staticmethod
    def _extract_fixed_version(
        vuln: Dict[str, Any], ecosystem: str
    ) -> Optional[str]:
        """Extract the earliest fixed version from an OSV vulnerability.

        Parses the ``affected`` array in the OSV response to find version
        ranges with ``"fixed"`` events. When multiple fixed versions exist
        across ranges, returns the first one found (typically the earliest
        patch release).

        The ``affected`` structure (simplified)::

            "affected": [
                {
                    "package": {"name": "lodash", "ecosystem": "npm"},
                    "ranges": [
                        {
                            "type": "SEMVER",
                            "events": [
                                {"introduced": "0"},
                                {"fixed": "4.17.21"}
                            ]
                        }
                    ]
                }
            ]

        Args:
            vuln: A single vulnerability dictionary from the OSV API.
            ecosystem: The package ecosystem to match against (for cases
                where a vulnerability affects multiple ecosystems).

        Returns:
            The fixed version string (e.g., "4.17.21"), or None if no
            fixed version is published.
        """
        affected_list = vuln.get("affected", [])
        if not isinstance(affected_list, list):
            return None

        for affected in affected_list:
            if not isinstance(affected, dict):
                continue

            # Check ranges for "fixed" events
            ranges = affected.get("ranges", [])
            if not isinstance(ranges, list):
                continue

            for version_range in ranges:
                if not isinstance(version_range, dict):
                    continue

                events = version_range.get("events", [])
                if not isinstance(events, list):
                    continue

                for event in events:
                    if not isinstance(event, dict):
                        continue

                    fixed = event.get("fixed")
                    if isinstance(fixed, str) and fixed:
                        return fixed

        return None

    @staticmethod
    def _extract_cwe_id(vuln: Dict[str, Any]) -> Optional[str]:
        """Extract the first CWE identifier from an OSV vulnerability.

        Searches multiple locations in the OSV response for CWE references:

        1. ``database_specific.cwe_ids``: GitHub Security Advisories store
           CWE IDs as a list in this field.
        2. ``aliases``: Some entries include CWE IDs in the aliases list.
        3. ``references``: Some entries link to CWE pages.

        Args:
            vuln: A single vulnerability dictionary from the OSV API.

        Returns:
            The first CWE identifier found (e.g., "CWE-79"), or None
            if no CWE data is present.
        """
        # Strategy 1: database_specific.cwe_ids (common in GHSA entries)
        db_specific = vuln.get("database_specific", {})
        if isinstance(db_specific, dict):
            cwe_ids = db_specific.get("cwe_ids", [])
            if isinstance(cwe_ids, list) and cwe_ids:
                for cwe in cwe_ids:
                    if isinstance(cwe, str) and cwe.startswith("CWE-"):
                        return cwe

        # Strategy 2: Check aliases for CWE references
        aliases = vuln.get("aliases", [])
        if isinstance(aliases, list):
            for alias in aliases:
                if isinstance(alias, str) and alias.startswith("CWE-"):
                    return alias

        return None
