# PM-DB Commands Reference & Import Walkthrough

Full command invocations for init, import, dashboard, migrate, and export, plus the step-by-step import walkthroughs (including manual import via the Python API).

## Quick Start Workflows

### "Set up project tracking" → Init + Import

```bash
# 1. Initialize the database (creates ~/.claude/projects.db)
python3 ~/.claude/skills/pm-db/scripts/init_db.py

# 2. Import specs from job-queue
python3 ~/.claude/skills/pm-db/scripts/import_specs.py --auto-confirm

# 3. Also import from monorepo job-queue (if applicable)
python3 ~/.claude/skills/pm-db/scripts/import_specs.py --auto-confirm \
  --job-queue-dir /home/artsmc/applications/low-code/job-queue

# 4. View what was imported
python3 ~/.claude/skills/pm-db/scripts/generate_report.py
```

### "What's the project status?" → Dashboard

```bash
python3 ~/.claude/skills/pm-db/scripts/generate_report.py
python3 ~/.claude/skills/pm-db/scripts/generate_report.py --format json
python3 ~/.claude/skills/pm-db/scripts/generate_report.py --format markdown
python3 ~/.claude/skills/pm-db/scripts/generate_report.py --project aiforge
```

If the database doesn't exist, tell the user to run init first.

### "I just ran /spec-plan, now track the tasks" → Import from Spec-Plan

Spec-plan outputs land in `/home/artsmc/applications/low-code/job-queue/feature-*/docs/`.
PM-DB imports from that same location:

```bash
# Import all specs from the monorepo job-queue
python3 ~/.claude/skills/pm-db/scripts/import_specs.py --auto-confirm \
  --job-queue-dir /home/artsmc/applications/low-code/job-queue
```

If the spec-plan output is in a non-standard location (e.g., a workspace dir),
you can import manually using the Python API:

```python
import sys
sys.path.insert(0, str(Path.home() / '.claude/lib'))
from project_database import ProjectDatabase

with ProjectDatabase() as db:
    # Create or find the project
    project = db.get_project_by_name("aiforge")
    if not project:
        project_id = db.create_project("aiforge", "AIForge platform",
                                        "/home/artsmc/applications/low-code")
    else:
        project_id = project['id']

    # Create a phase for the feature
    phase_id = db.create_phase(
        project_id=project_id,
        name="feature-name",
        description="Feature description",
        status="planning"
    )

    # Create a plan with the spec documents
    plan_id = db.create_phase_plan(
        phase_id=phase_id,
        documents={
            "frd": open("path/to/FRD.md").read(),
            "tr": open("path/to/TR.md").read(),
            "task_list": open("path/to/task-list.md").read()
        }
    )
```

## Commands Reference

### `init` — Initialize Database

Creates `~/.claude/projects.db` with all migrations applied.

```bash
python3 ~/.claude/skills/pm-db/scripts/init_db.py
python3 ~/.claude/skills/pm-db/scripts/init_db.py --reset  # Backup + fresh DB
```

### `import` — Import Specifications

Imports specs from job-queue directories into projects/phases/plans.

```bash
python3 ~/.claude/skills/pm-db/scripts/import_specs.py --auto-confirm
python3 ~/.claude/skills/pm-db/scripts/import_specs.py --auto-confirm --job-queue-dir /path/to/job-queue
python3 ~/.claude/skills/pm-db/scripts/import_specs.py --project auth  # Filter by name
```

**Two import scripts exist:**
- `import_specs.py` — Imports raw spec files (FRD, FRS, GS, TR, task-list) from job-queue
- `import_phases.py` — Imports structured phase definitions with tasks and dependencies

Use `import_specs.py` for importing from `/spec-plan` output. Use `import_phases.py` for importing from `/start-phase-plan` output.

### `dashboard` — Show Status

Generates a status dashboard with project/phase/task metrics.

```bash
python3 ~/.claude/skills/pm-db/scripts/generate_report.py
python3 ~/.claude/skills/pm-db/scripts/generate_report.py --format json
python3 ~/.claude/skills/pm-db/scripts/generate_report.py --format markdown
python3 ~/.claude/skills/pm-db/scripts/generate_report.py --project aiforge
```

### `migrate` — Run Migrations

Applies pending database schema migrations.

```bash
python3 ~/.claude/skills/pm-db/scripts/migrate.py
python3 ~/.claude/skills/pm-db/scripts/migrate.py --dry-run
```

### `export` — Export to Memory Bank

Exports project data to per-project Memory Bank directories.

```bash
python3 ~/.claude/skills/pm-db/scripts/export_to_memory_bank.py
```
