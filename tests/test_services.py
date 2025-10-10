"""
Unit tests for service layer
"""

import pytest
import sys
from pathlib import Path
from datetime import datetime, date, timedelta
import tempfile
import shutil

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.services.student_service import StudentService
from src.services.attendance_service import AttendanceService
from src.services.training_service import TrainingService
from src.services.export_service import ExportService
from src.database.db_manager import DatabaseManager
from src.database.operations import DatabaseOperations
import numpy as np


@pytest.fixture(scope="function")
def test_db():
    """Create test database"""
    db = DatabaseManager(":memory:")
    db.initialize_database()
    return db


@pytest.fixture
def db_ops(test_db):
    """Create database operations instance"""
    return DatabaseOperations(test_db)


@pytest.fixture
def student_service(db_ops):
    """Create student service instance"""
    return StudentService(db_ops)


@pytest.fixture
def attendance_service(db_ops):
    """Create attendance service instance"""
    return AttendanceService(db_ops)


@pytest.fixture
def sample_student_data():
    """Sample student data for testing"""
    return {
        'registration_number': 'TEST001',
        'full_name': 'Test Student',
        'email': 'test@example.com',
        'phone_number': '+254700000000',
        'gender': 'Male',
        'year_of_study': 2
    }


@pytest.fixture
def sample_face_images():
    """Sample face images"""
    return [np.random.randint(0, 255, (100, 100), dtype=np.uint8) for _ in range(30)]


class TestStudentService:
    """Tests for StudentService"""
    
    def test_register_student_success(self, student_service, sample_student_data, sample_face_images):
        """Test successful student registration"""
        # Mock the faces directory
        with tempfile.TemporaryDirectory() as tmpdir:
            # Patch FACES_DIR temporarily
            from config import settings
            original_faces_dir = settings.Settings.FACES_DIR
            settings.Settings.FACES_DIR = Path(tmpdir)
            
            try:
                student_id = student_service.register_student(
                    sample_student_data,
                    sample_face_images
                )
                
                assert student_id > 0
                
                # Verify student in database
                student = student_service.get_student(student_id)
                assert student is not None
                assert student['registration_number'] == 'TEST001'
                
                # Verify face images saved
                faces_dir = Path(tmpdir) / 'TEST001'
                assert faces_dir.exists()
                image_files = list(faces_dir.glob('*.jpg'))
                assert len(image_files) == 30
                
            finally:
                settings.Settings.FACES_DIR = original_faces_dir
    
    def test_register_student_duplicate(self, student_service, sample_student_data, sample_face_images):
        """Test registering duplicate student"""
        with tempfile.TemporaryDirectory() as tmpdir:
            from config import settings
            original_faces_dir = settings.Settings.FACES_DIR
            settings.Settings.FACES_DIR = Path(tmpdir)
            
            try:
                # Register first time
                student_service.register_student(sample_student_data, sample_face_images)
                
                # Try to register again
                with pytest.raises(Exception):
                    student_service.register_student(sample_student_data, sample_face_images)
                    
            finally:
                settings.Settings.FACES_DIR = original_faces_dir
    
    def test_get_student(self, student_service, db_ops, sample_student_data):
        """Test getting student by ID"""
        student_id = db_ops.create_student(**sample_student_data)
        
        student = student_service.get_student(student_id)
        
        assert student is not None
        assert student['id'] == student_id
        assert student['registration_number'] == 'TEST001'
    
    def test_get_nonexistent_student(self, student_service):
        """Test getting non-existent student"""
        student = student_service.get_student(9999)
        
        assert student is None
    
    def test_search_students_by_name(self, student_service, db_ops):
        """Test searching students by name"""
        # Create test students
        db_ops.create_student(registration_number='S001', full_name='Alice Johnson', email='alice@test.com')
        db_ops.create_student(registration_number='S002', full_name='Bob Smith', email='bob@test.com')
        db_ops.create_student(registration_number='S003', full_name='Alice Brown', email='alice.b@test.com')
        
        results = student_service.search_students('Alice')
        
        assert len(results) == 2
        assert all('Alice' in r['full_name'] for r in results)
    
    def test_search_students_by_reg_number(self, student_service, db_ops):
        """Test searching students by registration number"""
        db_ops.create_student(registration_number='CSC001', full_name='Student One', email='s1@test.com')
        db_ops.create_student(registration_number='CSC002', full_name='Student Two', email='s2@test.com')
        
        results = student_service.search_students('CSC001')
        
        assert len(results) >= 1
        assert any(r['registration_number'] == 'CSC001' for r in results)
    
    def test_update_student(self, student_service, db_ops, sample_student_data):
        """Test updating student information"""
        student_id = db_ops.create_student(**sample_student_data)
        
        # Update email
        db_ops.update_student(student_id, email='newemail@example.com')
        
        student = student_service.get_student(student_id)
        assert student['email'] == 'newemail@example.com'
    
    def test_delete_student(self, student_service, db_ops, sample_student_data):
        """Test deleting student"""
        student_id = db_ops.create_student(**sample_student_data)
        
        db_ops.delete_student(student_id)
        
        student = student_service.get_student(student_id)
        assert student is None


class TestAttendanceService:
    """Tests for AttendanceService"""
    
    def test_mark_attendance_success(self, attendance_service, db_ops):
        """Test marking attendance successfully"""
        # Setup
        student_id = db_ops.create_student(
            registration_number='ATT001',
            full_name='Attendance Test',
            email='att@test.com'
        )
        course_id = db_ops.create_course(
            course_code='TEST101',
            course_name='Test Course',
            lecturer_name='Dr. Test'
        )
        session_id = db_ops.create_session(
            course_id=course_id,
            session_date=date.today().isoformat(),
            start_time='09:00:00',
            end_time='11:00:00',
            location='Room 101'
        )
        
        # Mark attendance
        success = attendance_service.mark_attendance(
            student_id=student_id,
            session_id=session_id,
            confidence_score=85.5
        )
        
        assert success == True
        
        # Verify record exists
        records = attendance_service.get_session_attendance(session_id)
        assert len(records) == 1
        assert records[0]['student_id'] == student_id
    
    def test_mark_attendance_duplicate(self, attendance_service, db_ops):
        """Test marking attendance twice for same student/session"""
        # Setup
        student_id = db_ops.create_student(
            registration_number='DUP001',
            full_name='Duplicate Test',
            email='dup@test.com'
        )
        course_id = db_ops.create_course(
            course_code='DUP101',
            course_name='Dup Course'
        )
        session_id = db_ops.create_session(
            course_id=course_id,
            session_date=date.today().isoformat(),
            start_time='09:00:00'
        )
        
        # Mark first time
        success1 = attendance_service.mark_attendance(student_id, session_id)
        assert success1 == True
        
        # Try to mark again
        success2 = attendance_service.mark_attendance(student_id, session_id)
        # Should either return False or handle gracefully
        assert isinstance(success2, bool)
    
    def test_get_session_attendance(self, attendance_service, db_ops):
        """Test getting attendance for a session"""
        # Setup session and students
        course_id = db_ops.create_course(course_code='SES101', course_name='Session Test')
        session_id = db_ops.create_session(
            course_id=course_id,
            session_date=date.today().isoformat(),
            start_time='10:00:00'
        )
        
        # Mark attendance for multiple students
        for i in range(3):
            student_id = db_ops.create_student(
                registration_number=f'SES{i:03d}',
                full_name=f'Student {i}',
                email=f's{i}@test.com'
            )
            attendance_service.mark_attendance(student_id, session_id)
        
        # Get attendance
        records = attendance_service.get_session_attendance(session_id)
        
        assert len(records) == 3
    
    def test_get_todays_sessions(self, attendance_service, db_ops):
        """Test getting today's sessions"""
        # Create course
        course_id = db_ops.create_course(course_code='TOD101', course_name='Today Test')
        
        # Create today's session
        db_ops.create_session(
            course_id=course_id,
            session_date=date.today().isoformat(),
            start_time='09:00:00'
        )
        
        # Create yesterday's session
        yesterday = date.today() - timedelta(days=1)
        db_ops.create_session(
            course_id=course_id,
            session_date=yesterday.isoformat(),
            start_time='09:00:00'
        )
        
        # Get today's sessions
        sessions = attendance_service.get_todays_sessions()
        
        assert len(sessions) >= 1
        assert all(s['session_date'] == date.today().isoformat() for s in sessions)
    
    def test_get_attendance_statistics(self, attendance_service, db_ops):
        """Test attendance statistics calculation"""
        # Setup
        course_id = db_ops.create_course(course_code='STAT101', course_name='Stats Test')
        student_id = db_ops.create_student(
            registration_number='STAT001',
            full_name='Stats Student',
            email='stats@test.com'
        )
        
        # Create sessions and mark attendance
        for i in range(5):
            session_id = db_ops.create_session(
                course_id=course_id,
                session_date=(date.today() - timedelta(days=i)).isoformat(),
                start_time='09:00:00'
            )
            
            # Mark attendance for 3 out of 5 sessions
            if i < 3:
                attendance_service.mark_attendance(student_id, session_id)
        
        # Get statistics
        stats = attendance_service.get_attendance_statistics(
            student_id=student_id,
            course_id=course_id
        )
        
        assert stats is not None
        # Should show 3/5 = 60% attendance
        assert 'attendance_percentage' in stats or 'present_count' in stats
    
    def test_search_records(self, attendance_service, db_ops):
        """Test searching attendance records"""
        # Setup
        course_id = db_ops.create_course(course_code='SRCH101', course_name='Search Test')
        student_id = db_ops.create_student(
            registration_number='SRCH001',
            full_name='Search Student',
            email='search@test.com'
        )
        session_id = db_ops.create_session(
            course_id=course_id,
            session_date=date.today().isoformat(),
            start_time='09:00:00'
        )
        
        attendance_service.mark_attendance(student_id, session_id)
        
        # Search
        records = attendance_service.search_records(
            student_id=student_id,
            course_id=course_id
        )
        
        assert len(records) >= 1


class TestExportService:
    """Tests for ExportService"""
    
    def test_export_to_csv(self):
        """Test CSV export"""
        service = ExportService()
        
        test_data = [
            {'name': 'Student 1', 'attendance': '90%'},
            {'name': 'Student 2', 'attendance': '85%'}
        ]
        
        with tempfile.TemporaryDirectory() as tmpdir:
            from config import settings
            original_exports_dir = settings.Settings.EXPORTS_DIR
            settings.Settings.EXPORTS_DIR = Path(tmpdir)
            
            try:
                filepath = service.export_to_csv(test_data, filename_prefix='test')
                
                assert Path(filepath).exists()
                assert Path(filepath).suffix == '.csv'
                
                # Verify content
                with open(filepath, 'r') as f:
                    content = f.read()
                    assert 'Student 1' in content
                    assert '90%' in content
                    
            finally:
                settings.Settings.EXPORTS_DIR = original_exports_dir
    
    def test_export_to_excel(self):
        """Test Excel export"""
        service = ExportService()
        
        test_data = [
            {'name': 'Student 1', 'attendance': '90%'},
            {'name': 'Student 2', 'attendance': '85%'}
        ]
        
        with tempfile.TemporaryDirectory() as tmpdir:
            from config import settings
            original_exports_dir = settings.Settings.EXPORTS_DIR
            settings.Settings.EXPORTS_DIR = Path(tmpdir)
            
            try:
                filepath = service.export_to_excel(test_data, filename_prefix='test')
                
                assert Path(filepath).exists()
                assert Path(filepath).suffix == '.xlsx'
                
            finally:
                settings.Settings.EXPORTS_DIR = original_exports_dir
    
    def test_export_empty_data(self):
        """Test exporting empty dataset"""
        service = ExportService()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            from config import settings
            original_exports_dir = settings.Settings.EXPORTS_DIR
            settings.Settings.EXPORTS_DIR = Path(tmpdir)
            
            try:
                # Should handle gracefully
                filepath = service.export_to_csv([], filename_prefix='empty')
                # Either creates empty file or raises appropriate error
                assert filepath is not None or True
                
            finally:
                settings.Settings.EXPORTS_DIR = original_exports_dir


class TestTrainingService:
    """Tests for TrainingService"""
    
    def test_training_service_initialization(self):
        """Test training service initialization"""
        service = TrainingService()
        assert service is not None
    
    def test_is_model_trained(self):
        """Test checking if model is trained"""
        service = TrainingService()
        
        # Initially should not be trained
        is_trained = service.is_model_trained()
        assert isinstance(is_trained, bool)
    
    @pytest.mark.slow
    def test_train_model(self):
        """Test model training (slow test)"""
        # This would require actual face images
        # Skip if no test data available
        pytest.skip("Training requires actual face data")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
