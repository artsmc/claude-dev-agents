#!/usr/bin/env python3
"""
Exact Duplicate Detection for Code Duplication Analysis Skill

Provides code normalization and exact duplicate detection using
hash-based comparison. Supports multiple programming languages.
"""

import io
import tokenize
import hashlib
from typing import List, Set, Tuple, Optional
from pathlib import Path

from models import DuplicateBlock, CodeLocation, DuplicateType
from utils import normalize_line_endings


def normalize_python_code(source: str) -> str:
    """
    Normalize Python source code by removing comments and standardizing whitespace.

    Preserves structural elements (indentation, keywords, operators) while
    removing superficial differences (comments, blank lines, trailing whitespace).

    Args:
        source: Python source code to normalize

    Returns:
        Normalized Python code string

    Raises:
        ValueError: If source code has syntax errors
    """
    import re

    # Normalize line endings first
    source = normalize_line_endings(source)

    # Handle empty source
    if not source.strip():
        return ""

    try:
        # Convert source to bytes for tokenizer
        source_bytes = source.encode('utf-8')
        source_io = io.BytesIO(source_bytes)

        # Use tokenize.generate_tokens for better control
        tokens = list(tokenize.tokenize(source_io.readline))

        # Filter tokens - remove comments and encoding
        filtered_tokens = []
        for tok in tokens:
            if tok.type in (tokenize.COMMENT, tokenize.ENCODING):
                continue
            if tok.type == tokenize.NL:  # Blank newlines
                continue
            filtered_tokens.append(tok)

        # Reconstruct source using tokenize.untokenize
        # This preserves indentation automatically
        reconstructed = tokenize.untokenize(filtered_tokens)

        # untokenize returns bytes in Python 3
        if isinstance(reconstructed, bytes):
            normalized = reconstructed.decode('utf-8')
        else:
            normalized = reconstructed

        # Clean up untokenize artifacts
        normalized = normalized.lstrip('\\').strip()

        # Clean up extra newlines
        normalized = re.sub(r'\n\s*\n+', '\n', normalized)

        # Normalize whitespace around operators (but preserve indentation)
        lines = normalized.split('\n')
        normalized_lines = []

        for line in lines:
            # Get leading whitespace (indentation)
            leading_space = len(line) - len(line.lstrip())
            indent = line[:leading_space]
            code = line[leading_space:]

            # Normalize spacing in code part only
            # Multiple spaces to single space (except at line start)
            code = re.sub(r'  +', ' ', code)

            # Remove trailing whitespace
            code = code.rstrip()

            if code:  # Skip empty lines
                normalized_lines.append(indent + code)

        normalized = '\n'.join(normalized_lines)

        return normalized.strip()

    except tokenize.TokenError as e:
        raise ValueError(f"Invalid Python syntax: {e}")
    except Exception as e:
        raise ValueError(f"Failed to normalize Python code: {e}")


def normalize_javascript_code(source: str) -> str:
    """
    Normalize JavaScript/TypeScript source code.

    Removes comments and standardizes whitespace while preserving structure.
    Uses regex-based approach since JS tokenizer not in stdlib.

    Args:
        source: JavaScript/TypeScript source code

    Returns:
        Normalized code string
    """
    import re

    # Normalize line endings
    source = normalize_line_endings(source)

    # Remove single-line comments
    source = re.sub(r'//.*?$', '', source, flags=re.MULTILINE)

    # Remove multi-line comments
    source = re.sub(r'/\*.*?\*/', '', source, flags=re.DOTALL)

    # Remove blank lines
    source = re.sub(r'\n\s*\n', '\n', source)

    # Normalize whitespace (multiple spaces to single space)
    source = re.sub(r'[ \t]+', ' ', source)

    # Remove trailing whitespace from each line
    source = '\n'.join(line.rstrip() for line in source.split('\n'))

    # Normalize indentation (tabs to 4 spaces)
    source = source.replace('\t', '    ')

    return source.strip()


def compute_hash(content: str) -> str:
    """
    Compute MD5 hash of content.

    Args:
        content: String to hash

    Returns:
        Hex digest of MD5 hash
    """
    return hashlib.md5(content.encode('utf-8')).hexdigest()


def extract_code_blocks(
    file_path: Path,
    source: str,
    language: str,
    min_lines: int = 5
) -> List[Tuple[str, int, int, str]]:
    """
    Extract blocks of code from source file for duplicate detection.

    Uses sliding window approach to extract overlapping blocks.

    Args:
        file_path: Path to source file
        source: Source code content
        language: Programming language identifier
        min_lines: Minimum lines per block (default: 5)

    Returns:
        List of tuples: (block_content, start_line, end_line, normalized_hash)
    """
    # Split into lines
    lines = source.split('\n')

    # Filter out blank lines for block extraction
    non_blank_lines = []
    line_map = []  # Maps filtered line index to original line number

    for i, line in enumerate(lines, start=1):
        stripped = line.strip()
        if stripped and not stripped.startswith('#') and not stripped.startswith('//'):
            non_blank_lines.append(line)
            line_map.append(i)

    # Extract blocks using sliding window
    blocks = []

    # Window size from min_lines to total lines
    for window_size in range(min_lines, len(non_blank_lines) + 1):
        # Slide window
        for start_idx in range(len(non_blank_lines) - window_size + 1):
            end_idx = start_idx + window_size

            # Extract block
            block_lines = non_blank_lines[start_idx:end_idx]
            block_content = '\n'.join(block_lines)

            # Normalize based on language
            try:
                if language == 'python':
                    normalized = normalize_python_code(block_content)
                elif language in ('javascript', 'typescript'):
                    normalized = normalize_javascript_code(block_content)
                else:
                    # Generic normalization for other languages
                    normalized = block_content.strip()

                # Compute hash
                block_hash = compute_hash(normalized)

                # Get actual line numbers
                start_line = line_map[start_idx]
                end_line = line_map[end_idx - 1]

                blocks.append((block_content, start_line, end_line, block_hash))

            except ValueError:
                # Skip blocks that fail normalization (syntax errors)
                continue

    return blocks


def find_exact_duplicates(
    files_content: List[Tuple[Path, str, str]],
    min_lines: int = 5,
    min_chars: int = 50
) -> List[DuplicateBlock]:
    """
    Find exact duplicates across multiple files.

    Args:
        files_content: List of tuples (file_path, content, language)
        min_lines: Minimum lines to consider a duplicate
        min_chars: Minimum characters to consider a duplicate

    Returns:
        List of DuplicateBlock objects
    """
    # Extract all blocks from all files
    hash_to_blocks = {}  # hash -> list of (file, start, end, content)

    for file_path, content, language in files_content:
        blocks = extract_code_blocks(file_path, content, language, min_lines)

        for block_content, start_line, end_line, block_hash in blocks:
            # Filter by minimum characters
            if len(block_content) < min_chars:
                continue

            # Add to hash map
            if block_hash not in hash_to_blocks:
                hash_to_blocks[block_hash] = []

            hash_to_blocks[block_hash].append({
                'file': file_path,
                'start_line': start_line,
                'end_line': end_line,
                'content': block_content,
                'line_count': end_line - start_line + 1
            })

    # Find duplicates (hash appears more than once)
    duplicates = []
    duplicate_id = 1

    for block_hash, instances in hash_to_blocks.items():
        if len(instances) < 2:
            continue  # Not a duplicate

        # Create CodeLocation objects
        locations = []
        for inst in instances:
            locations.append(CodeLocation(
                file_path=inst['file'],
                start_line=inst['start_line'],
                end_line=inst['end_line'],
                line_count=inst['line_count']
            ))

        # Use first instance content as sample
        code_sample = instances[0]['content']

        # Create DuplicateBlock
        duplicate = DuplicateBlock(
            id=duplicate_id,
            type=DuplicateType.EXACT,
            hash=block_hash,
            instances=locations,
            code_sample=code_sample,
            similarity_score=1.0,  # Exact match
            suggestion=None  # Will be filled later
        )

        duplicates.append(duplicate)
        duplicate_id += 1

    # Sort by number of instances (descending)
    duplicates.sort(key=lambda d: len(d.instances), reverse=True)

    return duplicates


def filter_overlapping_duplicates(duplicates: List[DuplicateBlock]) -> List[DuplicateBlock]:
    """
    Remove overlapping duplicate blocks, keeping larger ones.

    When two duplicate blocks overlap in the same file, keep the larger block.

    Args:
        duplicates: List of duplicate blocks

    Returns:
        Filtered list with overlaps removed
    """
    # Group by file
    file_blocks = {}

    for duplicate in duplicates:
        for location in duplicate.instances:
            file_key = str(location.file_path)

            if file_key not in file_blocks:
                file_blocks[file_key] = []

            file_blocks[file_key].append({
                'duplicate': duplicate,
                'location': location
            })

    # For each file, find overlapping blocks
    blocks_to_remove = set()

    for file_key, blocks in file_blocks.items():
        # Sort by start line
        blocks.sort(key=lambda b: b['location'].start_line)

        # Check for overlaps
        for i in range(len(blocks)):
            for j in range(i + 1, len(blocks)):
                block1 = blocks[i]
                block2 = blocks[j]

                loc1 = block1['location']
                loc2 = block2['location']

                # Check if overlapping
                if (loc1.start_line <= loc2.end_line and
                    loc2.start_line <= loc1.end_line):

                    # Keep larger block
                    if loc1.line_count >= loc2.line_count:
                        blocks_to_remove.add(id(block2['duplicate']))
                    else:
                        blocks_to_remove.add(id(block1['duplicate']))

    # Filter out removed blocks
    filtered = [d for d in duplicates if id(d) not in blocks_to_remove]

    return filtered


# Export public API
__all__ = [
    'normalize_python_code',
    'normalize_javascript_code',
    'compute_hash',
    'extract_code_blocks',
    'find_exact_duplicates',
    'filter_overlapping_duplicates',
]
