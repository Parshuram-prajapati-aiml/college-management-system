-- College Management System - BLDEA College of Engineering
-- Authoritative MySQL 8.0.x Schema DDL

CREATE DATABASE IF NOT EXISTS college_management_system;
USE college_management_system;

-- 1. user_account
CREATE TABLE IF NOT EXISTS user_account (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('ADMIN', 'TEACHER', 'STUDENT', 'ADMISSION_OFFICER') NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    status ENUM('ACTIVE', 'INACTIVE', 'LOCKED') DEFAULT 'ACTIVE',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 2. departments
CREATE TABLE IF NOT EXISTS departments (
    department_id INT AUTO_INCREMENT PRIMARY KEY,
    department_name VARCHAR(150) NOT NULL UNIQUE,
    department_code VARCHAR(30) NOT NULL UNIQUE,
    building VARCHAR(100) DEFAULT NULL,
    hod_name VARCHAR(150) DEFAULT NULL,
    hod_email VARCHAR(150) DEFAULT NULL,
    hod_phone VARCHAR(30) DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 3. programs
CREATE TABLE IF NOT EXISTS programs (
    program_id INT AUTO_INCREMENT PRIMARY KEY,
    department_id INT NOT NULL,
    program_name VARCHAR(150) NOT NULL UNIQUE,
    program_code VARCHAR(30) NOT NULL UNIQUE,
    description VARCHAR(1000) DEFAULT NULL,
    degree_type ENUM('UG', 'PG') DEFAULT 'UG',
    duration_years INT NOT NULL,
    capacity INT NOT NULL,
    status ENUM('ACTIVE', 'INACTIVE') DEFAULT 'ACTIVE',
    FOREIGN KEY (department_id) REFERENCES departments(department_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 4. staff
CREATE TABLE IF NOT EXISTS staff (
    staff_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    department_id INT DEFAULT NULL,
    first_name VARCHAR(80) NOT NULL,
    last_name VARCHAR(80) NOT NULL,
    staff_name VARCHAR(170) NOT NULL,
    designation VARCHAR(100) DEFAULT NULL,
    qualification VARCHAR(200) DEFAULT NULL,
    staff_type ENUM('TEACHER', 'ADMISSION_OFFICER', 'ADMINISTRATOR', 'OTHER') DEFAULT 'TEACHER',
    email VARCHAR(150) NOT NULL UNIQUE,
    phone VARCHAR(30) DEFAULT NULL,
    joining_date DATE DEFAULT NULL,
    experience_years INT DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES user_account(user_id) ON DELETE CASCADE,
    FOREIGN KEY (department_id) REFERENCES departments(department_id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 5. students
CREATE TABLE IF NOT EXISTS students (
    student_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    usn VARCHAR(30) NOT NULL UNIQUE,
    registration_number VARCHAR(50) NOT NULL UNIQUE,
    first_name VARCHAR(80) NOT NULL,
    last_name VARCHAR(80) NOT NULL,
    student_name VARCHAR(170) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    phone VARCHAR(30) DEFAULT NULL,
    address VARCHAR(500) DEFAULT NULL,
    date_of_birth DATE NOT NULL,
    gender ENUM('MALE', 'FEMALE', 'OTHER') DEFAULT NULL,
    department_id INT NOT NULL,
    program_id INT NOT NULL,
    admission_date DATE DEFAULT (CURDATE()),
    enrollment_date DATE DEFAULT (CURDATE()),
    academic_year VARCHAR(20) NOT NULL,
    semester VARCHAR(30) NOT NULL,
    gpa DECIMAL(3,2) DEFAULT 0.00,
    status ENUM('ACTIVE', 'PROBATION', 'GRADUATED', 'ON_LEAVE', 'INACTIVE') DEFAULT 'ACTIVE',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user_account(user_id) ON DELETE CASCADE,
    FOREIGN KEY (department_id) REFERENCES departments(department_id) ON DELETE CASCADE,
    FOREIGN KEY (program_id) REFERENCES programs(program_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 6. parents
CREATE TABLE IF NOT EXISTS parents (
    parent_id INT AUTO_INCREMENT PRIMARY KEY,
    parent_name VARCHAR(150) NOT NULL,
    relationship VARCHAR(50) DEFAULT NULL,
    phone VARCHAR(30) DEFAULT NULL,
    email VARCHAR(150) DEFAULT NULL,
    occupation VARCHAR(100) DEFAULT NULL,
    address VARCHAR(500) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 7. student_parent
CREATE TABLE IF NOT EXISTS student_parent (
    student_id INT NOT NULL,
    parent_id INT NOT NULL,
    is_primary TINYINT(1) DEFAULT 0,
    PRIMARY KEY (student_id, parent_id),
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
    FOREIGN KEY (parent_id) REFERENCES parents(parent_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 8. admissions
CREATE TABLE IF NOT EXISTS admissions (
    admission_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT DEFAULT NULL,
    usn VARCHAR(30) DEFAULT NULL,
    application_number VARCHAR(50) NOT NULL UNIQUE,
    program_id INT DEFAULT NULL,
    admission_year YEAR DEFAULT NULL,
    admission_type VARCHAR(50) DEFAULT NULL,
    admission_date DATE DEFAULT NULL,
    status ENUM('PENDING', 'UNDER_REVIEW', 'APPROVED', 'REJECTED', 'CANCELLED') DEFAULT 'PENDING',
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE SET NULL,
    FOREIGN KEY (program_id) REFERENCES programs(program_id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 9. applications
CREATE TABLE IF NOT EXISTS applications (
    application_id INT AUTO_INCREMENT PRIMARY KEY,
    application_number VARCHAR(50) NOT NULL UNIQUE,
    applicant_name VARCHAR(170) NOT NULL,
    email VARCHAR(150) NOT NULL,
    phone VARCHAR(30) DEFAULT NULL,
    program_id INT NOT NULL,
    application_date DATE DEFAULT (CURDATE()),
    status ENUM('PENDING', 'UNDER_REVIEW', 'DOCUMENTS_REQUIRED', 'APPROVED', 'REJECTED') DEFAULT 'PENDING',
    documents_path VARCHAR(500) DEFAULT NULL,
    notes VARCHAR(2000) DEFAULT NULL,
    FOREIGN KEY (program_id) REFERENCES programs(program_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 10. courses
CREATE TABLE IF NOT EXISTS courses (
    course_id INT AUTO_INCREMENT PRIMARY KEY,
    course_code VARCHAR(30) NOT NULL UNIQUE,
    course_name VARCHAR(150) NOT NULL,
    credits INT DEFAULT 3,
    department_id INT NOT NULL,
    semester VARCHAR(30) NOT NULL,
    FOREIGN KEY (department_id) REFERENCES departments(department_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 11. classes
CREATE TABLE IF NOT EXISTS classes (
    class_id INT AUTO_INCREMENT PRIMARY KEY,
    course_id INT NOT NULL,
    program_id INT NOT NULL,
    staff_id INT NOT NULL,
    academic_year VARCHAR(20) NOT NULL,
    semester VARCHAR(30) NOT NULL,
    schedule VARCHAR(100) DEFAULT NULL,
    room VARCHAR(50) DEFAULT NULL,
    capacity INT NOT NULL,
    FOREIGN KEY (course_id) REFERENCES courses(course_id) ON DELETE CASCADE,
    FOREIGN KEY (program_id) REFERENCES programs(program_id) ON DELETE CASCADE,
    FOREIGN KEY (staff_id) REFERENCES staff(staff_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 12. enrollments
CREATE TABLE IF NOT EXISTS enrollments (
    enrollment_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    class_id INT NOT NULL,
    enrollment_date DATE DEFAULT (CURDATE()),
    status ENUM('ENROLLED', 'COMPLETED', 'DROPPED') DEFAULT 'ENROLLED',
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
    FOREIGN KEY (class_id) REFERENCES classes(class_id) ON DELETE CASCADE,
    UNIQUE KEY uk_student_class (student_id, class_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 13. attendance
CREATE TABLE IF NOT EXISTS attendance (
    attendance_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    class_id INT NOT NULL,
    date_recorded DATE DEFAULT (CURDATE()),
    status ENUM('PRESENT', 'ABSENT') NOT NULL,
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
    FOREIGN KEY (class_id) REFERENCES classes(class_id) ON DELETE CASCADE,
    UNIQUE KEY uk_student_class_date (student_id, class_id, date_recorded)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 14. internal_marks
CREATE TABLE IF NOT EXISTS internal_marks (
    mark_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    class_id INT NOT NULL,
    assessment_name VARCHAR(100) NOT NULL,
    internal_marks DECIMAL(5,2) DEFAULT 0.00,
    assignment_marks DECIMAL(5,2) DEFAULT 0.00,
    exam_marks DECIMAL(5,2) DEFAULT 0.00,
    total_marks DECIMAL(5,2) DEFAULT 0.00,
    grade VARCHAR(5) NOT NULL,
    semester VARCHAR(30) NOT NULL,
    remarks VARCHAR(500) DEFAULT NULL,
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
    FOREIGN KEY (class_id) REFERENCES classes(class_id) ON DELETE CASCADE,
    UNIQUE KEY uk_student_class_assessment (student_id, class_id, assessment_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 15. documents
CREATE TABLE IF NOT EXISTS documents (
    document_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    document_type VARCHAR(100) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    original_name VARCHAR(255) DEFAULT NULL,
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    uploaded_by INT DEFAULT NULL,
    status ENUM('VERIFIED', 'PENDING', 'REJECTED') DEFAULT 'PENDING',
    rejection_reason VARCHAR(1000) DEFAULT NULL,
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
    FOREIGN KEY (uploaded_by) REFERENCES user_account(user_id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 16. document_receipts
CREATE TABLE IF NOT EXISTS document_receipts (
    receipt_id INT AUTO_INCREMENT PRIMARY KEY,
    document_id INT NOT NULL,
    receipt_number VARCHAR(100) NOT NULL UNIQUE,
    submission_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    remarks VARCHAR(1000) DEFAULT NULL,
    FOREIGN KEY (document_id) REFERENCES documents(document_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 17. study_materials
CREATE TABLE IF NOT EXISTS study_materials (
    material_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description VARCHAR(2000) DEFAULT NULL,
    course_id INT NOT NULL,
    class_id INT NOT NULL,
    staff_id INT NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_type VARCHAR(30) NOT NULL,
    academic_year VARCHAR(20) NOT NULL,
    semester VARCHAR(30) NOT NULL,
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    published_status ENUM('DRAFT', 'PUBLISHED', 'ARCHIVED') DEFAULT 'DRAFT',
    FOREIGN KEY (course_id) REFERENCES courses(course_id) ON DELETE CASCADE,
    FOREIGN KEY (class_id) REFERENCES classes(class_id) ON DELETE CASCADE,
    FOREIGN KEY (staff_id) REFERENCES staff(staff_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 18. announcements
CREATE TABLE IF NOT EXISTS announcements (
    announcement_id INT AUTO_INCREMENT PRIMARY KEY,
    staff_id INT NOT NULL,
    class_id INT DEFAULT NULL,
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    target_type ENUM('ALL', 'STUDENTS', 'CLASS') DEFAULT 'CLASS',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (staff_id) REFERENCES staff(staff_id) ON DELETE CASCADE,
    FOREIGN KEY (class_id) REFERENCES classes(class_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
