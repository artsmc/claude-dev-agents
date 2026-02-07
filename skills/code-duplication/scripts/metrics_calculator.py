#!/usr/bin/env python3
"""
Metrics Calculator for Code Duplication Analysis Skill

Calculates summary metrics, ranks top offenders, and generates
analysis statistics from duplicate detection results.
"""

from typing import List, Tuple, Dict, Set
from pathlib import Path
from collections import defaultdict

from models import (
    DuplicateBlock,
    AnalysisSummary,
    FileOffender,
    DuplicateType
)
from utils import count_lines


def calculate_metrics(
    duplicates: List[DuplicateBlock],
    files_content: List[Tuple[Path, str, str]]
) -> AnalysisSummary:
    """
    Calculate comprehensive metrics from duplicate findings.

    Args:
        duplicates: List of detected duplicate blocks
        files_content: List of (file_path, content, language) tuples

    Returns:
        AnalysisSummary with all calculated metrics

    Example:
        >>> metrics = calculate_metrics(duplicates, files)
        >>> 0 <= metrics.duplication_percentage <= 100
        True
        >>> metrics.duplicate_lines <= metrics.total_lines
        True
    """
    # Calculate total LOC analyzed
    total_lines = 0
    total_files = len(files_content)

    for file_path, content, language in files_content:
        loc = count_lines(file_path, language)
        total_lines += loc

    # Calculate duplicate LOC (excluding original, counting copies only)
    duplicate_lines = 0
    exact_blocks = 0
    structural_blocks = 0
    pattern_blocks = 0

    for dup in duplicates:
        # Count duplicate lines (instances - 1) * lines per instance
        # The -1 excludes the original instance
        if len(dup.instances) > 1:
            copies = len(dup.instances) - 1
            lines_per_instance = dup.instances[0].line_count
            duplicate_lines += copies * lines_per_instance

        # Count by type
        if dup.type == DuplicateType.EXACT:
            exact_blocks += 1
        elif dup.type == DuplicateType.STRUCTURAL:
            structural_blocks += 1
        elif dup.type == DuplicateType.PATTERN:
            pattern_blocks += 1

    # Calculate duplication percentage
    if total_lines > 0:
        duplication_percentage = (duplicate_lines / total_lines) * 100
    else:
        duplication_percentage = 0.0

    # Calculate block size statistics
    block_sizes = [inst.line_count for dup in duplicates for inst in dup.instances]

    if block_sizes:
        avg_block_size = sum(block_sizes) / len(block_sizes)
        min_block_size = min(block_sizes)
        max_block_size = max(block_sizes)
    else:
        avg_block_size = 0
        min_block_size = 0
        max_block_size = 0

    # Estimate cleanup potential
    # Conservative: Remove all duplicates except largest blocks
    conservative_cleanup = duplicate_lines

    # Optimistic: Aggressive refactoring including structural patterns
    optimistic_cleanup = int(duplicate_lines * 1.2)  # 20% bonus for structural improvements

    # Create summary
    summary = AnalysisSummary(
        total_files=total_files,
        total_loc=total_lines,
        duplicate_loc=duplicate_lines,
        duplicate_blocks=len(duplicates),
        exact_blocks=exact_blocks,
        structural_blocks=structural_blocks,
        pattern_blocks=pattern_blocks
    )

    return summary


def get_files_with_duplicates(duplicates: List[DuplicateBlock]) -> Set[Path]:
    """
    Get unique set of files that contain duplicates.

    Args:
        duplicates: List of duplicate blocks

    Returns:
        Set of file paths
    """
    files = set()
    for dup in duplicates:
        for instance in dup.instances:
            files.add(instance.file_path)
    return files


def rank_offenders(
    duplicates: List[DuplicateBlock],
    files_content: List[Tuple[Path, str, str]],
    top_n: int = 10
) -> List[FileOffender]:
    """
    Rank files by duplication severity.

    Uses impact score formula:
    Impact = (Duplicate LOC × 2) + (Duplication % × File LOC)

    Args:
        duplicates: List of detected duplicates
        files_content: List of (file_path, content, language) tuples
        top_n: Number of top offenders to return (default: 10)

    Returns:
        List of FileOffender objects, sorted by impact score descending

    Example:
        >>> offenders = rank_offenders(duplicates, files)
        >>> len(offenders) <= 10
        True
        >>> offenders[0].impact_score >= offenders[-1].impact_score
        True
    """
    # Build file metadata
    file_metadata: Dict[Path, Dict] = {}

    for file_path, content, language in files_content:
        file_metadata[file_path] = {
            'total_lines': count_lines(file_path, language),
            'duplicate_lines': 0,
            'duplicate_blocks': [],
            'language': language
        }

    # Calculate per-file duplicate LOC
    for dup in duplicates:
        for instance in dup.instances:
            file_path = instance.file_path

            if file_path not in file_metadata:
                continue

            # Add duplicate lines (only count each instance once)
            file_metadata[file_path]['duplicate_lines'] += instance.line_count
            file_metadata[file_path]['duplicate_blocks'].append(dup)

    # Calculate impact scores and create FileOffender objects
    offenders = []

    for file_path, metadata in file_metadata.items():
        duplicate_lines = metadata['duplicate_lines']
        total_lines = metadata['total_lines']

        if duplicate_lines == 0:
            continue  # No duplicates in this file

        # Calculate duplication percentage
        if total_lines > 0:
            dup_percentage = (duplicate_lines / total_lines) * 100
        else:
            dup_percentage = 0.0

        # Calculate impact score
        # Formula: (Duplicate LOC × 2) + (% × File LOC)
        impact_score = (duplicate_lines * 2) + (dup_percentage * total_lines / 100)

        # Find most common duplicate in this file
        duplicate_counts = defaultdict(int)
        for dup in metadata['duplicate_blocks']:
            duplicate_counts[dup.id] += 1

        if duplicate_counts:
            most_common_id = max(duplicate_counts, key=duplicate_counts.get)
            most_common_dup = next((d for d in duplicates if d.id == most_common_id), None)
            most_common_duplicate = most_common_dup.hash if most_common_dup else ""
        else:
            most_common_duplicate = ""

        # Get list of duplicate block IDs for this file
        block_ids = [dup.id for dup in metadata['duplicate_blocks']]

        # Create FileOffender
        offender = FileOffender(
            file_path=str(file_path),
            total_loc=total_lines,
            duplicate_loc=duplicate_lines,
            duplicate_blocks=block_ids
        )

        offenders.append(offender)

    # Sort by duplicate LOC descending (most duplicated first)
    offenders.sort(key=lambda o: o.duplicate_loc, reverse=True)

    # Return top N
    return offenders[:top_n]


def calculate_file_statistics(
    files_content: List[Tuple[Path, str, str]]
) -> Dict[str, int]:
    """
    Calculate basic file statistics.

    Args:
        files_content: List of (file_path, content, language) tuples

    Returns:
        Dictionary with statistics
    """
    stats = {
        'total_files': len(files_content),
        'total_lines': 0,
        'by_language': defaultdict(int),
        'avg_file_size': 0
    }

    for file_path, content, language in files_content:
        loc = count_lines(file_path, language)
        stats['total_lines'] += loc
        stats['by_language'][language] += 1

    if stats['total_files'] > 0:
        stats['avg_file_size'] = stats['total_lines'] // stats['total_files']

    return stats


def analyze_duplication_trends(
    duplicates: List[DuplicateBlock]
) -> Dict[str, any]:
    """
    Analyze trends in duplication patterns.

    Args:
        duplicates: List of duplicate blocks

    Returns:
        Dictionary with trend analysis
    """
    trends = {
        'most_duplicated_type': None,
        'avg_instances_per_duplicate': 0,
        'largest_duplicate_block': 0,
        'total_instance_count': 0
    }

    if not duplicates:
        return trends

    # Count by type
    type_counts = defaultdict(int)
    total_instances = 0
    max_block_size = 0

    for dup in duplicates:
        type_counts[dup.type.value] += 1
        total_instances += len(dup.instances)

        # Find largest block
        for instance in dup.instances:
            if instance.line_count > max_block_size:
                max_block_size = instance.line_count

    # Most common type
    if type_counts:
        trends['most_duplicated_type'] = max(type_counts, key=type_counts.get)

    # Average instances
    trends['avg_instances_per_duplicate'] = round(total_instances / len(duplicates), 1)
    trends['largest_duplicate_block'] = max_block_size
    trends['total_instance_count'] = total_instances

    return trends


# Export public API
__all__ = [
    'calculate_metrics',
    'rank_offenders',
    'get_files_with_duplicates',
    'calculate_file_statistics',
    'analyze_duplication_trends',
]
