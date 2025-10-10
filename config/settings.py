"""
Application Settings and Configuration
Loads settings from .env file or uses defaults
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings:
    """Application configuration settings"""
    
    # Base paths
    BASE_DIR = Path(__file__).parent.parent
    CONFIG_DIR = BASE_DIR / 'config'
    SRC_DIR = BASE_DIR / 'src'
    DATA_DIR = BASE_DIR / 'data'
    
    # Application
    APP_NAME = os.getenv('APP_NAME', 'Smart Class Attendance System')
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    # Camera Settings
    CAMERA_TYPE = os.getenv('CAMERA_TYPE', 'USB')  # USB or PICAMERA
    CAMERA_INDEX = int(os.getenv('CAMERA_INDEX', 0))
    CAMERA_WIDTH = int(os.getenv('CAMERA_WIDTH', 640))
    CAMERA_HEIGHT = int(os.getenv('CAMERA_HEIGHT', 480))
    CAMERA_FPS = int(os.getenv('CAMERA_FPS', 30))
    
    # Face Detection Settings (Haar Cascade)
    HAAR_CASCADE_PATH = str(CONFIG_DIR / 'haarcascade_frontalface_default.xml')
    SCALE_FACTOR = float(os.getenv('SCALE_FACTOR', 1.1))
    MIN_NEIGHBORS = int(os.getenv('MIN_NEIGHBORS', 5))
    MIN_FACE_SIZE = int(os.getenv('MIN_FACE_SIZE', 30))
    
    # Face Recognition Settings (LBPH)
    RECOGNITION_THRESHOLD = int(os.getenv('RECOGNITION_THRESHOLD', 50))
    RECOGNITION_RADIUS = 1
    RECOGNITION_NEIGHBORS = 8
    RECOGNITION_GRID_X = 8
    RECOGNITION_GRID_Y = 8
    
    # Training Settings
    IMAGES_PER_STUDENT = int(os.getenv('IMAGES_PER_STUDENT', 30))
    IMAGE_CAPTURE_DELAY = float(os.getenv('IMAGE_CAPTURE_DELAY', 0.1))
    TRAINING_IMAGE_SIZE = (200, 200)
    
    # Database
    DATABASE_PATH = str(DATA_DIR / 'database' / 'attendance.db')
    
    # Data Directories
    FACES_DIR = DATA_DIR / 'faces'
    MODELS_DIR = DATA_DIR / 'models'
    EXPORTS_DIR = DATA_DIR / 'exports'
    LOGS_DIR = BASE_DIR / 'logs'
    
    # Model Files
    TRAINED_MODEL_PATH = str(MODELS_DIR / 'trained_model.yml')
    LABEL_MAP_PATH = str(MODELS_DIR / 'label_map.json')
    
    # Email Configuration
    EMAIL_ENABLED = os.getenv('EMAIL_ENABLED', 'False').lower() == 'true'
    SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
    SMTP_USERNAME = os.getenv('SMTP_USERNAME', '')
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')
    EMAIL_FROM = os.getenv('EMAIL_FROM', '')
    EMAIL_TO = os.getenv('EMAIL_TO', '')
    
    # SMS Configuration (Africa's Talking)
    SMS_ENABLED = os.getenv('SMS_ENABLED', 'False').lower() == 'true'
    AFRICASTALKING_USERNAME = os.getenv('AFRICASTALKING_USERNAME', 'sandbox')
    AFRICASTALKING_API_KEY = os.getenv('AFRICASTALKING_API_KEY', '')
    SMS_SENDER_ID = os.getenv('SMS_SENDER_ID', 'ATTENDANCE')
    
    # Institution Details
    INSTITUTION_NAME = os.getenv('INSTITUTION_NAME', 'Moi University')
    DEPARTMENT = os.getenv('DEPARTMENT', 'Electrical and Electronics Engineering')
    ACADEMIC_YEAR = os.getenv('ACADEMIC_YEAR', '2024/2025')
    SEMESTER = os.getenv('SEMESTER', '1')
    
    # UI Settings
    WINDOW_TITLE = f"{APP_NAME} - {INSTITUTION_NAME}"
    WINDOW_SIZE = "1200x800"
    THEME_COLOR = "#2c3e50"
    ACCENT_COLOR = "#3498db"
    SUCCESS_COLOR = "#27ae60"
    ERROR_COLOR = "#e74c3c"
    
    @classmethod
    def ensure_directories(cls):
        """Create necessary directories if they don't exist"""
        directories = [
            cls.DATA_DIR / 'database',
            cls.FACES_DIR,
            cls.MODELS_DIR,
            cls.EXPORTS_DIR / 'excel',
            cls.EXPORTS_DIR / 'csv',
            cls.LOGS_DIR,
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def validate(cls):
        """Validate critical settings"""
        if not os.path.exists(cls.HAAR_CASCADE_PATH):
            raise FileNotFoundError(
                f"Haar Cascade file not found: {cls.HAAR_CASCADE_PATH}\n"
                "Please download it from OpenCV repository."
            )
        
        return True


# Initialize directories on import
Settings.ensure_directories()
