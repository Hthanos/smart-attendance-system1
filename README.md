# Smart Class Attendance System

**Automated Face Recognition-Based Attendance Management**

A comprehensive attendance tracking system using facial recognition technology, developed for educational institutions. Built with Python, OpenCV, and SQLite.

---

## 👥 Team

- **Sharon Yegon** – E028-01-1532/2022
- **Gidion Yegon** – E028-01-1278/2020
- **Gabriel Okal** – E028-01-1307/2020

**Supervisor:** Dr. Tafara  
**Institution:**Dedan Kimathi University of Technology - Department of Electrical and Electronics Engineering

---

## 🎯 Features

- ✅ **Contactless Attendance** - Face recognition-based identification
- ✅ **Real-time Detection** - Live camera feed with instant recognition
- ✅ **Automated Logging** - Attendance automatically saved to database
- ✅ **Multiple Courses** - Support for multiple courses and sessions
- ✅ **Excel Reports** - Export attendance to Excel/CSV
- ✅ **Student Management** - Register and manage student records
- ✅ **Statistics & Analytics** - Attendance percentages and trends
- ✅ **Raspberry Pi Support** - Works on Raspberry Pi with camera module
- ✅ **Optional Notifications** - Email/SMS alerts for attendance

---

## 🛠️ Technology Stack

- **Programming Language:** Python 3.8+
- **Computer Vision:** OpenCV 4.8+
- **Face Recognition:** LBPH (Local Binary Patterns Histograms)
- **Database:** SQLite
- **GUI:** Tkinter
- **Data Export:** Pandas, OpenPyXL
- **Hardware:** Raspberry Pi / USB Webcam

---

## 📋 Prerequisites

### System Requirements

- Python 3.8 or higher
- Webcam or Raspberry Pi Camera Module
- 2GB RAM minimum (4GB recommended)
- 1GB free disk space

### For Raspberry Pi

```bash
sudo apt-get update
sudo apt-get install python3-opencv python3-tk
```

---

## 🚀 Installation

### 1. open the project folder

```bash

cd attendance-system
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
cp .env.example .env
# Edit .env file with your settings
```

### 5. Initialize Database

```bash
python -m src.database.db_manager
```

---

## 📖 Usage

### Start the Application

```bash
python app.py
```

Or use the run script:

```bash
chmod +x run.sh
./run.sh
```

### Console Mode (No GUI)

If GUI is not available, the app automatically falls back to console mode.

---

## 📚 Quick Start Guide

### 1. Register Students

1. Open the application
2. Navigate to "Student Registration"
3. Fill in student details
4. Capture 30+ face images per student
5. Save registration

### 2. Train Model

1. Go to "Train Model" section
2. Click "Start Training"
3. Wait for training to complete
4. Model is automatically saved

### 3. Create Class Session

1. Navigate to "Sessions"
2. Select course and date
3. Click "Create Session"

### 4. Take Attendance

1. Open "Take Attendance"
2. Select active session
3. Start camera
4. System automatically recognizes and marks attendance
5. Review and export results

---

## 🗂️ Project Structure

```
attendance-system/
├── config/              # Configuration files
├── src/                # Source code
│   ├── core/          # Core modules (camera, face detection, recognition)
│   ├── database/      # Database layer
│   ├── services/      # Business logic
│   ├── ui/            # User interface
│   ├── utils/         # Utilities
│   └── notifications/ # Email/SMS notifications
├── data/              # Data storage
│   ├── database/     # SQLite database
│   ├── faces/        # Student face images
│   ├── models/       # Trained models
│   └── exports/      # Generated reports
├── logs/             # Application logs
├── docs/             # Documentation
├── tests/            # Unit tests
└── app.py            # Main entry point
```

---

## 🔧 Configuration

Edit `.env` file to configure:

- Camera settings (USB/PiCamera)
- Recognition threshold
- Database path
- Email/SMS credentials
- Institution details

---

## 📊 Database Schema

The system uses SQLite with the following main tables:

- **students** - Student information
- **courses** - Course details
- **enrollments** - Student-course relationships
- **class_sessions** - Class sessions
- **attendance** - Attendance records

---

## 🧪 Testing

Run tests:

```bash
pytest tests/
```

Test individual modules:

```bash
python src/core/camera.py           # Test camera
python src/core/face_detector.py    # Test face detection
python src/core/face_recognizer.py  # Test recognition
```

---

## 📈 Performance

- **Face Detection:** 30+ FPS on USB webcam
- **Recognition Accuracy:** 95%+ with good lighting
- **Training Time:** ~5 seconds for 10 students (300 images)
- **Database:** Handles 1000+ students efficiently


---

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🙏 Acknowledgments

- OpenCV community for computer vision libraries
- Dedan kimathi University for project support
- Dr. Tafara for supervision and guidance

---

## ⚠️ Known Issues

- Face recognition accuracy decreases in low light
- Multiple faces in frame may slow down processing
- Raspberry Pi Camera requires specific setup



---

## 🔮 Future Enhancements

- [ ] Mobile app integration
- [ ] Real-time dashboard
- [ ] Multi-camera support
- [ ] Deep learning models (FaceNet, ArcFace)
- [ ] Biometric fusion (face + fingerprint)

---

**Made with ❤️ by Dedan Kimathi University Engineering Students**
