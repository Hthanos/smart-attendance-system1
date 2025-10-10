# Smart Class Attendance System
## DEVELOPER GUIDE

**Version:** 1.0  
**For:** Developers, Maintainers, and Contributors

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Project Structure](#2-project-structure)
3. [Core Modules](#3-core-modules)
4. [Database Layer](#4-database-layer)
5. [Service Layer](#5-service-layer)
6. [UI Layer](#6-ui-layer)
7. [Configuration](#7-configuration)
8. [Testing](#8-testing)
9. [Deployment](#9-deployment)
10. [Contributing](#10-contributing)

---

## 1. ARCHITECTURE OVERVIEW

### 1.1 System Design

The system follows a **layered architecture** pattern:

```
┌──────────────────────────────────────┐
│     Presentation Layer (UI)          │
│     - Tkinter windows/components     │
└───────────────┬──────────────────────┘
                │
┌───────────────┴──────────────────────┐
│     Service Layer                    │
│     - Business logic & orchestration │
└───────────────┬──────────────────────┘
                │
┌───────────────┴──────────────────────┐
│     Core Layer                       │
│     - Face detection/recognition     │
│     - Image processing, Camera       │
└───────────────┬──────────────────────┘
                │
┌───────────────┴──────────────────────┐
│     Data Layer                       │
│     - Database operations & schema   │
└──────────────────────────────────────┘
```

### 1.2 Design Principles

- **Separation of Concerns**: Each layer has distinct responsibilities
- **Dependency Injection**: Components receive dependencies rather than creating them
- **Single Responsibility**: Each module/class has one primary purpose
- **DRY (Don't Repeat Yourself)**: Reusable components and utilities
- **Configuration over Code**: Settings externalized in config files

### 1.3 Technology Stack

| Layer | Technology |
|-------|------------|
| UI | Tkinter, PIL/Pillow |
| Services | Python classes |
| Core | OpenCV, NumPy |
| Data | SQLite, SQL |
| Config | python-dotenv |
| Testing | pytest |

---

## 2. PROJECT STRUCTURE

```
attendance-system/
├── app.py                      # Main entry point
├── requirements.txt            # Python dependencies
├── setup.py                    # Installation script
├── .env.example               # Environment variables template
├── .gitignore                 # Git ignore rules
├── run.sh                     # Launch script
├── verify_setup.py            # Setup verification
│
├── config/                    # Configuration
│   ├── __init__.py
│   ├── settings.py            # Settings class
│   └── haarcascade_frontalface_default.xml
│
├── src/                       # Source code
│   ├── core/                  # Core modules
│   │   ├── camera.py          # Camera abstraction
│   │   ├── face_detector.py   # Haar Cascade wrapper
│   │   ├── face_recognizer.py # LBPH recognizer
│   │   ├── image_processor.py # Image preprocessing
│   │   └── attendance_logger.py
│   │
│   ├── database/              # Data layer
│   │   ├── db_manager.py      # Database connection
│   │   ├── schema.sql         # Database schema
│   │   └── operations.py      # CRUD operations
│   │
│   ├── services/              # Service layer
│   │   ├── student_service.py
│   │   ├── attendance_service.py
│   │   ├── training_service.py
│   │   └── export_service.py
│   │
│   ├── ui/                    # User interface
│   │   ├── app.py             # Main application
│   │   ├── windows/           # Application windows
│   │   └── components/        # Reusable components
│   │
│   ├── utils/                 # Utilities
│   │   ├── logger.py          # Logging setup
│   │   ├── validators.py      # Input validation
│   │   └── helpers.py         # Helper functions
│   │
│   └── notifications/         # Notification modules
│       ├── email_notifier.py
│       └── sms_notifier.py
│
├── data/                      # Data storage
│   ├── database/             # SQLite database
│   ├── faces/                # Face images
│   ├── models/               # Trained models
│   └── exports/              # Generated reports
│
├── tests/                    # Unit tests
│   ├── test_database.py
│   ├── test_face_detection.py
│   ├── test_recognition.py
│   └── test_services.py
│
├── scripts/                  # Utility scripts
│   ├── install_opencv.sh
│   ├── setup_camera.sh
│   ├── backup_db.py
│   └── populate_sample_data.py
│
├── docs/                     # Documentation
│   ├── 01_PROJECT_PROPOSAL.md
│   ├── 02_INSTALLATION.md
│   ├── 03_USER_MANUAL.md
│   ├── 04_DEVELOPER_GUIDE.md
│   └── 05_TESTING_REPORT.md
│
├── resources/                # Resources
│   ├── icons/               # Application icons
│   └── sounds/              # Sound effects
│
└── logs/                    # Application logs
```

---

## 3. CORE MODULES

### 3.1 Camera (`src/core/camera.py`)

**Purpose**: Hardware abstraction for camera access

**Class**: `Camera`

```python
class Camera:
    def __init__(self, camera_type='usb', camera_index=0):
        """Initialize camera"""
        
    def open(self) -> bool:
        """Open camera connection"""
        
    def read(self) -> Tuple[bool, np.ndarray]:
        """Read frame from camera"""
        
    def release(self):
        """Release camera resource"""
        
    def is_opened(self) -> bool:
        """Check if camera is open"""
```

**Usage**:
```python
camera = Camera(camera_type='usb', camera_index=0)
if camera.open():
    ret, frame = camera.read()
    camera.release()
```

**Supported Camera Types**:
- `usb`: Standard USB webcam (uses cv2.VideoCapture)
- `picamera`: Raspberry Pi Camera Module (uses picamera library)

### 3.2 Face Detector (`src/core/face_detector.py`)

**Purpose**: Detect faces in images using Haar Cascade

**Class**: `FaceDetector`

```python
class FaceDetector:
    def __init__(self, cascade_path=None):
        """Initialize with Haar Cascade classifier"""
        
    def detect_faces(self, image: np.ndarray) -> List[Tuple]:
        """Detect faces, returns list of (x, y, w, h)"""
        
    def extract_face(self, image: np.ndarray, 
                     face_rect: Tuple, margin=10) -> np.ndarray:
        """Extract face ROI with margin"""
```

**Parameters**:
- `scaleFactor`: 1.1 (default) - Image pyramid scale
- `minNeighbors`: 5 (default) - Detection quality
- `minSize`: (30, 30) - Minimum face size

**Usage**:
```python
detector = FaceDetector()
faces = detector.detect_faces(frame)
for (x, y, w, h) in faces:
    face_img = detector.extract_face(frame, (x, y, w, h))
```

### 3.3 Face Recognizer (`src/core/face_recognizer.py`)

**Purpose**: Train and predict using LBPH algorithm

**Class**: `FaceRecognizer`

**Key Methods**:

```python
def train(self, faces: List[np.ndarray], labels: List[int]):
    """Train model with face images and labels"""
    
def predict(self, face: np.ndarray) -> Tuple[int, float]:
    """Predict label and confidence for face"""
    
def save_model(self, model_path: str):
    """Save trained model to file"""
    
def load_model(self, model_path: str) -> bool:
    """Load model from file"""
```

**Algorithm**: LBPH (Local Binary Patterns Histograms)
- Radius: 1
- Neighbors: 8
- Grid X: 8
- Grid Y: 8

**Confidence Scores**:
- Lower is better (0 = perfect match)
- Typical threshold: 60-70
- >100 usually indicates no match

### 3.4 Image Processor (`src/core/image_processor.py`)

**Purpose**: Preprocess images for better recognition

**Functions**:

```python
def preprocess_face(image: np.ndarray) -> np.ndarray:
    """
    Apply preprocessing pipeline:
    1. Convert to grayscale
    2. Equalize histogram
    3. Normalize size
    4. Denoise
    """
    
def enhance_image(image: np.ndarray) -> np.ndarray:
    """Enhance image contrast and brightness"""
    
def normalize_face(face: np.ndarray, size=(200, 200)) -> np.ndarray:
    """Resize face to standard size"""
```

**Usage**:
```python
from src.core.image_processor import ImageProcessor

raw_face = detector.extract_face(frame, face_rect)
processed = ImageProcessor.preprocess_face(raw_face)
label, confidence = recognizer.predict(processed)
```

---

## 4. DATABASE LAYER

### 4.1 Database Manager (`src/database/db_manager.py`)

**Purpose**: Manage SQLite database connections

**Class**: `DatabaseManager`

**Key Methods**:

```python
def get_connection(self) -> sqlite3.Connection:
    """Get database connection"""
    
def get_cursor(self) -> ContextManager:
    """Get cursor with automatic commit/rollback"""
    
def initialize_database(self):
    """Create tables from schema.sql"""
    
def backup_database(self, backup_path: str):
    """Create database backup"""
```

**Context Manager Usage**:
```python
db = DatabaseManager()
with db.get_cursor() as cursor:
    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()
# Auto-commit on success, rollback on exception
```

### 4.2 Schema (`src/database/schema.sql`)

**Main Tables**:

**students**:
```sql
CREATE TABLE students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    registration_number VARCHAR(50) UNIQUE NOT NULL,
    full_name VARCHAR(200) NOT NULL,
    email VARCHAR(100),
    phone_number VARCHAR(20),
    gender VARCHAR(10),
    year_of_study INTEGER,
    date_registered DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT 1
);
```

**courses**:
```sql
CREATE TABLE courses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_code VARCHAR(20) UNIQUE NOT NULL,
    course_name VARCHAR(200) NOT NULL,
    lecturer_name VARCHAR(200),
    credits INTEGER
);
```

**class_sessions**:
```sql
CREATE TABLE class_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_id INTEGER NOT NULL,
    session_date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME,
    location VARCHAR(100),
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE
);
```

**attendance**:
```sql
CREATE TABLE attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    session_id INTEGER NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'Present',
    confidence_score REAL,
    marked_by VARCHAR(50),
    notes TEXT,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (session_id) REFERENCES class_sessions(id) ON DELETE CASCADE
);
```

**Views**:

- `view_student_attendance_summary`: Attendance stats per student per course
- `view_course_attendance_summary`: Overall course attendance stats
- `view_todays_attendance`: Today's attendance records

### 4.3 Operations (`src/database/operations.py`)

**Purpose**: CRUD operations for all entities

**Key Methods**:

```python
# Students
def create_student(self, **kwargs) -> int
def get_student(self, student_id: int) -> dict
def get_all_students(self) -> List[dict]
def update_student(self, student_id: int, **kwargs)
def delete_student(self, student_id: int)

# Courses
def create_course(self, **kwargs) -> int
def get_all_courses(self) -> List[dict]

# Sessions
def create_session(self, **kwargs) -> int
def get_todays_sessions(self) -> List[dict]

# Attendance
def mark_attendance(self, student_id, session_id, **kwargs) -> int
def get_session_attendance(self, session_id) -> List[dict]
def get_student_attendance(self, student_id, course_id=None) -> List[dict]

# Settings
def get_setting(self, key: str) -> str
def update_setting(self, key: str, value: str)
```

---

## 5. SERVICE LAYER

### 5.1 Student Service (`src/services/student_service.py`)

**Purpose**: Business logic for student management

**Key Methods**:

```python
def register_student(self, student_data: dict, 
                    face_images: List[np.ndarray]) -> int:
    """
    Register student with face images
    1. Validate data
    2. Save to database
    3. Save face images to disk
    4. Return student_id
    """
    
def get_student(self, student_id: int) -> dict:
    """Get student by ID"""
    
def search_students(self, query: str) -> List[dict]:
    """Search by name or registration number"""
```

### 5.2 Attendance Service (`src/services/attendance_service.py`)

**Purpose**: Attendance business logic

**Key Methods**:

```python
def mark_attendance(self, student_id: int, session_id: int, 
                   confidence_score: float = None) -> bool:
    """
    Mark student attendance
    - Check if already marked
    - Determine status (Present/Late)
    - Log to database
    """
    
def get_session_attendance(self, session_id: int) -> List[dict]:
    """Get all attendance for a session"""
    
def get_attendance_statistics(self, student_id: int = None,
                              course_id: int = None) -> dict:
    """Calculate attendance statistics"""
    
def search_records(self, **filters) -> List[dict]:
    """Search attendance records with filters"""
```

### 5.3 Training Service (`src/services/training_service.py`)

**Purpose**: Model training workflow

**Key Methods**:

```python
def train_model(self) -> bool:
    """
    Train recognition model
    1. Load all student face images
    2. Preprocess images
    3. Train LBPH recognizer
    4. Save model and labels
    """
    
def load_trained_model(self) -> bool:
    """Load previously trained model"""
    
def is_model_trained(self) -> bool:
    """Check if model exists and is trained"""
    
def get_recognizer(self) -> FaceRecognizer:
    """Get loaded recognizer instance"""
```

### 5.4 Export Service (`src/services/export_service.py`)

**Purpose**: Generate reports and exports

**Key Methods**:

```python
def export_to_excel(self, data: List[dict], 
                   filename_prefix: str = "attendance") -> str:
    """
    Export data to Excel with formatting
    - Multiple sheets (Summary, Details)
    - Styling and formatting
    - Charts (if applicable)
    """
    
def export_to_csv(self, data: List[dict],
                 filename_prefix: str = "attendance") -> str:
    """Export data to CSV"""
    
def generate_attendance_report(self, course_id: int,
                               start_date: str, end_date: str) -> str:
    """Generate comprehensive attendance report"""
```

---

## 6. UI LAYER

### 6.1 Main Application (`src/ui/app.py`)

**Purpose**: Main Tkinter application

**Class**: `AttendanceApp`

```python
class AttendanceApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Smart Class Attendance System")
        self._setup_menu()
        self._show_dashboard()
        
    def _setup_menu(self):
        """Create menu bar"""
        
    def _show_dashboard(self):
        """Display dashboard window"""
```

**Window Management**:
- Uses `tk.Toplevel` for secondary windows
- One window at a time (modal dialogs)
- Window references stored to prevent garbage collection

### 6.2 Windows (`src/ui/windows/`)

Each window is a `tk.Toplevel` subclass:

**Dashboard** (`dashboard.py`):
- Statistics cards
- Today's sessions table
- Quick actions

**Student Registration** (`student_registration.py`):
- Student information form
- Camera integration
- Face capture workflow
- Save functionality

**Take Attendance** (`take_attendance.py`):
- Session selection
- Live camera feed
- Real-time recognition
- Attendance list

**View Records** (`view_records.py`):
- Search filters
- Results table with sorting
- Export buttons

**Settings** (`settings.py`):
- Tabbed interface
- Recognition settings
- Institution settings
- Camera configuration
- Model management

### 6.3 Components (`src/ui/components/`)

Reusable widgets:

**VideoWidget** (`video_widget.py`):
```python
class VideoWidget(tk.Frame):
    """Reusable video display"""
    def start(self):
        """Start video feed"""
    def stop(self):
        """Stop video feed"""
    def set_update_callback(self, callback):
        """Set frame processing callback"""
```

**StudentCard** (`student_card.py`):
```python
class StudentCard(tk.Frame):
    """Display student information"""
    def set_student(self, student_data: dict):
        """Update card with student data"""
```

---

## 7. CONFIGURATION

### 7.1 Settings (`config/settings.py`)

**Centralized configuration** using class attributes:

```python
class Settings:
    # Paths
    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = BASE_DIR / "data"
    FACES_DIR = DATA_DIR / "faces"
    
    # Camera
    CAMERA_TYPE = os.getenv("CAMERA_TYPE", "usb")
    CAMERA_INDEX = int(os.getenv("CAMERA_INDEX", "0"))
    
    # Recognition
    RECOGNITION_CONFIDENCE_THRESHOLD = 60
    MIN_TRAINING_IMAGES = 30
    
    # Database
    DATABASE_PATH = DATA_DIR / "database" / "attendance.db"
```

**Loading from Environment**:
- Uses `python-dotenv` to load `.env` file
- Environment variables override defaults
- See `.env.example` for available variables

### 7.2 Environment Variables

Create `.env` file (copy from `.env.example`):

```bash
# Camera Configuration
CAMERA_TYPE=usb
CAMERA_INDEX=0

# Recognition
CONFIDENCE_THRESHOLD=60

# Email (optional)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password

# SMS (optional)
AFRICASTALKING_USERNAME=sandbox
AFRICASTALKING_API_KEY=your_api_key

# Institution
INSTITUTION_NAME=Moi University
DEPARTMENT=Computer Science
ACADEMIC_YEAR=2024/2025
SEMESTER=Semester 1
```

---

## 8. TESTING

### 8.1 Unit Tests

**Framework**: pytest

**Running Tests**:
```bash
# All tests
pytest

# Specific file
pytest tests/test_database.py

# With coverage
pytest --cov=src tests/

# Verbose
pytest -v
```

### 8.2 Test Structure

**test_database.py**:
```python
import pytest
from src.database.db_manager import DatabaseManager
from src.database.operations import DatabaseOperations

@pytest.fixture
def db():
    """Create test database"""
    db = DatabaseManager(":memory:")
    db.initialize_database()
    return db

def test_create_student(db):
    ops = DatabaseOperations(db)
    student_id = ops.create_student(
        registration_number="TEST001",
        full_name="Test Student",
        email="test@example.com"
    )
    assert student_id > 0
```

### 8.3 Integration Tests

Test complete workflows:
```python
def test_attendance_workflow():
    # 1. Register student
    # 2. Train model
    # 3. Mark attendance
    # 4. Verify record
    pass
```

### 8.4 Manual Testing

**Test Checklist**:
- [ ] Student registration with camera
- [ ] Face detection in various lighting
- [ ] Model training with multiple students
- [ ] Attendance marking accuracy
- [ ] Export to Excel/CSV
- [ ] Settings persistence
- [ ] Error handling

---

## 9. DEPLOYMENT

### 9.1 Production Setup

**1. Install Dependencies**:
```bash
pip install -r requirements.txt
```

**2. Configure Environment**:
```bash
cp .env.example .env
# Edit .env with production settings
```

**3. Initialize Database**:
```bash
python -c "from src.database.db_manager import DatabaseManager; DatabaseManager().initialize_database()"
```

**4. Verify Setup**:
```bash
python verify_setup.py
```

### 9.2 Raspberry Pi Deployment

**Requirements**:
- Raspberry Pi 4 (4GB+ recommended)
- Raspberry Pi OS (64-bit)
- Pi Camera Module v2

**Setup**:
```bash
# Install OpenCV
sudo apt-get update
sudo apt-get install python3-opencv

# Install other dependencies
pip3 install -r requirements.txt

# Configure camera
sudo raspi-config
# Enable camera interface

# Set camera type in .env
echo "CAMERA_TYPE=picamera" >> .env
```

### 9.3 Running as Service

**systemd service** (Linux):

Create `/etc/systemd/system/attendance.service`:
```ini
[Unit]
Description=Attendance System
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/attendance-system
ExecStart=/usr/bin/python3 /home/pi/attendance-system/app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable attendance
sudo systemctl start attendance
```

### 9.4 Backup Strategy

**Automated Backup Script** (`scripts/backup_db.py`):
```python
#!/usr/bin/env python3
import shutil
from datetime import datetime
from pathlib import Path

def backup():
    db_path = Path("data/database/attendance.db")
    backup_dir = Path("backups")
    backup_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = backup_dir / f"attendance_{timestamp}.db"
    
    shutil.copy2(db_path, backup_path)
    print(f"Backup created: {backup_path}")

if __name__ == "__main__":
    backup()
```

**Cron Job** (daily backup at 2 AM):
```bash
0 2 * * * cd /path/to/attendance-system && python3 scripts/backup_db.py
```

---

## 10. CONTRIBUTING

### 10.1 Code Style

**PEP 8 Compliance**:
- 4 spaces for indentation
- Max line length: 100 characters
- Use type hints where applicable

**Naming Conventions**:
- Classes: `PascalCase`
- Functions/methods: `snake_case`
- Constants: `UPPER_SNAKE_CASE`
- Private members: `_leading_underscore`

### 10.2 Adding Features

**1. Create Branch**:
```bash
git checkout -b feature/your-feature-name
```

**2. Implement Feature**:
- Follow existing architecture
- Add tests
- Update documentation

**3. Test**:
```bash
pytest
python verify_setup.py
```

**4. Commit**:
```bash
git add .
git commit -m "feat: Add your feature description"
```

**5. Push and Create PR**:
```bash
git push origin feature/your-feature-name
```

### 10.3 Git Commit Messages

Follow Conventional Commits:
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation
- `test:` Tests
- `refactor:` Code refactoring
- `style:` Formatting
- `chore:` Maintenance

### 10.4 Documentation

Update docs when:
- Adding new features
- Changing API
- Fixing bugs with workarounds
- Updating configuration options

---

## APPENDIX: Common Tasks

### Add New Face Recognition Algorithm

1. Create `src/core/new_recognizer.py`
2. Implement interface matching `FaceRecognizer`
3. Update `TrainingService` to support new algorithm
4. Add configuration option in Settings
5. Update tests

### Add New Database Table

1. Add CREATE TABLE to `schema.sql`
2. Add CRUD methods to `DatabaseOperations`
3. Create service class if needed
4. Update UI if user-facing
5. Write migration script for existing databases

### Add New UI Window

1. Create `src/ui/windows/new_window.py`
2. Extend `tk.Toplevel`
3. Add menu item in `app.py`
4. Use existing components where possible
5. Follow existing window patterns

### Integrate New Camera Type

1. Extend `Camera` class in `src/core/camera.py`
2. Add camera type to `Settings.CAMERA_TYPE` options
3. Implement `_open()` method for new type
4. Test thoroughly
5. Update documentation

---

**For Questions**: Open an issue on GitHub  
**For Bugs**: Create bug report with logs  
**For Features**: Submit feature request with use case

**Happy Coding! 🚀**
