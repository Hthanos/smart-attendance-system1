"""
Test database operations
"""

import unittest
import os
import tempfile
from pathlib import Path

from src.database.db_manager import DatabaseManager
from src.database.operations import DatabaseOperations


class TestDatabase(unittest.TestCase):
    """Test database functionality"""
    
    def setUp(self):
        """Setup test database"""
        self.temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        self.db_manager = DatabaseManager(self.temp_db.name)
        self.db_manager.initialize_database()
        self.db_ops = DatabaseOperations()
    
    def tearDown(self):
        """Cleanup test database"""
        try:
            os.unlink(self.temp_db.name)
        except:
            pass
    
    def test_add_student(self):
        """Test adding a student"""
        student_id = self.db_ops.add_student(
            registration_number="E028-01-1234/2024",
            full_name="Test Student",
            email="test@example.com"
        )
        self.assertIsNotNone(student_id)
    
    def test_get_student(self):
        """Test retrieving a student"""
        # Add student first
        student_id = self.db_ops.add_student(
            registration_number="E028-01-1235/2024",
            full_name="Test Student 2"
        )
        
        # Retrieve
        student = self.db_ops.get_student_by_id(student_id)
        self.assertIsNotNone(student)
        self.assertEqual(student['full_name'], "Test Student 2")


if __name__ == '__main__':
    unittest.main()
