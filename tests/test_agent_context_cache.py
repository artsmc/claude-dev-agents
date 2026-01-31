"""
Unit tests for Agent Context Caching System in ProjectDatabase.

Tests file caching, agent invocation tracking, checklist management,
verifications, templates, and statistics.

Zero external dependencies - uses only Python standard library (unittest, tempfile).
"""

import unittest
import tempfile
import os
from pathlib import Path
import sys
import json
from datetime import datetime

# Add parent directory to path to import project_database
sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.project_database import ProjectDatabase


class TestFileCaching(unittest.TestCase):
    """Test file caching functionality."""

    def setUp(self):
        """Create temporary database for each test."""
        self.temp_db = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.db')
        self.temp_db.close()
        self.db = ProjectDatabase(self.temp_db.name)

        # Create schema_version table (required by migration)
        self.db.conn.execute("""
            CREATE TABLE IF NOT EXISTS schema_version (
                version INTEGER PRIMARY KEY,
                description TEXT NOT NULL,
                applied_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
        """)
        self.db.conn.commit()

        # Apply migration 006
        migration_path = Path(__file__).parent.parent / 'migrations' / '006_agent_context_cache.sql'
        with open(migration_path, 'r') as f:
            migration_sql = f.read()
        self.db.conn.executescript(migration_sql)
        self.db.conn.commit()

    def tearDown(self):
        """Clean up temporary database."""
        self.db.close()
        os.unlink(self.temp_db.name)

    def test_calculate_file_hash(self):
        """Test SHA-256 hash calculation."""
        content = "# Test Content\n\nHello World!"
        hash1 = self.db.calculate_file_hash(content)

        # Should be 64-character hex string
        self.assertEqual(len(hash1), 64)
        self.assertTrue(all(c in '0123456789abcdef' for c in hash1))

        # Same content should produce same hash
        hash2 = self.db.calculate_file_hash(content)
        self.assertEqual(hash1, hash2)

        # Different content should produce different hash
        hash3 = self.db.calculate_file_hash(content + " extra")
        self.assertNotEqual(hash1, hash3)

    def test_cache_file_new(self):
        """Test caching a new file."""
        file_id = self.db.cache_file(
            file_path='cline-docs/systemArchitecture.md',
            content='# System Architecture\n\nTest content',
            file_type='markdown',
            cache_priority='high'
        )

        self.assertIsNotNone(file_id)
        self.assertGreater(file_id, 0)

        # Verify file was cached
        cached = self.db.get_cached_file('cline-docs/systemArchitecture.md')
        self.assertIsNotNone(cached)
        self.assertEqual(cached['file_path'], 'cline-docs/systemArchitecture.md')
        self.assertEqual(cached['file_type'], 'markdown')
        self.assertEqual(cached['cache_priority'], 'high')
        self.assertEqual(cached['access_count'], 1)  # get_cached_file increments access
        self.assertEqual(cached['hit_count'], 1)
        self.assertEqual(cached['miss_count'], 1)  # Initial cache is a miss

    def test_cache_file_update_same_content(self):
        """Test caching file with same content updates priority only."""
        content = '# Test\n\nContent'

        # Cache with normal priority
        file_id1 = self.db.cache_file(
            file_path='test.md',
            content=content,
            cache_priority='normal'
        )

        # Cache again with high priority (same content)
        file_id2 = self.db.cache_file(
            file_path='test.md',
            content=content,
            cache_priority='high'
        )

        # Should return same file ID
        self.assertEqual(file_id1, file_id2)

        # Priority should be updated
        cached = self.db.get_cached_file('test.md')
        self.assertEqual(cached['cache_priority'], 'high')
        self.assertEqual(cached['miss_count'], 1)  # Should not increment miss count

    def test_cache_file_update_changed_content(self):
        """Test caching file with changed content updates cache."""
        # Cache initial content
        file_id1 = self.db.cache_file(
            file_path='test.md',
            content='Original content'
        )

        # Cache changed content
        file_id2 = self.db.cache_file(
            file_path='test.md',
            content='Changed content'
        )

        # Should return same file ID
        self.assertEqual(file_id1, file_id2)

        # Content should be updated
        cached = self.db.get_cached_file('test.md')
        self.assertEqual(cached['content'], 'Changed content')
        self.assertEqual(cached['miss_count'], 2)  # Content change counts as miss

    def test_get_cached_file_not_found(self):
        """Test getting non-existent cached file returns None."""
        result = self.db.get_cached_file('nonexistent.md')
        self.assertIsNone(result)

    def test_get_cached_file_updates_stats(self):
        """Test that get_cached_file updates access statistics."""
        # Cache a file
        self.db.cache_file('test.md', 'content')

        # Get it multiple times
        self.db.get_cached_file('test.md')  # access_count=1, hit_count=1
        self.db.get_cached_file('test.md')  # access_count=2, hit_count=2
        cached = self.db.get_cached_file('test.md')  # access_count=3, hit_count=3

        self.assertEqual(cached['access_count'], 3)
        self.assertEqual(cached['hit_count'], 3)
        self.assertIsNotNone(cached['last_accessed'])

    def test_invalidate_cache(self):
        """Test cache invalidation."""
        # Cache a file
        self.db.cache_file('test.md', 'content')

        # Verify it exists
        self.assertIsNotNone(self.db.get_cached_file('test.md'))

        # Invalidate
        self.db.invalidate_cache('test.md')

        # Verify it's gone
        self.assertIsNone(self.db.get_cached_file('test.md'))

    def test_update_file_access_hit(self):
        """Test updating file access stats with cache hit."""
        self.db.cache_file('test.md', 'content')

        # Manually update access stats
        self.db.update_file_access('test.md', cache_hit=True)

        cached = self.db.get_cached_file('test.md')
        # Note: get_cached_file also increments stats, so we have:
        # - Initial cache: access=0, hit=0, miss=1
        # - update_file_access(hit): access=1, hit=1, miss=1
        # - get_cached_file: access=2, hit=2, miss=1
        self.assertEqual(cached['access_count'], 2)
        self.assertEqual(cached['hit_count'], 2)
        self.assertEqual(cached['miss_count'], 1)

    def test_update_file_access_miss(self):
        """Test updating file access stats with cache miss."""
        self.db.cache_file('test.md', 'content')

        # Manually update access stats with miss
        self.db.update_file_access('test.md', cache_hit=False)

        cached = self.db.get_cached_file('test.md')
        # Initial: access=0, hit=0, miss=1
        # update_file_access(miss): access=1, hit=0, miss=2
        # get_cached_file: access=2, hit=1, miss=2
        self.assertEqual(cached['access_count'], 2)
        self.assertEqual(cached['hit_count'], 1)
        self.assertEqual(cached['miss_count'], 2)


class TestAgentInvocationTracking(unittest.TestCase):
    """Test agent invocation tracking."""

    def setUp(self):
        """Create temporary database for each test."""
        self.temp_db = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.db')
        self.temp_db.close()
        self.db = ProjectDatabase(self.temp_db.name)

        # Create schema_version table (required by migration)
        self.db.conn.execute("""
            CREATE TABLE IF NOT EXISTS schema_version (
                version INTEGER PRIMARY KEY,
                description TEXT NOT NULL,
                applied_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
        """)

        # Create stub FK tables (phase_runs, task_runs) for agent_invocations
        self.db.conn.execute("""
            CREATE TABLE IF NOT EXISTS phase_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                phase_id INTEGER NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending'
            )
        """)
        self.db.conn.execute("""
            CREATE TABLE IF NOT EXISTS task_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                phase_run_id INTEGER NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending'
            )
        """)
        self.db.conn.commit()

        # Apply migration 006
        migration_path = Path(__file__).parent.parent / 'migrations' / '006_agent_context_cache.sql'
        with open(migration_path, 'r') as f:
            migration_sql = f.read()
        self.db.conn.executescript(migration_sql)
        self.db.conn.commit()

    def tearDown(self):
        """Clean up temporary database."""
        self.db.close()
        os.unlink(self.temp_db.name)

    def test_create_agent_invocation(self):
        """Test creating agent invocation."""
        invocation_id = self.db.create_agent_invocation(
            agent_name='technical-writer',
            purpose='documentation',
            metadata={'task': 'Update FRD'}
        )

        self.assertIsNotNone(invocation_id)
        self.assertGreater(invocation_id, 0)

        # Verify invocation was created
        invocation = self.db.get_agent_invocation(invocation_id)
        self.assertIsNotNone(invocation)
        self.assertEqual(invocation['agent_name'], 'technical-writer')
        self.assertEqual(invocation['purpose'], 'documentation')
        self.assertEqual(invocation['status'], 'in-progress')
        self.assertEqual(invocation['total_files_read'], 0)
        self.assertEqual(invocation['cache_hits'], 0)
        self.assertEqual(invocation['cache_misses'], 0)
        self.assertIsNotNone(invocation['started_at'])
        self.assertIsNone(invocation['completed_at'])

    def test_complete_agent_invocation_success(self):
        """Test completing agent invocation successfully."""
        invocation_id = self.db.create_agent_invocation(
            agent_name='test-agent',
            purpose='testing'
        )

        self.db.complete_agent_invocation(
            invocation_id,
            status='completed',
            summary='All tasks completed successfully'
        )

        invocation = self.db.get_agent_invocation(invocation_id)
        self.assertEqual(invocation['status'], 'completed')
        self.assertEqual(invocation['summary'], 'All tasks completed successfully')
        self.assertIsNotNone(invocation['completed_at'])
        self.assertIsNotNone(invocation['duration_seconds'])  # Trigger should calculate

    def test_complete_agent_invocation_failed(self):
        """Test completing agent invocation with failure."""
        invocation_id = self.db.create_agent_invocation(
            agent_name='test-agent',
            purpose='testing'
        )

        self.db.complete_agent_invocation(
            invocation_id,
            status='failed',
            error_message='Connection timeout'
        )

        invocation = self.db.get_agent_invocation(invocation_id)
        self.assertEqual(invocation['status'], 'failed')
        self.assertEqual(invocation['error_message'], 'Connection timeout')

    def test_list_agent_invocations_no_filter(self):
        """Test listing all agent invocations."""
        # Create multiple invocations
        self.db.create_agent_invocation('agent-1', 'planning')
        self.db.create_agent_invocation('agent-2', 'implementation')
        self.db.create_agent_invocation('agent-1', 'review')

        invocations = self.db.list_agent_invocations()
        self.assertEqual(len(invocations), 3)

    def test_list_agent_invocations_by_name(self):
        """Test filtering invocations by agent name."""
        self.db.create_agent_invocation('agent-1', 'planning')
        self.db.create_agent_invocation('agent-2', 'implementation')
        self.db.create_agent_invocation('agent-1', 'review')

        invocations = self.db.list_agent_invocations(agent_name='agent-1')
        self.assertEqual(len(invocations), 2)
        self.assertTrue(all(i['agent_name'] == 'agent-1' for i in invocations))

    def test_list_agent_invocations_by_status(self):
        """Test filtering invocations by status."""
        inv1 = self.db.create_agent_invocation('agent-1', 'planning')
        inv2 = self.db.create_agent_invocation('agent-2', 'implementation')

        self.db.complete_agent_invocation(inv1, 'completed')

        # Get only in-progress
        invocations = self.db.list_agent_invocations(status='in-progress')
        self.assertEqual(len(invocations), 1)
        self.assertEqual(invocations[0]['id'], inv2)

    def test_log_file_read_hit(self):
        """Test logging file read with cache hit."""
        invocation_id = self.db.create_agent_invocation('test-agent', 'testing')

        file_read_id = self.db.log_file_read(
            invocation_id=invocation_id,
            file_path='test.md',
            cache_status='hit',
            file_size_bytes=1024
        )

        self.assertIsNotNone(file_read_id)

        # Verify invocation stats were updated
        invocation = self.db.get_agent_invocation(invocation_id)
        self.assertEqual(invocation['total_files_read'], 1)
        self.assertEqual(invocation['cache_hits'], 1)
        self.assertEqual(invocation['cache_misses'], 0)
        self.assertEqual(invocation['estimated_tokens_used'], 1024 // 4)

    def test_log_file_read_miss(self):
        """Test logging file read with cache miss."""
        invocation_id = self.db.create_agent_invocation('test-agent', 'testing')

        self.db.log_file_read(
            invocation_id=invocation_id,
            file_path='test.md',
            cache_status='miss',
            file_size_bytes=2048
        )

        invocation = self.db.get_agent_invocation(invocation_id)
        self.assertEqual(invocation['total_files_read'], 1)
        self.assertEqual(invocation['cache_hits'], 0)
        self.assertEqual(invocation['cache_misses'], 1)
        self.assertEqual(invocation['estimated_tokens_used'], 2048 // 4)

    def test_get_agent_file_reads(self):
        """Test getting all file reads for an invocation."""
        invocation_id = self.db.create_agent_invocation('test-agent', 'testing')

        self.db.log_file_read(invocation_id, 'file1.md', 'hit', 1024)
        self.db.log_file_read(invocation_id, 'file2.md', 'miss', 2048)
        self.db.log_file_read(invocation_id, 'file3.md', 'hit', 512)

        reads = self.db.get_agent_file_reads(invocation_id)
        self.assertEqual(len(reads), 3)
        self.assertEqual(reads[0]['file_path'], 'file1.md')
        self.assertEqual(reads[1]['file_path'], 'file2.md')
        self.assertEqual(reads[2]['file_path'], 'file3.md')


class TestChecklistManagement(unittest.TestCase):
    """Test checklist management."""

    def setUp(self):
        """Create temporary database for each test."""
        self.temp_db = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.db')
        self.temp_db.close()
        self.db = ProjectDatabase(self.temp_db.name)

        # Create schema_version table (required by migration)
        self.db.conn.execute("""
            CREATE TABLE IF NOT EXISTS schema_version (
                version INTEGER PRIMARY KEY,
                description TEXT NOT NULL,
                applied_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
        """)

        # Create stub FK tables for agent_invocations
        self.db.conn.execute("""
            CREATE TABLE IF NOT EXISTS phase_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                phase_id INTEGER NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending'
            )
        """)
        self.db.conn.execute("""
            CREATE TABLE IF NOT EXISTS task_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                phase_run_id INTEGER NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending'
            )
        """)
        self.db.conn.commit()

        # Apply migration 006
        migration_path = Path(__file__).parent.parent / 'migrations' / '006_agent_context_cache.sql'
        with open(migration_path, 'r') as f:
            migration_sql = f.read()
        self.db.conn.executescript(migration_sql)
        self.db.conn.commit()

        # Create test invocation
        self.invocation_id = self.db.create_agent_invocation('test-agent', 'testing')

    def tearDown(self):
        """Clean up temporary database."""
        self.db.close()
        os.unlink(self.temp_db.name)

    def test_create_checklist(self):
        """Test creating a checklist."""
        checklist_id = self.db.create_checklist(
            invocation_id=self.invocation_id,
            checklist_name='Code Review Checklist',
            total_items=10
        )

        self.assertIsNotNone(checklist_id)
        self.assertGreater(checklist_id, 0)

        # Verify checklist was created
        checklist = self.db.get_checklist_progress(checklist_id)
        self.assertIsNotNone(checklist)
        self.assertEqual(checklist['checklist_name'], 'Code Review Checklist')
        self.assertEqual(checklist['total_items'], 10)
        self.assertEqual(checklist['completed_items'], 0)
        self.assertEqual(checklist['status'], 'in-progress')

        # Verify invocation was updated with checklist link
        invocation = self.db.get_agent_invocation(self.invocation_id)
        self.assertEqual(invocation['checklist_id'], checklist_id)

    def test_create_checklist_items(self):
        """Test bulk creating checklist items."""
        checklist_id = self.db.create_checklist(
            self.invocation_id,
            'Test Checklist',
            3
        )

        items = [
            {
                'item_order': 1,
                'item_key': 'SEC-01',
                'description': 'Check for SQL injection',
                'category': 'security',
                'priority': 'critical'
            },
            {
                'item_order': 2,
                'item_key': 'SEC-02',
                'description': 'Validate input sanitization',
                'category': 'security',
                'priority': 'high'
            },
            {
                'item_order': 3,
                'description': 'Check error handling',
                'category': 'functionality'
            }
        ]

        item_ids = self.db.create_checklist_items(checklist_id, items)
        self.assertEqual(len(item_ids), 3)

        # Verify items were created
        checklist = self.db.get_checklist(checklist_id)
        self.assertEqual(len(checklist['items']), 3)
        self.assertEqual(checklist['items'][0]['item_key'], 'SEC-01')
        self.assertEqual(checklist['items'][1]['priority'], 'high')
        self.assertEqual(checklist['items'][2]['status'], 'pending')

    def test_update_checklist_item_to_completed(self):
        """Test updating checklist item to completed."""
        checklist_id = self.db.create_checklist(self.invocation_id, 'Test', 2)
        items = [
            {'item_order': 1, 'description': 'Task 1'},
            {'item_order': 2, 'description': 'Task 2'}
        ]
        item_ids = self.db.create_checklist_items(checklist_id, items)

        # Update first item to completed
        self.db.update_checklist_item(
            item_ids[0],
            status='completed',
            notes='All checks passed'
        )

        # Verify item was updated
        checklist = self.db.get_checklist(checklist_id)
        self.assertEqual(checklist['items'][0]['status'], 'completed')
        self.assertEqual(checklist['items'][0]['notes'], 'All checks passed')
        self.assertIsNotNone(checklist['items'][0]['completed_at'])

        # Verify checklist progress was auto-updated by trigger
        progress = self.db.get_checklist_progress(checklist_id)
        self.assertEqual(progress['completed_items'], 1)
        self.assertEqual(progress['completion_percent'], 50.0)

    def test_update_checklist_item_status_transitions(self):
        """Test checklist item status transitions set timestamps."""
        checklist_id = self.db.create_checklist(self.invocation_id, 'Test', 1)
        items = [{'item_order': 1, 'description': 'Task 1'}]
        item_ids = self.db.create_checklist_items(checklist_id, items)

        # Transition to in-progress
        self.db.update_checklist_item(item_ids[0], 'in-progress')
        checklist = self.db.get_checklist(checklist_id)
        self.assertIsNotNone(checklist['items'][0]['started_at'])
        self.assertIsNone(checklist['items'][0]['completed_at'])

        # Transition to completed
        self.db.update_checklist_item(item_ids[0], 'completed')
        checklist = self.db.get_checklist(checklist_id)
        self.assertIsNotNone(checklist['items'][0]['completed_at'])

    def test_complete_checklist(self):
        """Test marking checklist as completed."""
        checklist_id = self.db.create_checklist(self.invocation_id, 'Test', 1)

        self.db.complete_checklist(checklist_id, 'completed')

        checklist = self.db.get_checklist_progress(checklist_id)
        self.assertEqual(checklist['status'], 'completed')
        self.assertIsNotNone(checklist['completed_at'])
        self.assertIsNotNone(checklist['duration_seconds'])  # Trigger should calculate


class TestChecklistVerification(unittest.TestCase):
    """Test checklist verification functionality."""

    def setUp(self):
        """Create temporary database for each test."""
        self.temp_db = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.db')
        self.temp_db.close()
        self.db = ProjectDatabase(self.temp_db.name)

        # Create schema_version table (required by migration)
        self.db.conn.execute("""
            CREATE TABLE IF NOT EXISTS schema_version (
                version INTEGER PRIMARY KEY,
                description TEXT NOT NULL,
                applied_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
        """)

        # Create stub FK tables for agent_invocations
        self.db.conn.execute("""
            CREATE TABLE IF NOT EXISTS phase_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                phase_id INTEGER NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending'
            )
        """)
        self.db.conn.execute("""
            CREATE TABLE IF NOT EXISTS task_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                phase_run_id INTEGER NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending'
            )
        """)
        # Create stub quality_gates table for checklist_verifications FK
        self.db.conn.execute("""
            CREATE TABLE IF NOT EXISTS quality_gates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                phase_run_id INTEGER NOT NULL,
                gate_type TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending'
            )
        """)
        self.db.conn.commit()

        # Apply migration 006
        migration_path = Path(__file__).parent.parent / 'migrations' / '006_agent_context_cache.sql'
        with open(migration_path, 'r') as f:
            migration_sql = f.read()
        self.db.conn.executescript(migration_sql)
        self.db.conn.commit()

        # Create test data
        invocation_id = self.db.create_agent_invocation('test-agent', 'testing')
        checklist_id = self.db.create_checklist(invocation_id, 'Test', 1)
        items = [{'item_order': 1, 'description': 'Test item'}]
        item_ids = self.db.create_checklist_items(checklist_id, items)
        self.item_id = item_ids[0]

    def tearDown(self):
        """Clean up temporary database."""
        self.db.close()
        os.unlink(self.temp_db.name)

    def test_add_checklist_verification(self):
        """Test adding verification outcome."""
        verification_id = self.db.add_checklist_verification(
            checklist_item_id=self.item_id,
            result='passed',
            verification_method='automated',
            verified_by='test-runner',
            evidence_text='All 15 tests passed'
        )

        self.assertIsNotNone(verification_id)
        self.assertGreater(verification_id, 0)

        # Verify it was created
        verifications = self.db.get_checklist_verifications(self.item_id)
        self.assertEqual(len(verifications), 1)
        self.assertEqual(verifications[0]['result'], 'passed')
        self.assertEqual(verifications[0]['verification_method'], 'automated')
        self.assertEqual(verifications[0]['evidence_text'], 'All 15 tests passed')

    def test_multiple_verifications_per_item(self):
        """Test multiple verifications for same item."""
        # Add multiple verifications
        self.db.add_checklist_verification(
            self.item_id, 'passed', 'automated', 'test-runner'
        )
        self.db.add_checklist_verification(
            self.item_id, 'passed', 'manual', 'code-reviewer',
            evidence_text='Manually reviewed code'
        )

        verifications = self.db.get_checklist_verifications(self.item_id)
        self.assertEqual(len(verifications), 2)


class TestChecklistTemplates(unittest.TestCase):
    """Test checklist template functionality."""

    def setUp(self):
        """Create temporary database for each test."""
        self.temp_db = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.db')
        self.temp_db.close()
        self.db = ProjectDatabase(self.temp_db.name)

        # Create schema_version table (required by migration)
        self.db.conn.execute("""
            CREATE TABLE IF NOT EXISTS schema_version (
                version INTEGER PRIMARY KEY,
                description TEXT NOT NULL,
                applied_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
        """)
        self.db.conn.commit()

        # Apply migration 006
        migration_path = Path(__file__).parent.parent / 'migrations' / '006_agent_context_cache.sql'
        with open(migration_path, 'r') as f:
            migration_sql = f.read()
        self.db.conn.executescript(migration_sql)
        self.db.conn.commit()

    def tearDown(self):
        """Clean up temporary database."""
        self.db.close()
        os.unlink(self.temp_db.name)

    def test_create_checklist_template(self):
        """Test creating a checklist template."""
        items = [
            {'item_key': 'SEC-01', 'description': 'Check SQL injection', 'priority': 'critical'},
            {'item_key': 'SEC-02', 'description': 'Check XSS', 'priority': 'high'},
            {'item_key': 'SEC-03', 'description': 'Check CSRF', 'priority': 'high'}
        ]

        template_id = self.db.create_checklist_template(
            name='security-checklist',
            agent_type='code-reviewer',
            items=items,
            description='Security review checklist'
        )

        self.assertIsNotNone(template_id)
        self.assertGreater(template_id, 0)

        # Verify template was created
        template = self.db.get_checklist_template('security-checklist')
        self.assertIsNotNone(template)
        self.assertEqual(template['name'], 'security-checklist')
        self.assertEqual(template['agent_type'], 'code-reviewer')
        self.assertEqual(template['total_items'], 3)
        self.assertEqual(len(template['items']), 3)
        self.assertEqual(template['items'][0]['item_key'], 'SEC-01')

    def test_get_checklist_template_latest_version(self):
        """Test getting latest version of template."""
        items = [{'description': 'Task 1'}]

        # Create version 1
        self.db.create_checklist_template('test-template', 'test-agent', items, version=1)

        # Create version 2
        items_v2 = [{'description': 'Task 1'}, {'description': 'Task 2'}]
        self.db.create_checklist_template('test-template', 'test-agent', items_v2, version=2)

        # Get without version (should return latest)
        template = self.db.get_checklist_template('test-template')
        self.assertEqual(template['version'], 2)
        self.assertEqual(len(template['items']), 2)

    def test_get_checklist_template_specific_version(self):
        """Test getting specific version of template."""
        items = [{'description': 'Task 1'}]
        self.db.create_checklist_template('test-template', 'test-agent', items, version=1)

        items_v2 = [{'description': 'Task 1'}, {'description': 'Task 2'}]
        self.db.create_checklist_template('test-template', 'test-agent', items_v2, version=2)

        # Get version 1 specifically
        template = self.db.get_checklist_template('test-template', version=1)
        self.assertEqual(template['version'], 1)
        self.assertEqual(len(template['items']), 1)

    def test_list_checklist_templates_all(self):
        """Test listing all templates."""
        self.db.create_checklist_template('template-1', 'agent-1', [{'description': 'Task'}])
        self.db.create_checklist_template('template-2', 'agent-2', [{'description': 'Task'}])

        templates = self.db.list_checklist_templates()
        self.assertEqual(len(templates), 2)

    def test_list_checklist_templates_by_agent_type(self):
        """Test filtering templates by agent type."""
        self.db.create_checklist_template('template-1', 'code-reviewer', [{'description': 'Task'}])
        self.db.create_checklist_template('template-2', 'technical-writer', [{'description': 'Task'}])
        self.db.create_checklist_template('template-3', 'code-reviewer', [{'description': 'Task'}])

        templates = self.db.list_checklist_templates(agent_type='code-reviewer')
        self.assertEqual(len(templates), 2)
        self.assertTrue(all(t['agent_type'] == 'code-reviewer' for t in templates))


class TestCacheStatistics(unittest.TestCase):
    """Test cache statistics functionality."""

    def setUp(self):
        """Create temporary database for each test."""
        self.temp_db = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.db')
        self.temp_db.close()
        self.db = ProjectDatabase(self.temp_db.name)

        # Create schema_version table (required by migration)
        self.db.conn.execute("""
            CREATE TABLE IF NOT EXISTS schema_version (
                version INTEGER PRIMARY KEY,
                description TEXT NOT NULL,
                applied_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
        """)

        # Create stub FK tables for agent_invocations
        self.db.conn.execute("""
            CREATE TABLE IF NOT EXISTS phase_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                phase_id INTEGER NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending'
            )
        """)
        self.db.conn.execute("""
            CREATE TABLE IF NOT EXISTS task_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                phase_run_id INTEGER NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending'
            )
        """)
        self.db.conn.commit()

        # Apply migration 006
        migration_path = Path(__file__).parent.parent / 'migrations' / '006_agent_context_cache.sql'
        with open(migration_path, 'r') as f:
            migration_sql = f.read()
        self.db.conn.executescript(migration_sql)
        self.db.conn.commit()

    def tearDown(self):
        """Clean up temporary database."""
        self.db.close()
        os.unlink(self.temp_db.name)

    def test_update_cache_statistics_new(self):
        """Test creating new cache statistics."""
        self.db.update_cache_statistics(
            stat_date='2026-01-31',
            file_path=None,  # Global stats
            total_reads=100,
            cache_hits=75,
            cache_misses=25,
            tokens_saved=150000,
            avg_lookup_time_ms=2.5
        )

        stats = self.db.get_cache_stats('2026-01-31', None)
        self.assertIsNotNone(stats)
        self.assertEqual(stats['total_reads'], 100)
        self.assertEqual(stats['cache_hits'], 75)
        self.assertEqual(stats['cache_misses'], 25)
        self.assertEqual(stats['hit_rate_percent'], 75.0)
        self.assertEqual(stats['tokens_saved'], 150000)

    def test_update_cache_statistics_existing(self):
        """Test updating existing cache statistics."""
        # Create initial stats
        self.db.update_cache_statistics('2026-01-31', None, 100, 75, 25, 150000, 2.5)

        # Update with new values
        self.db.update_cache_statistics('2026-01-31', None, 200, 160, 40, 320000, 2.3)

        stats = self.db.get_cache_stats('2026-01-31', None)
        self.assertEqual(stats['total_reads'], 200)
        self.assertEqual(stats['cache_hits'], 160)
        self.assertEqual(stats['hit_rate_percent'], 80.0)

    def test_cache_statistics_per_file(self):
        """Test per-file cache statistics."""
        self.db.update_cache_statistics(
            '2026-01-31',
            'cline-docs/systemArchitecture.md',
            50, 45, 5, 90000, 1.8
        )

        stats = self.db.get_cache_stats('2026-01-31', 'cline-docs/systemArchitecture.md')
        self.assertIsNotNone(stats)
        self.assertEqual(stats['file_path'], 'cline-docs/systemArchitecture.md')
        self.assertEqual(stats['total_reads'], 50)

    def test_get_agent_metrics_no_invocations(self):
        """Test getting metrics when no invocations exist."""
        metrics = self.db.get_agent_metrics('nonexistent-agent')
        self.assertEqual(metrics['total_invocations'], 0)
        self.assertEqual(metrics['completed'], 0)
        self.assertEqual(metrics['cache_hit_rate'], 0.0)

    def test_get_agent_metrics_with_invocations(self):
        """Test getting aggregated agent metrics."""
        # Create multiple invocations
        inv1 = self.db.create_agent_invocation('test-agent', 'planning')
        self.db.log_file_read(inv1, 'file1.md', 'hit', 1024)
        self.db.log_file_read(inv1, 'file2.md', 'hit', 2048)
        self.db.complete_agent_invocation(inv1, 'completed')

        inv2 = self.db.create_agent_invocation('test-agent', 'implementation')
        self.db.log_file_read(inv2, 'file3.md', 'miss', 4096)
        self.db.log_file_read(inv2, 'file4.md', 'hit', 1024)
        self.db.complete_agent_invocation(inv2, 'completed')

        # Get metrics
        metrics = self.db.get_agent_metrics('test-agent')
        self.assertEqual(metrics['total_invocations'], 2)
        self.assertEqual(metrics['completed'], 2)
        self.assertEqual(metrics['failed'], 0)
        self.assertEqual(metrics['avg_files_read'], 2.0)
        self.assertEqual(metrics['avg_cache_hits'], 1.5)
        self.assertEqual(metrics['avg_cache_misses'], 0.5)
        self.assertEqual(metrics['cache_hit_rate'], 75.0)  # 3 hits / 4 total

    def test_get_agent_metrics_filtered_by_date(self):
        """Test filtering metrics by date range."""
        # Create invocation
        inv1 = self.db.create_agent_invocation('test-agent', 'planning')
        self.db.complete_agent_invocation(inv1, 'completed')

        # Get metrics with date filter
        today = datetime.now().strftime('%Y-%m-%d')
        metrics = self.db.get_agent_metrics('test-agent', start_date=today, end_date=today)
        self.assertEqual(metrics['total_invocations'], 1)


if __name__ == '__main__':
    # Run all tests with verbose output
    unittest.main(verbosity=2)
