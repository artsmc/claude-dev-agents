#!/usr/bin/env python3
"""on-task-complete Hook - Marks task complete"""
import sys, json
from pathlib import Path
lib_path = Path(__file__).parent.parent.parent / "lib"
sys.path.insert(0, str(lib_path))
from project_database import ProjectDatabase

try:
    data = json.load(sys.stdin)
    job_id = data.get('job_id')
    task_name = data.get('task_name')
    exit_code = data.get('exit_code', 0)

    if not job_id or not task_name:
        print(json.dumps({"error": "job_id and task_name required", "status": "failed"}))
        sys.exit(0)

    with ProjectDatabase() as db:
        # Find task by name in this job
        tasks = db.get_tasks(job_id)
        task = next((t for t in tasks if t['name'] == task_name), None)

        if task:
            db.complete_task(task['id'], exit_code)
            print(json.dumps({"task_id": task['id'], "status": "completed"}))
        else:
            print(json.dumps({"error": "task not found", "status": "failed"}))
except Exception as e:
    print(json.dumps({"error": str(e), "status": "failed"}), file=sys.stderr)
    sys.exit(0)
