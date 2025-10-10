"""
Camera Interface - Supports both USB webcam and Raspberry Pi Camera
"""

import cv2
import numpy as np
from typing import Optional, Tuple
import logging

from config.settings import Settings

logger = logging.getLogger(__name__)


class Camera:
    """Camera interface for capturing images"""
    
    def __init__(self, camera_type: Optional[str] = None, camera_index: int = 0):
        """
        Initialize camera
        
        Args:
            camera_type: 'USB' or 'PICAMERA' (defaults to Settings.CAMERA_TYPE)
            camera_index: Camera index for USB cameras
        """
        self.camera_type = camera_type or Settings.CAMERA_TYPE
        self.camera_index = camera_index
        self.cap = None
        self.is_opened = False
        
        # For Raspberry Pi Camera
        self.picamera = None
        self.picamera_array = None
    
    def open(self) -> bool:
        """
        Open camera connection
        
        Returns:
            bool: True if successful
        """
        try:
            if self.camera_type == 'PICAMERA':
                return self._open_picamera()
            else:
                return self._open_usb_camera()
        except Exception as e:
            logger.error(f"Failed to open camera: {str(e)}")
            return False
    
    def _open_usb_camera(self) -> bool:
        """Open USB webcam"""
        try:
            self.cap = cv2.VideoCapture(self.camera_index)
            
            if not self.cap.isOpened():
                logger.error(f"Failed to open USB camera at index {self.camera_index}")
                return False
            
            # Set camera properties
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, Settings.CAMERA_WIDTH)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, Settings.CAMERA_HEIGHT)
            self.cap.set(cv2.CAP_PROP_FPS, Settings.CAMERA_FPS)
            
            self.is_opened = True
            logger.info(f"USB camera opened successfully (index: {self.camera_index})")
            return True
            
        except Exception as e:
            logger.error(f"Error opening USB camera: {str(e)}")
            return False
    
    def _open_picamera(self) -> bool:
        """Open Raspberry Pi Camera"""
        try:
            from picamera import PiCamera
            from picamera.array import PiRGBArray
            import time
            
            self.picamera = PiCamera()
            self.picamera.resolution = (Settings.CAMERA_WIDTH, Settings.CAMERA_HEIGHT)
            self.picamera.framerate = Settings.CAMERA_FPS
            
            # Allow camera to warm up
            time.sleep(0.1)
            
            self.picamera_array = PiRGBArray(self.picamera, size=(Settings.CAMERA_WIDTH, Settings.CAMERA_HEIGHT))
            
            self.is_opened = True
            logger.info("Raspberry Pi camera opened successfully")
            return True
            
        except ImportError:
            logger.error("picamera module not found. Install with: pip install picamera")
            return False
        except Exception as e:
            logger.error(f"Error opening Raspberry Pi camera: {str(e)}")
            return False
    
    def read(self) -> Tuple[bool, Optional[np.ndarray]]:
        """
        Read a frame from camera
        
        Returns:
            tuple: (success, frame)
        """
        if not self.is_opened:
            return False, None
        
        try:
            if self.camera_type == 'PICAMERA':
                return self._read_picamera()
            else:
                return self._read_usb_camera()
        except Exception as e:
            logger.error(f"Error reading frame: {str(e)}")
            return False, None
    
    def _read_usb_camera(self) -> Tuple[bool, Optional[np.ndarray]]:
        """Read frame from USB camera"""
        if self.cap is None or not self.cap.isOpened():
            return False, None
        
        ret, frame = self.cap.read()
        return ret, frame
    
    def _read_picamera(self) -> Tuple[bool, Optional[np.ndarray]]:
        """Read frame from Raspberry Pi camera"""
        if self.picamera is None:
            return False, None
        
        try:
            self.picamera.capture(self.picamera_array, format="bgr", use_video_port=True)
            frame = self.picamera_array.array
            self.picamera_array.truncate(0)  # Clear for next capture
            return True, frame
        except Exception as e:
            logger.error(f"Error capturing from Pi camera: {str(e)}")
            return False, None
    
    def release(self):
        """Release camera resources"""
        try:
            if self.camera_type == 'PICAMERA' and self.picamera is not None:
                self.picamera.close()
                self.picamera = None
                self.picamera_array = None
            elif self.cap is not None:
                self.cap.release()
                self.cap = None
            
            self.is_opened = False
            logger.info("Camera released")
            
        except Exception as e:
            logger.error(f"Error releasing camera: {str(e)}")
    
    def get_frame_size(self) -> Tuple[int, int]:
        """
        Get current frame size
        
        Returns:
            tuple: (width, height)
        """
        if self.camera_type == 'PICAMERA' and self.picamera is not None:
            return self.picamera.resolution
        elif self.cap is not None and self.cap.isOpened():
            width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            return (width, height)
        else:
            return (Settings.CAMERA_WIDTH, Settings.CAMERA_HEIGHT)
    
    def is_available(self) -> bool:
        """Check if camera is available and opened"""
        return self.is_opened
    
    def __enter__(self):
        """Context manager entry"""
        self.open()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.release()
    
    def __del__(self):
        """Destructor"""
        self.release()


def test_camera():
    """Test camera functionality"""
    print("Testing camera...")
    
    with Camera() as camera:
        if not camera.is_available():
            print("✗ Camera not available")
            return False
        
        print("✓ Camera opened successfully")
        print(f"  Frame size: {camera.get_frame_size()}")
        
        # Try to capture a few frames
        for i in range(5):
            ret, frame = camera.read()
            if ret:
                print(f"✓ Frame {i+1} captured: {frame.shape}")
            else:
                print(f"✗ Failed to capture frame {i+1}")
                return False
        
        print("\n✓ Camera test passed!")
        return True


if __name__ == '__main__':
    test_camera()
