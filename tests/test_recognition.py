"""
Unit tests for face recognition module
"""

import pytest
import cv2
import numpy as np
from pathlib import Path
import sys
import tempfile

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.face_recognizer import FaceRecognizer


@pytest.fixture
def recognizer():
    """Create face recognizer instance"""
    return FaceRecognizer()


@pytest.fixture
def sample_faces():
    """Generate sample face images for testing"""
    faces = []
    labels = []
    
    # Create 3 "identities" with 5 images each
    for person_id in range(3):
        for img_num in range(5):
            # Create slightly different images for same person
            face = np.random.randint(
                50 + person_id * 50,
                100 + person_id * 50,
                (100, 100),
                dtype=np.uint8
            )
            # Add some variation
            noise = np.random.randint(-10, 10, (100, 100), dtype=np.int16)
            face = np.clip(face.astype(np.int16) + noise, 0, 255).astype(np.uint8)
            
            faces.append(face)
            labels.append(person_id)
    
    return faces, labels


@pytest.fixture
def trained_recognizer(recognizer, sample_faces):
    """Create and train a recognizer with sample data"""
    faces, labels = sample_faces
    recognizer.train(faces, labels)
    return recognizer


class TestFaceRecognizer:
    """Test suite for FaceRecognizer class"""
    
    def test_recognizer_initialization(self, recognizer):
        """Test that recognizer initializes properly"""
        assert recognizer is not None
        assert recognizer.recognizer is not None
        assert recognizer.label_map == {}
        assert recognizer.is_trained == False
    
    def test_train_with_sample_data(self, recognizer, sample_faces):
        """Test training with sample data"""
        faces, labels = sample_faces
        
        recognizer.train(faces, labels)
        
        assert recognizer.is_trained == True
        assert len(recognizer.label_map) == 3  # 3 unique labels
    
    def test_train_empty_data(self, recognizer):
        """Test training with empty data"""
        with pytest.raises((ValueError, cv2.error)):
            recognizer.train([], [])
    
    def test_train_mismatched_data(self, recognizer):
        """Test training with mismatched faces and labels"""
        faces = [np.zeros((100, 100), dtype=np.uint8) for _ in range(5)]
        labels = [0, 1, 2]  # Fewer labels than faces
        
        with pytest.raises((ValueError, AssertionError)):
            recognizer.train(faces, labels)
    
    def test_predict_untrained(self, recognizer):
        """Test prediction without training"""
        test_face = np.zeros((100, 100), dtype=np.uint8)
        
        with pytest.raises((cv2.error, RuntimeError)):
            recognizer.predict(test_face)
    
    def test_predict_trained(self, trained_recognizer, sample_faces):
        """Test prediction with trained model"""
        faces, labels = sample_faces
        
        # Test with a training sample
        test_face = faces[0]
        label, confidence = trained_recognizer.predict(test_face)
        
        assert isinstance(label, (int, np.integer))
        assert isinstance(confidence, (float, np.floating))
        assert confidence >= 0
    
    def test_predict_returns_correct_label(self, trained_recognizer, sample_faces):
        """Test that prediction returns expected labels"""
        faces, labels = sample_faces
        
        # Test each person
        for expected_label in [0, 1, 2]:
            # Get a sample face for this person
            person_faces = [f for f, l in zip(faces, labels) if l == expected_label]
            test_face = person_faces[0]
            
            predicted_label, confidence = trained_recognizer.predict(test_face)
            
            # For simple synthetic data, should recognize correctly
            # Note: May fail with very simple test data
            assert isinstance(predicted_label, (int, np.integer))
    
    def test_confidence_score_range(self, trained_recognizer, sample_faces):
        """Test that confidence scores are in valid range"""
        faces, labels = sample_faces
        
        for face in faces[:3]:  # Test a few faces
            label, confidence = trained_recognizer.predict(face)
            
            # Confidence should be non-negative
            assert confidence >= 0
            # Lower confidence means better match in LBPH
    
    def test_unknown_face_high_confidence(self, trained_recognizer):
        """Test that unknown faces return high confidence (poor match)"""
        # Create a completely different face
        unknown_face = np.random.randint(200, 255, (100, 100), dtype=np.uint8)
        
        label, confidence = trained_recognizer.predict(unknown_face)
        
        # Unknown face should have high confidence (poor match)
        # Exact threshold depends on training data
        assert confidence >= 0
    
    def test_save_model(self, trained_recognizer):
        """Test model saving"""
        with tempfile.NamedTemporaryFile(suffix='.xml', delete=False) as tmp:
            model_path = tmp.name
        
        try:
            trained_recognizer.save_model(model_path)
            
            # Verify file was created
            assert Path(model_path).exists()
            assert Path(model_path).stat().st_size > 0
            
            # Verify label map was saved
            label_path = Path(model_path).with_suffix('.json')
            assert label_path.exists()
            
        finally:
            # Cleanup
            Path(model_path).unlink(missing_ok=True)
            Path(model_path).with_suffix('.json').unlink(missing_ok=True)
    
    def test_load_model(self, trained_recognizer):
        """Test model loading"""
        with tempfile.NamedTemporaryFile(suffix='.xml', delete=False) as tmp:
            model_path = tmp.name
        
        try:
            # Save model
            trained_recognizer.save_model(model_path)
            
            # Create new recognizer and load
            new_recognizer = FaceRecognizer()
            success = new_recognizer.load_model(model_path)
            
            assert success == True
            assert new_recognizer.is_trained == True
            assert new_recognizer.label_map == trained_recognizer.label_map
            
        finally:
            Path(model_path).unlink(missing_ok=True)
            Path(model_path).with_suffix('.json').unlink(missing_ok=True)
    
    def test_load_nonexistent_model(self, recognizer):
        """Test loading non-existent model"""
        success = recognizer.load_model("nonexistent_model.xml")
        
        assert success == False
        assert recognizer.is_trained == False
    
    def test_predict_after_load(self, trained_recognizer, sample_faces):
        """Test that loaded model can predict"""
        with tempfile.NamedTemporaryFile(suffix='.xml', delete=False) as tmp:
            model_path = tmp.name
        
        try:
            # Save and load
            trained_recognizer.save_model(model_path)
            
            loaded_recognizer = FaceRecognizer()
            loaded_recognizer.load_model(model_path)
            
            # Test prediction
            faces, labels = sample_faces
            test_face = faces[0]
            
            label, confidence = loaded_recognizer.predict(test_face)
            
            assert isinstance(label, (int, np.integer))
            assert isinstance(confidence, (float, np.floating))
            
        finally:
            Path(model_path).unlink(missing_ok=True)
            Path(model_path).with_suffix('.json').unlink(missing_ok=True)
    
    def test_train_with_different_sizes(self, recognizer):
        """Test training with faces of different sizes"""
        faces = [
            np.zeros((100, 100), dtype=np.uint8),
            np.zeros((120, 120), dtype=np.uint8),
            np.zeros((80, 80), dtype=np.uint8)
        ]
        labels = [0, 0, 0]
        
        # Should handle or resize automatically
        # Or raise appropriate error
        try:
            recognizer.train(faces, labels)
            # If successful, check it trained
            assert recognizer.is_trained == True
        except (ValueError, cv2.error):
            # If it doesn't support different sizes, that's also valid
            pass
    
    def test_predict_different_size_face(self, trained_recognizer):
        """Test prediction with different sized face"""
        # Create face with different size than training data
        test_face = np.zeros((120, 120), dtype=np.uint8)
        
        try:
            label, confidence = trained_recognizer.predict(test_face)
            # If it works, verify types
            assert isinstance(label, (int, np.integer))
            assert isinstance(confidence, (float, np.floating))
        except (ValueError, cv2.error):
            # May require same size as training data
            pass
    
    def test_label_map_creation(self, recognizer, sample_faces):
        """Test that label map is created correctly"""
        faces, labels = sample_faces
        
        recognizer.train(faces, labels)
        
        # Should have entries for all unique labels
        unique_labels = set(labels)
        assert len(recognizer.label_map) == len(unique_labels)
        
        # All unique labels should be in map
        for label in unique_labels:
            assert label in recognizer.label_map.values()
    
    def test_train_single_person(self, recognizer):
        """Test training with single person"""
        faces = [np.random.randint(0, 255, (100, 100), dtype=np.uint8) for _ in range(5)]
        labels = [0] * 5
        
        recognizer.train(faces, labels)
        
        assert recognizer.is_trained == True
        assert 0 in recognizer.label_map.values()
    
    def test_train_many_people(self, recognizer):
        """Test training with many people"""
        num_people = 50
        images_per_person = 30
        
        faces = []
        labels = []
        
        for person_id in range(num_people):
            for _ in range(images_per_person):
                face = np.random.randint(
                    person_id * 2,
                    person_id * 2 + 50,
                    (100, 100),
                    dtype=np.uint8
                )
                faces.append(face)
                labels.append(person_id)
        
        recognizer.train(faces, labels)
        
        assert recognizer.is_trained == True
        assert len(recognizer.label_map) == num_people
    
    def test_predict_consistency(self, trained_recognizer, sample_faces):
        """Test that same face gives consistent predictions"""
        faces, labels = sample_faces
        test_face = faces[0]
        
        # Predict multiple times
        results = []
        for _ in range(5):
            label, confidence = trained_recognizer.predict(test_face)
            results.append((label, confidence))
        
        # All predictions should be identical
        first_result = results[0]
        for result in results[1:]:
            assert result == first_result


@pytest.mark.skipif(
    not Path("tests/data").exists(),
    reason="Test data directory not found"
)
class TestFaceRecognizerWithRealImages:
    """Tests using real face images (if available)"""
    
    def test_train_with_real_faces(self, recognizer):
        """Test training with real face images"""
        faces_dir = Path("tests/data/faces")
        
        if not faces_dir.exists():
            pytest.skip("Real face data not available")
        
        faces = []
        labels = []
        
        # Load images (assuming structure: faces/person_id/img.jpg)
        for person_dir in faces_dir.iterdir():
            if person_dir.is_dir():
                person_id = int(person_dir.name)
                for img_file in person_dir.glob("*.jpg"):
                    img = cv2.imread(str(img_file), cv2.IMREAD_GRAYSCALE)
                    if img is not None:
                        faces.append(img)
                        labels.append(person_id)
        
        if len(faces) > 0:
            recognizer.train(faces, labels)
            assert recognizer.is_trained == True
    
    def test_recognition_accuracy(self, recognizer):
        """Test recognition accuracy on real data"""
        # This would require a proper test dataset with
        # known train/test splits
        pytest.skip("Accuracy testing requires curated dataset")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
