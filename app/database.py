from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.config import DATABASE_URL, db_info

# Configure engine arguments based on engine type
if db_info["engine"] == "sqlite":
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False}, 
        echo=True
    )
else:
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=3600,
        pool_size=10,
        max_overflow=20,
        echo = True
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """Dependency that provides a database session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """
    Creates all database tables defined in models and seeds initial
    sample data if the database is newly initialized.
    """
    from app import models
    Base.metadata.create_all(bind=engine)
    
    # Auto-seed if tables are empty
    db = SessionLocal()
    try:
        dept_count = db.query(models.Department).count()
        if dept_count == 0:
            print("[Database] Empty database detected. Populating with initial seed data...")
            seed_initial_data(db)
            print("[Database] Seed data populated successfully!")
    except Exception as e:
        print(f"[Database Error during seed] {e}")
        db.rollback()
    finally:
        db.close()

def seed_initial_data(db):
    """Seed initial departments, courses, students, enrollments, and attendance."""
    from app import models
    from datetime import date

    if db.query(models.Department).count() > 0:
        return

    # 1. Departments
    cse = models.Department(
        code="CSE",
        name="Computer Science & Engineering",
        head_of_department="Dr. Alan Turing",
        description="Software development, artificial intelligence, and computing systems."
    )
    ece = models.Department(
        code="ECE",
        name="Electronics & Communication Engineering",
        head_of_department="Dr. Claude Shannon",
        description="Signal processing, embedded systems, and telecommunications."
    )
    mech = models.Department(
        code="MECH",
        name="Mechanical Engineering",
        head_of_department="Dr. James Watt",
        description="Mechanics, robotics, and thermal sciences."
    )
    bba = models.Department(
        code="BBA",
        name="Business Administration",
        head_of_department="Dr. Peter Drucker",
        description="Management, business strategy, and accounting."
    )
    db.add_all([cse, ece, mech, bba])
    db.flush()

    # 2. Courses
    c1 = models.Course(
        code="CS101",
        name="Intro to Programming (Python)",
        credits=4,
        department_id=cse.id,
        instructor="Prof. Guido van Rossum",
        description="Fundamentals of procedural & object-oriented programming."
    )
    c2 = models.Course(
        code="CS201",
        name="Database Management Systems",
        credits=4,
        department_id=cse.id,
        instructor="Prof. Edgar Codd",
        description="Relational database design, SQL, normalization, and ACID transactions."
    )
    c3 = models.Course(
        code="CS301",
        name="Web Application Engineering",
        credits=3,
        department_id=cse.id,
        instructor="Prof. Tim Berners-Lee",
        description="RESTful API design, FastAPI backends, and frontend architectures."
    )
    c4 = models.Course(
        code="EC101",
        name="Digital Electronics & Logic Design",
        credits=3,
        department_id=ece.id,
        instructor="Prof. Claude Shannon",
        description="Boolean algebra, logic gates, combinational and sequential circuits."
    )
    c5 = models.Course(
        code="ME101",
        name="Engineering Mechanics",
        credits=4,
        department_id=mech.id,
        instructor="Prof. Isaac Newton",
        description="Principles of static and dynamic equilibrium."
    )
    c6 = models.Course(
        code="BB101",
        name="Principles of Management",
        credits=3,
        department_id=bba.id,
        instructor="Prof. Mary Parker Follett",
        description="Foundations of modern management and organizational dynamics."
    )
    db.add_all([c1, c2, c3, c4, c5, c6])
    db.flush()

    # 3. Students
    s1 = models.Student(
        roll_number="STU-2024-001",
        first_name="Aarav",
        last_name="Sharma",
        email="aarav.sharma@example.edu",
        phone="+91 98765 43210",
        date_of_birth=date(2003, 5, 14),
        gender="Male",
        address="124 Park Avenue, Tech Hub",
        department_id=cse.id,
        year_of_study=2,
        semester=3,
        status="Active",
        enrollment_date=date(2023, 8, 1)
    )
    s2 = models.Student(
        roll_number="STU-2024-002",
        first_name="Sophia",
        last_name="Chen",
        email="sophia.chen@example.edu",
        phone="+1 415 555 2671",
        date_of_birth=date(2004, 2, 20),
        gender="Female",
        address="88 Silicon Blvd, San Jose",
        department_id=cse.id,
        year_of_study=1,
        semester=1,
        status="Active",
        enrollment_date=date(2024, 8, 1)
    )
    s3 = models.Student(
        roll_number="STU-2024-003",
        first_name="Liam",
        last_name="Johnson",
        email="liam.j@example.edu",
        phone="+1 212 555 8920",
        date_of_birth=date(2002, 11, 9),
        gender="Male",
        address="45 Broadway, New York",
        department_id=ece.id,
        year_of_study=3,
        semester=5,
        status="Active",
        enrollment_date=date(2022, 8, 1)
    )
    s4 = models.Student(
        roll_number="STU-2024-004",
        first_name="Priya",
        last_name="Patel",
        email="priya.patel@example.edu",
        phone="+91 91234 56789",
        date_of_birth=date(2003, 8, 25),
        gender="Female",
        address="12 Lake View Road, Bangalore",
        department_id=cse.id,
        year_of_study=2,
        semester=4,
        status="Active",
        enrollment_date=date(2023, 8, 1)
    )
    s5 = models.Student(
        roll_number="STU-2024-005",
        first_name="Mateo",
        last_name="Rodriguez",
        email="mateo.r@example.edu",
        phone="+34 91 123 4567",
        date_of_birth=date(2001, 7, 18),
        gender="Male",
        address="Gran Via 40, Madrid",
        department_id=mech.id,
        year_of_study=4,
        semester=7,
        status="Active",
        enrollment_date=date(2021, 8, 1)
    )
    s6 = models.Student(
        roll_number="STU-2024-006",
        first_name="Ananya",
        last_name="Iyer",
        email="ananya.iyer@example.edu",
        phone="+91 98220 11223",
        date_of_birth=date(2004, 1, 30),
        gender="Female",
        address="74 Gandhi Nagar, Chennai",
        department_id=bba.id,
        year_of_study=1,
        semester=2,
        status="Active",
        enrollment_date=date(2024, 8, 1)
    )
    s7 = models.Student(
        roll_number="STU-2024-007",
        first_name="Emma",
        last_name="Watson",
        email="emma.w@example.edu",
        phone="+44 20 7946 0912",
        date_of_birth=date(2000, 4, 15),
        gender="Female",
        address="221B Baker St, London",
        department_id=cse.id,
        year_of_study=4,
        semester=8,
        status="Graduated",
        enrollment_date=date(2020, 8, 1)
    )
    db.add_all([s1, s2, s3, s4, s5, s6, s7])
    db.flush()

    # 4. Enrollments & Grades
    e1 = models.Enrollment(student_id=s1.id, course_id=c1.id, semester_name="Fall 2023", grade="A", grade_point=4.00, status="Completed", enrolled_date=date(2023, 8, 10))
    e2 = models.Enrollment(student_id=s1.id, course_id=c2.id, semester_name="Spring 2024", grade="A-", grade_point=3.70, status="Completed", enrolled_date=date(2024, 1, 10))
    e3 = models.Enrollment(student_id=s1.id, course_id=c3.id, semester_name="Fall 2024", grade=None, grade_point=None, status="Enrolled", enrolled_date=date(2024, 8, 10))
    e4 = models.Enrollment(student_id=s2.id, course_id=c1.id, semester_name="Fall 2024", grade=None, grade_point=None, status="Enrolled", enrolled_date=date(2024, 8, 10))
    e5 = models.Enrollment(student_id=s3.id, course_id=c4.id, semester_name="Fall 2024", grade="B+", grade_point=3.30, status="Completed", enrolled_date=date(2024, 8, 10))
    e6 = models.Enrollment(student_id=s4.id, course_id=c2.id, semester_name="Spring 2024", grade="A", grade_point=4.00, status="Completed", enrolled_date=date(2024, 1, 10))
    e7 = models.Enrollment(student_id=s4.id, course_id=c3.id, semester_name="Fall 2024", grade=None, grade_point=None, status="Enrolled", enrolled_date=date(2024, 8, 10))
    e8 = models.Enrollment(student_id=s5.id, course_id=c5.id, semester_name="Fall 2024", grade="A-", grade_point=3.70, status="Completed", enrolled_date=date(2024, 8, 10))
    e9 = models.Enrollment(student_id=s6.id, course_id=c6.id, semester_name="Fall 2024", grade="A", grade_point=4.00, status="Completed", enrolled_date=date(2024, 8, 10))
    db.add_all([e1, e2, e3, e4, e5, e6, e7, e8, e9])
    db.flush()

    # 5. Attendance
    a1 = models.Attendance(student_id=s1.id, course_id=c3.id, date=date(2024, 9, 2), status="Present", remarks="Active engagement")
    a2 = models.Attendance(student_id=s1.id, course_id=c3.id, date=date(2024, 9, 4), status="Present", remarks="Full lecture")
    a3 = models.Attendance(student_id=s1.id, course_id=c3.id, date=date(2024, 9, 9), status="Late", remarks="10 mins late")
    a4 = models.Attendance(student_id=s2.id, course_id=c1.id, date=date(2024, 9, 2), status="Present", remarks="Attended")
    a5 = models.Attendance(student_id=s2.id, course_id=c1.id, date=date(2024, 9, 4), status="Absent", remarks="Medical reason")
    a6 = models.Attendance(student_id=s4.id, course_id=c3.id, date=date(2024, 9, 2), status="Present", remarks="Lab exercise finished")
    a7 = models.Attendance(student_id=s4.id, course_id=c3.id, date=date(2024, 9, 4), status="Present", remarks="Attended")
    db.add_all([a1, a2, a3, a4, a5, a6, a7])

    db.commit()

