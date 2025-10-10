#!/usr/bin/env python3
"""
Smart Class Attendance System - Main Application
Face Recognition based Attendance Management System

Authors: Sharon Yegon, Gidion Yegon, Gabriel Okal
Supervisor: Dr. Tafara
Institution: Moi University - Department of Electrical and Electronics Engineering
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.utils.logger import setup_logger
from config.settings import Settings

logger = setup_logger(__name__)


def main():
    """Main application entry point"""
    try:
        logger.info("="*60)
        logger.info(f"Starting {Settings.APP_NAME}")
        logger.info("="*60)
        
        # Initialize database
        from src.database.db_manager import db_manager
        
        if not db_manager.check_database_exists():
            logger.info("Initializing database...")
            db_manager.initialize_database()
        else:
            logger.info("Database already initialized")
        
        # Display database stats
        stats = db_manager.get_database_stats()
        logger.info(f"Students: {stats.get('total_students', 0)}")
        logger.info(f"Courses: {stats.get('total_courses', 0)}")
        logger.info(f"Attendance Records: {stats.get('total_attendance_records', 0)}")
        
        # Launch GUI
        logger.info("Launching user interface...")
        
        try:
            from src.ui.app import AttendanceApp
            app = AttendanceApp()
            app.run()
        except ImportError as e:
            logger.warning(f"GUI not available: {str(e)}")
            logger.info("Running in console mode...")
            console_mode()
        
    except KeyboardInterrupt:
        logger.info("\nApplication interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Application error: {str(e)}", exc_info=True)
        sys.exit(1)


def console_mode():
    """Console-based interface (fallback)"""
    from src.database.operations import DatabaseOperations
    
    db_ops = DatabaseOperations()
    
    print("\n" + "="*60)
    print("SMART CLASS ATTENDANCE SYSTEM - Console Mode")
    print("="*60)
    
    while True:
        print("\nOptions:")
        print("1. View all students")
        print("2. View today's sessions")
        print("3. Test camera")
        print("4. Train model")
        print("5. Exit")
        
        choice = input("\nEnter choice: ").strip()
        
        if choice == '1':
            students = db_ops.get_all_students()
            print(f"\nTotal Students: {len(students)}")
            for s in students[:10]:  # Show first 10
                print(f"  {s['registration_number']} - {s['full_name']}")
        
        elif choice == '2':
            sessions = db_ops.get_todays_sessions()
            print(f"\nToday's Sessions: {len(sessions)}")
            for s in sessions:
                print(f"  {s['course_code']} - {s['start_time']}")
        
        elif choice == '3':
            from src.core.camera import test_camera
            test_camera()
        
        elif choice == '4':
            from src.services.training_service import TrainingService
            trainer = TrainingService()
            print("Training model...")
            if trainer.train_model():
                print("✓ Training successful!")
            else:
                print("✗ Training failed")
        
        elif choice == '5':
            print("Goodbye!")
            break
        
        else:
            print("Invalid choice")


if __name__ == '__main__':
    main()
