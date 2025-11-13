"""
Main Tkinter Application
"""

import tkinter as tk
from tkinter import ttk, messagebox
import logging
import threading

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
        try:
            from src.ui.windows.student_registration import StudentRegistrationWindow
            window = StudentRegistrationWindow(self.root)
        except Exception as e:
            logger.error(f"Error opening registration: {e}")
            messagebox.showerror("Error", f"Could not open registration window:\n{str(e)}")
    
    def _open_attendance(self):
        """Open attendance tracking window"""
        try:
            from src.ui.windows.take_attendance_simple import TakeAttendanceWindow
            window = TakeAttendanceWindow(self.root)
        except Exception as e:
            logger.error(f"Error opening attendance: {e}")
            messagebox.showerror("Error", f"Could not open attendance window:\n{str(e)}")
    
    def _train_model(self):
        """Train recognition model"""
        import threading
        
        def train():
            try:
                from src.services.training_service import TrainingService
                
                # Show progress dialog
                progress_window = tk.Toplevel(self.root)
                progress_window.title("Training Model")
                progress_window.geometry("400x150")
                progress_window.transient(self.root)
                
                label = tk.Label(
                    progress_window,
                    text="Training face recognition model...\nThis may take a few minutes.",
                    font=("Arial", 12),
                    pady=20
                )
                label.pack()
                
                progress = ttk.Progressbar(
                    progress_window,
                    mode='indeterminate',
                    length=300
                )
                progress.pack(pady=20)
                progress.start()
                
                # Train in background
                trainer = TrainingService()
                success = trainer.train_model()
                
                progress.stop()
                progress_window.destroy()
                
                if success:
                    messagebox.showinfo(
                        "Success",
                        "Model trained successfully!\n\nYou can now use face recognition for attendance."
                    )
                else:
                    messagebox.showerror(
                        "Error",
                        "Model training failed. Check logs for details."
                    )
            except Exception as e:
                logger.error(f"Training error: {e}")
                try:
                    progress_window.destroy()
                except:
                    pass
                messagebox.showerror("Error", f"Training failed:\n{str(e)}")
        
        # Run training in separate thread
        thread = threading.Thread(target=train, daemon=True)
        thread.start()
    
    def _view_records(self):
        """View attendance records"""
        try:
            from src.ui.windows.view_records import ViewRecordsWindow
            window = ViewRecordsWindow(self.root)
        except Exception as e:
            logger.error(f"Error opening records: {e}")
            messagebox.showerror("Error", f"Could not open records window:\n{str(e)}")
    
    def _export_data(self):
        """Export attendance data"""
        from tkinter import filedialog
        from datetime import datetime
        
        try:
            from src.services.export_service import ExportService
            
            # Ask for export format
            export_window = tk.Toplevel(self.root)
            export_window.title("Export Data")
            export_window.geometry("300x200")
            export_window.transient(self.root)
            
            tk.Label(
                export_window,
                text="Select export format:",
                font=("Arial", 12),
                pady=20
            ).pack()
            
            def export_excel():
                filepath = filedialog.asksaveasfilename(
                    defaultextension=".xlsx",
                    filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
                    initialfile=f"attendance_{datetime.now().strftime('%Y%m%d')}.xlsx"
                )
                if filepath:
                    try:
                        exporter = ExportService()
                        exporter.export_all_attendance(filepath, format='xlsx')
                        messagebox.showinfo("Success", f"Data exported to:\n{filepath}")
                        export_window.destroy()
                    except Exception as e:
                        messagebox.showerror("Error", f"Export failed:\n{str(e)}")
            
            def export_csv():
                filepath = filedialog.asksaveasfilename(
                    defaultextension=".csv",
                    filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                    initialfile=f"attendance_{datetime.now().strftime('%Y%m%d')}.csv"
                )
                if filepath:
                    try:
                        exporter = ExportService()
                        exporter.export_all_attendance(filepath, format='csv')
                        messagebox.showinfo("Success", f"Data exported to:\n{filepath}")
                        export_window.destroy()
                    except Exception as e:
                        messagebox.showerror("Error", f"Export failed:\n{str(e)}")
            
            tk.Button(
                export_window,
                text="Export as Excel (.xlsx)",
                command=export_excel,
                width=20,
                bg=Settings.ACCENT_COLOR,
                fg="white"
            ).pack(pady=10)
            
            tk.Button(
                export_window,
                text="Export as CSV",
                command=export_csv,
                width=20,
                bg=Settings.ACCENT_COLOR,
                fg="white"
            ).pack(pady=10)
            
        except Exception as e:
            logger.error(f"Error in export: {e}")
            messagebox.showerror("Error", f"Could not export data:\n{str(e)}")
    
    def _open_settings(self):
        """Open settings window"""
        try:
            from src.ui.windows.settings import SettingsWindow
            window = SettingsWindow(self.root)
        except Exception as e:
            logger.error(f"Error opening settings: {e}")
            messagebox.showerror("Error", f"Could not open settings window:\n{str(e)}")
    
    def run(self):
        """Run the application"""
        logger.info("Starting GUI application")
        self.root.mainloop()


if __name__ == '__main__':
    app = AttendanceApp()
    app.run()
