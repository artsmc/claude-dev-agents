#!/usr/bin/env python3
"""
Memory Bank Sync Hook

Automatically exports project data to Memory Bank after job/task completion.

Uses PER-PROJECT debouncing (not global) to prevent excessive exports.

Hook triggers:
- on-job-complete
- on-task-complete
- manual /pm-db sync command

Debouncing:
- Per-project last_export timestamp
- Minimum interval: 5 minutes (configurable)
- Forces export if --force flag passed

Input JSON:
{
    "project_id": 123,        # Required
    "force": false            # Optional, default false
}

Output JSON:
{
    "status": "exported" | "skipped" | "failed",
    "project_name": "my-app",
    "reason": "...",
    "last_export": "2026-01-17 20:00:00"
}
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timedelta
import subprocess

# Add lib to path
lib_path = Path(__file__).parent.parent.parent / "lib"
sys.path.insert(0, str(lib_path))

from project_database import ProjectDatabase


# Configuration
DEBOUNCE_MINUTES = 5  # Minimum time between exports per project
DEBOUNCE_FILE = Path.home() / ".claude" / ".memory-bank-export-timestamps.json"


def load_debounce_state() -> dict:
    """
    Load debounce state from file.

    Returns:
        Dict of project_id -> last_export_timestamp
    """
    if not DEBOUNCE_FILE.exists():
        return {}

    try:
        with open(DEBOUNCE_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}


def save_debounce_state(state: dict):
    """
    Save debounce state to file.

    Args:
        state: Dict of project_id -> last_export_timestamp
    """
    try:
        DEBOUNCE_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(DEBOUNCE_FILE, 'w') as f:
            json.dump(state, f, indent=2)
    except IOError:
        pass  # Fail silently, debounce is best-effort


def should_export(project_id: int, force: bool = False) -> tuple[bool, str]:
    """
    Check if project should be exported based on debounce rules.

    Args:
        project_id: Project ID
        force: If True, ignore debounce

    Returns:
        Tuple of (should_export, reason)
    """
    if force:
        return True, "Force export requested"

    # Load debounce state
    state = load_debounce_state()
    project_key = str(project_id)

    # Check if project has been exported recently
    if project_key not in state:
        return True, "First export for this project"

    last_export_str = state[project_key]
    try:
        last_export = datetime.fromisoformat(last_export_str)
    except (ValueError, TypeError):
        return True, "Invalid last export timestamp"

    # Calculate time since last export
    now = datetime.now()
    time_since_export = now - last_export
    debounce_interval = timedelta(minutes=DEBOUNCE_MINUTES)

    if time_since_export < debounce_interval:
        remaining = debounce_interval - time_since_export
        minutes = int(remaining.total_seconds() / 60)
        return False, f"Debounced (exported {minutes}m ago, min {DEBOUNCE_MINUTES}m)"

    return True, f"Last export was {int(time_since_export.total_seconds() / 60)}m ago"


def record_export(project_id: int):
    """
    Record successful export in debounce state.

    Args:
        project_id: Project ID
    """
    state = load_debounce_state()
    state[str(project_id)] = datetime.now().isoformat()
    save_debounce_state(state)


def run_export(project_id: int) -> tuple[bool, str]:
    """
    Run export script for project.

    Args:
        project_id: Project ID

    Returns:
        Tuple of (success, output)
    """
    try:
        # Get project name for logging
        with ProjectDatabase() as db:
            project = db.get_project(project_id)
            if not project:
                return False, f"Project ID {project_id} not found"

            project_name = project['name']

        # Run export script
        script_path = Path(__file__).parent.parent.parent / "skills/pm-db/scripts/export_to_memory_bank.py"

        result = subprocess.run(
            ["python3", str(script_path), "--project", project_name],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode == 0:
            return True, result.stdout
        else:
            return False, result.stderr or result.stdout

    except subprocess.TimeoutExpired:
        return False, "Export script timeout (>30s)"
    except Exception as e:
        return False, f"Export failed: {e}"


def main():
    """Main hook entry point."""
    try:
        # Read input from stdin
        hook_data = json.load(sys.stdin)

        # Extract parameters
        project_id = hook_data.get('project_id')
        force = hook_data.get('force', False)

        # Validate input
        if not project_id:
            print(json.dumps({
                "status": "failed",
                "reason": "Missing required parameter: project_id"
            }))
            sys.exit(0)

        # Get project name for logging
        with ProjectDatabase() as db:
            project = db.get_project(project_id)
            if not project:
                print(json.dumps({
                    "status": "failed",
                    "project_id": project_id,
                    "reason": f"Project ID {project_id} not found"
                }))
                sys.exit(0)

            project_name = project['name']

        # Check debounce
        should_run, reason = should_export(project_id, force)

        if not should_run:
            print(json.dumps({
                "status": "skipped",
                "project_id": project_id,
                "project_name": project_name,
                "reason": reason
            }))
            sys.exit(0)

        # Run export
        success, output = run_export(project_id)

        if success:
            # Record successful export
            record_export(project_id)

            print(json.dumps({
                "status": "exported",
                "project_id": project_id,
                "project_name": project_name,
                "reason": reason,
                "last_export": datetime.now().isoformat()
            }))
        else:
            print(json.dumps({
                "status": "failed",
                "project_id": project_id,
                "project_name": project_name,
                "reason": f"Export failed: {output[:200]}"
            }))

    except json.JSONDecodeError:
        print(json.dumps({
            "status": "failed",
            "reason": "Invalid JSON input"
        }), file=sys.stderr)
        sys.exit(0)
    except Exception as e:
        print(json.dumps({
            "status": "failed",
            "reason": f"Unexpected error: {str(e)}"
        }), file=sys.stderr)
        sys.exit(0)


if __name__ == "__main__":
    main()
