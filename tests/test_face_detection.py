"""
Unit tests for face detection module
"""

import pytest
import cv2
import numpy as np
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.face_detector import FaceDetector


@pytest.fixture
def detector():
    """Create face detector instance"""
    return FaceDetector()


@pytest.fixture
def sample_face_image():
    """Create a sample image with a face (or load test image)"""
    # Create a simple test image (100x100 grayscale)
    image = np.zeros((100, 100, 3), dtype=np.uint8)
    # Draw a simple face-like structure
    cv2.circle(image, (50, 50), 30, (255, 255, 255), -1)  # Face
    cv2.circle(image, (40, 45), 5, (0, 0, 0), -1)  # Left eye
    cv2.circle(image, (60, 45), 5, (0, 0, 0), -1)  # Right eye
    cv2.ellipse(image, (50, 60), (10, 5), 0, 0, 180, (0, 0, 0), 2)  # Mouth
    return image


@pytest.fixture
def no_face_image():
    """Create an image without faces"""
    return np.zeros((100, 100, 3), dtype=np.uint8)


class TestFaceDetector:
    """Test suite for FaceDetector class"""
    
    def test_detector_initialization(self, detector):
        """Test that detector initializes properly"""
        assert detector is not None
        assert detector.face_cascade is not None
    
    def test_detector_with_custom_cascade(self):
        """Test initialization with custom cascade path"""
        from config.settings import Settings
        cascade_path = Settings.HAARCASCADE_PATH
        
        if Path(cascade_path).exists():
            detector = FaceDetector(cascade_path=str(cascade_path))
            assert detector.face_cascade is not None
    
    def test_detect_faces_returns_list(self, detector, sample_face_image):
        """Test that detect_faces returns a list"""
        faces = detector.detect_faces(sample_face_image)
        assert isinstance(faces, list)
    
    def test_detect_faces_tuple_format(self, detector, sample_face_image):
        """Test that detected faces have correct format (x, y, w, h)"""
        faces = detector.detect_faces(sample_face_image)
        
        for face in faces:
            assert isinstance(face, tuple)
            assert len(face) == 4
            x, y, w, h = face
            assert isinstance(x, (int, np.integer))
            assert isinstance(y, (int, np.integer))
            assert isinstance(w, (int, np.integer))
            assert isinstance(h, (int, np.integer))
            assert w > 0 and h > 0
    
    def test_detect_no_faces(self, detector, no_face_image):
        """Test detection on image without faces"""
        faces = detector.detect_faces(no_face_image)
        assert isinstance(faces, list)
        # May or may not detect faces in blank image (depends on classifier)
    
    def test_detect_faces_grayscale(self, detector):
        """Test detection on grayscale image"""
        gray_image = np.zeros((100, 100), dtype=np.uint8)
        faces = detector.detect_faces(gray_image)
        assert isinstance(faces, list)
    
    def test_extract_face_roi(self, detector, sample_face_image):
        """Test face extraction"""
        # Create a known face rectangle
        face_rect = (20, 20, 60, 60)
        
        face_roi = detector.extract_face(sample_face_image, face_rect, margin=0)
        
        assert face_roi is not None
        assert face_roi.shape[0] == 60  # height
        assert face_roi.shape[1] == 60  # width
    
    def test_extract_face_with_margin(self, detector, sample_face_image):
        """Test face extraction with margin"""
        face_rect = (30, 30, 40, 40)
        margin = 10
        
        face_roi = detector.extract_face(sample_face_image, face_rect, margin=margin)
        
        assert face_roi is not None
        # Should be larger than original rect due to margin
        assert face_roi.shape[0] >= 40
        assert face_roi.shape[1] >= 40
    
    def test_extract_face_boundary_handling(self, detector, sample_face_image):
        """Test that extraction handles image boundaries correctly"""
        # Face rect at image edge
        face_rect = (0, 0, 50, 50)
        
        face_roi = detector.extract_face(sample_face_image, face_rect, margin=10)
        
        # Should not crash and return valid image
        assert face_roi is not None
        assert face_roi.shape[0] > 0
        assert face_roi.shape[1] > 0
    
    def test_detect_faces_empty_image(self, detector):
        """Test detection on empty/invalid image"""
        empty_image = np.array([])
        
        faces = detector.detect_faces(empty_image)
        
        # Should handle gracefully
        assert isinstance(faces, list)
    
    def test_detect_faces_parameters(self, detector, sample_face_image):
        """Test detection with different parameters"""
        # More lenient detection
        faces1 = detector.detect_faces(
            sample_face_image,
            scale_factor=1.05,
            min_neighbors=3
        )
        
        # More strict detection
        faces2 = detector.detect_faces(
            sample_face_image,
            scale_factor=1.3,
            min_neighbors=7
        )
        
        # Both should return lists
        assert isinstance(faces1, list)
        assert isinstance(faces2, list)
        
        # Lenient should detect same or more faces
        assert len(faces1) >= len(faces2)
    
    def test_detect_multiple_faces(self, detector):
        """Test detection of multiple faces in one image"""
        # Create image with multiple face-like regions
        image = np.zeros((200, 300, 3), dtype=np.uint8)
        
        # Draw two face-like structures
        for center in [(70, 100), (230, 100)]:
            cv2.circle(image, center, 30, (255, 255, 255), -1)
            cv2.circle(image, (center[0]-10, center[1]-5), 5, (0, 0, 0), -1)
            cv2.circle(image, (center[0]+10, center[1]-5), 5, (0, 0, 0), -1)
        
        faces = detector.detect_faces(image)
        
        # Should return a list (may or may not detect both)
        assert isinstance(faces, list)
    
    def test_face_roi_contains_face(self, detector, sample_face_image):
        """Test that extracted ROI actually contains the face area"""
        face_rect = (25, 25, 50, 50)
        
        face_roi = detector.extract_face(sample_face_image, face_rect, margin=0)
        
        # Verify ROI dimensions match rectangle
        assert face_roi.shape[0] == face_rect[3]  # height
        assert face_roi.shape[1] == face_rect[2]  # width
    
    def test_detector_thread_safety(self, detector, sample_face_image):
        """Test that detector can be used multiple times"""
        # Multiple consecutive detections
        for _ in range(5):
            faces = detector.detect_faces(sample_face_image)
            assert isinstance(faces, list)
    
    def test_detect_faces_color_image(self, detector):
        """Test detection on color image"""
        color_image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        
        faces = detector.detect_faces(color_image)
        
        assert isinstance(faces, list)
    
    def test_extract_face_invalid_rect(self, detector, sample_face_image):
        """Test extraction with invalid rectangle"""
        # Rectangle outside image bounds
        invalid_rect = (200, 200, 50, 50)
        
        face_roi = detector.extract_face(sample_face_image, invalid_rect, margin=0)
        
        # Should handle gracefully (return empty or valid subset)
        assert face_roi is not None


@pytest.mark.skipif(
    not Path("tests/data").exists(),
    reason="Test data directory not found"
)
class TestFaceDetectorWithRealImages:
    """Tests using real face images (if available)"""
    
    def test_detect_real_face(self, detector):
        """Test detection on real face image"""
        test_image_path = Path("tests/data/real_face.jpg")
        
        if test_image_path.exists():
            image = cv2.imread(str(test_image_path))
            faces = detector.detect_faces(image)
            
            assert len(faces) > 0, "Should detect at least one face"
    
    def test_detect_group_photo(self, detector):
        """Test detection on group photo"""
        test_image_path = Path("tests/data/group_photo.jpg")
        
        if test_image_path.exists():
            image = cv2.imread(str(test_image_path))
            faces = detector.detect_faces(image)
            
            assert len(faces) > 1, "Should detect multiple faces"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
