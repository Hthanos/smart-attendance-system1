# Smart Class Attendance System
## USER MANUAL

**Version:** 1.0  
**Last Updated:** January 2025  
**For:** Teachers, Administrators, and End Users

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Getting Started](#2-getting-started)
3. [Dashboard](#3-dashboard)
4. [Student Management](#4-student-management)
5. [Taking Attendance](#5-taking-attendance)
6. [Viewing Records](#6-viewing-records)
7. [Reports and Export](#7-reports-and-export)
8. [Settings](#8-settings)
9. [Troubleshooting](#9-troubleshooting)
10. [FAQ](#10-faq)

---

## 1. INTRODUCTION

### 1.1 About the System

The Smart Class Attendance System is an automated attendance management solution that uses facial recognition technology to identify and mark student attendance. The system eliminates manual roll calls, prevents proxy attendance, and provides comprehensive attendance tracking and reporting.

### 1.2 Key Features

- ✅ **Automatic Face Recognition**: Identifies students using facial features
- ✅ **Real-time Processing**: Marks attendance in seconds
- ✅ **Student Management**: Register and manage student information
- ✅ **Course Management**: Create and manage courses and sessions
- ✅ **Comprehensive Reports**: Generate attendance reports in Excel/CSV
- ✅ **Search and Filter**: Find specific attendance records easily
- ✅ **Email & SMS Notifications**: Alert students about attendance status
- ✅ **User-Friendly Interface**: Intuitive GUI for easy operation

### 1.3 System Requirements

**Minimum Requirements**:
- Operating System: Windows 10/11, Linux (Ubuntu 18.04+), or macOS 10.14+
- Processor: Intel Core i3 or equivalent
- RAM: 4GB minimum (8GB recommended)
- Camera: USB Webcam (720p minimum) or Raspberry Pi Camera Module
- Storage: 5GB free space
- Python: 3.8 or higher

---

## 2. GETTING STARTED

### 2.1 Launching the Application

**Option 1: Using Run Script** (Linux/Mac):
```bash
cd /path/to/attendance-system
./run.sh
```

**Option 2: Using Python** (All Platforms):
```bash
cd /path/to/attendance-system
python app.py
```

**Option 3: Desktop Shortcut** (if configured):
- Double-click the attendance system icon on your desktop

### 2.2 First Launch

On first launch, the system will:
1. Initialize the database
2. Create necessary directories
3. Check camera availability
4. Display the main dashboard

**Default Admin Credentials** (if login is implemented):
- Username: `admin`
- Password: `admin123`
- *Please change these immediately in Settings*

### 2.3 Main Window Overview

The main window contains:
- **Title Bar**: Application name and status
- **Menu Bar**: Dashboard, Register Student, Take Attendance, View Records, Settings
- **Status Bar**: Current date/time, database status, camera status

---

## 3. DASHBOARD

The dashboard is your home screen showing key statistics and quick actions.

### 3.1 Statistics Cards

**Total Students**: Number of registered students in the system  
**Total Courses**: Number of courses created  
**Today's Sessions**: Number of class sessions scheduled for today  
**Total Records**: Total attendance records in the database

### 3.2 Today's Sessions Table

Shows all class sessions scheduled for today:
- **Course**: Course code and name
- **Time**: Start time
- **Location**: Classroom/venue
- **Present**: Number of students marked present
- **Total**: Total enrolled students
- **Attendance %**: Percentage of students present

**Actions**:
- Click on a session to view detailed attendance
- Use "Take Attendance" button to start marking for that session

### 3.3 Quick Actions

- **Register New Student**: Opens student registration window
- **Take Attendance**: Opens attendance marking window
- **View Records**: Opens records search window
- **Refresh**: Updates dashboard statistics

---

## 4. STUDENT MANAGEMENT

### 4.1 Registering a New Student

1. **Open Registration Window**:
   - Click "Register Student" from menu or dashboard

2. **Fill Student Information**:
   - **Full Name**: Student's complete name
   - **Registration Number**: Unique student ID (e.g., CSC/001/2023)
   - **Email**: Valid email address
   - **Phone Number**: Contact number (format: +254XXXXXXXXX)
   - **Course**: Select enrolled course from dropdown
   - **Year of Study**: Select year (1-4)
   - **Gender**: Select gender

3. **Capture Face Images**:
   - Click "Start Camera" to activate webcam
   - Position student's face in the camera view
   - Ensure:
     * Good lighting
     * Face clearly visible
     * No glasses/masks (or capture with and without)
     * Neutral expression
   - Click "Capture Images"
   - System will automatically capture 30+ images from different angles
   - Progress bar shows capture status

4. **Save Registration**:
   - Click "Save Student"
   - System will validate information and save to database
   - Face images stored in `data/faces/[registration_number]/`

### 4.2 Best Practices for Registration

**Lighting**:
- Use natural light or bright room lighting
- Avoid harsh shadows on face
- Position student facing light source

**Face Position**:
- Face should be centered in camera view
- Maintain 1-2 feet distance from camera
- Capture slight head turns (left, right, up, down)

**Quality**:
- Use high-quality webcam (720p minimum)
- Clean camera lens
- Ensure focus is sharp

**Multiple Captures**:
- Capture with different expressions (if student normally wears glasses, capture both with and without)
- Capture at different times of day for varying lighting

### 4.3 Updating Student Information

1. Go to "View Records" > "Students" tab
2. Select student to update
3. Click "Edit" button
4. Modify information as needed
5. Click "Save Changes"

*Note: To update face images, re-register the student (old images will be replaced)*

### 4.4 Deactivating/Deleting Students

**Deactivate** (recommended for graduated/transferred students):
- Select student
- Click "Deactivate"
- Student remains in database but won't appear in attendance

**Delete** (permanent):
- Select student
- Click "Delete"
- Confirm deletion
- *Warning: This removes all attendance history*

---

## 5. TAKING ATTENDANCE

### 5.1 Starting an Attendance Session

1. **Select Class Session**:
   - Open "Take Attendance" window
   - Select course and session from dropdown
   - Or create new session if not listed

2. **Start Camera**:
   - Click "Start Attendance"
   - Camera will activate
   - Face detection begins automatically

3. **Position Students**:
   - Students should stand/sit in front of camera
   - One student at a time (or multiple if system supports)
   - Maintain clear view of face

### 5.2 Automatic Recognition Process

When a face is detected:

1. **Face Detection**: Green rectangle appears around detected face
2. **Recognition**: System matches face against trained model
3. **Confidence Check**: Verifies recognition confidence (>60% default)
4. **Attendance Marking**: If recognized and confident:
   - Student name appears on screen
   - Attendance logged with timestamp
   - Beep sound (if enabled)
   - Green checkmark displayed

### 5.3 Attendance Status Indicators

**Green Rectangle + Name**: Student recognized and marked present  
**Blue Rectangle**: Face detected but not recognized  
**Red Rectangle**: Face detected but confidence too low  
**No Rectangle**: No face detected

### 5.4 Manual Attendance

If student is not recognized:

1. Click "Manual Entry" button
2. Search student by name or registration number
3. Select correct student
4. Click "Mark Present"
5. Add note: "Manual - Camera issue" or "Manual - Recognition failed"

### 5.5 Ending Attendance Session

1. Click "Stop Attendance"
2. Review marked students list
3. Add any missing students manually
4. Click "Complete Session"
5. System generates session summary

### 5.6 Late Arrivals

For students arriving after attendance:

1. Reopen same session
2. Start camera again
3. Mark late students
4. System automatically marks them as "Late" instead of "Present"

*Late threshold configured in Settings (default: 15 minutes after session start)*

---

## 6. VIEWING RECORDS

### 6.1 Search and Filter

**Filter Options**:
- **Student**: Select specific student or "All Students"
- **Course**: Select specific course or "All Courses"
- **Date Range**: From [date] to [date]
- **Status**: All, Present, Absent, Late

**Search Actions**:
1. Set desired filters
2. Click "Search"
3. Results appear in table below

### 6.2 Results Table

Columns displayed:
- **Date**: Attendance date
- **Time**: Timestamp
- **Student**: Student name
- **Reg No**: Registration number
- **Course**: Course name
- **Status**: Present/Absent/Late
- **Confidence**: Recognition confidence score

**Sorting**:
- Click column header to sort
- Click again to reverse sort

### 6.3 Viewing Details

- Double-click any record to view full details
- Details window shows:
  * Student photo
  * Complete student information
  * Session details
  * Attendance history for that course

### 6.4 Clear Filters

Click "Clear Filters" to reset all filters to defaults:
- All Students
- All Courses
- Last 7 days
- All statuses

---

## 7. REPORTS AND EXPORT

### 7.1 Generating Reports

**Quick Reports**:
1. Use filters to select desired records
2. Click "Export to Excel" or "Export to CSV"
3. Choose save location
4. Report generated with all filtered records

**Available Report Types**:
- Daily attendance report
- Weekly attendance summary
- Monthly attendance summary
- Student-wise attendance
- Course-wise attendance
- Defaulter report (students below threshold)

### 7.2 Excel Reports

Excel reports include:
- **Cover Page**: Report title, date range, institution details
- **Summary Sheet**: Overall statistics
- **Detailed Data**: Individual attendance records
- **Charts**: Attendance trends graph

**Features**:
- Color-coded status (Green=Present, Red=Absent, Orange=Late)
- Automatic calculations (attendance percentage)
- Formatted tables with borders
- Institution logo (if configured)

### 7.3 CSV Reports

Simple CSV files containing:
- All attendance records
- Compatible with Excel, Google Sheets, and other tools
- Easy to import into other systems

**Use CSV when**:
- Need to import data elsewhere
- Want maximum compatibility
- Don't need formatting/charts

### 7.4 Report Locations

Reports saved to:
```
data/exports/
├── attendance_YYYYMMDD_HHMMSS.xlsx
├── attendance_YYYYMMDD_HHMMSS.csv
└── ...
```

### 7.5 Printing Reports

1. Open exported Excel file
2. Review and adjust if needed
3. File > Print
4. Select printer and options
5. Print

---

## 8. SETTINGS

### 8.1 Recognition Settings

**Confidence Threshold**:
- Slider from 0-100
- Higher value = More strict (fewer false positives)
- Lower value = More lenient (may have false positives)
- **Recommended**: 60-70

**Minimum Training Images**:
- Number of face images required per student
- Default: 30
- More images = Better accuracy

**Auto-retrain Model**:
- Checkbox to enable/disable
- When enabled: Model retrains automatically when new students added
- When disabled: Manual training required

### 8.2 Institution Settings

Configure institution details (appears on reports):
- Institution Name
- Department
- Academic Year
- Semester

### 8.3 Camera Settings

**Camera Type**:
- USB Webcam: Standard USB camera
- Pi Camera: Raspberry Pi Camera Module

**Camera Index**:
- If multiple USB cameras, select which one (0, 1, 2...)

**Resolution**:
- Width and Height in pixels
- Common: 640x480, 1280x720, 1920x1080
- Higher resolution = Better quality, slower processing

**Target FPS**:
- Frames per second
- Higher = Smoother but more CPU usage
- Typical: 20-30 FPS

### 8.4 Model Management

**Train/Retrain Model**:
- Click to train recognition model with current student faces
- Required after:
  * Adding new students
  * Updating student photos
  * Initial setup
- Training takes 2-5 minutes depending on number of students

**Backup Model**:
- Save current trained model to backup file
- Useful before major changes

**Restore Model**:
- Load previously backed up model
- Use if training fails or results worse than before

### 8.5 Notification Settings

**Email Notifications**:
- SMTP server configuration
- Enable/disable email alerts
- Configure which events trigger emails

**SMS Notifications**:
- Africa's Talking API credentials
- Enable/disable SMS alerts
- Balance check

---

## 9. TROUBLESHOOTING

### 9.1 Common Issues

**Issue: Camera not working**

*Solutions*:
1. Check camera is properly connected
2. Try different USB port
3. Check camera permissions (allow app to access camera)
4. Test camera in different application
5. Update camera drivers
6. Change camera index in Settings

**Issue: Student not recognized**

*Solutions*:
1. Check lighting conditions
2. Ensure face clearly visible
3. Student should look at camera
4. Lower confidence threshold temporarily
5. Re-register student with more/better images
6. Retrain model

**Issue: Wrong student recognized**

*Solutions*:
1. Increase confidence threshold
2. Ensure good quality images during registration
3. Re-register both students with more distinct images
4. Use manual attendance and report issue

**Issue: System slow/laggy**

*Solutions*:
1. Close other applications
2. Reduce camera resolution
3. Lower FPS setting
4. Check system RAM usage
5. Consider hardware upgrade

**Issue: Database error**

*Solutions*:
1. Check database file not corrupted: `data/database/attendance.db`
2. Restore from backup if available
3. Check disk space
4. Run verify_setup.py script
5. Contact system administrator

**Issue: Export fails**

*Solutions*:
1. Check write permissions for exports folder
2. Ensure sufficient disk space
3. Close Excel if file already open
4. Try different export format (CSV instead of Excel)

### 9.2 Error Messages

**"No trained model found"**:
- Model needs training
- Go to Settings > Model > Train Model

**"Camera initialization failed"**:
- Camera not detected
- Check connections and permissions

**"Insufficient face images"**:
- Student needs more face captures during registration
- Minimum 30 images required

**"Database connection error"**:
- Database file missing or corrupted
- Check data/database/ directory

**"Confidence too low"**:
- Recognition not confident enough
- Use manual attendance or retrain model

### 9.3 Getting Help

**Check Logs**:
- Log files in `logs/` directory
- Look for ERROR or WARNING messages

**Documentation**:
- Read Developer Guide for technical details
- Check README.md for setup instructions

**Contact Support**:
- Email: support@example.com
- GitHub Issues: [repository URL]

---

## 10. FAQ

**Q: How many students can the system handle?**  
A: The system can handle hundreds of students. Larger numbers may require more powerful hardware.

**Q: Does it work with glasses/beard/hairstyle changes?**  
A: Yes, if you register with those features. For best results, capture images with and without glasses.

**Q: What if internet is down?**  
A: System works completely offline. Only email/SMS notifications require internet.

**Q: Can multiple teachers use the system?**  
A: Yes, implement user accounts (see Developer Guide for multi-user setup).

**Q: How long does training take?**  
A: Usually 2-5 minutes depending on number of students (1-2 seconds per student).

**Q: Can students use photos to fake attendance?**  
A: Basic LBPH can be fooled by photos. Consider upgrading to liveness detection for production use.

**Q: What happens if camera fails during attendance?**  
A: Use manual attendance mode. Fix camera for next session.

**Q: Can I use this on Raspberry Pi?**  
A: Yes! Select "picamera" in camera settings. Requires Raspberry Pi with camera module.

**Q: How to handle twins?**  
A: System may confuse twins. Use manual verification or add additional identifier (registration number check).

**Q: Can I integrate with existing student database?**  
A: Yes, see Developer Guide for database import instructions.

---

## APPENDIX A: Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| Ctrl+N | New Student Registration |
| Ctrl+T | Take Attendance |
| Ctrl+R | View Records |
| Ctrl+S | Settings |
| Ctrl+Q | Quit Application |
| Ctrl+P | Print Current View |
| F5 | Refresh Dashboard |
| Esc | Close Current Window |

---

## APPENDIX B: File Locations

| Data Type | Location |
|-----------|----------|
| Database | `data/database/attendance.db` |
| Face Images | `data/faces/[reg_number]/` |
| Trained Model | `data/models/trained_model.xml` |
| Exports | `data/exports/` |
| Logs | `logs/application.log` |
| Configuration | `.env` |

---

## APPENDIX C: Maintenance Tips

**Daily**:
- Backup database (automatic)
- Check log files for errors
- Test camera before first class

**Weekly**:
- Review attendance statistics
- Check for students with low attendance
- Clean camera lens

**Monthly**:
- Full database backup to external storage
- Review and archive old records
- Update system if new version available

**Semester Start**:
- Register new students
- Update courses
- Retrain model
- Review and update settings

**Semester End**:
- Generate final reports
- Archive semester data
- Deactivate graduated students

---

**For Technical Support**:  
Email: ramspheld@example.com  
Phone: +254 XXX XXX XXX  
Office Hours: Mon-Fri 8AM-5PM EAT

**Document Version**: 1.0  
**Last Updated**: January 2025  
**Next Review**: July 2025
