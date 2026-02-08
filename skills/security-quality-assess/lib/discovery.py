"""File discovery for security quality assessment.

Recursively discovers source files and lockfiles within a project directory,
respecting .gitignore patterns and excluding common non-source directories.
All functions use only the Python standard library (pathlib, fnmatch, logging).

Functions:
    parse_gitignore: Read and parse .gitignore patterns from a project root.
    should_exclude: Test whether a file path matches any exclusion pattern.
    discover_source_files: Recursively find source files by extension.
    discover_lockfiles: Find dependency lockfiles at any directory depth.

Usage:
    >>> from pathlib import Path
    >>> from lib.discovery import discover_source_files, discover_lockfiles
    >>> project = Path("/home/user/my-app")
    >>> source_files = discover_source_files(project)
    >>> lockfiles = discover_lockfiles(project)

Performance notes:
    - Directory exclusion is applied during traversal (os.walk with pruning),
      not as a post-filter, so large excluded trees (node_modules, .git) are
      never entered.
    - Generators are used where practical to avoid materializing large
      intermediate lists.
"""

from __future__ import annotations

import fnmatch
import logging
import os
from pathlib import Path
from typing import Dict, Iterator, List, Optional, Set

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

#: Source file extensions eligible for security analysis.
SOURCE_EXTENSIONS: Set[str] = {".py", ".js", ".ts", ".jsx", ".tsx"}

#: Lockfile basenames mapped to a human-readable lockfile type key.
#: The key is used as the dictionary key returned by ``discover_lockfiles``.
LOCKFILE_NAMES: Dict[str, str] = {
    "package-lock.json": "npm",
    "yarn.lock": "yarn",
    "poetry.lock": "poetry",
}

#: Directories that are always excluded from recursive scanning, regardless
#: of .gitignore contents.  These names are matched against individual path
#: components (directory basenames), not full paths.
ALWAYS_EXCLUDED_DIRS: Set[str] = {
    "node_modules",
    ".git",
    "__pycache__",
    "venv",
    ".venv",
    "env",
    ".env",
    "dist",
    "build",
    ".next",
    ".nuxt",
    "vendor",
    "third_party",
}

#: File patterns that indicate test, generated, or minified code.
#: These are matched with ``fnmatch`` against the file basename.
EXCLUDED_FILE_PATTERNS: List[str] = [
    "*.test.py",
    "*.spec.js",
    "*.spec.ts",
    "*.spec.jsx",
    "*.spec.tsx",
    "*.test.js",
    "*.test.ts",
    "*.test.jsx",
    "*.test.tsx",
    "*_pb2.py",
    "*.generated.ts",
    "*.generated.js",
    "*.min.js",
    "*.bundle.js",
]

#: Directory names that indicate test directories.  Matched against individual
#: path components so that ``tests/`` at any depth is excluded.
EXCLUDED_TEST_DIRS: Set[str] = {
    "tests",
    "test",
    "__tests__",
}


# ---------------------------------------------------------------------------
# .gitignore parsing
# ---------------------------------------------------------------------------


def parse_gitignore(project_path: Path) -> List[str]:
    """Read and parse .gitignore patterns from a project root.

    Reads the ``.gitignore`` file in *project_path*, strips comments and blank
    lines, and returns the remaining patterns as a list of strings suitable for
    use with :func:`should_exclude`.

    Negation patterns (lines starting with ``!``) are intentionally dropped
    because the simple fnmatch-based matcher used by :func:`should_exclude`
    does not support negation semantics.

    Trailing whitespace is stripped from each line.  Lines consisting only of
    whitespace after stripping are ignored.

    Args:
        project_path: Absolute or relative path to the project root directory.

    Returns:
        A list of gitignore glob patterns.  Returns an empty list if the
        ``.gitignore`` file does not exist, is unreadable, or contains only
        comments and blank lines.

    Example:
        >>> patterns = parse_gitignore(Path("/home/user/my-app"))
        >>> "*.pyc" in patterns
        True
    """
    gitignore_path = project_path / ".gitignore"

    if not gitignore_path.is_file():
        logger.debug(".gitignore not found at %s", gitignore_path)
        return []

    patterns: List[str] = []
    try:
        text = gitignore_path.read_text(encoding="utf-8")
    except OSError as exc:
        logger.warning("Could not read .gitignore at %s: %s", gitignore_path, exc)
        return []

    for raw_line in text.splitlines():
        line = raw_line.rstrip()

        # Skip empty lines and comments.
        if not line or line.startswith("#"):
            continue

        # Skip negation patterns -- fnmatch cannot represent them.
        if line.startswith("!"):
            logger.debug("Skipping negation pattern: %s", line)
            continue

        # Remove trailing inline comments (rare in .gitignore but possible).
        # Note: a trailing space-hash is ambiguous; we keep it simple.

        patterns.append(line)

    logger.debug(
        "Parsed %d patterns from %s", len(patterns), gitignore_path
    )
    return patterns


# ---------------------------------------------------------------------------
# Exclusion matching
# ---------------------------------------------------------------------------


def should_exclude(
    file_path: Path,
    base_path: Path,
    patterns: List[str],
) -> bool:
    """Check whether *file_path* matches any exclusion pattern.

    The function tests the path relative to *base_path* against each pattern
    in *patterns* using ``fnmatch``.  Both the full relative path string and
    the file basename are tested so that patterns like ``*.pyc`` (basename
    match) and ``docs/*.md`` (relative path match) both work.

    Directory-targeted patterns (those ending with ``/``) are matched against
    every component of the relative path.

    Args:
        file_path: Absolute path to the file being checked.
        base_path: Project root used to compute the relative path.
        patterns: Gitignore-style glob patterns (output of
            :func:`parse_gitignore`).

    Returns:
        ``True`` if the file matches at least one exclusion pattern,
        ``False`` otherwise.

    Example:
        >>> should_exclude(
        ...     Path("/project/build/output.js"),
        ...     Path("/project"),
        ...     ["build/"],
        ... )
        True
    """
    try:
        rel_path = file_path.relative_to(base_path)
    except ValueError:
        # file_path is not under base_path -- cannot match.
        return False

    rel_str = str(rel_path)
    basename = file_path.name
    parts = rel_path.parts  # individual path components

    for pattern in patterns:
        # Directory patterns (trailing slash).
        if pattern.endswith("/"):
            dir_pat = pattern.rstrip("/")
            for part in parts:
                if fnmatch.fnmatch(part, dir_pat):
                    return True
            continue

        # Patterns containing a slash are matched against the relative path.
        if "/" in pattern:
            if fnmatch.fnmatch(rel_str, pattern):
                return True
            # Also test with ** prefix removed if present.
            continue

        # Simple patterns are matched against the basename.
        if fnmatch.fnmatch(basename, pattern):
            return True

        # Also try matching against each component (handles patterns like
        # ``__pycache__`` which target directory names).
        for part in parts:
            if fnmatch.fnmatch(part, pattern):
                return True

    return False


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _is_excluded_dir(dirname: str) -> bool:
    """Return ``True`` if *dirname* is in the always-excluded set.

    Also returns ``True`` for hidden directories (starting with ``.``) that
    are not explicitly listed, as a conservative safety measure to avoid
    scanning IDE, tool, and OS metadata directories.

    Args:
        dirname: A single directory name (not a path).

    Returns:
        ``True`` when *dirname* should be pruned from the walk.
    """
    if dirname in ALWAYS_EXCLUDED_DIRS:
        return True
    if dirname in EXCLUDED_TEST_DIRS:
        return True
    return False


def _is_excluded_file(basename: str) -> bool:
    """Return ``True`` if *basename* matches a built-in excluded file pattern.

    Checks against the ``EXCLUDED_FILE_PATTERNS`` list (test files, generated
    code, minified bundles).

    Args:
        basename: File name without directory components.

    Returns:
        ``True`` when the file should be skipped.
    """
    for pattern in EXCLUDED_FILE_PATTERNS:
        if fnmatch.fnmatch(basename, pattern):
            return True
    return False


def _walk_project(
    project_path: Path,
    gitignore_patterns: List[str],
) -> Iterator[Path]:
    """Yield every regular file under *project_path*, pruning excluded dirs.

    Uses ``os.walk`` with ``topdown=True`` so that excluded directories are
    removed from the walk *before* they are descended into.  Symlinks to
    directories are **not** followed to prevent infinite loops.

    Args:
        project_path: Root directory to walk.
        gitignore_patterns: Parsed .gitignore patterns for additional
            directory-level filtering.

    Yields:
        Absolute ``Path`` objects for each regular file found.
    """
    project_str = str(project_path)

    for dirpath_str, dirnames, filenames in os.walk(
        project_str, topdown=True, followlinks=False
    ):
        # Prune excluded directories in-place (topdown=True requirement).
        dirnames[:] = [
            d
            for d in dirnames
            if not _is_excluded_dir(d)
            and not _dir_matches_gitignore(
                Path(dirpath_str) / d, project_path, gitignore_patterns
            )
        ]

        for filename in filenames:
            yield Path(dirpath_str) / filename


def _dir_matches_gitignore(
    dir_path: Path,
    base_path: Path,
    patterns: List[str],
) -> bool:
    """Check whether a directory matches any gitignore pattern.

    Only directory-targeted patterns (ending with ``/``) and bare-name
    patterns are considered.

    Args:
        dir_path: Absolute path to the directory being checked.
        base_path: Project root for relative path computation.
        patterns: Parsed gitignore patterns.

    Returns:
        ``True`` if the directory should be excluded.
    """
    try:
        rel_path = dir_path.relative_to(base_path)
    except ValueError:
        return False

    dirname = dir_path.name
    rel_str = str(rel_path)

    for pattern in patterns:
        if pattern.endswith("/"):
            dir_pat = pattern.rstrip("/")
            if fnmatch.fnmatch(dirname, dir_pat):
                return True
            if fnmatch.fnmatch(rel_str, dir_pat):
                return True
        elif "/" not in pattern:
            # Bare name patterns can match directory names.
            if fnmatch.fnmatch(dirname, pattern):
                return True
        else:
            # Path patterns -- match relative path.
            if fnmatch.fnmatch(rel_str, pattern):
                return True
            # Also check with trailing component as directory.
            if fnmatch.fnmatch(rel_str + "/", pattern):
                return True

    return False


# ---------------------------------------------------------------------------
# Public API -- source file discovery
# ---------------------------------------------------------------------------


def discover_source_files(
    project_path: Path,
    gitignore_patterns: Optional[List[str]] = None,
) -> List[Path]:
    """Recursively discover source files eligible for security analysis.

    Scans *project_path* for files whose extension is in
    :data:`SOURCE_EXTENSIONS`.  Excludes:

    * Directories listed in :data:`ALWAYS_EXCLUDED_DIRS` and
      :data:`EXCLUDED_TEST_DIRS` (pruned during walk -- never entered).
    * Files matching :data:`EXCLUDED_FILE_PATTERNS` (test, generated,
      minified).
    * Files and directories matching *gitignore_patterns*.

    If *gitignore_patterns* is ``None``, :func:`parse_gitignore` is called
    automatically to load patterns from the project root.

    The returned list is sorted by path for deterministic ordering.

    Args:
        project_path: Absolute path to the project root directory.
        gitignore_patterns: Pre-parsed gitignore patterns.  When ``None``,
            patterns are loaded from ``project_path/.gitignore``.

    Returns:
        A sorted list of ``Path`` objects pointing to discovered source files.
        Returns an empty list if *project_path* does not exist or is not a
        directory.

    Raises:
        No exceptions are raised.  Permission errors and OS errors during
        traversal are logged and the affected subtree is silently skipped.

    Example:
        >>> files = discover_source_files(Path("/home/user/my-app"))
        >>> all(f.suffix in SOURCE_EXTENSIONS for f in files)
        True
    """
    if not project_path.is_dir():
        logger.warning(
            "Project path does not exist or is not a directory: %s",
            project_path,
        )
        return []

    if gitignore_patterns is None:
        gitignore_patterns = parse_gitignore(project_path)

    discovered: List[Path] = []
    file_count = 0

    try:
        for file_path in _walk_project(project_path, gitignore_patterns):
            file_count += 1

            # Log progress periodically for large projects.
            if file_count % 5000 == 0:
                logger.info("File discovery: scanned %d files so far...", file_count)

            # Extension filter.
            if file_path.suffix not in SOURCE_EXTENSIONS:
                continue

            # Built-in file exclusion (test, generated, minified).
            if _is_excluded_file(file_path.name):
                continue

            # Gitignore pattern exclusion.
            if should_exclude(file_path, project_path, gitignore_patterns):
                continue

            discovered.append(file_path)

    except OSError as exc:
        logger.warning(
            "OS error during file discovery in %s: %s", project_path, exc
        )

    discovered.sort()

    logger.info(
        "Discovered %d source files out of %d total files in %s",
        len(discovered),
        file_count,
        project_path,
    )

    return discovered


# ---------------------------------------------------------------------------
# Public API -- lockfile discovery
# ---------------------------------------------------------------------------


def discover_lockfiles(project_path: Path) -> Dict[str, Path]:
    """Find dependency lockfiles at any depth within the project.

    Searches *project_path* recursively for files whose basename matches a
    key in :data:`LOCKFILE_NAMES`.  The same directory exclusion rules as
    :func:`discover_source_files` are applied so that lockfiles inside
    ``node_modules/``, ``.git/``, or other excluded trees are not returned.

    When multiple lockfiles of the same type exist (e.g., two
    ``package-lock.json`` files at different depths), the **shallowest** one
    (fewest path components from the project root) is preferred, as it is
    most likely the project-level lockfile.

    Args:
        project_path: Absolute path to the project root directory.

    Returns:
        A dictionary mapping lockfile type names (``"npm"``, ``"yarn"``,
        ``"poetry"``) to the ``Path`` of the discovered lockfile.  Only types
        that were actually found are included; the dictionary may be empty.

    Example:
        >>> lockfiles = discover_lockfiles(Path("/home/user/my-app"))
        >>> lockfiles.get("npm")
        PosixPath('/home/user/my-app/package-lock.json')
    """
    if not project_path.is_dir():
        logger.warning(
            "Project path does not exist or is not a directory: %s",
            project_path,
        )
        return {}

    # Use a lightweight walk with gitignore patterns for consistency.
    gitignore_patterns = parse_gitignore(project_path)
    lockfiles: Dict[str, Path] = {}
    # Track depth of found lockfiles to prefer shallowest.
    lockfile_depths: Dict[str, int] = {}

    try:
        for file_path in _walk_project(project_path, gitignore_patterns):
            basename = file_path.name
            if basename not in LOCKFILE_NAMES:
                continue

            lockfile_type = LOCKFILE_NAMES[basename]

            try:
                depth = len(file_path.relative_to(project_path).parts)
            except ValueError:
                depth = 999

            # Keep the shallowest lockfile of each type.
            if lockfile_type not in lockfiles or depth < lockfile_depths[lockfile_type]:
                lockfiles[lockfile_type] = file_path
                lockfile_depths[lockfile_type] = depth
                logger.debug(
                    "Found %s lockfile at depth %d: %s",
                    lockfile_type,
                    depth,
                    file_path,
                )

    except OSError as exc:
        logger.warning(
            "OS error during lockfile discovery in %s: %s", project_path, exc
        )

    logger.info(
        "Discovered %d lockfile(s) in %s: %s",
        len(lockfiles),
        project_path,
        ", ".join(f"{k}={v}" for k, v in lockfiles.items()) or "(none)",
    )

    return lockfiles
