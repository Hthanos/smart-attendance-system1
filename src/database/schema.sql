-- Smart Class Attendance System Database Schema
-- SQLite Database

-- Students table
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    registration_number TEXT UNIQUE NOT NULL,
    full_name TEXT NOT NULL,
    email TEXT,
    phone TEXT,
    department TEXT,
    year_of_study INTEGER,
    program TEXT,
    photo_path TEXT,
    face_encoding_path TEXT,
    date_registered TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active INTEGER DEFAULT 1,
    CONSTRAINT unique_reg_number UNIQUE (registration_number)
);

-- Create index on registration number for faster lookups
CREATE INDEX IF NOT EXISTS idx_students_reg_number ON students(registration_number);
CREATE INDEX IF NOT EXISTS idx_students_active ON students(is_active);

-- Courses table
CREATE TABLE IF NOT EXISTS courses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_code TEXT UNIQUE NOT NULL,
    course_name TEXT NOT NULL,
    instructor TEXT,
    semester TEXT,
    academic_year TEXT,
    credits INTEGER DEFAULT 3,
    description TEXT,
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_course_code UNIQUE (course_code)
);

CREATE INDEX IF NOT EXISTS idx_courses_code ON courses(course_code);
CREATE INDEX IF NOT EXISTS idx_courses_active ON courses(is_active);

-- Course enrollment - many-to-many relationship
CREATE TABLE IF NOT EXISTS enrollments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    course_id INTEGER NOT NULL,
    enrollment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'Active',
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
    CONSTRAINT unique_enrollment UNIQUE (student_id, course_id)
);

CREATE INDEX IF NOT EXISTS idx_enrollments_student ON enrollments(student_id);
CREATE INDEX IF NOT EXISTS idx_enrollments_course ON enrollments(course_id);

-- Class sessions table
CREATE TABLE IF NOT EXISTS class_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_id INTEGER NOT NULL,
    session_date DATE NOT NULL,
    start_time TIME,
    end_time TIME,
    location TEXT,
    topic TEXT,
    session_type TEXT DEFAULT 'Lecture',
    is_completed INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_sessions_course ON class_sessions(course_id);
CREATE INDEX IF NOT EXISTS idx_sessions_date ON class_sessions(session_date);

-- Attendance records table
CREATE TABLE IF NOT EXISTS attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    session_id INTEGER NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    confidence_score REAL,
    status TEXT DEFAULT 'Present',
    marked_by TEXT DEFAULT 'System',
    notes TEXT,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (session_id) REFERENCES class_sessions(id) ON DELETE CASCADE,
    CONSTRAINT unique_attendance UNIQUE(student_id, session_id)
);

CREATE INDEX IF NOT EXISTS idx_attendance_student ON attendance(student_id);
CREATE INDEX IF NOT EXISTS idx_attendance_session ON attendance(session_id);
CREATE INDEX IF NOT EXISTS idx_attendance_timestamp ON attendance(timestamp);

-- System settings table
CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    description TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert default settings
INSERT OR IGNORE INTO settings (key, value, description) VALUES
    ('recognition_threshold', '50', 'Minimum confidence score for face recognition'),
    ('min_images_per_student', '30', 'Minimum face images required for training'),
    ('attendance_grace_period', '15', 'Minutes after class start to mark late'),
    ('system_initialized', 'true', 'System initialization flag'),
    ('last_training_date', '', 'Last model training timestamp');

-- System logs table (optional - for audit trail)
CREATE TABLE IF NOT EXISTS system_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    log_level TEXT DEFAULT 'INFO',
    module TEXT,
    message TEXT,
    details TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_logs_timestamp ON system_logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_logs_level ON system_logs(log_level);

-- Views for common queries

-- View: Student attendance summary
CREATE VIEW IF NOT EXISTS view_student_attendance_summary AS
SELECT 
    s.id,
    s.registration_number,
    s.full_name,
    s.department,
    COUNT(DISTINCT a.session_id) as total_classes_attended,
    COUNT(DISTINCT cs.id) as total_classes,
    ROUND(CAST(COUNT(DISTINCT a.session_id) AS REAL) / 
          NULLIF(COUNT(DISTINCT cs.id), 0) * 100, 2) as attendance_percentage
FROM students s
LEFT JOIN enrollments e ON s.id = e.student_id
LEFT JOIN class_sessions cs ON e.course_id = cs.course_id
LEFT JOIN attendance a ON s.id = a.student_id AND cs.id = a.session_id
WHERE s.is_active = 1
GROUP BY s.id, s.registration_number, s.full_name, s.department;

-- View: Course attendance summary
CREATE VIEW IF NOT EXISTS view_course_attendance_summary AS
SELECT 
    c.id,
    c.course_code,
    c.course_name,
    COUNT(DISTINCT cs.id) as total_sessions,
    COUNT(DISTINCT e.student_id) as enrolled_students,
    COUNT(DISTINCT a.id) as total_attendance_records,
    ROUND(CAST(COUNT(DISTINCT a.id) AS REAL) / 
          NULLIF(COUNT(DISTINCT cs.id) * COUNT(DISTINCT e.student_id), 0) * 100, 2) as avg_attendance_rate
FROM courses c
LEFT JOIN class_sessions cs ON c.id = cs.course_id
LEFT JOIN enrollments e ON c.id = e.course_id
LEFT JOIN attendance a ON cs.id = a.session_id AND e.student_id = a.student_id
WHERE c.is_active = 1
GROUP BY c.id, c.course_code, c.course_name;

-- View: Today's attendance
CREATE VIEW IF NOT EXISTS view_todays_attendance AS
SELECT 
    cs.id as session_id,
    c.course_code,
    c.course_name,
    cs.session_date,
    cs.start_time,
    cs.location,
    COUNT(DISTINCT e.student_id) as expected_students,
    COUNT(DISTINCT a.student_id) as present_students,
    ROUND(CAST(COUNT(DISTINCT a.student_id) AS REAL) / 
          NULLIF(COUNT(DISTINCT e.student_id), 0) * 100, 2) as attendance_rate
FROM class_sessions cs
JOIN courses c ON cs.course_id = c.id
LEFT JOIN enrollments e ON c.id = e.course_id
LEFT JOIN attendance a ON cs.id = a.session_id AND e.student_id = a.student_id
WHERE cs.session_date = DATE('now')
GROUP BY cs.id, c.course_code, c.course_name, cs.session_date, cs.start_time, cs.location;
