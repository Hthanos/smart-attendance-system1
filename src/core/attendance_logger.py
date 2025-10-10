"""
Attendance Logger - Handles attendance recording logic
"""

from datetime import datetime, date, time
from typing import Optional, Dict, Any, List
import logging

from src.database.operations import DatabaseOperations
from config.settings import Settings

logger = logging.getLogger(__name__)


class AttendanceLogger:
    """Manages attendance logging and validation"""
    
    def __init__(self):
        """Initialize attendance logger"""
        self.db_ops = DatabaseOperations()
    
    def mark_present(
        self,
        student_id: int,
        session_id: int,
        confidence_score: Optional[float] = None,
        notes: Optional[str] = None
    ) -> bool:
        """
        Mark student as present for a session
        
        Args:
            student_id: Student database ID
            session_id: Class session ID
            confidence_score: Recognition confidence score
            notes: Optional notes
        
        Returns:
            bool: True if successful
        """
        try:
            # Check if already marked
            if self.db_ops.check_attendance_marked(student_id, session_id):
                logger.warning(f"Attendance already marked for student {student_id} in session {session_id}")
                return False
            
            # Mark attendance
            attendance_id = self.db_ops.mark_attendance(
                student_id=student_id,
                session_id=session_id,
                confidence_score=confidence_score,
                status='Present',
                marked_by='System',
                notes=notes
            )
            
            if attendance_id:
                logger.info(f"Attendance marked: Student {student_id}, Session {session_id}")
                return True
            else:
                logger.error(f"Failed to mark attendance: Student {student_id}, Session {session_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error marking attendance: {str(e)}")
            return False
    
    def mark_absent(
        self,
        student_id: int,
        session_id: int,
        notes: Optional[str] = None
    ) -> bool:
        """
        Mark student as absent
        
        Args:
            student_id: Student database ID
            session_id: Class session ID
            notes: Optional notes
        
        Returns:
            bool: True if successful
        """
        try:
            attendance_id = self.db_ops.mark_attendance(
                student_id=student_id,
                session_id=session_id,
                status='Absent',
                marked_by='Manual',
                notes=notes
            )
            
            return attendance_id is not None
            
        except Exception as e:
            logger.error(f"Error marking absent: {str(e)}")
            return False
    
    def mark_late(
        self,
        student_id: int,
        session_id: int,
        confidence_score: Optional[float] = None,
        notes: Optional[str] = None
    ) -> bool:
        """
        Mark student as late
        
        Args:
            student_id: Student database ID
            session_id: Class session ID
            confidence_score: Recognition confidence score
            notes: Optional notes
        
        Returns:
            bool: True if successful
        """
        try:
            attendance_id = self.db_ops.mark_attendance(
                student_id=student_id,
                session_id=session_id,
                confidence_score=confidence_score,
                status='Late',
                marked_by='System',
                notes=notes
            )
            
            return attendance_id is not None
            
        except Exception as e:
            logger.error(f"Error marking late: {str(e)}")
            return False
    
    def is_attendance_marked(self, student_id: int, session_id: int) -> bool:
        """
        Check if attendance is already marked
        
        Args:
            student_id: Student database ID
            session_id: Class session ID
        
        Returns:
            bool: True if already marked
        """
        return self.db_ops.check_attendance_marked(student_id, session_id)
    
    def get_session_attendance(self, session_id: int) -> List[Dict[str, Any]]:
        """
        Get all attendance records for a session
        
        Args:
            session_id: Class session ID
        
        Returns:
            List of attendance records
        """
        return self.db_ops.get_session_attendance(session_id)
    
    def get_student_attendance(
        self, 
        student_id: int, 
        course_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get attendance records for a student
        
        Args:
            student_id: Student database ID
            course_id: Optional course ID to filter
        
        Returns:
            List of attendance records
        """
        return self.db_ops.get_student_attendance(student_id, course_id)
    
    def calculate_attendance_rate(self, session_id: int) -> Dict[str, Any]:
        """
        Calculate attendance rate for a session
        
        Args:
            session_id: Class session ID
        
        Returns:
            Dictionary with attendance statistics
        """
        try:
            # Get session info
            session = self.db_ops.get_session_by_id(session_id)
            if not session:
                return {}
            
            # Get enrolled students
            enrolled = self.db_ops.get_course_students(session['course_id'])
            total_students = len(enrolled)
            
            # Get attendance records
            attendance = self.get_session_attendance(session_id)
            present_count = sum(1 for a in attendance if a['status'] == 'Present')
            late_count = sum(1 for a in attendance if a['status'] == 'Late')
            absent_count = total_students - len(attendance)
            
            # Calculate rate
            attendance_rate = (present_count / total_students * 100) if total_students > 0 else 0.0
            
            return {
                'session_id': session_id,
                'total_students': total_students,
                'present': present_count,
                'late': late_count,
                'absent': absent_count,
                'attendance_rate': round(attendance_rate, 2)
            }
            
        except Exception as e:
            logger.error(f"Error calculating attendance rate: {str(e)}")
            return {}
    
    def get_absent_students(self, session_id: int) -> List[Dict[str, Any]]:
        """
        Get list of students who are absent for a session
        
        Args:
            session_id: Class session ID
        
        Returns:
            List of absent students
        """
        try:
            # Get session info
            session = self.db_ops.get_session_by_id(session_id)
            if not session:
                return []
            
            # Get all enrolled students
            enrolled = self.db_ops.get_course_students(session['course_id'])
            
            # Get students who marked attendance
            attendance = self.get_session_attendance(session_id)
            attended_ids = {a['student_id'] for a in attendance}
            
            # Find absent students
            absent_students = [s for s in enrolled if s['id'] not in attended_ids]
            
            return absent_students
            
        except Exception as e:
            logger.error(f"Error getting absent students: {str(e)}")
            return []
    
    def auto_mark_absent(self, session_id: int) -> int:
        """
        Automatically mark all students who didn't attend as absent
        
        Args:
            session_id: Class session ID
        
        Returns:
            int: Number of students marked absent
        """
        try:
            absent_students = self.get_absent_students(session_id)
            count = 0
            
            for student in absent_students:
                if self.mark_absent(student['id'], session_id, notes="Auto-marked"):
                    count += 1
            
            logger.info(f"Auto-marked {count} students as absent for session {session_id}")
            return count
            
        except Exception as e:
            logger.error(f"Error auto-marking absent: {str(e)}")
            return 0
    
    def validate_session_active(self, session_id: int) -> bool:
        """
        Check if a session is active (today)
        
        Args:
            session_id: Class session ID
        
        Returns:
            bool: True if session is today
        """
        try:
            session = self.db_ops.get_session_by_id(session_id)
            if not session:
                return False
            
            session_date = session['session_date']
            today = date.today().isoformat()
            
            return session_date == today
            
        except Exception as e:
            logger.error(f"Error validating session: {str(e)}")
            return False
    
    def get_todays_sessions(self) -> List[Dict[str, Any]]:
        """
        Get all sessions scheduled for today
        
        Returns:
            List of session records
        """
        return self.db_ops.get_todays_sessions()
    
    def generate_attendance_summary(
        self, 
        student_id: int, 
        course_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Generate attendance summary for a student
        
        Args:
            student_id: Student database ID
            course_id: Optional course ID
        
        Returns:
            Dictionary with attendance summary
        """
        try:
            attendance_records = self.get_student_attendance(student_id, course_id)
            
            total_sessions = len(attendance_records)
            present_count = sum(1 for a in attendance_records if a['status'] == 'Present')
            late_count = sum(1 for a in attendance_records if a['status'] == 'Late')
            absent_count = sum(1 for a in attendance_records if a['status'] == 'Absent')
            
            attendance_percentage = (present_count / total_sessions * 100) if total_sessions > 0 else 0.0
            
            return {
                'student_id': student_id,
                'course_id': course_id,
                'total_sessions': total_sessions,
                'present': present_count,
                'late': late_count,
                'absent': absent_count,
                'attendance_percentage': round(attendance_percentage, 2)
            }
            
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            return {}


def test_attendance_logger():
    """Test attendance logger"""
    print("Testing Attendance Logger...")
    
    logger_instance = AttendanceLogger()
    print("✓ Attendance logger initialized")
    
    # Note: Full testing requires database setup
    print("✓ Basic initialization test passed")
    print("  (Full tests require database setup)")
    
    return True


if __name__ == '__main__':
    test_attendance_logger()
