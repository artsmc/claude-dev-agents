# PM-DB Hooks

These are **explicit-call utility scripts**, not Claude Code event hooks.

They are NOT registered in `settings.json` and are NOT auto-triggered by Claude Code events. Skills and agents invoke them directly by piping JSON to stdin.

## Database

All hooks use `~/.claude/projects.db` (via `lib/project_database.py`). There is no `pm.db` file.

## Usage Pattern

```bash
echo '{"key": "value"}' | python3 ~/.claude/hooks/pm-db/<hook-name>.py
```

All hooks read JSON from stdin and write JSON to stdout. On error, they write to stderr and exit 0 (non-blocking).

## Hook Reference

### on-job-start.py
Creates a job record when phase execution begins.

**Input:**
```json
{"job_name": "Build auth feature", "spec_id": 1, "assigned_agent": "python-backend-developer", "priority": "high", "session_id": "abc123"}
```
**Output:** `{"job_id": 42, "status": "created"}`
**Required fields:** `job_name`

### on-task-start.py
Creates and starts a task record within a job.

**Input:**
```json
{"job_id": 42, "task_name": "Implement login endpoint", "order": 1, "dependencies": null}
```
**Output:** `{"task_id": 7, "status": "created"}`
**Required fields:** `job_id`, `task_name`

### on-task-complete.py
Marks a task as completed.

**Input:**
```json
{"job_id": 42, "task_name": "Implement login endpoint", "exit_code": 0}
```
**Output:** `{"task_id": 7, "status": "completed"}`
**Required fields:** `job_id`, `task_name`

### on-agent-assign.py
Records an agent assignment to a job or task.

**Input:**
```json
{"agent_type": "code-reviewer", "job_id": 42, "task_id": 7}
```
**Output:** `{"assignment_id": 3, "status": "assigned"}`
**Required fields:** `agent_type`, and one of `job_id` or `task_id`

### on-tool-use.py
Logs a command execution within a job context.

**Input:**
```json
{"job_id": 42, "task_id": 7, "command": "npm test", "output": "...", "exit_code": 0, "start_time": 1706000000, "end_time": 1706000005}
```
**Output:** `{"log_id": 15, "status": "logged"}`
**Required fields:** `job_id` (skips silently if absent)

### on-code-review.py
Stores a code review summary for a phase run.

**Input:**
```json
{"phase_run_id": 10, "reviewer": "code-reviewer", "summary": "LGTM", "verdict": "passed", "issues_found": "[]", "files_reviewed": "[\"src/auth.ts\"]"}
```
**Output:** `{"review_id": 5, "status": "created"}`
**Required fields:** `phase_run_id`, `reviewer`, `summary`

### on-quality-gate.py
Records a quality gate check result.

**Input:**
```json
{"phase_run_id": 10, "gate_type": "testing", "status": "passed", "result_summary": "All 42 tests pass", "checked_by": "qa-engineer"}
```
**Output:** `{"gate_id": 3, "status": "passed"}`

### on-phase-run-start.py
Creates and starts a phase run record.

**Input:**
```json
{"phase_name": "Execute", "project_name": "my-project", "assigned_agent": "express-api-developer"}
```
**Output:** `{"phase_run_id": 10, "phase_id": 2, "plan_id": 5, "status": "started"}`

### on-phase-run-complete.py
Completes a phase run with exit code and summary.

**Input:**
```json
{"phase_run_id": 10, "exit_code": 0, "summary": "All tasks completed successfully"}
```
**Output:** `{"phase_run_id": 10, "status": "completed", "metrics": {...}}`

### on-task-run-start.py
Creates and starts a task run within a phase run.

**Input:**
```json
{"phase_run_id": 10, "task_key": "2.1a", "assigned_agent": "frontend-developer"}
```
**Output:** `{"task_run_id": 4, "task_id": 12, "status": "started"}`

### on-task-run-complete.py
Completes a task run.

**Input:**
```json
{"task_run_id": 4, "exit_code": 0}
```
**Output:** `{"task_run_id": 4, "status": "completed"}`

### on-memory-bank-sync.py
Exports project data to Memory Bank with per-project debouncing (5 min interval).

**Input:**
```json
{"project_id": 123, "force": false}
```
**Output:** `{"status": "exported", "project_id": 123, "project_name": "my-app", "last_export": "2026-01-17T20:00:00"}`
**Possible statuses:** `exported`, `skipped` (debounced), `failed`
