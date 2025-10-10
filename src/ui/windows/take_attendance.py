"""
Take Attendance Window - Live attendance tracking
"""

import tkinter as tk
from tkinter import ttk, messagebox
import cv2
from PIL import Image, ImageTk
import logging
from datetime import date

from config.settings import Settings
from src.services.attendance_service import AttendanceService
from src.services.training_service import TrainingService
from src.services.student_service import StudentService
from src.core.camera import Camera
from src.core.face_detector import FaceDetector
from src.database.operations import DatabaseOperations

logger = logging.getLogger(__name__)


class TakeAttendanceWindow(tk.Toplevel):
    """Take attendance window"""
    
    def __init__(self, parent):
        """Initialize attendance window"""
        super().__init__(parent)
        
        self.title("Take Attendance")
        self.geometry("1000x700")
        
        self.attendance_service = AttendanceService()
        self.training_service = TrainingService()
        self.student_service = StudentService()
        self.db_ops = DatabaseOperations()
        
        self.camera = None
        self.face_detector = FaceDetector()
        self.is_running = False
        
        self.current_session_id = None
        self.marked_students = set()
        
        self._setup_ui()
        self._load_sessions()
        
        # Load trained model
        if not self.training_service.load_trained_model():
            messagebox.showwarning(
                "Warning",
                "No trained model found. Please train the model first."
            )
    
    def _setup_ui(self):
        """Setup user interface"""
        # Title
        title_label = tk.Label(
            self,
            text="Take Attendance",
            font=("Arial", 16, "bold"),
            bg=Settings.THEME_COLOR,
            fg="white",
            pady=15
        )
        title_label.pack(fill=tk.X)
        
        # Main container
        main_frame = tk.Frame(self, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left side - Camera and controls
        left_frame = tk.Frame(main_frame)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        # Session selection
        session_frame = tk.LabelFrame(
            left_frame,
            text="Select Session",
            font=("Arial", 11, "bold"),
            padx=10,
            pady=10
        )
        session_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.session_combo = ttk.Combobox(
            session_frame,
            font=("Arial", 10),
            state="readonly",
            width=40
        )
        self.session_combo.pack(pady=5)
        self.session_combo.bind("<<ComboboxSelected>>", self._on_session_selected)
        
        # Camera display
        camera_frame = tk.LabelFrame(
            left_frame,
            text="Camera Feed",
            font=("Arial", 11, "bold"),
            padx=10,
            pady=10
        )
        camera_frame.pack(fill=tk.BOTH, expand=True)
        
        self.camera_label = tk.Label(
            camera_frame,
            text="Camera Off",
            bg="black",
            fg="white",
            width=50,
            height=20
        )
        self.camera_label.pack(pady=10)
        
        # Controls
        controls_frame = tk.Frame(camera_frame)
        controls_frame.pack(pady=10)
        
        self.start_btn = tk.Button(
            controls_frame,
            text="Start Attendance",
            command=self._start_attendance,
            bg=Settings.SUCCESS_COLOR,
            fg="white",
            font=("Arial", 11, "bold"),
            padx=20,
            pady=8,
            state=tk.DISABLED
        )
        self.start_btn.grid(row=0, column=0, padx=5)
        
        self.stop_btn = tk.Button(
            controls_frame,
            text="Stop",
            command=self._stop_attendance,
            bg=Settings.ERROR_COLOR,
            fg="white",
            font=("Arial", 11, "bold"),
            padx=20,
            pady=8,
            state=tk.DISABLED
        )
        self.stop_btn.grid(row=0, column=1, padx=5)
        
        # Right side - Attendance list
        right_frame = tk.LabelFrame(
            main_frame,
            text="Attendance Log",
            font=("Arial", 11, "bold"),
            padx=10,
            pady=10
        )
        right_frame.grid(row=0, column=1, sticky="nsew")
        
        # Attendance table
        columns = ("Reg No", "Name", "Time", "Confidence")
        self.attendance_tree = ttk.Treeview(
            right_frame,
            columns=columns,
            show="headings",
            height=20
        )
        
        for col in columns:
            self.attendance_tree.heading(col, text=col)
            self.attendance_tree.column(col, width=120)
        
        scrollbar = ttk.Scrollbar(
            right_frame,
            orient=tk.VERTICAL,
            command=self.attendance_tree.yview
        )
        self.attendance_tree.configure(yscroll=scrollbar.set)
        
        self.attendance_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Status label
        self.status_label = tk.Label(
            right_frame,
            text="Ready",
            font=("Arial", 10),
            fg=Settings.SUCCESS_COLOR
        )
        self.status_label.pack(pady=5)
        
        # Configure grid
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=2)
        main_frame.grid_columnconfigure(1, weight=1)
    
    def _load_sessions(self):
        """Load today's sessions"""
        try:
            sessions = self.attendance_service.get_todays_sessions()
            
            self.sessions = sessions
            session_names = [
                f"{s['course_code']} - {s['start_time']} ({s['location'] or 'N/A'})"
                for s in sessions
            ]
            
            self.session_combo['values'] = session_names
            
            if sessions:
                self.session_combo.current(0)
                self._on_session_selected(None)
            
        except Exception as e:
            logger.error(f"Error loading sessions: {str(e)}")
            messagebox.showerror("Error", f"Failed to load sessions: {str(e)}")
    
    def _on_session_selected(self, event):
        """Handle session selection"""
        idx = self.session_combo.current()
        if idx >= 0:
            self.current_session_id = self.sessions[idx]['id']
            self.start_btn.config(state=tk.NORMAL)
            self._load_session_attendance()
    
    def _load_session_attendance(self):
        """Load existing attendance for session"""
        if not self.current_session_id:
            return
        
        try:
            attendance = self.attendance_service.get_session_attendance(self.current_session_id)
            
            self.attendance_tree.delete(*self.attendance_tree.get_children())
            self.marked_students = set()
            
            for record in attendance:
                self.attendance_tree.insert(
                    "",
                    tk.END,
                    values=(
                        record['registration_number'],
                        record['full_name'],
                        record['timestamp'],
                        f"{record.get('confidence_score', 0):.1f}" if record.get('confidence_score') else "N/A"
                    )
                )
                self.marked_students.add(record['student_id'])
            
            self.status_label.config(text=f"Loaded: {len(attendance)} present")
            
        except Exception as e:
            logger.error(f"Error loading attendance: {str(e)}")
    
    def _start_attendance(self):
        """Start attendance tracking"""
        if not self.current_session_id:
            messagebox.showwarning("Warning", "Please select a session first")
            return
        
        if not self.training_service.is_model_trained():
            messagebox.showerror("Error", "Model not trained. Please train the model first.")
            return
        
        try:
            self.camera = Camera()
            if self.camera.open():
                self.is_running = True
                self.start_btn.config(state=tk.DISABLED)
                self.stop_btn.config(state=tk.NORMAL)
                self.session_combo.config(state=tk.DISABLED)
                
                self._process_attendance()
                logger.info("Attendance tracking started")
            else:
                messagebox.showerror("Error", "Failed to start camera")
        except Exception as e:
            logger.error(f"Start attendance error: {str(e)}")
            messagebox.showerror("Error", f"Failed to start: {str(e)}")
    
    def _process_attendance(self):
        """Process attendance from camera feed"""
        if not self.is_running or not self.camera:
            return
        
        ret, frame = self.camera.read()
        
        if ret:
            # Detect faces
            faces = self.face_detector.detect_faces(frame)
            
            # Recognize each face
            recognizer = self.training_service.get_recognizer()
            
            for face_rect in faces:
                x, y, w, h = face_rect
                
                # Extract and preprocess face
                face_img = self.face_detector.extract_face(frame, face_rect, margin=10)
                from src.core.image_processor import ImageProcessor
                processed = ImageProcessor.preprocess_face(face_img)
                
                # Recognize
                student_id, confidence = recognizer.predict(processed)
                
                if student_id and student_id not in self.marked_students:
                    # Mark attendance
                    success = self.attendance_service.mark_attendance(
                        student_id=student_id,
                        session_id=self.current_session_id,
                        confidence_score=confidence
                    )
                    
                    if success:
                        # Get student info
                        student = self.student_service.get_student(student_id)
                        
                        if student:
                            from datetime import datetime
                            self.attendance_tree.insert(
                                "",
                                0,  # Insert at top
                                values=(
                                    student['registration_number'],
                                    student['full_name'],
                                    datetime.now().strftime("%H:%M:%S"),
                                    f"{confidence:.1f}"
                                )
                            )
                            
                            self.marked_students.add(student_id)
                            
                            # Draw green rectangle for recognized
                            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                            cv2.putText(
                                frame,
                                student['full_name'],
                                (x, y-10),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                0.5,
                                (0, 255, 0),
                                2
                            )
                else:
                    # Draw blue rectangle for unknown or already marked
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
            
            # Update status
            self.status_label.config(
                text=f"Marked: {len(self.marked_students)} students"
            )
            
            # Display frame
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)
            img = img.resize((500, 375), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(image=img)
            
            self.camera_label.config(image=photo)
            self.camera_label.image = photo
        
        # Schedule next frame
        if self.is_running:
            self.after(100, self._process_attendance)
    
    def _stop_attendance(self):
        """Stop attendance tracking"""
        self.is_running = False
        
        if self.camera:
            self.camera.release()
        
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.session_combo.config(state="readonly")
        
        self.camera_label.config(image='', text="Camera Stopped")
        
        messagebox.showinfo(
            "Attendance Complete",
            f"Total students marked: {len(self.marked_students)}"
        )
        
        logger.info(f"Attendance tracking stopped. Total marked: {len(self.marked_students)}")
    
    def destroy(self):
        """Cleanup before closing"""
        self._stop_attendance()
        super().destroy()
