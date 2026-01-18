-- Migration 002: Add Code Reviews Table
-- Adds code_reviews table to track review summaries, verdicts, and issues

BEGIN TRANSACTION;

-- ==================== CODE REVIEWS TABLE ====================

CREATE TABLE code_reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id INTEGER,
    task_id INTEGER,
    reviewer TEXT NOT NULL,  -- Reviewer name or agent type
    summary TEXT NOT NULL,   -- Review summary text
    verdict TEXT NOT NULL,   -- approved, changes-requested, rejected
    issues_found TEXT,       -- JSON array of issues
    files_reviewed TEXT,     -- JSON array of files
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE,
    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE
);

CREATE INDEX idx_code_reviews_job_id ON code_reviews(job_id);
CREATE INDEX idx_code_reviews_task_id ON code_reviews(task_id);
CREATE INDEX idx_code_reviews_reviewer ON code_reviews(reviewer);
CREATE INDEX idx_code_reviews_verdict ON code_reviews(verdict);
CREATE INDEX idx_code_reviews_created_at ON code_reviews(created_at);

-- ==================== UPDATE SCHEMA VERSION ====================

INSERT INTO schema_version (version, description)
VALUES (2, 'Add code_reviews table for tracking code review results');

COMMIT;
