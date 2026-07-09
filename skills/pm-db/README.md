# /pm-db

> Project management database for tracking specs, phases, tasks, and execution runs. Use for project status, tracking feature work, progress dashboards, or importing specs from /spec-plan.

## Overview

SQLite-based tracking system (`~/.claude/projects.db`) for the full development lifecycle:

```
Project (e.g., "aiforge")
  └─ Phase (e.g., "file-upload-feature")
       └─ Plan (approved task breakdown + spec documents)
            └─ Tasks (atomic work items with waves/dependencies)
                 └─ Runs (execution attempts with timing/status)
```

Covers spec import (FRD, FRS, GS, TR, task-lists), execution runs, quality gates, code reviews, dashboards/reporting, Memory Bank export, and backup/restore with integrity verification.

## When it triggers

- "What's the status?" / "how's the project going?"
- "Track this feature" / "track this work"
- "Show me progress" / "give me a dashboard"
- "Import my specs" (after `/spec-plan`)

## Quick Start

```bash
/pm-db init        # initialize database + run migrations
/pm-db import      # import specs from job-queue into projects/phases
/pm-db dashboard   # status dashboard with metrics
/pm-db migrate     # apply pending schema migrations (--dry-run supported)
```

Full invocations, flags, and the step-by-step import walkthroughs (including manual import via the Python API) are in `references/commands.md`.

Import notes: default job-queue is `~/.claude/job-queue/`; for the AIForge monorepo add `--job-queue-dir /home/artsmc/applications/low-code/job-queue`. Use `import_specs.py` for `/spec-plan` output, `import_phases.py` for `/start-phase-plan` output.

## Database Schema (v5)

- **Core:** `projects`, `phases`, `phase_plans`, `plan_documents`, `tasks`, `task_dependencies`, `phase_runs`, `task_runs`
- **Tracking:** `task_updates`, `quality_gates`, `code_reviews`, `run_artifacts`, `phase_metrics`
- **Advanced:** `agent_context_cache`, `agent_invocations`, `agent_file_reads`, `checklists`, `checklist_items`

Migrations live in `~/.claude/migrations/`; to add one, create `00N_description.sql` with a `schema_version` insert, then `/pm-db migrate --dry-run` before applying.

## Python API

```python
from project_database import ProjectDatabase   # ~/.claude/lib/project_database.py

with ProjectDatabase() as db:
    project = db.get_project_by_name("aiforge")
    phases = db.list_phases(project_id=1)
    tasks = db.list_tasks(plan_id=1)
    run_id = db.create_phase_run(phase_id=1, plan_id=1)
    db.start_phase_run(run_id)
    db.complete_phase_run(run_id, status='completed')
    dashboard = db.generate_phase_dashboard(phase_id=1)
```

## Automatic Tracking (Hooks)

Hooks in `~/.claude/hooks/pm-db/` track work automatically: run/task lifecycle when `/start-phase execute` begins, per-command execution logging (command, output, exit code, duration), code-review results, and agent assignments. `/feature-new --continue` reads these `phase_runs`/`task_runs` records to resume interrupted work.

## Memory Bank Integration

Exports to **per-project Memory Banks**: reads `filesystem_path` from the projects table, writes to `{filesystem_path}/memory-bank/`, updates `activeContext.md` and `progress.md`, auto-creates minimal structure if missing, debounces per project.

## Performance

Design targets (met): query response <100ms P95, dashboard <2s, 100-spec import <5s, 10,000+ tasks without degradation.

## Context cost

Description always in context (~440 chars); SKILL.md body loads on trigger (~4k chars); `references/commands.md` (~4k chars) loads on demand before running any script. The other references/ docs (API_REFERENCE, DEVELOPMENT, USER_GUIDE, SECURITY_AUDIT, etc.) are deep-dive material read only when needed.

## Files

| Path | Purpose |
|------|---------|
| `SKILL.md` | Concepts, integration map, Python API quick reference, troubleshooting |
| `references/commands.md` | Full command invocations + import walkthroughs (primary reference) |
| `references/API_REFERENCE.md` | Complete Python API documentation |
| `references/DEVELOPMENT.md` | Development guide |
| `references/USER_GUIDE.md` | End-user guide |
| `references/SECURITY_AUDIT.md`, `references/ACCEPTANCE_CRITERIA_VERIFICATION.md`, `references/DOCUMENTATION_REVIEW.md` | Audit/verification records |
| `scripts/init_db.py` | Create DB + apply migrations (`--reset` backs up first) |
| `scripts/migrate.py` | Apply pending migrations (`--dry-run`) |
| `scripts/import_specs.py` | Import raw spec files from job-queue |
| `scripts/import_phases.py` | Import structured phases with tasks/dependencies |
| `scripts/generate_report.py` | Dashboard (text/json/markdown, `--project` filter) |
| `scripts/export_to_memory_bank.py` | Per-project Memory Bank export |
| `tests/` | 10 test suites: unit, hooks, integration, e2e, performance, security, backup/restore, deployment, UAT, v2 smoke |
| `evals/evals.json` | Skill evals |

Shared infrastructure outside this dir: `~/.claude/lib/project_database.py` (core abstraction), `~/.claude/migrations/`, `~/.claude/hooks/pm-db/`, `~/.claude/projects.db`.

## Troubleshooting

- **Database not found** → `python3 ~/.claude/skills/pm-db/scripts/init_db.py`
- **No projects found** → run import with `--auto-confirm`
- **Import found nothing** → check the job-queue path; add `--job-queue-dir` for the monorepo
- **Database locked** → `lsof ~/.claude/projects.db`; WAL mode is enabled by default
- **Migration failed** → `/pm-db migrate --dry-run`, fix the SQL, re-apply

## Related skills

- **/spec-plan** — produces the specs that `import_specs.py` ingests
- **/start-phase-plan / /start-phase-execute** — create and run the plans/tasks PM-DB tracks
- **/feature-new** — imports to PM-DB as Step 4; `--continue` resumes from PM-DB run records
- **/memory-bank-update** — complements the export: PM-DB writes progress, memory-bank skills manage the rest
