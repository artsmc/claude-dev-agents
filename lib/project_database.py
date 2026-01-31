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
    project_id = db.create_project("my-app", "My application project", "/path/to/app")

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
        description: Optional[str] = None,
        filesystem_path: Optional[str] = None
    ) -> int:
        """
        Create a new project.

        Args:
            name: Unique project name (e.g., "message-well")
            description: Optional project description
            filesystem_path: Absolute path to project folder

        Returns:
            Project ID (integer)

        Raises:
            ValueError: If name is empty or filesystem_path is invalid
            sqlite3.IntegrityError: If project name already exists
        """
        if not name or not name.strip():
            raise ValueError("Project name cannot be empty")

        if filesystem_path and not Path(filesystem_path).is_absolute():
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
