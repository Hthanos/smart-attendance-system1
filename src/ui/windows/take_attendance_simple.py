#!/usr/bin/env python3
"""
Simple Take Attendance Window
"""

import tkinter as tk
from tkinter import ttk, messagebox
import cv2
import json
from pathlib import Path
from PIL import Image, ImageTk
import logging

from config.settings import Settings
from src.core.face_recognizer import FaceRecognizer
from src.core.face_detector import FaceDetector
from src.database.operations import DatabaseOperations

logger = logging.getLogger(__name__)


class TakeAttendanceWindow:
    """Simple attendance taking window"""
    
    def __init__(self, parent):
        """Initialize window"""
        self.window = tk.Toplevel(parent)
        self.window.title("Take Attendance - Face Recognition")
        self.window.geometry("900x700")
        
        self.camera = None
        self.is_running = False
        self.recognizer = None
        self.detector = None
        self.label_mapping = {}
        
        # Load model
        self._load_model()
        
        # Setup UI
        self._setup_ui()
        
        # Start camera
        self._start_camera()
    
    def _load_model(self):
        """Load face recognition model"""
        try:
            model_path = Path('data/models/face_recognition_model.yml')
            mapping_path = Path('data/models/label_mapping.json')
            
            if not model_path.exists():
                messagebox.showerror(
                    "Error",
                    "Recognition model not found!\n\nPlease train the model first:\n- Click 'Train Model' button on main menu"
                )
                self.window.destroy()
                return
            
            # Load recognizer
            self.recognizer = FaceRecognizer()
            self.recognizer.load_model(str(model_path))
            
            # Load label mapping
            with open(mapping_path, 'r') as f:
                self.label_mapping = json.load(f)
            
            # Initialize detector
            self.detector = FaceDetector()
            
            logger.info("Model loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            messagebox.showerror("Error", f"Could not load recognition model:\n{str(e)}")
            self.window.destroy()
    
    def _setup_ui(self):
        """Setup user interface"""
        # Title
        title = tk.Label(
            self.window,
            text="Take Attendance - Face Recognition",
            font=("Arial", 16, "bold"),
            bg=Settings.THEME_COLOR,
            fg="white",
            pady=10
        )
        title.pack(fill=tk.X)
        
        # Course selection frame
        course_frame = tk.Frame(self.window, bg="#f8f9fa")
        course_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(
            course_frame,
            text="Select Course:",
            font=("Arial", 11, "bold"),
            bg="#f8f9fa"
        ).pack(side=tk.LEFT, padx=5)
        
        # Load courses
        ops = DatabaseOperations()
        self.courses = ops.get_all_courses()
        course_names = [f"{c['course_code']} - {c['course_name']}" for c in self.courses]
        
        self.course_var = tk.StringVar()
        self.course_combo = ttk.Combobox(
            course_frame,
            textvariable=self.course_var,
            values=course_names,
            state="readonly",
            width=40,
            font=("Arial", 10)
        )
        self.course_combo.pack(side=tk.LEFT, padx=5)
        
        if course_names:
            self.course_combo.current(0)
        
        # Session info
        self.session_id = None
        self.session_label = tk.Label(
            course_frame,
            text="",
            font=("Arial", 10),
            fg="green",
            bg="#f8f9fa"
        )
        self.session_label.pack(side=tk.LEFT, padx=10)
        
        # Create session button
        tk.Button(
            course_frame,
            text="Start Session",
            command=self._create_session,
            font=("Arial", 10),
            bg="#28a745",
            fg="white",
            padx=10
        ).pack(side=tk.LEFT, padx=5)
        
        # Video frame
        video_frame = tk.Frame(self.window, bg="black")
        video_frame.pack(pady=10)
        
        self.video_label = tk.Label(video_frame, bg="black")
        self.video_label.pack()
        
        # Info label
        self.info_label = tk.Label(
            self.window,
            text="Position your face in front of the camera",
            font=("Arial", 12),
            fg="blue"
        )
        self.info_label.pack(pady=10)
        
        # Recognized students list
        list_frame = tk.Frame(self.window)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        tk.Label(
            list_frame,
            text="Recognized Students:",
            font=("Arial", 12, "bold")
        ).pack(anchor=tk.W)
        
        # Create treeview
        self.tree = ttk.Treeview(
            list_frame,
            columns=("Name", "Reg Number", "Confidence", "Time"),
            show="headings",
            height=8
        )
        
        self.tree.heading("Name", text="Student Name")
        self.tree.heading("Reg Number", text="Registration Number")
        self.tree.heading("Confidence", text="Confidence")
        self.tree.heading("Time", text="Time")
        
        self.tree.column("Name", width=200)
        self.tree.column("Reg Number", width=180)
        self.tree.column("Confidence", width=100)
        self.tree.column("Time", width=150)
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Buttons
        btn_frame = tk.Frame(self.window)
        btn_frame.pack(pady=10)
        
        tk.Button(
            btn_frame,
            text="Close",
            command=self._close,
            width=15,
            font=("Arial", 11),
            bg="#dc3545",
            fg="white"
        ).pack(side=tk.LEFT, padx=5)
        
        # Track recognized students
        self.recognized_students = set()
        
        # Handle window close
        self.window.protocol("WM_DELETE_WINDOW", self._close)
    
    def _start_camera(self):
        """Start camera capture"""
        try:
            self.camera = cv2.VideoCapture(0)
            if not self.camera.isOpened():
                messagebox.showerror("Error", "Could not open camera!")
                self.window.destroy()
                return
            
            self.is_running = True
            self._update_frame()
            
        except Exception as e:
            logger.error(f"Camera error: {e}")
            messagebox.showerror("Error", f"Could not start camera:\n{str(e)}")
            self.window.destroy()
    
    def _update_frame(self):
        """Update video frame"""
        if not self.is_running:
            return
        
        try:
            ret, frame = self.camera.read()
            if not ret:
                return
            
            # Detect faces with STRICTER parameters to avoid false detections
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            # Use higher minNeighbors (7-8) and larger minSize to reduce false positives
            faces = self.detector.detect_faces(
                gray,
                scale_factor=1.1,
                min_neighbors=8,  # Increased from 5 to 8 - much stricter
                min_size=(60, 60)  # Larger minimum size
            )
            
            # Process each face with additional validation
            for (x, y, w, h) in faces:
                # VALIDATION 1: Check aspect ratio (faces are roughly square/slightly taller)
                aspect_ratio = w / h
                if aspect_ratio < 0.7 or aspect_ratio > 1.3:
                    continue  # Skip non-face-like rectangles
                
                # VALIDATION 2: Check minimum size (avoid tiny detections)
                if w < 80 or h < 80:
                    continue  # Too small to be a reliable face
                
                # VALIDATION 3: Check if face is too large (likely a false positive)
                if w > 400 or h > 400:
                    continue  # Too large, probably not a face
                
                # Extract face region
                face_roi = gray[y:y+h, x:x+w]
                face_resized = cv2.resize(face_roi, (200, 200))
                
                # Apply CLAHE for better preprocessing (same as training)
                clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
                face_processed = clahe.apply(face_resized)
                
                # Recognize
                label, confidence = self.recognizer.predict(face_processed)
                
                # Get student info
                # label is already the registration number from recognizer
                reg_number = label if label is not None else "Unknown"
                
                # Draw rectangle and text with STRICT confidence threshold
                # Lower confidence is better for LBPH - under 50 is excellent recognition
                if confidence < 50 and reg_number != "Unknown":  # Excellent recognition
                    color = (0, 255, 0)  # Green for recognized
                    text = f"{reg_number} ({confidence:.1f})"
                    
                    # Mark attendance if not already marked
                    if reg_number not in self.recognized_students and reg_number != "Unknown":
                        self._mark_attendance(reg_number, confidence)
                        self.recognized_students.add(reg_number)
                        
                elif confidence < 80 and reg_number != "Unknown":  # Good recognition
                    color = (0, 255, 0)  # Green for good match too
                    text = f"{reg_number} ({confidence:.1f})"
                    
                    # Mark attendance for good matches too
                    if reg_number not in self.recognized_students:
                        self._mark_attendance(reg_number, confidence)
                        self.recognized_students.add(reg_number)
                        
                elif confidence < 100:  # Uncertain
                    color = (255, 165, 0)  # Orange for uncertain
                    text = f"{reg_number}? ({confidence:.1f})"
                    
                else:  # Low confidence or unknown
                    color = (0, 0, 255)  # Red for unknown
                    text = f"Unknown ({confidence:.1f})"
                
                cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
                cv2.putText(frame, text, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
            
            # Convert to PhotoImage
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_resized = cv2.resize(frame_rgb, (640, 480))
            img = Image.fromarray(frame_resized)
            imgtk = ImageTk.PhotoImage(image=img)
            
            self.video_label.imgtk = imgtk
            self.video_label.configure(image=imgtk)
            
            # Update info
            if len(faces) == 0:
                self.info_label.config(text="No face detected", fg="gray")
            elif len(faces) == 1:
                self.info_label.config(text="Face detected - recognizing...", fg="blue")
            else:
                self.info_label.config(text=f"{len(faces)} faces detected", fg="orange")
            
        except Exception as e:
            logger.error(f"Frame update error: {e}")
        
        # Schedule next update
        if self.is_running:
            self.window.after(30, self._update_frame)
    
    def _create_session(self):
        """Create or get today's session for selected course"""
        try:
            from datetime import datetime, date, time
            from src.services.attendance_service import AttendanceService
            
            if not self.course_combo.get():
                messagebox.showwarning("Warning", "Please select a course first")
                return
            
            # Get selected course
            course_idx = self.course_combo.current()
            course = self.courses[course_idx]
            
            # Create session
            attendance_service = AttendanceService()
            current_time = datetime.now().time()
            self.session_id = attendance_service.create_session(
                course_id=course['id'],
                session_date=date.today(),
                start_time=current_time.strftime('%H:%M:%S') if current_time else None,
                location="Face Recognition System"
            )
            
            if self.session_id:
                self.session_label.config(
                    text=f"✓ Session Active (ID: {self.session_id})",
                    fg="green"
                )
                messagebox.showinfo(
                    "Session Created",
                    f"Attendance session started for:\n{course['course_code']} - {course['course_name']}"
                )
                logger.info(f"Session created: ID={self.session_id}, Course={course['course_code']}")
            else:
                messagebox.showerror("Error", "Failed to create session")
                
        except Exception as e:
            logger.error(f"Error creating session: {e}")
            messagebox.showerror("Error", f"Could not create session:\n{str(e)}")
    
    def _mark_attendance(self, reg_number, confidence):
        """Mark student attendance and save to database"""
        try:
            from datetime import datetime, date
            from src.services.attendance_service import AttendanceService
            
            # Get student info
            ops = DatabaseOperations()
            student = ops.get_student_by_reg_number(reg_number)
            
            if not student:
                return
            
            # Check if session is active
            if not self.session_id:
                # Add to tree but don't save to database
                timestamp = datetime.now().strftime("%H:%M:%S")
                self.tree.insert(
                    "",
                    0,
                    values=(
                        student['full_name'],
                        reg_number,
                        f"{confidence:.1f}",
                        timestamp + " (Not Saved)"
                    )
                )
                logger.warning(f"Recognition logged but not saved - no active session: {student['full_name']}")
                return
            
            # Save to database
            attendance_service = AttendanceService()
            success = attendance_service.mark_attendance(
                student_id=student['id'],
                session_id=self.session_id,
                confidence_score=confidence
            )
            
            if success:
                # Add to tree
                timestamp = datetime.now().strftime("%H:%M:%S")
                self.tree.insert(
                    "",
                    0,
                    values=(
                        student['full_name'],
                        reg_number,
                        f"{confidence:.1f}",
                        timestamp
                    )
                )
                
                # Log success
                logger.info(f"Attendance saved: {student['full_name']} ({reg_number}) - Session: {self.session_id}")
                
                # Flash info label
                self.info_label.config(
                    text=f"✓ Attendance Saved: {student['full_name']}",
                    fg="green"
                )
            else:
                logger.warning(f"Failed to save attendance for {student['full_name']}")
            
        except Exception as e:
            logger.error(f"Error marking attendance: {e}")
    
    def _close(self):
        """Close window"""
        self.is_running = False
        
        if self.camera:
            self.camera.release()
        
        self.window.destroy()


if __name__ == '__main__':
    root = tk.Tk()
    root.withdraw()
    window = TakeAttendanceWindow(root)
    root.mainloop()
