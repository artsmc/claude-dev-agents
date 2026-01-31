-- Migration 006: Agent Context Caching System
-- Created: 2026-01-31
-- Description: Add tables for caching agent context (Documentation Hub files, checklist progress,
--              quality gate results) to reduce token usage and enable session resumption.
-- Dependencies: Requires PM-DB v2 schema (005_cleanup_legacy.sql)
-- References: /planning/agent-context-caching/docs/TR.md

-- ============================================================================
-- TABLE 1: cached_files
-- Purpose: Store file content cache with SHA-256 hash for invalidation
-- ============================================================================

CREATE TABLE IF NOT EXISTS cached_files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_path TEXT NOT NULL UNIQUE,        -- Relative path from project root (e.g., "cline-docs/systemArchitecture.md")
    content_hash TEXT NOT NULL,            -- SHA-256 hex string (64 chars)
    content TEXT NOT NULL,                 -- File content (UTF-8 text)
    file_size_bytes INTEGER NOT NULL,      -- File size in bytes
    file_type TEXT NOT NULL DEFAULT 'markdown', -- markdown, text, json
    cache_priority TEXT NOT NULL DEFAULT 'normal', -- high, normal, low
    access_count INTEGER NOT NULL DEFAULT 0,      -- Total accesses
    hit_count INTEGER NOT NULL DEFAULT 0,         -- Cache hits
    miss_count INTEGER NOT NULL DEFAULT 1,        -- Cache misses (starts at 1 on creation)
    last_accessed TEXT,                    -- Last access timestamp
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_cached_files_file_path ON cached_files(file_path);
CREATE INDEX IF NOT EXISTS idx_cached_files_content_hash ON cached_files(content_hash);
CREATE INDEX IF NOT EXISTS idx_cached_files_priority ON cached_files(cache_priority);
CREATE INDEX IF NOT EXISTS idx_cached_files_last_accessed ON cached_files(last_accessed);

-- ============================================================================
-- TABLE 2: agent_invocations
-- Purpose: Track every agent invocation with context and metrics
-- ============================================================================

CREATE TABLE IF NOT EXISTS agent_invocations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_name TEXT NOT NULL,              -- e.g., 'nextjs-backend-developer', 'technical-writer'
    phase_run_id INTEGER,                  -- FK to phase_runs (optional)
    task_run_id INTEGER,                   -- FK to task_runs (optional)
    purpose TEXT NOT NULL,                 -- planning, implementation, review, testing, documentation
    parent_invocation_id INTEGER,          -- For nested invocations (agent spawns sub-agent)
    status TEXT NOT NULL DEFAULT 'in-progress', -- in-progress, completed, failed, cancelled
    checklist_id INTEGER,                  -- FK to checklists
    total_files_read INTEGER NOT NULL DEFAULT 0,
    cache_hits INTEGER NOT NULL DEFAULT 0,
    cache_misses INTEGER NOT NULL DEFAULT 0,
    estimated_tokens_used INTEGER NOT NULL DEFAULT 0,
    started_at TEXT NOT NULL DEFAULT (datetime('now')),
    completed_at TEXT,
    duration_seconds INTEGER,
    error_message TEXT,
    summary TEXT,
    metadata TEXT,                         -- JSON for additional context
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (phase_run_id) REFERENCES phase_runs(id) ON DELETE CASCADE,
    FOREIGN KEY (task_run_id) REFERENCES task_runs(id) ON DELETE CASCADE,
    FOREIGN KEY (parent_invocation_id) REFERENCES agent_invocations(id) ON DELETE SET NULL,
    FOREIGN KEY (checklist_id) REFERENCES checklists(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_agent_invocations_agent_name ON agent_invocations(agent_name);
CREATE INDEX IF NOT EXISTS idx_agent_invocations_phase_run_id ON agent_invocations(phase_run_id);
CREATE INDEX IF NOT EXISTS idx_agent_invocations_task_run_id ON agent_invocations(task_run_id);
CREATE INDEX IF NOT EXISTS idx_agent_invocations_status ON agent_invocations(status);
CREATE INDEX IF NOT EXISTS idx_agent_invocations_started_at ON agent_invocations(started_at);

-- Trigger to auto-calculate invocation duration
CREATE TRIGGER IF NOT EXISTS calc_agent_invocation_duration
AFTER UPDATE OF completed_at ON agent_invocations
WHEN NEW.completed_at IS NOT NULL AND NEW.started_at IS NOT NULL
BEGIN
    UPDATE agent_invocations
    SET duration_seconds = CAST((julianday(NEW.completed_at) - julianday(NEW.started_at)) * 86400 AS INTEGER)
    WHERE id = NEW.id;
END;

-- ============================================================================
-- TABLE 3: agent_file_reads
-- Purpose: Log every file read by agents for detailed analytics
-- ============================================================================

CREATE TABLE IF NOT EXISTS agent_file_reads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    invocation_id INTEGER NOT NULL,        -- FK to agent_invocations
    file_path TEXT NOT NULL,               -- File that was read
    cache_status TEXT NOT NULL,            -- hit, miss, error
    file_size_bytes INTEGER NOT NULL,
    estimated_tokens INTEGER NOT NULL,     -- file_size_bytes ÷ 4 (rough estimate)
    read_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (invocation_id) REFERENCES agent_invocations(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_agent_file_reads_invocation_id ON agent_file_reads(invocation_id);
CREATE INDEX IF NOT EXISTS idx_agent_file_reads_file_path ON agent_file_reads(file_path);
CREATE INDEX IF NOT EXISTS idx_agent_file_reads_cache_status ON agent_file_reads(cache_status);

-- ============================================================================
-- TABLE 4: checklists
-- Purpose: Store agent checklist definitions and progress
-- ============================================================================

CREATE TABLE IF NOT EXISTS checklists (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    invocation_id INTEGER NOT NULL,        -- FK to agent_invocations
    template_name TEXT,                    -- FK to checklist_templates (optional)
    template_version INTEGER,              -- Version of template used
    checklist_name TEXT NOT NULL,
    total_items INTEGER NOT NULL,
    completed_items INTEGER NOT NULL DEFAULT 0,
    failed_items INTEGER NOT NULL DEFAULT 0,
    skipped_items INTEGER NOT NULL DEFAULT 0,
    completion_percent REAL NOT NULL DEFAULT 0.0,
    status TEXT NOT NULL DEFAULT 'in-progress', -- in-progress, completed, partial, failed
    started_at TEXT NOT NULL DEFAULT (datetime('now')),
    completed_at TEXT,
    duration_seconds INTEGER,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (invocation_id) REFERENCES agent_invocations(id) ON DELETE CASCADE,
    FOREIGN KEY (template_name, template_version) REFERENCES checklist_templates(name, version) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_checklists_invocation_id ON checklists(invocation_id);
CREATE INDEX IF NOT EXISTS idx_checklists_template_name ON checklists(template_name);
CREATE INDEX IF NOT EXISTS idx_checklists_status ON checklists(status);

-- Trigger to auto-calculate checklist duration
CREATE TRIGGER IF NOT EXISTS calc_checklist_duration
AFTER UPDATE OF completed_at ON checklists
WHEN NEW.completed_at IS NOT NULL AND NEW.started_at IS NOT NULL
BEGIN
    UPDATE checklists
    SET duration_seconds = CAST((julianday(NEW.completed_at) - julianday(NEW.started_at)) * 86400 AS INTEGER)
    WHERE id = NEW.id;
END;

-- ============================================================================
-- TABLE 5: checklist_items
-- Purpose: Store individual checklist items with status and verification
-- ============================================================================

CREATE TABLE IF NOT EXISTS checklist_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    checklist_id INTEGER NOT NULL,         -- FK to checklists
    item_order INTEGER NOT NULL,           -- Display order (1, 2, 3, ...)
    item_key TEXT,                         -- Unique key within checklist (e.g., "SEC-01")
    description TEXT NOT NULL,
    category TEXT,                         -- security, performance, functionality, documentation, etc.
    status TEXT NOT NULL DEFAULT 'pending', -- pending, in-progress, completed, failed, skipped
    priority TEXT NOT NULL DEFAULT 'medium', -- low, medium, high, critical
    verification_type TEXT NOT NULL DEFAULT 'manual', -- manual, automated, tool-based
    notes TEXT,                            -- Agent notes for this item
    started_at TEXT,
    completed_at TEXT,
    duration_seconds INTEGER,
    metadata TEXT,                         -- JSON for additional context
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (checklist_id) REFERENCES checklists(id) ON DELETE CASCADE,
    UNIQUE (checklist_id, item_order)
);

CREATE INDEX IF NOT EXISTS idx_checklist_items_checklist_id ON checklist_items(checklist_id);
CREATE INDEX IF NOT EXISTS idx_checklist_items_status ON checklist_items(status);
CREATE INDEX IF NOT EXISTS idx_checklist_items_category ON checklist_items(category);

-- Trigger to auto-calculate item duration
CREATE TRIGGER IF NOT EXISTS calc_checklist_item_duration
AFTER UPDATE OF completed_at ON checklist_items
WHEN NEW.completed_at IS NOT NULL AND NEW.started_at IS NOT NULL
BEGIN
    UPDATE checklist_items
    SET duration_seconds = CAST((julianday(NEW.completed_at) - julianday(NEW.started_at)) * 86400 AS INTEGER)
    WHERE id = NEW.id;
END;

-- Trigger to update checklist completion percentage
CREATE TRIGGER IF NOT EXISTS update_checklist_progress
AFTER UPDATE OF status ON checklist_items
BEGIN
    UPDATE checklists
    SET
        completed_items = (SELECT COUNT(*) FROM checklist_items WHERE checklist_id = NEW.checklist_id AND status = 'completed'),
        failed_items = (SELECT COUNT(*) FROM checklist_items WHERE checklist_id = NEW.checklist_id AND status = 'failed'),
        skipped_items = (SELECT COUNT(*) FROM checklist_items WHERE checklist_id = NEW.checklist_id AND status = 'skipped'),
        completion_percent = (CAST((SELECT COUNT(*) FROM checklist_items WHERE checklist_id = NEW.checklist_id AND status = 'completed') AS REAL) / total_items) * 100.0
    WHERE id = NEW.checklist_id;
END;

-- ============================================================================
-- TABLE 6: checklist_verifications
-- Purpose: Store verification outcomes for quality trend analysis
-- ============================================================================

CREATE TABLE IF NOT EXISTS checklist_verifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    checklist_item_id INTEGER NOT NULL,    -- FK to checklist_items
    quality_gate_id INTEGER,               -- FK to quality_gates (optional)
    result TEXT NOT NULL,                  -- passed, failed, warning, skipped
    verification_method TEXT NOT NULL,     -- manual, automated, tool-based
    verified_by TEXT NOT NULL,             -- agent name or user
    evidence_text TEXT,                    -- Test output, review notes
    evidence_file_path TEXT,               -- Path to screenshot, log file
    verified_at TEXT NOT NULL DEFAULT (datetime('now')),
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (checklist_item_id) REFERENCES checklist_items(id) ON DELETE CASCADE,
    FOREIGN KEY (quality_gate_id) REFERENCES quality_gates(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_checklist_verifications_item_id ON checklist_verifications(checklist_item_id);
CREATE INDEX IF NOT EXISTS idx_checklist_verifications_quality_gate_id ON checklist_verifications(quality_gate_id);
CREATE INDEX IF NOT EXISTS idx_checklist_verifications_result ON checklist_verifications(result);
CREATE INDEX IF NOT EXISTS idx_checklist_verifications_verified_at ON checklist_verifications(verified_at);

-- ============================================================================
-- TABLE 7: checklist_templates
-- Purpose: Store reusable checklist templates for common workflows
-- ============================================================================

CREATE TABLE IF NOT EXISTS checklist_templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,                    -- e.g., 'code-review-checklist'
    version INTEGER NOT NULL DEFAULT 1,
    agent_type TEXT NOT NULL,              -- e.g., 'code-reviewer', 'technical-writer'
    description TEXT,
    items TEXT NOT NULL,                   -- JSON array of template items
    total_items INTEGER NOT NULL,
    is_active INTEGER NOT NULL DEFAULT 1,  -- 0 = archived, 1 = active
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE (name, version)
);

CREATE INDEX IF NOT EXISTS idx_checklist_templates_name ON checklist_templates(name);
CREATE INDEX IF NOT EXISTS idx_checklist_templates_agent_type ON checklist_templates(agent_type);
CREATE INDEX IF NOT EXISTS idx_checklist_templates_is_active ON checklist_templates(is_active);

-- ============================================================================
-- TABLE 8: cache_statistics
-- Purpose: Store aggregate cache statistics for reporting
-- ============================================================================

CREATE TABLE IF NOT EXISTS cache_statistics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stat_date TEXT NOT NULL,               -- Date of statistics (YYYY-MM-DD)
    file_path TEXT,                        -- NULL for global stats, file path for per-file stats
    total_reads INTEGER NOT NULL DEFAULT 0,
    cache_hits INTEGER NOT NULL DEFAULT 0,
    cache_misses INTEGER NOT NULL DEFAULT 0,
    hit_rate_percent REAL NOT NULL DEFAULT 0.0,
    tokens_saved INTEGER NOT NULL DEFAULT 0,
    avg_lookup_time_ms REAL NOT NULL DEFAULT 0.0,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE (stat_date, file_path)
);

CREATE INDEX IF NOT EXISTS idx_cache_statistics_stat_date ON cache_statistics(stat_date);
CREATE INDEX IF NOT EXISTS idx_cache_statistics_file_path ON cache_statistics(file_path);

-- ============================================================================
-- SCHEMA VERSION UPDATE
-- ============================================================================

INSERT INTO schema_version (version, description)
VALUES (6, 'Agent Context Caching System - Add tables for file caching, agent invocations, checklists, and cache statistics');

-- ============================================================================
-- MIGRATION COMPLETE
-- ============================================================================
-- Tables Added: 8
-- Indexes Added: 31
-- Triggers Added: 4
-- Schema Version: 6
-- Estimated execution time: < 5 seconds
-- Breaking changes: None (all additions)
-- ============================================================================
