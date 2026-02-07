#!/usr/bin/env python3
"""
.gitignore Pattern Parser for Code Duplication Analysis Skill

Parses .gitignore files and provides pattern matching functionality
to exclude files from analysis. Supports standard .gitignore syntax
including wildcards, negation, and directory-specific patterns.
"""

import re
from pathlib import Path
from typing import List, Set, Optional, Tuple


class GitignorePattern:
    """Represents a single .gitignore pattern."""

    def __init__(self, pattern: str, negation: bool = False, directory_only: bool = False):
        """
        Initialize gitignore pattern.

        Args:
            pattern: The pattern string (without leading !)
            negation: Whether this is a negation pattern (starts with !)
            directory_only: Whether pattern only applies to directories (ends with /)
        """
        self.original = pattern
        self.pattern = pattern
        self.negation = negation
        self.directory_only = directory_only
        self.regex = self._compile_pattern()

    def _compile_pattern(self) -> re.Pattern:
        """
        Convert gitignore pattern to regex.

        Gitignore pattern syntax:
        - * matches anything except /
        - ** matches anything including /
        - ? matches any single character except /
        - [abc] matches any character in the set
        - [!abc] matches any character not in the set
        - / at start anchors to root
        - / at end means directory only
        """
        pattern = self.pattern

        # Remove trailing / (already handled by directory_only flag)
        if pattern.endswith('/'):
            pattern = pattern[:-1]

        # Handle anchoring
        anchored = pattern.startswith('/')
        if anchored:
            pattern = pattern[1:]  # Remove leading /

        # Escape special regex characters (except wildcards)
        # Escape: . + ^ $ ( ) { } | \
        pattern = re.sub(r'([\.\+\^\$\(\)\{\}\|\\])', r'\\\1', pattern)

        # Convert gitignore wildcards to regex
        # ** matches anything including /
        pattern = pattern.replace('**/', '(.*/)?')  # Zero or more path components
        pattern = pattern.replace('/**', '(/.*)?')  # Trailing path components
        pattern = pattern.replace('**', '.*')  # Anything

        # * matches anything except /
        pattern = re.sub(r'(?<!\*)\*(?!\*)', r'[^/]*', pattern)

        # ? matches any single character except /
        pattern = pattern.replace('?', '[^/]')

        # Handle character classes [abc] and [!abc]
        pattern = re.sub(r'\[!([^\]]+)\]', r'[^\1]', pattern)

        # Build final regex
        if anchored:
            # Pattern must match from start
            regex_pattern = f'^{pattern}$'
        else:
            # Pattern can match anywhere in path
            regex_pattern = f'(^|/){pattern}$'

        return re.compile(regex_pattern)

    def matches(self, path: str, is_dir: bool = False) -> bool:
        """
        Check if path matches this pattern.

        Args:
            path: File or directory path (relative, with / separators)
            is_dir: Whether the path is a directory

        Returns:
            True if path matches the pattern
        """
        # Directory-only patterns only match directories
        if self.directory_only and not is_dir:
            return False

        # Try to match
        return self.regex.search(path) is not None

    def __repr__(self) -> str:
        prefix = '!' if self.negation else ''
        suffix = '/' if self.directory_only else ''
        return f"GitignorePattern('{prefix}{self.original}{suffix}')"


class GitignoreParser:
    """Parser for .gitignore files."""

    def __init__(self):
        """Initialize parser with no patterns."""
        self.patterns: List[GitignorePattern] = []
        self.loaded_files: Set[Path] = set()

    def parse_line(self, line: str) -> Optional[GitignorePattern]:
        """
        Parse a single line from .gitignore file.

        Args:
            line: Line from .gitignore

        Returns:
            GitignorePattern or None if line should be ignored
        """
        # Strip whitespace
        line = line.strip()

        # Skip empty lines and comments
        if not line or line.startswith('#'):
            return None

        # Check for negation
        negation = line.startswith('!')
        if negation:
            line = line[1:]

        # Check for directory-only pattern
        directory_only = line.endswith('/')

        # Skip empty pattern after removing prefix/suffix
        if not line or (directory_only and line == '/'):
            return None

        return GitignorePattern(line, negation=negation, directory_only=directory_only)

    def load_file(self, gitignore_path: Path) -> int:
        """
        Load patterns from a .gitignore file.

        Args:
            gitignore_path: Path to .gitignore file

        Returns:
            Number of patterns loaded

        Raises:
            FileNotFoundError: If file doesn't exist
            IOError: If file can't be read
        """
        if not gitignore_path.exists():
            raise FileNotFoundError(f".gitignore not found: {gitignore_path}")

        if gitignore_path in self.loaded_files:
            return 0  # Already loaded

        patterns_before = len(self.patterns)

        try:
            with open(gitignore_path, 'r', encoding='utf-8') as f:
                for line in f:
                    pattern = self.parse_line(line)
                    if pattern:
                        self.patterns.append(pattern)
        except Exception as e:
            raise IOError(f"Cannot read .gitignore file {gitignore_path}: {e}")

        self.loaded_files.add(gitignore_path)
        return len(self.patterns) - patterns_before

    def load_default_patterns(self) -> int:
        """
        Load default exclusion patterns (common files to ignore).

        Returns:
            Number of patterns added
        """
        default_patterns = [
            # Python
            '*.pyc',
            '*.pyo',
            '*.pyd',
            '__pycache__/',
            '*.egg-info/',
            '.pytest_cache/',
            '.mypy_cache/',
            '.tox/',
            'venv/',
            'env/',
            '.env/',

            # JavaScript/Node
            'node_modules/',
            'npm-debug.log',
            'yarn-error.log',
            '.npm/',
            '.yarn/',
            'dist/',
            'build/',

            # Git
            '.git/',
            '.gitignore',

            # IDEs
            '.vscode/',
            '.idea/',
            '*.swp',
            '*.swo',
            '*~',

            # OS
            '.DS_Store',
            'Thumbs.db',

            # Compiled
            '*.o',
            '*.obj',
            '*.exe',
            '*.dll',
            '*.so',
            '*.dylib',

            # Archives
            '*.zip',
            '*.tar.gz',
            '*.rar',
        ]

        patterns_before = len(self.patterns)
        for pattern_str in default_patterns:
            pattern = self.parse_line(pattern_str)
            if pattern:
                self.patterns.append(pattern)

        return len(self.patterns) - patterns_before

    def should_exclude(self, path: Path, base_path: Optional[Path] = None) -> bool:
        """
        Check if a path should be excluded based on loaded patterns.

        Args:
            path: Path to check
            base_path: Base path for relative path calculation (optional)

        Returns:
            True if path should be excluded
        """
        # Get relative path string
        if base_path:
            try:
                rel_path = path.relative_to(base_path)
            except ValueError:
                rel_path = path
        else:
            rel_path = path

        # Convert to string with forward slashes
        path_str = str(rel_path).replace('\\', '/')

        # Check if it's a directory
        is_dir = path.is_dir() if path.exists() else path_str.endswith('/')

        # Apply patterns in order (later patterns override earlier)
        excluded = False

        for pattern in self.patterns:
            if pattern.matches(path_str, is_dir):
                if pattern.negation:
                    excluded = False  # Negation un-excludes
                else:
                    excluded = True  # Normal pattern excludes

        return excluded

    def get_applicable_patterns(self, path: Path, base_path: Optional[Path] = None) -> List[GitignorePattern]:
        """
        Get all patterns that match a given path.

        Args:
            path: Path to check
            base_path: Base path for relative calculation

        Returns:
            List of matching patterns
        """
        if base_path:
            try:
                rel_path = path.relative_to(base_path)
            except ValueError:
                rel_path = path
        else:
            rel_path = path

        path_str = str(rel_path).replace('\\', '/')
        is_dir = path.is_dir() if path.exists() else path_str.endswith('/')

        matching = []
        for pattern in self.patterns:
            if pattern.matches(path_str, is_dir):
                matching.append(pattern)

        return matching


def find_gitignore_files(root_path: Path) -> List[Path]:
    """
    Find all .gitignore files in directory tree.

    Args:
        root_path: Root directory to search

    Returns:
        List of .gitignore file paths
    """
    gitignore_files = []

    for path in root_path.rglob('.gitignore'):
        if path.is_file():
            gitignore_files.append(path)

    return gitignore_files


def load_gitignore_patterns(
    root_path: Path,
    include_defaults: bool = True
) -> GitignoreParser:
    """
    Load all .gitignore files from directory tree.

    Args:
        root_path: Root directory to search
        include_defaults: Whether to include default patterns

    Returns:
        GitignoreParser with all patterns loaded
    """
    parser = GitignoreParser()

    # Load default patterns first (lowest priority)
    if include_defaults:
        parser.load_default_patterns()

    # Find and load all .gitignore files
    gitignore_files = find_gitignore_files(root_path)

    for gitignore_path in sorted(gitignore_files):
        try:
            parser.load_file(gitignore_path)
        except Exception:
            # Skip unreadable .gitignore files
            pass

    return parser


# Export public API
__all__ = [
    "GitignorePattern",
    "GitignoreParser",
    "load_gitignore_patterns",
    "find_gitignore_files",
]
