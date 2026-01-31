#!/usr/bin/env python3
import sys
import json
from pathlib import Path

lib_path = Path.home() / ".claude" / "lib"
sys.path.insert(0, str(lib_path))

from project_database import ProjectDatabase

def main():
    payload = json.load(sys.stdin)

    task_run_id = payload.get('task_run_id')
    exit_code = payload.get('exit_code', 0)

    db = ProjectDatabase()

    try:
        # Complete task run
        db.complete_task_run(task_run_id, exit_code)

        result = {
            "task_run_id": task_run_id,
            "status": "completed" if exit_code == 0 else "failed"
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
