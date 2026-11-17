import pytest
from app.database import SessionLocal, init_db
from app.routers import students, departments, courses, enrollments, attendance, analytics
from app import schemas, crud
from datetime import date
from decimal import Decimal

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    init_db()

@pytest.fixture
def db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

def test_system_status():
    status = analytics.get_system_status()
    assert status.connected is True
    assert status.engine in ["mysql", "sqlite"]

def test_dashboard_stats(db):
    stats = analytics.get_dashboard_stats(db)
    assert stats.total_students >= 1
    assert stats.total_departments >= 4
    assert stats.total_courses >= 6
    assert stats.average_gpa > 0

def test_departments_operations(db):
    # 1. List
    dept_list = departments.list_departments(db)
    initial_count = len(dept_list)
    assert initial_count >= 4

    # 2. Create
    new_dept = schemas.DepartmentCreate(
        code="AI_DS",
        name="Artificial Intelligence & Data Science",
        head_of_department="Dr. Geoffrey Hinton",
        description="Machine learning, deep neural nets, and data systems."
    )
    created = departments.create_department(new_dept, db)
    assert created.code == "AI_DS"
    dept_id = created.id

    # 3. Read
    fetched = departments.get_department(dept_id, db)
    assert fetched.name == "Artificial Intelligence & Data Science"

    # 4. Update
    updated = departments.update_department(
        dept_id,
        schemas.DepartmentUpdate(name="AI and Advanced Data Science"),
        db
    )
    assert updated.name == "AI and Advanced Data Science"

    # 5. Delete
    del_res = departments.delete_department(dept_id, db)
    assert del_res.success is True

def test_students_operations(db):
    depts = departments.list_departments(db)
    dept_id = depts[0].id

    # 1. Create Student
    student_in = schemas.StudentCreate(
        roll_number="TEST-2025-001",
        first_name="Alexander",
        last_name="Pierce",
        email="alex.pierce@example.edu",
        phone="+1 555 777 8888",
        date_of_birth=date(2003, 3, 21),
        gender="Male",
        address="100 Tech Park, Suite 4",
        department_id=dept_id,
        year_of_study=1,
        semester=2,
        status="Active",
        enrollment_date=date(2024, 1, 15)
    )
    created = students.create_student(student_in, db)
    student_id = created.id
    assert created.roll_number == "TEST-2025-001"
    assert created.full_name == "Alexander Pierce"

    # 2. Search Student
    search_results = students.list_students(search="Pierce", db=db)
    assert any(s.id == student_id for s in search_results)

    # 3. Get Student Detail
    detail = students.get_student_detail(student_id, db)
    assert detail.roll_number == "TEST-2025-001"
    assert detail.full_name == "Alexander Pierce"

    # 4. Update Student
    updated = students.update_student(
        student_id,
        schemas.StudentUpdate(first_name="Alex", status="Active"),
        db
    )
    assert updated.first_name == "Alex"

    # 5. CSV Export
    csv_response = students.export_students_csv(db)
    assert csv_response.status_code == 200
    assert "TEST-2025-001" in csv_response.body.decode("utf-8")

    # 6. Delete Student
    del_res = students.delete_student(student_id, db)
    assert del_res.success is True

def test_courses_operations(db):
    depts = departments.list_departments(db)
    dept_id = depts[0].id

    # Create Course
    course_in = schemas.CourseCreate(
        code="CS401",
        name="Cloud Computing & Distributed Systems",
        credits=4,
        department_id=dept_id,
        instructor="Prof. Werner Vogels",
        description="Scalable system architecture, microservices, and virtualization."
    )
    created = courses.create_course(course_in, db)
    course_id = created.id
    assert created.code == "CS401"

    # Read Course
    fetched = courses.get_course(course_id, db)
    assert fetched.name == "Cloud Computing & Distributed Systems"

    # Update Course
    updated = courses.update_course(
        course_id,
        schemas.CourseUpdate(credits=5),
        db
    )
    assert updated.credits == 5

    # Delete Course
    del_res = courses.delete_course(course_id, db)
    assert del_res.success is True

def test_enrollments_and_grades(db):
    all_students = [s for s in students.list_students(db=db) if s.status == "Active"]
    all_courses = courses.list_courses(db=db)
    
    # Pick a student and matching department course
    student = all_students[0]
    matching_courses = [c for c in all_courses if c.department_id == student.department_id]
    course = matching_courses[0]

    # 1. Valid Enrollment
    enroll_in = schemas.EnrollmentCreate(
        student_id=student.id,
        course_id=course.id,
        semester_name="Spring 2026",
        grade="A",
        grade_point=Decimal("4.00"),
        status="Completed",
        enrolled_date=date(2026, 1, 10)
    )
    enrollment = enrollments.create_enrollment(enroll_in, db)
    enrollment_id = enrollment.id
    assert enrollment.grade == "A"

    # 2. Test Edge Case: Department Mismatch raises 400
    different_dept_courses = [c for c in all_courses if c.department_id != student.department_id]
    if different_dept_courses:
        bad_course = different_dept_courses[0]
        with pytest.raises(Exception) as excinfo:
            enrollments.create_enrollment(
                schemas.EnrollmentCreate(
                    student_id=student.id,
                    course_id=bad_course.id,
                    semester_name="Spring 2026",
                    enrolled_date=date(2026, 1, 10)
                ),
                db
            )
        assert "Department mismatch" in str(excinfo.value.detail)

    # 3. Update Grade
    updated = enrollments.update_enrollment(
        enrollment_id,
        schemas.EnrollmentUpdate(grade="A+", grade_point=Decimal("4.00")),
        db
    )
    assert updated.grade == "A+"

    # 4. Remove enrollment
    del_res = enrollments.delete_enrollment(enrollment_id, db)
    assert del_res.success is True

def test_attendance_operations(db):
    all_students = [s for s in students.list_students(db=db) if s.status == "Active"]
    all_courses = courses.list_courses(db=db)
    
    # Find an actively enrolled student and course pair
    enrolled_pair = None
    for s in all_students:
        for c in all_courses:
            if crud.is_student_enrolled_in_course(db, s.id, c.id):
                enrolled_pair = (s, c)
                break
        if enrolled_pair:
            break

    assert enrolled_pair is not None, "No active enrollment found in seed data"
    student, course = enrolled_pair

    # 1. Valid attendance record
    att_in = schemas.AttendanceCreate(
        student_id=student.id,
        course_id=course.id,
        date=date(2025, 2, 1),
        status="Present",
        remarks="Active engagement in lecture"
    )
    record = attendance.mark_attendance(att_in, db)
    att_id = record.id
    assert record.status == "Present"

    # 2. List attendance & verify date filter
    logs = attendance.list_attendance(student_id=student.id, db=db)
    assert any(a.id == att_id for a in logs)

    # Date filter verification: must ONLY return records for that date
    date_logs = attendance.list_attendance(date=date(2025, 2, 1), db=db)
    assert len(date_logs) > 0
    assert all(a.date == date(2025, 2, 1) for a in date_logs)
    assert any(a.id == att_id for a in date_logs)

    # Date filter with date_val alias
    date_val_logs = attendance.list_attendance(date_val=date(2025, 2, 1), db=db)
    assert len(date_val_logs) == len(date_logs)

    # Non-matching date filter returns empty
    empty_logs = attendance.list_attendance(date=date(2020, 1, 1), db=db)
    assert len(empty_logs) == 0

    # Status filter
    present_logs = attendance.list_attendance(date=date(2025, 2, 1), status="Present", db=db)
    assert all(a.status == "Present" for a in present_logs)

    # 3. Test Edge Case: Marking attendance for a student NOT enrolled in the course must fail
    unenrolled_student = next(s for s in all_students if not crud.is_student_enrolled_in_course(db, s.id, course.id))
    with pytest.raises(Exception) as excinfo:
        attendance.mark_attendance(
            schemas.AttendanceCreate(
                student_id=unenrolled_student.id,
                course_id=course.id,
                date=date(2025, 2, 1),
                status="Present"
            ),
            db
        )
    assert "NOT enrolled in course" in str(excinfo.value.detail)

    # 4. Test Edge Case: Marking attendance for a future date must fail
    with pytest.raises(Exception) as excinfo:
        attendance.mark_attendance(
            schemas.AttendanceCreate(
                student_id=student.id,
                course_id=course.id,
                date=date(2099, 1, 1),
                status="Present"
            ),
            db
        )
    assert "future date" in str(excinfo.value.detail)

    # 5. Test Course enrolled students endpoint
    enrolled_students = courses.get_course_enrolled_students(course.id, db)
    assert any(s.id == student.id for s in enrolled_students)

    # Clean up attendance record
    del_res = attendance.delete_attendance(att_id, db)
    assert del_res.success is True
