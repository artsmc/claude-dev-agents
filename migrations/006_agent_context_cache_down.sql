-- Migration 006 ROLLBACK: Agent Context Caching System
-- Created: 2026-01-31
-- Description: Rollback Agent Context Caching System tables
-- WARNING: This will delete ALL cached data, agent invocation history, and checklist progress
-- References: /planning/agent-context-caching/docs/TR.md

-- ============================================================================
-- PRE-ROLLBACK VALIDATION
-- ============================================================================
-- Before running this rollback, ensure:
-- 1. You have a backup of projects.db
-- 2. You have exported any needed analytics data
-- 3. You understand that all cached context will be lost
-- 4. No agents are currently running (status = 'in-progress')

-- ============================================================================
-- DROP TRIGGERS (Must drop before tables)
-- ============================================================================

DROP TRIGGER IF EXISTS update_checklist_progress;
DROP TRIGGER IF EXISTS calc_checklist_item_duration;
DROP TRIGGER IF EXISTS calc_checklist_duration;
DROP TRIGGER IF EXISTS calc_agent_invocation_duration;

-- ============================================================================
-- DROP TABLES (In reverse dependency order)
-- ============================================================================

-- Drop tables that depend on other caching tables first
DROP TABLE IF EXISTS cache_statistics;
DROP TABLE IF EXISTS checklist_templates;
DROP TABLE IF EXISTS checklist_verifications;
DROP TABLE IF EXISTS checklist_items;
DROP TABLE IF EXISTS checklists;
DROP TABLE IF EXISTS agent_file_reads;
DROP TABLE IF EXISTS agent_invocations;
DROP TABLE IF EXISTS cached_files;

-- ============================================================================
-- REMOVE SCHEMA VERSION ENTRY
-- ============================================================================

DELETE FROM schema_version WHERE version = 6;

-- ============================================================================
-- POST-ROLLBACK VERIFICATION
-- ============================================================================
-- After rollback completes, verify:
-- 1. All 8 tables removed: SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%cached%' OR name LIKE '%agent_%' OR name LIKE '%checklist%';
-- 2. All 4 triggers removed: SELECT name FROM sqlite_master WHERE type='trigger' AND name LIKE '%agent%' OR name LIKE '%checklist%' OR name LIKE '%cache%';
-- 3. Schema version reverted: SELECT * FROM schema_version WHERE version = 6; (should return 0 rows)
-- 4. PM-DB v2 tables intact: SELECT COUNT(*) FROM phase_runs; (should work)

-- ============================================================================
-- MIGRATION ROLLBACK COMPLETE
-- ============================================================================
-- Tables Dropped: 8
-- Indexes Dropped: 31 (auto-dropped with tables)
-- Triggers Dropped: 4
-- Schema Version: Reverted to 5
-- Data Loss: ALL agent context cache, invocation history, and checklists
-- Estimated execution time: < 2 seconds
-- ============================================================================
