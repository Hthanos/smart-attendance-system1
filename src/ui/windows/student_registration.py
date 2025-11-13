"""
Student Registration Window
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import cv2
from PIL import Image, ImageTk
import logging
from pathlib import Path

from config.settings import Settings
from src.services.student_service import StudentService
from src.core.camera import Camera
from src.core.face_detector import FaceDetector
from src.core.image_processor import ImageProcessor

logger = logging.getLogger(__name__)


class StudentRegistrationWindow(tk.Toplevel):
    """Student registration window"""
    
    def __init__(self, parent):
        """Initialize registration window"""
        super().__init__(parent)
        
        self.title("Student Registration")
        self.geometry("1400x850")  # Much larger to fit big camera view
        
        self.student_service = StudentService()
        self.camera = None
        self.face_detector = FaceDetector()
        self.image_processor = ImageProcessor()
        
        self.captured_images = []
        self.is_capturing = False
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup user interface"""
        # Title
        title_label = tk.Label(
            self,
            text="Register New Student",
            font=("Arial", 16, "bold"),
            bg=Settings.THEME_COLOR,
            fg="white",
            pady=15
        )
        title_label.pack(fill=tk.X)
        
        # Main container
        main_frame = tk.Frame(self, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left side - Student Information
        info_frame = tk.LabelFrame(
            main_frame,
            text="Student Information",
            font=("Arial", 12, "bold"),
            padx=15,
            pady=15
        )
        info_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        # Form fields
        fields = [
            ("Registration Number:", "reg_number"),
            ("Full Name:", "full_name"),
            ("Email:", "email"),
            ("Phone:", "phone"),
            ("Department:", "department"),
            ("Year of Study:", "year"),
            ("Program:", "program")
        ]
        
        self.entries = {}
        
        for i, (label, key) in enumerate(fields):
            tk.Label(
                info_frame,
                text=label,
                font=("Arial", 10)
            ).grid(row=i, column=0, sticky="w", pady=5)
            
            entry = tk.Entry(info_frame, font=("Arial", 10), width=30)
            entry.grid(row=i, column=1, sticky="ew", pady=5)
            self.entries[key] = entry
        
        # Right side - Camera Capture (MUCH LARGER)
        camera_frame = tk.LabelFrame(
            main_frame,
            text="Face Capture",
            font=("Arial", 12, "bold"),
            padx=15,
            pady=15
        )
        camera_frame.grid(row=0, column=1, sticky="nsew")
        
        # Camera display - FULL SIZE to fill the space
        self.camera_label = tk.Label(
            camera_frame,
            text="Camera Preview\n\n\nClick 'Start Camera' to begin",
            bg="black",
            fg="white",
            font=("Arial", 14)
        )
        self.camera_label.pack(fill=tk.BOTH, expand=True, pady=10, padx=10)
        
        # Progress label above controls
        self.progress_label = tk.Label(
            camera_frame,
            text=f"Captured: 0 / {Settings.IMAGES_PER_STUDENT}",
            font=("Arial", 11, "bold")
        )
        self.progress_label.pack(pady=5)
        
        # Capture controls at BOTTOM
        controls_frame = tk.Frame(camera_frame)
        controls_frame.pack(pady=15)
        
        self.start_camera_btn = tk.Button(
            controls_frame,
            text="Start Camera",
            command=self._start_camera,
            bg=Settings.SUCCESS_COLOR,
            fg="white",
            font=("Arial", 11),
            padx=20,
            pady=8
        )
        self.start_camera_btn.grid(row=0, column=0, padx=8)
        
        self.capture_btn = tk.Button(
            controls_frame,
            text="Capture Images",
            command=self._capture_images,
            bg=Settings.ACCENT_COLOR,
            fg="white",
            font=("Arial", 11),
            padx=20,
            pady=8,
            state=tk.DISABLED
        )
        self.capture_btn.grid(row=0, column=1, padx=8)
        
        self.stop_camera_btn = tk.Button(
            controls_frame,
            text="Stop Camera",
            command=self._stop_camera,
            bg=Settings.ERROR_COLOR,
            fg="white",
            font=("Arial", 11),
            padx=20,
            pady=8,
            state=tk.DISABLED
        )
        self.stop_camera_btn.grid(row=0, column=2, padx=8)
        
        # Configure grid weights
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)
        
        # Bottom buttons
        button_frame = tk.Frame(self, padx=20, pady=10)
        button_frame.pack(fill=tk.X)
        
        save_btn = tk.Button(
            button_frame,
            text="Save Student",
            command=self._save_student,
            bg=Settings.SUCCESS_COLOR,
            fg="white",
            font=("Arial", 12, "bold"),
            padx=30,
            pady=10
        )
        save_btn.pack(side=tk.LEFT, padx=5)
        
        cancel_btn = tk.Button(
            button_frame,
            text="Cancel",
            command=self._cancel,
            bg=Settings.ERROR_COLOR,
            fg="white",
            font=("Arial", 12),
            padx=30,
            pady=10
        )
        cancel_btn.pack(side=tk.RIGHT, padx=5)
    
    def _start_camera(self):
        """Start camera for face capture"""
        try:
            self.camera = Camera()
            if self.camera.open():
                self.is_capturing = True
                self.start_camera_btn.config(state=tk.DISABLED)
                self.capture_btn.config(state=tk.NORMAL)
                self.stop_camera_btn.config(state=tk.NORMAL)
                self._update_camera_feed()
                logger.info("Camera started")
            else:
                messagebox.showerror("Error", "Failed to start camera")
        except Exception as e:
            logger.error(f"Camera start error: {str(e)}")
            messagebox.showerror("Error", f"Camera error: {str(e)}")
    
    def _update_camera_feed(self):
        """Update camera feed in UI"""
        if self.is_capturing and self.camera:
            ret, frame = self.camera.read()
            
            if ret:
                # Detect faces
                faces = self.face_detector.detect_faces(frame)
                
                # Draw rectangles
                display_frame = self.face_detector.draw_faces(frame, faces, label="Face")
                
                # Convert to PIL Image - MAXIMUM size for the space
                frame_rgb = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame_rgb)
                # Make it even bigger - 800x600 to fill the right section
                img = img.resize((800, 600), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(image=img)
                
                self.camera_label.config(image=photo)
                self.camera_label.image = photo
            
            # Schedule next update
            self.after(30, self._update_camera_feed)
    
    def _capture_images(self):
        """Capture multiple face images"""
        reg_number = self.entries['reg_number'].get().strip()
        
        if not reg_number:
            messagebox.showwarning("Warning", "Please enter registration number first")
            return
        
        try:
            import time
            
            self.captured_images = []
            target_count = Settings.IMAGES_PER_STUDENT
            
            messagebox.showinfo(
                "Ready",
                f"Will capture {target_count} images.\nPlease look at camera and move slightly.\nCapture will start in 2 seconds."
            )
            
            time.sleep(2)
            
            while len(self.captured_images) < target_count and self.is_capturing:
                ret, frame = self.camera.read()
                
                if ret:
                    # Detect face
                    face_rect = self.face_detector.detect_largest_face(frame)
                    
                    if face_rect:
                        # Extract and preprocess face
                        face_img = self.face_detector.extract_face(frame, face_rect, margin=10)
                        processed = self.image_processor.preprocess_face(face_img)
                        
                        self.captured_images.append(processed)
                        
                        # Update progress
                        self.progress_label.config(
                            text=f"Captured: {len(self.captured_images)} / {target_count}"
                        )
                        self.update()
                        
                        time.sleep(Settings.IMAGE_CAPTURE_DELAY)
            
            messagebox.showinfo("Success", f"Captured {len(self.captured_images)} images!")
            logger.info(f"Captured {len(self.captured_images)} face images")
            
        except Exception as e:
            logger.error(f"Image capture error: {str(e)}")
            messagebox.showerror("Error", f"Capture failed: {str(e)}")
    
    def _stop_camera(self):
        """Stop camera"""
        self.is_capturing = False
        if self.camera:
            self.camera.release()
        
        self.start_camera_btn.config(state=tk.NORMAL)
        self.capture_btn.config(state=tk.DISABLED)
        self.stop_camera_btn.config(state=tk.DISABLED)
        
        self.camera_label.config(image='', text="Camera Stopped")
        logger.info("Camera stopped")
    
    def _save_student(self):
        """Save student to database"""
        # Validate inputs
        reg_number = self.entries['reg_number'].get().strip()
        full_name = self.entries['full_name'].get().strip()
        
        if not reg_number or not full_name:
            messagebox.showwarning("Warning", "Registration number and name are required")
            return
        
        if len(self.captured_images) < Settings.IMAGES_PER_STUDENT:
            messagebox.showwarning(
                "Warning",
                f"Please capture at least {Settings.IMAGES_PER_STUDENT} face images"
            )
            return
        
        try:
            # Parse year of study safely
            year_str = self.entries['year'].get().strip()
            year_of_study = None
            if year_str:
                try:
                    year_of_study = int(year_str)
                except ValueError:
                    messagebox.showwarning("Warning", "Year of study must be a number")
                    return
            
            # Register student
            student_id = self.student_service.register_student(
                registration_number=reg_number,
                full_name=full_name,
                email=self.entries['email'].get().strip() or None,
                phone=self.entries['phone'].get().strip() or None,
                department=self.entries['department'].get().strip() or None,
                year_of_study=year_of_study,
                program=self.entries['program'].get().strip() or None
            )
            
            if not student_id:
                messagebox.showerror("Error", "Failed to register student (may already exist)")
                return
            
            # Save face images
            face_dir = self.student_service.get_student_face_images_dir(reg_number)
            
            for i, img in enumerate(self.captured_images):
                img_path = face_dir / f"{i+1:03d}.jpg"
                cv2.imwrite(str(img_path), img)
            
            logger.info(f"Student registered: {reg_number}")
            
            # Stop camera before showing dialogs to prevent widget access errors
            self._stop_camera()
            
            messagebox.showinfo(
                "Success",
                f"Student registered successfully!\nID: {student_id}\nImages saved: {len(self.captured_images)}"
            )
            
            # Ask if want to register another
            if messagebox.askyesno("Continue?", "Register another student?"):
                self._clear_form()
            else:
                self.destroy()
            
        except Exception as e:
            logger.error(f"Save student error: {str(e)}")
            messagebox.showerror("Error", f"Failed to save: {str(e)}")
    
    def _clear_form(self):
        """Clear all form fields"""
        for entry in self.entries.values():
            entry.delete(0, tk.END)
        
        self.captured_images = []
        self.progress_label.config(text=f"Captured: 0 / {Settings.IMAGES_PER_STUDENT}")
    
    def _cancel(self):
        """Cancel and close window"""
        self._stop_camera()
        self.destroy()
    
    def destroy(self):
        """Cleanup before destroying window"""
        self._stop_camera()
        super().destroy()
