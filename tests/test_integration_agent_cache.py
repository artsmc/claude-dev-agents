"""
Integration tests for Agent Context Caching System.

Tests multi-component scenarios, concurrent access, FK cascades,
transactions, and end-to-end workflows.

Zero external dependencies - uses only Python standard library.
"""

import unittest
import tempfile
import os
from pathlib import Path
import sys
import json
import time
import threading
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.project_database import ProjectDatabase


class TestMultiInvocationCaching(unittest.TestCase):
    """Test cache persistence across multiple agent invocations."""

    def setUp(self):
        """Create temporary database."""
        self.temp_db = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.db')
        self.temp_db.close()
        self.db = ProjectDatabase(self.temp_db.name)

        # Setup schema
        self._setup_schema()

    def _setup_schema(self):
        """Apply migration and create stub tables."""
        self.db.conn.execute("""
            CREATE TABLE IF NOT EXISTS schema_version (
                version INTEGER PRIMARY KEY,
                description TEXT NOT NULL,
                applied_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
        """)
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

        migration_path = Path(__file__).parent.parent / 'migrations' / '006_agent_context_cache.sql'
        with open(migration_path, 'r') as f:
            self.db.conn.executescript(f.read())
        self.db.conn.commit()

    def tearDown(self):
        """Clean up."""
        self.db.close()
        os.unlink(self.temp_db.name)

    def test_cache_persists_across_invocations(self):
        """Test that cache entries persist and are reused by subsequent invocations."""
        # Invocation 1: Cache a file
        inv1 = self.db.create_agent_invocation('agent-1', 'planning')
        file_content = '# Documentation\n\nThis is cached content'

        self.db.cache_file('docs/README.md', file_content)
        self.db.log_file_read(inv1, 'docs/README.md', 'miss', len(file_content))
        self.db.complete_agent_invocation(inv1, 'completed')

        # Invocation 2: Reuse cached file
        inv2 = self.db.create_agent_invocation('agent-2', 'implementation')
        cached = self.db.get_cached_file('docs/README.md')

        self.assertIsNotNone(cached)
        self.assertEqual(cached['content'], file_content)
        self.assertEqual(cached['hit_count'], 1)  # First hit

        self.db.log_file_read(inv2, 'docs/README.md', 'hit', len(file_content))
        self.db.complete_agent_invocation(inv2, 'completed')

        # Invocation 3: Another cache hit
        inv3 = self.db.create_agent_invocation('agent-3', 'review')
        cached = self.db.get_cached_file('docs/README.md')

        self.assertEqual(cached['hit_count'], 2)  # Second hit
        self.assertEqual(cached['access_count'], 2)

        # Verify all invocations logged correctly
        inv1_data = self.db.get_agent_invocation(inv1)
        inv2_data = self.db.get_agent_invocation(inv2)

        self.assertEqual(inv1_data['cache_misses'], 1)
        self.assertEqual(inv2_data['cache_hits'], 1)

    def test_cache_invalidation_on_content_change(self):
        """Test that cache invalidates when file content changes."""
        # Invocation 1: Cache original content
        inv1 = self.db.create_agent_invocation('agent-1', 'planning')
        original_content = '# Version 1'

        file_id = self.db.cache_file('docs/file.md', original_content)
        cached = self.db.get_cached_file('docs/file.md')
        original_hash = cached['content_hash']

        # Invocation 2: Update content (triggers cache miss)
        inv2 = self.db.create_agent_invocation('agent-2', 'implementation')
        updated_content = '# Version 2 - Updated'

        self.db.cache_file('docs/file.md', updated_content)
        cached = self.db.get_cached_file('docs/file.md')

        # Hash should be different
        self.assertNotEqual(cached['content_hash'], original_hash)
        self.assertEqual(cached['content'], updated_content)
        self.assertEqual(cached['miss_count'], 2)  # Initial + update

    def test_agent_metrics_aggregation(self):
        """Test that agent metrics aggregate correctly across invocations."""
        # Create 3 invocations with different cache patterns
        inv1 = self.db.create_agent_invocation('test-agent', 'planning')
        self.db.log_file_read(inv1, 'file1.md', 'miss', 1024)
        self.db.log_file_read(inv1, 'file2.md', 'miss', 2048)
        self.db.complete_agent_invocation(inv1, 'completed')

        inv2 = self.db.create_agent_invocation('test-agent', 'implementation')
        self.db.log_file_read(inv2, 'file1.md', 'hit', 1024)
        self.db.log_file_read(inv2, 'file2.md', 'hit', 2048)
        self.db.log_file_read(inv2, 'file3.md', 'miss', 4096)
        self.db.complete_agent_invocation(inv2, 'completed')

        inv3 = self.db.create_agent_invocation('test-agent', 'review')
        self.db.log_file_read(inv3, 'file1.md', 'hit', 1024)
        self.db.log_file_read(inv3, 'file2.md', 'hit', 2048)
        self.db.log_file_read(inv3, 'file3.md', 'hit', 4096)
        self.db.complete_agent_invocation(inv3, 'completed')

        # Get aggregated metrics
        metrics = self.db.get_agent_metrics('test-agent')

        self.assertEqual(metrics['total_invocations'], 3)
        self.assertEqual(metrics['completed'], 3)
        self.assertAlmostEqual(metrics['avg_files_read'], 2.67, places=1)  # (2+3+3)/3
        self.assertEqual(metrics['cache_hit_rate'], 62.5)  # 5 hits / 8 total


class TestChecklistSaveResume(unittest.TestCase):
    """Test checklist save/resume across sessions."""

    def setUp(self):
        """Create temporary database."""
        self.temp_db = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.db')
        self.temp_db.close()
        self.db_path = self.temp_db.name

        # Setup schema
        self.db = ProjectDatabase(self.db_path)
        self._setup_schema()

    def _setup_schema(self):
        """Apply migration and create stub tables."""
        self.db.conn.execute("""
            CREATE TABLE IF NOT EXISTS schema_version (
                version INTEGER PRIMARY KEY,
                description TEXT NOT NULL,
                applied_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
        """)
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

        migration_path = Path(__file__).parent.parent / 'migrations' / '006_agent_context_cache.sql'
        with open(migration_path, 'r') as f:
            self.db.conn.executescript(f.read())
        self.db.conn.commit()

    def tearDown(self):
        """Clean up."""
        self.db.close()
        os.unlink(self.db_path)

    def test_checklist_resume_across_sessions(self):
        """Test that checklist progress persists across database sessions."""
        # Session 1: Create checklist and complete first 2 items
        inv_id = self.db.create_agent_invocation('test-agent', 'testing')
        checklist_id = self.db.create_checklist(inv_id, 'Test Checklist', 5)

        items = [
            {'item_order': 1, 'description': 'Task 1', 'priority': 'high'},
            {'item_order': 2, 'description': 'Task 2', 'priority': 'medium'},
            {'item_order': 3, 'description': 'Task 3', 'priority': 'medium'},
            {'item_order': 4, 'description': 'Task 4', 'priority': 'low'},
            {'item_order': 5, 'description': 'Task 5', 'priority': 'low'},
        ]
        item_ids = self.db.create_checklist_items(checklist_id, items)

        # Complete first 2 items
        self.db.update_checklist_item(item_ids[0], 'completed')
        self.db.update_checklist_item(item_ids[1], 'completed')

        # Verify progress
        progress = self.db.get_checklist_progress(checklist_id)
        self.assertEqual(progress['completed_items'], 2)
        self.assertEqual(progress['completion_percent'], 40.0)

        # Close database (simulate session end)
        self.db.close()

        # Session 2: Reopen database and resume checklist
        self.db = ProjectDatabase(self.db_path)

        # Verify progress persisted
        progress = self.db.get_checklist_progress(checklist_id)
        self.assertEqual(progress['completed_items'], 2)
        self.assertEqual(progress['completion_percent'], 40.0)
        self.assertEqual(progress['status'], 'in-progress')

        # Complete remaining items
        self.db.update_checklist_item(item_ids[2], 'completed')
        self.db.update_checklist_item(item_ids[3], 'completed')
        self.db.update_checklist_item(item_ids[4], 'completed')

        # Verify final progress
        progress = self.db.get_checklist_progress(checklist_id)
        self.assertEqual(progress['completed_items'], 5)
        self.assertEqual(progress['completion_percent'], 100.0)

    def test_checklist_with_template_versioning(self):
        """Test checklist creation from templates with version tracking."""
        # Create template v1
        template_items = [
            {'item_key': 'SEC-01', 'description': 'Check SQL injection'},
            {'item_key': 'SEC-02', 'description': 'Check XSS'}
        ]
        self.db.create_checklist_template('security-checklist', 'code-reviewer', template_items, version=1)

        # Create template v2 with additional item
        template_items_v2 = [
            {'item_key': 'SEC-01', 'description': 'Check SQL injection'},
            {'item_key': 'SEC-02', 'description': 'Check XSS'},
            {'item_key': 'SEC-03', 'description': 'Check CSRF'}
        ]
        self.db.create_checklist_template('security-checklist', 'code-reviewer', template_items_v2, version=2)

        # Create checklist using v1
        inv1 = self.db.create_agent_invocation('reviewer-1', 'review')
        checklist1_id = self.db.create_checklist(
            inv1, 'Security Review Run 1', 2,
            template_name='security-checklist',
            template_version=1
        )

        # Create checklist using v2
        inv2 = self.db.create_agent_invocation('reviewer-2', 'review')
        checklist2_id = self.db.create_checklist(
            inv2, 'Security Review Run 2', 3,
            template_name='security-checklist',
            template_version=2
        )

        # Verify checklists reference correct template versions
        checklist1 = self.db.get_checklist_progress(checklist1_id)
        checklist2 = self.db.get_checklist_progress(checklist2_id)

        self.assertEqual(checklist1['template_version'], 1)
        self.assertEqual(checklist1['total_items'], 2)

        self.assertEqual(checklist2['template_version'], 2)
        self.assertEqual(checklist2['total_items'], 3)


class TestForeignKeyCascades(unittest.TestCase):
    """Test FK cascade deletes and relationships."""

    def setUp(self):
        """Create temporary database."""
        self.temp_db = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.db')
        self.temp_db.close()
        self.db = ProjectDatabase(self.temp_db.name)

        # Setup schema
        self._setup_schema()

    def _setup_schema(self):
        """Apply migration and create stub tables."""
        self.db.conn.execute("""
            CREATE TABLE IF NOT EXISTS schema_version (
                version INTEGER PRIMARY KEY,
                description TEXT NOT NULL,
                applied_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
        """)
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
        self.db.conn.execute("""
            CREATE TABLE IF NOT EXISTS quality_gates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                phase_run_id INTEGER NOT NULL,
                gate_type TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending'
            )
        """)
        self.db.conn.commit()

        migration_path = Path(__file__).parent.parent / 'migrations' / '006_agent_context_cache.sql'
        with open(migration_path, 'r') as f:
            self.db.conn.executescript(f.read())
        self.db.conn.commit()

    def tearDown(self):
        """Clean up."""
        self.db.close()
        os.unlink(self.temp_db.name)

    def test_delete_invocation_cascades_to_file_reads(self):
        """Test that deleting invocation cascades to agent_file_reads."""
        inv_id = self.db.create_agent_invocation('test-agent', 'testing')

        # Log file reads
        self.db.log_file_read(inv_id, 'file1.md', 'hit', 1024)
        self.db.log_file_read(inv_id, 'file2.md', 'miss', 2048)
        self.db.log_file_read(inv_id, 'file3.md', 'hit', 512)

        # Verify file reads exist
        reads = self.db.get_agent_file_reads(inv_id)
        self.assertEqual(len(reads), 3)

        # Delete invocation
        self.db.conn.execute("DELETE FROM agent_invocations WHERE id = ?", (inv_id,))
        self.db.conn.commit()

        # Verify file reads were cascade deleted
        reads = self.db.get_agent_file_reads(inv_id)
        self.assertEqual(len(reads), 0)

    def test_delete_invocation_cascades_to_checklist(self):
        """Test that deleting invocation cascades to checklists and items."""
        inv_id = self.db.create_agent_invocation('test-agent', 'testing')
        checklist_id = self.db.create_checklist(inv_id, 'Test Checklist', 3)

        items = [
            {'item_order': 1, 'description': 'Task 1'},
            {'item_order': 2, 'description': 'Task 2'},
            {'item_order': 3, 'description': 'Task 3'}
        ]
        self.db.create_checklist_items(checklist_id, items)

        # Verify checklist exists
        checklist = self.db.get_checklist(checklist_id)
        self.assertIsNotNone(checklist)
        self.assertEqual(len(checklist['items']), 3)

        # Delete invocation
        self.db.conn.execute("DELETE FROM agent_invocations WHERE id = ?", (inv_id,))
        self.db.conn.commit()

        # Verify checklist was cascade deleted
        checklist = self.db.get_checklist(checklist_id)
        self.assertIsNone(checklist)

    def test_delete_checklist_item_cascades_to_verifications(self):
        """Test that deleting checklist item cascades to verifications."""
        inv_id = self.db.create_agent_invocation('test-agent', 'testing')
        checklist_id = self.db.create_checklist(inv_id, 'Test', 1)

        items = [{'item_order': 1, 'description': 'Task'}]
        item_ids = self.db.create_checklist_items(checklist_id, items)
        item_id = item_ids[0]

        # Add verifications
        self.db.add_checklist_verification(item_id, 'passed', 'automated', 'test-runner')
        self.db.add_checklist_verification(item_id, 'passed', 'manual', 'reviewer')

        # Verify verifications exist
        verifications = self.db.get_checklist_verifications(item_id)
        self.assertEqual(len(verifications), 2)

        # Delete checklist item
        self.db.conn.execute("DELETE FROM checklist_items WHERE id = ?", (item_id,))
        self.db.conn.commit()

        # Verify verifications were cascade deleted
        verifications = self.db.get_checklist_verifications(item_id)
        self.assertEqual(len(verifications), 0)


class TestConcurrentAccess(unittest.TestCase):
    """Test concurrent access scenarios and race conditions."""

    def setUp(self):
        """Create temporary database."""
        self.temp_db = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.db')
        self.temp_db.close()
        self.db_path = self.temp_db.name

        # Setup schema
        db = ProjectDatabase(self.db_path)
        self._setup_schema(db)
        db.close()

    def _setup_schema(self, db):
        """Apply migration and create stub tables."""
        db.conn.execute("""
            CREATE TABLE IF NOT EXISTS schema_version (
                version INTEGER PRIMARY KEY,
                description TEXT NOT NULL,
                applied_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
        """)
        db.conn.execute("""
            CREATE TABLE IF NOT EXISTS phase_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                phase_id INTEGER NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending'
            )
        """)
        db.conn.execute("""
            CREATE TABLE IF NOT EXISTS task_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                phase_run_id INTEGER NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending'
            )
        """)
        db.conn.commit()

        migration_path = Path(__file__).parent.parent / 'migrations' / '006_agent_context_cache.sql'
        with open(migration_path, 'r') as f:
            db.conn.executescript(f.read())
        db.conn.commit()

    def tearDown(self):
        """Clean up."""
        os.unlink(self.db_path)

    def test_concurrent_cache_reads(self):
        """Test concurrent reads from multiple connections (simulates multiple agents)."""
        # Setup: Cache a file
        db = ProjectDatabase(self.db_path)
        content = '# Large Documentation File\n' + ('Content ' * 1000)
        db.cache_file('docs/large.md', content)
        db.close()

        results = []
        errors = []

        def read_cached_file():
            """Thread worker: read cached file."""
            try:
                db = ProjectDatabase(self.db_path)
                cached = db.get_cached_file('docs/large.md')
                results.append(cached is not None)
                db.close()
            except Exception as e:
                errors.append(str(e))

        # Spawn 10 concurrent readers
        threads = []
        for _ in range(10):
            t = threading.Thread(target=read_cached_file)
            threads.append(t)
            t.start()

        # Wait for all threads
        for t in threads:
            t.join()

        # Verify all reads succeeded
        self.assertEqual(len(errors), 0, f"Errors occurred: {errors}")
        self.assertEqual(len(results), 10)
        self.assertTrue(all(results))

        # Verify access count updated correctly
        db = ProjectDatabase(self.db_path)
        cached = db.get_cached_file('docs/large.md')
        # Should be 10 (concurrent reads) + 1 (this final read) = 11
        self.assertEqual(cached['access_count'], 11)
        self.assertEqual(cached['hit_count'], 11)
        db.close()

    def test_concurrent_agent_invocations(self):
        """Test creating multiple agent invocations concurrently."""
        results = []
        errors = []

        def create_invocation(agent_name):
            """Thread worker: create invocation."""
            try:
                db = ProjectDatabase(self.db_path)
                inv_id = db.create_agent_invocation(agent_name, 'testing')
                results.append(inv_id)
                db.close()
            except Exception as e:
                errors.append(str(e))

        # Spawn 5 concurrent invocation creators
        threads = []
        for i in range(5):
            t = threading.Thread(target=create_invocation, args=(f'agent-{i}',))
            threads.append(t)
            t.start()

        # Wait for all threads
        for t in threads:
            t.join()

        # Verify all invocations created successfully
        self.assertEqual(len(errors), 0, f"Errors occurred: {errors}")
        self.assertEqual(len(results), 5)
        # All IDs should be unique
        self.assertEqual(len(set(results)), 5)


class TestTransactionRollback(unittest.TestCase):
    """Test transaction rollback on error."""

    def setUp(self):
        """Create temporary database."""
        self.temp_db = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.db')
        self.temp_db.close()
        self.db = ProjectDatabase(self.temp_db.name)

        # Setup schema
        self._setup_schema()

    def _setup_schema(self):
        """Apply migration and create stub tables."""
        self.db.conn.execute("""
            CREATE TABLE IF NOT EXISTS schema_version (
                version INTEGER PRIMARY KEY,
                description TEXT NOT NULL,
                applied_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
        """)
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

        migration_path = Path(__file__).parent.parent / 'migrations' / '006_agent_context_cache.sql'
        with open(migration_path, 'r') as f:
            self.db.conn.executescript(f.read())
        self.db.conn.commit()

    def tearDown(self):
        """Clean up."""
        self.db.close()
        os.unlink(self.temp_db.name)

    def test_transaction_rollback_on_error(self):
        """Test that failed transactions roll back correctly."""
        # Note: Individual API methods auto-commit, so we test raw SQL transactions
        inv_id = self.db.create_agent_invocation('test-agent', 'testing')

        # Test transaction rollback with raw SQL
        checklist_id = None
        try:
            with self.db.transaction():
                # Insert checklist (no auto-commit in transaction context)
                cursor = self.db.conn.execute("""
                    INSERT INTO checklists (invocation_id, checklist_name, total_items, status)
                    VALUES (?, ?, ?, ?)
                """, (inv_id, 'Test Checklist', 2, 'in-progress'))
                checklist_id = cursor.lastrowid

                # Insert first item successfully
                self.db.conn.execute("""
                    INSERT INTO checklist_items (checklist_id, item_order, description, status)
                    VALUES (?, ?, ?, ?)
                """, (checklist_id, 1, 'Task 1', 'pending'))

                # Try to insert duplicate item_order (violates UNIQUE constraint)
                self.db.conn.execute("""
                    INSERT INTO checklist_items (checklist_id, item_order, description, status)
                    VALUES (?, ?, ?, ?)
                """, (checklist_id, 1, 'Duplicate Task', 'pending'))

        except Exception:
            pass  # Expected to fail

        # Verify entire transaction was rolled back - checklist should not exist
        checklist = self.db.get_checklist_progress(checklist_id)
        self.assertIsNone(checklist)


if __name__ == '__main__':
    # Run all integration tests with verbose output
    unittest.main(verbosity=2)
