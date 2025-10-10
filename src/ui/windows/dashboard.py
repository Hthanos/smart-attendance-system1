"""
Dashboard Window - Main application dashboard
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import logging

from config.settings import Settings
from src.database.operations import DatabaseOperations

logger = logging.getLogger(__name__)


class DashboardWindow(tk.Frame):
    """Main dashboard window"""
    
    def __init__(self, parent):
        """Initialize dashboard"""
        super().__init__(parent)
        self.db_ops = DatabaseOperations()
        
        self._setup_ui()
        self._load_dashboard_data()
    
    def _setup_ui(self):
        """Setup user interface"""
        # Title
        title_frame = tk.Frame(self, bg=Settings.THEME_COLOR)
        title_frame.pack(fill=tk.X, pady=(0, 20))
        
        title_label = tk.Label(
            title_frame,
            text="Dashboard",
            font=("Arial", 18, "bold"),
            bg=Settings.THEME_COLOR,
            fg="white",
            pady=15
        )
        title_label.pack()
        
        # Statistics Cards
        stats_frame = tk.Frame(self)
        stats_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.stats_widgets = {}
        stats = [
            ("total_students", "Total Students", Settings.ACCENT_COLOR),
            ("total_courses", "Active Courses", Settings.SUCCESS_COLOR),
            ("todays_sessions", "Today's Sessions", "#e67e22"),
            ("attendance_records", "Attendance Records", "#9b59b6")
        ]
        
        for i, (key, label, color) in enumerate(stats):
            card = self._create_stat_card(stats_frame, label, "0", color)
            card.grid(row=0, column=i, padx=10, pady=10, sticky="ew")
            stats_frame.grid_columnconfigure(i, weight=1)
            self.stats_widgets[key] = card
        
        # Today's Sessions
        sessions_frame = tk.LabelFrame(
            self,
            text="Today's Sessions",
            font=("Arial", 12, "bold"),
            padx=10,
            pady=10
        )
        sessions_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Sessions table
        columns = ("Course", "Time", "Location", "Status")
        self.sessions_tree = ttk.Treeview(
            sessions_frame,
            columns=columns,
            show="headings",
            height=8
        )
        
        for col in columns:
            self.sessions_tree.heading(col, text=col)
            self.sessions_tree.column(col, width=150)
        
        scrollbar = ttk.Scrollbar(
            sessions_frame,
            orient=tk.VERTICAL,
            command=self.sessions_tree.yview
        )
        self.sessions_tree.configure(yscroll=scrollbar.set)
        
        self.sessions_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Refresh button
        refresh_btn = tk.Button(
            self,
            text="Refresh Dashboard",
            command=self._load_dashboard_data,
            font=("Arial", 10),
            bg=Settings.ACCENT_COLOR,
            fg="white",
            padx=20,
            pady=10
        )
        refresh_btn.pack(pady=10)
    
    def _create_stat_card(self, parent, title, value, color):
        """Create a statistics card"""
        card_frame = tk.Frame(parent, bg=color, relief=tk.RAISED, bd=2)
        
        value_label = tk.Label(
            card_frame,
            text=value,
            font=("Arial", 24, "bold"),
            bg=color,
            fg="white"
        )
        value_label.pack(pady=(10, 0))
        
        title_label = tk.Label(
            card_frame,
            text=title,
            font=("Arial", 10),
            bg=color,
            fg="white"
        )
        title_label.pack(pady=(0, 10))
        
        # Store reference to value label for updates
        card_frame.value_label = value_label
        
        return card_frame
    
    def _load_dashboard_data(self):
        """Load dashboard data from database"""
        try:
            # Get statistics
            students = self.db_ops.get_all_students()
            courses = self.db_ops.get_all_courses()
            sessions = self.db_ops.get_todays_sessions()
            
            # Update statistics cards
            self.stats_widgets['total_students'].value_label.config(text=str(len(students)))
            self.stats_widgets['total_courses'].value_label.config(text=str(len(courses)))
            self.stats_widgets['todays_sessions'].value_label.config(text=str(len(sessions)))
            
            # Get total attendance records
            from src.database.db_manager import db_manager
            stats = db_manager.get_database_stats()
            self.stats_widgets['attendance_records'].value_label.config(
                text=str(stats.get('total_attendance_records', 0))
            )
            
            # Update sessions table
            self.sessions_tree.delete(*self.sessions_tree.get_children())
            
            for session in sessions:
                course_name = f"{session.get('course_code', 'N/A')} - {session.get('course_name', 'N/A')}"
                time = session.get('start_time', 'N/A')
                location = session.get('location', 'N/A')
                status = "Active" if session.get('is_completed', 0) == 0 else "Completed"
                
                self.sessions_tree.insert(
                    "",
                    tk.END,
                    values=(course_name, time, location, status)
                )
            
            logger.info("Dashboard data loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading dashboard data: {str(e)}")
            messagebox.showerror("Error", f"Failed to load dashboard: {str(e)}")
