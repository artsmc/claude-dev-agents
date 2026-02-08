"""Dependency lockfile parser for security vulnerability scanning.

Parses common lockfile formats (package-lock.json, yarn.lock, poetry.lock)
to extract dependency names, versions, and ecosystems. This information feeds
into the vulnerability scanner which cross-references dependencies against
known CVE databases.

Supported lockfile formats:
    - **package-lock.json** (npm v2 and v3 schemas)
    - **yarn.lock** (Yarn v1 classic format)
    - **poetry.lock** (Poetry TOML-like format)

This module uses only the Python standard library (json, re, pathlib) and has
no external dependencies.

Data structures:
    Dependency: A single third-party package with name, version, and ecosystem.

Classes:
    DependencyParser: Stateless parser that reads lockfiles and returns
        structured dependency lists.

References:
    - TR.md Section 3.3: DependencyParser
    - OWASP A06:2021 Vulnerable and Outdated Components
    - CWE-1035: Using Components with Known Vulnerabilities
"""

import json
import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import List

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------


@dataclass
class Dependency:
    """A third-party dependency extracted from a lockfile.

    Represents a single package pinned to a specific version, as recorded
    in a dependency lockfile. Used by the vulnerability analyzer to check
    against known CVE databases for affected versions.

    Attributes:
        name: The package name as it appears in the registry
            (e.g., "lodash", "@babel/core", "requests").
        version: The exact pinned version string from the lockfile
            (e.g., "4.17.21", "2.25.0"). This is always a concrete version,
            not a version range.
        ecosystem: The package registry ecosystem. One of "npm" (for
            JavaScript packages from npmjs.com) or "PyPI" (for Python
            packages from pypi.org).
    """

    name: str
    version: str
    ecosystem: str  # "npm", "PyPI"


# ---------------------------------------------------------------------------
# Regex patterns for lockfile parsing
# ---------------------------------------------------------------------------

# Matches a yarn.lock dependency header line.
# Captures the package name (including optional @scope) from entries like:
#   lodash@^4.17.15:
#   "@babel/core@^7.0.0":
#   "@types/node@>=12", "@types/node@^14.0.0":
_YARN_HEADER_PATTERN = re.compile(
    r'^"?(@?[a-zA-Z0-9][\w./-]*)@',
)

# Matches the version line inside a yarn.lock entry.
# Captures the version string from:
#   version "4.17.21"
_YARN_VERSION_PATTERN = re.compile(
    r'^\s+version\s+"([^"]+)"',
)


# ---------------------------------------------------------------------------
# Parser class
# ---------------------------------------------------------------------------


class DependencyParser:
    """Parse dependency lockfiles to extract package information.

    A stateless parser that reads lockfiles from disk and returns lists of
    :class:`Dependency` objects. Each parse method handles a specific lockfile
    format and returns an empty list if the file is missing, unreadable, or
    contains invalid data.

    All parse errors are logged as warnings rather than raised, because a
    corrupted lockfile should not prevent the rest of the security assessment
    from running.

    Usage::

        parser = DependencyParser()
        npm_deps = parser.parse_package_lock(Path("package-lock.json"))
        yarn_deps = parser.parse_yarn_lock(Path("yarn.lock"))
        py_deps = parser.parse_poetry_lock(Path("poetry.lock"))
    """

    def parse_package_lock(self, path: Path) -> List[Dependency]:
        """Parse an npm package-lock.json file.

        Supports both npm v3 (``packages`` key with ``node_modules/`` prefixed
        paths) and npm v2 (``dependencies`` key with flat package names)
        lockfile schemas. When both keys are present (npm v3 files include
        a ``dependencies`` key for backwards compatibility), the ``packages``
        key takes priority as it is the canonical format.

        Args:
            path: Filesystem path to the package-lock.json file.

        Returns:
            A list of :class:`Dependency` objects with ``ecosystem="npm"``.
            Returns an empty list if the file is missing, unreadable, or
            contains invalid JSON.

        Note:
            The root package entry (key ``""`` in the ``packages`` dict) is
            skipped because it represents the project itself, not a
            third-party dependency.
        """
        data = self._read_json(path)
        if data is None:
            return []

        # npm v3 schema: "packages" dict with "node_modules/<name>" keys
        packages = data.get("packages")
        if isinstance(packages, dict):
            return self._parse_npm_v3_packages(packages)

        # npm v2 schema: "dependencies" dict with package name keys
        dependencies = data.get("dependencies")
        if isinstance(dependencies, dict):
            return self._parse_npm_v2_dependencies(dependencies)

        logger.warning(
            "package-lock.json at %s has no 'packages' or 'dependencies' key",
            path,
        )
        return []

    def parse_yarn_lock(self, path: Path) -> List[Dependency]:
        """Parse a Yarn v1 yarn.lock file.

        Yarn.lock uses a custom non-JSON, non-YAML format where each entry
        begins with a header line containing the package name and version
        range, followed by indented fields including the resolved version.

        Example format::

            lodash@^4.17.15:
              version "4.17.21"
              resolved "https://registry.yarnpkg.com/lodash/-/lodash-4.17.21.tgz"

        Scoped packages are also supported::

            "@babel/core@^7.0.0":
              version "7.16.0"

        Args:
            path: Filesystem path to the yarn.lock file.

        Returns:
            A list of :class:`Dependency` objects with ``ecosystem="npm"``.
            Returns an empty list if the file is missing, unreadable, or
            cannot be parsed.

        Note:
            When a package appears under multiple version ranges in
            yarn.lock (e.g., ``lodash@^4.0.0, lodash@^4.17.0``), it is
            deduplicated by (name, version) pairs so each resolved version
            appears only once.
        """
        content = self._read_text(path)
        if content is None:
            return []

        dependencies: List[Dependency] = []
        seen: set[tuple[str, str]] = set()
        current_name: str | None = None

        for line in content.splitlines():
            # Skip comments and blank lines
            if not line or line.startswith("#"):
                current_name = None
                continue

            # Check for a header line (not indented)
            if not line[0].isspace():
                header_match = _YARN_HEADER_PATTERN.match(line)
                if header_match:
                    current_name = header_match.group(1)
                else:
                    current_name = None
                continue

            # Check for version line (indented, under a header)
            if current_name is not None:
                version_match = _YARN_VERSION_PATTERN.match(line)
                if version_match:
                    version = version_match.group(1)
                    key = (current_name, version)
                    if key not in seen:
                        seen.add(key)
                        dependencies.append(
                            Dependency(
                                name=current_name,
                                version=version,
                                ecosystem="npm",
                            )
                        )
                    current_name = None

        if not dependencies:
            logger.debug("No dependencies found in yarn.lock at %s", path)

        return dependencies

    def parse_poetry_lock(self, path: Path) -> List[Dependency]:
        """Parse a Poetry poetry.lock file.

        Poetry.lock uses TOML format, but this parser performs simple
        line-by-line extraction to avoid requiring an external TOML library.
        It looks for ``[[package]]`` section headers followed by ``name``
        and ``version`` key-value pairs.

        Example format::

            [[package]]
            name = "requests"
            version = "2.25.0"
            description = "Python HTTP library"

            [[package]]
            name = "urllib3"
            version = "1.26.7"

        Args:
            path: Filesystem path to the poetry.lock file.

        Returns:
            A list of :class:`Dependency` objects with ``ecosystem="PyPI"``.
            Returns an empty list if the file is missing, unreadable, or
            contains no package sections.
        """
        content = self._read_text(path)
        if content is None:
            return []

        dependencies: List[Dependency] = []
        current_name: str | None = None
        current_version: str | None = None
        in_package_section = False

        for line in content.splitlines():
            stripped = line.strip()

            # Detect start of a new [[package]] section
            if stripped == "[[package]]":
                # Flush the previous package if complete
                self._flush_poetry_package(
                    current_name, current_version, dependencies
                )
                current_name = None
                current_version = None
                in_package_section = True
                continue

            # Detect start of any other section (e.g., [[package.extras]])
            if stripped.startswith("[[") or stripped.startswith("["):
                # Flush any pending package before leaving the section
                if in_package_section:
                    self._flush_poetry_package(
                        current_name, current_version, dependencies
                    )
                    current_name = None
                    current_version = None
                in_package_section = stripped == "[[package]]"
                continue

            if not in_package_section:
                continue

            # Extract name = "value"
            if stripped.startswith("name"):
                value = self._extract_toml_string(stripped)
                if value is not None:
                    current_name = value

            # Extract version = "value"
            elif stripped.startswith("version"):
                value = self._extract_toml_string(stripped)
                if value is not None:
                    current_version = value

        # Flush the last package
        self._flush_poetry_package(current_name, current_version, dependencies)

        if not dependencies:
            logger.debug("No dependencies found in poetry.lock at %s", path)

        return dependencies

    # -------------------------------------------------------------------
    # Internal helpers
    # -------------------------------------------------------------------

    def _read_json(self, path: Path) -> dict | None:
        """Read and parse a JSON file, returning None on any error.

        Args:
            path: Filesystem path to the JSON file.

        Returns:
            The parsed JSON object as a dict, or None if the file cannot
            be read or contains invalid JSON.
        """
        try:
            text = path.read_text(encoding="utf-8")
        except FileNotFoundError:
            logger.debug("Lockfile not found: %s", path)
            return None
        except OSError as exc:
            logger.warning("Could not read lockfile %s: %s", path, exc)
            return None

        try:
            data = json.loads(text)
        except json.JSONDecodeError as exc:
            logger.warning("Invalid JSON in %s: %s", path, exc)
            return None

        if not isinstance(data, dict):
            logger.warning("Expected JSON object in %s, got %s", path, type(data).__name__)
            return None

        return data

    def _read_text(self, path: Path) -> str | None:
        """Read a text file, returning None on any error.

        Args:
            path: Filesystem path to the text file.

        Returns:
            The file contents as a string, or None if the file cannot
            be read.
        """
        try:
            return path.read_text(encoding="utf-8")
        except FileNotFoundError:
            logger.debug("Lockfile not found: %s", path)
            return None
        except OSError as exc:
            logger.warning("Could not read lockfile %s: %s", path, exc)
            return None

    def _parse_npm_v3_packages(self, packages: dict) -> List[Dependency]:
        """Extract dependencies from npm v3 'packages' dict.

        Args:
            packages: The ``packages`` dictionary from package-lock.json
                where keys are ``node_modules/<name>`` paths and values
                are objects containing at least a ``version`` field.

        Returns:
            A list of :class:`Dependency` objects for all entries that
            have a valid name and version.
        """
        dependencies: List[Dependency] = []

        for pkg_path, pkg_info in packages.items():
            # Skip the root package (empty key)
            if not pkg_path:
                continue

            if not isinstance(pkg_info, dict):
                continue

            version = pkg_info.get("version")
            if not isinstance(version, str) or not version:
                continue

            # Extract the package name from the path.
            # Handles nested node_modules (e.g., "node_modules/a/node_modules/b")
            # and scoped packages (e.g., "node_modules/@scope/pkg").
            name = self._extract_npm_package_name(pkg_path)
            if not name:
                continue

            dependencies.append(
                Dependency(name=name, version=version, ecosystem="npm")
            )

        return dependencies

    def _parse_npm_v2_dependencies(self, dependencies_dict: dict) -> List[Dependency]:
        """Extract dependencies from npm v2 'dependencies' dict.

        Args:
            dependencies_dict: The ``dependencies`` dictionary from
                package-lock.json where keys are package names and values
                are objects containing at least a ``version`` field.

        Returns:
            A list of :class:`Dependency` objects for all entries that
            have a valid version string.
        """
        dependencies: List[Dependency] = []

        for name, dep_info in dependencies_dict.items():
            if not isinstance(dep_info, dict):
                continue

            version = dep_info.get("version")
            if not isinstance(version, str) or not version:
                continue

            if not name:
                continue

            dependencies.append(
                Dependency(name=name, version=version, ecosystem="npm")
            )

            # npm v2 can have nested dependencies
            nested = dep_info.get("dependencies")
            if isinstance(nested, dict):
                dependencies.extend(self._parse_npm_v2_dependencies(nested))

        return dependencies

    @staticmethod
    def _extract_npm_package_name(pkg_path: str) -> str:
        """Extract the package name from an npm v3 node_modules path.

        Handles both regular and scoped packages, as well as nested
        node_modules directories.

        Args:
            pkg_path: A key from the npm v3 ``packages`` dict, e.g.,
                ``"node_modules/lodash"`` or
                ``"node_modules/@babel/core"`` or
                ``"node_modules/a/node_modules/@scope/b"``.

        Returns:
            The package name (e.g., ``"lodash"``, ``"@babel/core"``),
            or an empty string if the path cannot be parsed.
        """
        # Find the last "node_modules/" segment to handle nested deps
        prefix = "node_modules/"
        idx = pkg_path.rfind(prefix)
        if idx == -1:
            return ""

        remainder = pkg_path[idx + len(prefix):]
        if not remainder:
            return ""

        # Scoped packages: @scope/name
        if remainder.startswith("@"):
            # Need at least @scope/name
            parts = remainder.split("/", 2)
            if len(parts) >= 2:
                return f"{parts[0]}/{parts[1]}"
            return ""

        # Regular packages: just the name (first path segment)
        return remainder.split("/", 1)[0]

    @staticmethod
    def _extract_toml_string(line: str) -> str | None:
        """Extract a quoted string value from a TOML-like key = "value" line.

        Args:
            line: A stripped line from a TOML file, e.g.,
                ``'name = "requests"'``.

        Returns:
            The unquoted string value, or None if the line does not
            contain a valid quoted string value.
        """
        # Split on '=' and take the value part
        parts = line.split("=", 1)
        if len(parts) != 2:
            return None

        value = parts[1].strip()

        # Remove surrounding quotes (double or single)
        if len(value) >= 2:
            if (value[0] == '"' and value[-1] == '"') or (
                value[0] == "'" and value[-1] == "'"
            ):
                return value[1:-1]

        return None

    @staticmethod
    def _flush_poetry_package(
        name: str | None,
        version: str | None,
        dependencies: List[Dependency],
    ) -> None:
        """Append a poetry package to the dependencies list if complete.

        Args:
            name: The package name, or None if not yet parsed.
            version: The package version, or None if not yet parsed.
            dependencies: The list to append to (modified in place).
        """
        if name and version:
            dependencies.append(
                Dependency(name=name, version=version, ecosystem="PyPI")
            )
