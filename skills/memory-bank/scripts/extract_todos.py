#!/usr/bin/env python3
"""
Extract action items and next steps from various sources.

This tool:
- Extracts TODO comments from code files
- Identifies uncompleted tasks from progress.md
- Finds action items in activeContext.md
- Prioritizes by urgency/importance
- Formats for memory bank updates

Returns structured JSON with actionable next steps.
"""

import json
import sys
import re
from pathlib import Path
from typing import Dict, List


def extract_code_todos(project_path: Path, patterns: List[str] = None) -> List[Dict]:
    """Extract TODO comments from code files."""
    if patterns is None:
        patterns = ['**/*.ts', '**/*.tsx', '**/*.js', '**/*.jsx', '**/*.py']

    todos = []
    seen = set()  # Avoid duplicates

    for pattern in patterns:
        for file_path in project_path.glob(pattern):
            # Skip node_modules, venv, etc.
            if any(skip in str(file_path) for skip in [
                'node_modules', '.venv', 'venv', 'dist', 'build',
                '.git', '__pycache__', '.next'
            ]):
                continue

            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Find TODO comments
                # Patterns: // TODO:, # TODO:, /* TODO: */, etc.
                todo_patterns = [
                    r'//\s*TODO:?\s*(.+)',           # JS/TS single-line
                    r'#\s*TODO:?\s*(.+)',            # Python
                    r'/\*\s*TODO:?\s*(.+?)\*/',      # JS/TS multi-line
                    r'<!--\s*TODO:?\s*(.+?)-->',     # HTML/Markdown
                ]

                for todo_pattern in todo_patterns:
                    matches = re.finditer(todo_pattern, content, re.IGNORECASE)

                    for match in matches:
                        todo_text = match.group(1).strip()

                        # Avoid duplicates and very short TODOs
                        if todo_text and len(todo_text) > 10 and todo_text not in seen:
                            seen.add(todo_text)

                            # Determine priority from keywords
                            priority = "medium"
                            if any(word in todo_text.lower() for word in ['urgent', 'critical', 'asap', 'important']):
                                priority = "high"
                            elif any(word in todo_text.lower() for word in ['nice to have', 'optional', 'future']):
                                priority = "low"

                            todos.append({
                                "task": todo_text,
                                "priority": priority,
                                "source": "code",
                                "file": str(file_path.relative_to(project_path)),
                                "context": f"TODO comment in {file_path.name}"
                            })
            except Exception:
                continue

    return todos[:20]  # Limit to top 20


def extract_progress_todos(project_path: Path) -> List[Dict]:
    """Extract uncompleted tasks from progress.md."""
    memory_path = project_path / "memory-bank"
    progress_file = memory_path / "progress.md"
    todos = []

    if not progress_file.exists():
        return todos

    try:
        with open(progress_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Find unchecked checkboxes
        unchecked_pattern = r'[-*]\s*\[ \]\s*(.+)'
        matches = re.findall(unchecked_pattern, content)

        for match in matches:
            task_text = match.strip()
            if task_text and len(task_text) > 5:
                # Determine priority
                priority = "medium"
                if any(word in task_text.lower() for word in ['urgent', 'critical', 'bug', 'fix']):
                    priority = "high"
                elif any(word in task_text.lower() for word in ['enhancement', 'refactor', 'improve']):
                    priority = "low"

                todos.append({
                    "task": task_text,
                    "priority": priority,
                    "source": "progress.md",
                    "context": "Uncompleted item in progress tracking"
                })

        # Find "TODO" or "Next" sections
        todo_section_pattern = r'##\s*(?:TODO|Next Steps?|To Do)\s*\n((?:.+\n?)+?)(?=##|\Z)'
        section_matches = re.findall(todo_section_pattern, content, re.MULTILINE | re.IGNORECASE)

        for section_content in section_matches:
            # Extract bullet points
            bullets = re.findall(r'[-*]\s*(.+)', section_content)
            for bullet in bullets:
                if bullet.strip() and len(bullet.strip()) > 5:
                    # Check if already in todos
                    if not any(bullet.strip() in t["task"] for t in todos):
                        todos.append({
                            "task": bullet.strip(),
                            "priority": "medium",
                            "source": "progress.md",
                            "context": "Listed in TODO/Next Steps section"
                        })
    except Exception:
        pass

    return todos[:15]  # Limit to top 15


def extract_active_context_todos(project_path: Path) -> List[Dict]:
    """Extract action items from activeContext.md."""
    memory_path = project_path / "memory-bank"
    active_file = memory_path / "activeContext.md"
    todos = []

    if not active_file.exists():
        return todos

    try:
        with open(active_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Find "Next Steps" or similar sections
        next_steps_pattern = r'##\s*(?:Next Steps?|Immediate Actions?|Up Next)\s*\n((?:.+\n?)+?)(?=##|\Z)'
        matches = re.findall(next_steps_pattern, content, re.MULTILINE | re.IGNORECASE)

        for section_content in matches:
            # Extract bullet points or numbered items
            items = re.findall(r'(?:[-*]|\d+\.)\s*(.+)', section_content)

            for item in items:
                if item.strip() and len(item.strip()) > 5:
                    todos.append({
                        "task": item.strip(),
                        "priority": "high",  # activeContext items are usually current priorities
                        "source": "activeContext.md",
                        "context": "Active work item"
                    })

        # Find "Blockers" or "Issues"
        blocker_pattern = r'##\s*(?:Blockers?|Issues?|Problems?)\s*\n((?:.+\n?)+?)(?=##|\Z)'
        blocker_matches = re.findall(blocker_pattern, content, re.MULTILINE | re.IGNORECASE)

        for section_content in blocker_matches:
            items = re.findall(r'(?:[-*]|\d+\.)\s*(.+)', section_content)

            for item in items:
                if item.strip() and len(item.strip()) > 5:
                    todos.append({
                        "task": f"Resolve: {item.strip()}",
                        "priority": "high",
                        "source": "activeContext.md",
                        "context": "Blocker that needs resolution"
                    })
    except Exception:
        pass

    return todos[:10]  # Limit to top 10


def merge_and_deduplicate_todos(all_todos: List[List[Dict]]) -> List[Dict]:
    """Merge todos from all sources and remove duplicates."""
    merged = []
    seen_tasks = set()

    for todo_list in all_todos:
        for todo in todo_list:
            # Normalize task for comparison
            task_normalized = todo["task"].lower().strip()

            # Check for duplicates
            is_duplicate = False
            for seen_task in seen_tasks:
                # Simple similarity check: if 80% of words overlap
                task_words = set(task_normalized.split())
                seen_words = set(seen_task.split())

                if len(task_words) > 0 and len(seen_words) > 0:
                    overlap = len(task_words & seen_words)
                    similarity = overlap / max(len(task_words), len(seen_words))

                    if similarity > 0.8:
                        is_duplicate = True
                        break

            if not is_duplicate:
                seen_tasks.add(task_normalized)
                merged.append(todo)

    return merged


def prioritize_todos(todos: List[Dict]) -> List[Dict]:
    """Sort todos by priority and source."""
    priority_order = {"high": 0, "medium": 1, "low": 2}
    source_order = {"activeContext.md": 0, "progress.md": 1, "code": 2}

    return sorted(
        todos,
        key=lambda t: (priority_order.get(t["priority"], 1), source_order.get(t["source"], 2))
    )


def main():
    """Main TODO extraction function."""
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Project path required"}))
        sys.exit(1)

    project_path = Path(sys.argv[1]).resolve()

    if not project_path.exists():
        print(json.dumps({"error": f"Project path not found: {project_path}"}))
        sys.exit(1)

    # Optional: custom file patterns
    patterns = None
    if len(sys.argv) >= 3:
        patterns = sys.argv[2].split(',')

    # Extract from all sources
    code_todos = extract_code_todos(project_path, patterns)
    progress_todos = extract_progress_todos(project_path)
    active_todos = extract_active_context_todos(project_path)

    # Merge and deduplicate
    all_todos = merge_and_deduplicate_todos([code_todos, progress_todos, active_todos])

    # Prioritize
    prioritized_todos = prioritize_todos(all_todos)

    # Separate completed items (from progress.md)
    memory_path = project_path / "memory-bank"
    progress_file = memory_path / "progress.md"
    completed = []

    if progress_file.exists():
        try:
            with open(progress_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Find checked checkboxes
            checked_pattern = r'[-*]\s*\[x\]\s*(.+)'
            matches = re.findall(checked_pattern, content, re.IGNORECASE)

            completed = [match.strip() for match in matches if match.strip()][:10]
        except Exception:
            pass

    output = {
        "total_todos": len(prioritized_todos),
        "by_priority": {
            "high": len([t for t in prioritized_todos if t["priority"] == "high"]),
            "medium": len([t for t in prioritized_todos if t["priority"] == "medium"]),
            "low": len([t for t in prioritized_todos if t["priority"] == "low"])
        },
        "by_source": {
            "code": len([t for t in prioritized_todos if t["source"] == "code"]),
            "progress.md": len([t for t in prioritized_todos if t["source"] == "progress.md"]),
            "activeContext.md": len([t for t in prioritized_todos if t["source"] == "activeContext.md"])
        },
        "next_steps": prioritized_todos[:20],  # Top 20 prioritized
        "recently_completed": completed,
        "project_path": str(project_path)
    }

    print(json.dumps(output, indent=2))
    sys.exit(0)


if __name__ == "__main__":
    main()
