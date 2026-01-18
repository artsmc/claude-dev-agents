-- Migration 003: Add Execution Logs and Agent Assignments
-- Adds execution_logs and agent_assignments tables for complete audit trail

BEGIN TRANSACTION;

-- ==================== EXECUTION LOGS TABLE ====================

CREATE TABLE execution_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id INTEGER NOT NULL,
    task_id INTEGER,
    command TEXT NOT NULL,   -- Command that was executed
    output TEXT,             -- Command output (stdout + stderr)
    exit_code INTEGER,       -- Exit code
    duration_ms INTEGER,     -- Duration in milliseconds
    executed_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE,
    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE
);

CREATE INDEX idx_execution_logs_job_id ON execution_logs(job_id);
CREATE INDEX idx_execution_logs_task_id ON execution_logs(task_id);
CREATE INDEX idx_execution_logs_executed_at ON execution_logs(executed_at);
CREATE INDEX idx_execution_logs_exit_code ON execution_logs(exit_code);

-- ==================== AGENT ASSIGNMENTS TABLE ====================

CREATE TABLE agent_assignments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_type TEXT NOT NULL,  -- Type of agent (e.g., "python-backend-developer")
    job_id INTEGER,
    task_id INTEGER,
    status TEXT NOT NULL DEFAULT 'assigned',  -- assigned, in-progress, completed, failed
    assigned_at TEXT NOT NULL DEFAULT (datetime('now')),
    started_at TEXT,
    completed_at TEXT,
    duration_seconds INTEGER,
    FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE,
    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE
);

CREATE INDEX idx_agent_assignments_agent_type ON agent_assignments(agent_type);
CREATE INDEX idx_agent_assignments_job_id ON agent_assignments(job_id);
CREATE INDEX idx_agent_assignments_task_id ON agent_assignments(task_id);
CREATE INDEX idx_agent_assignments_status ON agent_assignments(status);
CREATE INDEX idx_agent_assignments_assigned_at ON agent_assignments(assigned_at);

-- Trigger to calculate agent assignment duration
CREATE TRIGGER agent_assignments_duration_trigger
AFTER UPDATE OF completed_at ON agent_assignments
WHEN NEW.completed_at IS NOT NULL AND NEW.started_at IS NOT NULL
BEGIN
    UPDATE agent_assignments
    SET duration_seconds = CAST((julianday(NEW.completed_at) - julianday(NEW.started_at)) * 86400 AS INTEGER)
    WHERE id = NEW.id;
END;

-- ==================== UPDATE SCHEMA VERSION ====================

INSERT INTO schema_version (version, description)
VALUES (3, 'Add execution_logs and agent_assignments tables for complete audit trail');

COMMIT;
