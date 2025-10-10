"""
Main Tkinter Application
"""

import tkinter as tk
from tkinter import ttk, messagebox
import logging

from config.settings import Settings

logger = logging.getLogger(__name__)


class AttendanceApp:
    """Main application window"""
    
    def __init__(self):
        """Initialize application"""
        self.root = tk.Tk()
        self.root.title(Settings.WINDOW_TITLE)
        self.root.geometry(Settings.WINDOW_SIZE)
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup user interface"""
        # Title
        title_label = tk.Label(
            self.root,
            text=Settings.APP_NAME,
            font=("Arial", 20, "bold"),
            bg=Settings.THEME_COLOR,
            fg="white",
            pady=20
        )
        title_label.pack(fill=tk.X)
        
        # Main menu
        menu_frame = tk.Frame(self.root, bg="white", pady=20)
        menu_frame.pack(fill=tk.BOTH, expand=True)
        
        buttons = [
            ("Register Student", self._open_registration),
            ("Take Attendance", self._open_attendance),
            ("Train Model", self._train_model),
            ("View Records", self._view_records),
            ("Export Data", self._export_data),
            ("Settings", self._open_settings),
        ]
        
        for text, command in buttons:
            btn = tk.Button(
                menu_frame,
                text=text,
                command=command,
                font=("Arial", 14),
                width=20,
                height=2,
                bg=Settings.ACCENT_COLOR,
                fg="white"
            )
            btn.pack(pady=10)
    
    def _open_registration(self):
        """Open student registration window"""
        messagebox.showinfo("Info", "Student registration coming soon!")
    
    def _open_attendance(self):
        """Open attendance tracking window"""
        messagebox.showinfo("Info", "Attendance tracking coming soon!")
    
    def _train_model(self):
        """Train recognition model"""
        messagebox.showinfo("Info", "Model training coming soon!")
    
    def _view_records(self):
        """View attendance records"""
        messagebox.showinfo("Info", "View records coming soon!")
    
    def _export_data(self):
        """Export attendance data"""
        messagebox.showinfo("Info", "Export data coming soon!")
    
    def _open_settings(self):
        """Open settings window"""
        messagebox.showinfo("Info", "Settings coming soon!")
    
    def run(self):
        """Run the application"""
        logger.info("Starting GUI application")
        self.root.mainloop()


if __name__ == '__main__':
    app = AttendanceApp()
    app.run()
