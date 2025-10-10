"""
Student Service - Business logic for student management
"""

import os
from pathlib import Path
from typing import Optional, List, Dict, Any
import logging
import shutil

from src.database.operations import DatabaseOperations
from config.settings import Settings

logger = logging.getLogger(__name__)


class StudentService:
    """Handles student management operations"""
    
    def __init__(self):
        """Initialize student service"""
        self.db_ops = DatabaseOperations()
    
    def register_student(
        self,
        registration_number: str,
        full_name: str,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        department: Optional[str] = None,
        year_of_study: Optional[int] = None,
        program: Optional[str] = None
    ) -> Optional[int]:
        """
        Register a new student
        
        Args:
            registration_number: Student registration number
            full_name: Full name
            email: Email address
            phone: Phone number
            department: Department name
            year_of_study: Year of study (1-5)
            program: Program name
        
        Returns:
            int: Student ID if successful, None otherwise
        """
        try:
            # Check if student already exists
            existing = self.db_ops.get_student_by_reg_number(registration_number)
            if existing:
                logger.error(f"Student already exists: {registration_number}")
                return None
            
            # Add student to database
            student_id = self.db_ops.add_student(
                registration_number=registration_number,
                full_name=full_name,
                email=email,
                phone=phone,
                department=department,
                year_of_study=year_of_study,
                program=program
            )
            
            if student_id:
                # Create face images directory
                self._create_student_directory(registration_number)
                logger.info(f"Student registered: {registration_number} (ID: {student_id})")
            
            return student_id
            
        except Exception as e:
            logger.error(f"Error registering student: {str(e)}")
            return None
    
    def get_student(self, student_id: int) -> Optional[Dict[str, Any]]:
        """Get student by ID"""
        return self.db_ops.get_student_by_id(student_id)
    
    def get_student_by_reg_number(self, reg_number: str) -> Optional[Dict[str, Any]]:
        """Get student by registration number"""
        return self.db_ops.get_student_by_reg_number(reg_number)
    
    def get_all_students(self, active_only: bool = True) -> List[Dict[str, Any]]:
        """Get all students"""
        return self.db_ops.get_all_students(active_only)
    
    def search_students(self, search_term: str) -> List[Dict[str, Any]]:
        """Search students by name or registration number"""
        return self.db_ops.search_students(search_term)
    
    def update_student(self, student_id: int, **kwargs) -> bool:
        """Update student information"""
        return self.db_ops.update_student(student_id, **kwargs)
    
    def delete_student(self, student_id: int) -> bool:
        """Delete student (soft delete)"""
        return self.db_ops.delete_student(student_id)
    
    def _create_student_directory(self, registration_number: str):
        """Create directory for student face images"""
        student_dir = Settings.FACES_DIR / registration_number
        student_dir.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Created directory: {student_dir}")
    
    def get_student_face_images_dir(self, registration_number: str) -> Path:
        """Get path to student's face images directory"""
        return Settings.FACES_DIR / registration_number
    
    def count_student_images(self, registration_number: str) -> int:
        """Count number of face images for a student"""
        student_dir = self.get_student_face_images_dir(registration_number)
        
        if not student_dir.exists():
            return 0
        
        image_extensions = ['.jpg', '.jpeg', '.png']
        count = sum(1 for f in student_dir.iterdir() 
                   if f.is_file() and f.suffix.lower() in image_extensions)
        
        return count
    
    def get_student_images(self, registration_number: str) -> List[Path]:
        """Get list of face image paths for a student"""
        student_dir = self.get_student_face_images_dir(registration_number)
        
        if not student_dir.exists():
            return []
        
        image_extensions = ['.jpg', '.jpeg', '.png']
        images = [f for f in student_dir.iterdir() 
                 if f.is_file() and f.suffix.lower() in image_extensions]
        
        return sorted(images)
    
    def delete_student_images(self, registration_number: str) -> bool:
        """Delete all face images for a student"""
        try:
            student_dir = self.get_student_face_images_dir(registration_number)
            
            if student_dir.exists():
                shutil.rmtree(student_dir)
                logger.info(f"Deleted images for student: {registration_number}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error deleting student images: {str(e)}")
            return False
    
    def enroll_in_course(self, student_id: int, course_id: int) -> bool:
        """Enroll student in a course"""
        try:
            enrollment_id = self.db_ops.enroll_student(student_id, course_id)
            if enrollment_id:
                logger.info(f"Student {student_id} enrolled in course {course_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error enrolling student: {str(e)}")
            return False
    
    def get_student_courses(self, student_id: int) -> List[Dict[str, Any]]:
        """Get all courses for a student"""
        return self.db_ops.get_student_courses(student_id)
    
    def get_student_attendance_summary(
        self, 
        student_id: int,
        course_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Get attendance summary for a student"""
        percentage = self.db_ops.get_student_attendance_percentage(student_id, course_id)
        attendance_records = self.db_ops.get_student_attendance(student_id, course_id)
        
        return {
            'student_id': student_id,
            'course_id': course_id,
            'attendance_percentage': percentage,
            'total_records': len(attendance_records),
            'records': attendance_records
        }
    
    def validate_registration_number(self, reg_number: str) -> bool:
        """Validate registration number format"""
        # Example format: E028-01-1532/2022
        if not reg_number:
            return False
        
        # Add your validation logic here
        return len(reg_number) > 0
    
    def get_students_needing_training(self) -> List[Dict[str, Any]]:
        """Get students who have images but model not trained"""
        students = self.get_all_students()
        needs_training = []
        
        for student in students:
            image_count = self.count_student_images(student['registration_number'])
            if image_count >= Settings.IMAGES_PER_STUDENT:
                needs_training.append({
                    **student,
                    'image_count': image_count
                })
        
        return needs_training
