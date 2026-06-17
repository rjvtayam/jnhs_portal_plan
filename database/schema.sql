-- ============================================
-- JNHS PORTAL - PostgreSQL Database Schema
-- ============================================

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('admin', 'teacher', 'student', 'parent', 'registrar')),
    email VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP WITH TIME ZONE
);

-- Students table
CREATE TABLE IF NOT EXISTS students (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id) ON DELETE SET NULL,
    lrn VARCHAR(20) UNIQUE NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    middle_name VARCHAR(50),
    last_name VARCHAR(50) NOT NULL,
    extension_name VARCHAR(10),
    birth_date DATE,
    gender VARCHAR(10),
    address TEXT,
    contact_number VARCHAR(15),
    guardian_name VARCHAR(100),
    guardian_contact VARCHAR(15),
    photo_url VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Teachers table
CREATE TABLE IF NOT EXISTS teachers (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id) ON DELETE SET NULL,
    employee_id VARCHAR(20) UNIQUE,
    first_name VARCHAR(50) NOT NULL,
    middle_name VARCHAR(50),
    last_name VARCHAR(50) NOT NULL,
    department VARCHAR(50),
    specialization VARCHAR(100),
    contact_number VARCHAR(15),
    is_adviser BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Parents table
CREATE TABLE IF NOT EXISTS parents (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id) ON DELETE SET NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    contact_number VARCHAR(15),
    email VARCHAR(100),
    address TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Parent-Student link
CREATE TABLE IF NOT EXISTS parent_student (
    parent_id INT REFERENCES parents(id) ON DELETE CASCADE,
    student_id INT REFERENCES students(id) ON DELETE CASCADE,
    relationship VARCHAR(30),
    PRIMARY KEY (parent_id, student_id)
);

-- Sections table
CREATE TABLE IF NOT EXISTS sections (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    grade_level VARCHAR(10) NOT NULL,
    track VARCHAR(20),
    school_year VARCHAR(10) NOT NULL,
    adviser_id INT REFERENCES teachers(id) ON DELETE SET NULL,
    max_students INT DEFAULT 50,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Subjects table
CREATE TABLE IF NOT EXISTS subjects (
    id SERIAL PRIMARY KEY,
    code VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    grade_level VARCHAR(10) NOT NULL,
    track VARCHAR(20),
    semester VARCHAR(10),
    is_specialized BOOLEAN DEFAULT FALSE,
    description TEXT
);

-- Section-Subject assignments
CREATE TABLE IF NOT EXISTS section_subjects (
    id SERIAL PRIMARY KEY,
    section_id INT REFERENCES sections(id) ON DELETE CASCADE,
    subject_id INT REFERENCES subjects(id) ON DELETE CASCADE,
    teacher_id INT REFERENCES teachers(id) ON DELETE SET NULL,
    schedule VARCHAR(100),
    room VARCHAR(50)
);

-- Enrollments table
CREATE TABLE IF NOT EXISTS enrollments (
    id SERIAL PRIMARY KEY,
    student_id INT REFERENCES students(id) ON DELETE CASCADE,
    section_id INT REFERENCES sections(id) ON DELETE CASCADE,
    school_year VARCHAR(10) NOT NULL,
    semester VARCHAR(10),
    status VARCHAR(20) DEFAULT 'enrolled',
    date_enrolled TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    date_graduated TIMESTAMP WITH TIME ZONE,
    date_transferred TIMESTAMP WITH TIME ZONE,
    remarks TEXT
);

-- Grades table
CREATE TABLE IF NOT EXISTS grades (
    id SERIAL PRIMARY KEY,
    student_id INT REFERENCES students(id) ON DELETE CASCADE,
    subject_id INT REFERENCES subjects(id) ON DELETE CASCADE,
    section_id INT REFERENCES sections(id) ON DELETE CASCADE,
    school_year VARCHAR(10) NOT NULL,
    semester VARCHAR(10),
    quarter VARCHAR(5) NOT NULL CHECK (quarter IN ('Q1', 'Q2', 'Q3', 'Q4')),

    -- Written Work
    ww_score DECIMAL(5,2),
    ww_possible DECIMAL(5,2),
    ww_percentage DECIMAL(5,2),

    -- Performance Tasks
    pt_score DECIMAL(5,2),
    pt_possible DECIMAL(5,2),
    pt_percentage DECIMAL(5,2),

    -- Quarterly Assessment
    qa_score DECIMAL(5,2),
    qa_possible DECIMAL(5,2),
    qa_percentage DECIMAL(5,2),

    -- Computed Grades
    raw_grade DECIMAL(5,2),
    transmuted_grade DECIMAL(5,2),

    remarks TEXT,
    encoded_by INT REFERENCES users(id),
    encoded_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(student_id, subject_id, quarter, school_year)
);

-- Attendance table
CREATE TABLE IF NOT EXISTS attendance (
    id SERIAL PRIMARY KEY,
    student_id INT REFERENCES students(id) ON DELETE CASCADE,
    section_id INT REFERENCES sections(id) ON DELETE CASCADE,
    subject_id INT REFERENCES subjects(id) ON DELETE SET NULL,
    date DATE NOT NULL,
    status VARCHAR(10) NOT NULL CHECK (status IN ('present', 'absent', 'late', 'excused')),
    remarks TEXT,
    recorded_by INT REFERENCES users(id),
    recorded_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Announcements table
CREATE TABLE IF NOT EXISTS announcements (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    target_audience VARCHAR(50) DEFAULT 'all',
    target_grade_levels VARCHAR(100),
    priority VARCHAR(10) DEFAULT 'normal',
    is_active BOOLEAN DEFAULT TRUE,
    posted_by INT REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Events table
CREATE TABLE IF NOT EXISTS events (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    event_date TIMESTAMP NOT NULL,
    event_time TIMESTAMP,
    end_date TIMESTAMP,
    location VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    created_by INT REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Documents table
CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    student_id INT REFERENCES students(id) ON DELETE SET NULL,
    document_type VARCHAR(50),
    school_year VARCHAR(10),
    semester VARCHAR(10),
    file_path VARCHAR(255),
    generated_by INT REFERENCES users(id),
    generated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- School settings table
CREATE TABLE IF NOT EXISTS school_settings (
    id SERIAL PRIMARY KEY,
    school_year VARCHAR(10) NOT NULL,
    semester VARCHAR(10),
    current_quarter VARCHAR(5),
    is_active BOOLEAN DEFAULT FALSE,
    grading_weights JSONB,
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Indexes
CREATE INDEX idx_students_lrn ON students(lrn);
CREATE INDEX idx_students_name ON students(last_name, first_name);
CREATE INDEX idx_grades_student ON grades(student_id);
CREATE INDEX idx_grades_section ON grades(section_id);
CREATE INDEX idx_grades_quarter ON grades(school_year, quarter);
CREATE INDEX idx_attendance_student ON attendance(student_id);
CREATE INDEX idx_attendance_date ON attendance(date);
CREATE INDEX idx_enrollments_school_year ON enrollments(school_year);
CREATE INDEX idx_announcements_active ON announcements(is_active, created_at DESC);
