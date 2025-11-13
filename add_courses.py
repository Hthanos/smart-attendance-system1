#!/usr/bin/env python3
"""
Add courses and enroll students (for when database already has students)
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.database.operations import DatabaseOperations

def add_courses():
    """Add sample courses"""
    ops = DatabaseOperations()
    
    # Sample courses for Electrical and Electronics Engineering
    courses = [
        {
            'code': 'EEE301',
            'name': 'Digital Signal Processing',
            'instructor': 'Dr. Tafara',
        },
        {
            'code': 'EEE302',
            'name': 'Power Electronics',
            'instructor': 'Prof. Kamau',
        },
        {
            'code': 'EEE303',
            'name': 'Control Systems',
            'instructor': 'Dr. Wanjiru',
        },
        {
            'code': 'EEE304',
            'name': 'Microprocessor Systems',
            'instructor': 'Dr. Mutua',
        },
        {
            'code': 'EEE305',
            'name': 'Communication Systems',
            'instructor': 'Prof. Ochieng',
        }
    ]
    
    print("Adding courses...")
    added = 0
    for course in courses:
        try:
            course_id = ops.add_course(
                course_code=course['code'],
                course_name=course['name'],
                instructor=course['instructor']
            )
            if course_id:
                print(f"✅ {course['code']}: {course['name']}")
                added += 1
        except Exception as e:
            print(f"⏭️  {course['code']}: Already exists or error")
    
    print(f"\n✅ Added {added} courses")
    return added > 0

def enroll_all_students():
    """Enroll all students in all courses"""
    ops = DatabaseOperations()
    
    # Get all students and courses
    students = ops.get_all_students()
    courses = ops.get_all_courses()
    
    if not students:
        print("❌ No students found!")
        return
    
    if not courses:
        print("❌ No courses found!")
        return
    
    print(f"\nEnrolling {len(students)} students in {len(courses)} courses...")
    
    enrolled = 0
    for student in students:
        student_id = student.get('id', student.get('student_id'))
        for course in courses:
            course_id = course.get('id', course.get('course_id'))
            try:
                ops.enroll_student(student_id, course_id)
                enrolled += 1
            except:
                pass  # Already enrolled or error
    
    print(f"✅ Completed {enrolled} enrollments")
    
    # Show summary
    print("\n" + "="*60)
    print("ENROLLMENT SUMMARY")
    print("="*60)
    for student in students:
        print(f"\n📚 {student['full_name']} ({student['registration_number']})")
        print(f"   Enrolled in {len(courses)} courses:")
        for course in courses:
            print(f"   - {course['course_code']}: {course['course_name']}")

def main():
    print("\n" + "="*60)
    print("ADD COURSES AND ENROLL STUDENTS")
    print("="*60)
    
    # Add courses
    add_courses()
    
    # Enroll all students
    enroll_all_students()
    
    print("\n" + "="*60)
    print("✅ COMPLETE!")
    print("="*60)
    print("\nNext step: Train the model")
    print("  python train_model.py")
    print("="*60)

if __name__ == '__main__':
    main()
