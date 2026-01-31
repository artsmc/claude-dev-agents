#!/usr/bin/env python3
import sys
import json
from pathlib import Path

lib_path = Path.home() / ".claude" / "lib"
sys.path.insert(0, str(lib_path))

from project_database import ProjectDatabase

def main():
    payload = json.load(sys.stdin)

    phase_run_id = payload.get('phase_run_id')
    task_key = payload.get('task_key')  # e.g., "2.1a"
    assigned_agent = payload.get('assigned_agent')

    db = ProjectDatabase()

    try:
        # Get phase run to find plan_id
        run = db.get_phase_run(phase_run_id)
        if not run:
            error = {"error": f"Phase run {phase_run_id} not found"}
            print(json.dumps(error), file=sys.stderr)
            return error

        # Get task by task_key from the plan
        tasks = db.list_tasks(run['plan_id'])
        task = next((t for t in tasks if t['task_key'] == task_key), None)
        if not task:
            error = {"error": f"Task {task_key} not found in plan"}
            print(json.dumps(error), file=sys.stderr)
            return error

        # Create task run (links phase_run to task)
        task_run_id = db.create_task_run(
            phase_run_id=phase_run_id,
            task_id=task['id'],
            assigned_agent=assigned_agent
        )

        # Start task run
        db.start_task_run(task_run_id)

        result = {
            "task_run_id": task_run_id,
            "task_id": task['id'],
            "status": "started"
        }

        print(json.dumps(result))
        return result

    except Exception as e:
        error = {"error": str(e)}
        print(json.dumps(error), file=sys.stderr)
        return error
    finally:
        db.close()

if __name__ == "__main__":
    main()
