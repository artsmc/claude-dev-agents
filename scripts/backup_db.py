#!/usr/bin/env python3
"""
Backup Script for PM-DB System

Creates timestamped backups of the projects.db database.

Usage:
    python3 scripts/backup_db.py [--db-path PATH] [--backup-dir DIR]

Examples:
    # Backup default database to default location
    python3 scripts/backup_db.py

    # Backup custom database to custom location
    python3 scripts/backup_db.py --db-path /path/to/projects.db --backup-dir /backups

Default Locations:
    Database: ~/.claude/lib/projects.db
    Backups:  ~/.claude/backups/
"""

import argparse
import shutil
import sqlite3
from pathlib import Path
from datetime import datetime
import sys


def create_backup(db_path: Path, backup_dir: Path) -> Path:
    """
    Create a backup of the database using SQLite's backup API.

    Args:
        db_path: Path to the database to backup
        backup_dir: Directory to store the backup

    Returns:
        Path to the created backup file

    Raises:
        FileNotFoundError: If database doesn't exist
        PermissionError: If cannot write to backup directory
    """
    # Verify database exists
    if not db_path.exists():
        raise FileNotFoundError(f"Database not found: {db_path}")

    # Create backup directory if needed
    backup_dir.mkdir(parents=True, exist_ok=True)

    # Generate backup filename with timestamp (including microseconds to avoid collisions)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    backup_filename = f"projects-backup-{timestamp}.db"
    backup_path = backup_dir / backup_filename

    print(f"Creating backup: {backup_path}")

    # Use SQLite's backup API for safe online backup
    # This ensures a consistent snapshot even if the database is in use
    source_conn = sqlite3.connect(str(db_path))
    backup_conn = sqlite3.connect(str(backup_path))

    try:
        # Perform the backup
        source_conn.backup(backup_conn)

        # Verify backup integrity
        cursor = backup_conn.execute("PRAGMA integrity_check")
        result = cursor.fetchone()
        if result[0] != "ok":
            raise RuntimeError(f"Backup integrity check failed: {result}")

        print(f"✅ Backup created successfully: {backup_path}")
        print(f"   Size: {backup_path.stat().st_size:,} bytes")

        return backup_path

    finally:
        source_conn.close()
        backup_conn.close()


def list_backups(backup_dir: Path) -> list:
    """
    List all backup files in the backup directory.

    Args:
        backup_dir: Directory containing backups

    Returns:
        List of backup file paths, sorted by creation time (newest first)
    """
    if not backup_dir.exists():
        return []

    backups = sorted(
        backup_dir.glob("projects-backup-*.db"),
        key=lambda p: p.stat().st_mtime,
        reverse=True
    )

    return backups


def cleanup_old_backups(backup_dir: Path, keep_count: int = 10):
    """
    Remove old backups, keeping only the most recent N backups.

    Args:
        backup_dir: Directory containing backups
        keep_count: Number of recent backups to keep (default: 10)
    """
    backups = list_backups(backup_dir)

    if len(backups) <= keep_count:
        print(f"Found {len(backups)} backups (keeping all)")
        return

    to_delete = backups[keep_count:]
    print(f"Cleaning up {len(to_delete)} old backups (keeping {keep_count} most recent)")

    for backup in to_delete:
        print(f"  Removing: {backup.name}")
        backup.unlink()

    print(f"✅ Cleanup complete: {len(to_delete)} backups removed")


def main():
    """Main backup script entry point"""
    parser = argparse.ArgumentParser(
        description="Backup PM-DB database",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument(
        "--db-path",
        type=Path,
        default=Path.home() / ".claude" / "lib" / "projects.db",
        help="Path to database (default: ~/.claude/lib/projects.db)"
    )

    parser.add_argument(
        "--backup-dir",
        type=Path,
        default=Path.home() / ".claude" / "backups",
        help="Backup directory (default: ~/.claude/backups/)"
    )

    parser.add_argument(
        "--keep",
        type=int,
        default=10,
        help="Number of recent backups to keep (default: 10)"
    )

    parser.add_argument(
        "--list",
        action="store_true",
        help="List existing backups and exit"
    )

    args = parser.parse_args()

    # List mode
    if args.list:
        backups = list_backups(args.backup_dir)
        if not backups:
            print(f"No backups found in {args.backup_dir}")
            return 0

        print(f"Found {len(backups)} backups in {args.backup_dir}:\n")
        for backup in backups:
            size = backup.stat().st_size
            mtime = datetime.fromtimestamp(backup.stat().st_mtime)
            print(f"  {backup.name}")
            print(f"    Created: {mtime.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"    Size: {size:,} bytes")
            print()

        return 0

    # Backup mode
    try:
        print("PM-DB Backup Script")
        print("=" * 60)
        print(f"Database: {args.db_path}")
        print(f"Backup directory: {args.backup_dir}")
        print()

        # Create backup
        backup_path = create_backup(args.db_path, args.backup_dir)

        print()

        # Cleanup old backups
        cleanup_old_backups(args.backup_dir, args.keep)

        print()
        print("=" * 60)
        print("✅ Backup complete!")
        print()
        print(f"Backup saved to: {backup_path}")
        print(f"To restore: python3 scripts/restore_db.py {backup_path}")

        return 0

    except Exception as e:
        print(f"❌ Backup failed: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
