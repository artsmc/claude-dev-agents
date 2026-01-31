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
    exit_code = payload.get('exit_code', 0)
    summary = payload.get('summary', '')

    db = ProjectDatabase()

    try:
        # Complete phase run
        db.complete_phase_run(phase_run_id, exit_code, summary)

        # Get phase_id for metrics
        run = db.get_phase_run(phase_run_id)
        if not run:
            error = {"error": f"Phase run {phase_run_id} not found"}
            print(json.dumps(error), file=sys.stderr)
            return error

        # Update phase metrics
        metrics = db.get_phase_metrics(run['phase_id'])

        result = {
            "phase_run_id": phase_run_id,
            "status": "completed" if exit_code == 0 else "failed",
            "metrics": metrics
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
