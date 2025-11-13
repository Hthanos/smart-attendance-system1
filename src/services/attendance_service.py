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
    
    def search_records(
        self,
        student_id: Optional[int] = None,
        course_id: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search attendance records with filters
        
        Args:
            student_id: Filter by student
            course_id: Filter by course
            start_date: Start date range
            end_date: End date range
            status: Filter by status (present/absent/late)
            
        Returns:
            List of attendance records
        """
        try:
            # Build SQL query with filters
            query = """
                SELECT 
                    a.id,
                    a.timestamp,
                    a.status,
                    a.confidence_score,
                    s.full_name as student_name,
                    s.registration_number,
                    c.course_code,
                    c.course_name,
                    cs.session_date
                FROM attendance a
                JOIN students s ON a.student_id = s.id
                JOIN class_sessions cs ON a.session_id = cs.id
                JOIN courses c ON cs.course_id = c.id
                WHERE 1=1
            """
            
            params = []
            
            if student_id:
                query += " AND a.student_id = ?"
                params.append(student_id)
            
            if course_id:
                query += " AND cs.course_id = ?"
                params.append(course_id)
            
            if start_date:
                query += " AND cs.session_date >= ?"
                params.append(start_date)
            
            if end_date:
                query += " AND cs.session_date <= ?"
                params.append(end_date)
            
            if status and status.lower() != 'all':
                query += " AND a.status = ?"
                params.append(status.lower())
            
            query += " ORDER BY a.timestamp DESC"
            
            # Execute query
            import sqlite3
            conn = sqlite3.connect(Settings.DATABASE_PATH)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query, params)
            
            rows = cursor.fetchall()
            conn.close()
            
            # Format results
            records = []
            for row in rows:
                timestamp = datetime.fromisoformat(row['timestamp'])
                record = {
                    'date': row['session_date'],
                    'time': timestamp.strftime('%H:%M:%S'),
                    'student_name': row['student_name'],
                    'registration_number': row['registration_number'],
                    'course_code': row['course_code'],
                    'course_name': row['course_name'],
                    'status': row['status'].capitalize(),
                    'confidence_score': row['confidence_score']
                }
                records.append(record)
            
            return records
            
        except Exception as e:
            logger.error(f"Error searching records: {e}")
            return []
