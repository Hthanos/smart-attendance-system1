# Smart Class Attendance System - Installation Guide

## System Requirements

### Hardware
- Computer or Raspberry Pi 3/4
- USB Webcam or Raspberry Pi Camera Module
- Minimum 2GB RAM
- 1GB free disk space

### Software
- Python 3.8 or higher
- pip (Python package manager)
- Git

---

## Installation Steps

### 1. For Ubuntu/Debian/Raspberry Pi OS

```bash
# Update system
sudo apt-get update
sudo apt-get upgrade

# Install Python and dependencies
sudo apt-get install python3 python3-pip python3-venv
sudo apt-get install python3-opencv python3-tk

# For Raspberry Pi Camera
sudo apt-get install python3-picamera
```

### 2. For Windows

1. Download Python from [python.org](https://www.python.org/downloads/)
2. Install Python (check "Add Python to PATH")
3. Open Command Prompt as Administrator

### 3. Clone Repository

```bash
git clone https://github.com/RamspheldOnyangoOchieng/attendance-system.git
cd attendance-system
```

### 4. Create Virtual Environment

```bash
python3 -m venv venv

# Activate:
# Linux/Mac:
source venv/bin/activate

# Windows:
venv\Scripts\activate
```

### 5. Install Requirements

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 6. Configure Application

```bash
cp .env.example .env
# Edit .env with your settings
nano .env  # or use any text editor
```

### 7. Initialize Database

```bash
python -m src.database.db_manager
```

### 8. Test Installation

```bash
# Test camera
python src/core/camera.py

# Test face detection
python src/core/face_detector.py
```

### 9. Run Application

```bash
python app.py

# Or use the launch script:
./run.sh
```

---

## Troubleshooting

### OpenCV Installation Issues

If OpenCV fails to install:

```bash
# Try opencv-python-headless (no GUI)
pip install opencv-python-headless

# Or build from source (advanced)
```

### Camera Not Detected

```bash
# List video devices
ls /dev/video*

# Test camera
python -c "import cv2; print(cv2.VideoCapture(0).isOpened())"
```

### Permission Errors on Raspberry Pi

```bash
sudo usermod -a -G video $USER
sudo chmod 666 /dev/video0
```

---

## Next Steps

1. Register students
2. Capture face images
3. Train the model
4. Start taking attendance

See [USER_MANUAL.md](03_USER_MANUAL.md) for detailed usage instructions.
