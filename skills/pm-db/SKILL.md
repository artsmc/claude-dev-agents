---
name: pm-db
description: "Project management database for tracking specs, phases, tasks, and execution runs. Use this skill whenever the user asks about project status, wants to track feature work, needs a dashboard of progress, wants to import specs from /spec-plan, or mentions tracking tasks, phases, or runs. Also use when the user says things like 'what's the status', 'how's the project going', 'track this work', 'show me progress', or 'import my specs'."
args:
  command:
    type: string
    description: "Command to execute: init, import, dashboard, status, migrate"
    required: false
---

# PM-DB: Project Management Database

SQLite-based tracking for the full development lifecycle: specs → phases → tasks → runs.

## Core Concepts

PM-DB tracks work in a hierarchy:

```
Project (e.g., "aiforge")
  └─ Phase (e.g., "file-upload-feature")
       └─ Plan (approved task breakdown)
            └─ Tasks (atomic work items with waves/dependencies)
                 └─ Runs (execution attempts with timing/status)
```

**Why this matters:** When a user asks "what's the status?", you query projects → phases → tasks. When they say "track this feature", you create a phase with a plan and tasks.

## Commands & Import Walkthrough

Full command invocations (init, import, dashboard, migrate, export) and the step-by-step import walkthroughs (including manual Python-API import) live in `references/commands.md` — read it before running any pm-db script or importing specs.

## Cross-Skill Integration

PM-DB connects to other skills in the workflow:

```
/spec-plan → generates specs in job-queue/
     ↓
/pm-db import → imports specs into projects/phases
     ↓
/start-phase-plan → creates execution plan with tasks
     ↓
/pm-db tracks → phases, runs, task completions
     ↓
/pm-db dashboard → shows progress
```

**Key paths:**
- Spec-plan output: `/home/artsmc/applications/low-code/job-queue/feature-*/docs/`
- PM-DB database: `~/.claude/projects.db`
- Python API: `~/.claude/lib/project_database.py`

## Python API (Quick Reference)

```python
from project_database import ProjectDatabase

with ProjectDatabase() as db:
    # Projects
    projects = db.list_projects()
    project = db.get_project_by_name("aiforge")

    # Phases
    phases = db.list_phases(project_id=1)
    phase = db.get_phase(phase_id=1)

    # Plans and tasks
    plans = db.list_phase_plans(phase_id=1)
    tasks = db.list_tasks(plan_id=1)

    # Runs
    run_id = db.create_phase_run(phase_id=1, plan_id=1)
    db.start_phase_run(run_id)
    db.complete_phase_run(run_id, status='completed')

    # Dashboard
    dashboard = db.generate_phase_dashboard(phase_id=1)
    metrics = db.get_phase_metrics(phase_id=1)
```

For the complete API, read `~/.claude/lib/project_database.py`.

## Database Schema (v5)

Core tables: `projects`, `phases`, `phase_plans`, `plan_documents`, `tasks`, `task_dependencies`, `phase_runs`, `task_runs`

Tracking tables: `task_updates`, `quality_gates`, `code_reviews`, `run_artifacts`, `phase_metrics`

Advanced: `agent_context_cache`, `agent_invocations`, `agent_file_reads`, `checklists`, `checklist_items`

## Troubleshooting

**"Database not found"** → Run `python3 ~/.claude/skills/pm-db/scripts/init_db.py`

**"No projects found"** → Run import: `python3 ~/.claude/skills/pm-db/scripts/import_specs.py --auto-confirm`

**"Import found nothing"** → Check the job-queue path. Default is `~/.claude/job-queue/`. For the monorepo, add `--job-queue-dir /home/artsmc/applications/low-code/job-queue`

**"Which import script?"** → `import_specs.py` for spec files, `import_phases.py` for structured phases

**"Database locked"** → Check `lsof ~/.claude/projects.db`. WAL mode is enabled by default.

---

**Database:** `~/.claude/projects.db`
**API:** `~/.claude/lib/project_database.py`
**Version:** 2.0
