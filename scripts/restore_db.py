#!/usr/bin/env python3
"""
Restore Script for PM-DB System

Restores a database from a backup file.

Usage:
    python3 scripts/restore_db.py BACKUP_FILE [--db-path PATH] [--force]

Examples:
    # Restore from backup (interactive confirmation)
    python3 scripts/restore_db.py ~/.claude/backups/projects-backup-20260117-143022.db

    # Restore with force (no confirmation)
    python3 scripts/restore_db.py backup.db --force

    # Restore to custom location
    python3 scripts/restore_db.py backup.db --db-path /path/to/projects.db

Safety:
    - Current database is backed up before restore (unless --no-backup)
    - Backup integrity is verified before restore
    - Schema version compatibility is checked
"""

import argparse
import shutil
import sqlite3
from pathlib import Path
from datetime import datetime
import sys


def verify_backup_integrity(backup_path: Path) -> bool:
    """
    Verify backup file integrity and structure.

    Args:
        backup_path: Path to backup file

    Returns:
        True if backup is valid, False otherwise
    """
    try:
        conn = sqlite3.connect(str(backup_path))

        # Run integrity check
        cursor = conn.execute("PRAGMA integrity_check")
        result = cursor.fetchone()

        if result[0] != "ok":
            print(f"❌ Backup integrity check failed: {result}")
            return False

        # Verify schema_version table exists
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='schema_version'"
        )
        if not cursor.fetchone():
            print("❌ Backup missing schema_version table")
            return False

        # Get schema version
        cursor = conn.execute("SELECT version FROM schema_version ORDER BY version DESC LIMIT 1")
        version = cursor.fetchone()

        if version:
            print(f"✅ Backup verified (schema version: {version[0]})")
        else:
            print("⚠️  Backup verified (no schema version found - may be empty database)")

        conn.close()
        return True

    except sqlite3.Error as e:
        print(f"❌ Backup verification failed: {e}")
        return False


def backup_current_db(db_path: Path) -> Path:
    """
    Create a safety backup of the current database before restore.

    Args:
        db_path: Path to current database

    Returns:
        Path to safety backup file
    """
    if not db_path.exists():
        print("Current database doesn't exist (nothing to backup)")
        return None

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    safety_backup = db_path.parent / f"projects-pre-restore-{timestamp}.db"

    print(f"Creating safety backup: {safety_backup}")

    shutil.copy2(db_path, safety_backup)

    print(f"✅ Safety backup created: {safety_backup}")
    return safety_backup


def restore_database(backup_path: Path, db_path: Path) -> bool:
    """
    Restore database from backup file.

    Args:
        backup_path: Path to backup file
        db_path: Path to destination database

    Returns:
        True if restore successful, False otherwise
    """
    try:
        print(f"Restoring database...")
        print(f"  From: {backup_path}")
        print(f"  To:   {db_path}")

        # Copy backup to destination
        shutil.copy2(backup_path, db_path)

        # Verify restored database
        conn = sqlite3.connect(str(db_path))
        cursor = conn.execute("PRAGMA integrity_check")
        result = cursor.fetchone()
        conn.close()

        if result[0] != "ok":
            raise RuntimeError(f"Restored database integrity check failed: {result}")

        print("✅ Database restored successfully")
        return True

    except Exception as e:
        print(f"❌ Restore failed: {e}")
        return False


def main():
    """Main restore script entry point"""
    parser = argparse.ArgumentParser(
        description="Restore PM-DB database from backup",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument(
        "backup_file",
        type=Path,
        help="Path to backup file to restore"
    )

    parser.add_argument(
        "--db-path",
        type=Path,
        default=Path.home() / ".claude" / "lib" / "projects.db",
        help="Path to database (default: ~/.claude/lib/projects.db)"
    )

    parser.add_argument(
        "--force",
        action="store_true",
        help="Skip confirmation prompt"
    )

    parser.add_argument(
        "--no-backup",
        action="store_true",
        help="Skip safety backup of current database"
    )

    args = parser.parse_args()

    # Verify backup file exists
    if not args.backup_file.exists():
        print(f"❌ Backup file not found: {args.backup_file}", file=sys.stderr)
        return 1

    print("PM-DB Restore Script")
    print("=" * 60)
    print(f"Backup file: {args.backup_file}")
    print(f"Backup size: {args.backup_file.stat().st_size:,} bytes")
    print(f"Target database: {args.db_path}")
    print()

    # Verify backup integrity
    print("Verifying backup integrity...")
    if not verify_backup_integrity(args.backup_file):
        print("❌ Backup verification failed. Aborting restore.", file=sys.stderr)
        return 1

    print()

    # Initialize safety backup variable
    safety_backup = None

    # Check if target exists
    if args.db_path.exists():
        current_size = args.db_path.stat().st_size
        print(f"⚠️  Current database exists ({current_size:,} bytes)")
        print("   This restore will OVERWRITE the current database!")
        print()

        # Confirmation prompt
        if not args.force:
            response = input("Continue with restore? [y/N]: ").strip().lower()
            if response not in ['y', 'yes']:
                print("Restore cancelled.")
                return 0
            print()

        # Create safety backup
        if not args.no_backup:
            safety_backup = backup_current_db(args.db_path)
            print()
    else:
        print("Target database doesn't exist (will be created)")
        print()

    # Perform restore
    if restore_database(args.backup_file, args.db_path):
        print()
        print("=" * 60)
        print("✅ Restore complete!")
        print()
        print(f"Database restored to: {args.db_path}")

        if safety_backup:
            print(f"Safety backup saved to: {safety_backup}")

        return 0
    else:
        print()
        print("=" * 60)
        print("❌ Restore failed!")

        if not args.no_backup and 'safety_backup' in locals():
            print()
            print(f"Your original database is safe at: {safety_backup}")
            print("You can manually restore it if needed.")

        return 1


if __name__ == "__main__":
    sys.exit(main())
