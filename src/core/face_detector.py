"""
Face Detector - Haar Cascade based face detection
"""

import cv2
import numpy as np
from typing import List, Tuple, Optional
import logging

from config.settings import Settings

logger = logging.getLogger(__name__)


class FaceDetector:
    """Face detection using Haar Cascade Classifier"""
    
    def __init__(self, cascade_path: Optional[str] = None):
        """
        Initialize face detector
        
        Args:
            cascade_path: Path to Haar Cascade XML file
        """
        self.cascade_path = cascade_path or Settings.HAAR_CASCADE_PATH
        self.face_cascade = None
        self.is_loaded = False
        
        self._load_cascade()
    
    def _load_cascade(self) -> bool:
        """Load Haar Cascade classifier"""
        try:
            self.face_cascade = cv2.CascadeClassifier(self.cascade_path)
            
            if self.face_cascade.empty():
                logger.error(f"Failed to load Haar Cascade from: {self.cascade_path}")
                return False
            
            self.is_loaded = True
            logger.info("Face detector initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error loading Haar Cascade: {str(e)}")
            return False
    
    def detect_faces(
        self, 
        image: np.ndarray,
        scale_factor: Optional[float] = None,
        min_neighbors: Optional[int] = None,
        min_size: Optional[Tuple[int, int]] = None
    ) -> List[Tuple[int, int, int, int]]:
        """
        Detect faces in an image
        
        Args:
            image: Input image (BGR or grayscale)
            scale_factor: Parameter specifying how much the image size is reduced
            min_neighbors: Parameter specifying how many neighbors each candidate rectangle should have
            min_size: Minimum possible object size (width, height)
        
        Returns:
            List of face bounding boxes as (x, y, width, height)
        """
        if not self.is_loaded:
            logger.error("Face detector not initialized")
            return []
        
        # Use defaults from settings if not provided
        scale_factor = scale_factor or Settings.SCALE_FACTOR
        min_neighbors = min_neighbors or Settings.MIN_NEIGHBORS
        min_size = min_size or (Settings.MIN_FACE_SIZE, Settings.MIN_FACE_SIZE)
        
        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Detect faces
        try:
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=scale_factor,
                minNeighbors=min_neighbors,
                minSize=min_size,
                flags=cv2.CASCADE_SCALE_IMAGE
            )
            
            return faces.tolist() if len(faces) > 0 else []
            
        except Exception as e:
            logger.error(f"Error detecting faces: {str(e)}")
            return []
    
    def detect_largest_face(
        self, 
        image: np.ndarray,
        **kwargs
    ) -> Optional[Tuple[int, int, int, int]]:
        """
        Detect the largest face in an image
        
        Args:
            image: Input image
            **kwargs: Additional arguments for detect_faces
        
        Returns:
            Largest face bounding box as (x, y, width, height) or None
        """
        faces = self.detect_faces(image, **kwargs)
        
        if not faces:
            return None
        
        # Find largest face by area
        largest_face = max(faces, key=lambda face: face[2] * face[3])
        return largest_face
    
    def extract_face(
        self, 
        image: np.ndarray, 
        face_rect: Tuple[int, int, int, int],
        margin: int = 0
    ) -> Optional[np.ndarray]:
        """
        Extract face region from image
        
        Args:
            image: Input image
            face_rect: Face bounding box (x, y, width, height)
            margin: Additional margin around face (pixels)
        
        Returns:
            Extracted face image or None
        """
        try:
            x, y, w, h = face_rect
            
            # Add margin
            x_start = max(0, x - margin)
            y_start = max(0, y - margin)
            x_end = min(image.shape[1], x + w + margin)
            y_end = min(image.shape[0], y + h + margin)
            
            face_image = image[y_start:y_end, x_start:x_end]
            
            return face_image if face_image.size > 0 else None
            
        except Exception as e:
            logger.error(f"Error extracting face: {str(e)}")
            return None
    
    def draw_faces(
        self, 
        image: np.ndarray, 
        faces: List[Tuple[int, int, int, int]],
        color: Tuple[int, int, int] = (0, 255, 0),
        thickness: int = 2,
        label: Optional[str] = None
    ) -> np.ndarray:
        """
        Draw bounding boxes around detected faces
        
        Args:
            image: Input image
            faces: List of face bounding boxes
            color: Rectangle color (BGR)
            thickness: Rectangle line thickness
            label: Optional text label to display
        
        Returns:
            Image with drawn rectangles
        """
        output = image.copy()
        
        for i, (x, y, w, h) in enumerate(faces):
            # Draw rectangle
            cv2.rectangle(output, (x, y), (x + w, y + h), color, thickness)
            
            # Draw label if provided
            if label:
                text = f"{label} {i+1}" if len(faces) > 1 else label
                cv2.putText(
                    output, 
                    text, 
                    (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    color,
                    2
                )
        
        return output
    
    def count_faces(self, image: np.ndarray, **kwargs) -> int:
        """
        Count number of faces in an image
        
        Args:
            image: Input image
            **kwargs: Additional arguments for detect_faces
        
        Returns:
            Number of faces detected
        """
        faces = self.detect_faces(image, **kwargs)
        return len(faces)


def test_face_detector():
    """Test face detector"""
    import sys
    
    print("Testing Face Detector...")
    
    detector = FaceDetector()
    
    if not detector.is_loaded:
        print("✗ Failed to load face detector")
        return False
    
    print("✓ Face detector loaded successfully")
    
    # Try to detect faces from camera
    try:
        from .camera import Camera
        
        print("\nTesting with live camera feed (press 'q' to quit)...")
        
        with Camera() as camera:
            if not camera.is_available():
                print("✗ Camera not available")
                return False
            
            while True:
                ret, frame = camera.read()
                if not ret:
                    continue
                
                # Detect faces
                faces = detector.detect_faces(frame)
                
                # Draw faces
                output = detector.draw_faces(frame, faces, label="Face")
                
                # Display count
                cv2.putText(
                    output,
                    f"Faces: {len(faces)}",
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 255, 0),
                    2
                )
                
                cv2.imshow('Face Detection Test', output)
                
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        
        cv2.destroyAllWindows()
        print("\n✓ Face detector test completed!")
        return True
        
    except ImportError:
        print("✗ Camera module not available for testing")
        return False
    except Exception as e:
        print(f"✗ Test failed: {str(e)}")
        return False


if __name__ == '__main__':
    test_face_detector()
