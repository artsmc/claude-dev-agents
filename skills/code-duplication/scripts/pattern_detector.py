#!/usr/bin/env python3
"""
Pattern Duplicate Detection for Code Duplication Analysis Skill

Detects common code patterns that appear repeatedly and suggests
refactoring into shared utilities or design patterns.
"""

import re
import ast
from typing import List, Dict, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass

from models import DuplicateBlock, CodeLocation, DuplicateType, RefactoringSuggestion, RefactoringTechnique


@dataclass
class Pattern:
    """
    Defines a code pattern to detect.

    Attributes:
        name: Pattern name (e.g., "try-catch-logging")
        description: Human-readable description
        regex_pattern: Regex pattern to match (None if AST-based)
        ast_pattern: AST pattern to match (None if regex-based)
        min_occurrences: Minimum occurrences to report (default: 3)
        refactoring_suggestion: How to refactor this pattern
        estimated_loc_reduction: Lines saved per instance refactored
    """
    name: str
    description: str
    regex_pattern: Optional[str] = None
    ast_pattern: Optional[str] = None
    min_occurrences: int = 3
    refactoring_suggestion: str = ""
    estimated_loc_reduction: int = 3


# Pattern Catalog - Common duplicated patterns
PATTERN_CATALOG = [
    Pattern(
        name="try-catch-logging",
        description="Try-catch blocks with logging",
        regex_pattern=r'try:\s+.*?\s+except\s+\w+\s+as\s+\w+:\s+.*?(?:logging|logger|log)\.',
        refactoring_suggestion="Extract into a @retry_with_logging decorator or error handling utility function",
        estimated_loc_reduction=5
    ),

    Pattern(
        name="null-check",
        description="Null/None checking pattern",
        regex_pattern=r'if\s+\w+\s+is\s+not\s+None:\s+',
        refactoring_suggestion="Use Optional type hints and early returns, or extract validation into a helper",
        estimated_loc_reduction=2
    ),

    Pattern(
        name="env-var-access",
        description="Environment variable access with default",
        regex_pattern=r'os\.getenv\(["\'][\w_]+["\']\s*,\s*["\'].*?["\']\)',
        refactoring_suggestion="Create a config class with typed environment variable accessors",
        estimated_loc_reduction=3
    ),

    Pattern(
        name="input-validation",
        description="Input validation pattern",
        regex_pattern=r'if\s+not\s+\w+:\s+raise\s+ValueError\(["\'].*?["\']\)',
        refactoring_suggestion="Create a validation decorator or use a validation library (pydantic, marshmallow)",
        estimated_loc_reduction=4
    ),

    Pattern(
        name="file-open-close",
        description="File open with explicit close",
        regex_pattern=r'(\w+)\s*=\s*open\([^)]+\).*?(?:\1\.close\(\)|finally:.*?\1\.close\(\))',
        refactoring_suggestion="Use context manager (with open() as f:) instead of explicit close",
        estimated_loc_reduction=3
    ),

    Pattern(
        name="dict-get-default",
        description="Dictionary get with default value",
        regex_pattern=r'\w+\.get\(["\'][\w_]+["\']\s*,\s*["\'].*?["\']\)',
        refactoring_suggestion="Consider using defaultdict or dataclass with default values",
        estimated_loc_reduction=1
    ),

    Pattern(
        name="list-comprehension-filter",
        description="List comprehension with filter",
        regex_pattern=r'\[\s*\w+\s+for\s+\w+\s+in\s+\w+\s+if\s+.+?\]',
        refactoring_suggestion="Extract complex list comprehensions into named functions for readability",
        estimated_loc_reduction=2
    ),

    Pattern(
        name="string-format",
        description="String formatting pattern",
        regex_pattern=r'["\'].*?%[sdf].*?["\']\s*%\s*\(',
        refactoring_suggestion="Use f-strings for cleaner string formatting",
        estimated_loc_reduction=1
    ),

    Pattern(
        name="api-error-handling",
        description="API request with status code check",
        regex_pattern=r'response\s*=\s*requests\.\w+\(.*?\).*?if\s+response\.status_code\s*[!=]=\s*200:',
        refactoring_suggestion="Create an API client wrapper with automatic error handling and retries",
        estimated_loc_reduction=6
    ),

    Pattern(
        name="database-connection",
        description="Database connection pattern",
        regex_pattern=r'connection\s*=\s*\w+\.connect\(.*?\).*?cursor\s*=\s*connection\.cursor\(\)',
        refactoring_suggestion="Use connection pooling or ORM (SQLAlchemy, Django ORM) for database access",
        estimated_loc_reduction=5
    ),

    Pattern(
        name="datetime-parsing",
        description="Date/time parsing pattern",
        regex_pattern=r'datetime\.strptime\([^)]+,\s*["\']%[YmdHMS%-]+["\']\)',
        refactoring_suggestion="Create a date utility module with common date parsing functions",
        estimated_loc_reduction=2
    ),

    Pattern(
        name="json-loads-exception",
        description="JSON parsing with exception handling",
        regex_pattern=r'try:\s+.*?json\.loads\(.*?\).*?except\s+(?:json\.)?JSONDecodeError:',
        refactoring_suggestion="Create a safe_json_loads() utility function",
        estimated_loc_reduction=4
    ),
]


def load_patterns() -> List[Pattern]:
    """
    Load pattern catalog.

    Returns:
        List of Pattern objects

    Example:
        >>> patterns = load_patterns()
        >>> len(patterns) >= 10
        True
        >>> all(p.refactoring_suggestion for p in patterns)
        True
    """
    return PATTERN_CATALOG.copy()


def match_pattern(
    source: str,
    pattern: Pattern,
    file_path: Path
) -> List[Dict]:
    """
    Match a pattern against source code.

    Args:
        source: Source code to search
        pattern: Pattern to match
        file_path: Path to source file (for reporting)

    Returns:
        List of match dictionaries with:
        - start_line: Match start line
        - end_line: Match end line
        - code: Matched code snippet
        - pattern: Pattern that matched

    Example:
        >>> source = "if not value: raise ValueError('Invalid')"
        >>> pattern = PATTERN_CATALOG[3]  # input-validation
        >>> matches = match_pattern(source, pattern, Path("test.py"))
        >>> len(matches) > 0
        True
    """
    matches = []

    if pattern.regex_pattern:
        # Regex-based matching
        lines = source.split('\n')

        # Try multiline matching
        for match in re.finditer(pattern.regex_pattern, source, re.MULTILINE | re.DOTALL):
            matched_text = match.group(0)

            # Find line numbers
            start_pos = match.start()
            end_pos = match.end()

            # Count newlines before match to get start line
            start_line = source[:start_pos].count('\n') + 1
            end_line = source[:end_pos].count('\n') + 1

            matches.append({
                'start_line': start_line,
                'end_line': end_line,
                'code': matched_text.strip(),
                'pattern': pattern
            })

    elif pattern.ast_pattern:
        # AST-based matching (future enhancement)
        # For now, skip AST patterns
        pass

    return matches


def detect_pattern_duplicates(
    files_content: List[Tuple[Path, str, str]],
    patterns: Optional[List[Pattern]] = None,
    min_occurrences: int = 3
) -> List[DuplicateBlock]:
    """
    Detect pattern duplicates across multiple files.

    Args:
        files_content: List of (file_path, content, language) tuples
        patterns: List of patterns to detect (default: load all)
        min_occurrences: Minimum occurrences to report

    Returns:
        List of DuplicateBlock objects with type=PATTERN

    Example:
        >>> files = [(Path("a.py"), "if not x: raise ValueError('msg')", "python")]
        >>> dups = detect_pattern_duplicates(files)
        >>> all(d.type == DuplicateType.PATTERN for d in dups)
        True
    """
    if patterns is None:
        patterns = load_patterns()

    # Match all patterns across all files
    pattern_matches: Dict[str, List[Dict]] = {}

    for file_path, content, language in files_content:
        if language != 'python':
            continue  # Only Python patterns for now

        for pattern in patterns:
            matches = match_pattern(content, pattern, file_path)

            if not matches:
                continue

            # Group by pattern name
            pattern_key = pattern.name
            if pattern_key not in pattern_matches:
                pattern_matches[pattern_key] = []

            # Store matches with file info
            for match in matches:
                match['file'] = file_path
                pattern_matches[pattern_key].append(match)

    # Convert to DuplicateBlock objects
    duplicates = []
    duplicate_id = 1

    for pattern_key, matches in pattern_matches.items():
        # Filter by minimum occurrences
        if len(matches) < min_occurrences:
            continue

        # Get pattern info
        pattern = next((p for p in patterns if p.name == pattern_key), None)
        if not pattern:
            continue

        # Create CodeLocation instances
        locations = []
        for match in matches:
            locations.append(CodeLocation(
                file_path=match['file'],
                start_line=match['start_line'],
                end_line=match['end_line'],
                line_count=match['end_line'] - match['start_line'] + 1
            ))

        # Use first match as code sample
        code_sample = matches[0]['code']

        # Calculate potential LOC reduction
        total_reduction = len(matches) * pattern.estimated_loc_reduction

        # Create refactoring suggestion
        suggestion = RefactoringSuggestion(
            technique=RefactoringTechnique.EXTRACT_FUNCTION,  # Most common for patterns
            description=pattern.refactoring_suggestion,
            estimated_loc_reduction=total_reduction,
            implementation_steps=[
                f"Identify all {len(matches)} instances of this pattern",
                "Extract common logic into a utility function/decorator",
                "Replace all instances with the utility call",
                "Test thoroughly to ensure behavior is preserved"
            ],
            example_code=code_sample,
            difficulty='easy' if len(matches) < 5 else 'medium'
        )

        # Create DuplicateBlock
        duplicate = DuplicateBlock(
            id=duplicate_id,
            type=DuplicateType.PATTERN,
            hash=pattern_key,  # Use pattern name as hash
            instances=locations,
            code_sample=code_sample,
            similarity_score=1.0,  # Exact pattern match
            suggestion=suggestion
        )

        duplicates.append(duplicate)
        duplicate_id += 1

    # Sort by impact (instances * estimated_loc_reduction)
    duplicates.sort(
        key=lambda d: len(d.instances) * (d.suggestion.estimated_loc_reduction if d.suggestion else 0),
        reverse=True
    )

    return duplicates


def find_all_patterns(
    files_content: List[Tuple[Path, str, str]]
) -> Dict[str, int]:
    """
    Find all pattern occurrences and count them.

    Useful for summary statistics.

    Args:
        files_content: List of (file_path, content, language) tuples

    Returns:
        Dictionary mapping pattern name to occurrence count

    Example:
        >>> files = [(Path("a.py"), "if not x: raise ValueError('msg')", "python")]
        >>> counts = find_all_patterns(files)
        >>> isinstance(counts, dict)
        True
    """
    patterns = load_patterns()
    counts = {}

    for file_path, content, language in files_content:
        if language != 'python':
            continue

        for pattern in patterns:
            matches = match_pattern(content, pattern, file_path)

            if pattern.name not in counts:
                counts[pattern.name] = 0

            counts[pattern.name] += len(matches)

    return counts


# Export public API
__all__ = [
    'Pattern',
    'load_patterns',
    'match_pattern',
    'detect_pattern_duplicates',
    'find_all_patterns',
    'PATTERN_CATALOG',
]
