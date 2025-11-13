#!/usr/bin/env python3
"""
Populate Sample Data
Generates sample students, courses, and attendance for testing
"""

import sys
import random
from pathlib import Path
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database.operations import DatabaseOperations
from config.settings import Settings


# Sample data
FIRST_NAMES = [
    "John", "Jane", "Michael", "Sarah", "David", "Emily", "James", "Emma",
    "Robert", "Olivia", "William", "Sophia", "Richard", "Isabella", "Joseph",
    "Ava", "Thomas", "Mia", "Charles", "Charlotte", "Daniel", "Amelia",
    "Matthew", "Harper", "Anthony", "Evelyn", "Mark", "Abigail", "Paul", "Ella"
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
    "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Wilson",
    "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee",
    "Thompson", "White", "Harris", "Clark", "Lewis", "Robinson", "Walker",
    "Hall", "Allen", "Young"
]

COURSES = [
    ("CSC 101", "Introduction to Programming", "Dr. John Smith"),
    ("CSC 201", "Data Structures and Algorithms", "Dr. Jane Doe"),
    ("CSC 301", "Database Systems", "Prof. Michael Johnson"),
    ("CSC 302", "Computer Networks", "Dr. Sarah Williams"),
    ("CSC 401", "Artificial Intelligence", "Prof. David Brown"),
    ("MAT 101", "Calculus I", "Dr. Emily Jones"),
    ("MAT 201", "Linear Algebra", "Prof. James Garcia"),
    ("PHY 101", "Physics I", "Dr. Emma Miller"),
    ("ENG 101", "Technical Writing", "Prof. Robert Davis"),
    ("BUS 201", "Business Management", "Dr. Olivia Rodriguez")
]

LOCATIONS = [
    "Room A101", "Room A102", "Lab B201", "Lab B202", "Lecture Hall C",
    "Seminar Room D", "Computer Lab 1", "Computer Lab 2", "Auditorium",
    "Conference Room"
]


def generate_registration_number(index, year=2022):
    """Generate realistic registration number - Moi University format"""
    # Format: E028-01-XXXX/YYYY (e.g., E028-01-1532/2022)
    return f"E028-01-{1000 + index:04d}/{year}"


def create_sample_students(ops, count=50):
    """Create sample students"""
    print(f"\n📚 Creating {count} sample students...")
    
    students = []
    for i in range(count):
        first_name = random.choice(FIRST_NAMES)
        last_name = random.choice(LAST_NAMES)
        full_name = f"{first_name} {last_name}"
        
        reg_number = generate_registration_number(i + 1)
        email = f"{first_name.lower()}.{last_name.lower()}@student.example.com"
        phone = f"+254{random.randint(700000000, 799999999)}"
        gender = random.choice(["Male", "Female"])
        year = random.randint(1, 4)
        
        try:
            student_id = ops.create_student(
                registration_number=reg_number,
                full_name=full_name,
                email=email,
                phone_number=phone,
                gender=gender,
                year_of_study=year
            )
            
            students.append(student_id)
            print(f"  ✓ Created: {reg_number} - {full_name}")
            
        except Exception as e:
            print(f"  ✗ Failed to create {reg_number}: {str(e)}")
    
    print(f"✅ Created {len(students)} students")
    return students


def create_sample_courses(ops):
    """Create sample courses"""
    print(f"\n📖 Creating {len(COURSES)} sample courses...")
    
    course_ids = []
    for course_code, course_name, lecturer in COURSES:
        try:
            course_id = ops.create_course(
                course_code=course_code,
                course_name=course_name,
                lecturer_name=lecturer,
                credits=random.randint(2, 4)
            )
            
            course_ids.append(course_id)
            print(f"  ✓ Created: {course_code} - {course_name}")
            
        except Exception as e:
            print(f"  ✗ Failed to create {course_code}: {str(e)}")
    
    print(f"✅ Created {len(course_ids)} courses")
    return course_ids


def enroll_students(ops, student_ids, course_ids):
    """Enroll students in random courses"""
    print(f"\n🎓 Enrolling students in courses...")
    
    enrollments = 0
    for student_id in student_ids:
        # Each student enrolled in 3-6 random courses
        num_courses = random.randint(3, 6)
        student_courses = random.sample(course_ids, num_courses)
        
        for course_id in student_courses:
            try:
                ops.enroll_student(student_id, course_id)
                enrollments += 1
            except Exception as e:
                pass  # Ignore duplicates
    
    print(f"✅ Created {enrollments} enrollments")


def create_class_sessions(ops, course_ids, days=30):
    """Create class sessions for the past N days"""
    print(f"\n📅 Creating class sessions for past {days} days...")
    
    session_ids = []
    today = datetime.now().date()
    
    for day_offset in range(days):
        session_date = today - timedelta(days=day_offset)
        
        # Skip weekends
        if session_date.weekday() >= 5:
            continue
        
        # 2-4 sessions per day
        num_sessions = random.randint(2, 4)
        daily_courses = random.sample(course_ids, num_sessions)
        
        for course_id in daily_courses:
            hour = random.randint(8, 16)
            minute = random.choice([0, 30])
            start_time = f"{hour:02d}:{minute:02d}:00"
            end_time = f"{hour+1:02d}:{minute:02d}:00"
            location = random.choice(LOCATIONS)
            
            try:
                session_id = ops.create_session(
                    course_id=course_id,
                    session_date=session_date.isoformat(),
                    start_time=start_time,
                    end_time=end_time,
                    location=location
                )
                
                session_ids.append((session_id, course_id, session_date))
                
            except Exception as e:
                print(f"  ✗ Failed to create session: {str(e)}")
    
    print(f"✅ Created {len(session_ids)} sessions")
    return session_ids


def mark_sample_attendance(ops, session_ids):
    """Mark attendance for sessions with realistic patterns"""
    print(f"\n✅ Marking attendance for {len(session_ids)} sessions...")
    
    total_records = 0
    
    for session_id, course_id, session_date in session_ids:
        # Get enrolled students for this course
        try:
            enrollments = ops.get_course_enrollments(course_id)
            student_ids = [e['student_id'] for e in enrollments]
            
            # Attendance rate: 70-95% randomly
            attendance_rate = random.uniform(0.70, 0.95)
            num_present = int(len(student_ids) * attendance_rate)
            
            # Randomly select students to mark present
            present_students = random.sample(student_ids, num_present)
            
            for student_id in present_students:
                # Random confidence score (60-95 for good recognition)
                confidence = random.uniform(60, 95)
                
                # Determine status (most present, few late)
                status = "Present" if random.random() > 0.1 else "Late"
                
                # Random time during session
                hour = random.randint(8, 16)
                minute = random.randint(0, 59)
                timestamp = f"{session_date} {hour:02d}:{minute:02d}:{random.randint(0, 59):02d}"
                
                try:
                    ops.mark_attendance(
                        student_id=student_id,
                        session_id=session_id,
                        status=status,
                        confidence_score=confidence,
                        timestamp=timestamp
                    )
                    total_records += 1
                    
                except Exception as e:
                    pass  # Ignore duplicates
        
        except Exception as e:
            print(f"  ✗ Error processing session {session_id}: {str(e)}")
    
    print(f"✅ Created {total_records} attendance records")


def populate_all(student_count=50, days=30):
    """Populate all sample data"""
    print("=" * 60)
    print("Sample Data Population Script")
    print("=" * 60)
    
    # Initialize database operations
    ops = DatabaseOperations()
    
    # Create data
    student_ids = create_sample_students(ops, count=student_count)
    course_ids = create_sample_courses(ops)
    enroll_students(ops, student_ids, course_ids)
    session_ids = create_class_sessions(ops, course_ids, days=days)
    mark_sample_attendance(ops, session_ids)
    
    # Summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    
    stats = ops.get_database_statistics()
    print(f"✅ Total Students: {stats.get('total_students', 0)}")
    print(f"✅ Total Courses: {stats.get('total_courses', 0)}")
    print(f"✅ Total Sessions: {stats.get('total_sessions', 0)}")
    print(f"✅ Total Attendance Records: {stats.get('total_attendance_records', 0)}")
    
    print("\n🎉 Sample data population complete!")
    print("\nYou can now:")
    print("  1. Run the application: python3 app.py")
    print("  2. View students and attendance records")
    print("  3. Test the system with sample data")
    print("\nNote: This is sample data for testing purposes only.")


def clear_all_data(ops, confirm=True):
    """Clear all data from database (WARNING: Destructive)"""
    if confirm:
        print("\n⚠️  WARNING: This will DELETE ALL DATA from the database!")
        response = input("Are you sure? Type 'DELETE' to confirm: ")
        if response != 'DELETE':
            print("Operation cancelled")
            return False
    
    print("\n🗑️  Clearing all data...")
    
    with ops.db.get_cursor() as cursor:
        cursor.execute("DELETE FROM attendance")
        cursor.execute("DELETE FROM enrollments")
        cursor.execute("DELETE FROM class_sessions")
        cursor.execute("DELETE FROM courses")
        cursor.execute("DELETE FROM students")
    
    print("✅ All data cleared")
    return True


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Populate database with sample data for testing"
    )
    
    parser.add_argument(
        '--students',
        type=int,
        default=50,
        help='Number of sample students to create (default: 50)'
    )
    
    parser.add_argument(
        '--days',
        type=int,
        default=30,
        help='Number of days of attendance history (default: 30)'
    )
    
    parser.add_argument(
        '--clear',
        action='store_true',
        help='Clear all existing data before populating (DESTRUCTIVE!)'
    )
    
    parser.add_argument(
        '--yes',
        action='store_true',
        help='Skip confirmation prompts'
    )
    
    args = parser.parse_args()
    
    ops = DatabaseOperations()
    
    # Clear existing data if requested
    if args.clear:
        if not clear_all_data(ops, confirm=not args.yes):
            return
    
    # Populate sample data
    populate_all(student_count=args.students, days=args.days)


if __name__ == "__main__":
    main()
