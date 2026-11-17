# 🎓 EduTrack — Student Management System (DBMS)

A complete, production-grade **Student Management System** built with **MySQL** for the relational DBMS, **Python FastAPI** for high-performance backend REST APIs, and a modern, responsive **Frontend Dashboard** (HTML5, Tailwind CSS, FontAwesome, Chart.js, Vanilla JavaScript).

---

## 🌟 Key Features

### 👨‍🎓 1. Student Management (Core CRUD)
- **Student Registration**: Capture Roll Number, First & Last Name, Email, Phone, Date of Birth, Gender, Address, Department, Year of Study, Semester, Status, and Enrollment Date.
- **Real-Time Search & Multi-Filters**: Instant client-side & server-side search by name, roll number, or email, with filters for Department, Status (`Active`, `Graduated`, `Suspended`, `Inactive`), and Semester.
- **Detailed Student Profile**: Modal profile drawer showing student bio, enrolled courses, letter grades, computed GPA, and attendance history with percentage.
- **Export Data**: Single-click export of all student records to downloadable **CSV** (`/api/students/export/csv`).
- **Update & Soft/Hard Delete**: Edit student records anytime or delete with confirmation modals.

### 📚 2. Course Offerings & Curriculum
- Manage course catalog with Course Code, Course Name, Credit Units (1-10), Department mapping, Instructor, and Syllabus description.
- Filter courses by department.
- Add, update, and remove courses.

### 🏢 3. Academic Departments
- Manage departments with Department Code (e.g. `CSE`, `ECE`, `MECH`, `BBA`), Full Name, Head of Department (HOD), and Description.
- Live counters showing enrolled students and active course offerings per department.
- Relational integrity check: prevents accidental deletion if students are enrolled.

### 📝 4. Enrollments & Grade Management (GPA)
- Enroll students into courses for specific academic terms (e.g., `Fall 2024`, `Spring 2025`).
- Assign and update letter grades (`A+`, `A`, `A-`, `B+`, `B`, `B-`, `C+`, `C`, `D`, `F`).
- Automated grade point conversion (4.0 scale) and weighted cumulative GPA calculation.

### 📅 5. Attendance Tracking
- Mark attendance per course and date with statuses: **Present**, **Absent**, **Late**, **Excused**.
- Optional remarks (e.g., medical leave, late arrival reasons).
- Automatic attendance rate (%) calculation displayed on each student's profile.

### 📊 6. Interactive Dashboard & Analytics
- Live KPI summary cards: Total Students, Active Students, Courses, Departments, Average GPA.
- Interactive **Chart.js** doughnut chart displaying student distribution across academic departments.
- Recent student activities table.

### 🗄️ 7. Dual DBMS Architecture (MySQL + Auto-Fallback)
- **Primary DBMS**: Relational MySQL with InnoDB engine, Foreign Keys, cascading rules, unique indexes, and utf8mb4 encoding.
- **Smart Fallback**: If MySQL is not running on your machine, the system automatically falls back to local SQLite (`student_management.db`) so you can test and use the application without any setup friction!
- **System Settings Panel**: Live connection status badge in the navbar and a dedicated diagnostics page showing target host, port, database, and status.

---

## 🏗️ Project Structure

```
Student_Management_System_DBMS/
├── app/
│   ├── __init__.py
│   ├── config.py           # Environment variables, MySQL auto-connector & fallback
│   ├── database.py         # SQLAlchemy engine, session maker, auto-seeder
│   ├── models.py           # Relational ORM models (Department, Student, Course, Enrollment, Attendance)
│   ├── schemas.py          # Pydantic v2 schemas for request validation & serialization
│   ├── crud.py             # Database query operations and GPA/attendance calculations
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── students.py     # Student endpoints (CRUD, search, CSV export)
│   │   ├── departments.py  # Department endpoints
│   │   ├── courses.py      # Course endpoints
│   │   ├── enrollments.py  # Enrollments & Grades endpoints
│   │   ├── attendance.py   # Attendance tracking endpoints
│   │   └── analytics.py    # Analytics & system status endpoints
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css   # Custom styles, transitions, badges
│   │   └── js/
│   │       ├── api.js      # Fetch API wrapper
│   │       └── app.js      # SPA dashboard interactivity, modals, charts, toasts
│   └── templates/
│       └── index.html      # Single Page Application Dashboard
├── database/
│   ├── schema.sql          # Raw MySQL DDL schema
│   ├── seed.sql            # Raw MySQL sample seed data
│   └── seed_data.py        # Python automated database seeder
├── tests/
│   └── test_api.py         # Automated pytest suite (7 test suites)
├── .env.example            # Sample configuration file
├── .env                    # Active configuration file
├── requirements.txt        # Python dependencies
├── main.py                 # FastAPI application entry point
├── run.py                  # CLI launch script with terminal banner
└── README.md               # Complete documentation
```

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- **Python 3.10+** (Tested on Python 3.10 through 3.14)
- **MySQL Server** (MySQL 8.0+, MariaDB, or XAMPP) — *optional for first run thanks to automatic SQLite fallback!*

### 2. Clone / Open Directory
```bash
cd Student_Management_System_DBMS
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure MySQL Database
Edit the `.env` file with your MySQL credentials:
```ini
# MySQL Database Configuration
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=student_management_db

# Fallback: if MySQL is unreachable, uses SQLite seamlessly
FALLBACK_TO_SQLITE=True
```

> **Note**: If MySQL server is running, the app automatically executes `CREATE DATABASE IF NOT EXISTS student_management_db` and builds all tables on launch!
> You can also import the schema manually into MySQL:
> ```bash
> mysql -u root -p < database/schema.sql
> mysql -u root -p < database/seed.sql
> ```

### 5. Launch the Application
Run the launcher:
```bash
python run.py
```
Or with Uvicorn directly:
```bash
uvicorn main:app --reload
```

Open your browser to:
- 🌐 **Web Dashboard**: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- 📖 **Interactive Swagger API Docs**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- 📑 **ReDoc Documentation**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## 🧪 Running Automated Tests

Run the test suite using `pytest`:
```bash
python -m pytest tests/ -v
```

All 7 test suites verify:
- System health and database connectivity
- Dashboard statistics and KPI aggregations
- Department CRUD and integrity constraints
- Student registration, search, duplicate prevention, and CSV export
- Course offerings management
- Course enrollments, grade point mapping, and GPA calculation
- Attendance logging and deletion

---

## 📡 REST API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Serves the interactive Web Application |
| `GET` | `/api/system/status` | Current database engine & connection info |
| `GET` | `/api/analytics/stats` | KPI metrics & department distribution |
| **Students** | | |
| `GET` | `/api/students` | List students (filters: search, dept, status, sem) |
| `POST` | `/api/students` | Register a new student |
| `GET` | `/api/students/export/csv` | Download student roster as CSV file |
| `GET` | `/api/students/{id}` | Get basic student profile |
| `GET` | `/api/students/{id}/detail` | Full student profile with courses & attendance |
| `PUT` | `/api/students/{id}` | Update student details |
| `DELETE` | `/api/students/{id}` | Delete a student |
| **Courses** | | |
| `GET` | `/api/courses` | List courses (optional `department_id` filter) |
| `POST` | `/api/courses` | Create a new course |
| `GET` | `/api/courses/{id}` | Get course details |
| `PUT` | `/api/courses/{id}` | Update course info |
| `DELETE` | `/api/courses/{id}` | Delete a course |
| **Departments** | | |
| `GET` | `/api/departments` | List all departments with student/course counts |
| `POST` | `/api/departments` | Add a department |
| `PUT` | `/api/departments/{id}` | Update department details |
| `DELETE` | `/api/departments/{id}` | Delete department (validates no enrolled students) |
| **Enrollments & Grades** | | |
| `GET` | `/api/enrollments` | List enrollments (filters: student, course, sem) |
| `POST` | `/api/enrollments` | Enroll a student in a course |
| `PUT` | `/api/enrollments/{id}` | Assign/update letter grade or status |
| `DELETE` | `/api/enrollments/{id}` | Drop/remove an enrollment |
| **Attendance** | | |
| `GET` | `/api/attendance` | List attendance records (filters: student, course, date) |
| `POST` | `/api/attendance` | Mark student attendance (Present/Absent/Late/Excused) |
| `DELETE` | `/api/attendance/{id}` | Delete an attendance record |

---

## 🛡️ License & Credits
Built with ❤️ using FastAPI, SQLAlchemy, MySQL, and Tailwind CSS.
Licensed under the MIT License.

