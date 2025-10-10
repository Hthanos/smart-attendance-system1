"""
View Attendance Records Window
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date, timedelta
import logging

from config.settings import Settings
from src.services.attendance_service import AttendanceService
from src.services.export_service import ExportService
from src.database.operations import DatabaseOperations

logger = logging.getLogger(__name__)


class ViewRecordsWindow(tk.Toplevel):
    """View and search attendance records"""
    
    def __init__(self, parent):
        """Initialize records window"""
        super().__init__(parent)
        
        self.title("View Attendance Records")
        self.geometry("1200x700")
        
        self.attendance_service = AttendanceService()
        self.export_service = ExportService()
        self.db_ops = DatabaseOperations()
        
        self._setup_ui()
        self._load_filters()
        self._search_records()
    
    def _setup_ui(self):
        """Setup user interface"""
        # Title
        title_label = tk.Label(
            self,
            text="Attendance Records",
            font=("Arial", 16, "bold"),
            bg=Settings.THEME_COLOR,
            fg="white",
            pady=15
        )
        title_label.pack(fill=tk.X)
        
        # Main container
        main_frame = tk.Frame(self, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Search panel
        search_frame = tk.LabelFrame(
            main_frame,
            text="Search Filters",
            font=("Arial", 11, "bold"),
            padx=15,
            pady=15
        )
        search_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Row 1: Student, Course, Date Range
        filter_row1 = tk.Frame(search_frame)
        filter_row1.pack(fill=tk.X, pady=5)
        
        # Student filter
        tk.Label(filter_row1, text="Student:", font=("Arial", 10)).grid(
            row=0, column=0, sticky="w", padx=(0, 5)
        )
        self.student_combo = ttk.Combobox(
            filter_row1,
            font=("Arial", 10),
            width=25,
            state="readonly"
        )
        self.student_combo.grid(row=0, column=1, padx=(0, 20))
        
        # Course filter
        tk.Label(filter_row1, text="Course:", font=("Arial", 10)).grid(
            row=0, column=2, sticky="w", padx=(0, 5)
        )
        self.course_combo = ttk.Combobox(
            filter_row1,
            font=("Arial", 10),
            width=25,
            state="readonly"
        )
        self.course_combo.grid(row=0, column=3, padx=(0, 20))
        
        # Date range
        tk.Label(filter_row1, text="From:", font=("Arial", 10)).grid(
            row=0, column=4, sticky="w", padx=(0, 5)
        )
        self.from_date_entry = tk.Entry(filter_row1, font=("Arial", 10), width=12)
        self.from_date_entry.grid(row=0, column=5, padx=(0, 10))
        
        # Default to last 7 days
        default_from = (date.today() - timedelta(days=7)).strftime("%Y-%m-%d")
        self.from_date_entry.insert(0, default_from)
        
        tk.Label(filter_row1, text="To:", font=("Arial", 10)).grid(
            row=0, column=6, sticky="w", padx=(0, 5)
        )
        self.to_date_entry = tk.Entry(filter_row1, font=("Arial", 10), width=12)
        self.to_date_entry.grid(row=0, column=7)
        
        # Default to today
        self.to_date_entry.insert(0, date.today().strftime("%Y-%m-%d"))
        
        # Row 2: Status filter and buttons
        filter_row2 = tk.Frame(search_frame)
        filter_row2.pack(fill=tk.X, pady=10)
        
        tk.Label(filter_row2, text="Status:", font=("Arial", 10)).grid(
            row=0, column=0, sticky="w", padx=(0, 5)
        )
        self.status_var = tk.StringVar(value="All")
        statuses = ["All", "Present", "Absent", "Late"]
        for i, status in enumerate(statuses):
            rb = tk.Radiobutton(
                filter_row2,
                text=status,
                variable=self.status_var,
                value=status,
                font=("Arial", 10)
            )
            rb.grid(row=0, column=i+1, padx=5)
        
        # Search buttons
        button_frame = tk.Frame(filter_row2)
        button_frame.grid(row=0, column=10, sticky="e", padx=(20, 0))
        
        search_btn = tk.Button(
            button_frame,
            text="Search",
            command=self._search_records,
            bg=Settings.THEME_COLOR,
            fg="white",
            font=("Arial", 10, "bold"),
            padx=15,
            pady=5
        )
        search_btn.grid(row=0, column=0, padx=5)
        
        clear_btn = tk.Button(
            button_frame,
            text="Clear Filters",
            command=self._clear_filters,
            font=("Arial", 10),
            padx=15,
            pady=5
        )
        clear_btn.grid(row=0, column=1, padx=5)
        
        filter_row2.grid_columnconfigure(9, weight=1)
        
        # Results table
        results_frame = tk.LabelFrame(
            main_frame,
            text="Results",
            font=("Arial", 11, "bold"),
            padx=10,
            pady=10
        )
        results_frame.pack(fill=tk.BOTH, expand=True)
        
        # Table
        columns = ("Date", "Time", "Student", "Reg No", "Course", "Status", "Confidence")
        self.results_tree = ttk.Treeview(
            results_frame,
            columns=columns,
            show="headings",
            height=18
        )
        
        # Column configuration
        widths = [100, 80, 150, 100, 120, 80, 90]
        for col, width in zip(columns, widths):
            self.results_tree.heading(col, text=col)
            self.results_tree.column(col, width=width)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(
            results_frame,
            orient=tk.VERTICAL,
            command=self.results_tree.yview
        )
        h_scrollbar = ttk.Scrollbar(
            results_frame,
            orient=tk.HORIZONTAL,
            command=self.results_tree.xview
        )
        self.results_tree.configure(
            yscroll=v_scrollbar.set,
            xscroll=h_scrollbar.set
        )
        
        self.results_tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        results_frame.grid_rowconfigure(0, weight=1)
        results_frame.grid_columnconfigure(0, weight=1)
        
        # Bottom bar - Statistics and Export
        bottom_frame = tk.Frame(main_frame)
        bottom_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.stats_label = tk.Label(
            bottom_frame,
            text="Total records: 0",
            font=("Arial", 10),
            fg=Settings.THEME_COLOR
        )
        self.stats_label.pack(side=tk.LEFT)
        
        # Export buttons
        export_frame = tk.Frame(bottom_frame)
        export_frame.pack(side=tk.RIGHT)
        
        export_excel_btn = tk.Button(
            export_frame,
            text="Export to Excel",
            command=self._export_excel,
            bg=Settings.SUCCESS_COLOR,
            fg="white",
            font=("Arial", 10),
            padx=15,
            pady=5
        )
        export_excel_btn.grid(row=0, column=0, padx=5)
        
        export_csv_btn = tk.Button(
            export_frame,
            text="Export to CSV",
            command=self._export_csv,
            font=("Arial", 10),
            padx=15,
            pady=5
        )
        export_csv_btn.grid(row=0, column=1, padx=5)
    
    def _load_filters(self):
        """Load filter options"""
        try:
            # Load students
            students = self.db_ops.get_all_students()
            student_options = ["All Students"] + [
                f"{s['registration_number']} - {s['full_name']}"
                for s in students
            ]
            self.student_combo['values'] = student_options
            self.student_combo.current(0)
            
            # Load courses
            courses = self.db_ops.get_all_courses()
            course_options = ["All Courses"] + [
                f"{c['course_code']} - {c['course_name']}"
                for c in courses
            ]
            self.course_combo['values'] = course_options
            self.course_combo.current(0)
            
        except Exception as e:
            logger.error(f"Error loading filters: {str(e)}")
    
    def _search_records(self):
        """Search attendance records"""
        try:
            # Get filter values
            student_idx = self.student_combo.current()
            student_id = None
            if student_idx > 0:
                students = self.db_ops.get_all_students()
                student_id = students[student_idx - 1]['id']
            
            course_idx = self.course_combo.current()
            course_id = None
            if course_idx > 0:
                courses = self.db_ops.get_all_courses()
                course_id = courses[course_idx - 1]['id']
            
            from_date = self.from_date_entry.get()
            to_date = self.to_date_entry.get()
            status = self.status_var.get()
            
            # Search
            records = self.attendance_service.search_records(
                student_id=student_id,
                course_id=course_id,
                from_date=from_date if from_date else None,
                to_date=to_date if to_date else None,
                status=status if status != "All" else None
            )
            
            # Clear existing
            self.results_tree.delete(*self.results_tree.get_children())
            
            # Populate results
            for record in records:
                timestamp = datetime.fromisoformat(record['timestamp'])
                self.results_tree.insert(
                    "",
                    tk.END,
                    values=(
                        timestamp.strftime("%Y-%m-%d"),
                        timestamp.strftime("%H:%M:%S"),
                        record['student_name'],
                        record['registration_number'],
                        f"{record['course_code']} - {record['course_name']}",
                        record['status'],
                        f"{record['confidence_score']:.1f}" if record.get('confidence_score') else "N/A"
                    )
                )
            
            # Update stats
            self.stats_label.config(text=f"Total records: {len(records)}")
            
            logger.info(f"Search returned {len(records)} records")
            
        except Exception as e:
            logger.error(f"Search error: {str(e)}")
            messagebox.showerror("Error", f"Search failed: {str(e)}")
    
    def _clear_filters(self):
        """Clear all filters"""
        self.student_combo.current(0)
        self.course_combo.current(0)
        
        default_from = (date.today() - timedelta(days=7)).strftime("%Y-%m-%d")
        self.from_date_entry.delete(0, tk.END)
        self.from_date_entry.insert(0, default_from)
        
        self.to_date_entry.delete(0, tk.END)
        self.to_date_entry.insert(0, date.today().strftime("%Y-%m-%d"))
        
        self.status_var.set("All")
        
        self._search_records()
    
    def _export_excel(self):
        """Export results to Excel"""
        try:
            # Get current results
            items = self.results_tree.get_children()
            if not items:
                messagebox.showwarning("Warning", "No records to export")
                return
            
            data = []
            for item in items:
                values = self.results_tree.item(item)['values']
                data.append({
                    'Date': values[0],
                    'Time': values[1],
                    'Student': values[2],
                    'Registration Number': values[3],
                    'Course': values[4],
                    'Status': values[5],
                    'Confidence': values[6]
                })
            
            # Export
            filename = self.export_service.export_to_excel(
                data,
                filename_prefix="attendance_records"
            )
            
            messagebox.showinfo(
                "Success",
                f"Exported to:\n{filename}"
            )
            
        except Exception as e:
            logger.error(f"Export error: {str(e)}")
            messagebox.showerror("Error", f"Export failed: {str(e)}")
    
    def _export_csv(self):
        """Export results to CSV"""
        try:
            items = self.results_tree.get_children()
            if not items:
                messagebox.showwarning("Warning", "No records to export")
                return
            
            data = []
            for item in items:
                values = self.results_tree.item(item)['values']
                data.append({
                    'Date': values[0],
                    'Time': values[1],
                    'Student': values[2],
                    'Registration Number': values[3],
                    'Course': values[4],
                    'Status': values[5],
                    'Confidence': values[6]
                })
            
            filename = self.export_service.export_to_csv(
                data,
                filename_prefix="attendance_records"
            )
            
            messagebox.showinfo(
                "Success",
                f"Exported to:\n{filename}"
            )
            
        except Exception as e:
            logger.error(f"Export error: {str(e)}")
            messagebox.showerror("Error", f"Export failed: {str(e)}")
