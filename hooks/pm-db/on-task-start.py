#!/usr/bin/env python3
"""on-task-start Hook - Creates and starts task record"""
import sys, json
from pathlib import Path
lib_path = Path(__file__).parent.parent.parent / "lib"
sys.path.insert(0, str(lib_path))
from project_database import ProjectDatabase

try:
    data = json.load(sys.stdin)
    job_id = data.get('job_id')
    task_name = data.get('task_name')
    order = data.get('order', 0)
    dependencies = data.get('dependencies')

    if not job_id or not task_name:
        print(json.dumps({"error": "job_id and task_name required", "status": "failed"}))
        sys.exit(0)

    with ProjectDatabase() as db:
        task_id = db.create_task(job_id, task_name, order, dependencies)
        db.start_task(task_id)
        print(json.dumps({"task_id": task_id, "status": "created"}))
except Exception as e:
    print(json.dumps({"error": str(e), "status": "failed"}), file=sys.stderr)
    sys.exit(0)
