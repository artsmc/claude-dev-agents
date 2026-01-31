-- Migration 004: PM-DB v2 Schema Transformation
-- Migrates from spec-centric model (v3) to phase-based execution tracking (v2)
-- Breaking change: v3 → v4 with data preservation

BEGIN TRANSACTION;

-- ============================================================================
-- STEP 1: Drop old indexes and rename tables to *_legacy for reference
-- ============================================================================

-- Drop old indexes first to avoid conflicts
DROP INDEX IF EXISTS idx_specs_project_id;
DROP INDEX IF EXISTS idx_specs_status;
DROP INDEX IF EXISTS idx_jobs_spec_id;
DROP INDEX IF EXISTS idx_jobs_status;
DROP INDEX IF EXISTS idx_tasks_job_id;
DROP INDEX IF EXISTS idx_tasks_status;
DROP INDEX IF EXISTS idx_code_reviews_job_id;
DROP INDEX IF EXISTS idx_code_reviews_task_id;
DROP INDEX IF EXISTS idx_execution_logs_job_id;
DROP INDEX IF EXISTS idx_execution_logs_task_id;
DROP INDEX IF EXISTS idx_agent_assignments_job_id;
DROP INDEX IF EXISTS idx_agent_assignments_task_id;

-- Rename old tables
ALTER TABLE specs RENAME TO specs_legacy;
ALTER TABLE jobs RENAME TO jobs_legacy;
ALTER TABLE tasks RENAME TO tasks_legacy;

-- ============================================================================
-- STEP 2: Create new core tables (phases, phase_plans, plan_documents)
-- ============================================================================

-- phases: Top-level feature/project phases (replaces specs)
CREATE TABLE phases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    phase_type TEXT NOT NULL DEFAULT 'feature', -- feature, bugfix, refactor, etc.
    status TEXT NOT NULL DEFAULT 'draft', -- draft, planning, approved, in-progress, completed, archived
    job_queue_rel_path TEXT, -- Path to job-queue folder
    planning_rel_path TEXT, -- Path to planning folder
    approved_plan_id INTEGER, -- FK to phase_plans (latest approved plan)
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (approved_plan_id) REFERENCES phase_plans(id) ON DELETE SET NULL,
    UNIQUE (project_id, name)
);

CREATE INDEX idx_phases_project_id ON phases(project_id);
CREATE INDEX idx_phases_status ON phases(status);
CREATE INDEX idx_phases_phase_type ON phases(phase_type);

-- phase_plans: Versioned plans for each phase (with revision tracking)
CREATE TABLE phase_plans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    phase_id INTEGER NOT NULL,
    revision INTEGER NOT NULL DEFAULT 1,
    planning_approach TEXT, -- Approach description
    status TEXT NOT NULL DEFAULT 'draft', -- draft, approved, superseded
    approved_by TEXT,
    approved_at TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (phase_id) REFERENCES phases(id) ON DELETE CASCADE,
    UNIQUE (phase_id, revision)
);

CREATE INDEX idx_phase_plans_phase_id ON phase_plans(phase_id);
CREATE INDEX idx_phase_plans_status ON phase_plans(status);

-- plan_documents: FRD/FRS/GS/TR as rows instead of columns
CREATE TABLE plan_documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    phase_plan_id INTEGER NOT NULL,
    doc_type TEXT NOT NULL, -- frd, frs, gs, tr, task-list, etc.
    doc_name TEXT NOT NULL,
    content TEXT NOT NULL,
    file_path TEXT, -- Relative path to file (e.g., docs/FRD.md)
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (phase_plan_id) REFERENCES phase_plans(id) ON DELETE CASCADE,
    UNIQUE (phase_plan_id, doc_type)
);

CREATE INDEX idx_plan_documents_phase_plan_id ON plan_documents(phase_plan_id);
CREATE INDEX idx_plan_documents_doc_type ON plan_documents(doc_type);

-- ============================================================================
-- STEP 3: Create execution tables (phase_runs, tasks, task_dependencies, task_runs, task_updates)
-- ============================================================================

-- phase_runs: Multiple execution runs per phase (replaces jobs)
CREATE TABLE phase_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    phase_id INTEGER NOT NULL,
    plan_id INTEGER NOT NULL, -- Which plan version was executed
    run_number INTEGER NOT NULL, -- Auto-incremented per phase
    status TEXT NOT NULL DEFAULT 'pending', -- pending, in-progress, completed, failed, cancelled
    assigned_agent TEXT, -- Agent assigned to this run
    started_at TEXT,
    completed_at TEXT,
    duration_seconds INTEGER,
    exit_code INTEGER,
    summary TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (phase_id) REFERENCES phases(id) ON DELETE CASCADE,
    FOREIGN KEY (plan_id) REFERENCES phase_plans(id) ON DELETE CASCADE,
    UNIQUE (phase_id, run_number)
);

CREATE INDEX idx_phase_runs_phase_id ON phase_runs(phase_id);
CREATE INDEX idx_phase_runs_plan_id ON phase_runs(plan_id);
CREATE INDEX idx_phase_runs_status ON phase_runs(status);
CREATE INDEX idx_phase_runs_assigned_agent ON phase_runs(assigned_agent);

-- Trigger to auto-calculate duration
CREATE TRIGGER calc_phase_run_duration
AFTER UPDATE OF completed_at ON phase_runs
WHEN NEW.completed_at IS NOT NULL AND NEW.started_at IS NOT NULL
BEGIN
    UPDATE phase_runs
    SET duration_seconds = CAST((julianday(NEW.completed_at) - julianday(NEW.started_at)) * 86400 AS INTEGER)
    WHERE id = NEW.id;
END;

-- tasks: Enhanced task definitions (linked to phase_plans, not phase_runs)
CREATE TABLE tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    phase_plan_id INTEGER NOT NULL,
    task_key TEXT NOT NULL, -- Hierarchical key (e.g., "2.1a", "3.0b")
    name TEXT NOT NULL,
    description TEXT,
    sub_phase TEXT, -- Phase 1, Phase 2, etc. (within a feature)
    execution_order INTEGER NOT NULL,
    wave INTEGER NOT NULL DEFAULT 1, -- Parallel execution wave
    priority TEXT NOT NULL DEFAULT 'medium', -- low, medium, high, critical
    difficulty TEXT NOT NULL DEFAULT 'medium', -- small, medium, large, xlarge
    status TEXT NOT NULL DEFAULT 'pending', -- pending, in-progress, completed, blocked, skipped
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (phase_plan_id) REFERENCES phase_plans(id) ON DELETE CASCADE,
    UNIQUE (phase_plan_id, task_key)
);

CREATE INDEX idx_tasks_phase_plan_id ON tasks(phase_plan_id);
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_wave ON tasks(wave);
CREATE INDEX idx_tasks_execution_order ON tasks(execution_order);
CREATE INDEX idx_tasks_sub_phase ON tasks(sub_phase);

-- task_dependencies: Explicit dependency tracking (not JSON)
CREATE TABLE task_dependencies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL,
    depends_on_task_id INTEGER NOT NULL,
    dependency_type TEXT NOT NULL DEFAULT 'blocks', -- blocks, related, suggests
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE,
    FOREIGN KEY (depends_on_task_id) REFERENCES tasks(id) ON DELETE CASCADE,
    UNIQUE (task_id, depends_on_task_id)
);

CREATE INDEX idx_task_dependencies_task_id ON task_dependencies(task_id);
CREATE INDEX idx_task_dependencies_depends_on_task_id ON task_dependencies(depends_on_task_id);

-- task_runs: Links phase_runs to tasks (execution tracking)
CREATE TABLE task_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    phase_run_id INTEGER NOT NULL,
    task_id INTEGER NOT NULL,
    assigned_agent TEXT, -- Agent assigned to this specific task execution
    status TEXT NOT NULL DEFAULT 'pending', -- pending, in-progress, completed, failed, skipped
    started_at TEXT,
    completed_at TEXT,
    duration_seconds INTEGER,
    exit_code INTEGER,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (phase_run_id) REFERENCES phase_runs(id) ON DELETE CASCADE,
    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE,
    UNIQUE (phase_run_id, task_id)
);

CREATE INDEX idx_task_runs_phase_run_id ON task_runs(phase_run_id);
CREATE INDEX idx_task_runs_task_id ON task_runs(task_id);
CREATE INDEX idx_task_runs_status ON task_runs(status);
CREATE INDEX idx_task_runs_assigned_agent ON task_runs(assigned_agent);

-- Trigger to auto-calculate task run duration
CREATE TRIGGER calc_task_run_duration
AFTER UPDATE OF completed_at ON task_runs
WHEN NEW.completed_at IS NOT NULL AND NEW.started_at IS NOT NULL
BEGIN
    UPDATE task_runs
    SET duration_seconds = CAST((julianday(NEW.completed_at) - julianday(NEW.started_at)) * 86400 AS INTEGER)
    WHERE id = NEW.id;
END;

-- task_updates: Progress notes during execution
CREATE TABLE task_updates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_run_id INTEGER NOT NULL,
    update_type TEXT NOT NULL, -- progress, blocker, question, solution, note
    content TEXT NOT NULL,
    file_path TEXT, -- Relative path to file (e.g., planning/task-updates/phase-1-stream-b.md)
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (task_run_id) REFERENCES task_runs(id) ON DELETE CASCADE
);

CREATE INDEX idx_task_updates_task_run_id ON task_updates(task_run_id);
CREATE INDEX idx_task_updates_update_type ON task_updates(update_type);

-- ============================================================================
-- STEP 4: Create quality & artifacts tables (quality_gates, run_artifacts, phase_metrics)
-- ============================================================================

-- quality_gates: Build/test/lint validation
CREATE TABLE quality_gates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    phase_run_id INTEGER NOT NULL,
    gate_type TEXT NOT NULL, -- code_review, testing, security, linting, build
    status TEXT NOT NULL DEFAULT 'pending', -- pending, passed, failed, skipped
    result_summary TEXT,
    checked_by TEXT,
    checked_at TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (phase_run_id) REFERENCES phase_runs(id) ON DELETE CASCADE
);

CREATE INDEX idx_quality_gates_phase_run_id ON quality_gates(phase_run_id);
CREATE INDEX idx_quality_gates_gate_type ON quality_gates(gate_type);
CREATE INDEX idx_quality_gates_status ON quality_gates(status);

-- run_artifacts: Store planning artifacts
CREATE TABLE run_artifacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    phase_run_id INTEGER NOT NULL,
    artifact_type TEXT NOT NULL, -- log, report, screenshot, diagram, etc.
    artifact_name TEXT NOT NULL,
    file_path TEXT, -- Relative path to file
    file_size_bytes INTEGER,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (phase_run_id) REFERENCES phase_runs(id) ON DELETE CASCADE
);

CREATE INDEX idx_run_artifacts_phase_run_id ON run_artifacts(phase_run_id);
CREATE INDEX idx_run_artifacts_artifact_type ON run_artifacts(artifact_type);

-- phase_metrics: Aggregated metrics per phase
CREATE TABLE phase_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    phase_id INTEGER NOT NULL,
    total_runs INTEGER NOT NULL DEFAULT 0,
    successful_runs INTEGER NOT NULL DEFAULT 0,
    failed_runs INTEGER NOT NULL DEFAULT 0,
    avg_duration_seconds INTEGER,
    total_tasks INTEGER NOT NULL DEFAULT 0,
    completed_tasks INTEGER NOT NULL DEFAULT 0,
    blocked_tasks INTEGER NOT NULL DEFAULT 0,
    total_quality_gates INTEGER NOT NULL DEFAULT 0,
    passed_quality_gates INTEGER NOT NULL DEFAULT 0,
    last_calculated_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (phase_id) REFERENCES phases(id) ON DELETE CASCADE,
    UNIQUE (phase_id)
);

CREATE INDEX idx_phase_metrics_phase_id ON phase_metrics(phase_id);

-- ============================================================================
-- STEP 5: Update existing tables to link to phase_runs
-- ============================================================================

-- Update code_reviews to link to phase_runs instead of jobs
CREATE TABLE code_reviews_new (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    phase_run_id INTEGER NOT NULL,
    reviewer TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    comments TEXT,
    reviewed_at TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (phase_run_id) REFERENCES phase_runs(id) ON DELETE CASCADE
);

-- Migrate data from old code_reviews (if exists)
-- Note: phase_run_id set to 0 as placeholder - manual migration needed
INSERT INTO code_reviews_new (id, phase_run_id, reviewer, status, comments, reviewed_at, created_at)
SELECT cr.id, 0, cr.reviewer, cr.verdict, cr.summary, cr.created_at, cr.created_at
FROM code_reviews cr
WHERE EXISTS (SELECT 1 FROM sqlite_master WHERE type='table' AND name='code_reviews');

DROP TABLE IF EXISTS code_reviews;
ALTER TABLE code_reviews_new RENAME TO code_reviews;

CREATE INDEX idx_code_reviews_phase_run_id ON code_reviews(phase_run_id);
CREATE INDEX idx_code_reviews_status ON code_reviews(status);

-- Update execution_logs to link to phase_runs instead of jobs
CREATE TABLE execution_logs_new (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    phase_run_id INTEGER NOT NULL,
    log_level TEXT NOT NULL DEFAULT 'INFO',
    message TEXT NOT NULL,
    logged_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (phase_run_id) REFERENCES phase_runs(id) ON DELETE CASCADE
);

-- Migrate data from old execution_logs (if exists)
-- Note: Convert command execution logs to simple INFO messages
INSERT INTO execution_logs_new (id, phase_run_id, log_level, message, logged_at)
SELECT el.id, 0, 'INFO',
       'Command: ' || el.command || ' (exit=' || COALESCE(el.exit_code, 'null') || ')',
       el.executed_at
FROM execution_logs el
WHERE EXISTS (SELECT 1 FROM sqlite_master WHERE type='table' AND name='execution_logs');

DROP TABLE IF EXISTS execution_logs;
ALTER TABLE execution_logs_new RENAME TO execution_logs;

CREATE INDEX idx_execution_logs_phase_run_id ON execution_logs(phase_run_id);
CREATE INDEX idx_execution_logs_log_level ON execution_logs(log_level);

-- Update agent_assignments to link to phase_runs instead of jobs
CREATE TABLE agent_assignments_new (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    phase_run_id INTEGER NOT NULL,
    agent_name TEXT NOT NULL,
    role TEXT NOT NULL,
    assigned_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (phase_run_id) REFERENCES phase_runs(id) ON DELETE CASCADE
);

-- Migrate data from old agent_assignments (if exists)
-- Note: Use agent_type as both agent_name and role
INSERT INTO agent_assignments_new (id, phase_run_id, agent_name, role, assigned_at)
SELECT aa.id, 0, aa.agent_type, aa.agent_type, aa.assigned_at
FROM agent_assignments aa
WHERE EXISTS (SELECT 1 FROM sqlite_master WHERE type='table' AND name='agent_assignments');

DROP TABLE IF EXISTS agent_assignments;
ALTER TABLE agent_assignments_new RENAME TO agent_assignments;

CREATE INDEX idx_agent_assignments_phase_run_id ON agent_assignments(phase_run_id);
CREATE INDEX idx_agent_assignments_agent_name ON agent_assignments(agent_name);

-- ============================================================================
-- STEP 6: Migrate existing data (specs → phases → phase_plans → plan_documents)
-- ============================================================================

-- Migrate specs to phases
INSERT INTO phases (id, project_id, name, description, phase_type, status, created_at, updated_at)
SELECT id, project_id, name, NULL, 'feature', status, created_at, updated_at
FROM specs_legacy;

-- Migrate specs to phase_plans (create initial plan for each phase)
INSERT INTO phase_plans (id, phase_id, revision, planning_approach, status, approved_by, approved_at, created_at)
SELECT id, id, 1, 'Initial plan from legacy spec', 'approved', 'system', created_at, created_at
FROM specs_legacy;

-- Update phases to point to their approved plans
UPDATE phases
SET approved_plan_id = id
WHERE id IN (SELECT id FROM phase_plans);

-- Migrate FRD/FRS/GS/TR to plan_documents
INSERT INTO plan_documents (phase_plan_id, doc_type, doc_name, content, created_at, updated_at)
SELECT id, 'frd', 'Functional Requirements Document', frd_content, created_at, updated_at
FROM specs_legacy WHERE frd_content IS NOT NULL AND frd_content != '';

INSERT INTO plan_documents (phase_plan_id, doc_type, doc_name, content, created_at, updated_at)
SELECT id, 'frs', 'Functional Requirements Specification', frs_content, created_at, updated_at
FROM specs_legacy WHERE frs_content IS NOT NULL AND frs_content != '';

INSERT INTO plan_documents (phase_plan_id, doc_type, doc_name, content, created_at, updated_at)
SELECT id, 'gs', 'Getting Started Guide', gs_content, created_at, updated_at
FROM specs_legacy WHERE gs_content IS NOT NULL AND gs_content != '';

INSERT INTO plan_documents (phase_plan_id, doc_type, doc_name, content, created_at, updated_at)
SELECT id, 'tr', 'Test Report', tr_content, created_at, updated_at
FROM specs_legacy WHERE tr_content IS NOT NULL AND tr_content != '';

INSERT INTO plan_documents (phase_plan_id, doc_type, doc_name, content, created_at, updated_at)
SELECT id, 'task-list', 'Task List', task_list_content, created_at, updated_at
FROM specs_legacy WHERE task_list_content IS NOT NULL AND task_list_content != '';

-- ============================================================================
-- STEP 7: Update schema version to 4
-- ============================================================================

INSERT INTO schema_version (version, description)
VALUES (4, 'PM-DB v2: Phase-based execution tracking with versioned plans');

COMMIT;
