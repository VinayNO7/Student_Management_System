-- ========================================================
-- Student Management System Seed Data (MySQL)
-- ========================================================

USE student_management_db;

-- 1. Insert Departments
INSERT INTO departments (id, code, name, head_of_department, description) VALUES
(1, 'CSE', 'Computer Science and Engineering', 'Dr. Alan Turing', 'Focuses on software engineering, artificial intelligence, algorithms, and computer systems.'),
(2, 'ECE', 'Electronics and Communication Engineering', 'Dr. Claude Shannon', 'Covers signal processing, embedded systems, telecommunications, and microelectronics.'),
(3, 'MECH', 'Mechanical Engineering', 'Dr. James Watt', 'Focuses on thermodynamics, mechanics, robotics, and manufacturing systems.'),
(4, 'BBA', 'Business Administration', 'Dr. Peter Drucker', 'Encompasses management, financial accounting, marketing, and organizational leadership.'),
(5, 'BIO', 'Biotechnology', 'Dr. Rosalind Franklin', 'Covers molecular biology, genetics, bioinformatics, and bioprocess engineering.')
ON DUPLICATE KEY UPDATE name=VALUES(name);

-- 2. Insert Courses
INSERT INTO courses (id, code, name, credits, department_id, instructor, description) VALUES
(1, 'CS101', 'Introduction to Computer Science', 4, 1, 'Prof. Ada Lovelace', 'Foundations of programming, logic, and data structures.'),
(2, 'CS201', 'Database Management Systems', 4, 1, 'Prof. Edgar Codd', 'Relational database theory, SQL, transaction management, and indexing.'),
(3, 'CS301', 'Web Applications with FastAPI', 3, 1, 'Prof. Guido van Rossum', 'Modern web backend APIs, asynchronous Python, and frontend integration.'),
(4, 'EC101', 'Circuit Theory & Analysis', 3, 2, 'Prof. Nikola Tesla', 'DC/AC network analysis, theorems, resonance, and state variable analysis.'),
(5, 'ME101', 'Engineering Mechanics', 4, 3, 'Prof. Isaac Newton', 'Statics and dynamics of particles and rigid bodies.'),
(6, 'BB101', 'Principles of Management', 3, 4, 'Prof. Mary Parker Follett', 'Managerial functions, organizational behavior, and leadership strategies.')
ON DUPLICATE KEY UPDATE name=VALUES(name);

-- 3. Insert Students
INSERT INTO students (id, roll_number, first_name, last_name, email, phone, date_of_birth, gender, address, department_id, year_of_study, semester, status, enrollment_date) VALUES
(1, 'STU-2024-001', 'Aarav', 'Sharma', 'aarav.sharma@example.edu', '+91 98765 43210', '2003-05-14', 'Male', '124 Park Avenue, Tech City', 1, 2, 3, 'Active', '2023-08-01'),
(2, 'STU-2024-002', 'Sophia', 'Chen', 'sophia.chen@example.edu', '+1 415 555 2671', '2004-02-20', 'Female', '88 Maple Street, Silicon Valley', 1, 1, 1, 'Active', '2024-08-01'),
(3, 'STU-2024-003', 'Liam', 'Johnson', 'liam.j@example.edu', '+1 212 555 8920', '2002-11-09', 'Male', '45 Broadway, New York', 2, 3, 5, 'Active', '2022-08-01'),
(4, 'STU-2024-004', 'Priya', 'Patel', 'priya.patel@example.edu', '+91 91234 56789', '2003-08-25', 'Female', '12 Lake View Road, Bangalore', 1, 2, 4, 'Active', '2023-08-01'),
(5, 'STU-2024-005', 'Mateo', 'Rodriguez', 'mateo.r@example.edu', '+34 91 123 4567', '2001-07-18', 'Male', 'Gran Via 40, Madrid', 3, 4, 7, 'Active', '2021-08-01'),
(6, 'STU-2024-006', 'Ananya', 'Iyer', 'ananya.iyer@example.edu', '+91 98220 11223', '2004-01-30', 'Female', '74 Gandhi Nagar, Chennai', 4, 1, 2, 'Active', '2024-08-01'),
(7, 'STU-2024-007', 'Lucas', 'Silva', 'lucas.silva@example.edu', '+55 11 9876 5432', '2002-09-12', 'Male', 'Av. Paulista 1000, Sao Paulo', 1, 3, 6, 'Active', '2022-08-01'),
(8, 'STU-2024-008', 'Emma', 'Watson', 'emma.w@example.edu', '+44 20 7946 0912', '2000-04-15', 'Female', '221B Baker St, London', 1, 4, 8, 'Graduated', '2020-08-01')
ON DUPLICATE KEY UPDATE email=VALUES(email);

-- 4. Insert Enrollments & Grades
INSERT INTO enrollments (student_id, course_id, semester_name, grade, grade_point, status, enrolled_date) VALUES
(1, 1, 'Fall 2023', 'A', 4.00, 'Completed', '2023-08-10'),
(1, 2, 'Spring 2024', 'A-', 3.70, 'Completed', '2024-01-10'),
(1, 3, 'Fall 2024', NULL, NULL, 'Enrolled', '2024-08-10'),
(2, 1, 'Fall 2024', NULL, NULL, 'Enrolled', '2024-08-10'),
(3, 4, 'Fall 2024', 'B+', 3.30, 'Completed', '2024-08-10'),
(4, 2, 'Spring 2024', 'A', 4.00, 'Completed', '2024-01-10'),
(4, 3, 'Fall 2024', NULL, NULL, 'Enrolled', '2024-08-10'),
(5, 5, 'Fall 2024', 'A-', 3.70, 'Completed', '2024-08-10'),
(6, 6, 'Fall 2024', 'A', 4.00, 'Completed', '2024-08-10')
ON DUPLICATE KEY UPDATE status=VALUES(status);

-- 5. Insert Attendance
INSERT INTO attendance (student_id, course_id, date, status, remarks) VALUES
(1, 3, '2024-09-02', 'Present', 'Attended lecture and lab'),
(1, 3, '2024-09-04', 'Present', 'On time'),
(1, 3, '2024-09-09', 'Late', 'Late by 10 mins due to traffic'),
(2, 1, '2024-09-02', 'Present', 'Active participation'),
(2, 1, '2024-09-04', 'Absent', 'Sick leave notified'),
(4, 3, '2024-09-02', 'Present', 'Attended'),
(4, 3, '2024-09-04', 'Present', 'Submitted assignment')
ON DUPLICATE KEY UPDATE status=VALUES(status);

