-- Migration 001: Initial Schema
-- Creates core tables: projects, specs, jobs, tasks
-- Includes filesystem_path in projects table for Memory Bank exports

BEGIN TRANSACTION;

-- ==================== PROJECTS TABLE ====================

CREATE TABLE projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    filesystem_path TEXT NOT NULL,  -- Absolute path to project folder for Memory Bank exports
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX idx_projects_name ON projects(name);
CREATE INDEX idx_projects_created_at ON projects(created_at);

-- ==================== SPECS TABLE ====================

CREATE TABLE specs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'draft',  -- draft, approved, in-progress, completed
    frd_content TEXT,
    frs_content TEXT,
    gs_content TEXT,
    tr_content TEXT,
    task_list_content TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    UNIQUE(project_id, name)
);

CREATE INDEX idx_specs_project_id ON specs(project_id);
CREATE INDEX idx_specs_status ON specs(status);
CREATE INDEX idx_specs_name ON specs(name);

-- ==================== JOBS TABLE ====================

CREATE TABLE jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    spec_id INTEGER,
    name TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',  -- pending, in-progress, completed, failed, blocked
    priority TEXT NOT NULL DEFAULT 'normal',  -- low, normal, high, critical
    assigned_agent TEXT,
    exit_code INTEGER,
    summary TEXT,
    session_id TEXT,
    last_activity_at TEXT,
    resume_count INTEGER DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    started_at TEXT,
    completed_at TEXT,
    duration_seconds INTEGER,
    FOREIGN KEY (spec_id) REFERENCES specs(id) ON DELETE SET NULL
);

CREATE INDEX idx_jobs_spec_id ON jobs(spec_id);
CREATE INDEX idx_jobs_status ON jobs(status);
CREATE INDEX idx_jobs_priority ON jobs(priority);
CREATE INDEX idx_jobs_session_id ON jobs(session_id);
CREATE INDEX idx_jobs_created_at ON jobs(created_at);

-- Trigger to calculate job duration
CREATE TRIGGER jobs_duration_trigger
AFTER UPDATE OF completed_at ON jobs
WHEN NEW.completed_at IS NOT NULL AND NEW.started_at IS NOT NULL
BEGIN
    UPDATE jobs
    SET duration_seconds = CAST((julianday(NEW.completed_at) - julianday(NEW.started_at)) * 86400 AS INTEGER)
    WHERE id = NEW.id;
END;

-- ==================== TASKS TABLE ====================

CREATE TABLE tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',  -- pending, in-progress, completed, failed, blocked
    `order` INTEGER DEFAULT 0,
    dependencies TEXT,  -- JSON array of task IDs this depends on
    exit_code INTEGER,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    started_at TEXT,
    completed_at TEXT,
    duration_seconds INTEGER,
    FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE
);

CREATE INDEX idx_tasks_job_id ON tasks(job_id);
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_order ON tasks(`order`);

-- Trigger to calculate task duration
CREATE TRIGGER tasks_duration_trigger
AFTER UPDATE OF completed_at ON tasks
WHEN NEW.completed_at IS NOT NULL AND NEW.started_at IS NOT NULL
BEGIN
    UPDATE tasks
    SET duration_seconds = CAST((julianday(NEW.completed_at) - julianday(NEW.started_at)) * 86400 AS INTEGER)
    WHERE id = NEW.id;
END;

-- ==================== SCHEMA VERSION ====================

CREATE TABLE schema_version (
    version INTEGER PRIMARY KEY,
    applied_at TEXT NOT NULL DEFAULT (datetime('now')),
    description TEXT
);

INSERT INTO schema_version (version, description)
VALUES (1, 'Initial schema: projects, specs, jobs, tasks');

COMMIT;
