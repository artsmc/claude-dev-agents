#!/usr/bin/env python3
"""
Validate Memory Bank structure and detect issues.

This tool checks:
- All 6 required files exist
- File hierarchy consistency
- Empty files
- Staleness (last modified timestamps)
- Markdown formatting
- Cross-file references

Returns structured JSON with validation results.
"""

import json
import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Tuple


def get_file_age_days(file_path: Path) -> int:
    """Get age of file in days since last modification."""
    if not file_path.exists():
        return -1

    modified_time = datetime.fromtimestamp(file_path.stat().st_mtime)
    age = datetime.now() - modified_time
    return age.days


def validate_file_structure(project_path: Path) -> Dict:
    """Check if all required memory bank files exist."""
    memory_path = project_path / "memory-bank"
    required_files = [
        "projectbrief.md",
        "productContext.md",
        "techContext.md",
        "systemPatterns.md",
        "activeContext.md",
        "progress.md"
    ]

    errors = []
    warnings = []

    if not memory_path.exists():
        errors.append("Memory bank directory 'memory-bank' not found")
        return {
            "check": "file_structure",
            "passed": False,
            "errors": errors,
            "warnings": warnings
        }

    for file_name in required_files:
        file_path = memory_path / file_name
        if not file_path.exists():
            errors.append(f"Missing required file: {file_name}")
        elif file_path.stat().st_size == 0:
            warnings.append(f"File is empty: {file_name}")

    return {
        "check": "file_structure",
        "passed": len(errors) == 0,
        "errors": errors,
        "warnings": warnings
    }


def check_staleness(project_path: Path) -> Dict:
    """Check for stale files that haven't been updated recently."""
    memory_path = project_path / "memory-bank"
    errors = []
    warnings = []

    # Dynamic files should be updated frequently
    dynamic_files = {
        "activeContext.md": 14,  # Should update within 14 days
        "progress.md": 14        # Should update within 14 days
    }

    # Static files can be older but not too old
    static_files = {
        "projectbrief.md": 90,
        "productContext.md": 90,
        "techContext.md": 60,
        "systemPatterns.md": 60
    }

    last_updated = {}

    for file_name, max_age in dynamic_files.items():
        file_path = memory_path / file_name
        if file_path.exists():
            age_days = get_file_age_days(file_path)
            last_updated[file_name] = age_days

            if age_days > max_age:
                warnings.append({
                    "file": file_name,
                    "days_old": age_days,
                    "message": f"Dynamic file not updated in {age_days} days (recommend update within {max_age} days)"
                })

    for file_name, max_age in static_files.items():
        file_path = memory_path / file_name
        if file_path.exists():
            age_days = get_file_age_days(file_path)
            last_updated[file_name] = age_days

            if age_days > max_age:
                warnings.append({
                    "file": file_name,
                    "days_old": age_days,
                    "message": f"File not updated in {age_days} days (may need review)"
                })

    return {
        "check": "staleness",
        "passed": True,  # Warnings don't fail validation
        "errors": errors,
        "warnings": warnings,
        "last_updated": last_updated
    }


def validate_hierarchy(project_path: Path) -> Dict:
    """Validate that files reference each other correctly in the hierarchy."""
    memory_path = project_path / "memory-bank"
    errors = []
    warnings = []

    # Expected references (parent → child mentions)
    expected_refs = {
        "projectbrief.md": ["productContext", "techContext", "systemPatterns"],
        "productContext.md": ["activeContext"],
        "techContext.md": ["activeContext"],
        "systemPatterns.md": ["activeContext"],
        "activeContext.md": ["progress"]
    }

    for file_name, expected_children in expected_refs.items():
        file_path = memory_path / file_name
        if not file_path.exists():
            continue

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().lower()

            # Check if children are referenced
            for child in expected_children:
                if child.lower() not in content:
                    warnings.append({
                        "file": file_name,
                        "message": f"May not reference {child} (hierarchy may be unclear)"
                    })
        except Exception as e:
            errors.append(f"Error reading {file_name}: {str(e)}")

    return {
        "check": "hierarchy",
        "passed": len(errors) == 0,
        "errors": errors,
        "warnings": warnings
    }


def check_empty_sections(project_path: Path) -> Dict:
    """Check for files with very little content."""
    memory_path = project_path / "memory-bank"
    errors = []
    warnings = []

    min_size_bytes = 100  # Files should have at least 100 bytes

    required_files = [
        "projectbrief.md",
        "productContext.md",
        "techContext.md",
        "systemPatterns.md",
        "activeContext.md",
        "progress.md"
    ]

    for file_name in required_files:
        file_path = memory_path / file_name
        if file_path.exists():
            size = file_path.stat().st_size
            if 0 < size < min_size_bytes:
                warnings.append({
                    "file": file_name,
                    "size": size,
                    "message": f"File is very small ({size} bytes) - may need more content"
                })

    return {
        "check": "empty_sections",
        "passed": True,
        "errors": errors,
        "warnings": warnings
    }


def validate_markdown_links(project_path: Path) -> Dict:
    """Validate internal markdown links."""
    memory_path = project_path / "memory-bank"
    errors = []
    warnings = []

    import re

    # Build list of all markdown files
    all_files = set()
    for file_path in memory_path.glob("*.md"):
        all_files.add(file_path.name)

    # Check links in each file
    for file_path in memory_path.glob("*.md"):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Find markdown links [text](link)
            links = re.findall(r'\[([^\]]+)\]\(([^\)]+)\)', content)

            for text, link in links:
                # Skip external links
                if link.startswith('http'):
                    continue

                # Check internal file references
                if link.endswith('.md'):
                    if link not in all_files:
                        errors.append({
                            "file": file_path.name,
                            "message": f"Broken link to: {link}"
                        })
        except Exception as e:
            warnings.append(f"Could not check links in {file_path.name}: {str(e)}")

    return {
        "check": "markdown_links",
        "passed": len(errors) == 0,
        "errors": errors,
        "warnings": warnings
    }


def main():
    """Main validation function."""
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Project path required"}))
        sys.exit(1)

    project_path = Path(sys.argv[1]).resolve()

    if not project_path.exists():
        print(json.dumps({"error": f"Project path not found: {project_path}"}))
        sys.exit(1)

    memory_path = project_path / "memory-bank"
    if not memory_path.exists():
        print(json.dumps({
            "valid": False,
            "errors": ["Memory bank not found. Run /memorybank initialize first."],
            "warnings": [],
            "checks_run": 0
        }))
        sys.exit(0)

    # Run all validation checks
    results = []
    results.append(validate_file_structure(project_path))
    results.append(check_staleness(project_path))
    results.append(validate_hierarchy(project_path))
    results.append(check_empty_sections(project_path))
    results.append(validate_markdown_links(project_path))

    # Aggregate results
    all_errors = []
    all_warnings = []
    last_updated = {}

    for result in results:
        errors = result.get('errors', [])
        warnings = result.get('warnings', [])

        # Normalize error format
        for error in errors:
            if isinstance(error, str):
                all_errors.append({"message": error})
            else:
                all_errors.append(error)

        for warning in warnings:
            if isinstance(warning, str):
                all_warnings.append({"message": warning})
            else:
                all_warnings.append(warning)

        # Collect last_updated info
        if 'last_updated' in result:
            last_updated.update(result['last_updated'])

    output = {
        "valid": len(all_errors) == 0,
        "errors": all_errors,
        "warnings": all_warnings,
        "checks_run": len(results),
        "last_updated": last_updated,
        "project_path": str(project_path),
        "memory_path": str(memory_path)
    }

    print(json.dumps(output, indent=2))
    sys.exit(0 if output["valid"] else 1)


if __name__ == "__main__":
    main()
