"""
Student Card Component - Display student information
"""

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from pathlib import Path
import logging

from config.settings import Settings

logger = logging.getLogger(__name__)


class StudentCard(tk.Frame):
    """Student information card component"""
    
    def __init__(self, parent, student_data=None, **kwargs):
        """
        Initialize student card
        
        Args:
            parent: Parent widget
            student_data: Dictionary with student information
        """
        super().__init__(parent, relief=tk.RAISED, borderwidth=2, **kwargs)
        
        self.student_data = student_data
        self._setup_ui()
        
        if student_data:
            self.set_student(student_data)
    
    def _setup_ui(self):
        """Setup UI components"""
        # Configure grid
        self.grid_columnconfigure(1, weight=1)
        
        # Photo frame
        photo_frame = tk.Frame(self, width=100, height=120)
        photo_frame.grid(row=0, column=0, rowspan=5, padx=10, pady=10, sticky="n")
        photo_frame.grid_propagate(False)
        
        self.photo_label = tk.Label(
            photo_frame,
            text="No Photo",
            bg="lightgray",
            fg="gray"
        )
        self.photo_label.pack(fill=tk.BOTH, expand=True)
        
        # Information fields
        info_frame = tk.Frame(self)
        info_frame.grid(row=0, column=1, sticky="ew", padx=10, pady=5)
        
        # Name
        self.name_label = tk.Label(
            info_frame,
            text="Student Name",
            font=("Arial", 12, "bold"),
            anchor="w"
        )
        self.name_label.pack(fill=tk.X)
        
        # Registration number
        self.reg_label = tk.Label(
            info_frame,
            text="Registration Number",
            font=("Arial", 10),
            fg="gray",
            anchor="w"
        )
        self.reg_label.pack(fill=tk.X)
        
        # Separator
        ttk.Separator(self, orient=tk.HORIZONTAL).grid(
            row=1, column=1, sticky="ew", padx=10, pady=5
        )
        
        # Details frame
        details_frame = tk.Frame(self)
        details_frame.grid(row=2, column=1, sticky="ew", padx=10, pady=5)
        
        # Email
        email_row = tk.Frame(details_frame)
        email_row.pack(fill=tk.X, pady=2)
        tk.Label(
            email_row,
            text="Email:",
            font=("Arial", 9, "bold"),
            width=10,
            anchor="w"
        ).pack(side=tk.LEFT)
        self.email_label = tk.Label(
            email_row,
            text="",
            font=("Arial", 9),
            anchor="w"
        )
        self.email_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Phone
        phone_row = tk.Frame(details_frame)
        phone_row.pack(fill=tk.X, pady=2)
        tk.Label(
            phone_row,
            text="Phone:",
            font=("Arial", 9, "bold"),
            width=10,
            anchor="w"
        ).pack(side=tk.LEFT)
        self.phone_label = tk.Label(
            phone_row,
            text="",
            font=("Arial", 9),
            anchor="w"
        )
        self.phone_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Course
        course_row = tk.Frame(details_frame)
        course_row.pack(fill=tk.X, pady=2)
        tk.Label(
            course_row,
            text="Course:",
            font=("Arial", 9, "bold"),
            width=10,
            anchor="w"
        ).pack(side=tk.LEFT)
        self.course_label = tk.Label(
            course_row,
            text="",
            font=("Arial", 9),
            anchor="w"
        )
        self.course_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Status indicator
        status_frame = tk.Frame(self)
        status_frame.grid(row=3, column=1, sticky="ew", padx=10, pady=5)
        
        self.status_label = tk.Label(
            status_frame,
            text="",
            font=("Arial", 9),
            anchor="w"
        )
        self.status_label.pack(side=tk.LEFT)
    
    def set_student(self, student_data):
        """
        Set student information
        
        Args:
            student_data: Dictionary with keys:
                - full_name
                - registration_number
                - email
                - phone_number
                - course (optional)
                - photo_path (optional)
                - status (optional)
        """
        self.student_data = student_data
        
        # Update name
        name = student_data.get('full_name', 'Unknown')
        self.name_label.config(text=name)
        
        # Update registration number
        reg_no = student_data.get('registration_number', 'N/A')
        self.reg_label.config(text=f"Reg No: {reg_no}")
        
        # Update email
        email = student_data.get('email', 'N/A')
        self.email_label.config(text=email)
        
        # Update phone
        phone = student_data.get('phone_number', 'N/A')
        self.phone_label.config(text=phone)
        
        # Update course
        course = student_data.get('course', 'N/A')
        self.course_label.config(text=course)
        
        # Update photo
        self._load_photo(student_data.get('photo_path'))
        
        # Update status
        status = student_data.get('status', '')
        if status:
            color = Settings.SUCCESS_COLOR if status == "Active" else "gray"
            self.status_label.config(text=f"Status: {status}", fg=color)
    
    def _load_photo(self, photo_path):
        """Load and display student photo"""
        try:
            if photo_path and Path(photo_path).exists():
                # Load image
                img = Image.open(photo_path)
                img = img.resize((100, 120), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                
                self.photo_label.config(image=photo, text='')
                self.photo_label.image = photo
            else:
                # Try to load first face image from dataset
                if self.student_data and 'registration_number' in self.student_data:
                    reg_no = self.student_data['registration_number']
                    faces_dir = Path(Settings.FACES_DIR) / reg_no
                    
                    if faces_dir.exists():
                        face_images = list(faces_dir.glob("*.jpg"))
                        if face_images:
                            img = Image.open(face_images[0])
                            img = img.resize((100, 120), Image.Resampling.LANCZOS)
                            photo = ImageTk.PhotoImage(img)
                            
                            self.photo_label.config(image=photo, text='')
                            self.photo_label.image = photo
                            return
                
                # Use placeholder
                self.photo_label.config(image='', text="No Photo")
                
        except Exception as e:
            logger.error(f"Error loading photo: {str(e)}")
            self.photo_label.config(image='', text="Error")
    
    def clear(self):
        """Clear card content"""
        self.student_data = None
        self.name_label.config(text="Student Name")
        self.reg_label.config(text="Registration Number")
        self.email_label.config(text="")
        self.phone_label.config(text="")
        self.course_label.config(text="")
        self.status_label.config(text="")
        self.photo_label.config(image='', text="No Photo")


class StudentListItem(tk.Frame):
    """Compact student list item for lists/trees"""
    
    def __init__(self, parent, student_data, on_click=None, **kwargs):
        """
        Initialize list item
        
        Args:
            parent: Parent widget
            student_data: Student information
            on_click: Callback function when clicked
        """
        super().__init__(
            parent,
            relief=tk.FLAT,
            borderwidth=1,
            cursor="hand2",
            **kwargs
        )
        
        self.student_data = student_data
        self.on_click = on_click
        self.selected = False
        
        self._setup_ui()
        self.bind("<Button-1>", self._handle_click)
    
    def _setup_ui(self):
        """Setup UI"""
        # Configure
        self.config(bg="white")
        
        # Photo thumbnail
        photo_label = tk.Label(
            self,
            text="📷",
            font=("Arial", 16),
            bg="white",
            width=3
        )
        photo_label.grid(row=0, column=0, rowspan=2, padx=5, pady=5)
        
        # Name
        name_label = tk.Label(
            self,
            text=self.student_data.get('full_name', 'Unknown'),
            font=("Arial", 10, "bold"),
            bg="white",
            anchor="w"
        )
        name_label.grid(row=0, column=1, sticky="w", padx=5)
        
        # Reg number
        reg_label = tk.Label(
            self,
            text=self.student_data.get('registration_number', 'N/A'),
            font=("Arial", 9),
            fg="gray",
            bg="white",
            anchor="w"
        )
        reg_label.grid(row=1, column=1, sticky="w", padx=5)
        
        # Bind click to all children
        for widget in self.winfo_children():
            widget.bind("<Button-1>", self._handle_click)
    
    def _handle_click(self, event):
        """Handle click event"""
        self.select()
        if self.on_click:
            self.on_click(self.student_data)
    
    def select(self):
        """Mark as selected"""
        self.selected = True
        self.config(bg=Settings.THEME_COLOR, relief=tk.RAISED)
        for widget in self.winfo_children():
            if isinstance(widget, tk.Label):
                widget.config(bg=Settings.THEME_COLOR, fg="white")
    
    def deselect(self):
        """Mark as deselected"""
        self.selected = False
        self.config(bg="white", relief=tk.FLAT)
        for widget in self.winfo_children():
            if isinstance(widget, tk.Label):
                widget.config(bg="white")
                # Restore original fg color
                text = widget.cget("text")
                if self.student_data.get('registration_number') in str(text):
                    widget.config(fg="gray")
                else:
                    widget.config(fg="black")
