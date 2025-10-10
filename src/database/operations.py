"""
Database Operations - CRUD operations for all tables
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, date, time

from .db_manager import db_manager


class DatabaseOperations:
    """Database CRUD operations"""
    
    # ==================== STUDENT OPERATIONS ====================
    
    @staticmethod
    def add_student(
        registration_number: str,
        full_name: str,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        department: Optional[str] = None,
        year_of_study: Optional[int] = None,
        program: Optional[str] = None,
        photo_path: Optional[str] = None
    ) -> Optional[int]:
        """
        Add a new student
        
        Returns:
            int: Student ID if successful, None otherwise
        """
        query = """
            INSERT INTO students (
                registration_number, full_name, email, phone, 
                department, year_of_study, program, photo_path
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        try:
            with db_manager.get_cursor() as cursor:
                cursor.execute(query, (
                    registration_number, full_name, email, phone,
                    department, year_of_study, program, photo_path
                ))
                return cursor.lastrowid
        except Exception as e:
            print(f"✗ Error adding student: {str(e)}")
            return None
    
    @staticmethod
    def get_student_by_id(student_id: int) -> Optional[Dict[str, Any]]:
        """Get student by ID"""
        query = "SELECT * FROM students WHERE id = ?"
        results = db_manager.execute_query(query, (student_id,))
        return dict(results[0]) if results else None
    
    @staticmethod
    def get_student_by_reg_number(reg_number: str) -> Optional[Dict[str, Any]]:
        """Get student by registration number"""
        query = "SELECT * FROM students WHERE registration_number = ?"
        results = db_manager.execute_query(query, (reg_number,))
        return dict(results[0]) if results else None
    
    @staticmethod
    def get_all_students(active_only: bool = True) -> List[Dict[str, Any]]:
        """Get all students"""
        if active_only:
            query = "SELECT * FROM students WHERE is_active = 1 ORDER BY full_name"
        else:
            query = "SELECT * FROM students ORDER BY full_name"
        
        results = db_manager.execute_query(query)
        return [dict(row) for row in results]
    
    @staticmethod
    def update_student(student_id: int, **kwargs) -> bool:
        """Update student information"""
        allowed_fields = [
            'full_name', 'email', 'phone', 'department', 
            'year_of_study', 'program', 'photo_path', 
            'face_encoding_path', 'is_active'
        ]
        
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
        
        if not updates:
            return False
        
        set_clause = ', '.join([f"{k} = ?" for k in updates.keys()])
        query = f"UPDATE students SET {set_clause} WHERE id = ?"
        
        values = list(updates.values()) + [student_id]
        
        try:
            rows_affected = db_manager.execute_update(query, tuple(values))
            return rows_affected > 0
        except Exception as e:
            print(f"✗ Error updating student: {str(e)}")
            return False
    
    @staticmethod
    def delete_student(student_id: int) -> bool:
        """Soft delete student (set is_active = 0)"""
        return DatabaseOperations.update_student(student_id, is_active=0)
    
    @staticmethod
    def search_students(search_term: str) -> List[Dict[str, Any]]:
        """Search students by name or registration number"""
        query = """
            SELECT * FROM students 
            WHERE is_active = 1 
            AND (full_name LIKE ? OR registration_number LIKE ?)
            ORDER BY full_name
        """
        search_pattern = f"%{search_term}%"
        results = db_manager.execute_query(query, (search_pattern, search_pattern))
        return [dict(row) for row in results]
    
    # ==================== COURSE OPERATIONS ====================
    
    @staticmethod
    def add_course(
        course_code: str,
        course_name: str,
        instructor: Optional[str] = None,
        semester: Optional[str] = None,
        academic_year: Optional[str] = None,
        credits: int = 3,
        description: Optional[str] = None
    ) -> Optional[int]:
        """Add a new course"""
        query = """
            INSERT INTO courses (
                course_code, course_name, instructor, semester, 
                academic_year, credits, description
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        
        try:
            with db_manager.get_cursor() as cursor:
                cursor.execute(query, (
                    course_code, course_name, instructor, semester,
                    academic_year, credits, description
                ))
                return cursor.lastrowid
        except Exception as e:
            print(f"✗ Error adding course: {str(e)}")
            return None
    
    @staticmethod
    def get_course_by_id(course_id: int) -> Optional[Dict[str, Any]]:
        """Get course by ID"""
        query = "SELECT * FROM courses WHERE id = ?"
        results = db_manager.execute_query(query, (course_id,))
        return dict(results[0]) if results else None
    
    @staticmethod
    def get_all_courses(active_only: bool = True) -> List[Dict[str, Any]]:
        """Get all courses"""
        if active_only:
            query = "SELECT * FROM courses WHERE is_active = 1 ORDER BY course_code"
        else:
            query = "SELECT * FROM courses ORDER BY course_code"
        
        results = db_manager.execute_query(query)
        return [dict(row) for row in results]
    
    @staticmethod
    def update_course(course_id: int, **kwargs) -> bool:
        """Update course information"""
        allowed_fields = [
            'course_name', 'instructor', 'semester', 
            'academic_year', 'credits', 'description', 'is_active'
        ]
        
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
        
        if not updates:
            return False
        
        set_clause = ', '.join([f"{k} = ?" for k in updates.keys()])
        query = f"UPDATE courses SET {set_clause} WHERE id = ?"
        
        values = list(updates.values()) + [course_id]
        
        try:
            rows_affected = db_manager.execute_update(query, tuple(values))
            return rows_affected > 0
        except Exception as e:
            print(f"✗ Error updating course: {str(e)}")
            return False
    
    # ==================== ENROLLMENT OPERATIONS ====================
    
    @staticmethod
    def enroll_student(student_id: int, course_id: int) -> Optional[int]:
        """Enroll a student in a course"""
        query = """
            INSERT INTO enrollments (student_id, course_id)
            VALUES (?, ?)
        """
        
        try:
            with db_manager.get_cursor() as cursor:
                cursor.execute(query, (student_id, course_id))
                return cursor.lastrowid
        except Exception as e:
            print(f"✗ Error enrolling student: {str(e)}")
            return None
    
    @staticmethod
    def get_student_courses(student_id: int) -> List[Dict[str, Any]]:
        """Get all courses for a student"""
        query = """
            SELECT c.* FROM courses c
            JOIN enrollments e ON c.id = e.course_id
            WHERE e.student_id = ? AND e.status = 'Active'
            ORDER BY c.course_code
        """
        results = db_manager.execute_query(query, (student_id,))
        return [dict(row) for row in results]
    
    @staticmethod
    def get_course_students(course_id: int) -> List[Dict[str, Any]]:
        """Get all students enrolled in a course"""
        query = """
            SELECT s.* FROM students s
            JOIN enrollments e ON s.id = e.student_id
            WHERE e.course_id = ? AND e.status = 'Active' AND s.is_active = 1
            ORDER BY s.full_name
        """
        results = db_manager.execute_query(query, (course_id,))
        return [dict(row) for row in results]
    
    # ==================== SESSION OPERATIONS ====================
    
    @staticmethod
    def create_session(
        course_id: int,
        session_date: date,
        start_time: Optional[time] = None,
        end_time: Optional[time] = None,
        location: Optional[str] = None,
        topic: Optional[str] = None,
        session_type: str = 'Lecture'
    ) -> Optional[int]:
        """Create a class session"""
        query = """
            INSERT INTO class_sessions (
                course_id, session_date, start_time, end_time, 
                location, topic, session_type
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        
        try:
            with db_manager.get_cursor() as cursor:
                cursor.execute(query, (
                    course_id, session_date, start_time, end_time,
                    location, topic, session_type
                ))
                return cursor.lastrowid
        except Exception as e:
            print(f"✗ Error creating session: {str(e)}")
            return None
    
    @staticmethod
    def get_session_by_id(session_id: int) -> Optional[Dict[str, Any]]:
        """Get session by ID"""
        query = "SELECT * FROM class_sessions WHERE id = ?"
        results = db_manager.execute_query(query, (session_id,))
        return dict(results[0]) if results else None
    
    @staticmethod
    def get_course_sessions(course_id: int) -> List[Dict[str, Any]]:
        """Get all sessions for a course"""
        query = """
            SELECT * FROM class_sessions 
            WHERE course_id = ? 
            ORDER BY session_date DESC, start_time DESC
        """
        results = db_manager.execute_query(query, (course_id,))
        return [dict(row) for row in results]
    
    @staticmethod
    def get_todays_sessions() -> List[Dict[str, Any]]:
        """Get today's sessions"""
        query = """
            SELECT cs.*, c.course_code, c.course_name
            FROM class_sessions cs
            JOIN courses c ON cs.course_id = c.id
            WHERE cs.session_date = DATE('now')
            ORDER BY cs.start_time
        """
        results = db_manager.execute_query(query)
        return [dict(row) for row in results]
    
    # ==================== ATTENDANCE OPERATIONS ====================
    
    @staticmethod
    def mark_attendance(
        student_id: int,
        session_id: int,
        confidence_score: Optional[float] = None,
        status: str = 'Present',
        marked_by: str = 'System',
        notes: Optional[str] = None
    ) -> Optional[int]:
        """Mark student attendance"""
        query = """
            INSERT OR REPLACE INTO attendance (
                student_id, session_id, confidence_score, 
                status, marked_by, notes
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """
        
        try:
            with db_manager.get_cursor() as cursor:
                cursor.execute(query, (
                    student_id, session_id, confidence_score,
                    status, marked_by, notes
                ))
                return cursor.lastrowid
        except Exception as e:
            print(f"✗ Error marking attendance: {str(e)}")
            return None
    
    @staticmethod
    def get_session_attendance(session_id: int) -> List[Dict[str, Any]]:
        """Get attendance for a session"""
        query = """
            SELECT 
                a.*, 
                s.registration_number, 
                s.full_name,
                s.department
            FROM attendance a
            JOIN students s ON a.student_id = s.id
            WHERE a.session_id = ?
            ORDER BY s.full_name
        """
        results = db_manager.execute_query(query, (session_id,))
        return [dict(row) for row in results]
    
    @staticmethod
    def get_student_attendance(student_id: int, course_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get student's attendance records"""
        if course_id:
            query = """
                SELECT 
                    a.*, 
                    cs.session_date, 
                    cs.start_time,
                    c.course_code,
                    c.course_name
                FROM attendance a
                JOIN class_sessions cs ON a.session_id = cs.id
                JOIN courses c ON cs.course_id = c.id
                WHERE a.student_id = ? AND cs.course_id = ?
                ORDER BY cs.session_date DESC
            """
            results = db_manager.execute_query(query, (student_id, course_id))
        else:
            query = """
                SELECT 
                    a.*, 
                    cs.session_date, 
                    cs.start_time,
                    c.course_code,
                    c.course_name
                FROM attendance a
                JOIN class_sessions cs ON a.session_id = cs.id
                JOIN courses c ON cs.course_id = c.id
                WHERE a.student_id = ?
                ORDER BY cs.session_date DESC
            """
            results = db_manager.execute_query(query, (student_id,))
        
        return [dict(row) for row in results]
    
    @staticmethod
    def check_attendance_marked(student_id: int, session_id: int) -> bool:
        """Check if attendance is already marked"""
        query = """
            SELECT COUNT(*) FROM attendance 
            WHERE student_id = ? AND session_id = ?
        """
        results = db_manager.execute_query(query, (student_id, session_id))
        return results[0][0] > 0 if results else False
    
    # ==================== STATISTICS ====================
    
    @staticmethod
    def get_student_attendance_percentage(student_id: int, course_id: Optional[int] = None) -> float:
        """Calculate student attendance percentage"""
        if course_id:
            query = """
                SELECT 
                    COUNT(DISTINCT cs.id) as total_sessions,
                    COUNT(DISTINCT a.session_id) as attended_sessions
                FROM class_sessions cs
                JOIN enrollments e ON cs.course_id = e.course_id
                LEFT JOIN attendance a ON cs.id = a.session_id AND a.student_id = e.student_id
                WHERE e.student_id = ? AND cs.course_id = ?
            """
            results = db_manager.execute_query(query, (student_id, course_id))
        else:
            query = """
                SELECT 
                    COUNT(DISTINCT cs.id) as total_sessions,
                    COUNT(DISTINCT a.session_id) as attended_sessions
                FROM class_sessions cs
                JOIN enrollments e ON cs.course_id = e.course_id
                LEFT JOIN attendance a ON cs.id = a.session_id AND a.student_id = e.student_id
                WHERE e.student_id = ?
            """
            results = db_manager.execute_query(query, (student_id,))
        
        if results and results[0]['total_sessions'] > 0:
            total = results[0]['total_sessions']
            attended = results[0]['attended_sessions']
            return round((attended / total) * 100, 2) if total > 0 else 0.0
        
        return 0.0
