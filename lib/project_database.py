"""
ProjectDatabase - SQLite abstraction layer for project management tracking.

Provides a complete Python API for managing projects, specifications, jobs,
tasks, code reviews, agent assignments, and execution logs.

Zero external dependencies - uses only Python standard library.

Usage:
    from lib.project_database import ProjectDatabase

    db = ProjectDatabase()  # Opens ~/.claude/projects.db

    # Create a project
    project_id = db.create_project("my-app", "My application project", "/path/to/app")

    # Use as context manager
    with ProjectDatabase() as db:
        job_id = db.create_job(spec_id=1, name="Build feature", assigned_agent="python-backend")
        db.start_job(job_id)
        # ... work happens ...
        db.complete_job(job_id, exit_code=0)
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any, Tuple
from contextlib import contextmanager


class ProjectDatabase:
    """
    SQLite database abstraction for project management tracking.

    Provides methods for:
    - Project and specification management
    - Job and task tracking
    - Code review recording
    - Agent assignment tracking
    - Execution logging
    - Dashboard and reporting

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
                db.create_spec(...)
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
            filesystem_path: Absolute path to project folder for Memory Bank exports
                           (e.g., "/home/mark/applications/message-well/")

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
        """
        Get project by ID.

        Args:
            project_id: Project ID

        Returns:
            Project dict or None if not found
        """
        cursor = self.conn.execute(
            "SELECT * FROM projects WHERE id = ?",
            (project_id,)
        )
        row = cursor.fetchone()
        return dict(row) if row else None

    def get_project_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get project by name.

        Args:
            name: Project name

        Returns:
            Project dict or None if not found
        """
        cursor = self.conn.execute(
            "SELECT * FROM projects WHERE name = ?",
            (name,)
        )
        row = cursor.fetchone()
        return dict(row) if row else None

    def list_projects(self) -> List[Dict[str, Any]]:
        """
        List all projects.

        Returns:
            List of project dicts
        """
        cursor = self.conn.execute(
            "SELECT * FROM projects ORDER BY created_at DESC"
        )
        return [dict(row) for row in cursor.fetchall()]

    # ==================== SPEC MANAGEMENT ====================

    def create_spec(
        self,
        project_id: int,
        name: str,
        frd_content: Optional[str] = None,
        frs_content: Optional[str] = None,
        gs_content: Optional[str] = None,
        tr_content: Optional[str] = None,
        task_list_content: Optional[str] = None,
        status: str = "draft"
    ) -> int:
        """
        Create a new specification.

        Args:
            project_id: Foreign key to projects table
            name: Spec name (e.g., "feature-auth")
            frd_content: Full text of FRD.md
            frs_content: Full text of FRS.md
            gs_content: Full text of GS.md
            tr_content: Full text of TR.md
            task_list_content: Full text of task-list.md
            status: Spec status (draft, approved, in-progress, completed)

        Returns:
            Spec ID (integer)

        Raises:
            ValueError: If project_id or name is invalid
            sqlite3.IntegrityError: If spec already exists for this project
        """
        if not name or not name.strip():
            raise ValueError("Spec name cannot be empty")

        valid_statuses = ['draft', 'approved', 'in-progress', 'completed']
        if status not in valid_statuses:
            raise ValueError(f"Status must be one of: {valid_statuses}")

        cursor = self.conn.execute(
            """
            INSERT INTO specs (
                project_id, name, status,
                frd_content, frs_content, gs_content, tr_content, task_list_content
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (project_id, name.strip(), status,
             frd_content, frs_content, gs_content, tr_content, task_list_content)
        )
        self.conn.commit()
        return cursor.lastrowid

    def get_spec(self, spec_id: int) -> Optional[Dict[str, Any]]:
        """
        Get specification by ID.

        Args:
            spec_id: Spec ID

        Returns:
            Spec dict or None if not found
        """
        cursor = self.conn.execute(
            "SELECT * FROM specs WHERE id = ?",
            (spec_id,)
        )
        row = cursor.fetchone()
        return dict(row) if row else None

    def list_specs(self, project_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        List specifications, optionally filtered by project.

        Args:
            project_id: Optional project ID to filter by

        Returns:
            List of spec dicts
        """
        if project_id is not None:
            cursor = self.conn.execute(
                "SELECT * FROM specs WHERE project_id = ? ORDER BY created_at DESC",
                (project_id,)
            )
        else:
            cursor = self.conn.execute(
                "SELECT * FROM specs ORDER BY created_at DESC"
            )
        return [dict(row) for row in cursor.fetchall()]

    # ==================== JOB MANAGEMENT ====================

    def create_job(
        self,
        spec_id: Optional[int],
        name: str,
        priority: str = "normal",
        assigned_agent: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> int:
        """
        Create a new job.

        Args:
            spec_id: Foreign key to specs table (nullable)
            name: Job name (e.g., "Build auth feature")
            priority: Job priority (low, normal, high, critical)
            assigned_agent: Agent type assigned to job
            session_id: Unique session identifier

        Returns:
            Job ID (integer)

        Raises:
            ValueError: If name is empty or priority invalid
        """
        if not name or not name.strip():
            raise ValueError("Job name cannot be empty")

        valid_priorities = ['low', 'normal', 'high', 'critical']
        if priority not in valid_priorities:
            raise ValueError(f"Priority must be one of: {valid_priorities}")

        cursor = self.conn.execute(
            """
            INSERT INTO jobs (spec_id, name, priority, assigned_agent, session_id)
            VALUES (?, ?, ?, ?, ?)
            """,
            (spec_id, name.strip(), priority, assigned_agent, session_id)
        )
        self.conn.commit()
        return cursor.lastrowid

    def update_job_status(
        self,
        job_id: int,
        status: str,
        exit_code: Optional[int] = None,
        summary: Optional[str] = None
    ):
        """
        Update job status.

        Args:
            job_id: Job ID
            status: New status (pending, in-progress, completed, failed, blocked)
            exit_code: Optional exit code
            summary: Optional summary text

        Raises:
            ValueError: If status is invalid
        """
        valid_statuses = ['pending', 'in-progress', 'completed', 'failed', 'blocked']
        if status not in valid_statuses:
            raise ValueError(f"Status must be one of: {valid_statuses}")

        self.conn.execute(
            """
            UPDATE jobs
            SET status = ?, exit_code = ?, summary = ?, last_activity_at = datetime('now')
            WHERE id = ?
            """,
            (status, exit_code, summary, job_id)
        )
        self.conn.commit()

    def start_job(self, job_id: int):
        """
        Mark job as started.

        Args:
            job_id: Job ID
        """
        self.conn.execute(
            """
            UPDATE jobs
            SET status = 'in-progress',
                started_at = datetime('now'),
                last_activity_at = datetime('now')
            WHERE id = ?
            """,
            (job_id,)
        )
        self.conn.commit()

    def complete_job(self, job_id: int, exit_code: int = 0, summary: Optional[str] = None):
        """
        Mark job as completed.

        Args:
            job_id: Job ID
            exit_code: Exit code (0 = success, non-zero = failure)
            summary: Optional completion summary
        """
        status = 'completed' if exit_code == 0 else 'failed'

        self.conn.execute(
            """
            UPDATE jobs
            SET status = ?,
                exit_code = ?,
                summary = ?,
                completed_at = datetime('now'),
                last_activity_at = datetime('now')
            WHERE id = ?
            """,
            (status, exit_code, summary, job_id)
        )
        self.conn.commit()

    def get_job(self, job_id: int) -> Optional[Dict[str, Any]]:
        """
        Get job by ID.

        Args:
            job_id: Job ID

        Returns:
            Job dict or None if not found
        """
        cursor = self.conn.execute(
            "SELECT * FROM jobs WHERE id = ?",
            (job_id,)
        )
        row = cursor.fetchone()
        return dict(row) if row else None

    def list_jobs(
        self,
        spec_id: Optional[int] = None,
        status: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        List jobs with optional filters.

        Args:
            spec_id: Optional spec ID to filter by
            status: Optional status to filter by
            limit: Maximum number of jobs to return

        Returns:
            List of job dicts
        """
        query = "SELECT * FROM jobs WHERE 1=1"
        params = []

        if spec_id is not None:
            query += " AND spec_id = ?"
            params.append(spec_id)

        if status is not None:
            query += " AND status = ?"
            params.append(status)

        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)

        cursor = self.conn.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

    # ==================== TASK MANAGEMENT ====================

    def create_task(
        self,
        job_id: int,
        name: str,
        order: int = 0,
        dependencies: Optional[str] = None
    ) -> int:
        """
        Create a new task.

        Args:
            job_id: Foreign key to jobs table
            name: Task name
            order: Task execution order
            dependencies: Optional JSON array of task IDs this depends on

        Returns:
            Task ID (integer)

        Raises:
            ValueError: If name is empty
        """
        if not name or not name.strip():
            raise ValueError("Task name cannot be empty")

        cursor = self.conn.execute(
            """
            INSERT INTO tasks (job_id, name, `order`, dependencies)
            VALUES (?, ?, ?, ?)
            """,
            (job_id, name.strip(), order, dependencies)
        )
        self.conn.commit()
        return cursor.lastrowid

    def update_task_status(
        self,
        task_id: int,
        status: str,
        exit_code: Optional[int] = None
    ):
        """
        Update task status.

        Args:
            task_id: Task ID
            status: New status (pending, in-progress, completed, failed, blocked)
            exit_code: Optional exit code

        Raises:
            ValueError: If status is invalid
        """
        valid_statuses = ['pending', 'in-progress', 'completed', 'failed', 'blocked']
        if status not in valid_statuses:
            raise ValueError(f"Status must be one of: {valid_statuses}")

        self.conn.execute(
            """
            UPDATE tasks
            SET status = ?, exit_code = ?
            WHERE id = ?
            """,
            (status, exit_code, task_id)
        )
        self.conn.commit()

    def start_task(self, task_id: int):
        """
        Mark task as started.

        Args:
            task_id: Task ID
        """
        self.conn.execute(
            """
            UPDATE tasks
            SET status = 'in-progress',
                started_at = datetime('now')
            WHERE id = ?
            """,
            (task_id,)
        )
        self.conn.commit()

    def complete_task(self, task_id: int, exit_code: int = 0):
        """
        Mark task as completed.

        Args:
            task_id: Task ID
            exit_code: Exit code (0 = success, non-zero = failure)
        """
        status = 'completed' if exit_code == 0 else 'failed'

        self.conn.execute(
            """
            UPDATE tasks
            SET status = ?,
                exit_code = ?,
                completed_at = datetime('now')
            WHERE id = ?
            """,
            (status, exit_code, task_id)
        )
        self.conn.commit()

    def get_tasks(self, job_id: int) -> List[Dict[str, Any]]:
        """
        Get all tasks for a job.

        Args:
            job_id: Job ID

        Returns:
            List of task dicts ordered by execution order
        """
        cursor = self.conn.execute(
            "SELECT * FROM tasks WHERE job_id = ? ORDER BY `order`",
            (job_id,)
        )
        return [dict(row) for row in cursor.fetchall()]

    # ==================== CODE REVIEW MANAGEMENT ====================

    def add_code_review(
        self,
        job_id: Optional[int],
        task_id: Optional[int],
        reviewer: str,
        summary: str,
        verdict: str,
        issues_found: Optional[str] = None,
        files_reviewed: Optional[str] = None
    ) -> int:
        """
        Add a code review record.

        Args:
            job_id: Optional foreign key to jobs table
            task_id: Optional foreign key to tasks table
            reviewer: Reviewer name or agent type
            summary: Review summary text
            verdict: Review verdict (approved, changes-requested, rejected)
            issues_found: Optional JSON array of issues
            files_reviewed: Optional JSON array of files

        Returns:
            Review ID (integer)

        Raises:
            ValueError: If reviewer/summary empty or verdict invalid
        """
        if not reviewer or not reviewer.strip():
            raise ValueError("Reviewer cannot be empty")

        if not summary or not summary.strip():
            raise ValueError("Summary cannot be empty")

        valid_verdicts = ['approved', 'changes-requested', 'rejected']
        if verdict not in valid_verdicts:
            raise ValueError(f"Verdict must be one of: {valid_verdicts}")

        cursor = self.conn.execute(
            """
            INSERT INTO code_reviews (
                job_id, task_id, reviewer, summary, verdict,
                issues_found, files_reviewed
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (job_id, task_id, reviewer.strip(), summary.strip(), verdict,
             issues_found, files_reviewed)
        )
        self.conn.commit()
        return cursor.lastrowid

    def get_code_reviews(
        self,
        job_id: Optional[int] = None,
        task_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get code reviews, optionally filtered by job or task.

        Args:
            job_id: Optional job ID to filter by
            task_id: Optional task ID to filter by

        Returns:
            List of code review dicts
        """
        query = "SELECT * FROM code_reviews WHERE 1=1"
        params = []

        if job_id is not None:
            query += " AND job_id = ?"
            params.append(job_id)

        if task_id is not None:
            query += " AND task_id = ?"
            params.append(task_id)

        query += " ORDER BY created_at DESC"

        cursor = self.conn.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

    # ==================== AGENT ASSIGNMENT MANAGEMENT ====================

    def assign_agent(
        self,
        agent_type: str,
        job_id: Optional[int] = None,
        task_id: Optional[int] = None
    ) -> int:
        """
        Record an agent assignment.

        Args:
            agent_type: Type of agent (e.g., "python-backend-developer")
            job_id: Optional job ID
            task_id: Optional task ID

        Returns:
            Assignment ID (integer)

        Raises:
            ValueError: If agent_type is empty or both job_id and task_id are None
        """
        if not agent_type or not agent_type.strip():
            raise ValueError("Agent type cannot be empty")

        if job_id is None and task_id is None:
            raise ValueError("At least one of job_id or task_id must be provided")

        cursor = self.conn.execute(
            """
            INSERT INTO agent_assignments (agent_type, job_id, task_id)
            VALUES (?, ?, ?)
            """,
            (agent_type.strip(), job_id, task_id)
        )
        self.conn.commit()
        return cursor.lastrowid

    def complete_agent_work(self, assignment_id: int, exit_code: int = 0):
        """
        Mark agent assignment as completed.

        Args:
            assignment_id: Assignment ID
            exit_code: Exit code (0 = success, non-zero = failure)
        """
        status = 'completed' if exit_code == 0 else 'failed'

        self.conn.execute(
            """
            UPDATE agent_assignments
            SET status = ?,
                completed_at = datetime('now')
            WHERE id = ?
            """,
            (status, assignment_id)
        )
        self.conn.commit()

    def get_agent_assignments(
        self,
        job_id: Optional[int] = None,
        task_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get agent assignments, optionally filtered by job or task.

        Args:
            job_id: Optional job ID to filter by
            task_id: Optional task ID to filter by

        Returns:
            List of agent assignment dicts
        """
        query = "SELECT * FROM agent_assignments WHERE 1=1"
        params = []

        if job_id is not None:
            query += " AND job_id = ?"
            params.append(job_id)

        if task_id is not None:
            query += " AND task_id = ?"
            params.append(task_id)

        query += " ORDER BY assigned_at DESC"

        cursor = self.conn.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

    # ==================== EXECUTION LOGGING ====================

    def log_execution(
        self,
        job_id: int,
        task_id: Optional[int],
        command: str,
        output: Optional[str] = None,
        exit_code: Optional[int] = None,
        duration_ms: Optional[int] = None
    ) -> int:
        """
        Log a command execution.

        Args:
            job_id: Job ID
            task_id: Optional task ID
            command: Command that was executed
            output: Optional command output (stdout + stderr)
            exit_code: Optional exit code
            duration_ms: Optional duration in milliseconds

        Returns:
            Log ID (integer)

        Raises:
            ValueError: If command is empty
        """
        if not command or not command.strip():
            raise ValueError("Command cannot be empty")

        # Truncate output if too large (> 50KB)
        if output and len(output) > 50000:
            output = output[:50000] + "\n... (truncated)"

        cursor = self.conn.execute(
            """
            INSERT INTO execution_logs (
                job_id, task_id, command, output, exit_code, duration_ms
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (job_id, task_id, command.strip(), output, exit_code, duration_ms)
        )
        self.conn.commit()
        return cursor.lastrowid

    def get_execution_logs(
        self,
        job_id: Optional[int] = None,
        task_id: Optional[int] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get execution logs, optionally filtered by job or task.

        Args:
            job_id: Optional job ID to filter by
            task_id: Optional task ID to filter by
            limit: Maximum number of logs to return

        Returns:
            List of execution log dicts
        """
        query = "SELECT * FROM execution_logs WHERE 1=1"
        params = []

        if job_id is not None:
            query += " AND job_id = ?"
            params.append(job_id)

        if task_id is not None:
            query += " AND task_id = ?"
            params.append(task_id)

        query += " ORDER BY executed_at DESC LIMIT ?"
        params.append(limit)

        cursor = self.conn.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

    # ==================== REPORTING AND QUERIES ====================

    def generate_dashboard(self) -> Dict[str, Any]:
        """
        Generate status dashboard with job metrics.

        Returns:
            Dashboard dict with active jobs, recent completions, and velocity
        """
        # Active jobs
        active_jobs = self.list_jobs(status='in-progress')
        pending_jobs = self.list_jobs(status='pending')

        # Recent completions (last 7 days)
        cursor = self.conn.execute(
            """
            SELECT * FROM jobs
            WHERE status IN ('completed', 'failed')
            AND completed_at >= datetime('now', '-7 days')
            ORDER BY completed_at DESC
            """
        )
        recent_completions = [dict(row) for row in cursor.fetchall()]

        # Velocity metrics (this week vs last week)
        cursor = self.conn.execute(
            """
            SELECT
                SUM(CASE WHEN completed_at >= datetime('now', '-7 days') THEN 1 ELSE 0 END) as this_week,
                SUM(CASE WHEN completed_at >= datetime('now', '-14 days')
                     AND completed_at < datetime('now', '-7 days') THEN 1 ELSE 0 END) as last_week
            FROM jobs
            WHERE status = 'completed'
            """
        )
        row = cursor.fetchone()
        this_week = row['this_week'] or 0
        last_week = row['last_week'] or 0

        velocity_trend = 0
        if last_week > 0:
            velocity_trend = ((this_week - last_week) / last_week) * 100

        return {
            'active_jobs': active_jobs,
            'pending_jobs': pending_jobs,
            'recent_completions': recent_completions,
            'velocity': {
                'this_week': this_week,
                'last_week': last_week,
                'trend_percent': round(velocity_trend, 1)
            }
        }

    def get_job_timeline(self, job_id: int) -> List[Dict[str, Any]]:
        """
        Get complete timeline of events for a job.

        Args:
            job_id: Job ID

        Returns:
            List of timeline events (job, tasks, reviews) sorted chronologically
        """
        timeline = []

        # Job events
        job = self.get_job(job_id)
        if job:
            if job['created_at']:
                timeline.append({
                    'type': 'job_created',
                    'timestamp': job['created_at'],
                    'data': job
                })
            if job['started_at']:
                timeline.append({
                    'type': 'job_started',
                    'timestamp': job['started_at'],
                    'data': job
                })
            if job['completed_at']:
                timeline.append({
                    'type': 'job_completed',
                    'timestamp': job['completed_at'],
                    'data': job
                })

        # Task events
        tasks = self.get_tasks(job_id)
        for task in tasks:
            if task['created_at']:
                timeline.append({
                    'type': 'task_created',
                    'timestamp': task['created_at'],
                    'data': task
                })
            if task['started_at']:
                timeline.append({
                    'type': 'task_started',
                    'timestamp': task['started_at'],
                    'data': task
                })
            if task['completed_at']:
                timeline.append({
                    'type': 'task_completed',
                    'timestamp': task['completed_at'],
                    'data': task
                })

        # Code review events
        reviews = self.get_code_reviews(job_id=job_id)
        for review in reviews:
            timeline.append({
                'type': 'code_review',
                'timestamp': review['created_at'],
                'data': review
            })

        # Sort by timestamp
        timeline.sort(key=lambda x: x['timestamp'])

        return timeline

    def get_dependency_graph(self, job_id: int) -> Dict[str, Any]:
        """
        Get task dependency graph for a job.

        Args:
            job_id: Job ID

        Returns:
            Dict with nodes (tasks) and edges (dependencies)
        """
        tasks = self.get_tasks(job_id)

        nodes = []
        edges = []

        for task in tasks:
            nodes.append({
                'id': task['id'],
                'name': task['name'],
                'status': task['status'],
                'order': task['order']
            })

            if task['dependencies']:
                try:
                    deps = json.loads(task['dependencies'])
                    for dep_id in deps:
                        edges.append({
                            'from': dep_id,
                            'to': task['id']
                        })
                except json.JSONDecodeError:
                    pass

        return {
            'nodes': nodes,
            'edges': edges
        }

    def search_execution_logs(
        self,
        job_id: Optional[int] = None,
        task_id: Optional[int] = None,
        command_pattern: Optional[str] = None,
        output_pattern: Optional[str] = None,
        exit_code: Optional[int] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Search execution logs with multiple filter criteria.

        Args:
            job_id: Optional job ID filter
            task_id: Optional task ID filter
            command_pattern: Optional SQL LIKE pattern for command text
            output_pattern: Optional SQL LIKE pattern for output text
            exit_code: Optional exit code filter (exact match)
            start_date: Optional start date (ISO format: YYYY-MM-DD HH:MM:SS)
            end_date: Optional end date (ISO format: YYYY-MM-DD HH:MM:SS)
            limit: Maximum number of results (default: 100)

        Returns:
            List of execution log dicts matching criteria

        Examples:
            # Search for failed commands
            db.search_execution_logs(exit_code=1)

            # Search for pytest commands in last week
            db.search_execution_logs(
                command_pattern='%pytest%',
                start_date='2026-01-10 00:00:00'
            )

            # Search for output containing "error"
            db.search_execution_logs(output_pattern='%error%')
        """
        query = "SELECT * FROM execution_logs WHERE 1=1"
        params = []

        # Job ID filter
        if job_id is not None:
            query += " AND job_id = ?"
            params.append(job_id)

        # Task ID filter
        if task_id is not None:
            query += " AND task_id = ?"
            params.append(task_id)

        # Command pattern (case-insensitive LIKE)
        if command_pattern:
            query += " AND command LIKE ?"
            params.append(command_pattern)

        # Output pattern (case-insensitive LIKE)
        if output_pattern:
            query += " AND output LIKE ?"
            params.append(output_pattern)

        # Exit code filter (exact match)
        if exit_code is not None:
            query += " AND exit_code = ?"
            params.append(exit_code)

        # Date range filters
        if start_date:
            query += " AND executed_at >= ?"
            params.append(start_date)

        if end_date:
            query += " AND executed_at <= ?"
            params.append(end_date)

        # Order by most recent first
        query += " ORDER BY executed_at DESC LIMIT ?"
        params.append(limit)

        cursor = self.conn.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]
