#!/usr/bin/env python3
"""
Dashboard Report Generator for Project Management Database (v2 Phase-Based)

Generates formatted status dashboard with project/phase/task metrics
using the PM-DB v2 phase-based execution model.

Usage:
    python3 skills/pm-db/scripts/generate_report.py
    python3 skills/pm-db/scripts/generate_report.py --format json
    python3 skills/pm-db/scripts/generate_report.py --format markdown
    python3 skills/pm-db/scripts/generate_report.py --project auth
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# Add lib to path
lib_path = Path(__file__).parent.parent.parent.parent / "lib"
sys.path.insert(0, str(lib_path))

from project_database import ProjectDatabase


def format_status_bar(completed: int, total: int, width: int = 20) -> str:
    """Create ASCII progress bar."""
    if total == 0:
        filled = 0
    else:
        filled = int((completed / total) * width)

    bar = "\u2588" * filled + "\u2591" * (width - filled)
    percent = int((completed / total) * 100) if total > 0 else 0
    return f"[{bar}] {completed}/{total} ({percent}%)"


def gather_dashboard_data(db, project_filter=None):
    """
    Gather all dashboard data from the v2 phase-based API.

    Args:
        db: ProjectDatabase instance
        project_filter: Optional project name substring to filter by

    Returns:
        Dict with all dashboard data, or None if no projects exist
    """
    projects = db.list_projects()

    if not projects:
        return None

    # Apply project name filter if specified
    if project_filter:
        filter_lower = project_filter.lower()
        projects = [p for p in projects if filter_lower in p['name'].lower()]
        if not projects:
            return {'empty_filter': True, 'filter': project_filter}

    project_data = []
    totals = {
        'projects': len(projects),
        'phases': 0,
        'tasks': 0,
        'tasks_by_status': {
            'pending': 0,
            'in-progress': 0,
            'completed': 0,
            'blocked': 0,
            'skipped': 0,
        },
        'runs_total': 0,
        'runs_completed': 0,
        'runs_failed': 0,
    }

    for project in projects:
        phases = db.list_phases(project_id=project['id'])
        totals['phases'] += len(phases)

        phase_details = []
        for phase in phases:
            phase_info = {
                'id': phase['id'],
                'name': phase['name'],
                'status': phase['status'],
                'phase_type': phase.get('phase_type', 'feature'),
                'created_at': phase.get('created_at', ''),
                'task_count': 0,
                'tasks_by_status': {},
                'run_count': 0,
                'completed_runs': 0,
                'failed_runs': 0,
                'metrics': None,
            }

            # Get plans for this phase and count tasks
            plans = db.list_phase_plans(phase['id'])
            for plan in plans:
                tasks = db.list_tasks(plan_id=plan['id'])
                phase_info['task_count'] += len(tasks)
                totals['tasks'] += len(tasks)

                for task in tasks:
                    status = task.get('status', 'pending')
                    phase_info['tasks_by_status'][status] = (
                        phase_info['tasks_by_status'].get(status, 0) + 1
                    )
                    if status in totals['tasks_by_status']:
                        totals['tasks_by_status'][status] += 1

            # Get runs for this phase
            runs = db.list_phase_runs(phase_id=phase['id'])
            phase_info['run_count'] = len(runs)
            phase_info['completed_runs'] = sum(
                1 for r in runs if r.get('status') == 'completed'
            )
            phase_info['failed_runs'] = sum(
                1 for r in runs if r.get('status') == 'failed'
            )
            totals['runs_total'] += phase_info['run_count']
            totals['runs_completed'] += phase_info['completed_runs']
            totals['runs_failed'] += phase_info['failed_runs']

            # Try to get phase metrics (may crash on NOT NULL constraint)
            try:
                metrics = db.get_phase_metrics(phase['id'])
                phase_info['metrics'] = metrics
            except Exception:
                # Fallback: metrics already computed above from raw data
                phase_info['metrics'] = None

            phase_details.append(phase_info)

        project_data.append({
            'id': project['id'],
            'name': project['name'],
            'description': project.get('description', ''),
            'filesystem_path': project.get('filesystem_path', ''),
            'created_at': project.get('created_at', ''),
            'phases': phase_details,
        })

    return {
        'projects': project_data,
        'totals': totals,
        'generated_at': datetime.now().isoformat(),
    }


def format_text_dashboard(data: dict) -> str:
    """Format dashboard as plain text."""
    lines = []

    lines.append("\u2501" * 50)
    lines.append("  Project Management Dashboard")
    lines.append("\u2501" * 50)
    lines.append(f"  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")

    # Aggregate summary
    totals = data['totals']
    lines.append("\u2501" * 50)
    lines.append("  Summary")
    lines.append("\u2501" * 50)
    lines.append(f"  Projects:  {totals['projects']}")
    lines.append(f"  Phases:    {totals['phases']}")
    lines.append(f"  Tasks:     {totals['tasks']}")
    lines.append(f"  Runs:      {totals['runs_total']} total, "
                 f"{totals['runs_completed']} completed, "
                 f"{totals['runs_failed']} failed")
    lines.append("")

    # Task status breakdown
    tbs = totals['tasks_by_status']
    if totals['tasks'] > 0:
        lines.append("  Tasks by Status:")
        lines.append(f"    Pending:     {tbs.get('pending', 0)}")
        lines.append(f"    In Progress: {tbs.get('in-progress', 0)}")
        lines.append(f"    Completed:   {tbs.get('completed', 0)}")
        lines.append(f"    Blocked:     {tbs.get('blocked', 0)}")
        lines.append(f"    Skipped:     {tbs.get('skipped', 0)}")
        lines.append("")
        completed = tbs.get('completed', 0)
        lines.append(f"  Progress: {format_status_bar(completed, totals['tasks'])}")
    lines.append("")

    # Per-project details
    lines.append("\u2501" * 50)
    lines.append("  Projects & Phases")
    lines.append("\u2501" * 50)

    for proj in data['projects']:
        lines.append("")
        lines.append(f"  [{proj['name']}]")
        if proj['description']:
            lines.append(f"    {proj['description']}")

        if not proj['phases']:
            lines.append("    (no phases)")
            continue

        for phase in proj['phases']:
            status_icon = _status_icon(phase['status'])
            lines.append(
                f"    {status_icon} {phase['name']}  "
                f"[{phase['status']}]  "
                f"type={phase['phase_type']}"
            )
            lines.append(
                f"       Tasks: {phase['task_count']}  |  "
                f"Runs: {phase['run_count']} "
                f"({phase['completed_runs']} completed)"
            )

            # Task breakdown if any
            if phase['tasks_by_status']:
                parts = []
                for s, c in sorted(phase['tasks_by_status'].items()):
                    if c > 0:
                        parts.append(f"{s}={c}")
                if parts:
                    lines.append(f"       Task status: {', '.join(parts)}")

    lines.append("")
    lines.append("\u2501" * 50)
    return "\n".join(lines)


def format_markdown_dashboard(data: dict) -> str:
    """Format dashboard as Markdown."""
    lines = []

    lines.append("# Project Management Dashboard")
    lines.append("")
    lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")

    # Summary
    totals = data['totals']
    lines.append("## Summary")
    lines.append("")
    lines.append(f"| Metric | Count |")
    lines.append(f"|--------|-------|")
    lines.append(f"| Projects | {totals['projects']} |")
    lines.append(f"| Phases | {totals['phases']} |")
    lines.append(f"| Tasks | {totals['tasks']} |")
    lines.append(f"| Runs (total) | {totals['runs_total']} |")
    lines.append(f"| Runs (completed) | {totals['runs_completed']} |")
    lines.append(f"| Runs (failed) | {totals['runs_failed']} |")
    lines.append("")

    # Task status breakdown
    tbs = totals['tasks_by_status']
    if totals['tasks'] > 0:
        lines.append("### Tasks by Status")
        lines.append("")
        lines.append("| Status | Count |")
        lines.append("|--------|-------|")
        lines.append(f"| Pending | {tbs.get('pending', 0)} |")
        lines.append(f"| In Progress | {tbs.get('in-progress', 0)} |")
        lines.append(f"| Completed | {tbs.get('completed', 0)} |")
        lines.append(f"| Blocked | {tbs.get('blocked', 0)} |")
        lines.append(f"| Skipped | {tbs.get('skipped', 0)} |")
        lines.append("")

    # Per-project details
    for proj in data['projects']:
        lines.append(f"## {proj['name']}")
        lines.append("")
        if proj['description']:
            lines.append(f"*{proj['description']}*")
            lines.append("")

        if not proj['phases']:
            lines.append("*No phases defined.*")
            lines.append("")
            continue

        lines.append("| Phase | Status | Type | Tasks | Runs | Completed Runs |")
        lines.append("|-------|--------|------|-------|------|----------------|")
        for phase in proj['phases']:
            lines.append(
                f"| {phase['name']} "
                f"| {phase['status']} "
                f"| {phase['phase_type']} "
                f"| {phase['task_count']} "
                f"| {phase['run_count']} "
                f"| {phase['completed_runs']} |"
            )
        lines.append("")

    return "\n".join(lines)


def _status_icon(status: str) -> str:
    """Return a text icon for a phase/task status."""
    icons = {
        'draft': '[ ]',
        'planning': '[~]',
        'approved': '[+]',
        'in-progress': '[>]',
        'completed': '[x]',
        'archived': '[-]',
        'failed': '[!]',
        'pending': '[ ]',
        'blocked': '[#]',
        'skipped': '[-]',
    }
    return icons.get(status, '[?]')


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate PM-DB v2 dashboard report"
    )
    parser.add_argument(
        "--format",
        choices=['text', 'json', 'markdown'],
        default='text',
        help="Output format (default: text)"
    )
    parser.add_argument(
        "--project",
        help="Filter by project name (substring match)"
    )

    args = parser.parse_args()

    # Check database exists
    db_path = Path.home() / ".claude" / "projects.db"
    if not db_path.exists():
        print("Error: Database not found at ~/.claude/projects.db")
        print("Run `/pm-db init` then `/pm-db import` to set up the database.")
        sys.exit(1)

    try:
        with ProjectDatabase() as db:
            data = gather_dashboard_data(db, project_filter=args.project)

            # Handle empty state
            if data is None:
                print("No projects found.")
                print("Run `/pm-db init` then `/pm-db import` to populate the database.")
                sys.exit(0)

            # Handle empty filter results
            if data.get('empty_filter'):
                print(f"No projects matching filter '{data['filter']}'.")
                sys.exit(0)

            # Format output
            if args.format == 'json':
                print(json.dumps(data, indent=2, default=str))
            elif args.format == 'markdown':
                print(format_markdown_dashboard(data))
            else:
                print(format_text_dashboard(data))

    except Exception as e:
        print(f"Error generating dashboard: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
