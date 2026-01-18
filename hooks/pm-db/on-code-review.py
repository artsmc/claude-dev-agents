#!/usr/bin/env python3
"""on-code-review Hook - Stores code review summary"""
import sys, json
from pathlib import Path
lib_path = Path(__file__).parent.parent.parent / "lib"
sys.path.insert(0, str(lib_path))
from project_database import ProjectDatabase

try:
    data = json.load(sys.stdin)
    job_id = data.get('job_id')
    task_id = data.get('task_id')
    reviewer = data.get('reviewer')
    summary = data.get('summary')
    verdict = data.get('verdict', 'approved')
    issues_found = data.get('issues_found')  # JSON string
    files_reviewed = data.get('files_reviewed')  # JSON string

    if not reviewer or not summary:
        print(json.dumps({"error": "reviewer and summary required", "status": "failed"}))
        sys.exit(0)

    with ProjectDatabase() as db:
        review_id = db.add_code_review(job_id, task_id, reviewer, summary, verdict, issues_found, files_reviewed)
        print(json.dumps({"review_id": review_id, "status": "created"}))
except Exception as e:
    print(json.dumps({"error": str(e), "status": "failed"}), file=sys.stderr)
    sys.exit(0)
