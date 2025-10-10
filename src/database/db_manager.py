"""
Database Manager - Handles SQLite connection and initialization
"""

import sqlite3
import os
from pathlib import Path
from typing import Optional
from contextlib import contextmanager

from config.settings import Settings


class DatabaseManager:
    """Manages database connections and initialization"""
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize database manager
        
        Args:
            db_path: Path to SQLite database file (uses Settings.DATABASE_PATH if None)
        """
        self.db_path = db_path or Settings.DATABASE_PATH
        self._ensure_database_directory()
        self._initialized = False
    
    def _ensure_database_directory(self):
        """Create database directory if it doesn't exist"""
        db_dir = Path(self.db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)
    
    def get_connection(self) -> sqlite3.Connection:
        """
        Get a database connection
        
        Returns:
            sqlite3.Connection: Database connection
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        return conn
    
    @contextmanager
    def get_cursor(self):
        """
        Context manager for database cursor
        
        Usage:
            with db_manager.get_cursor() as cursor:
                cursor.execute("SELECT * FROM students")
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            yield cursor
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()
    
    def initialize_database(self) -> bool:
        """
        Initialize database with schema
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Read schema file
            schema_path = Path(__file__).parent / 'schema.sql'
            
            if not schema_path.exists():
                raise FileNotFoundError(f"Schema file not found: {schema_path}")
            
            with open(schema_path, 'r', encoding='utf-8') as f:
                schema_sql = f.read()
            
            # Execute schema
            with self.get_cursor() as cursor:
                cursor.executescript(schema_sql)
            
            self._initialized = True
            print(f"✓ Database initialized successfully: {self.db_path}")
            return True
            
        except Exception as e:
            print(f"✗ Database initialization failed: {str(e)}")
            return False
    
    def check_database_exists(self) -> bool:
        """
        Check if database file exists and has tables
        
        Returns:
            bool: True if database exists with tables
        """
        if not os.path.exists(self.db_path):
            return False
        
        try:
            with self.get_cursor() as cursor:
                cursor.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name='students'"
                )
                return cursor.fetchone() is not None
        except Exception:
            return False
    
    def reset_database(self) -> bool:
        """
        Drop all tables and reinitialize database
        WARNING: This will delete all data!
        
        Returns:
            bool: True if successful
        """
        try:
            with self.get_cursor() as cursor:
                # Get all tables
                cursor.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'"
                )
                tables = cursor.fetchall()
                
                # Drop all tables
                for table in tables:
                    cursor.execute(f"DROP TABLE IF EXISTS {table[0]}")
                
                # Drop all views
                cursor.execute(
                    "SELECT name FROM sqlite_master WHERE type='view'"
                )
                views = cursor.fetchall()
                for view in views:
                    cursor.execute(f"DROP VIEW IF EXISTS {view[0]}")
            
            # Reinitialize
            return self.initialize_database()
            
        except Exception as e:
            print(f"✗ Database reset failed: {str(e)}")
            return False
    
    def backup_database(self, backup_path: Optional[str] = None) -> bool:
        """
        Create a backup of the database
        
        Args:
            backup_path: Path for backup file (auto-generated if None)
        
        Returns:
            bool: True if successful
        """
        try:
            import shutil
            from datetime import datetime
            
            if backup_path is None:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                backup_dir = Settings.DATA_DIR / 'backups'
                backup_dir.mkdir(parents=True, exist_ok=True)
                backup_path = backup_dir / f'attendance_backup_{timestamp}.db'
            
            shutil.copy2(self.db_path, backup_path)
            print(f"✓ Database backed up to: {backup_path}")
            return True
            
        except Exception as e:
            print(f"✗ Database backup failed: {str(e)}")
            return False
    
    def get_database_stats(self) -> dict:
        """
        Get database statistics
        
        Returns:
            dict: Statistics including table counts
        """
        stats = {}
        
        try:
            with self.get_cursor() as cursor:
                # Count students
                cursor.execute("SELECT COUNT(*) FROM students WHERE is_active = 1")
                stats['total_students'] = cursor.fetchone()[0]
                
                # Count courses
                cursor.execute("SELECT COUNT(*) FROM courses WHERE is_active = 1")
                stats['total_courses'] = cursor.fetchone()[0]
                
                # Count sessions
                cursor.execute("SELECT COUNT(*) FROM class_sessions")
                stats['total_sessions'] = cursor.fetchone()[0]
                
                # Count attendance records
                cursor.execute("SELECT COUNT(*) FROM attendance")
                stats['total_attendance_records'] = cursor.fetchone()[0]
                
                # Database size
                stats['database_size_mb'] = os.path.getsize(self.db_path) / (1024 * 1024)
                
        except Exception as e:
            print(f"✗ Error getting database stats: {str(e)}")
        
        return stats
    
    def execute_query(self, query: str, params: tuple = ()) -> list:
        """
        Execute a SELECT query and return results
        
        Args:
            query: SQL query string
            params: Query parameters
        
        Returns:
            list: Query results
        """
        try:
            with self.get_cursor() as cursor:
                cursor.execute(query, params)
                return cursor.fetchall()
        except Exception as e:
            print(f"✗ Query execution failed: {str(e)}")
            return []
    
    def execute_update(self, query: str, params: tuple = ()) -> int:
        """
        Execute an INSERT/UPDATE/DELETE query
        
        Args:
            query: SQL query string
            params: Query parameters
        
        Returns:
            int: Number of affected rows
        """
        try:
            with self.get_cursor() as cursor:
                cursor.execute(query, params)
                return cursor.rowcount
        except Exception as e:
            print(f"✗ Update execution failed: {str(e)}")
            return 0


# Global database manager instance
db_manager = DatabaseManager()


if __name__ == '__main__':
    # Initialize database when run directly
    manager = DatabaseManager()
    
    if manager.check_database_exists():
        print("Database already exists.")
        stats = manager.get_database_stats()
        print("\nDatabase Statistics:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
    else:
        print("Initializing new database...")
        manager.initialize_database()
