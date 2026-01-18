#!/usr/bin/env python3
"""
on-job-start Hook for Project Management Database

Automatically creates a job record when /start-phase execute begins.

Hook data (JSON from stdin):
{
  "job_name": "Build auth feature",
  "spec_id": 1,
  "assigned_agent": "python-backend-developer",
  "priority": "high",
  "session_id": "abc123"
}

Output (JSON to stdout):
{
  "job_id": 42,
  "status": "created"
}
"""

import sys
import json
from pathlib import Path

# Add lib to path
lib_path = Path(__file__).parent.parent.parent / "lib"
sys.path.insert(0, str(lib_path))

from project_database import ProjectDatabase


def main():
    """Main hook entry point."""
    try:
        # Read hook data from stdin
        hook_data = json.load(sys.stdin)

        # Extract fields
        job_name = hook_data.get('job_name')
        spec_id = hook_data.get('spec_id')
        assigned_agent = hook_data.get('assigned_agent')
        priority = hook_data.get('priority', 'normal')
        session_id = hook_data.get('session_id')

        # Validate required fields
        if not job_name:
            print(json.dumps({
                "error": "job_name is required",
                "status": "failed"
            }))
            sys.exit(0)  # Don't fail execution, just log error

        # Create job record
        with ProjectDatabase() as db:
            job_id = db.create_job(
                spec_id=spec_id,
                name=job_name,
                priority=priority,
                assigned_agent=assigned_agent,
                session_id=session_id
            )

            # Start the job
            db.start_job(job_id)

            # Output job_id
            print(json.dumps({
                "job_id": job_id,
                "status": "created"
            }))

    except json.JSONDecodeError as e:
        # Invalid JSON input - log but don't fail
        print(json.dumps({
            "error": f"Invalid JSON input: {e}",
            "status": "failed"
        }), file=sys.stderr)
        sys.exit(0)

    except Exception as e:
        # Log error but don't fail execution
        print(json.dumps({
            "error": str(e),
            "status": "failed"
        }), file=sys.stderr)
        sys.exit(0)


if __name__ == "__main__":
    main()
