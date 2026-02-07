#!/usr/bin/env python3
"""
Git Integration for Code Duplication Analysis Skill

Provides git integration for incremental analysis mode, allowing
analysis of only modified files instead of the entire codebase.
"""

import subprocess
from pathlib import Path
from typing import List, Optional, Set
import re


class GitError(Exception):
    """Raised when git operations fail."""
    pass


def is_git_repository(path: Path) -> bool:
    """
    Check if path is within a git repository.

    Args:
        path: Directory to check

    Returns:
        True if path is in a git repository
    """
    try:
        result = subprocess.run(
            ['git', 'rev-parse', '--git-dir'],
            cwd=path,
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def get_git_root(path: Path) -> Optional[Path]:
    """
    Get the root directory of the git repository.

    Args:
        path: Any path within the repository

    Returns:
        Path to repository root, or None if not in a git repo
    """
    try:
        result = subprocess.run(
            ['git', 'rev-parse', '--show-toplevel'],
            cwd=path,
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            return Path(result.stdout.strip())
        return None
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return None


def get_current_branch(repo_path: Path) -> Optional[str]:
    """
    Get the name of the current git branch.

    Args:
        repo_path: Path to git repository

    Returns:
        Branch name or None if detached HEAD
    """
    try:
        result = subprocess.run(
            ['git', 'branch', '--show-current'],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            branch = result.stdout.strip()
            return branch if branch else None
        return None
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return None


def get_current_commit(repo_path: Path) -> Optional[str]:
    """
    Get the current commit hash.

    Args:
        repo_path: Path to git repository

    Returns:
        Commit hash (short) or None
    """
    try:
        result = subprocess.run(
            ['git', 'rev-parse', '--short', 'HEAD'],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            return result.stdout.strip()
        return None
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return None


def get_modified_files(
    repo_path: Path,
    include_staged: bool = True,
    include_unstaged: bool = True,
    include_untracked: bool = False,
    compare_to: Optional[str] = None
) -> List[Path]:
    """
    Get list of modified files in git repository.

    Args:
        repo_path: Path to git repository
        include_staged: Include staged changes
        include_unstaged: Include unstaged changes
        include_untracked: Include untracked files
        compare_to: Compare to specific commit/branch (e.g., 'main', 'HEAD~1')

    Returns:
        List of modified file paths (absolute)

    Raises:
        GitError: If git command fails
    """
    modified_files: Set[Path] = set()
    git_root = get_git_root(repo_path)

    if not git_root:
        raise GitError(f"Not a git repository: {repo_path}")

    try:
        # Get files from diff
        if compare_to:
            # Compare to specific ref
            result = subprocess.run(
                ['git', 'diff', '--name-only', compare_to],
                cwd=git_root,
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if line:
                        file_path = git_root / line
                        if file_path.exists():
                            modified_files.add(file_path)
        else:
            # Get staged changes
            if include_staged:
                result = subprocess.run(
                    ['git', 'diff', '--cached', '--name-only'],
                    cwd=git_root,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                if result.returncode == 0:
                    for line in result.stdout.strip().split('\n'):
                        if line:
                            file_path = git_root / line
                            if file_path.exists():
                                modified_files.add(file_path)

            # Get unstaged changes
            if include_unstaged:
                result = subprocess.run(
                    ['git', 'diff', '--name-only'],
                    cwd=git_root,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                if result.returncode == 0:
                    for line in result.stdout.strip().split('\n'):
                        if line:
                            file_path = git_root / line
                            if file_path.exists():
                                modified_files.add(file_path)

            # Get untracked files
            if include_untracked:
                result = subprocess.run(
                    ['git', 'ls-files', '--others', '--exclude-standard'],
                    cwd=git_root,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                if result.returncode == 0:
                    for line in result.stdout.strip().split('\n'):
                        if line:
                            file_path = git_root / line
                            if file_path.exists():
                                modified_files.add(file_path)

    except subprocess.TimeoutExpired:
        raise GitError("Git command timed out")
    except FileNotFoundError:
        raise GitError("Git not found - is git installed?")
    except Exception as e:
        raise GitError(f"Git command failed: {e}")

    return sorted(modified_files)


def get_files_in_commit(repo_path: Path, commit: str = 'HEAD') -> List[Path]:
    """
    Get list of files changed in a specific commit.

    Args:
        repo_path: Path to git repository
        commit: Commit ref (default: HEAD)

    Returns:
        List of file paths changed in the commit

    Raises:
        GitError: If git command fails
    """
    git_root = get_git_root(repo_path)

    if not git_root:
        raise GitError(f"Not a git repository: {repo_path}")

    try:
        result = subprocess.run(
            ['git', 'diff-tree', '--no-commit-id', '--name-only', '-r', commit],
            cwd=git_root,
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode != 0:
            raise GitError(f"Failed to get files from commit {commit}")

        files = []
        for line in result.stdout.strip().split('\n'):
            if line:
                file_path = git_root / line
                if file_path.exists():
                    files.append(file_path)

        return files

    except subprocess.TimeoutExpired:
        raise GitError("Git command timed out")
    except FileNotFoundError:
        raise GitError("Git not found")
    except Exception as e:
        raise GitError(f"Git command failed: {e}")


def get_files_changed_since(
    repo_path: Path,
    since_commit: str,
    until_commit: str = 'HEAD'
) -> List[Path]:
    """
    Get all files changed between two commits.

    Args:
        repo_path: Path to git repository
        since_commit: Start commit (exclusive)
        until_commit: End commit (inclusive, default: HEAD)

    Returns:
        List of changed files

    Raises:
        GitError: If git command fails
    """
    git_root = get_git_root(repo_path)

    if not git_root:
        raise GitError(f"Not a git repository: {repo_path}")

    try:
        result = subprocess.run(
            ['git', 'diff', '--name-only', f"{since_commit}..{until_commit}"],
            cwd=git_root,
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode != 0:
            raise GitError(f"Failed to get diff {since_commit}..{until_commit}")

        files = []
        for line in result.stdout.strip().split('\n'):
            if line:
                file_path = git_root / line
                if file_path.exists():
                    files.append(file_path)

        return files

    except subprocess.TimeoutExpired:
        raise GitError("Git command timed out")
    except FileNotFoundError:
        raise GitError("Git not found")
    except Exception as e:
        raise GitError(f"Git command failed: {e}")


def has_uncommitted_changes(repo_path: Path) -> bool:
    """
    Check if repository has uncommitted changes.

    Args:
        repo_path: Path to git repository

    Returns:
        True if there are uncommitted changes
    """
    try:
        # Check for staged or unstaged changes
        result = subprocess.run(
            ['git', 'status', '--porcelain'],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0:
            return bool(result.stdout.strip())

        return False

    except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
        return False


def get_file_last_modified_commit(repo_path: Path, file_path: Path) -> Optional[str]:
    """
    Get the commit hash where file was last modified.

    Args:
        repo_path: Path to git repository
        file_path: Path to file (relative to repo root)

    Returns:
        Commit hash or None
    """
    git_root = get_git_root(repo_path)
    if not git_root:
        return None

    try:
        # Get relative path from git root
        rel_path = file_path.relative_to(git_root)

        result = subprocess.run(
            ['git', 'log', '-1', '--format=%H', '--', str(rel_path)],
            cwd=git_root,
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0:
            commit = result.stdout.strip()
            return commit if commit else None

        return None

    except (ValueError, subprocess.TimeoutExpired, FileNotFoundError, Exception):
        return None


def get_git_status_summary(repo_path: Path) -> dict:
    """
    Get summary of git repository status.

    Args:
        repo_path: Path to git repository

    Returns:
        Dictionary with status information
    """
    summary = {
        'is_git_repo': False,
        'git_root': None,
        'current_branch': None,
        'current_commit': None,
        'has_changes': False,
        'modified_count': 0,
        'staged_count': 0,
        'untracked_count': 0,
    }

    if not is_git_repository(repo_path):
        return summary

    summary['is_git_repo'] = True
    summary['git_root'] = str(get_git_root(repo_path))
    summary['current_branch'] = get_current_branch(repo_path)
    summary['current_commit'] = get_current_commit(repo_path)
    summary['has_changes'] = has_uncommitted_changes(repo_path)

    try:
        # Count modified files
        modified = get_modified_files(
            repo_path,
            include_staged=False,
            include_unstaged=True,
            include_untracked=False
        )
        summary['modified_count'] = len(modified)

        # Count staged files
        staged = get_modified_files(
            repo_path,
            include_staged=True,
            include_unstaged=False,
            include_untracked=False
        )
        summary['staged_count'] = len(staged)

        # Count untracked files
        untracked = get_modified_files(
            repo_path,
            include_staged=False,
            include_unstaged=False,
            include_untracked=True
        )
        summary['untracked_count'] = len(untracked)

    except GitError:
        pass

    return summary


# Export public API
__all__ = [
    "GitError",
    "is_git_repository",
    "get_git_root",
    "get_current_branch",
    "get_current_commit",
    "get_modified_files",
    "get_files_in_commit",
    "get_files_changed_since",
    "has_uncommitted_changes",
    "get_file_last_modified_commit",
    "get_git_status_summary",
]
