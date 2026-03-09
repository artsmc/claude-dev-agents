# PM-DB Tracking Reference

Detailed hook commands for tracking execution in the PM-DB database.
Read this file when you need to integrate with PM-DB during execution.

## Prerequisites

- Database exists at `~/.claude/projects.db`
- Hooks exist at `~/.claude/hooks/pm-db/`

## Phase Run Lifecycle

### Start Phase Run (call at Phase 1)

```bash
echo '{
  "phase_name": "FEATURE_NAME",
  "project_name": "PROJECT_NAME",
  "assigned_agent": "start-phase-execute"
}' | python3 ~/.claude/hooks/pm-db/on-phase-run-start.py
```

Returns: `{"phase_run_id": N, "phase_id": N, "plan_id": N, "status": "started"}`

Store `phase_run_id` for the session.

### Start Task Run (call before each task)

```bash
echo '{
  "phase_run_id": PHASE_RUN_ID,
  "task_key": "TASK_NUMBER",
  "assigned_agent": "AGENT_TYPE"
}' | python3 ~/.claude/hooks/pm-db/on-task-run-start.py
```

Returns: `{"task_run_id": N, "task_id": N, "status": "started"}`

### Complete Task Run (call after each task)

```bash
echo '{
  "task_run_id": TASK_RUN_ID,
  "exit_code": 0
}' | python3 ~/.claude/hooks/pm-db/on-task-run-complete.py
```

### Record Quality Gate

```bash
echo '{
  "phase_run_id": PHASE_RUN_ID,
  "gate_type": "code_review",
  "status": "passed",
  "result_summary": "Lint: 0 errors, Build: success",
  "checked_by": "quality-gate"
}' | python3 ~/.claude/hooks/pm-db/on-quality-gate.py
```

### Complete Phase Run (call at Phase 5)

```bash
echo '{
  "phase_run_id": PHASE_RUN_ID,
  "exit_code": 0,
  "summary": "Completed all N tasks for FEATURE_NAME"
}' | python3 ~/.claude/hooks/pm-db/on-phase-run-complete.py
```

## Error Handling

If any hook fails, log the error and continue execution.
PM-DB tracking is valuable but should never block task execution.

```bash
# Safe hook call pattern
hook_output=$(echo '...' | python3 ~/.claude/hooks/pm-db/on-phase-run-start.py 2>&1) || \
  echo "PM-DB hook failed (non-blocking): $hook_output"
```

## Querying Progress

```sql
-- Find latest phase run for a feature
SELECT pr.id, pr.status, pr.started_at,
       COUNT(tr.id) as task_runs,
       SUM(CASE WHEN tr.status='completed' THEN 1 ELSE 0 END) as completed
FROM phase_runs pr
LEFT JOIN task_runs tr ON tr.phase_run_id = pr.id
JOIN phases p ON p.id = pr.phase_id
WHERE p.name LIKE '%feature_name%'
GROUP BY pr.id
ORDER BY pr.started_at DESC LIMIT 1;
```
