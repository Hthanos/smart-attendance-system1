"""
Settings Window
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import logging
from pathlib import Path

from config.settings import Settings
from src.database.operations import DatabaseOperations
from src.services.training_service import TrainingService

logger = logging.getLogger(__name__)


class SettingsWindow(tk.Toplevel):
    """Application settings window"""
    
    def __init__(self, parent):
        """Initialize settings window"""
        super().__init__(parent)
        
        self.title("Settings")
        self.geometry("800x600")
        
        self.db_ops = DatabaseOperations()
        self.training_service = TrainingService()
        
        self._setup_ui()
        self._load_settings()
    
    def _setup_ui(self):
        """Setup user interface"""
        # Title
        title_label = tk.Label(
            self,
            text="Settings",
            font=("Arial", 16, "bold"),
            bg=Settings.THEME_COLOR,
            fg="white",
            pady=15
        )
        title_label.pack(fill=tk.X)
        
        # Main container with tabs
        main_frame = tk.Frame(self, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Notebook for tabs
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Recognition settings tab
        self.recognition_frame = tk.Frame(notebook, padx=20, pady=20)
        notebook.add(self.recognition_frame, text="Recognition")
        self._setup_recognition_tab()
        
        # Institution settings tab
        self.institution_frame = tk.Frame(notebook, padx=20, pady=20)
        notebook.add(self.institution_frame, text="Institution")
        self._setup_institution_tab()
        
        # Camera settings tab
        self.camera_frame = tk.Frame(notebook, padx=20, pady=20)
        notebook.add(self.camera_frame, text="Camera")
        self._setup_camera_tab()
        
        # Model Management tab
        self.model_frame = tk.Frame(notebook, padx=20, pady=20)
        notebook.add(self.model_frame, text="Model")
        self._setup_model_tab()
        
        # Buttons
        button_frame = tk.Frame(main_frame)
        button_frame.pack(pady=(15, 0))
        
        save_btn = tk.Button(
            button_frame,
            text="Save Settings",
            command=self._save_settings,
            bg=Settings.SUCCESS_COLOR,
            fg="white",
            font=("Arial", 11, "bold"),
            padx=25,
            pady=8
        )
        save_btn.grid(row=0, column=0, padx=5)
        
        cancel_btn = tk.Button(
            button_frame,
            text="Cancel",
            command=self.destroy,
            font=("Arial", 11),
            padx=25,
            pady=8
        )
        cancel_btn.grid(row=0, column=1, padx=5)
    
    def _setup_recognition_tab(self):
        """Setup recognition settings"""
        # Confidence threshold
        conf_frame = tk.LabelFrame(
            self.recognition_frame,
            text="Recognition Confidence",
            font=("Arial", 11, "bold"),
            padx=15,
            pady=15
        )
        conf_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(
            conf_frame,
            text="Minimum Confidence Threshold:",
            font=("Arial", 10)
        ).grid(row=0, column=0, sticky="w", pady=5)
        
        self.confidence_var = tk.DoubleVar(value=Settings.RECOGNITION_CONFIDENCE_THRESHOLD)
        self.confidence_scale = tk.Scale(
            conf_frame,
            from_=0,
            to=100,
            orient=tk.HORIZONTAL,
            variable=self.confidence_var,
            length=300
        )
        self.confidence_scale.grid(row=1, column=0, pady=5)
        
        tk.Label(
            conf_frame,
            text="Lower value = More lenient, Higher value = More strict",
            font=("Arial", 9),
            fg="gray"
        ).grid(row=2, column=0, sticky="w")
        
        # Training parameters
        train_frame = tk.LabelFrame(
            self.recognition_frame,
            text="Training Parameters",
            font=("Arial", 11, "bold"),
            padx=15,
            pady=15
        )
        train_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(
            train_frame,
            text="Minimum Images per Student:",
            font=("Arial", 10)
        ).grid(row=0, column=0, sticky="w", pady=5)
        
        self.min_images_var = tk.IntVar(value=Settings.MIN_TRAINING_IMAGES)
        tk.Spinbox(
            train_frame,
            from_=10,
            to=100,
            textvariable=self.min_images_var,
            font=("Arial", 10),
            width=10
        ).grid(row=0, column=1, padx=(10, 0), pady=5)
        
        tk.Label(
            train_frame,
            text="Auto-retrain when adding new students:",
            font=("Arial", 10)
        ).grid(row=1, column=0, sticky="w", pady=5)
        
        self.auto_train_var = tk.BooleanVar(value=False)
        tk.Checkbutton(
            train_frame,
            variable=self.auto_train_var,
            font=("Arial", 10)
        ).grid(row=1, column=1, sticky="w", padx=(10, 0), pady=5)
    
    def _setup_institution_tab(self):
        """Setup institution settings"""
        inst_frame = tk.LabelFrame(
            self.institution_frame,
            text="Institution Information",
            font=("Arial", 11, "bold"),
            padx=15,
            pady=15
        )
        inst_frame.pack(fill=tk.X)
        
        # Institution name
        tk.Label(inst_frame, text="Institution Name:", font=("Arial", 10)).grid(
            row=0, column=0, sticky="w", pady=5
        )
        self.inst_name_var = tk.StringVar(value=Settings.INSTITUTION_NAME)
        tk.Entry(
            inst_frame,
            textvariable=self.inst_name_var,
            font=("Arial", 10),
            width=40
        ).grid(row=0, column=1, padx=(10, 0), pady=5)
        
        # Department
        tk.Label(inst_frame, text="Department:", font=("Arial", 10)).grid(
            row=1, column=0, sticky="w", pady=5
        )
        self.dept_var = tk.StringVar(value=Settings.DEPARTMENT)
        tk.Entry(
            inst_frame,
            textvariable=self.dept_var,
            font=("Arial", 10),
            width=40
        ).grid(row=1, column=1, padx=(10, 0), pady=5)
        
        # Academic year
        tk.Label(inst_frame, text="Academic Year:", font=("Arial", 10)).grid(
            row=2, column=0, sticky="w", pady=5
        )
        self.year_var = tk.StringVar(value=Settings.ACADEMIC_YEAR)
        tk.Entry(
            inst_frame,
            textvariable=self.year_var,
            font=("Arial", 10),
            width=40
        ).grid(row=2, column=1, padx=(10, 0), pady=5)
        
        # Semester
        tk.Label(inst_frame, text="Semester:", font=("Arial", 10)).grid(
            row=3, column=0, sticky="w", pady=5
        )
        self.semester_var = tk.StringVar(value=Settings.SEMESTER)
        semesters = ["Semester 1", "Semester 2", "Summer"]
        ttk.Combobox(
            inst_frame,
            textvariable=self.semester_var,
            values=semesters,
            font=("Arial", 10),
            width=37,
            state="readonly"
        ).grid(row=3, column=1, padx=(10, 0), pady=5)
    
    def _setup_camera_tab(self):
        """Setup camera settings"""
        cam_frame = tk.LabelFrame(
            self.camera_frame,
            text="Camera Configuration",
            font=("Arial", 11, "bold"),
            padx=15,
            pady=15
        )
        cam_frame.pack(fill=tk.X)
        
        # Camera type
        tk.Label(cam_frame, text="Camera Type:", font=("Arial", 10)).grid(
            row=0, column=0, sticky="w", pady=5
        )
        
        self.camera_type_var = tk.StringVar(value=Settings.CAMERA_TYPE)
        camera_types = ["usb", "picamera"]
        ttk.Combobox(
            cam_frame,
            textvariable=self.camera_type_var,
            values=camera_types,
            font=("Arial", 10),
            width=37,
            state="readonly"
        ).grid(row=0, column=1, padx=(10, 0), pady=5)
        
        # Camera index (for USB)
        tk.Label(cam_frame, text="USB Camera Index:", font=("Arial", 10)).grid(
            row=1, column=0, sticky="w", pady=5
        )
        self.camera_index_var = tk.IntVar(value=Settings.CAMERA_INDEX)
        tk.Spinbox(
            cam_frame,
            from_=0,
            to=10,
            textvariable=self.camera_index_var,
            font=("Arial", 10),
            width=10
        ).grid(row=1, column=1, sticky="w", padx=(10, 0), pady=5)
        
        # Resolution
        tk.Label(cam_frame, text="Resolution:", font=("Arial", 10)).grid(
            row=2, column=0, sticky="w", pady=5
        )
        
        res_frame = tk.Frame(cam_frame)
        res_frame.grid(row=2, column=1, sticky="w", padx=(10, 0), pady=5)
        
        self.width_var = tk.IntVar(value=Settings.CAMERA_WIDTH)
        tk.Label(res_frame, text="Width:", font=("Arial", 9)).pack(side=tk.LEFT)
        tk.Spinbox(
            res_frame,
            from_=320,
            to=1920,
            increment=80,
            textvariable=self.width_var,
            font=("Arial", 9),
            width=8
        ).pack(side=tk.LEFT, padx=5)
        
        self.height_var = tk.IntVar(value=Settings.CAMERA_HEIGHT)
        tk.Label(res_frame, text="Height:", font=("Arial", 9)).pack(
            side=tk.LEFT, padx=(10, 0)
        )
        tk.Spinbox(
            res_frame,
            from_=240,
            to=1080,
            increment=60,
            textvariable=self.height_var,
            font=("Arial", 9),
            width=8
        ).pack(side=tk.LEFT, padx=5)
        
        # FPS
        tk.Label(cam_frame, text="Target FPS:", font=("Arial", 10)).grid(
            row=3, column=0, sticky="w", pady=5
        )
        self.fps_var = tk.IntVar(value=Settings.CAMERA_FPS)
        tk.Spinbox(
            cam_frame,
            from_=10,
            to=60,
            increment=5,
            textvariable=self.fps_var,
            font=("Arial", 10),
            width=10
        ).grid(row=3, column=1, sticky="w", padx=(10, 0), pady=5)
    
    def _setup_model_tab(self):
        """Setup model management"""
        # Model info
        info_frame = tk.LabelFrame(
            self.model_frame,
            text="Model Information",
            font=("Arial", 11, "bold"),
            padx=15,
            pady=15
        )
        info_frame.pack(fill=tk.X, pady=(0, 15))
        
        is_trained = self.training_service.is_model_trained()
        status_text = "Model Status: "
        status_text += "Trained ✓" if is_trained else "Not Trained ✗"
        
        self.model_status_label = tk.Label(
            info_frame,
            text=status_text,
            font=("Arial", 10, "bold"),
            fg=Settings.SUCCESS_COLOR if is_trained else Settings.ERROR_COLOR
        )
        self.model_status_label.pack(pady=5)
        
        if is_trained:
            model_path = Settings.MODEL_PATH
            if Path(model_path).exists():
                from datetime import datetime
                mod_time = datetime.fromtimestamp(
                    Path(model_path).stat().st_mtime
                )
                tk.Label(
                    info_frame,
                    text=f"Last trained: {mod_time.strftime('%Y-%m-%d %H:%M:%S')}",
                    font=("Arial", 9),
                    fg="gray"
                ).pack()
        
        # Model actions
        actions_frame = tk.LabelFrame(
            self.model_frame,
            text="Model Actions",
            font=("Arial", 11, "bold"),
            padx=15,
            pady=15
        )
        actions_frame.pack(fill=tk.X)
        
        train_btn = tk.Button(
            actions_frame,
            text="Train/Retrain Model",
            command=self._train_model,
            bg=Settings.THEME_COLOR,
            fg="white",
            font=("Arial", 10, "bold"),
            padx=20,
            pady=8
        )
        train_btn.pack(pady=5)
        
        tk.Label(
            actions_frame,
            text="Train the recognition model with current student faces",
            font=("Arial", 9),
            fg="gray"
        ).pack(pady=(0, 10))
        
        backup_btn = tk.Button(
            actions_frame,
            text="Backup Model",
            command=self._backup_model,
            font=("Arial", 10),
            padx=20,
            pady=8
        )
        backup_btn.pack(pady=5)
        
        restore_btn = tk.Button(
            actions_frame,
            text="Restore Model",
            command=self._restore_model,
            font=("Arial", 10),
            padx=20,
            pady=8
        )
        restore_btn.pack(pady=5)
    
    def _load_settings(self):
        """Load current settings"""
        try:
            settings = self.db_ops.get_all_settings()
            
            for setting in settings:
                key = setting['setting_key']
                value = setting['setting_value']
                
                # Update UI based on settings
                # (Settings from DB would override defaults)
                
        except Exception as e:
            logger.error(f"Error loading settings: {str(e)}")
    
    def _save_settings(self):
        """Save settings"""
        try:
            # Save to database
            settings = {
                'confidence_threshold': self.confidence_var.get(),
                'min_training_images': self.min_images_var.get(),
                'auto_train': self.auto_train_var.get(),
                'institution_name': self.inst_name_var.get(),
                'department': self.dept_var.get(),
                'academic_year': self.year_var.get(),
                'semester': self.semester_var.get(),
                'camera_type': self.camera_type_var.get(),
                'camera_index': self.camera_index_var.get(),
                'camera_width': self.width_var.get(),
                'camera_height': self.height_var.get(),
                'camera_fps': self.fps_var.get()
            }
            
            for key, value in settings.items():
                self.db_ops.update_setting(key, str(value))
            
            messagebox.showinfo(
                "Success",
                "Settings saved successfully!\nRestart the application for changes to take effect."
            )
            
            logger.info("Settings saved successfully")
            self.destroy()
            
        except Exception as e:
            logger.error(f"Error saving settings: {str(e)}")
            messagebox.showerror("Error", f"Failed to save settings: {str(e)}")
    
    def _train_model(self):
        """Train recognition model"""
        response = messagebox.askyesno(
            "Confirm Training",
            "This will train the model with all current student faces.\n"
            "This may take several minutes.\n\n"
            "Continue?"
        )
        
        if not response:
            return
        
        try:
            # Create progress window
            progress = tk.Toplevel(self)
            progress.title("Training Model")
            progress.geometry("400x150")
            progress.transient(self)
            progress.grab_set()
            
            tk.Label(
                progress,
                text="Training model...",
                font=("Arial", 12, "bold")
            ).pack(pady=20)
            
            progress_bar = ttk.Progressbar(
                progress,
                mode='indeterminate',
                length=300
            )
            progress_bar.pack(pady=10)
            progress_bar.start(10)
            
            status_label = tk.Label(
                progress,
                text="Please wait...",
                font=("Arial", 10)
            )
            status_label.pack()
            
            self.update()
            
            # Train in background
            def train():
                try:
                    success = self.training_service.train_model()
                    progress.destroy()
                    
                    if success:
                        messagebox.showinfo(
                            "Success",
                            "Model trained successfully!"
                        )
                        self._setup_model_tab()  # Refresh model info
                    else:
                        messagebox.showerror(
                            "Error",
                            "Training failed. Check logs for details."
                        )
                except Exception as e:
                    progress.destroy()
                    messagebox.showerror("Error", f"Training error: {str(e)}")
            
            self.after(100, train)
            
        except Exception as e:
            logger.error(f"Training error: {str(e)}")
            messagebox.showerror("Error", f"Training failed: {str(e)}")
    
    def _backup_model(self):
        """Backup model file"""
        try:
            model_path = Path(Settings.MODEL_PATH)
            if not model_path.exists():
                messagebox.showwarning("Warning", "No trained model to backup")
                return
            
            backup_path = filedialog.asksaveasfilename(
                defaultextension=".xml",
                filetypes=[("XML files", "*.xml"), ("All files", "*.*")],
                initialfile=f"model_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xml"
            )
            
            if backup_path:
                import shutil
                shutil.copy2(model_path, backup_path)
                messagebox.showinfo("Success", f"Model backed up to:\n{backup_path}")
                
        except Exception as e:
            logger.error(f"Backup error: {str(e)}")
            messagebox.showerror("Error", f"Backup failed: {str(e)}")
    
    def _restore_model(self):
        """Restore model from backup"""
        try:
            backup_path = filedialog.askopenfilename(
                filetypes=[("XML files", "*.xml"), ("All files", "*.*")],
                title="Select model backup file"
            )
            
            if backup_path:
                import shutil
                shutil.copy2(backup_path, Settings.MODEL_PATH)
                messagebox.showinfo("Success", "Model restored successfully!")
                self._setup_model_tab()  # Refresh model info
                
        except Exception as e:
            logger.error(f"Restore error: {str(e)}")
            messagebox.showerror("Error", f"Restore failed: {str(e)}")
