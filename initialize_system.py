#!/usr/bin/env python3
"""
Initialize the attendance system database and train the face recognition model
"""

import sys
import os
from pathlib import Path
import sqlite3
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.database.db_manager import DatabaseManager
from src.database.operations import DatabaseOperations


def initialize_database():
    """Initialize the database with schema"""
    print("\n" + "="*60)
    print("INITIALIZING DATABASE")
    print("="*60)
    
    db_path = Path('data/database/attendance.db')
    
    # Check if database already exists
    if db_path.exists():
        response = input(f"\nDatabase already exists at {db_path}. Reinitialize? (y/N): ")
        if response.lower() != 'y':
            print("Skipping database initialization.")
            return False
        
        # Backup existing database
        backup_path = db_path.parent / f"attendance_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        print(f"Backing up existing database to {backup_path}")
        import shutil
        shutil.copy(db_path, backup_path)
    
    # Initialize database
    print("\nCreating database schema...")
    db_manager = DatabaseManager()
    db_manager.initialize_database()
    print("✅ Database initialized successfully!")
    
    return True


def add_students_from_faces():
    """Add students to database based on face directories"""
    print("\n" + "="*60)
    print("ADDING STUDENTS FROM FACE DIRECTORIES")
    print("="*60)
    
    faces_dir = Path('data/faces')
    ops = DatabaseOperations()
    
    # Get existing registration numbers
    existing_students = ops.get_all_students()
    # Handle both 'id' and 'student_id' column names
    existing_reg_numbers = {s['registration_number'] for s in existing_students}
    
    # Scan face directories
    student_dirs = [d for d in faces_dir.iterdir() if d.is_dir()]
    print(f"\nFound {len(student_dirs)} student directories in data/faces/")
    
    added_count = 0
    for student_dir in student_dirs:
        # Convert directory name to registration number format
        # E028-01-1303-2020 -> E028-01-1303/2020
        reg_number = student_dir.name.replace('-2020', '/2020').replace('-2022', '/2022')
        
        # Check if student already exists
        if reg_number in existing_reg_numbers:
            print(f"⏭️  Student {reg_number} already exists, skipping")
            continue
        
        # Count images
        image_files = list(student_dir.glob('*.jpg')) + list(student_dir.glob('*.jpeg')) + list(student_dir.glob('*.png'))
        num_images = len(image_files)
        
        if num_images < 7:
            print(f"⚠️  {reg_number}: Only {num_images} images found (minimum 7 required)")
            print(f"   Skipping - please add more images")
            continue
        elif num_images < 10:
            print(f"⚠️  {reg_number}: Only {num_images} images found (10+ recommended for better accuracy)")
        
        # Prompt for student details
        print(f"\n📝 Adding student: {reg_number}")
        print(f"   Found {num_images} face images")
        
        first_name = input(f"   First Name: ").strip()
        if not first_name:
            print(f"   Skipping (no name provided)")
            continue
            
        last_name = input(f"   Last Name: ").strip()
        full_name = f"{first_name} {last_name}".strip()
        
        email = input(f"   Email (optional): ").strip() or None
        phone = input(f"   Phone (optional): ").strip() or None
        
        try:
            student_id = ops.add_student(
                registration_number=reg_number,
                full_name=full_name,
                email=email,
                phone=phone
            )
            
            if student_id:
                print(f"✅ Added student: {full_name} ({reg_number})")
                added_count += 1
            else:
                print(f"❌ Failed to add student {reg_number}")
        except Exception as e:
            print(f"❌ Error adding student {reg_number}: {e}")
            
        except Exception as e:
            print(f"❌ Error adding student {reg_number}: {e}")
    
    print(f"\n✅ Added {added_count} new students to database")
    
    # Show summary
    all_students = ops.get_all_students()
    print(f"\nTotal students in database: {len(all_students)}")
    
    return added_count > 0


def add_sample_courses():
    """Add sample courses"""
    print("\n" + "="*60)
    print("ADDING SAMPLE COURSES")
    print("="*60)
    
    ops = DatabaseOperations()
    
    # Check if courses already exist
    conn = sqlite3.connect('data/database/attendance.db')
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM courses")
    count = cursor.fetchone()[0]
    conn.close()
    
    if count > 0:
        print(f"Courses already exist ({count} courses found)")
        response = input("Add more courses? (y/N): ")
        if response.lower() != 'y':
            return
    
    # Sample courses
    sample_courses = [
        {
            'code': 'EEE301',
            'name': 'Digital Signal Processing',
            'lecturer': 'Dr. Tafara',
            'schedule': 'Mon/Wed 10:00-12:00'
        },
        {
            'code': 'EEE302',
            'name': 'Power Electronics',
            'lecturer': 'Prof. Kamau',
            'schedule': 'Tue/Thu 14:00-16:00'
        },
        {
            'code': 'EEE303',
            'name': 'Control Systems',
            'lecturer': 'Dr. Wanjiru',
            'schedule': 'Mon/Fri 08:00-10:00'
        }
    ]
    
    print("\nAdding sample courses:")
    for course in sample_courses:
        try:
            ops.add_course(
                course_code=course['code'],
                course_name=course['name'],
                instructor=course['lecturer']
            )
            print(f"✅ Added: {course['code']} - {course['name']}")
        except Exception as e:
            print(f"⏭️  {course['code']} - {str(e)}")
    
    # Allow adding custom courses
    print("\nWould you like to add more courses?")
    while True:
        response = input("Add another course? (y/N): ")
        if response.lower() != 'y':
            break
        
        code = input("Course Code: ").strip()
        name = input("Course Name: ").strip()
        lecturer = input("Lecturer: ").strip()
        
        try:
            ops.add_course(code, name, instructor=lecturer)
            print(f"✅ Added course: {code}")
        except Exception as e:
            print(f"❌ Error: {e}")


def enroll_students():
    """Enroll students in courses"""
    print("\n" + "="*60)
    print("ENROLLING STUDENTS IN COURSES")
    print("="*60)
    
    ops = DatabaseOperations()
    
    # Get all students and courses
    students = ops.get_all_students()
    
    conn = sqlite3.connect('data/database/attendance.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, course_code, course_name FROM courses")
    courses = cursor.fetchall()
    conn.close()
    
    if not courses:
        print("No courses found. Please add courses first.")
        return
    
    if not students:
        print("No students found. Please add students first.")
        return
    
    print(f"\nAvailable courses:")
    for idx, (course_id, code, name) in enumerate(courses, 1):
        print(f"  {idx}. {code} - {name}")
    
    print(f"\nFound {len(students)} students to enroll")
    
    # Option to enroll all students in all courses
    response = input("\nEnroll ALL students in ALL courses? (y/N): ")
    if response.lower() == 'y':
        enrolled_count = 0
        for student in students:
            student_id = student.get('id', student.get('student_id'))
            for course_id, code, name in courses:
                try:
                    ops.enroll_student(student_id, course_id)
                    enrolled_count += 1
                except:
                    pass  # Already enrolled
        print(f"✅ Enrolled students in courses ({enrolled_count} enrollments)")
        return
    
    # Manual enrollment
    print("\nManual enrollment (enter 'done' when finished):")
    while True:
        print("\nStudents:")
        for idx, student in enumerate(students, 1):
            print(f"  {idx}. {student['registration_number']} - {student['full_name']}")
        
        student_choice = input("\nSelect student number (or 'done'): ").strip()
        if student_choice.lower() == 'done':
            break
        
        try:
            student_idx = int(student_choice) - 1
            student = students[student_idx]
            student_id = student.get('id', student.get('student_id'))
        except:
            print("Invalid choice")
            continue
        
        print(f"\nCourses:")
        for idx, (course_id, code, name) in enumerate(courses, 1):
            print(f"  {idx}. {code} - {name}")
        
        course_choice = input("Select course number: ").strip()
        try:
            course_idx = int(course_choice) - 1
            course_id, code, name = courses[course_idx]
            
            ops.enroll_student(student_id, course_id)
            print(f"✅ Enrolled {student['registration_number']} in {code}")
        except Exception as e:
            print(f"❌ Error: {e}")


def main():
    """Main setup function"""
    print("\n" + "="*60)
    print("SMART CLASS ATTENDANCE SYSTEM - INITIALIZATION")
    print("="*60)
    print("\nThis script will:")
    print("  1. Initialize the database with schema")
    print("  2. Add students based on face directories")
    print("  3. Add sample courses")
    print("  4. Enroll students in courses")
    print("\n" + "="*60)
    
    # Check if face directories exist
    faces_dir = Path('data/faces')
    if not faces_dir.exists():
        print("❌ Error: data/faces directory not found!")
        return
    
    # Step 1: Initialize database
    if not initialize_database():
        response = input("\nContinue with existing database? (y/N): ")
        if response.lower() != 'y':
            return
    
    # Step 2: Add students
    add_students_from_faces()
    
    # Step 3: Add courses
    add_sample_courses()
    
    # Step 4: Enroll students
    enroll_students()
    
    print("\n" + "="*60)
    print("✅ DATABASE SETUP COMPLETE!")
    print("="*60)
    print("\nNext steps:")
    print("  1. Train the face recognition model:")
    print("     python train_model.py")
    print("\n  2. Or run the application:")
    print("     python app.py")
    print("\n" + "="*60)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup cancelled by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
