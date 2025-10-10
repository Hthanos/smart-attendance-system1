"""
Face Recognizer - LBPH (Local Binary Patterns Histograms) based recognition
"""

import cv2
import numpy as np
import json
import os
from typing import List, Tuple, Optional, Dict
from pathlib import Path
import logging

from config.settings import Settings

logger = logging.getLogger(__name__)


class FaceRecognizer:
    """Face recognition using LBPH algorithm"""
    
    def __init__(self):
        """Initialize face recognizer"""
        self.recognizer = cv2.face.LBPHFaceRecognizer_create(
            radius=Settings.RECOGNITION_RADIUS,
            neighbors=Settings.RECOGNITION_NEIGHBORS,
            grid_x=Settings.RECOGNITION_GRID_X,
            grid_y=Settings.RECOGNITION_GRID_Y
        )
        
        self.label_map = {}  # Map label IDs to student IDs
        self.is_trained = False
        
        self.model_path = Settings.TRAINED_MODEL_PATH
        self.label_map_path = Settings.LABEL_MAP_PATH
    
    def train(
        self, 
        faces: List[np.ndarray], 
        labels: List[int],
        student_ids: Optional[List[int]] = None
    ) -> bool:
        """
        Train recognizer with face images and labels
        
        Args:
            faces: List of face images (grayscale)
            labels: List of corresponding labels (0, 1, 2, ...)
            student_ids: Optional list of actual student IDs
        
        Returns:
            bool: True if training successful
        """
        if len(faces) == 0 or len(labels) == 0:
            logger.error("No training data provided")
            return False
        
        if len(faces) != len(labels):
            logger.error("Number of faces and labels must match")
            return False
        
        try:
            # Train the recognizer
            self.recognizer.train(faces, np.array(labels))
            
            # Create label map
            if student_ids and len(student_ids) == len(set(labels)):
                unique_labels = sorted(set(labels))
                unique_student_ids = sorted(set(student_ids))
                self.label_map = {label: sid for label, sid in zip(unique_labels, unique_student_ids)}
            else:
                self.label_map = {label: label for label in set(labels)}
            
            self.is_trained = True
            logger.info(f"Training completed with {len(faces)} images, {len(set(labels))} unique labels")
            return True
            
        except Exception as e:
            logger.error(f"Training failed: {str(e)}")
            return False
    
    def predict(
        self, 
        face: np.ndarray
    ) -> Tuple[Optional[int], float]:
        """
        Predict identity of a face
        
        Args:
            face: Face image (grayscale)
        
        Returns:
            tuple: (student_id, confidence) or (None, 0) if not recognized
        """
        if not self.is_trained:
            logger.error("Recognizer not trained")
            return None, 0.0
        
        try:
            label, confidence = self.recognizer.predict(face)
            
            # Lower confidence value = better match (distance metric)
            # Check if confidence is below threshold
            if confidence > Settings.RECOGNITION_THRESHOLD:
                return None, confidence
            
            # Map label to student ID
            student_id = self.label_map.get(label, None)
            
            return student_id, confidence
            
        except Exception as e:
            logger.error(f"Prediction failed: {str(e)}")
            return None, 0.0
    
    def predict_batch(
        self, 
        faces: List[np.ndarray]
    ) -> List[Tuple[Optional[int], float]]:
        """
        Predict identities for multiple faces
        
        Args:
            faces: List of face images
        
        Returns:
            List of (student_id, confidence) tuples
        """
        return [self.predict(face) for face in faces]
    
    def save_model(self, model_path: Optional[str] = None) -> bool:
        """
        Save trained model to file
        
        Args:
            model_path: Path to save model (uses default if None)
        
        Returns:
            bool: True if successful
        """
        if not self.is_trained:
            logger.error("Cannot save untrained model")
            return False
        
        model_path = model_path or self.model_path
        label_map_path = model_path.replace('.yml', '_labels.json')
        
        try:
            # Ensure directory exists
            Path(model_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Save model
            self.recognizer.save(model_path)
            
            # Save label map
            with open(label_map_path, 'w') as f:
                json.dump(self.label_map, f, indent=2)
            
            logger.info(f"Model saved to: {model_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save model: {str(e)}")
            return False
    
    def load_model(self, model_path: Optional[str] = None) -> bool:
        """
        Load trained model from file
        
        Args:
            model_path: Path to model file (uses default if None)
        
        Returns:
            bool: True if successful
        """
        model_path = model_path or self.model_path
        label_map_path = model_path.replace('.yml', '_labels.json')
        
        if not os.path.exists(model_path):
            logger.error(f"Model file not found: {model_path}")
            return False
        
        try:
            # Load model
            self.recognizer.read(model_path)
            
            # Load label map
            if os.path.exists(label_map_path):
                with open(label_map_path, 'r') as f:
                    # JSON keys are strings, convert to int
                    label_map_str = json.load(f)
                    self.label_map = {int(k): v for k, v in label_map_str.items()}
            else:
                logger.warning("Label map file not found, using default mapping")
                self.label_map = {}
            
            self.is_trained = True
            logger.info(f"Model loaded from: {model_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load model: {str(e)}")
            return False
    
    def update_model(
        self, 
        new_faces: List[np.ndarray], 
        new_labels: List[int]
    ) -> bool:
        """
        Update existing model with new training data
        
        Args:
            new_faces: New face images
            new_labels: Corresponding labels
        
        Returns:
            bool: True if successful
        """
        if not self.is_trained:
            logger.error("Cannot update untrained model")
            return False
        
        try:
            self.recognizer.update(new_faces, np.array(new_labels))
            logger.info(f"Model updated with {len(new_faces)} new images")
            return True
            
        except Exception as e:
            logger.error(f"Model update failed: {str(e)}")
            return False
    
    def get_confidence_percentage(self, confidence: float) -> float:
        """
        Convert confidence score to percentage
        Lower confidence = higher match percentage
        
        Args:
            confidence: Raw confidence score
        
        Returns:
            float: Confidence percentage (0-100)
        """
        # LBPH confidence is a distance metric (lower is better)
        # Normalize to percentage
        max_distance = Settings.RECOGNITION_THRESHOLD * 2
        percentage = max(0, 100 - (confidence / max_distance * 100))
        return round(percentage, 2)
    
    def get_num_trained_labels(self) -> int:
        """Get number of unique labels in trained model"""
        return len(self.label_map)


def test_face_recognizer():
    """Test face recognizer"""
    print("Testing Face Recognizer...")
    
    recognizer = FaceRecognizer()
    print("✓ Recognizer initialized")
    
    # Create dummy training data
    faces = []
    labels = []
    
    for i in range(3):  # 3 students
        for j in range(10):  # 10 images each
            # Create dummy face image
            face = np.random.randint(0, 256, (200, 200), dtype=np.uint8)
            faces.append(face)
            labels.append(i)
    
    print(f"✓ Created {len(faces)} dummy face images")
    
    # Train
    success = recognizer.train(faces, labels, student_ids=[101, 102, 103])
    
    if success:
        print("✓ Training successful")
        print(f"  Trained labels: {recognizer.get_num_trained_labels()}")
        print(f"  Label map: {recognizer.label_map}")
    else:
        print("✗ Training failed")
        return False
    
    # Test prediction
    test_face = faces[0]
    student_id, confidence = recognizer.predict(test_face)
    print(f"✓ Prediction: Student ID={student_id}, Confidence={confidence:.2f}")
    print(f"  Confidence %: {recognizer.get_confidence_percentage(confidence):.2f}%")
    
    # Test save/load
    import tempfile
    with tempfile.NamedTemporaryFile(suffix='.yml', delete=False) as f:
        temp_path = f.name
    
    if recognizer.save_model(temp_path):
        print(f"✓ Model saved to {temp_path}")
        
        # Load in new instance
        recognizer2 = FaceRecognizer()
        if recognizer2.load_model(temp_path):
            print("✓ Model loaded successfully")
        else:
            print("✗ Model loading failed")
            return False
    else:
        print("✗ Model saving failed")
        return False
    
    # Cleanup
    try:
        os.remove(temp_path)
        os.remove(temp_path.replace('.yml', '_labels.json'))
    except:
        pass
    
    print("\n✓ All face recognizer tests passed!")
    return True


if __name__ == '__main__':
    test_face_recognizer()
