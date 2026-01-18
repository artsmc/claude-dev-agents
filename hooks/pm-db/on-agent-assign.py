#!/usr/bin/env python3
"""on-agent-assign Hook - Records agent assignment"""
import sys, json
from pathlib import Path
lib_path = Path(__file__).parent.parent.parent / "lib"
sys.path.insert(0, str(lib_path))
from project_database import ProjectDatabase

try:
    data = json.load(sys.stdin)
    agent_type = data.get('agent_type')
    job_id = data.get('job_id')
    task_id = data.get('task_id')

    if not agent_type or (not job_id and not task_id):
        print(json.dumps({"error": "agent_type and (job_id or task_id) required", "status": "failed"}))
        sys.exit(0)

    with ProjectDatabase() as db:
        assignment_id = db.assign_agent(agent_type, job_id, task_id)
        print(json.dumps({"assignment_id": assignment_id, "status": "assigned"}))
except Exception as e:
    print(json.dumps({"error": str(e), "status": "failed"}), file=sys.stderr)
    sys.exit(0)
