#!/usr/bin/env python3
"""on-tool-use Hook - Logs command execution"""
import sys, json
from pathlib import Path
lib_path = Path(__file__).parent.parent.parent / "lib"
sys.path.insert(0, str(lib_path))
from project_database import ProjectDatabase

try:
    data = json.load(sys.stdin)
    job_id = data.get('job_id')

    # Skip if no job_id (not in execution context)
    if not job_id:
        sys.exit(0)

    task_id = data.get('task_id')
    command = data.get('command')
    output = data.get('output')
    exit_code = data.get('exit_code')
    start_time = data.get('start_time')
    end_time = data.get('end_time')

    # Calculate duration if timestamps provided
    duration_ms = None
    if start_time and end_time:
        duration_ms = int((end_time - start_time) * 1000)

    if command:
        with ProjectDatabase() as db:
            log_id = db.log_execution(job_id, task_id, command, output, exit_code, duration_ms)
            print(json.dumps({"log_id": log_id, "status": "logged"}))
except Exception as e:
    print(json.dumps({"error": str(e), "status": "failed"}), file=sys.stderr)
    sys.exit(0)
