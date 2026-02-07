#!/usr/bin/env python3
"""
Heatmap Renderer for Code Duplication Analysis Skill

Generates hierarchical heatmap data structure showing duplication
distribution across the codebase directory tree.
"""

from typing import List, Tuple, Dict, Optional
from pathlib import Path
from collections import defaultdict

from models import DuplicateBlock, HeatmapData, HeatmapEntry
from utils import count_lines


def calculate_file_duplication_percentage(
    file_path: Path,
    duplicates: List[DuplicateBlock],
    total_lines: int
) -> float:
    """
    Calculate duplication percentage for a specific file.

    Args:
        file_path: File to calculate for
        duplicates: List of all duplicates
        total_lines: Total lines in the file

    Returns:
        Duplication percentage (0.0-100.0)
    """
    if total_lines == 0:
        return 0.0

    # Count duplicate lines in this file
    duplicate_lines = 0

    for dup in duplicates:
        for instance in dup.instances:
            if instance.file_path == file_path:
                duplicate_lines += instance.line_count

    return (duplicate_lines / total_lines) * 100


def get_duplication_symbol(percentage: float) -> str:
    """
    Get visual symbol for duplication level.

    Args:
        percentage: Duplication percentage (0-100)

    Returns:
        Symbol character (░▒▓█)
    """
    if percentage == 0:
        return ' '
    elif percentage < 10:
        return '░'  # Light
    elif percentage < 25:
        return '▒'  # Medium
    elif percentage < 50:
        return '▓'  # Dark
    else:
        return '█'  # Solid


def build_directory_tree(
    files_content: List[Tuple[Path, str, str]],
    duplicates: List[DuplicateBlock],
    max_depth: int = 5
) -> Dict[Path, List[Path]]:
    """
    Build directory tree from file paths.

    Args:
        files_content: List of (file_path, content, language) tuples
        duplicates: List of duplicate blocks
        max_depth: Maximum directory depth to traverse

    Returns:
        Dictionary mapping directory -> list of files
    """
    tree = defaultdict(list)

    for file_path, content, language in files_content:
        # Get parent directory
        parent = file_path.parent

        # Limit depth
        parts = parent.parts
        if len(parts) > max_depth:
            parent = Path(*parts[:max_depth])

        tree[parent].append(file_path)

    return tree


def generate_heatmap_data(
    files_content: List[Tuple[Path, str, str]],
    duplicates: List[DuplicateBlock]
) -> HeatmapData:
    """
    Generate heatmap data structure.

    Args:
        files_content: List of (file_path, content, language) tuples
        duplicates: List of duplicate blocks

    Returns:
        HeatmapData object with file entries

    Example:
        >>> heatmap = generate_heatmap_data(files, duplicates)
        >>> len(heatmap.entries) > 0
        True
    """
    entries = []

    for file_path, content, language in files_content:
        # Calculate totals for this file
        total_loc = count_lines(file_path, language)

        # Count duplicate LOC and blocks in this file
        duplicate_loc = 0
        block_count = 0

        for dup in duplicates:
            for instance in dup.instances:
                if instance.file_path == file_path:
                    duplicate_loc += instance.line_count
                    block_count += 1

        # Calculate percentage
        if total_loc > 0:
            dup_percentage = (duplicate_loc / total_loc) * 100
        else:
            dup_percentage = 0.0

        # Create entry
        entry = HeatmapEntry(
            file_path=file_path,
            duplication_percentage=round(dup_percentage, 2),
            duplicate_loc=duplicate_loc,
            total_loc=total_loc,
            block_count=block_count
        )

        entries.append(entry)

    # Sort by duplication percentage (highest first)
    entries.sort(key=lambda e: e.duplication_percentage, reverse=True)

    return HeatmapData(entries=entries)


def render_heatmap_text(heatmap: HeatmapData, max_width: int = 80) -> str:
    """
    Render heatmap as text for console display.

    Args:
        heatmap: HeatmapData to render
        max_width: Maximum width in characters

    Returns:
        Formatted text heatmap
    """
    lines = []

    # Add header
    lines.append("Duplication Heatmap:")
    lines.append("=" * max_width)
    lines.append("Legend: ░=Low(1-10%) ▒=Med(10-25%) ▓=High(25-50%) █=Critical(50%+)")
    lines.append("")

    # Render files
    for entry in heatmap.entries:
        symbol = get_duplication_symbol(entry.duplication_percentage)
        file_name = str(entry.file_path)
        pct = entry.duplication_percentage
        dup_loc = entry.duplicate_loc
        total_loc = entry.total_loc

        lines.append(f"{symbol} {file_name:<50} {pct:>6.1f}% ({dup_loc}/{total_loc} LOC)")

    return "\n".join(lines)


def generate_heatmap_summary(heatmap: HeatmapData) -> Dict[str, any]:
    """
    Generate summary statistics from heatmap.

    Args:
        heatmap: HeatmapData to summarize

    Returns:
        Dictionary with summary stats
    """
    summary = {
        'total_files': len(heatmap.entries),
        'avg_duplication': 0,
        'hotspots': [],  # Files with >50% duplication
        'clean_files': 0,  # Files with 0% duplication
    }

    total_dup = 0

    for entry in heatmap.entries:
        total_dup += entry.duplication_percentage

        if entry.duplication_percentage == 0:
            summary['clean_files'] += 1
        elif entry.duplication_percentage >= 50:
            summary['hotspots'].append({
                'file': entry.file_path,
                'percentage': entry.duplication_percentage
            })

    # Calculate average
    if summary['total_files'] > 0:
        summary['avg_duplication'] = total_dup / summary['total_files']

    return summary


# Export public API
__all__ = [
    'generate_heatmap_data',
    'render_heatmap_text',
    'calculate_file_duplication_percentage',
    'get_duplication_symbol',
    'build_directory_tree',
    'generate_heatmap_summary',
]
