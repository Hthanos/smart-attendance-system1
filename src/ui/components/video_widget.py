"""
Video Widget - Reusable video display component
"""

import tkinter as tk
from tkinter import ttk
import cv2
from PIL import Image, ImageTk
import logging

logger = logging.getLogger(__name__)


class VideoWidget(tk.Frame):
    """Reusable video display widget for camera feeds"""
    
    def __init__(self, parent, width=640, height=480, **kwargs):
        """
        Initialize video widget
        
        Args:
            parent: Parent widget
            width: Display width
            height: Display height
        """
        super().__init__(parent, **kwargs)
        
        self.display_width = width
        self.display_height = height
        
        self.camera = None
        self.is_running = False
        self.update_callback = None
        self.frame_callback = None
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup UI components"""
        # Video label
        self.video_label = tk.Label(
            self,
            text="No Video",
            bg="black",
            fg="white",
            width=self.display_width // 8,
            height=self.display_height // 16
        )
        self.video_label.pack(fill=tk.BOTH, expand=True)
        
        # Status bar
        self.status_label = tk.Label(
            self,
            text="Ready",
            font=("Arial", 9),
            fg="gray",
            anchor="w",
            padx=5
        )
        self.status_label.pack(fill=tk.X)
    
    def set_camera(self, camera):
        """Set camera source"""
        self.camera = camera
    
    def start(self):
        """Start video feed"""
        if not self.camera:
            logger.error("No camera set")
            return False
        
        if not self.camera.is_opened():
            if not self.camera.open():
                logger.error("Failed to open camera")
                return False
        
        self.is_running = True
        self._update_frame()
        return True
    
    def stop(self):
        """Stop video feed"""
        self.is_running = False
        self.video_label.config(image='', text="Stopped")
        self.status_label.config(text="Stopped")
    
    def set_update_callback(self, callback):
        """
        Set callback for frame updates
        
        Args:
            callback: Function(frame) -> processed_frame
        """
        self.update_callback = callback
    
    def set_frame_callback(self, callback):
        """
        Set callback to be called after each frame
        
        Args:
            callback: Function(frame) -> None
        """
        self.frame_callback = callback
    
    def _update_frame(self):
        """Update video frame"""
        if not self.is_running or not self.camera:
            return
        
        try:
            ret, frame = self.camera.read()
            
            if ret:
                # Apply callback if set
                if self.update_callback:
                    try:
                        frame = self.update_callback(frame)
                    except Exception as e:
                        logger.error(f"Update callback error: {str(e)}")
                
                # Convert and display
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame_rgb)
                img = img.resize(
                    (self.display_width, self.display_height),
                    Image.Resampling.LANCZOS
                )
                photo = ImageTk.PhotoImage(image=img)
                
                self.video_label.config(image=photo, text='')
                self.video_label.image = photo
                
                # Call frame callback if set
                if self.frame_callback:
                    try:
                        self.frame_callback(frame)
                    except Exception as e:
                        logger.error(f"Frame callback error: {str(e)}")
                
                # Update status
                fps = self.camera.get_fps()
                self.status_label.config(
                    text=f"FPS: {fps:.1f}" if fps else "Running"
                )
            else:
                logger.warning("Failed to read frame")
                self.status_label.config(text="Read error", fg="red")
            
        except Exception as e:
            logger.error(f"Frame update error: {str(e)}")
            self.status_label.config(text=f"Error: {str(e)}", fg="red")
        
        # Schedule next update
        if self.is_running:
            self.after(33, self._update_frame)  # ~30 FPS
    
    def get_current_frame(self):
        """Get current frame from camera"""
        if self.camera:
            ret, frame = self.camera.read()
            if ret:
                return frame
        return None
    
    def display_frame(self, frame):
        """Display a specific frame"""
        try:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)
            img = img.resize(
                (self.display_width, self.display_height),
                Image.Resampling.LANCZOS
            )
            photo = ImageTk.PhotoImage(image=img)
            
            self.video_label.config(image=photo, text='')
            self.video_label.image = photo
            
        except Exception as e:
            logger.error(f"Display frame error: {str(e)}")
    
    def set_status(self, message, color="gray"):
        """Set status message"""
        self.status_label.config(text=message, fg=color)
    
    def destroy(self):
        """Cleanup before destroying"""
        self.stop()
        super().destroy()


class VideoRecorder:
    """Video recording utility"""
    
    def __init__(self, output_path, fps=20.0, frame_size=(640, 480)):
        """
        Initialize video recorder
        
        Args:
            output_path: Output video file path
            fps: Frames per second
            frame_size: (width, height)
        """
        self.output_path = output_path
        self.fps = fps
        self.frame_size = frame_size
        
        self.writer = None
        self.is_recording = False
    
    def start(self):
        """Start recording"""
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        self.writer = cv2.VideoWriter(
            self.output_path,
            fourcc,
            self.fps,
            self.frame_size
        )
        
        if self.writer.isOpened():
            self.is_recording = True
            logger.info(f"Started recording to {self.output_path}")
            return True
        else:
            logger.error("Failed to start recording")
            return False
    
    def write_frame(self, frame):
        """Write frame to video"""
        if self.is_recording and self.writer:
            # Resize if needed
            if frame.shape[:2][::-1] != self.frame_size:
                frame = cv2.resize(frame, self.frame_size)
            
            self.writer.write(frame)
    
    def stop(self):
        """Stop recording"""
        if self.writer:
            self.writer.release()
            self.is_recording = False
            logger.info(f"Recording saved to {self.output_path}")
    
    def __enter__(self):
        """Context manager entry"""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.stop()
