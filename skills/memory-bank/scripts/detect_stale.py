#!/usr/bin/env python3
"""
Detect stale or contradictory information in Memory Bank.

This tool:
- Identifies outdated files
- Detects contradictions between files
- Finds completed items still in progress
- Checks technical context vs actual dependencies
- Validates cross-file consistency

Returns structured JSON with stale information and recommendations.
"""

import json
import sys
import re
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Set


def get_file_age_days(file_path: Path) -> int:
    """Get age of file in days since last modification."""
    if not file_path.exists():
        return -1

    modified_time = datetime.fromtimestamp(file_path.stat().st_mtime)
    age = datetime.now() - modified_time
    return age.days


def detect_stale_files(project_path: Path) -> List[Dict]:
    """Detect files that haven't been updated recently."""
    memory_path = project_path / "memory-bank"
    stale_files = []

    # Thresholds for staleness
    thresholds = {
        "activeContext.md": 14,   # Should update every 2 weeks
        "progress.md": 14,        # Should update every 2 weeks
        "systemPatterns.md": 60,  # Review every 2 months
        "techContext.md": 60,     # Review every 2 months
        "productContext.md": 90,  # Review every 3 months
        "projectbrief.md": 90     # Review every 3 months
    }

    for file_name, threshold in thresholds.items():
        file_path = memory_path / file_name
        if file_path.exists():
            age_days = get_file_age_days(file_path)

            if age_days > threshold:
                recommendation = ""
                if file_name in ["activeContext.md", "progress.md"]:
                    recommendation = "Update current focus, recent changes, and progress"
                elif file_name in ["systemPatterns.md", "techContext.md"]:
                    recommendation = "Review for accuracy, check if patterns/tech changed"
                else:
                    recommendation = "Review for accuracy, update if project scope changed"

                stale_files.append({
                    "file": file_name,
                    "last_modified": datetime.fromtimestamp(file_path.stat().st_mtime).strftime("%Y-%m-%d"),
                    "days_old": age_days,
                    "threshold": threshold,
                    "severity": "high" if age_days > threshold * 1.5 else "medium",
                    "recommendation": recommendation
                })

    return sorted(stale_files, key=lambda x: x["days_old"], reverse=True)


def detect_tech_contradictions(project_path: Path) -> List[Dict]:
    """Detect contradictions between techContext.md and actual dependencies."""
    memory_path = project_path / "memory-bank"
    tech_context_file = memory_path / "techContext.md"
    contradictions = []

    if not tech_context_file.exists():
        return contradictions

    # Read tech context
    with open(tech_context_file, 'r', encoding='utf-8') as f:
        tech_content = f.read().lower()

    # Check package.json
    package_json = project_path / "package.json"
    if package_json.exists():
        try:
            with open(package_json, 'r', encoding='utf-8') as f:
                package_data = json.load(f)

            dependencies = package_data.get('dependencies', {})
            dev_dependencies = package_data.get('devDependencies', {})
            all_deps = {**dependencies, **dev_dependencies}

            # Common frameworks to check
            frameworks_to_check = {
                'next': 'Next.js',
                'react': 'React',
                'vue': 'Vue',
                'express': 'Express',
                'fastapi': 'FastAPI',
                'django': 'Django'
            }

            for dep_key, framework_name in frameworks_to_check.items():
                in_package = any(dep_key in dep_name.lower() for dep_name in all_deps.keys())
                in_tech_context = framework_name.lower() in tech_content

                if in_package and not in_tech_context:
                    contradictions.append({
                        "type": "missing_in_tech_context",
                        "item": framework_name,
                        "message": f"{framework_name} found in package.json but not documented in techContext.md"
                    })
                elif in_tech_context and not in_package:
                    contradictions.append({
                        "type": "outdated_in_tech_context",
                        "item": framework_name,
                        "message": f"{framework_name} mentioned in techContext.md but not found in package.json"
                    })
        except Exception as e:
            pass

    # Check requirements.txt (Python)
    requirements_txt = project_path / "requirements.txt"
    if requirements_txt.exists():
        try:
            with open(requirements_txt, 'r', encoding='utf-8') as f:
                requirements = f.read().lower()

            python_frameworks = {
                'django': 'Django',
                'flask': 'Flask',
                'fastapi': 'FastAPI'
            }

            for dep_key, framework_name in python_frameworks.items():
                in_requirements = dep_key in requirements
                in_tech_context = framework_name.lower() in tech_content

                if in_requirements and not in_tech_context:
                    contradictions.append({
                        "type": "missing_in_tech_context",
                        "item": framework_name,
                        "message": f"{framework_name} found in requirements.txt but not documented in techContext.md"
                    })
                elif in_tech_context and not in_requirements:
                    contradictions.append({
                        "type": "outdated_in_tech_context",
                        "item": framework_name,
                        "message": f"{framework_name} mentioned in techContext.md but not found in requirements.txt"
                    })
        except Exception as e:
            pass

    return contradictions


def detect_completed_in_progress(project_path: Path) -> List[str]:
    """Find items that might be completed but still marked as in-progress."""
    memory_path = project_path / "memory-bank"
    progress_file = memory_path / "progress.md"
    completed_items = []

    if not progress_file.exists():
        return completed_items

    with open(progress_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Look for common "in progress" indicators
    in_progress_patterns = [
        r'[-*]\s*\[ \]\s*(.+)',  # Unchecked checkboxes
        r'[-*]\s*(?:TODO|WIP|In Progress):\s*(.+)',  # Explicit markers
        r'##\s*(?:In Progress|Current Work|Working On)\s*\n((?:.+\n?)+?)##',  # Sections
    ]

    in_progress_items = []
    for pattern in in_progress_patterns:
        matches = re.findall(pattern, content, re.MULTILINE | re.IGNORECASE)
        in_progress_items.extend(matches)

    # Look for "done" indicators that might conflict
    done_patterns = [
        r'[-*]\s*\[x\]\s*(.+)',  # Checked checkboxes
        r'[-*]\s*(?:DONE|Completed|Finished):\s*(.+)',
    ]

    done_items = []
    for pattern in done_patterns:
        matches = re.findall(pattern, content, re.MULTILINE | re.IGNORECASE)
        done_items.extend(matches)

    # Simple check: if item appears in both, might be confusion
    for item in in_progress_items:
        item_clean = item.strip()[:50]  # First 50 chars
        for done_item in done_items:
            if item_clean in done_item or done_item in item_clean:
                completed_items.append(f"Possible conflict: '{item_clean}' marked both in-progress and done")

    return completed_items[:5]  # Limit to top 5


def detect_cross_file_inconsistencies(project_path: Path) -> List[Dict]:
    """Detect inconsistencies between memory bank files."""
    memory_path = project_path / "memory-bank"
    inconsistencies = []

    # Check if activeContext mentions features not in productContext
    active_file = memory_path / "activeContext.md"
    product_file = memory_path / "productContext.md"

    if active_file.exists() and product_file.exists():
        with open(active_file, 'r', encoding='utf-8') as f:
            active_content = f.read().lower()
        with open(product_file, 'r', encoding='utf-8') as f:
            product_content = f.read().lower()

        # Look for feature mentions in active that aren't in product
        # This is a simple heuristic
        active_features = re.findall(r'(?:feature|implement|build|add)\s+(\w+(?:\s+\w+){0,2})', active_content)
        for feature in active_features[:5]:  # Check first 5
            if feature not in product_content and len(feature) > 5:
                inconsistencies.append({
                    "type": "missing_context",
                    "message": f"activeContext mentions '{feature}' which may not be in productContext.md"
                })

    return inconsistencies


def main():
    """Main staleness detection function."""
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
            "error": "Memory bank not found. Run /memorybank initialize first."
        }))
        sys.exit(0)

    # Run detection
    stale_files = detect_stale_files(project_path)
    tech_contradictions = detect_tech_contradictions(project_path)
    completed_in_progress = detect_completed_in_progress(project_path)
    cross_file_issues = detect_cross_file_inconsistencies(project_path)

    # Calculate overall staleness score (0-1, higher is worse)
    staleness_score = 0.0
    if stale_files:
        # Weight by severity and count
        high_severity = len([f for f in stale_files if f["severity"] == "high"])
        medium_severity = len([f for f in stale_files if f["severity"] == "medium"])

        staleness_score = min((high_severity * 0.3 + medium_severity * 0.15), 1.0)

    # Generate recommendations
    recommendations = []

    if stale_files:
        for stale_file in stale_files[:3]:  # Top 3
            recommendations.append(f"Update {stale_file['file']}: {stale_file['recommendation']}")

    if tech_contradictions:
        recommendations.append("Sync techContext.md with actual dependencies in package.json/requirements.txt")

    if completed_in_progress:
        recommendations.append("Review progress.md for completed items that need moving or cleanup")

    if cross_file_issues:
        recommendations.append("Review cross-file consistency between activeContext and productContext")

    output = {
        "staleness_score": round(staleness_score, 3),
        "status": "good" if staleness_score < 0.3 else "needs_attention" if staleness_score < 0.6 else "stale",
        "stale_files": stale_files,
        "tech_contradictions": tech_contradictions,
        "completed_in_progress": completed_in_progress,
        "cross_file_inconsistencies": cross_file_issues,
        "recommendations": recommendations,
        "project_path": str(project_path),
        "memory_path": str(memory_path)
    }

    print(json.dumps(output, indent=2))
    sys.exit(0)


if __name__ == "__main__":
    main()
