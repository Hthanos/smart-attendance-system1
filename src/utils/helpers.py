"""
Helper utilities
"""

from datetime import datetime, date, time
from typing import Optional
import os


class Helpers:
    """General helper functions"""
    
    @staticmethod
    def format_date(date_obj: date, format_str: str = '%Y-%m-%d') -> str:
        """Format date object to string"""
        if isinstance(date_obj, str):
            return date_obj
        return date_obj.strftime(format_str)
    
    @staticmethod
    def format_time(time_obj: time, format_str: str = '%H:%M') -> str:
        """Format time object to string"""
        if isinstance(time_obj, str):
            return time_obj
        return time_obj.strftime(format_str)
    
    @staticmethod
    def parse_date(date_str: str, format_str: str = '%Y-%m-%d') -> Optional[date]:
        """Parse date string to date object"""
        try:
            return datetime.strptime(date_str, format_str).date()
        except:
            return None
    
    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """Format file size in human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
    
    @staticmethod
    def ensure_directory(path: str):
        """Ensure directory exists"""
        os.makedirs(path, exist_ok=True)
    
    @staticmethod
    def get_timestamp(format_str: str = '%Y%m%d_%H%M%S') -> str:
        """Get current timestamp as string"""
        return datetime.now().strftime(format_str)
