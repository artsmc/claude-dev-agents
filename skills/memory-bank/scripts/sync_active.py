#!/usr/bin/env python3
"""
Fast synchronization of activeContext.md and progress.md.

This tool provides quick updates to the dynamic memory bank files
without requiring a full memory bank review. Use this after completing
individual tasks for fast documentation updates.

Input: JSON with completed tasks, new focus, learnings, blockers
Output: Updated files and change summary
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List


def read_file_safe(file_path: Path) -> str:
    """Safely read a file, return empty string if not exists."""
    if not file_path.exists():
        return ""

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception:
        return ""


def update_active_context(memory_path: Path, updates: Dict) -> Dict:
    """Update activeContext.md with new information."""
    active_file = memory_path / "activeContext.md"
    content = read_file_safe(active_file)

    changes = {
        "updated_focus": False,
        "added_blockers": 0,
        "added_learnings": 0
    }

    # Update current focus if provided
    if updates.get("new_focus"):
        new_focus = updates["new_focus"]

        # Look for "Current Focus" or similar section
        import re
        focus_pattern = r'(##\s*(?:Current Focus|Working On|Active Work)\s*\n)((?:.+\n?)+?)(?=##|\Z)'

        if re.search(focus_pattern, content, re.IGNORECASE):
            # Update existing section
            def replace_focus(match):
                header = match.group(1)
                return f"{header}\n{new_focus}\n\n"

            content = re.sub(focus_pattern, replace_focus, content, flags=re.IGNORECASE)
            changes["updated_focus"] = True
        else:
            # Add new section at the top (after title if exists)
            if content.startswith('#'):
                # Find end of first header
                first_line_end = content.find('\n')
                if first_line_end > 0:
                    content = (content[:first_line_end + 1] +
                             f"\n## Current Focus\n\n{new_focus}\n\n" +
                             content[first_line_end + 1:])
                    changes["updated_focus"] = True
            else:
                # No header, add at top
                content = f"# Active Context\n\n## Current Focus\n\n{new_focus}\n\n" + content
                changes["updated_focus"] = True

    # Add blockers if provided
    if updates.get("blockers") and isinstance(updates["blockers"], list):
        blockers = updates["blockers"]

        # Look for Blockers section
        blocker_pattern = r'(##\s*(?:Blockers?|Issues?)\s*\n)((?:.+\n?)+?)(?=##|\Z)'

        if re.search(blocker_pattern, content, re.IGNORECASE):
            # Add to existing section
            def add_blockers(match):
                header = match.group(1)
                existing = match.group(2)
                new_items = '\n'.join([f"- {b}" for b in blockers])
                return f"{header}{existing}\n{new_items}\n\n"

            content = re.sub(blocker_pattern, add_blockers, content, flags=re.IGNORECASE)
            changes["added_blockers"] = len(blockers)
        else:
            # Create new Blockers section
            blocker_section = "\n## Blockers\n\n" + '\n'.join([f"- {b}" for b in blockers]) + "\n\n"
            content += blocker_section
            changes["added_blockers"] = len(blockers)

    # Add learnings if provided
    if updates.get("learnings") and isinstance(updates["learnings"], list):
        learnings = updates["learnings"]

        # Look for Learnings section
        learning_pattern = r'(##\s*(?:Learnings?|Lessons Learned|Insights)\s*\n)((?:.+\n?)+?)(?=##|\Z)'

        if re.search(learning_pattern, content, re.IGNORECASE):
            # Add to existing section
            def add_learnings(match):
                header = match.group(1)
                existing = match.group(2)
                new_items = '\n'.join([f"- {l}" for l in learnings])
                return f"{header}{existing}\n{new_items}\n\n"

            content = re.sub(learning_pattern, add_learnings, content, flags=re.IGNORECASE)
            changes["added_learnings"] = len(learnings)
        else:
            # Create new Learnings section
            learning_section = "\n## Learnings\n\n" + '\n'.join([f"- {l}" for l in learnings]) + "\n\n"
            content += learning_section
            changes["added_learnings"] = len(learnings)

    # Add timestamp comment
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    content += f"\n<!-- Last synced: {timestamp} -->\n"

    # Write updated content
    with open(active_file, 'w', encoding='utf-8') as f:
        f.write(content)

    return changes


def update_progress(memory_path: Path, updates: Dict) -> Dict:
    """Update progress.md with completed items."""
    progress_file = memory_path / "progress.md"
    content = read_file_safe(progress_file)

    changes = {
        "moved_to_completed": 0,
        "added_to_working": 0
    }

    # Move completed items from active to progress
    if updates.get("completed") and isinstance(updates["completed"], list):
        completed_items = updates["completed"]

        # Look for "What's Working" or "Completed" section
        import re
        completed_pattern = r'(##\s*(?:What\'s Working|Completed|Done)\s*\n)((?:.+\n?)+?)(?=##|\Z)'

        if re.search(completed_pattern, content, re.IGNORECASE):
            # Add to existing section
            def add_completed(match):
                header = match.group(1)
                existing = match.group(2)
                timestamp = datetime.now().strftime("%Y-%m-%d")
                new_items = '\n'.join([f"- [{timestamp}] {item}" for item in completed_items])
                return f"{header}{new_items}\n{existing}\n"

            content = re.sub(completed_pattern, add_completed, content, flags=re.IGNORECASE)
            changes["moved_to_completed"] = len(completed_items)
        else:
            # Create new section
            timestamp = datetime.now().strftime("%Y-%m-%d")
            completed_section = "\n## What's Working\n\n" + '\n'.join([f"- [{timestamp}] {item}" for item in completed_items]) + "\n\n"

            # Add near the top (after first header)
            if content.startswith('#'):
                first_section = content.find('\n##')
                if first_section > 0:
                    content = content[:first_section] + completed_section + content[first_section:]
                else:
                    content += completed_section
            else:
                content = "# Progress\n\n" + completed_section + content

            changes["moved_to_completed"] = len(completed_items)

    # Add what's working if provided
    if updates.get("working") and isinstance(updates["working"], list):
        working_items = updates["working"]

        working_pattern = r'(##\s*(?:What\'s Working|Successes?)\s*\n)((?:.+\n?)+?)(?=##|\Z)'

        if re.search(working_pattern, content, re.IGNORECASE):
            def add_working(match):
                header = match.group(1)
                existing = match.group(2)
                new_items = '\n'.join([f"- {item}" for item in working_items])
                return f"{header}{new_items}\n{existing}\n"

            content = re.sub(working_pattern, add_working, content, flags=re.IGNORECASE)
            changes["added_to_working"] = len(working_items)

    # Add timestamp comment
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    content += f"\n<!-- Last synced: {timestamp} -->\n"

    # Write updated content
    with open(progress_file, 'w', encoding='utf-8') as f:
        f.write(content)

    return changes


def main():
    """Main sync function."""
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

    # Parse updates from JSON input (via stdin or file)
    updates = {}
    if len(sys.argv) >= 3:
        # JSON provided as argument
        try:
            updates = json.loads(sys.argv[2])
        except json.JSONDecodeError:
            print(json.dumps({"error": "Invalid JSON input"}))
            sys.exit(1)
    else:
        # Read from stdin
        try:
            updates = json.load(sys.stdin)
        except json.JSONDecodeError:
            print(json.dumps({"error": "Invalid JSON input from stdin"}))
            sys.exit(1)

    # Update files
    active_changes = update_active_context(memory_path, updates)
    progress_changes = update_progress(memory_path, updates)

    output = {
        "success": True,
        "updated": {
            "activeContext.md": active_changes["updated_focus"] or active_changes["added_blockers"] > 0 or active_changes["added_learnings"] > 0,
            "progress.md": progress_changes["moved_to_completed"] > 0 or progress_changes["added_to_working"] > 0
        },
        "changes": {
            "activeContext": active_changes,
            "progress": progress_changes
        },
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "memory_path": str(memory_path)
    }

    print(json.dumps(output, indent=2))
    sys.exit(0)


if __name__ == "__main__":
    main()
