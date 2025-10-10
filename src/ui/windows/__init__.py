"""
UI windows package
"""

from .dashboard import DashboardWindow
from .student_registration import StudentRegistrationWindow
from .take_attendance import TakeAttendanceWindow
from .view_records import ViewRecordsWindow
from .settings import SettingsWindow

__all__ = [
    'DashboardWindow',
    'StudentRegistrationWindow',
    'TakeAttendanceWindow',
    'ViewRecordsWindow',
    'SettingsWindow'
]
