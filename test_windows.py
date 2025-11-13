#!/usr/bin/env python3
"""
Test which UI windows work
"""

import sys
import tkinter as tk
from tkinter import messagebox

def test_registration():
    try:
        from src.ui.windows.student_registration import StudentRegistrationWindow
        root = tk.Tk()
        root.withdraw()
        window = StudentRegistrationWindow(root)
        print("✅ StudentRegistrationWindow works!")
        root.destroy()
        return True
    except Exception as e:
        print(f"❌ StudentRegistrationWindow failed: {e}")
        return False

def test_attendance():
    try:
        from src.ui.windows.take_attendance_simple import TakeAttendanceWindow
        print("✅ TakeAttendanceWindow import works!")
        return True
    except Exception as e:
        print(f"❌ TakeAttendanceWindow failed: {e}")
        return False

def test_view_records():
    try:
        from src.ui.windows.view_records import ViewRecordsWindow
        print("✅ ViewRecordsWindow import works!")
        return True
    except Exception as e:
        print(f"❌ ViewRecordsWindow failed: {e}")
        return False

def test_settings():
    try:
        from src.ui.windows.settings import SettingsWindow
        print("✅ SettingsWindow import works!")
        return True
    except Exception as e:
        print(f"❌ SettingsWindow failed: {e}")
        return False

if __name__ == '__main__':
    print("\nTesting UI Windows...\n")
    print("="*50)
    
    results = []
    results.append(("Registration", test_registration()))
    results.append(("Attendance", test_attendance()))
    results.append(("View Records", test_view_records()))
    results.append(("Settings", test_settings()))
    
    print("="*50)
    print("\nSummary:")
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {name}: {status}")
