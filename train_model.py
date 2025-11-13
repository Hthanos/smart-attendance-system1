#!/usr/bin/env python3
"""
Train the face recognition model using student face images
"""

import sys
import os
from pathlib import Path
import cv2
import numpy as np
import json
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.core.face_recognizer import FaceRecognizer
from src.core.image_processor import ImageProcessor
from src.database.operations import DatabaseOperations


def load_training_data():
    """Load face images from data/faces directory"""
    print("\n" + "="*60)
    print("LOADING TRAINING DATA")
    print("="*60)
    
    faces_dir = Path('data/faces')
    ops = DatabaseOperations()
    
    # Get all students from database
    students = ops.get_all_students()
    if not students:
        print("❌ No students found in database!")
        print("   Run: python initialize_system.py first")
        return None, None, None
    
    print(f"\nFound {len(students)} students in database")
    
    # Create mapping of registration numbers to student IDs (handle both 'id' and 'student_id')
    reg_to_id = {s['registration_number']: s.get('id', s.get('student_id')) for s in students}
    
    faces = []
    labels = []
    label_mapping = {}
    label_counter = 0
    
    # Process each student directory
    for student_dir in faces_dir.iterdir():
        if not student_dir.is_dir() or student_dir.name == 'README.md':
            continue
        
        # Convert directory name to registration number
        # E028-01-1303-2020 -> E028-01-1303/2020
        dir_name = student_dir.name
        
        # Try different format variations
        possible_formats = [
            dir_name.replace('-2020', '/2020'),
            dir_name.replace('-2022', '/2022'),
            dir_name.replace('-2023', '/2023'),
            dir_name.replace('-2024', '/2024'),
            dir_name.replace(' 20222', '/2022'),  # Handle space typo
            dir_name.replace(' 2020', '/2020'),
        ]
        
        reg_number = None
        for format_try in possible_formats:
            if format_try in reg_to_id:
                reg_number = format_try
                break
        
        if not reg_number:
            print(f"⚠️  Directory '{dir_name}' doesn't match any student in database")
            print(f"   Tried formats: {possible_formats[:3]}")
            continue
        
        # Assign label
        label_mapping[label_counter] = reg_number
        
        # Load images
        image_files = list(student_dir.glob('*.jpg')) + \
                     list(student_dir.glob('*.jpeg')) + \
                     list(student_dir.glob('*.png'))
        
        if len(image_files) < 7:
            print(f"⚠️  {reg_number}: Only {len(image_files)} images (minimum 7 required) - SKIPPING")
            continue
        elif len(image_files) < 10:
            print(f"⚠️  {reg_number}: Only {len(image_files)} images (10+ recommended)")
        
        loaded_count = 0
        for img_path in image_files:
            try:
                # Load image
                img = cv2.imread(str(img_path))
                if img is None:
                    continue
                
                # Convert to grayscale
                if len(img.shape) == 3:
                    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                else:
                    gray = img
                
                # Resize to consistent size
                processed = cv2.resize(gray, (200, 200))
                
                # Apply histogram equalization for better recognition
                processed = cv2.equalizeHist(processed)
                
                faces.append(processed)
                labels.append(label_counter)
                loaded_count += 1
                
            except Exception as e:
                print(f"   Error loading {img_path.name}: {e}")
                continue
        
        print(f"✅ {reg_number}: Loaded {loaded_count} images")
        label_counter += 1
    
    if not faces:
        print("\n❌ No face images loaded!")
        return None, None, None
    
    print(f"\n✅ Total: {len(faces)} images from {len(label_mapping)} students")
    
    return faces, labels, label_mapping


def train_model(faces, labels, label_mapping):
    """Train the LBPH face recognizer"""
    print("\n" + "="*60)
    print("TRAINING MODEL")
    print("="*60)
    
    # Initialize recognizer
    recognizer = FaceRecognizer()
    
    print(f"\nTraining with {len(faces)} images...")
    print("This may take a few minutes...\n")
    
    # Train
    start_time = datetime.now()
    recognizer.train(faces, np.array(labels))
    training_time = (datetime.now() - start_time).total_seconds()
    
    print(f"✅ Training completed in {training_time:.2f} seconds")
    
    # Save model
    models_dir = Path('data/models')
    models_dir.mkdir(parents=True, exist_ok=True)
    
    model_path = models_dir / 'face_recognition_model.yml'
    recognizer.save_model(str(model_path))
    print(f"✅ Model saved to {model_path}")
    
    # Save label mapping
    mapping_path = models_dir / 'label_mapping.json'
    with open(mapping_path, 'w') as f:
        json.dump(label_mapping, f, indent=2)
    print(f"✅ Label mapping saved to {mapping_path}")
    
    # Save metadata
    metadata = {
        'training_date': datetime.now().isoformat(),
        'num_students': len(label_mapping),
        'num_images': len(faces),
        'training_time_seconds': training_time,
        'opencv_version': cv2.__version__,
        'algorithm': 'LBPH',
        'image_size': '200x200'
    }
    
    metadata_path = models_dir / 'training_metadata.json'
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    print(f"✅ Metadata saved to {metadata_path}")
    
    # Create backup
    backups_dir = models_dir / 'backups'
    backups_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = backups_dir / f'model_{timestamp}.yml'
    import shutil
    shutil.copy(model_path, backup_path)
    print(f"✅ Backup created at {backup_path}")
    
    return recognizer, label_mapping


def test_model(recognizer, label_mapping, faces, labels):
    """Test the trained model"""
    print("\n" + "="*60)
    print("TESTING MODEL")
    print("="*60)
    
    print("\nPerforming quick accuracy test...")
    
    # Test on random sample
    test_size = min(20, len(faces))
    test_indices = np.random.choice(len(faces), test_size, replace=False)
    
    correct = 0
    for idx in test_indices:
        predicted_label, confidence = recognizer.predict(faces[idx])
        if predicted_label == labels[idx]:
            correct += 1
    
    accuracy = (correct / test_size) * 100
    print(f"\nTest Accuracy: {accuracy:.1f}% ({correct}/{test_size} correct)")
    
    if accuracy >= 90:
        print("✅ Excellent! Model is ready for use.")
    elif accuracy >= 75:
        print("⚠️  Good, but consider adding more training images.")
    else:
        print("⚠️  Low accuracy. Please add more diverse training images.")
    
    # Show label mapping
    print("\n📋 Label Mapping:")
    for label, reg_number in label_mapping.items():
        count = np.sum(np.array(labels) == int(label))
        print(f"   {label}: {reg_number} ({count} images)")


def main():
    """Main training function"""
    print("\n" + "="*60)
    print("FACE RECOGNITION MODEL TRAINING")
    print("="*60)
    
    # Check if database is initialized
    db_path = Path('data/database/attendance.db')
    if not db_path.exists():
        print("\n❌ Database not found!")
        print("   Run: python initialize_system.py first")
        return
    
    # Check if face images exist
    faces_dir = Path('data/faces')
    if not faces_dir.exists() or not list(faces_dir.iterdir()):
        print("\n❌ No face images found!")
        print("   Add student face images to data/faces/")
        return
    
    # Load training data
    faces, labels, label_mapping = load_training_data()
    
    if faces is None:
        return
    
    # Check minimum requirements
    unique_labels = len(set(labels))
    if unique_labels < 2:
        print(f"\n❌ Need at least 2 students, found {unique_labels}")
        return
    
    # Train model
    recognizer, label_mapping = train_model(faces, labels, label_mapping)
    
    # Test model
    test_model(recognizer, label_mapping, faces, labels)
    
    print("\n" + "="*60)
    print("✅ TRAINING COMPLETE!")
    print("="*60)
    print("\nModel files created:")
    print("  📄 data/models/face_recognition_model.yml")
    print("  📄 data/models/label_mapping.json")
    print("  📄 data/models/training_metadata.json")
    print("\nYou can now run the application:")
    print("  python app.py")
    print("\n" + "="*60)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Training cancelled by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
