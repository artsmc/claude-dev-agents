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
    gate_type = payload.get('gate_type')  # code_review, testing, linting, build
    status = payload.get('status', 'pending')
    result_summary = payload.get('result_summary')
    checked_by = payload.get('checked_by')

    db = ProjectDatabase()

    try:
        # Add quality gate
        gate_id = db.add_quality_gate(
            phase_run_id=phase_run_id,
            gate_type=gate_type,
            status=status,
            result_summary=result_summary,
            checked_by=checked_by
        )

        result = {
            "gate_id": gate_id,
            "status": status
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
