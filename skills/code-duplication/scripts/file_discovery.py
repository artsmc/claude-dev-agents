#!/usr/bin/env python3
"""
File Discovery Module for Code Duplication Analysis Skill

Handles file traversal, filtering, and discovery of source code files
for analysis. Supports .gitignore patterns, custom exclusions, and
language-based filtering.
"""

import os
from pathlib import Path
from typing import List, Set, Optional
import fnmatch

from models import Config
from utils import is_text_file, is_generated_file, get_file_language


# Standard directories to exclude by default
DEFAULT_EXCLUDE_DIRS = {
    'node_modules',
    '__pycache__',
    '.git',
    '.svn',
    '.hg',
    'venv',
    'env',
    '.env',
    'dist',
    'build',
    'target',
    'bin',
    'obj',
    '.idea',
    '.vscode',
    '__generated__',
    '.generated',
    'coverage',
    '.coverage',
    '.pytest_cache',
    '.mypy_cache',
    '.tox',
    'site-packages',
}


# File extensions for supported languages
LANGUAGE_EXTENSIONS = {
    'python': {'.py', '.pyw', '.pyi'},
    'javascript': {'.js', '.jsx', '.mjs', '.cjs'},
    'typescript': {'.ts', '.tsx'},
    'java': {'.java'},
    'go': {'.go'},
    'rust': {'.rs'},
    'cpp': {'.cpp', '.cc', '.cxx', '.c', '.h', '.hpp', '.hxx'},
    'csharp': {'.cs'},
    'ruby': {'.rb'},
    'php': {'.php'},
    'swift': {'.swift'},
    'kotlin': {'.kt', '.kts'},
    'scala': {'.scala'},
    'shell': {'.sh', '.bash', '.zsh', '.fish'},
}


def get_supported_extensions(languages: List[str]) -> Set[str]:
    """
    Get set of file extensions for specified languages.

    Args:
        languages: List of language identifiers

    Returns:
        Set of file extensions (e.g., {'.py', '.js', '.ts'})
    """
    extensions = set()
    for lang in languages:
        if lang in LANGUAGE_EXTENSIONS:
            extensions.update(LANGUAGE_EXTENSIONS[lang])
    return extensions


def should_exclude_dir(dir_name: str, exclude_patterns: List[str]) -> bool:
    """
    Check if directory should be excluded from traversal.

    Args:
        dir_name: Directory name to check
        exclude_patterns: List of glob patterns

    Returns:
        True if directory should be excluded
    """
    # Check default exclusions
    if dir_name in DEFAULT_EXCLUDE_DIRS:
        return True

    # Check if name starts with dot (hidden directories)
    if dir_name.startswith('.') and dir_name not in {'.', '..'}:
        return True

    # Check custom patterns
    for pattern in exclude_patterns:
        # Handle directory-specific patterns
        if pattern.endswith('/'):
            pattern = pattern.rstrip('/')

        # Match pattern
        if fnmatch.fnmatch(dir_name, pattern):
            return True
        if fnmatch.fnmatch(f"**/{dir_name}", pattern):
            return True
        if fnmatch.fnmatch(f"{dir_name}/**", pattern):
            return True

    return False


def should_exclude_file(file_path: Path, exclude_patterns: List[str]) -> bool:
    """
    Check if file should be excluded from analysis.

    Args:
        file_path: File path to check
        exclude_patterns: List of glob patterns

    Returns:
        True if file should be excluded
    """
    # Get relative path string
    file_str = str(file_path)
    file_name = file_path.name

    # Check custom patterns
    for pattern in exclude_patterns:
        # Direct file name match
        if fnmatch.fnmatch(file_name, pattern):
            return True

        # Full path match
        if fnmatch.fnmatch(file_str, pattern):
            return True

        # Wildcard path match
        if '**' in pattern:
            # Convert glob pattern to match
            if fnmatch.fnmatch(file_str, pattern):
                return True

    return False


def should_include_file(
    file_path: Path,
    supported_extensions: Set[str],
    include_patterns: List[str]
) -> bool:
    """
    Check if file should be included based on extension or patterns.

    Args:
        file_path: File path to check
        supported_extensions: Set of valid file extensions
        include_patterns: List of glob patterns to explicitly include

    Returns:
        True if file should be included
    """
    # Check include patterns first (highest priority)
    if include_patterns:
        file_str = str(file_path)
        file_name = file_path.name

        for pattern in include_patterns:
            if fnmatch.fnmatch(file_name, pattern):
                return True
            if fnmatch.fnmatch(file_str, pattern):
                return True

    # Check file extension
    if file_path.suffix.lower() in supported_extensions:
        return True

    return False


def discover_files(
    config: Config,
    root_path: Optional[Path] = None,
    progress_callback: Optional[callable] = None
) -> List[Path]:
    """
    Discover source code files for analysis.

    Walks directory tree, applies filtering rules, and returns list
    of files to analyze.

    Args:
        config: Configuration object with filtering rules
        root_path: Root directory to search (defaults to current directory)
        progress_callback: Optional callback function(current_file_count) for progress

    Returns:
        List of file paths to analyze

    Raises:
        PermissionError: If root path is not accessible
    """
    if root_path is None:
        root_path = Path.cwd()

    root_path = root_path.resolve()

    if not root_path.exists():
        raise FileNotFoundError(f"Root path does not exist: {root_path}")

    if not root_path.is_dir():
        raise NotADirectoryError(f"Root path is not a directory: {root_path}")

    # Get supported extensions from config
    supported_extensions = get_supported_extensions(config.languages)

    discovered_files: List[Path] = []
    files_checked = 0

    # Walk directory tree
    for dir_path, dir_names, file_names in os.walk(root_path):
        current_dir = Path(dir_path)

        # Filter out excluded directories (modifies dir_names in-place)
        dir_names[:] = [
            d for d in dir_names
            if not should_exclude_dir(d, config.exclude_patterns)
        ]

        # Process files in current directory
        for file_name in file_names:
            file_path = current_dir / file_name
            files_checked += 1

            # Progress callback
            if progress_callback and files_checked % 100 == 0:
                progress_callback(len(discovered_files))

            # Skip if file should be excluded
            if should_exclude_file(file_path, config.exclude_patterns):
                continue

            # Check if file should be included
            if not should_include_file(file_path, supported_extensions, config.include_patterns):
                continue

            # Check if text file (skip binary)
            if not is_text_file(file_path):
                continue

            # Check if generated file (skip if not explicitly included)
            if is_generated_file(file_path):
                # Only skip if not in include_patterns
                if not config.include_patterns:
                    continue
                # Check if explicitly included
                is_explicit = False
                for pattern in config.include_patterns:
                    if fnmatch.fnmatch(str(file_path), pattern):
                        is_explicit = True
                        break
                if not is_explicit:
                    continue

            # Check file size
            try:
                file_size_kb = file_path.stat().st_size / 1024
                if file_size_kb > config.max_file_size_kb:
                    continue
            except OSError:
                continue

            # File passes all filters
            discovered_files.append(file_path)

    # Final progress callback
    if progress_callback:
        progress_callback(len(discovered_files))

    return discovered_files


def discover_files_from_list(
    file_paths: List[Path],
    config: Config
) -> List[Path]:
    """
    Filter a list of files using discovery rules.

    Useful for incremental mode where git provides the file list.

    Args:
        file_paths: List of file paths to filter
        config: Configuration object with filtering rules

    Returns:
        Filtered list of file paths
    """
    supported_extensions = get_supported_extensions(config.languages)
    filtered_files: List[Path] = []

    for file_path in file_paths:
        # Skip if doesn't exist
        if not file_path.exists() or not file_path.is_file():
            continue

        # Apply same filters as discover_files
        if should_exclude_file(file_path, config.exclude_patterns):
            continue

        if not should_include_file(file_path, supported_extensions, config.include_patterns):
            continue

        if not is_text_file(file_path):
            continue

        if is_generated_file(file_path):
            if not config.include_patterns:
                continue

        try:
            file_size_kb = file_path.stat().st_size / 1024
            if file_size_kb > config.max_file_size_kb:
                continue
        except OSError:
            continue

        filtered_files.append(file_path)

    return filtered_files


def get_file_stats(files: List[Path]) -> dict:
    """
    Calculate statistics about discovered files.

    Args:
        files: List of file paths

    Returns:
        Dictionary with statistics
    """
    stats = {
        'total_files': len(files),
        'by_language': {},
        'by_extension': {},
        'total_size_bytes': 0,
    }

    for file_path in files:
        # Count by language
        lang = get_file_language(file_path)
        if lang:
            stats['by_language'][lang] = stats['by_language'].get(lang, 0) + 1

        # Count by extension
        ext = file_path.suffix.lower()
        stats['by_extension'][ext] = stats['by_extension'].get(ext, 0) + 1

        # Total size
        try:
            stats['total_size_bytes'] += file_path.stat().st_size
        except OSError:
            pass

    return stats


def discover_files_incremental(
    config: Config,
    root_path: Optional[Path] = None,
    compare_to: Optional[str] = None
) -> List[Path]:
    """
    Discover modified files using git for incremental analysis.

    Only analyzes files that have been modified according to git.
    Much faster than full discovery for large codebases.

    Args:
        config: Configuration object with filtering rules
        root_path: Root directory (defaults to current directory)
        compare_to: Git ref to compare against (e.g., 'main', 'HEAD~1')
                   If None, uses uncommitted changes

    Returns:
        List of modified file paths to analyze

    Raises:
        ImportError: If git_integration module not available
        GitError: If git operations fail
    """
    try:
        from git_integration import (
            is_git_repository,
            get_modified_files,
            GitError
        )
    except ImportError:
        raise ImportError(
            "git_integration module required for incremental mode. "
            "Ensure git_integration.py is available."
        )

    if root_path is None:
        root_path = Path.cwd()

    root_path = root_path.resolve()

    # Check if we're in a git repository
    if not is_git_repository(root_path):
        raise GitError(
            f"Incremental mode requires a git repository. "
            f"Path {root_path} is not in a git repo."
        )

    # Get modified files from git
    try:
        if compare_to:
            # Compare against specific ref
            modified_files = get_modified_files(
                root_path,
                include_staged=True,
                include_unstaged=True,
                include_untracked=False,
                compare_to=compare_to
            )
        else:
            # Use uncommitted changes
            modified_files = get_modified_files(
                root_path,
                include_staged=True,
                include_unstaged=True,
                include_untracked=config.include_patterns is not None
            )
    except GitError as e:
        raise GitError(f"Failed to get modified files: {e}")

    # Filter using standard discovery rules
    filtered_files = discover_files_from_list(modified_files, config)

    return filtered_files


# Export public API
__all__ = [
    "discover_files",
    "discover_files_from_list",
    "discover_files_incremental",
    "get_file_stats",
    "get_supported_extensions",
]
