# Database Setup and Training Guide

## Quick Start

Follow these steps to set up the database and train the face recognition model:

### 1. Prerequisites

Ensure you have:
- ✅ Python 3.8+ installed
- ✅ Virtual environment activated
- ✅ Face images in `data/faces/` directory
  - Each student should have their own folder
  - Folder name: `E028-01-XXXX-YYYY` (e.g., `E028-01-1303-2020`)
  - Minimum 7 images per student (10+ recommended)

### 2. Install Dependencies

```bash
# Activate virtual environment (if not already active)
source venv/bin/activate

# Install required packages
pip install opencv-python numpy pillow pandas openpyxl python-dotenv
```

### 3. Initialize Database

Run the initialization script to create the database and add students:

```bash
python initialize_system.py
```

This script will:
1. Create the database schema
2. Scan `data/faces/` for student directories
3. Prompt you to enter student details (name, email, phone)
4. Add sample courses
5. Enroll students in courses

**Interactive Prompts:**
- Enter student's first name
- Enter student's last name
- Enter email (optional - press Enter to skip)
- Enter phone (optional - press Enter to skip)

**Important:** 
- Students with fewer than 7 images will be skipped
- Registration numbers are extracted from folder names
- Format: `E028-01-1303-2020` → `E028-01-1303/2020`

### 4. Train the Model

After adding all students, train the face recognition model:

```bash
python train_model.py
```

This script will:
1. Load all face images from `data/faces/`
2. Preprocess and prepare images for training
3. Train the LBPH face recognizer
4. Save the model to `data/models/`
5. Create label mappings
6. Perform accuracy test

**Expected Output:**
```
============================================================
FACE RECOGNITION MODEL TRAINING
============================================================

============================================================
LOADING TRAINING DATA
============================================================

Found 6 students in database
✅ E028-01-1303/2020: Loaded 10 images
✅ E028-01-1304/2020: Loaded 12 images
...

✅ Total: 65 images from 6 students

============================================================
TRAINING MODEL
============================================================

Training with 65 images...
✅ Training completed in 2.34 seconds
✅ Model saved to data/models/face_recognition_model.yml
✅ Label mapping saved to data/models/label_mapping.json

============================================================
TESTING MODEL
============================================================

Test Accuracy: 95.0% (19/20 correct)
✅ Excellent! Model is ready for use.

============================================================
✅ TRAINING COMPLETE!
============================================================
```

### 5. Verify Setup

Test the database connection:

```bash
python test_db.py
```

### 6. Run the Application

```bash
python app.py
```

## Troubleshooting

### Issue: "Only X images found (minimum 7 required)"

**Solution:** Add more face images to that student's folder.

```bash
# Check how many images you have
ls -la data/faces/E028-01-1303-2020/
```

### Issue: "No students found in database"

**Solution:** Run the initialization script first:

```bash
python initialize_system.py
```

### Issue: "ModuleNotFoundError: No module named 'cv2'"

**Solution:** Install OpenCV:

```bash
pip install opencv-python
```

### Issue: Registration number format mismatch

If your folder names don't match the expected format, update them:

**Current format:** `E028-01-1303-2020`  
**Should match:** Student's actual registration number

The script will convert:
- `E028-01-1303-2020` → `E028-01-1303/2020`
- `E028-01-1276 20222` → `E028-01-1276/20222` (note the typo will be preserved)

**Fix folder names:**
```bash
cd data/faces
mv "E028-01-1276 20222" "E028-01-1276-2022"
```

### Issue: Database already exists

If you need to reinitialize:

```bash
# Backup existing database
cp data/database/attendance.db data/database/attendance_backup.db

# Remove it
rm data/database/attendance.db

# Reinitialize
python initialize_system.py
```

## Folder Structure

After setup, you should have:

```
attendance-system/
├── data/
│   ├── database/
│   │   └── attendance.db          ✅ Database file
│   ├── faces/
│   │   ├── E028-01-1303-2020/
│   │   │   ├── IMG-001.jpg
│   │   │   └── ...
│   │   └── ...
│   └── models/
│       ├── face_recognition_model.yml     ✅ Trained model
│       ├── label_mapping.json              ✅ Label mapping
│       ├── training_metadata.json          ✅ Training info
│       └── backups/
│           └── model_20251013_*.yml
```

## Image Requirements

### Quality Guidelines

✅ **Good Images:**
- Clear face, well-lit
- Face centered in frame
- Looking at camera
- Neutral expression
- No sunglasses or face masks

❌ **Poor Images:**
- Too dark or blurry
- Face partially hidden
- Extreme angles
- Motion blur

### Recommended Image Collection

For each student, capture images with:
- **Frontal view:** Face directly toward camera (5-7 images)
- **Slight angles:** Small head turns (3-4 images)
- **Different expressions:** Neutral, smiling (2-3 images)
- **Lighting variations:** Different times of day (if possible)

## Database Schema

The system creates these tables:

- **students** - Student information
- **courses** - Course details
- **enrollments** - Student-course relationships
- **class_sessions** - Class session records
- **attendance** - Attendance records
- **settings** - System settings
- **system_logs** - Activity logs
- **notifications** - Notification queue

## Next Steps

After successful setup:

1. **Test Recognition:**
   - Run the application
   - Go to "Take Attendance"
   - Point camera at a registered student
   - Verify recognition works

2. **Add More Courses:**
   - Open application
   - Go to Settings
   - Add your actual courses

3. **Create Class Sessions:**
   - Navigate to attendance window
   - Create session for a course
   - Start marking attendance

4. **Generate Reports:**
   - Go to "View Records"
   - Filter by date, course, or student
   - Export to Excel or CSV

## Support

If you encounter issues:

1. Check `logs/attendance_system.log` for error messages
2. Verify all packages are installed: `pip list`
3. Ensure face images are in correct format (JPG/JPEG/PNG)
4. Test database connection: `python test_db.py`

## Manual Database Inspection

To inspect the database directly:

```bash
sqlite3 data/database/attendance.db

# List all tables
.tables

# View students
SELECT * FROM students;

# Count students
SELECT COUNT(*) FROM students;

# Exit
.quit
```
