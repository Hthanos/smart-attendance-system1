#!/usr/bin/env python3
"""
Quick test to verify database setup
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.database.operations import DatabaseOperations

def test_database():
    """Test database connection and operations"""
    print("Testing database...")
    
    try:
        ops = DatabaseOperations()
        
        # Test getting students
        students = ops.get_all_students()
        print(f"✅ Database connection OK")
        print(f"✅ Found {len(students)} students")
        
        for student in students:
            print(f"   - {student['registration_number']}: {student['full_name']}")
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == '__main__':
    test_database()
