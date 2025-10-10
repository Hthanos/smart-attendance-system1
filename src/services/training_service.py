"""
Training Service - Handles model training workflow
"""

import os
import cv2
import numpy as np
from pathlib import Path
from typing import List, Tuple, Optional
import logging
from datetime import datetime

from src.core.face_recognizer import FaceRecognizer
from src.core.image_processor import ImageProcessor
from src.services.student_service import StudentService
from config.settings import Settings

logger = logging.getLogger(__name__)


class TrainingService:
    """Handles facial recognition model training"""
    
    def __init__(self):
        """Initialize training service"""
        self.recognizer = FaceRecognizer()
        self.image_processor = ImageProcessor()
        self.student_service = StudentService()
    
    def load_training_data(self) -> Tuple[List[np.ndarray], List[int], List[int]]:
        """
        Load all student face images for training
        
        Returns:
            tuple: (faces, labels, student_ids)
        """
        faces = []
        labels = []
        student_ids = []
        
        students = self.student_service.get_all_students()
        label_counter = 0
        
        for student in students:
            reg_number = student['registration_number']
            student_id = student['id']
            
            # Get student images
            image_paths = self.student_service.get_student_images(reg_number)
            
            if len(image_paths) < Settings.IMAGES_PER_STUDENT:
                logger.warning(f"Student {reg_number} has only {len(image_paths)} images (need {Settings.IMAGES_PER_STUDENT})")
                continue
            
            # Load and process images
            for img_path in image_paths:
                img = cv2.imread(str(img_path), cv2.IMREAD_GRAYSCALE)
                if img is not None:
                    # Preprocess
                    processed = self.image_processor.preprocess_face(img)
                    faces.append(processed)
                    labels.append(label_counter)
            
            if len(image_paths) > 0:
                student_ids.append(student_id)
                label_counter += 1
                logger.info(f"Loaded {len(image_paths)} images for {reg_number}")
        
        return faces, labels, student_ids
    
    def train_model(self) -> bool:
        """
        Train the facial recognition model
        
        Returns:
            bool: True if successful
        """
        try:
            logger.info("Starting model training...")
            
            # Load training data
            faces, labels, student_ids = self.load_training_data()
            
            if len(faces) == 0:
                logger.error("No training data available")
                return False
            
            logger.info(f"Training with {len(faces)} images from {len(set(labels))} students")
            
            # Train recognizer
            success = self.recognizer.train(faces, labels, student_ids)
            
            if not success:
                return False
            
            # Save model
            if self.recognizer.save_model():
                logger.info("Model trained and saved successfully")
                return True
            else:
                logger.error("Failed to save model")
                return False
                
        except Exception as e:
            logger.error(f"Training failed: {str(e)}")
            return False
    
    def load_trained_model(self) -> bool:
        """Load existing trained model"""
        return self.recognizer.load_model()
    
    def is_model_trained(self) -> bool:
        """Check if model is trained and loaded"""
        return self.recognizer.is_trained
    
    def get_recognizer(self) -> FaceRecognizer:
        """Get the recognizer instance"""
        return self.recognizer
