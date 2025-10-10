#!/usr/bin/env python3
"""
Database Backup Utility
Backs up the attendance database with timestamp
"""

import shutil
import sqlite3
from pathlib import Path
from datetime import datetime
import argparse
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import Settings


def backup_database(backup_dir=None, keep_last=10):
    """
    Backup the database
    
    Args:
        backup_dir: Directory to store backups (default: data/backups)
        keep_last: Number of recent backups to keep (0 = keep all)
    """
    # Source database
    db_path = Path(Settings.DATABASE_PATH)
    
    if not db_path.exists():
        print(f"❌ Database not found: {db_path}")
        return False
    
    # Backup directory
    if backup_dir is None:
        backup_dir = Settings.DATA_DIR / "backups"
    else:
        backup_dir = Path(backup_dir)
    
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    # Create backup filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"attendance_backup_{timestamp}.db"
    backup_path = backup_dir / backup_filename
    
    try:
        # Method 1: SQLite backup API (safer, handles locks)
        print(f"📦 Creating backup: {backup_filename}")
        
        source_conn = sqlite3.connect(str(db_path))
        backup_conn = sqlite3.connect(str(backup_path))
        
        with backup_conn:
            source_conn.backup(backup_conn)
        
        source_conn.close()
        backup_conn.close()
        
        # Verify backup
        backup_size = backup_path.stat().st_size
        original_size = db_path.stat().st_size
        
        print(f"✅ Backup created successfully!")
        print(f"   Location: {backup_path}")
        print(f"   Size: {backup_size / 1024:.2f} KB")
        print(f"   Original: {original_size / 1024:.2f} KB")
        
        # Clean up old backups
        if keep_last > 0:
            cleanup_old_backups(backup_dir, keep_last)
        
        return True
        
    except Exception as e:
        print(f"❌ Backup failed: {str(e)}")
        if backup_path.exists():
            backup_path.unlink()  # Remove incomplete backup
        return False


def cleanup_old_backups(backup_dir, keep_last):
    """Remove old backup files, keeping only the most recent ones"""
    backup_files = sorted(
        backup_dir.glob("attendance_backup_*.db"),
        key=lambda p: p.stat().st_mtime,
        reverse=True
    )
    
    if len(backup_files) > keep_last:
        print(f"\n🗑️  Cleaning up old backups (keeping last {keep_last})...")
        
        for old_backup in backup_files[keep_last:]:
            print(f"   Removing: {old_backup.name}")
            old_backup.unlink()
        
        print(f"✅ Cleanup complete")


def list_backups(backup_dir=None):
    """List all available backups"""
    if backup_dir is None:
        backup_dir = Settings.DATA_DIR / "backups"
    else:
        backup_dir = Path(backup_dir)
    
    if not backup_dir.exists():
        print("No backups found")
        return
    
    backup_files = sorted(
        backup_dir.glob("attendance_backup_*.db"),
        key=lambda p: p.stat().st_mtime,
        reverse=True
    )
    
    if not backup_files:
        print("No backups found")
        return
    
    print(f"\n📋 Available backups in {backup_dir}:\n")
    print(f"{'Filename':<40} {'Size':<15} {'Date'}")
    print("-" * 75)
    
    for backup_file in backup_files:
        size = backup_file.stat().st_size / 1024
        mtime = datetime.fromtimestamp(backup_file.stat().st_mtime)
        
        print(f"{backup_file.name:<40} {size:>10.2f} KB   {mtime.strftime('%Y-%m-%d %H:%M:%S')}")
    
    print(f"\nTotal: {len(backup_files)} backup(s)")


def restore_backup(backup_file, confirm=True):
    """
    Restore database from backup
    
    Args:
        backup_file: Path to backup file
        confirm: Ask for confirmation before restoring
    """
    backup_path = Path(backup_file)
    
    if not backup_path.exists():
        print(f"❌ Backup file not found: {backup_path}")
        return False
    
    db_path = Path(Settings.DATABASE_PATH)
    
    if confirm:
        print(f"\n⚠️  WARNING: This will replace the current database!")
        print(f"   Current: {db_path}")
        print(f"   Backup: {backup_path}")
        
        response = input("\nAre you sure you want to continue? (yes/no): ")
        if response.lower() != 'yes':
            print("Restore cancelled")
            return False
    
    try:
        # Backup current database first
        if db_path.exists():
            safety_backup = db_path.parent / f"attendance_before_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            print(f"\n📦 Creating safety backup: {safety_backup.name}")
            shutil.copy2(db_path, safety_backup)
        
        # Restore from backup
        print(f"♻️  Restoring database...")
        shutil.copy2(backup_path, db_path)
        
        print(f"✅ Database restored successfully!")
        print(f"   From: {backup_path.name}")
        print(f"   To: {db_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ Restore failed: {str(e)}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Backup and restore attendance database"
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Backup command
    backup_parser = subparsers.add_parser('backup', help='Create database backup')
    backup_parser.add_argument(
        '--dir',
        type=str,
        help='Backup directory (default: data/backups)'
    )
    backup_parser.add_argument(
        '--keep',
        type=int,
        default=10,
        help='Number of recent backups to keep (default: 10, 0 = keep all)'
    )
    
    # List command
    list_parser = subparsers.add_parser('list', help='List available backups')
    list_parser.add_argument(
        '--dir',
        type=str,
        help='Backup directory (default: data/backups)'
    )
    
    # Restore command
    restore_parser = subparsers.add_parser('restore', help='Restore from backup')
    restore_parser.add_argument(
        'backup_file',
        type=str,
        help='Backup file to restore'
    )
    restore_parser.add_argument(
        '--no-confirm',
        action='store_true',
        help='Skip confirmation prompt'
    )
    
    args = parser.parse_args()
    
    if args.command == 'backup':
        success = backup_database(
            backup_dir=args.dir,
            keep_last=args.keep
        )
        sys.exit(0 if success else 1)
        
    elif args.command == 'list':
        list_backups(backup_dir=args.dir)
        
    elif args.command == 'restore':
        success = restore_backup(
            backup_file=args.backup_file,
            confirm=not args.no_confirm
        )
        sys.exit(0 if success else 1)
        
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    print("=" * 50)
    print("Database Backup Utility")
    print("=" * 50)
    print()
    
    main()
