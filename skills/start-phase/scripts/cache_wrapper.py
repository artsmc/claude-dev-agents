#!/usr/bin/python3
"""
Agent Context Caching wrapper for start-phase workflows.

Usage:
    # Initialize invocation
    python cache_wrapper.py init \
        --agent-name "start-phase-plan" \
        --purpose "Strategic planning for auth feature" \
        --phase-run-id 42  # Optional

    # Log file read with caching
    python cache_wrapper.py read \
        --invocation-id 123 \
        --file-path "/path/to/file.md"

    # Complete invocation
    python cache_wrapper.py complete \
        --invocation-id 123

    # Get invocation stats
    python cache_wrapper.py stats \
        --invocation-id 123
"""

import sys
import json
import hashlib
import warnings
from pathlib import Path
from typing import Optional, Dict, Any

# Suppress all warnings (including locale warnings) to prevent contaminating JSON output
warnings.filterwarnings('ignore')

# Add lib to path
sys.path.insert(0, str(Path.home() / '.claude' / 'lib'))
from project_database import ProjectDatabase

def calculate_file_hash(content: str) -> str:
    """Calculate SHA-256 hash of file content."""
    return hashlib.sha256(content.encode('utf-8')).hexdigest()

def init_invocation(
    agent_name: str,
    purpose: str,
    phase_run_id: Optional[int] = None,
    task_run_id: Optional[int] = None
) -> Dict[str, Any]:
    """Initialize agent invocation and return invocation_id."""
    db = ProjectDatabase()
    invocation_id = db.create_agent_invocation(
        agent_name=agent_name,
        purpose=purpose,
        phase_run_id=phase_run_id,
        task_run_id=task_run_id
    )
    return {
        "invocation_id": invocation_id,
        "agent_name": agent_name,
        "phase_run_id": phase_run_id,
        "task_run_id": task_run_id
    }

def read_file_with_cache(
    invocation_id: int,
    file_path: str
) -> Dict[str, Any]:
    """
    Read file with cache tracking.

    Returns:
        {
            "content": "file content",
            "cache_status": "hit|miss|new",
            "file_size_bytes": 1234,
            "estimated_tokens": 308,
            "from_cache": true
        }
    """
    db = ProjectDatabase()
    path = Path(file_path).resolve()

    # Read actual file content
    if not path.exists():
        return {
            "error": f"File not found: {file_path}",
            "cache_status": "error"
        }

    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    content_hash = calculate_file_hash(content)
    file_size_bytes = len(content.encode('utf-8'))

    # Check cache
    cached = db.get_cached_file(str(path))

    if cached and cached['content_hash'] == content_hash:
        # Cache HIT
        cache_status = "hit"
        from_cache = True
    elif cached:
        # Cache MISS (stale)
        cache_status = "miss"
        from_cache = False
        # Update cache
        db.cache_file(str(path), content, file_type='markdown')
    else:
        # Cache NEW
        cache_status = "new"
        from_cache = False
        # Create cache entry
        db.cache_file(str(path), content, file_type='markdown')

    # Log file read
    db.log_file_read(
        invocation_id=invocation_id,
        file_path=str(path),
        cache_status=cache_status,
        file_size_bytes=file_size_bytes
    )

    return {
        "content": content,
        "cache_status": cache_status,
        "file_size_bytes": file_size_bytes,
        "estimated_tokens": file_size_bytes // 4,
        "from_cache": from_cache
    }

def complete_invocation(invocation_id: int) -> Dict[str, Any]:
    """Mark invocation complete and return summary stats."""
    db = ProjectDatabase()
    db.complete_agent_invocation(invocation_id)

    # Get stats
    invocation = db.conn.execute(
        """SELECT * FROM agent_invocations WHERE id = ?""",
        (invocation_id,)
    ).fetchone()

    if not invocation:
        return {}

    # Convert Row to dict manually to ensure JSON serializability
    result = {}
    for key in invocation.keys():
        result[key] = invocation[key]
    return result

def get_stats(invocation_id: int) -> Dict[str, Any]:
    """Get current invocation statistics."""
    db = ProjectDatabase()
    invocation = db.conn.execute(
        """SELECT * FROM agent_invocations WHERE id = ?""",
        (invocation_id,)
    ).fetchone()

    if not invocation:
        return {"error": "Invocation not found"}

    return {
        "invocation_id": invocation['id'],
        "agent_name": invocation['agent_name'],
        "files_read": invocation['total_files_read'],
        "cache_hits": invocation['cache_hits'],
        "cache_misses": invocation['cache_misses'],
        "estimated_tokens": invocation['estimated_tokens_used'],
        "duration_seconds": invocation['duration_seconds'] if invocation['duration_seconds'] else 0,
        "status": invocation['status']
    }

def main():
    import argparse

    parser = argparse.ArgumentParser(description='Agent Context Caching wrapper')
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    # init command
    init_parser = subparsers.add_parser('init', help='Initialize agent invocation')
    init_parser.add_argument('--agent-name', required=True, help='Agent name')
    init_parser.add_argument('--purpose', required=True, help='Invocation purpose')
    init_parser.add_argument('--phase-run-id', type=int, help='Optional phase run ID')
    init_parser.add_argument('--task-run-id', type=int, help='Optional task run ID')

    # read command
    read_parser = subparsers.add_parser('read', help='Read file with cache tracking')
    read_parser.add_argument('--invocation-id', type=int, required=True)
    read_parser.add_argument('--file-path', required=True)

    # complete command
    complete_parser = subparsers.add_parser('complete', help='Complete invocation')
    complete_parser.add_argument('--invocation-id', type=int, required=True)

    # stats command
    stats_parser = subparsers.add_parser('stats', help='Get invocation stats')
    stats_parser.add_argument('--invocation-id', type=int, required=True)

    args = parser.parse_args()

    if args.command == 'init':
        result = init_invocation(
            agent_name=args.agent_name,
            purpose=args.purpose,
            phase_run_id=args.phase_run_id,
            task_run_id=args.task_run_id
        )
        print(json.dumps(result, indent=2))

    elif args.command == 'read':
        result = read_file_with_cache(
            invocation_id=args.invocation_id,
            file_path=args.file_path
        )
        # Print only metadata (not full content)
        metadata = {k: v for k, v in result.items() if k != 'content'}
        print(json.dumps(metadata, indent=2))

    elif args.command == 'complete':
        result = complete_invocation(args.invocation_id)
        print(json.dumps(result, indent=2))

    elif args.command == 'stats':
        result = get_stats(args.invocation_id)
        print(json.dumps(result, indent=2))

    else:
        parser.print_help()
        sys.exit(1)

if __name__ == '__main__':
    main()
