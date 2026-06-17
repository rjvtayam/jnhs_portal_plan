-- ============================================
-- JNHS PORTAL - Seed Data
-- ============================================

-- School Year Settings
INSERT INTO school_settings (school_year, semester, current_quarter, is_active)
VALUES ('2025-2026', '1st', 'Q1', TRUE);

-- ============================================
-- Junior High School Subjects (Grades 7-10)
-- ============================================

-- Grade 7
INSERT INTO subjects (code, name, grade_level) VALUES
('FIL7', 'Filipino', '7'),
('ENG7', 'English', '7'),
('MATH7', 'Mathematics', '7'),
('SCI7', 'Science', '7'),
('AP7', 'Araling Panlipunan', '7'),
('MAPEH7', 'MAPEH', '7'),
('TLE7', 'Technology and Livelihood Education', '7'),
('ESP7', 'Edukasyon sa Pagpapakatao', '7'),
('COMP7', 'Computer Education', '7');

-- Grade 8
INSERT INTO subjects (code, name, grade_level) VALUES
('FIL8', 'Filipino', '8'),
('ENG8', 'English', '8'),
('MATH8', 'Mathematics', '8'),
('SCI8', 'Science', '8'),
('AP8', 'Araling Panlipunan', '8'),
('MAPEH8', 'MAPEH', '8'),
('TLE8', 'Technology and Livelihood Education', '8'),
('ESP8', 'Edukasyon sa Pagpapakatao', '8'),
('COMP8', 'Computer Education', '8');

-- Grade 9
INSERT INTO subjects (code, name, grade_level) VALUES
('FIL9', 'Filipino', '9'),
('ENG9', 'English', '9'),
('MATH9', 'Mathematics', '9'),
('SCI9', 'Science', '9'),
('AP9', 'Araling Panlipunan', '9'),
('MAPEH9', 'MAPEH', '9'),
('TLE9', 'Technology and Livelihood Education', '9'),
('ESP9', 'Edukasyon sa Pagpapakatao', '9'),
('COMP9', 'Computer Education', '9');

-- Grade 10
INSERT INTO subjects (code, name, grade_level) VALUES
('FIL10', 'Filipino', '10'),
('ENG10', 'English', '10'),
('MATH10', 'Mathematics', '10'),
('SCI10', 'Science', '10'),
('AP10', 'Araling Panlipunan', '10'),
('MAPEH10', 'MAPEH', '10'),
('TLE10', 'Technology and Livelihood Education', '10'),
('ESP10', 'Edukasyon sa Pagpapakatao', '10'),
('COMP10', 'Computer Education', '10');

-- ============================================
-- Senior High School Subjects (Grades 11-12)
-- ============================================

-- Core Subjects
INSERT INTO subjects (code, name, grade_level, semester) VALUES
('COMM11', 'Oral Communication', '11', '1st'),
('RWRIT11', 'Reading and Writing Skills', '11', '1st'),
('MAS11', 'Mathematics in the Modern World', '11', '1st'),
('FIL11', 'Komunikasyon at Pananaliksik sa Wika at Kulturang Pilipino', '11', '1st'),
('EARTH11', 'Earth and Life Science', '11', '1st'),
('PE11', 'Physical Education and Health', '11', '1st'),
('RHIST11', 'Reading and Writing Skills', '11', '2nd'),
('CONTEMP11', 'Contemporary Arts from the Regions', '11', '2nd'),
('PHILO11', 'Introduction to Philosophy of the Human Person', '11', '2nd'),
('PE12', 'Physical Education and Health', '12', '1st'),
('ENTREP12', 'Entrepreneurship', '12', '1st'),
('INTECH12', 'Empowerment Technologies', '12', '1st');

-- STEM Track
INSERT INTO subjects (code, name, grade_level, track, semester, is_specialized) VALUES
('PRECAL11', 'Pre-Calculus', '11', 'STEM', '1st', TRUE),
('BASICCAL11', 'Basic Calculus', '11', 'STEM', '2nd', TRUE),
('GENBIO11', 'General Biology 1', '11', 'STEM', '1st', TRUE),
('GENCHEM11', 'General Chemistry 1', '11', 'STEM', '2nd', TRUE),
('GENPHY11', 'General Physics 1', '11', 'STEM', '2nd', TRUE),
('GENBIO12', 'General Biology 2', '12', 'STEM', '1st', TRUE),
('GENCHEM12', 'General Chemistry 2', '12', 'STEM', '1st', TRUE),
('GENPHY12', 'General Physics 2', '12', 'STEM', '2nd', TRUE);

-- ABM Track
INSERT INTO subjects (code, name, grade_level, track, semester, is_specialized) VALUES
('FUNDABM11', 'Fundamentals of Accountancy, Business and Management 1', '11', 'ABM', '1st', TRUE),
('FUNDABM12', 'Fundamentals of Accountancy, Business and Management 2', '12', 'ABM', '1st', TRUE),
('BUSMAN11', 'Business Math', '11', 'ABM', '2nd', TRUE),
('HUMSS11', 'Humanities from the Regions', '11', 'HUMSS', '1st', TRUE);

-- HUMSS Track
INSERT INTO subjects (code, name, grade_level, track, semester, is_specialized) VALUES
('CREAWR11', 'Creative Writing', '11', 'HUMSS', '1st', TRUE),
('TRENDS11', 'Trends, Networks, and Critical Thinking in the 21st Century', '11', 'HUMSS', '2nd', TRUE),
('PHILO12', 'Philosophy of the Human Person', '12', 'HUMSS', '1st', TRUE);

-- GAS Track
INSERT INTO subjects (code, name, grade_level, track, semester, is_specialized) VALUES
('GAS11', 'General Academic Strand Elective 1', '11', 'GAS', '1st', TRUE),
('GAS12', 'General Academic Strand Elective 2', '12', 'GAS', '1st', TRUE);

-- Default Admin User (password: admin123)
INSERT INTO users (username, password_hash, role, email) VALUES
('admin', '$2b$12$LJ3m4ys4Gz8k5Q8q5Q8q5uQ8q5Q8q5Q8q5Q8q5Q8q5Q8q5Q8q5', 'admin', 'admin@jnhs.edu.ph');

-- Super Admin (password: superadmin123)
INSERT INTO users (username, password_hash, role, email) VALUES
('superadmin', '$2b$12$LJ3m4ys4Gz8k5Q8q5Q8q5uQ8q5Q8q5Q8q5Q8q5Q8q5Q8q5Q8q5', 'super_admin', 'superadmin@jnhs.edu.ph');

-- Principal (password: principal123)
INSERT INTO users (username, password_hash, role, email) VALUES
('principal', '$2b$12$LJ3m4ys4Gz8k5Q8q5Q8q5uQ8q5Q8q5Q8q5Q8q5Q8q5Q8q5Q8q5', 'principal', 'principal@jnhs.edu.ph');
