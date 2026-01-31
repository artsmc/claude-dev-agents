"""
ProjectDatabase - SQLite abstraction layer for PM-DB v2 phase-based execution tracking.

Provides a complete Python API for managing projects, phases, phase plans, tasks,
phase runs, quality gates, and execution tracking.

PM-DB v2 separates planning (phase_plans) from execution (phase_runs), enabling:
- Multiple execution runs per phase with distinct tracking
- Versioned plans with revision history
- Task-level execution tracking across runs
- Quality gate validation and artifact storage
- Agent workload balancing and delegation

Zero external dependencies - uses only Python standard library.

Usage:
    from lib.project_database import ProjectDatabase

    db = ProjectDatabase()  # Opens ~/.claude/projects.db

    # Create a project
    project_id = db.create_project("my-app", "/path/to/app", "My application project")

    # Create a phase
    phase_id = db.create_phase(project_id, "feature-auth", "feature",
                                "job-queue/feature-auth", "planning")

    # Create a phase plan
    plan_id = db.create_phase_plan(phase_id, "Implement authentication system")
    db.add_plan_document(plan_id, "frd", "FRD", "# Functional Requirements...")
    db.create_task(plan_id, "1.0", "Setup auth middleware", "...", 1, 1, "high", "medium")
    db.approve_phase_plan(plan_id, "tech-lead")

    # Execute the phase
    run_id = db.create_phase_run(phase_id, plan_id, "backend-agent")
    db.start_phase_run(run_id)
    task_run_id = db.create_task_run(run_id, task_id, "backend-agent")
    db.complete_task_run(task_run_id, 0)
    db.complete_phase_run(run_id, 0, "All tasks completed successfully")
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any, Tuple
from contextlib import contextmanager


class ProjectDatabase:
    """
    SQLite database abstraction for PM-DB v2 phase-based execution tracking.

    Provides methods for:
    - Project management
    - Phase and phase plan management (versioned planning)
    - Plan document management (FRD/FRS/GS/TR)
    - Task and task dependency management
    - Phase run and task run execution tracking
    - Quality gate validation
    - Artifact storage
    - Metrics and reporting

    All methods use parameterized queries for security.
    Supports transactions via context manager.
    """

    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize database connection.

        Args:
            db_path: Path to SQLite database file.
                    Defaults to ~/.claude/projects.db

        Raises:
            sqlite3.Error: If database connection fails
        """
        if db_path is None:
            db_path = str(Path.home() / ".claude" / "projects.db")

        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row  # Enable dict-like row access

        # Enable WAL mode for better concurrency
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute("PRAGMA foreign_keys=ON")  # Enforce foreign keys

    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
        return False

    @contextmanager
    def transaction(self):
        """
        Transaction context manager.

        Usage:
            with db.transaction():
                db.create_project(...)
                db.create_phase(...)
                # Commits on success, rolls back on exception
        """
        try:
            yield
            self.conn.commit()
        except Exception:
            self.conn.rollback()
            raise

    # ==================== PROJECT MANAGEMENT ====================

    def create_project(
        self,
        name: str,
        filesystem_path: str,
        description: Optional[str] = None
    ) -> int:
        """
        Create a new project.

        Args:
            name: Unique project name (e.g., "message-well")
            filesystem_path: Absolute path to project folder (required)
            description: Optional project description

        Returns:
            Project ID (integer)

        Raises:
            ValueError: If name is empty or filesystem_path is invalid
            sqlite3.IntegrityError: If project name already exists
        """
        if not name or not name.strip():
            raise ValueError("Project name cannot be empty")

        if not filesystem_path or not filesystem_path.strip():
            raise ValueError("filesystem_path is required")

        if not Path(filesystem_path).is_absolute():
            raise ValueError("filesystem_path must be an absolute path")

        cursor = self.conn.execute(
            """
            INSERT INTO projects (name, description, filesystem_path)
            VALUES (?, ?, ?)
            """,
            (name.strip(), description, filesystem_path)
        )
        self.conn.commit()
        return cursor.lastrowid

    def get_project(self, project_id: int) -> Optional[Dict[str, Any]]:
        """Get project by ID."""
        cursor = self.conn.execute(
            "SELECT * FROM projects WHERE id = ?",
            (project_id,)
        )
        row = cursor.fetchone()
        return dict(row) if row else None

    def get_project_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Get project by name."""
        cursor = self.conn.execute(
            "SELECT * FROM projects WHERE name = ?",
            (name,)
        )
        row = cursor.fetchone()
        return dict(row) if row else None

    def list_projects(self) -> List[Dict[str, Any]]:
        """List all projects."""
        cursor = self.conn.execute(
            "SELECT * FROM projects ORDER BY created_at DESC"
        )
        return [dict(row) for row in cursor.fetchall()]

    # ==================== PHASE MANAGEMENT ====================

    def create_phase(
        self,
        project_id: int,
        name: str,
        phase_type: str = 'feature',
        job_queue_rel_path: Optional[str] = None,
        planning_rel_path: Optional[str] = None,
        description: Optional[str] = None,
        status: str = 'draft'
    ) -> int:
        """
        Create a new phase.

        Args:
            project_id: Foreign key to projects table
            name: Phase name (e.g., "feature-auth")
            phase_type: Type (feature, bugfix, refactor, etc.)
            job_queue_rel_path: Relative path to job-queue folder
            planning_rel_path: Relative path to planning folder
            description: Optional description
            status: Initial status (draft, planning, approved, in-progress, completed, archived)

        Returns:
            Phase ID (integer)
        """
        if not name or not name.strip():
            raise ValueError("Phase name cannot be empty")

        cursor = self.conn.execute(
            """
            INSERT INTO phases (
                project_id, name, description, phase_type, status,
                job_queue_rel_path, planning_rel_path
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (project_id, name.strip(), description, phase_type, status,
             job_queue_rel_path, planning_rel_path)
        )
        self.conn.commit()
        return cursor.lastrowid

    def update_phase_status(self, phase_id: int, status: str):
        """Update phase status."""
        valid_statuses = ['draft', 'planning', 'approved', 'in-progress', 'completed', 'archived']
        if status not in valid_statuses:
            raise ValueError(f"Status must be one of: {valid_statuses}")

        self.conn.execute(
            "UPDATE phases SET status = ?, updated_at = datetime('now') WHERE id = ?",
            (status, phase_id)
        )
        self.conn.commit()

    def get_phase(self, phase_id: int) -> Optional[Dict[str, Any]]:
        """Get phase by ID."""
        cursor = self.conn.execute(
            "SELECT * FROM phases WHERE id = ?",
            (phase_id,)
        )
        row = cursor.fetchone()
        return dict(row) if row else None

    def list_phases(
        self,
        project_id: Optional[int] = None,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List phases with optional filters."""
        query = "SELECT * FROM phases WHERE 1=1"
        params = []

        if project_id is not None:
            query += " AND project_id = ?"
            params.append(project_id)

        if status is not None:
            query += " AND status = ?"
            params.append(status)

        query += " ORDER BY created_at DESC"

        cursor = self.conn.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

    # ==================== PHASE PLAN MANAGEMENT ====================

    def create_phase_plan(
        self,
        phase_id: int,
        planning_approach: str,
        revision: Optional[int] = None
    ) -> int:
        """
        Create a new phase plan (versioned).

        Args:
            phase_id: Foreign key to phases table
            planning_approach: Description of planning approach
            revision: Optional revision number (auto-increments if None)

        Returns:
            Plan ID (integer)
        """
        if revision is None:
            # Auto-increment revision
            cursor = self.conn.execute(
                "SELECT COALESCE(MAX(revision), 0) + 1 FROM phase_plans WHERE phase_id = ?",
                (phase_id,)
            )
            revision = cursor.fetchone()[0]

        cursor = self.conn.execute(
            """
            INSERT INTO phase_plans (phase_id, revision, planning_approach, status)
            VALUES (?, ?, ?, 'draft')
            """,
            (phase_id, revision, planning_approach)
        )
        self.conn.commit()
        return cursor.lastrowid

    def approve_phase_plan(self, plan_id: int, approved_by: str) -> None:
        """
        Approve a phase plan and set it as the active plan for the phase.

        Args:
            plan_id: Plan ID to approve
            approved_by: Name of approver
        """
        # Get phase_id
        cursor = self.conn.execute(
            "SELECT phase_id FROM phase_plans WHERE id = ?",
            (plan_id,)
        )
        row = cursor.fetchone()
        if not row:
            raise ValueError(f"Plan {plan_id} not found")

        phase_id = row[0]

        # Update plan status
        self.conn.execute(
            """
            UPDATE phase_plans
            SET status = 'approved', approved_by = ?, approved_at = datetime('now')
            WHERE id = ?
            """,
            (approved_by, plan_id)
        )

        # Update phase to point to this plan
        self.conn.execute(
            "UPDATE phases SET approved_plan_id = ? WHERE id = ?",
            (plan_id, phase_id)
        )

        self.conn.commit()

    def get_phase_plan(self, plan_id: int) -> Optional[Dict[str, Any]]:
        """Get phase plan by ID."""
        cursor = self.conn.execute(
            "SELECT * FROM phase_plans WHERE id = ?",
            (plan_id,)
        )
        row = cursor.fetchone()
        return dict(row) if row else None

    def list_phase_plans(self, phase_id: int) -> List[Dict[str, Any]]:
        """List all plans for a phase."""
        cursor = self.conn.execute(
            "SELECT * FROM phase_plans WHERE phase_id = ? ORDER BY revision DESC",
            (phase_id,)
        )
        return [dict(row) for row in cursor.fetchall()]

    # ==================== PLAN DOCUMENT MANAGEMENT ====================

    def add_plan_document(
        self,
        plan_id: int,
        doc_type: str,
        doc_name: str,
        content: str,
        file_path: Optional[str] = None
    ) -> int:
        """
        Add a plan document (FRD, FRS, GS, TR, etc.).

        Args:
            plan_id: Foreign key to phase_plans table
            doc_type: Document type (frd, frs, gs, tr, task-list, etc.)
            doc_name: Document name
            content: Full document content
            file_path: Optional relative file path

        Returns:
            Document ID (integer)
        """
        cursor = self.conn.execute(
            """
            INSERT INTO plan_documents (phase_plan_id, doc_type, doc_name, content, file_path)
            VALUES (?, ?, ?, ?, ?)
            """,
            (plan_id, doc_type, doc_name, content, file_path)
        )
        self.conn.commit()
        return cursor.lastrowid

    def update_plan_document(self, doc_id: int, content: str):
        """Update plan document content."""
        self.conn.execute(
            """
            UPDATE plan_documents
            SET content = ?, updated_at = datetime('now')
            WHERE id = ?
            """,
            (content, doc_id)
        )
        self.conn.commit()

    def get_plan_documents(self, plan_id: int) -> List[Dict[str, Any]]:
        """Get all documents for a plan."""
        cursor = self.conn.execute(
            "SELECT * FROM plan_documents WHERE phase_plan_id = ? ORDER BY doc_type",
            (plan_id,)
        )
        return [dict(row) for row in cursor.fetchall()]

    def get_plan_document(self, plan_id: int, doc_type: str) -> Optional[Dict[str, Any]]:
        """Get a specific document by type."""
        cursor = self.conn.execute(
            "SELECT * FROM plan_documents WHERE phase_plan_id = ? AND doc_type = ?",
            (plan_id, doc_type)
        )
        row = cursor.fetchone()
        return dict(row) if row else None

    # ==================== TASK MANAGEMENT ====================

    def create_task(
        self,
        plan_id: int,
        task_key: str,
        name: str,
        description: str,
        execution_order: int,
        wave: int = 1,
        priority: str = 'medium',
        difficulty: str = 'medium',
        sub_phase: Optional[str] = None
    ) -> int:
        """
        Create a new task.

        Args:
            plan_id: Foreign key to phase_plans table
            task_key: Hierarchical key (e.g., "2.1a", "3.0b")
            name: Task name
            description: Task description
            execution_order: Order of execution
            wave: Parallel execution wave (default 1)
            priority: Priority (low, medium, high, critical)
            difficulty: Difficulty (small, medium, large, xlarge)
            sub_phase: Optional sub-phase identifier (e.g., "2", "3")

        Returns:
            Task ID (integer)
        """
        cursor = self.conn.execute(
            """
            INSERT INTO tasks (
                phase_plan_id, task_key, name, description,
                execution_order, wave, priority, difficulty, sub_phase
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (plan_id, task_key, name, description, execution_order,
             wave, priority, difficulty, sub_phase)
        )
        self.conn.commit()
        return cursor.lastrowid

    def update_task_status(self, task_id: int, status: str):
        """Update task status."""
        valid_statuses = ['pending', 'in-progress', 'completed', 'blocked', 'skipped']
        if status not in valid_statuses:
            raise ValueError(f"Status must be one of: {valid_statuses}")

        self.conn.execute(
            "UPDATE tasks SET status = ?, updated_at = datetime('now') WHERE id = ?",
            (status, task_id)
        )
        self.conn.commit()

    def get_task(self, task_id: int) -> Optional[Dict[str, Any]]:
        """Get task by ID."""
        cursor = self.conn.execute(
            "SELECT * FROM tasks WHERE id = ?",
            (task_id,)
        )
        row = cursor.fetchone()
        return dict(row) if row else None

    def list_tasks(
        self,
        plan_id: int,
        sub_phase: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List all tasks for a plan, optionally filtered by sub-phase."""
        query = "SELECT * FROM tasks WHERE phase_plan_id = ?"
        params = [plan_id]

        if sub_phase is not None:
            query += " AND sub_phase = ?"
            params.append(sub_phase)

        query += " ORDER BY execution_order"

        cursor = self.conn.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

    def get_tasks_by_wave(self, plan_id: int, wave: int) -> List[Dict[str, Any]]:
        """Get all tasks in a specific wave."""
        cursor = self.conn.execute(
            """
            SELECT * FROM tasks
            WHERE phase_plan_id = ? AND wave = ?
            ORDER BY execution_order
            """,
            (plan_id, wave)
        )
        return [dict(row) for row in cursor.fetchall()]

    def get_tasks_by_sub_phase(self, plan_id: int, sub_phase: str) -> List[Dict[str, Any]]:
        """Get all tasks in a specific sub-phase."""
        cursor = self.conn.execute(
            """
            SELECT * FROM tasks
            WHERE phase_plan_id = ? AND sub_phase = ?
            ORDER BY execution_order
            """,
            (plan_id, sub_phase)
        )
        return [dict(row) for row in cursor.fetchall()]

    # ==================== TASK DEPENDENCY MANAGEMENT ====================

    def add_task_dependency(
        self,
        task_id: int,
        depends_on_task_id: int,
        dependency_type: str = 'blocks'
    ) -> int:
        """
        Add a task dependency.

        Args:
            task_id: Task that has the dependency
            depends_on_task_id: Task that must complete first
            dependency_type: Type (blocks, related, suggests)

        Returns:
            Dependency ID (integer)
        """
        cursor = self.conn.execute(
            """
            INSERT INTO task_dependencies (task_id, depends_on_task_id, dependency_type)
            VALUES (?, ?, ?)
            """,
            (task_id, depends_on_task_id, dependency_type)
        )
        self.conn.commit()
        return cursor.lastrowid

    def get_task_dependencies(self, task_id: int) -> List[Dict[str, Any]]:
        """Get all dependencies for a task."""
        cursor = self.conn.execute(
            """
            SELECT td.*, t.task_key, t.name
            FROM task_dependencies td
            JOIN tasks t ON td.depends_on_task_id = t.id
            WHERE td.task_id = ?
            """,
            (task_id,)
        )
        return [dict(row) for row in cursor.fetchall()]

    def get_dependency_graph(self, plan_id: int) -> Dict[str, Any]:
        """
        Get complete dependency graph for a plan.

        Returns:
            Dict with 'nodes' (tasks) and 'edges' (dependencies)
        """
        # Get all tasks
        tasks = self.list_tasks(plan_id)
        nodes = [
            {
                'id': t['id'],
                'task_key': t['task_key'],
                'name': t['name'],
                'status': t['status'],
                'wave': t['wave']
            }
            for t in tasks
        ]

        # Get all dependencies
        cursor = self.conn.execute(
            """
            SELECT td.*
            FROM task_dependencies td
            JOIN tasks t ON td.task_id = t.id
            WHERE t.phase_plan_id = ?
            """,
            (plan_id,)
        )
        edges = [
            {
                'from': row['depends_on_task_id'],
                'to': row['task_id'],
                'type': row['dependency_type']
            }
            for row in cursor.fetchall()
        ]

        return {'nodes': nodes, 'edges': edges}

    # ==================== PHASE RUN MANAGEMENT ====================

    def create_phase_run(
        self,
        phase_id: int,
        plan_id: int,
        assigned_agent: Optional[str] = None
    ) -> int:
        """
        Create a new phase run (execution instance).

        Args:
            phase_id: Foreign key to phases table
            plan_id: Foreign key to phase_plans table (which plan to execute)
            assigned_agent: Optional agent assigned to this run

        Returns:
            Run ID (integer)
        """
        # Auto-increment run_number
        cursor = self.conn.execute(
            "SELECT COALESCE(MAX(run_number), 0) + 1 FROM phase_runs WHERE phase_id = ?",
            (phase_id,)
        )
        run_number = cursor.fetchone()[0]

        cursor = self.conn.execute(
            """
            INSERT INTO phase_runs (phase_id, plan_id, run_number, assigned_agent, status)
            VALUES (?, ?, ?, ?, 'pending')
            """,
            (phase_id, plan_id, run_number, assigned_agent)
        )
        self.conn.commit()
        return cursor.lastrowid

    def start_phase_run(self, run_id: int):
        """Mark phase run as started."""
        self.conn.execute(
            """
            UPDATE phase_runs
            SET status = 'in-progress', started_at = datetime('now')
            WHERE id = ?
            """,
            (run_id,)
        )
        self.conn.commit()

    def complete_phase_run(
        self,
        run_id: int,
        exit_code: int,
        summary: Optional[str] = None
    ):
        """Mark phase run as completed."""
        status = 'completed' if exit_code == 0 else 'failed'

        self.conn.execute(
            """
            UPDATE phase_runs
            SET status = ?, exit_code = ?, summary = ?, completed_at = datetime('now')
            WHERE id = ?
            """,
            (status, exit_code, summary, run_id)
        )
        self.conn.commit()

    def update_phase_run_status(self, run_id: int, status: str):
        """Update phase run status."""
        valid_statuses = ['pending', 'in-progress', 'completed', 'failed', 'cancelled']
        if status not in valid_statuses:
            raise ValueError(f"Status must be one of: {valid_statuses}")

        self.conn.execute(
            "UPDATE phase_runs SET status = ? WHERE id = ?",
            (status, run_id)
        )
        self.conn.commit()

    def get_phase_run(self, run_id: int) -> Optional[Dict[str, Any]]:
        """Get phase run by ID."""
        cursor = self.conn.execute(
            "SELECT * FROM phase_runs WHERE id = ?",
            (run_id,)
        )
        row = cursor.fetchone()
        return dict(row) if row else None

    def list_phase_runs(
        self,
        phase_id: Optional[int] = None,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List phase runs with optional filters."""
        query = "SELECT * FROM phase_runs WHERE 1=1"
        params = []

        if phase_id is not None:
            query += " AND phase_id = ?"
            params.append(phase_id)

        if status is not None:
            query += " AND status = ?"
            params.append(status)

        query += " ORDER BY created_at DESC"

        cursor = self.conn.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

    # ==================== TASK RUN MANAGEMENT ====================

    def create_task_run(
        self,
        phase_run_id: int,
        task_id: int,
        assigned_agent: Optional[str] = None
    ) -> int:
        """
        Create a new task run (links phase run to task execution).

        Args:
            phase_run_id: Foreign key to phase_runs table
            task_id: Foreign key to tasks table
            assigned_agent: Optional agent assigned to this task

        Returns:
            Task run ID (integer)
        """
        cursor = self.conn.execute(
            """
            INSERT INTO task_runs (phase_run_id, task_id, assigned_agent, status)
            VALUES (?, ?, ?, 'pending')
            """,
            (phase_run_id, task_id, assigned_agent)
        )
        self.conn.commit()
        return cursor.lastrowid

    def start_task_run(self, task_run_id: int):
        """Mark task run as started."""
        self.conn.execute(
            """
            UPDATE task_runs
            SET status = 'in-progress', started_at = datetime('now')
            WHERE id = ?
            """,
            (task_run_id,)
        )
        self.conn.commit()

    def complete_task_run(self, task_run_id: int, exit_code: int):
        """Mark task run as completed."""
        status = 'completed' if exit_code == 0 else 'failed'

        self.conn.execute(
            """
            UPDATE task_runs
            SET status = ?, exit_code = ?, completed_at = datetime('now')
            WHERE id = ?
            """,
            (status, exit_code, task_run_id)
        )
        self.conn.commit()

    def update_task_run_status(
        self,
        task_run_id: int,
        status: str,
        assigned_agent: Optional[str] = None
    ):
        """Update task run status and optionally reassign agent."""
        valid_statuses = ['pending', 'in-progress', 'completed', 'failed', 'skipped']
        if status not in valid_statuses:
            raise ValueError(f"Status must be one of: {valid_statuses}")

        if assigned_agent is not None:
            self.conn.execute(
                "UPDATE task_runs SET status = ?, assigned_agent = ? WHERE id = ?",
                (status, assigned_agent, task_run_id)
            )
        else:
            self.conn.execute(
                "UPDATE task_runs SET status = ? WHERE id = ?",
                (status, task_run_id)
            )
        self.conn.commit()

    def get_task_run(self, task_run_id: int) -> Optional[Dict[str, Any]]:
        """Get task run by ID."""
        cursor = self.conn.execute(
            "SELECT * FROM task_runs WHERE id = ?",
            (task_run_id,)
        )
        row = cursor.fetchone()
        return dict(row) if row else None

    def list_task_runs(
        self,
        phase_run_id: Optional[int] = None,
        task_id: Optional[int] = None,
        assigned_agent: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List task runs with optional filters."""
        query = "SELECT * FROM task_runs WHERE 1=1"
        params = []

        if phase_run_id is not None:
            query += " AND phase_run_id = ?"
            params.append(phase_run_id)

        if task_id is not None:
            query += " AND task_id = ?"
            params.append(task_id)

        if assigned_agent is not None:
            query += " AND assigned_agent = ?"
            params.append(assigned_agent)

        query += " ORDER BY created_at DESC"

        cursor = self.conn.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

    def get_task_run_history(self, task_id: int) -> List[Dict[str, Any]]:
        """Get all execution runs for a specific task across all phase runs."""
        cursor = self.conn.execute(
            """
            SELECT tr.*, pr.run_number, pr.started_at as run_started_at
            FROM task_runs tr
            JOIN phase_runs pr ON tr.phase_run_id = pr.id
            WHERE tr.task_id = ?
            ORDER BY pr.run_number DESC
            """,
            (task_id,)
        )
        return [dict(row) for row in cursor.fetchall()]

    def get_agent_workload(self, assigned_agent: str) -> Dict[str, Any]:
        """Get workload summary for a specific agent."""
        cursor = self.conn.execute(
            """
            SELECT
                COUNT(*) as total_tasks,
                SUM(CASE WHEN status = 'in-progress' THEN 1 ELSE 0 END) as active_tasks,
                SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed_tasks,
                SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed_tasks
            FROM task_runs
            WHERE assigned_agent = ?
            """,
            (assigned_agent,)
        )
        row = cursor.fetchone()
        return dict(row) if row else {}

    # ==================== TASK UPDATE MANAGEMENT ====================

    def add_task_update(
        self,
        task_run_id: int,
        update_type: str,
        content: str,
        file_path: Optional[str] = None
    ) -> int:
        """
        Add a task update (progress note).

        Args:
            task_run_id: Foreign key to task_runs table
            update_type: Type (progress, blocker, question, solution, note)
            content: Update content
            file_path: Optional relative file path

        Returns:
            Update ID (integer)
        """
        cursor = self.conn.execute(
            """
            INSERT INTO task_updates (task_run_id, update_type, content, file_path)
            VALUES (?, ?, ?, ?)
            """,
            (task_run_id, update_type, content, file_path)
        )
        self.conn.commit()
        return cursor.lastrowid

    def get_task_updates(self, task_run_id: int) -> List[Dict[str, Any]]:
        """Get all updates for a task run."""
        cursor = self.conn.execute(
            "SELECT * FROM task_updates WHERE task_run_id = ? ORDER BY created_at",
            (task_run_id,)
        )
        return [dict(row) for row in cursor.fetchall()]

    # ==================== QUALITY GATE MANAGEMENT ====================

    def add_quality_gate(
        self,
        phase_run_id: int,
        gate_type: str,
        status: str = 'pending',
        result_summary: Optional[str] = None,
        checked_by: Optional[str] = None
    ) -> int:
        """
        Add a quality gate.

        Args:
            phase_run_id: Foreign key to phase_runs table
            gate_type: Type (code_review, testing, security, linting, build)
            status: Status (pending, passed, failed, skipped)
            result_summary: Optional summary of results
            checked_by: Optional checker name

        Returns:
            Gate ID (integer)
        """
        cursor = self.conn.execute(
            """
            INSERT INTO quality_gates (
                phase_run_id, gate_type, status, result_summary, checked_by
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (phase_run_id, gate_type, status, result_summary, checked_by)
        )
        self.conn.commit()
        return cursor.lastrowid

    def update_quality_gate(
        self,
        gate_id: int,
        status: str,
        result_summary: Optional[str] = None
    ):
        """Update quality gate status and results."""
        valid_statuses = ['pending', 'passed', 'failed', 'skipped']
        if status not in valid_statuses:
            raise ValueError(f"Status must be one of: {valid_statuses}")

        self.conn.execute(
            """
            UPDATE quality_gates
            SET status = ?, result_summary = ?, checked_at = datetime('now')
            WHERE id = ?
            """,
            (status, result_summary, gate_id)
        )
        self.conn.commit()

    def get_quality_gates(self, phase_run_id: int) -> List[Dict[str, Any]]:
        """Get all quality gates for a phase run."""
        cursor = self.conn.execute(
            "SELECT * FROM quality_gates WHERE phase_run_id = ? ORDER BY created_at",
            (phase_run_id,)
        )
        return [dict(row) for row in cursor.fetchall()]

    # ==================== CODE REVIEW MANAGEMENT ====================

    def add_code_review(
        self,
        phase_run_id: int,
        reviewer: str,
        summary: str,
        verdict: str,
        issues_found: Optional[List[str]] = None,
        files_reviewed: Optional[List[str]] = None
    ) -> int:
        """
        Add a code review record linked to phase run.

        Args:
            phase_run_id: Foreign key to phase_runs table
            reviewer: Name of the reviewer agent
            summary: Review summary/comments
            verdict: Review status (pending, passed, failed, needs_changes)
            issues_found: Optional list of issues (for backwards compatibility)
            files_reviewed: Optional list of files (for backwards compatibility)

        Returns:
            Review ID (integer)
        """
        cursor = self.conn.execute(
            """
            INSERT INTO code_reviews (phase_run_id, reviewer, status, comments, reviewed_at)
            VALUES (?, ?, ?, ?, datetime('now'))
            """,
            (phase_run_id, reviewer, verdict, summary)
        )
        self.conn.commit()
        return cursor.lastrowid

    def get_code_reviews(self, phase_run_id: int) -> List[Dict[str, Any]]:
        """Get all code reviews for a phase run."""
        cursor = self.conn.execute(
            "SELECT * FROM code_reviews WHERE phase_run_id = ? ORDER BY created_at",
            (phase_run_id,)
        )
        return [dict(row) for row in cursor.fetchall()]

    # ==================== ARTIFACT MANAGEMENT ====================

    def add_run_artifact(
        self,
        phase_run_id: int,
        artifact_type: str,
        artifact_name: str,
        file_path: Optional[str] = None,
        file_size_bytes: Optional[int] = None
    ) -> int:
        """
        Add a run artifact.

        Args:
            phase_run_id: Foreign key to phase_runs table
            artifact_type: Type (log, report, screenshot, diagram, etc.)
            artifact_name: Artifact name
            file_path: Optional relative file path
            file_size_bytes: Optional file size

        Returns:
            Artifact ID (integer)
        """
        cursor = self.conn.execute(
            """
            INSERT INTO run_artifacts (
                phase_run_id, artifact_type, artifact_name, file_path, file_size_bytes
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (phase_run_id, artifact_type, artifact_name, file_path, file_size_bytes)
        )
        self.conn.commit()
        return cursor.lastrowid

    def get_run_artifacts(self, phase_run_id: int) -> List[Dict[str, Any]]:
        """Get all artifacts for a phase run."""
        cursor = self.conn.execute(
            "SELECT * FROM run_artifacts WHERE phase_run_id = ? ORDER BY created_at",
            (phase_run_id,)
        )
        return [dict(row) for row in cursor.fetchall()]

    # ==================== METRICS & REPORTING ====================

    def get_phase_metrics(self, phase_id: int) -> Dict[str, Any]:
        """
        Get aggregated metrics for a phase.

        Returns:
            Dict with total_runs, successful_runs, avg_duration, etc.
        """
        # Get or create metrics row
        cursor = self.conn.execute(
            "SELECT * FROM phase_metrics WHERE phase_id = ?",
            (phase_id,)
        )
        row = cursor.fetchone()

        if not row:
            # Create initial metrics
            self.conn.execute(
                "INSERT INTO phase_metrics (phase_id) VALUES (?)",
                (phase_id,)
            )
            self.conn.commit()
            return self.get_phase_metrics(phase_id)

        # Recalculate metrics
        cursor = self.conn.execute(
            """
            SELECT
                COUNT(*) as total_runs,
                SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as successful_runs,
                SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed_runs,
                AVG(CASE WHEN duration_seconds IS NOT NULL THEN duration_seconds ELSE NULL END) as avg_duration
            FROM phase_runs
            WHERE phase_id = ?
            """,
            (phase_id,)
        )
        run_metrics = dict(cursor.fetchone())

        # Get task metrics
        cursor = self.conn.execute(
            """
            SELECT
                COUNT(DISTINCT t.id) as total_tasks,
                SUM(CASE WHEN t.status = 'completed' THEN 1 ELSE 0 END) as completed_tasks,
                SUM(CASE WHEN t.status = 'blocked' THEN 1 ELSE 0 END) as blocked_tasks
            FROM tasks t
            JOIN phase_plans pp ON t.phase_plan_id = pp.id
            WHERE pp.phase_id = ?
            """,
            (phase_id,)
        )
        task_metrics = dict(cursor.fetchone())

        # Get quality gate metrics
        cursor = self.conn.execute(
            """
            SELECT
                COUNT(*) as total_gates,
                SUM(CASE WHEN qg.status = 'passed' THEN 1 ELSE 0 END) as passed_gates
            FROM quality_gates qg
            JOIN phase_runs pr ON qg.phase_run_id = pr.id
            WHERE pr.phase_id = ?
            """,
            (phase_id,)
        )
        gate_metrics = dict(cursor.fetchone())

        # Update metrics table
        self.conn.execute(
            """
            UPDATE phase_metrics
            SET total_runs = ?, successful_runs = ?, failed_runs = ?,
                avg_duration_seconds = ?, total_tasks = ?, completed_tasks = ?,
                blocked_tasks = ?, total_quality_gates = ?, passed_quality_gates = ?,
                last_calculated_at = datetime('now')
            WHERE phase_id = ?
            """,
            (
                run_metrics['total_runs'], run_metrics['successful_runs'],
                run_metrics['failed_runs'], run_metrics['avg_duration'],
                task_metrics['total_tasks'], task_metrics['completed_tasks'],
                task_metrics['blocked_tasks'], gate_metrics['total_gates'],
                gate_metrics['passed_gates'], phase_id
            )
        )
        self.conn.commit()

        return {**run_metrics, **task_metrics, **gate_metrics}

    def generate_phase_dashboard(self, phase_id: int) -> Dict[str, Any]:
        """
        Generate a comprehensive dashboard for a phase.

        Returns:
            Dict with current status, recent runs, task progress, etc.
        """
        phase = self.get_phase(phase_id)
        metrics = self.get_phase_metrics(phase_id)
        recent_runs = self.list_phase_runs(phase_id)[:5]

        # Get current approved plan
        approved_plan = None
        if phase and phase['approved_plan_id']:
            approved_plan = self.get_phase_plan(phase['approved_plan_id'])

        # Get task progress
        task_progress = {}
        if approved_plan:
            tasks = self.list_tasks(approved_plan['id'])
            task_progress = {
                'total': len(tasks),
                'pending': sum(1 for t in tasks if t['status'] == 'pending'),
                'in_progress': sum(1 for t in tasks if t['status'] == 'in-progress'),
                'completed': sum(1 for t in tasks if t['status'] == 'completed'),
                'blocked': sum(1 for t in tasks if t['status'] == 'blocked')
            }

        return {
            'phase': phase,
            'metrics': metrics,
            'recent_runs': recent_runs,
            'task_progress': task_progress,
            'approved_plan': approved_plan
        }

    def get_phase_timeline(self, phase_id: int) -> List[Dict[str, Any]]:
        """Get timeline of all events for a phase."""
        timeline = []

        # Phase creation
        phase = self.get_phase(phase_id)
        if phase:
            timeline.append({
                'type': 'phase_created',
                'timestamp': phase['created_at'],
                'data': phase
            })

        # Phase plans
        plans = self.list_phase_plans(phase_id)
        for plan in plans:
            timeline.append({
                'type': 'plan_created',
                'timestamp': plan['created_at'],
                'data': plan
            })
            if plan['approved_at']:
                timeline.append({
                    'type': 'plan_approved',
                    'timestamp': plan['approved_at'],
                    'data': plan
                })

        # Phase runs
        runs = self.list_phase_runs(phase_id)
        for run in runs:
            timeline.append({
                'type': 'run_created',
                'timestamp': run['created_at'],
                'data': run
            })
            if run['started_at']:
                timeline.append({
                    'type': 'run_started',
                    'timestamp': run['started_at'],
                    'data': run
                })
            if run['completed_at']:
                timeline.append({
                    'type': 'run_completed',
                    'timestamp': run['completed_at'],
                    'data': run
                })

        # Sort by timestamp
        timeline.sort(key=lambda x: x['timestamp'])

        return timeline

    # ==================== MIGRATION HELPERS ====================

    def migrate_spec_to_phase(self, spec_id: int) -> int:
        """
        Manually migrate a legacy spec to a phase.

        Args:
            spec_id: Legacy spec ID from specs_legacy table

        Returns:
            New phase ID
        """
        # Get legacy spec
        cursor = self.conn.execute(
            "SELECT * FROM specs_legacy WHERE id = ?",
            (spec_id,)
        )
        spec = cursor.fetchone()
        if not spec:
            raise ValueError(f"Legacy spec {spec_id} not found")

        # Create phase
        phase_id = self.create_phase(
            project_id=spec['project_id'],
            name=spec['name'],
            description=spec['description'],
            phase_type='feature',
            status=spec['status']
        )

        # Create phase plan
        plan_id = self.create_phase_plan(
            phase_id=phase_id,
            planning_approach="Migrated from legacy spec"
        )

        # Migrate documents
        if spec['frd_content']:
            self.add_plan_document(plan_id, 'frd', 'FRD', spec['frd_content'])
        if spec['frs_content']:
            self.add_plan_document(plan_id, 'frs', 'FRS', spec['frs_content'])
        if spec['gs_content']:
            self.add_plan_document(plan_id, 'gs', 'GS', spec['gs_content'])
        if spec['tr_content']:
            self.add_plan_document(plan_id, 'tr', 'TR', spec['tr_content'])
        if spec['task_list_content']:
            self.add_plan_document(plan_id, 'task-list', 'Task List', spec['task_list_content'])

        # Approve plan
        self.approve_phase_plan(plan_id, 'migration')

        self.conn.commit()
        return phase_id

    def list_legacy_specs(self) -> List[Dict[str, Any]]:
        """List all unmigrated legacy specs."""
        cursor = self.conn.execute(
            "SELECT * FROM specs_legacy ORDER BY created_at DESC"
        )
        return [dict(row) for row in cursor.fetchall()]

    # ==================== AGENT CONTEXT CACHING ====================

    def calculate_file_hash(self, content: str) -> str:
        """
        Calculate SHA-256 hash of file content.

        Args:
            content: File content string

        Returns:
            SHA-256 hex string (64 characters)
        """
        import hashlib
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

    def cache_file(
        self,
        file_path: str,
        content: str,
        file_type: str = 'markdown',
        cache_priority: str = 'normal'
    ) -> int:
        """
        Cache a file with SHA-256 hash for invalidation.

        Args:
            file_path: Relative path from project root
            content: File content (UTF-8 text)
            file_type: File type (markdown, text, json)
            cache_priority: Cache priority (high, normal, low)

        Returns:
            Cached file ID (integer)
        """
        content_hash = self.calculate_file_hash(content)
        file_size_bytes = len(content.encode('utf-8'))

        # Check if file already exists
        cursor = self.conn.execute(
            "SELECT id, content_hash FROM cached_files WHERE file_path = ?",
            (file_path,)
        )
        row = cursor.fetchone()

        if row:
            # Update existing entry
            if row['content_hash'] != content_hash:
                # Content changed - update cache
                self.conn.execute(
                    """
                    UPDATE cached_files
                    SET content_hash = ?, content = ?, file_size_bytes = ?,
                        file_type = ?, cache_priority = ?,
                        miss_count = miss_count + 1, updated_at = datetime('now')
                    WHERE file_path = ?
                    """,
                    (content_hash, content, file_size_bytes, file_type, cache_priority, file_path)
                )
            else:
                # Content unchanged - just update priority if needed
                self.conn.execute(
                    """
                    UPDATE cached_files
                    SET cache_priority = ?, updated_at = datetime('now')
                    WHERE file_path = ?
                    """,
                    (cache_priority, file_path)
                )
            self.conn.commit()
            return row['id']
        else:
            # Insert new entry
            cursor = self.conn.execute(
                """
                INSERT INTO cached_files (
                    file_path, content_hash, content, file_size_bytes,
                    file_type, cache_priority
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (file_path, content_hash, content, file_size_bytes, file_type, cache_priority)
            )
            self.conn.commit()
            return cursor.lastrowid

    def get_cached_file(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        Get cached file by path and update access stats.

        Args:
            file_path: Relative path from project root

        Returns:
            Dict with file data or None if not cached
        """
        cursor = self.conn.execute(
            "SELECT * FROM cached_files WHERE file_path = ?",
            (file_path,)
        )
        row = cursor.fetchone()

        if row:
            # Update access stats (cache hit)
            self.conn.execute(
                """
                UPDATE cached_files
                SET access_count = access_count + 1,
                    hit_count = hit_count + 1,
                    last_accessed = datetime('now')
                WHERE file_path = ?
                """,
                (file_path,)
            )
            self.conn.commit()

            # Fetch updated row to return current values
            cursor = self.conn.execute(
                "SELECT * FROM cached_files WHERE file_path = ?",
                (file_path,)
            )
            updated_row = cursor.fetchone()
            return dict(updated_row) if updated_row else None

        return None

    def invalidate_cache(self, file_path: str):
        """
        Invalidate cache entry for a file.

        Args:
            file_path: Relative path from project root
        """
        self.conn.execute(
            "DELETE FROM cached_files WHERE file_path = ?",
            (file_path,)
        )
        self.conn.commit()

    def update_file_access(self, file_path: str, cache_hit: bool):
        """
        Update file access statistics.

        Args:
            file_path: Relative path from project root
            cache_hit: True if cache hit, False if cache miss
        """
        if cache_hit:
            self.conn.execute(
                """
                UPDATE cached_files
                SET access_count = access_count + 1,
                    hit_count = hit_count + 1,
                    last_accessed = datetime('now')
                WHERE file_path = ?
                """,
                (file_path,)
            )
        else:
            self.conn.execute(
                """
                UPDATE cached_files
                SET access_count = access_count + 1,
                    miss_count = miss_count + 1,
                    last_accessed = datetime('now')
                WHERE file_path = ?
                """,
                (file_path,)
            )
        self.conn.commit()

    # ==================== AGENT INVOCATION TRACKING ====================

    def create_agent_invocation(
        self,
        agent_name: str,
        purpose: str,
        phase_run_id: Optional[int] = None,
        task_run_id: Optional[int] = None,
        parent_invocation_id: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Create a new agent invocation record.

        Args:
            agent_name: Agent name (e.g., 'nextjs-backend-developer')
            purpose: Purpose (planning, implementation, review, testing, documentation)
            phase_run_id: Optional FK to phase_runs
            task_run_id: Optional FK to task_runs
            parent_invocation_id: Optional parent invocation for nested agents
            metadata: Optional JSON metadata

        Returns:
            Invocation ID (integer)
        """
        metadata_json = json.dumps(metadata) if metadata else None

        cursor = self.conn.execute(
            """
            INSERT INTO agent_invocations (
                agent_name, purpose, phase_run_id, task_run_id,
                parent_invocation_id, metadata, status
            )
            VALUES (?, ?, ?, ?, ?, ?, 'in-progress')
            """,
            (agent_name, purpose, phase_run_id, task_run_id, parent_invocation_id, metadata_json)
        )
        self.conn.commit()
        return cursor.lastrowid

    def complete_agent_invocation(
        self,
        invocation_id: int,
        status: str = 'completed',
        error_message: Optional[str] = None,
        summary: Optional[str] = None
    ):
        """
        Mark agent invocation as completed.

        Args:
            invocation_id: Invocation ID
            status: Status (completed, failed, cancelled)
            error_message: Optional error message if failed
            summary: Optional summary of work done
        """
        valid_statuses = ['completed', 'failed', 'cancelled']
        if status not in valid_statuses:
            raise ValueError(f"Status must be one of: {valid_statuses}")

        self.conn.execute(
            """
            UPDATE agent_invocations
            SET status = ?, error_message = ?, summary = ?, completed_at = datetime('now')
            WHERE id = ?
            """,
            (status, error_message, summary, invocation_id)
        )
        self.conn.commit()

    def get_agent_invocation(self, invocation_id: int) -> Optional[Dict[str, Any]]:
        """Get agent invocation by ID."""
        cursor = self.conn.execute(
            "SELECT * FROM agent_invocations WHERE id = ?",
            (invocation_id,)
        )
        row = cursor.fetchone()
        return dict(row) if row else None

    def list_agent_invocations(
        self,
        agent_name: Optional[str] = None,
        status: Optional[str] = None,
        phase_run_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """List agent invocations with optional filters."""
        query = "SELECT * FROM agent_invocations WHERE 1=1"
        params = []

        if agent_name is not None:
            query += " AND agent_name = ?"
            params.append(agent_name)

        if status is not None:
            query += " AND status = ?"
            params.append(status)

        if phase_run_id is not None:
            query += " AND phase_run_id = ?"
            params.append(phase_run_id)

        query += " ORDER BY started_at DESC"

        cursor = self.conn.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

    def log_file_read(
        self,
        invocation_id: int,
        file_path: str,
        cache_status: str,
        file_size_bytes: int
    ) -> int:
        """
        Log a file read by an agent.

        Args:
            invocation_id: Agent invocation ID
            file_path: File path that was read
            cache_status: Cache status (hit, miss, error)
            file_size_bytes: File size in bytes

        Returns:
            File read log ID (integer)
        """
        estimated_tokens = file_size_bytes // 4  # Rough estimate

        cursor = self.conn.execute(
            """
            INSERT INTO agent_file_reads (
                invocation_id, file_path, cache_status,
                file_size_bytes, estimated_tokens
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (invocation_id, file_path, cache_status, file_size_bytes, estimated_tokens)
        )

        # Update invocation stats
        if cache_status == 'hit':
            self.conn.execute(
                """
                UPDATE agent_invocations
                SET total_files_read = total_files_read + 1,
                    cache_hits = cache_hits + 1,
                    estimated_tokens_used = estimated_tokens_used + ?
                WHERE id = ?
                """,
                (estimated_tokens, invocation_id)
            )
        elif cache_status == 'miss':
            self.conn.execute(
                """
                UPDATE agent_invocations
                SET total_files_read = total_files_read + 1,
                    cache_misses = cache_misses + 1,
                    estimated_tokens_used = estimated_tokens_used + ?
                WHERE id = ?
                """,
                (estimated_tokens, invocation_id)
            )

        self.conn.commit()
        return cursor.lastrowid

    def get_agent_file_reads(self, invocation_id: int) -> List[Dict[str, Any]]:
        """Get all file reads for an invocation."""
        cursor = self.conn.execute(
            "SELECT * FROM agent_file_reads WHERE invocation_id = ? ORDER BY read_at",
            (invocation_id,)
        )
        return [dict(row) for row in cursor.fetchall()]

    # ==================== CHECKLIST MANAGEMENT ====================

    def create_checklist(
        self,
        invocation_id: int,
        checklist_name: str,
        total_items: int,
        template_name: Optional[str] = None,
        template_version: Optional[int] = None
    ) -> int:
        """
        Create a new checklist.

        Args:
            invocation_id: Agent invocation ID
            checklist_name: Checklist name
            total_items: Total number of items in checklist
            template_name: Optional template name
            template_version: Optional template version

        Returns:
            Checklist ID (integer)
        """
        cursor = self.conn.execute(
            """
            INSERT INTO checklists (
                invocation_id, checklist_name, total_items,
                template_name, template_version, status
            )
            VALUES (?, ?, ?, ?, ?, 'in-progress')
            """,
            (invocation_id, checklist_name, total_items, template_name, template_version)
        )

        # Update agent invocation with checklist link
        checklist_id = cursor.lastrowid
        self.conn.execute(
            "UPDATE agent_invocations SET checklist_id = ? WHERE id = ?",
            (checklist_id, invocation_id)
        )

        self.conn.commit()
        return checklist_id

    def create_checklist_items(
        self,
        checklist_id: int,
        items: List[Dict[str, Any]]
    ) -> List[int]:
        """
        Bulk create checklist items.

        Args:
            checklist_id: Checklist ID
            items: List of item dicts with keys:
                   - description (required)
                   - item_order (required)
                   - item_key (optional)
                   - category (optional)
                   - priority (optional, default: medium)
                   - verification_type (optional, default: manual)

        Returns:
            List of item IDs
        """
        item_ids = []
        for item in items:
            cursor = self.conn.execute(
                """
                INSERT INTO checklist_items (
                    checklist_id, item_order, item_key, description,
                    category, priority, verification_type, status
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, 'pending')
                """,
                (
                    checklist_id,
                    item['item_order'],
                    item.get('item_key'),
                    item['description'],
                    item.get('category'),
                    item.get('priority', 'medium'),
                    item.get('verification_type', 'manual')
                )
            )
            item_ids.append(cursor.lastrowid)

        self.conn.commit()
        return item_ids

    def update_checklist_item(
        self,
        item_id: int,
        status: str,
        notes: Optional[str] = None
    ):
        """
        Update checklist item status.

        Args:
            item_id: Checklist item ID
            status: New status (pending, in-progress, completed, failed, skipped)
            notes: Optional notes
        """
        valid_statuses = ['pending', 'in-progress', 'completed', 'failed', 'skipped']
        if status not in valid_statuses:
            raise ValueError(f"Status must be one of: {valid_statuses}")

        # Get current status to check if this is a transition to completed
        cursor = self.conn.execute(
            "SELECT status, started_at FROM checklist_items WHERE id = ?",
            (item_id,)
        )
        row = cursor.fetchone()

        if not row:
            raise ValueError(f"Checklist item {item_id} not found")

        old_status = row['status']
        started_at = row['started_at']

        # Update item
        updates = ["status = ?", "notes = ?"]
        params = [status, notes]

        # Set started_at if transitioning to in-progress
        if status == 'in-progress' and old_status == 'pending':
            updates.append("started_at = datetime('now')")

        # Set completed_at if transitioning to terminal state
        if status in ['completed', 'failed', 'skipped'] and old_status not in ['completed', 'failed', 'skipped']:
            updates.append("completed_at = datetime('now')")

        params.append(item_id)

        self.conn.execute(
            f"UPDATE checklist_items SET {', '.join(updates)} WHERE id = ?",
            params
        )
        self.conn.commit()

    def get_checklist_progress(self, checklist_id: int) -> Dict[str, Any]:
        """
        Get checklist progress summary.

        Returns:
            Dict with completed_items, total_items, completion_percent, etc.
        """
        cursor = self.conn.execute(
            "SELECT * FROM checklists WHERE id = ?",
            (checklist_id,)
        )
        row = cursor.fetchone()
        return dict(row) if row else None

    def get_checklist(self, checklist_id: int) -> Optional[Dict[str, Any]]:
        """Get full checklist with all items."""
        checklist = self.get_checklist_progress(checklist_id)
        if not checklist:
            return None

        # Get all items
        cursor = self.conn.execute(
            "SELECT * FROM checklist_items WHERE checklist_id = ? ORDER BY item_order",
            (checklist_id,)
        )
        items = [dict(row) for row in cursor.fetchall()]

        return {
            **checklist,
            'items': items
        }

    def complete_checklist(self, checklist_id: int, status: str = 'completed'):
        """
        Mark checklist as completed.

        Args:
            checklist_id: Checklist ID
            status: Final status (completed, partial, failed)
        """
        valid_statuses = ['completed', 'partial', 'failed']
        if status not in valid_statuses:
            raise ValueError(f"Status must be one of: {valid_statuses}")

        self.conn.execute(
            """
            UPDATE checklists
            SET status = ?, completed_at = datetime('now')
            WHERE id = ?
            """,
            (status, checklist_id)
        )
        self.conn.commit()

    # ==================== CHECKLIST VERIFICATION ====================

    def add_checklist_verification(
        self,
        checklist_item_id: int,
        result: str,
        verification_method: str,
        verified_by: str,
        evidence_text: Optional[str] = None,
        evidence_file_path: Optional[str] = None,
        quality_gate_id: Optional[int] = None
    ) -> int:
        """
        Add a verification outcome for a checklist item.

        Args:
            checklist_item_id: Checklist item ID
            result: Verification result (passed, failed, warning, skipped)
            verification_method: Method used (manual, automated, tool-based)
            verified_by: Agent name or user
            evidence_text: Optional evidence text
            evidence_file_path: Optional evidence file path
            quality_gate_id: Optional quality gate ID

        Returns:
            Verification ID (integer)
        """
        cursor = self.conn.execute(
            """
            INSERT INTO checklist_verifications (
                checklist_item_id, result, verification_method, verified_by,
                evidence_text, evidence_file_path, quality_gate_id
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (checklist_item_id, result, verification_method, verified_by,
             evidence_text, evidence_file_path, quality_gate_id)
        )
        self.conn.commit()
        return cursor.lastrowid

    def get_checklist_verifications(self, checklist_item_id: int) -> List[Dict[str, Any]]:
        """Get all verifications for a checklist item."""
        cursor = self.conn.execute(
            "SELECT * FROM checklist_verifications WHERE checklist_item_id = ? ORDER BY verified_at",
            (checklist_item_id,)
        )
        return [dict(row) for row in cursor.fetchall()]

    # ==================== CHECKLIST TEMPLATES ====================

    def create_checklist_template(
        self,
        name: str,
        agent_type: str,
        items: List[Dict[str, Any]],
        description: Optional[str] = None,
        version: int = 1
    ) -> int:
        """
        Create a reusable checklist template.

        Args:
            name: Template name (unique)
            agent_type: Agent type (e.g., 'code-reviewer')
            items: List of template items (JSON serializable)
            description: Optional description
            version: Template version (default 1)

        Returns:
            Template ID (integer)
        """
        items_json = json.dumps(items)
        total_items = len(items)

        cursor = self.conn.execute(
            """
            INSERT INTO checklist_templates (
                name, version, agent_type, description, items, total_items
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (name, version, agent_type, description, items_json, total_items)
        )
        self.conn.commit()
        return cursor.lastrowid

    def get_checklist_template(
        self,
        name: str,
        version: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get checklist template by name and optional version.

        Args:
            name: Template name
            version: Optional version (gets latest if None)

        Returns:
            Dict with template data or None
        """
        if version is not None:
            cursor = self.conn.execute(
                "SELECT * FROM checklist_templates WHERE name = ? AND version = ? AND is_active = 1",
                (name, version)
            )
        else:
            cursor = self.conn.execute(
                """
                SELECT * FROM checklist_templates
                WHERE name = ? AND is_active = 1
                ORDER BY version DESC
                LIMIT 1
                """,
                (name,)
            )

        row = cursor.fetchone()
        if row:
            result = dict(row)
            # Parse items JSON
            result['items'] = json.loads(result['items'])
            return result
        return None

    def list_checklist_templates(
        self,
        agent_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List checklist templates, optionally filtered by agent type."""
        if agent_type is not None:
            cursor = self.conn.execute(
                """
                SELECT * FROM checklist_templates
                WHERE agent_type = ? AND is_active = 1
                ORDER BY name, version DESC
                """,
                (agent_type,)
            )
        else:
            cursor = self.conn.execute(
                "SELECT * FROM checklist_templates WHERE is_active = 1 ORDER BY name, version DESC"
            )

        results = []
        for row in cursor.fetchall():
            result = dict(row)
            # Parse items JSON
            result['items'] = json.loads(result['items'])
            results.append(result)

        return results

    # ==================== CACHE STATISTICS ====================

    def get_cache_stats(
        self,
        stat_date: Optional[str] = None,
        file_path: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get cache statistics for a date and optional file.

        Args:
            stat_date: Date string (YYYY-MM-DD), defaults to today
            file_path: Optional file path for per-file stats

        Returns:
            Dict with cache statistics or None
        """
        if stat_date is None:
            stat_date = datetime.now().strftime('%Y-%m-%d')

        cursor = self.conn.execute(
            """
            SELECT * FROM cache_statistics
            WHERE stat_date = ? AND file_path IS ?
            """,
            (stat_date, file_path)
        )
        row = cursor.fetchone()
        return dict(row) if row else None

    def update_cache_statistics(
        self,
        stat_date: str,
        file_path: Optional[str],
        total_reads: int,
        cache_hits: int,
        cache_misses: int,
        tokens_saved: int,
        avg_lookup_time_ms: float
    ):
        """
        Update cache statistics for a date and file.

        Args:
            stat_date: Date string (YYYY-MM-DD)
            file_path: Optional file path (None for global stats)
            total_reads: Total number of reads
            cache_hits: Number of cache hits
            cache_misses: Number of cache misses
            tokens_saved: Estimated tokens saved
            avg_lookup_time_ms: Average lookup time in milliseconds
        """
        hit_rate_percent = (cache_hits / total_reads * 100.0) if total_reads > 0 else 0.0

        # Check if record exists
        cursor = self.conn.execute(
            """
            SELECT id FROM cache_statistics
            WHERE stat_date = ? AND file_path IS ?
            """,
            (stat_date, file_path)
        )
        row = cursor.fetchone()

        if row:
            # Update existing
            self.conn.execute(
                """
                UPDATE cache_statistics
                SET total_reads = ?, cache_hits = ?, cache_misses = ?,
                    hit_rate_percent = ?, tokens_saved = ?, avg_lookup_time_ms = ?
                WHERE stat_date = ? AND file_path IS ?
                """,
                (total_reads, cache_hits, cache_misses, hit_rate_percent,
                 tokens_saved, avg_lookup_time_ms, stat_date, file_path)
            )
        else:
            # Insert new
            self.conn.execute(
                """
                INSERT INTO cache_statistics (
                    stat_date, file_path, total_reads, cache_hits, cache_misses,
                    hit_rate_percent, tokens_saved, avg_lookup_time_ms
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (stat_date, file_path, total_reads, cache_hits, cache_misses,
                 hit_rate_percent, tokens_saved, avg_lookup_time_ms)
            )

        self.conn.commit()

    def get_agent_metrics(
        self,
        agent_name: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get aggregated metrics for agent invocations.

        Args:
            agent_name: Optional agent name filter
            start_date: Optional start date (YYYY-MM-DD)
            end_date: Optional end date (YYYY-MM-DD)

        Returns:
            Dict with metrics (total_invocations, avg_files_read, cache_hit_rate, etc.)
        """
        query = "SELECT * FROM agent_invocations WHERE 1=1"
        params = []

        if agent_name is not None:
            query += " AND agent_name = ?"
            params.append(agent_name)

        if start_date is not None:
            query += " AND DATE(started_at) >= ?"
            params.append(start_date)

        if end_date is not None:
            query += " AND DATE(started_at) <= ?"
            params.append(end_date)

        cursor = self.conn.execute(query, params)
        invocations = [dict(row) for row in cursor.fetchall()]

        if not invocations:
            return {
                'total_invocations': 0,
                'completed': 0,
                'failed': 0,
                'avg_files_read': 0.0,
                'avg_cache_hits': 0.0,
                'avg_cache_misses': 0.0,
                'cache_hit_rate': 0.0,
                'total_tokens_used': 0,
                'avg_duration_seconds': 0.0
            }

        total = len(invocations)
        completed = sum(1 for i in invocations if i['status'] == 'completed')
        failed = sum(1 for i in invocations if i['status'] == 'failed')

        total_files = sum(i['total_files_read'] for i in invocations)
        total_hits = sum(i['cache_hits'] for i in invocations)
        total_misses = sum(i['cache_misses'] for i in invocations)
        total_tokens = sum(i['estimated_tokens_used'] for i in invocations)

        # Calculate average duration for completed invocations
        completed_invs = [i for i in invocations if i['duration_seconds'] is not None]
        avg_duration = sum(i['duration_seconds'] for i in completed_invs) / len(completed_invs) if completed_invs else 0.0

        cache_hit_rate = (total_hits / (total_hits + total_misses) * 100.0) if (total_hits + total_misses) > 0 else 0.0

        return {
            'total_invocations': total,
            'completed': completed,
            'failed': failed,
            'avg_files_read': total_files / total,
            'avg_cache_hits': total_hits / total,
            'avg_cache_misses': total_misses / total,
            'cache_hit_rate': cache_hit_rate,
            'total_tokens_used': total_tokens,
            'avg_duration_seconds': avg_duration
        }
