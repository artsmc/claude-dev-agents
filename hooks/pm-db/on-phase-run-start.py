#!/usr/bin/env python3
import sys
import json
from pathlib import Path

# Add lib to path
lib_path = Path.home() / ".claude" / "lib"
sys.path.insert(0, str(lib_path))

from project_database import ProjectDatabase

def main():
    # Read JSON input from stdin
    payload = json.load(sys.stdin)

    phase_name = payload.get('phase_name')
    project_name = payload.get('project_name')
    assigned_agent = payload.get('assigned_agent')

    db = ProjectDatabase()

    try:
        # Get project
        project = db.get_project_by_name(project_name)
        if not project:
            error = {"error": f"Project '{project_name}' not found"}
            print(json.dumps(error), file=sys.stderr)
            return error

        # Get phase
        phases = db.list_phases(project_id=project['id'])
        phase = next((p for p in phases if p['name'] == phase_name), None)
        if not phase:
            error = {"error": f"Phase '{phase_name}' not found"}
            print(json.dumps(error), file=sys.stderr)
            return error

        # Get approved plan
        if not phase['approved_plan_id']:
            error = {"error": f"Phase '{phase_name}' has no approved plan"}
            print(json.dumps(error), file=sys.stderr)
            return error

        # Create phase run
        run_id = db.create_phase_run(
            phase_id=phase['id'],
            plan_id=phase['approved_plan_id'],
            assigned_agent=assigned_agent
        )

        # Start phase run
        db.start_phase_run(run_id)

        # Return result
        result = {
            "phase_run_id": run_id,
            "phase_id": phase['id'],
            "plan_id": phase['approved_plan_id'],
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
