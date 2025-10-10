"""
Image Processor - Image preprocessing utilities
"""

import cv2
import numpy as np
from typing import Tuple, Optional
import logging

from config.settings import Settings

logger = logging.getLogger(__name__)


class ImageProcessor:
    """Image preprocessing for face recognition"""
    
    @staticmethod
    def convert_to_grayscale(image: np.ndarray) -> np.ndarray:
        """
        Convert image to grayscale
        
        Args:
            image: Input image (BGR or grayscale)
        
        Returns:
            Grayscale image
        """
        if len(image.shape) == 2:
            return image
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    @staticmethod
    def resize_image(
        image: np.ndarray, 
        size: Optional[Tuple[int, int]] = None
    ) -> np.ndarray:
        """
        Resize image to specified size
        
        Args:
            image: Input image
            size: Target size as (width, height). Uses Settings.TRAINING_IMAGE_SIZE if None
        
        Returns:
            Resized image
        """
        size = size or Settings.TRAINING_IMAGE_SIZE
        return cv2.resize(image, size, interpolation=cv2.INTER_AREA)
    
    @staticmethod
    def enhance_contrast(image: np.ndarray) -> np.ndarray:
        """
        Enhance image contrast using histogram equalization
        
        Args:
            image: Input grayscale image
        
        Returns:
            Enhanced image
        """
        return cv2.equalizeHist(image)
    
    @staticmethod
    def apply_clahe(image: np.ndarray, clip_limit: float = 2.0, tile_size: int = 8) -> np.ndarray:
        """
        Apply Contrast Limited Adaptive Histogram Equalization (CLAHE)
        
        Args:
            image: Input grayscale image
            clip_limit: Threshold for contrast limiting
            tile_size: Size of grid for histogram equalization
        
        Returns:
            Enhanced image
        """
        clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=(tile_size, tile_size))
        return clahe.apply(image)
    
    @staticmethod
    def denoise_image(image: np.ndarray, strength: int = 10) -> np.ndarray:
        """
        Remove noise from image
        
        Args:
            image: Input image
            strength: Denoising strength
        
        Returns:
            Denoised image
        """
        if len(image.shape) == 2:
            return cv2.fastNlMeansDenoising(image, None, strength, 7, 21)
        else:
            return cv2.fastNlMeansDenoisingColored(image, None, strength, strength, 7, 21)
    
    @staticmethod
    def normalize_image(image: np.ndarray) -> np.ndarray:
        """
        Normalize image pixel values to [0, 1]
        
        Args:
            image: Input image
        
        Returns:
            Normalized image
        """
        return image.astype(np.float32) / 255.0
    
    @staticmethod
    def preprocess_face(
        face_image: np.ndarray,
        target_size: Optional[Tuple[int, int]] = None,
        enhance: bool = True
    ) -> np.ndarray:
        """
        Complete preprocessing pipeline for face images
        
        Args:
            face_image: Input face image
            target_size: Target size for resizing
            enhance: Whether to apply contrast enhancement
        
        Returns:
            Preprocessed face image
        """
        # Convert to grayscale
        gray = ImageProcessor.convert_to_grayscale(face_image)
        
        # Resize
        resized = ImageProcessor.resize_image(gray, target_size)
        
        # Enhance contrast
        if enhance:
            enhanced = ImageProcessor.apply_clahe(resized)
        else:
            enhanced = resized
        
        return enhanced
    
    @staticmethod
    def apply_blur(image: np.ndarray, kernel_size: int = 5) -> np.ndarray:
        """
        Apply Gaussian blur to image
        
        Args:
            image: Input image
            kernel_size: Blur kernel size (must be odd)
        
        Returns:
            Blurred image
        """
        if kernel_size % 2 == 0:
            kernel_size += 1
        return cv2.GaussianBlur(image, (kernel_size, kernel_size), 0)
    
    @staticmethod
    def detect_edges(image: np.ndarray, low_threshold: int = 50, high_threshold: int = 150) -> np.ndarray:
        """
        Detect edges using Canny edge detector
        
        Args:
            image: Input grayscale image
            low_threshold: Lower threshold for edge detection
            high_threshold: Upper threshold for edge detection
        
        Returns:
            Edge map
        """
        return cv2.Canny(image, low_threshold, high_threshold)
    
    @staticmethod
    def rotate_image(image: np.ndarray, angle: float) -> np.ndarray:
        """
        Rotate image by specified angle
        
        Args:
            image: Input image
            angle: Rotation angle in degrees (positive = counter-clockwise)
        
        Returns:
            Rotated image
        """
        height, width = image.shape[:2]
        center = (width // 2, height // 2)
        
        rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(image, rotation_matrix, (width, height))
        
        return rotated
    
    @staticmethod
    def adjust_brightness(image: np.ndarray, factor: float) -> np.ndarray:
        """
        Adjust image brightness
        
        Args:
            image: Input image
            factor: Brightness factor (1.0 = no change, >1 = brighter, <1 = darker)
        
        Returns:
            Adjusted image
        """
        adjusted = cv2.convertScaleAbs(image, alpha=factor, beta=0)
        return adjusted
    
    @staticmethod
    def crop_to_square(image: np.ndarray) -> np.ndarray:
        """
        Crop image to square (center crop)
        
        Args:
            image: Input image
        
        Returns:
            Square cropped image
        """
        height, width = image.shape[:2]
        size = min(height, width)
        
        y_start = (height - size) // 2
        x_start = (width - size) // 2
        
        return image[y_start:y_start+size, x_start:x_start+size]
    
    @staticmethod
    def save_image(image: np.ndarray, filepath: str) -> bool:
        """
        Save image to file
        
        Args:
            image: Image to save
            filepath: Output file path
        
        Returns:
            bool: True if successful
        """
        try:
            cv2.imwrite(filepath, image)
            return True
        except Exception as e:
            logger.error(f"Failed to save image: {str(e)}")
            return False
    
    @staticmethod
    def load_image(filepath: str, grayscale: bool = False) -> Optional[np.ndarray]:
        """
        Load image from file
        
        Args:
            filepath: Input file path
            grayscale: Whether to load as grayscale
        
        Returns:
            Loaded image or None
        """
        try:
            if grayscale:
                image = cv2.imread(filepath, cv2.IMREAD_GRAYSCALE)
            else:
                image = cv2.imread(filepath)
            
            return image if image is not None else None
        except Exception as e:
            logger.error(f"Failed to load image: {str(e)}")
            return None


def test_image_processor():
    """Test image processor functionality"""
    print("Testing Image Processor...")
    
    # Create test image
    test_image = np.random.randint(0, 256, (480, 640, 3), dtype=np.uint8)
    
    print("✓ Test image created")
    
    # Test grayscale conversion
    gray = ImageProcessor.convert_to_grayscale(test_image)
    print(f"✓ Grayscale conversion: {gray.shape}")
    
    # Test resize
    resized = ImageProcessor.resize_image(gray, (200, 200))
    print(f"✓ Resize: {resized.shape}")
    
    # Test contrast enhancement
    enhanced = ImageProcessor.enhance_contrast(gray)
    print(f"✓ Contrast enhancement: {enhanced.shape}")
    
    # Test CLAHE
    clahe = ImageProcessor.apply_clahe(gray)
    print(f"✓ CLAHE: {clahe.shape}")
    
    # Test preprocessing pipeline
    preprocessed = ImageProcessor.preprocess_face(test_image)
    print(f"✓ Preprocessing pipeline: {preprocessed.shape}")
    
    print("\n✓ All image processor tests passed!")
    return True


if __name__ == '__main__':
    test_image_processor()
