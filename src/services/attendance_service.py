"""
Attendance Service - Business logic for attendance management
"""

from datetime import date, time, datetime
from typing import Optional, List, Dict, Any
import logging

from src.core.attendance_logger import AttendanceLogger
from src.database.operations import DatabaseOperations
from config.settings import Settings

logger = logging.getLogger(__name__)


class AttendanceService:
    """Handles attendance management operations"""
    
    def __init__(self):
        """Initialize attendance service"""
        self.attendance_logger = AttendanceLogger()
        self.db_ops = DatabaseOperations()
    
    def create_session(
        self,
        course_id: int,
        session_date: date,
        start_time: Optional[time] = None,
        end_time: Optional[time] = None,
        location: Optional[str] = None,
        topic: Optional[str] = None
    ) -> Optional[int]:
        """Create a new class session"""
        return self.db_ops.create_session(
            course_id=course_id,
            session_date=session_date,
            start_time=start_time,
            end_time=end_time,
            location=location,
            topic=topic
        )
    
    def mark_attendance(
        self,
        student_id: int,
        session_id: int,
        confidence_score: Optional[float] = None
    ) -> bool:
        """Mark student attendance"""
        return self.attendance_logger.mark_present(
            student_id=student_id,
            session_id=session_id,
            confidence_score=confidence_score
        )
    
    def get_todays_sessions(self) -> List[Dict[str, Any]]:
        """Get today's sessions"""
        return self.attendance_logger.get_todays_sessions()
    
    def get_session_attendance(self, session_id: int) -> List[Dict[str, Any]]:
        """Get attendance for a session"""
        return self.attendance_logger.get_session_attendance(session_id)
    
    def calculate_attendance_rate(self, session_id: int) -> Dict[str, Any]:
        """Calculate attendance statistics"""
        return self.attendance_logger.calculate_attendance_rate(session_id)
