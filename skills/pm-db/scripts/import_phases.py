#!/usr/bin/env python3
"""
Phase Import Script for PM-DB v2

Imports phases from /job-queue/feature-*/docs/ into PM-DB v2 schema.

Usage:
    python3 skills/pm-db/scripts/import_phases.py
    python3 skills/pm-db/scripts/import_phases.py --project deepwiki-integration
"""

import sys
from pathlib import Path
import os

# Suppress locale warnings by setting C.UTF-8
os.environ['LC_ALL'] = 'C.UTF-8'
os.environ['LANG'] = 'C.UTF-8'

# Add lib to path
lib_path = Path.home() / ".claude" / "lib"
sys.path.insert(0, str(lib_path))

from project_database import ProjectDatabase


def infer_project_path(feature_folder: Path) -> str:
    """Infer project filesystem path from feature folder name."""
    feature_name = feature_folder.name.replace('feature-', '')
    home = Path.home()

    candidates = [
        home / "applications" / feature_name,
        home / "projects" / feature_name,
        home / "repos" / feature_name,
        home / feature_name
    ]

    for path in candidates:
        if path.exists():
            return str(path)

    return str(home / "applications" / feature_name)


def prompt_for_path(project_name: str, inferred_path: str) -> str:
    """Prompt user for project filesystem path."""
    print(f"\n📍 Project Path Needed: {project_name}")
    print(f"   Inferred path: {inferred_path}")

    response = input(f"   Use this path? (Y/n) or enter custom path: ").strip()

    if not response or response.lower() == 'y':
        path = inferred_path
    else:
        path = response

    path_obj = Path(path)
    if not path_obj.is_absolute():
        print(f"   ⚠️  Path must be absolute, converting...")
        path = str(path_obj.absolute())

    if not path_obj.exists():
        print(f"   ⚠️  Warning: Path does not exist yet: {path}")
        confirm = input(f"   Use anyway? (y/N): ").strip()
        if confirm.lower() != 'y':
            return prompt_for_path(project_name, inferred_path)

    return path


def import_phase(
    db: ProjectDatabase,
    feature_folder: Path,
    project_filter: str = None,
    auto_confirm: bool = False
) -> bool:
    """
    Import a single phase from feature folder.

    Returns:
        True if imported, False if skipped
    """
    docs_folder = feature_folder / "docs"

    if not docs_folder.exists():
        return False

    feature_name = feature_folder.name

    # Filter by project if specified
    if project_filter and project_filter not in feature_name:
        return False

    print(f"\n📦 Processing: {feature_name}")

    # Read spec files
    spec_files = {
        'frd': docs_folder / "FRD.md",
        'frs': docs_folder / "FRS.md",
        'gs': docs_folder / "GS.md",
        'tr': docs_folder / "TR.md",
        'task_list': docs_folder / "task-list.md"
    }

    contents = {}
    found_files = 0

    for key, file_path in spec_files.items():
        if file_path.exists():
            with open(file_path, 'r') as f:
                contents[key] = f.read()
            found_files += 1
            print(f"   ✅ Found: {file_path.name}")
        else:
            contents[key] = None

    if found_files == 0:
        print(f"   ❌ No spec files found, skipping")
        return False

    # Extract project name from feature name
    project_name = feature_name.replace('feature-', '')

    # Check if project exists
    existing_project = db.get_project_by_name(project_name)

    if existing_project:
        project_id = existing_project['id']
        print(f"   📁 Using existing project: {project_name} (ID: {project_id})")
        filesystem_path = existing_project.get('filesystem_path')
    else:
        # Create project
        inferred_path = infer_project_path(feature_folder)

        if auto_confirm:
            filesystem_path = inferred_path
        else:
            filesystem_path = prompt_for_path(project_name, inferred_path)

        print(f"   📁 Creating project: {project_name}")
        print(f"   📍 Filesystem path: {filesystem_path}")

        project_id = db.create_project(
            name=project_name,
            description=f"Auto-imported from {feature_name}",
            filesystem_path=filesystem_path
        )

    # Check if phase already exists
    phases = db.list_phases(project_id=project_id)
    phase_name = project_name  # Use project name as phase name
    existing_phase = next((p for p in phases if p['name'] == phase_name), None)

    if existing_phase:
        phase_id = existing_phase['id']
        print(f"   📋 Using existing phase: {phase_name} (ID: {phase_id})")
    else:
        # Create phase
        print(f"   📋 Creating phase: {phase_name}")
        phase_id = db.create_phase(
            project_id=project_id,
            name=phase_name,
            phase_type='feature',
            job_queue_rel_path=str(feature_folder),
            description=f"Auto-imported from {feature_name}",
            status='draft'
        )

    # Check if phase plan already exists
    plans = db.list_phase_plans(phase_id=phase_id)
    if plans:
        print(f"   ⚠️  Phase plan already exists (ID: {plans[0]['id']}), skipping")
        return False

    # Create phase plan
    print(f"   📝 Creating phase plan")
    plan_id = db.create_phase_plan(
        phase_id=phase_id,
        planning_approach=f"Imported from {feature_name}"
    )

    # Add documents to phase plan
    doc_types = {
        'frd': ('frd', 'Functional Requirements Document'),
        'frs': ('frs', 'Functional Requirements Specification'),
        'gs': ('gs', 'Getting Started Guide'),
        'tr': ('tr', 'Technical Requirements'),
        'task_list': ('task-list', 'Task List')
    }

    for key, (doc_type, doc_name) in doc_types.items():
        if contents[key]:
            db.add_plan_document(
                plan_id=plan_id,
                doc_type=doc_type,
                doc_name=doc_name,
                content=contents[key]
            )
            print(f"   ✅ Added document: {doc_name}")

    print(f"   ✅ Phase plan imported (ID: {plan_id})")

    return True


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Import phases from job-queue")
    parser.add_argument(
        "--project",
        help="Filter by project name (e.g., 'deepwiki-integration')"
    )
    parser.add_argument(
        "--job-queue-dir",
        default=str(Path.home() / ".claude" / "job-queue"),
        help="Path to job-queue directory"
    )
    parser.add_argument(
        "--auto-confirm",
        action="store_true",
        help="Auto-confirm inferred paths (no prompts)"
    )

    args = parser.parse_args()

    job_queue = Path(args.job_queue_dir)

    if not job_queue.exists():
        print(f"❌ Job queue directory not found: {job_queue}")
        sys.exit(1)

    print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"📥 Phase Import (PM-DB v2)")
    print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"\nScanning: {job_queue}")

    # Find all feature-* folders
    feature_folders = sorted(job_queue.glob("feature-*"))

    if not feature_folders:
        print(f"\n⚠️  No feature folders found")
        sys.exit(0)

    print(f"Found {len(feature_folders)} feature folder(s)")

    # Import each phase
    imported = 0
    skipped = 0

    with ProjectDatabase() as db:
        for feature_folder in feature_folders:
            if import_phase(db, feature_folder, args.project, args.auto_confirm):
                imported += 1
            else:
                skipped += 1

    # Summary
    print(f"\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"✅ Import Complete")
    print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"\nImported: {imported}")
    print(f"Skipped: {skipped}")
    print(f"Total processed: {imported + skipped}")
    print()


if __name__ == "__main__":
    main()
