-- Migration 005: Cleanup Legacy Tables
-- Drops all *_legacy tables created during PM-DB v2 migration
-- Run this after verifying that migration 004 completed successfully

BEGIN TRANSACTION;

-- Drop legacy tables (preserved during migration 004 for reference)
DROP TABLE IF EXISTS specs_legacy;
DROP TABLE IF EXISTS jobs_legacy;
DROP TABLE IF EXISTS tasks_legacy;

-- Update schema version to 5
INSERT INTO schema_version (version, description)
VALUES (5, 'Cleanup: Removed legacy tables from PM-DB v2 migration');

COMMIT;
