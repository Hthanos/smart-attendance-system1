"""
Database package for Smart Class Attendance System
"""

from .db_manager import DatabaseManager
from .operations import DatabaseOperations

__all__ = ['DatabaseManager', 'DatabaseOperations']
