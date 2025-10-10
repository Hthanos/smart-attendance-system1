#!/usr/bin/env python3
"""
Smart Class Attendance System - Setup Verification Script
Run this to verify your installation is correct
"""

import sys
import os
from pathlib import Path

# Colors for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_success(msg):
    print(f"{GREEN}✓{RESET} {msg}")

def print_error(msg):
    print(f"{RED}✗{RESET} {msg}")

def print_warning(msg):
    print(f"{YELLOW}⚠{RESET} {msg}")

def print_info(msg):
    print(f"{BLUE}ℹ{RESET} {msg}")

def check_python_version():
    """Check Python version"""
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print_success(f"Python version: {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print_error(f"Python version: {version.major}.{version.minor}.{version.micro} (need 3.8+)")
        return False

def check_dependencies():
    """Check required packages"""
    packages = [
        ('cv2', 'opencv-python'),
        ('numpy', 'numpy'),
        ('PIL', 'Pillow'),
        ('pandas', 'pandas'),
        ('openpyxl', 'openpyxl'),
    ]
    
    all_good = True
    for module_name, package_name in packages:
        try:
            __import__(module_name)
            print_success(f"Package installed: {package_name}")
        except ImportError:
            print_error(f"Package missing: {package_name}")
            all_good = False
    
    return all_good

def check_file_structure():
    """Check project file structure"""
    required_files = [
        'app.py',
        'requirements.txt',
        'README.md',
        'config/settings.py',
        'config/haarcascade_frontalface_default.xml',
        'src/core/camera.py',
        'src/core/face_detector.py',
        'src/core/face_recognizer.py',
        'src/database/db_manager.py',
        'src/database/schema.sql',
        'src/services/student_service.py',
        'src/services/training_service.py',
    ]
    
    all_good = True
    for filepath in required_files:
        if os.path.exists(filepath):
            print_success(f"File exists: {filepath}")
        else:
            print_error(f"File missing: {filepath}")
            all_good = False
    
    return all_good

def check_directories():
    """Check required directories"""
    required_dirs = [
        'config',
        'src/core',
        'src/database',
        'src/services',
        'src/ui',
        'src/utils',
        'tests',
        'docs',
    ]
    
    all_good = True
    for dirpath in required_dirs:
        if os.path.isdir(dirpath):
            print_success(f"Directory exists: {dirpath}")
        else:
            print_error(f"Directory missing: {dirpath}")
            all_good = False
    
    return all_good

def check_imports():
    """Check if core modules can be imported"""
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    modules = [
        'config.settings',
        'src.core.camera',
        'src.core.face_detector',
        'src.database.db_manager',
    ]
    
    all_good = True
    for module in modules:
        try:
            __import__(module)
            print_success(f"Module imports: {module}")
        except Exception as e:
            print_error(f"Import failed: {module} - {str(e)}")
            all_good = False
    
    return all_good

def main():
    """Run all verification checks"""
    print("\n" + "="*60)
    print("  SMART CLASS ATTENDANCE SYSTEM - SETUP VERIFICATION")
    print("="*60 + "\n")
    
    checks = [
        ("Python Version", check_python_version),
        ("File Structure", check_file_structure),
        ("Directories", check_directories),
        ("Dependencies", check_dependencies),
        ("Module Imports", check_imports),
    ]
    
    results = []
    
    for name, check_func in checks:
        print(f"\n{BLUE}Checking {name}...{RESET}")
        result = check_func()
        results.append((name, result))
    
    # Summary
    print("\n" + "="*60)
    print("  VERIFICATION SUMMARY")
    print("="*60 + "\n")
    
    all_passed = True
    for name, result in results:
        if result:
            print_success(f"{name}: PASSED")
        else:
            print_error(f"{name}: FAILED")
            all_passed = False
    
    print("\n" + "="*60)
    
    if all_passed:
        print(f"\n{GREEN}✓ All checks passed! Your setup is complete.{RESET}\n")
        print_info("Next steps:")
        print("  1. Configure .env file")
        print("  2. Initialize database: python -m src.database.db_manager")
        print("  3. Run application: python app.py")
        print()
        return 0
    else:
        print(f"\n{RED}✗ Some checks failed. Please fix the issues above.{RESET}\n")
        print_info("To install missing dependencies:")
        print("  pip install -r requirements.txt")
        print()
        return 1

if __name__ == '__main__':
    sys.exit(main())
