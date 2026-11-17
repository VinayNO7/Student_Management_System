from sqlalchemy.orm import Session
from sqlalchemy import or_, func, desc
from app import models, schemas
from typing import Optional, List, Dict, Any
from decimal import Decimal

# Grade Point Mapping standard
GRADE_POINTS = {
    "A+": 4.0, "A": 4.0, "A-": 3.7,
    "B+": 3.3, "B": 3.0, "B-": 2.7,
    "C+": 2.3, "C": 2.0, "C-": 1.7,
    "D+": 1.3, "D": 1.0, "F": 0.0
}

# --- Student CRUD ---

def calculate_student_gpa(db: Session, student_id: int) -> Optional[float]:
    """Calculates weighted GPA based on completed course credits and grade points."""
    enrollments = (
        db.query(models.Enrollment, models.Course)
        .join(models.Course, models.Enrollment.course_id == models.Course.id)
        .filter(models.Enrollment.student_id == student_id, models.Enrollment.grade_point.isnot(None))
        .all()
    )
    if not enrollments:
        return None
    total_points = sum(float(e.grade_point) * c.credits for e, c in enrollments)
    total_credits = sum(c.credits for e, c in enrollments)
    if total_credits == 0:
        return None
    return round(total_points / total_credits, 2)

def calculate_student_attendance_rate(db: Session, student_id: int) -> Optional[float]:
    """Calculates percentage of attendance marked as Present or Late."""
    total = db.query(models.Attendance).filter(models.Attendance.student_id == student_id).count()
    if total == 0:
        return None
    present = db.query(models.Attendance).filter(
        models.Attendance.student_id == student_id,
        models.Attendance.status.in_(["Present", "Late"])
    ).count()
    return round((present / total) * 100.0, 1)

def get_students(
    db: Session,
    search: Optional[str] = None,
    department_id: Optional[int] = None,
    status: Optional[str] = None,
    semester: Optional[int] = None,
    skip: int = 0,
    limit: int = 100
) -> List[schemas.StudentOut]:
    query = db.query(models.Student)

    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(
                models.Student.first_name.ilike(search_pattern),
                models.Student.last_name.ilike(search_pattern),
                models.Student.roll_number.ilike(search_pattern),
                models.Student.email.ilike(search_pattern)
            )
        )
    if department_id:
        query = query.filter(models.Student.department_id == department_id)
    if status:
        query = query.filter(models.Student.status == status)
    if semester:
        query = query.filter(models.Student.semester == semester)

    students = query.order_by(models.Student.id.desc()).offset(skip).limit(limit).all()

    result = []
    for s in students:
        s_out = schemas.StudentOut(
            id=s.id,
            roll_number=s.roll_number,
            first_name=s.first_name,
            last_name=s.last_name,
            full_name=s.full_name,
            email=s.email,
            phone=s.phone,
            date_of_birth=s.date_of_birth,
            gender=s.gender,
            address=s.address,
            department_id=s.department_id,
            department_name=s.department.name if s.department else None,
            department_code=s.department.code if s.department else None,
            year_of_study=s.year_of_study,
            semester=s.semester,
            status=s.status,
            enrollment_date=s.enrollment_date,
            gpa=calculate_student_gpa(db, s.id),
            created_at=s.created_at,
            updated_at=s.updated_at
        )
        result.append(s_out)
    return result

def get_student_by_id(db: Session, student_id: int) -> Optional[models.Student]:
    return db.query(models.Student).filter(models.Student.id == student_id).first()

def get_student_by_roll(db: Session, roll_number: str) -> Optional[models.Student]:
    return db.query(models.Student).filter(models.Student.roll_number == roll_number).first()

def get_student_by_email(db: Session, email: str) -> Optional[models.Student]:
    return db.query(models.Student).filter(models.Student.email == email).first()

def create_student(db: Session, student_in: schemas.StudentCreate) -> models.Student:
    db_student = models.Student(**student_in.model_dump())
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student

def update_student(db: Session, student_id: int, student_in: schemas.StudentUpdate) -> Optional[models.Student]:
    db_student = get_student_by_id(db, student_id)
    if not db_student:
        return None
    update_data = student_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_student, field, value)
    db.commit()
    db.refresh(db_student)
    return db_student

def delete_student(db: Session, student_id: int) -> bool:
    db_student = get_student_by_id(db, student_id)
    if not db_student:
        return False
    db.delete(db_student)
    db.commit()
    return True

def get_student_detail(db: Session, student_id: int) -> Optional[schemas.StudentDetailOut]:
    student = get_student_by_id(db, student_id)
    if not student:
        return None

    # Enrich enrollments
    enrollments_out = []
    for e in student.enrollments:
        enrollments_out.append(
            schemas.EnrollmentOut(
                id=e.id,
                student_id=e.student_id,
                student_name=student.full_name,
                student_roll=student.roll_number,
                course_id=e.course_id,
                course_code=e.course.code if e.course else None,
                course_name=e.course.name if e.course else None,
                course_credits=e.course.credits if e.course else None,
                semester_name=e.semester_name,
                grade=e.grade,
                grade_point=e.grade_point,
                status=e.status,
                enrolled_date=e.enrolled_date,
                created_at=e.created_at
            )
        )

    # Enrich attendance
    attendance_out = []
    for a in student.attendance_records:
        attendance_out.append(
            schemas.AttendanceOut(
                id=a.id,
                student_id=a.student_id,
                student_name=student.full_name,
                student_roll=student.roll_number,
                course_id=a.course_id,
                course_code=a.course.code if a.course else None,
                course_name=a.course.name if a.course else None,
                date=a.date,
                status=a.status,
                remarks=a.remarks,
                created_at=a.created_at
            )
        )

    return schemas.StudentDetailOut(
        id=student.id,
        roll_number=student.roll_number,
        first_name=student.first_name,
        last_name=student.last_name,
        full_name=student.full_name,
        email=student.email,
        phone=student.phone,
        date_of_birth=student.date_of_birth,
        gender=student.gender,
        address=student.address,
        department_id=student.department_id,
        department_name=student.department.name if student.department else None,
        department_code=student.department.code if student.department else None,
        year_of_study=student.year_of_study,
        semester=student.semester,
        status=student.status,
        enrollment_date=student.enrollment_date,
        gpa=calculate_student_gpa(db, student.id),
        created_at=student.created_at,
        updated_at=student.updated_at,
        enrollments=enrollments_out,
        attendance_records=attendance_out,
        attendance_percentage=calculate_student_attendance_rate(db, student.id)
    )

# --- Department CRUD ---

def get_departments(db: Session) -> List[schemas.DepartmentOut]:
    departments = db.query(models.Department).order_by(models.Department.id.asc()).all()
    result = []
    for d in departments:
        result.append(
            schemas.DepartmentOut(
                id=d.id,
                code=d.code,
                name=d.name,
                head_of_department=d.head_of_department,
                description=d.description,
                created_at=d.created_at,
                student_count=len(d.students),
                course_count=len(d.courses)
            )
        )
    return result

def get_department_by_id(db: Session, dept_id: int) -> Optional[models.Department]:
    return db.query(models.Department).filter(models.Department.id == dept_id).first()

def get_department_by_code(db: Session, code: str) -> Optional[models.Department]:
    return db.query(models.Department).filter(models.Department.code == code).first()

def create_department(db: Session, dept_in: schemas.DepartmentCreate) -> models.Department:
    dept = models.Department(**dept_in.model_dump())
    db.add(dept)
    db.commit()
    db.refresh(dept)
    return dept

def update_department(db: Session, dept_id: int, dept_in: schemas.DepartmentUpdate) -> Optional[models.Department]:
    dept = get_department_by_id(db, dept_id)
    if not dept:
        return None
    for field, val in dept_in.model_dump(exclude_unset=True).items():
        setattr(dept, field, val)
    db.commit()
    db.refresh(dept)
    return dept

def delete_department(db: Session, dept_id: int) -> bool:
    dept = get_department_by_id(db, dept_id)
    if not dept:
        return False
    # Check if students are linked
    if dept.students:
        raise ValueError("Cannot delete department because students are currently enrolled in it.")
    db.delete(dept)
    db.commit()
    return True

# --- Course CRUD ---

def get_courses(db: Session, department_id: Optional[int] = None) -> List[schemas.CourseOut]:
    query = db.query(models.Course)
    if department_id:
        query = query.filter(models.Course.department_id == department_id)
    courses = query.order_by(models.Course.id.asc()).all()
    result = []
    for c in courses:
        result.append(
            schemas.CourseOut(
                id=c.id,
                code=c.code,
                name=c.name,
                credits=c.credits,
                department_id=c.department_id,
                department_name=c.department.name if c.department else None,
                instructor=c.instructor,
                description=c.description,
                created_at=c.created_at
            )
        )
    return result

def get_course_by_id(db: Session, course_id: int) -> Optional[models.Course]:
    return db.query(models.Course).filter(models.Course.id == course_id).first()

def get_course_by_code(db: Session, code: str) -> Optional[models.Course]:
    return db.query(models.Course).filter(models.Course.code == code).first()

def create_course(db: Session, course_in: schemas.CourseCreate) -> models.Course:
    course = models.Course(**course_in.model_dump())
    db.add(course)
    db.commit()
    db.refresh(course)
    return course

def update_course(db: Session, course_id: int, course_in: schemas.CourseUpdate) -> Optional[models.Course]:
    course = get_course_by_id(db, course_id)
    if not course:
        return None
    for field, val in course_in.model_dump(exclude_unset=True).items():
        setattr(course, field, val)
    db.commit()
    db.refresh(course)
    return course

def delete_course(db: Session, course_id: int) -> bool:
    course = get_course_by_id(db, course_id)
    if not course:
        return False
    db.delete(course)
    db.commit()
    return True

# --- Enrollment CRUD ---

def get_enrollments(
    db: Session,
    student_id: Optional[int] = None,
    course_id: Optional[int] = None,
    semester_name: Optional[str] = None
) -> List[schemas.EnrollmentOut]:
    query = db.query(models.Enrollment)
    if student_id:
        query = query.filter(models.Enrollment.student_id == student_id)
    if course_id:
        query = query.filter(models.Enrollment.course_id == course_id)
    if semester_name:
        query = query.filter(models.Enrollment.semester_name == semester_name)

    enrollments = query.order_by(models.Enrollment.id.desc()).all()
    result = []
    for e in enrollments:
        result.append(
            schemas.EnrollmentOut(
                id=e.id,
                student_id=e.student_id,
                student_name=e.student.full_name if e.student else None,
                student_roll=e.student.roll_number if e.student else None,
                course_id=e.course_id,
                course_code=e.course.code if e.course else None,
                course_name=e.course.name if e.course else None,
                course_credits=e.course.credits if e.course else None,
                semester_name=e.semester_name,
                grade=e.grade,
                grade_point=e.grade_point,
                status=e.status,
                enrolled_date=e.enrolled_date,
                created_at=e.created_at
            )
        )
    return result

def get_enrollment_by_id(db: Session, enrollment_id: int) -> Optional[models.Enrollment]:
    return db.query(models.Enrollment).filter(models.Enrollment.id == enrollment_id).first()

def create_enrollment(db: Session, enrollment_in: schemas.EnrollmentCreate) -> models.Enrollment:
    # Auto-calculate grade_point if grade provided
    grade_point = enrollment_in.grade_point
    if enrollment_in.grade and not grade_point:
        grade_point = Decimal(str(GRADE_POINTS.get(enrollment_in.grade.upper(), 0.0)))
    
    data = enrollment_in.model_dump()
    data["grade_point"] = grade_point
    enrollment = models.Enrollment(**data)
    db.add(enrollment)
    db.commit()
    db.refresh(enrollment)
    return enrollment

def update_enrollment(db: Session, enrollment_id: int, enrollment_in: schemas.EnrollmentUpdate) -> Optional[models.Enrollment]:
    enrollment = get_enrollment_by_id(db, enrollment_id)
    if not enrollment:
        return None
    update_data = enrollment_in.model_dump(exclude_unset=True)
    if "grade" in update_data and update_data["grade"] and "grade_point" not in update_data:
        update_data["grade_point"] = Decimal(str(GRADE_POINTS.get(update_data["grade"].upper(), 0.0)))
    for field, val in update_data.items():
        setattr(enrollment, field, val)
    db.commit()
    db.refresh(enrollment)
    return enrollment

def delete_enrollment(db: Session, enrollment_id: int) -> bool:
    enrollment = get_enrollment_by_id(db, enrollment_id)
    if not enrollment:
        return False
    db.delete(enrollment)
    db.commit()
    return True

def is_student_enrolled_in_course(db: Session, student_id: int, course_id: int) -> bool:
    """Checks if a student has an active enrollment (Enrolled or Completed) in a course."""
    enrollment = db.query(models.Enrollment).filter(
        models.Enrollment.student_id == student_id,
        models.Enrollment.course_id == course_id,
        models.Enrollment.status.in_(["Enrolled", "Completed"])
    ).first()
    return enrollment is not None

def get_enrolled_students_for_course(db: Session, course_id: int) -> List[schemas.StudentOut]:
    """Returns all students actively enrolled in a given course."""
    enrollments = db.query(models.Enrollment).filter(
        models.Enrollment.course_id == course_id,
        models.Enrollment.status.in_(["Enrolled", "Completed"])
    ).all()

    results = []
    seen_ids = set()
    for e in enrollments:
        if e.student and e.student.id not in seen_ids:
            seen_ids.add(e.student.id)
            s = e.student
            results.append(
                schemas.StudentOut(
                    id=s.id,
                    roll_number=s.roll_number,
                    first_name=s.first_name,
                    last_name=s.last_name,
                    full_name=s.full_name,
                    email=s.email,
                    phone=s.phone,
                    date_of_birth=s.date_of_birth,
                    gender=s.gender,
                    address=s.address,
                    department_id=s.department_id,
                    department_name=s.department.name if s.department else None,
                    department_code=s.department.code if s.department else None,
                    year_of_study=s.year_of_study,
                    semester=s.semester,
                    status=s.status,
                    enrollment_date=s.enrollment_date,
                    gpa=calculate_student_gpa(db, s.id),
                    created_at=s.created_at,
                    updated_at=s.updated_at
                )
            )
    return results

# --- Attendance CRUD ---

def get_attendance_records(
    db: Session,
    student_id: Optional[int] = None,
    course_id: Optional[int] = None,
    date_val: Optional[Any] = None
) -> List[schemas.AttendanceOut]:
    query = db.query(models.Attendance)
    if student_id:
        query = query.filter(models.Attendance.student_id == student_id)
    if course_id:
        query = query.filter(models.Attendance.course_id == course_id)
    if date_val:
        query = query.filter(models.Attendance.date == date_val)

    records = query.order_by(models.Attendance.date.desc(), models.Attendance.id.desc()).all()
    result = []
    for a in records:
        result.append(
            schemas.AttendanceOut(
                id=a.id,
                student_id=a.student_id,
                student_name=a.student.full_name if a.student else None,
                student_roll=a.student.roll_number if a.student else None,
                course_id=a.course_id,
                course_code=a.course.code if a.course else None,
                course_name=a.course.name if a.course else None,
                date=a.date,
                status=a.status,
                remarks=a.remarks,
                created_at=a.created_at
            )
        )
    return result

def mark_attendance(db: Session, attendance_in: schemas.AttendanceCreate) -> models.Attendance:
    # Check if record already exists for (student_id, course_id, date)
    existing = db.query(models.Attendance).filter(
        models.Attendance.student_id == attendance_in.student_id,
        models.Attendance.course_id == attendance_in.course_id,
        models.Attendance.date == attendance_in.date
    ).first()

    if existing:
        existing.status = attendance_in.status
        existing.remarks = attendance_in.remarks
        db.commit()
        db.refresh(existing)
        return existing
    else:
        record = models.Attendance(**attendance_in.model_dump())
        db.add(record)
        db.commit()
        db.refresh(record)
        return record

def batch_mark_attendance(db: Session, batch_in: schemas.AttendanceBatchCreate) -> int:
    """Batch marks or updates attendance for multiple students for a given course & date."""
    marked = 0
    for item in batch_in.records:
        existing = db.query(models.Attendance).filter(
            models.Attendance.student_id == item.student_id,
            models.Attendance.course_id == batch_in.course_id,
            models.Attendance.date == batch_in.date
        ).first()
        if existing:
            existing.status = item.status
            if item.remarks is not None:
                existing.remarks = item.remarks
        else:
            rec = models.Attendance(
                student_id=item.student_id,
                course_id=batch_in.course_id,
                date=batch_in.date,
                status=item.status,
                remarks=item.remarks
            )
            db.add(rec)
        marked += 1
    db.commit()
    return marked

def delete_attendance(db: Session, attendance_id: int) -> bool:
    record = db.query(models.Attendance).filter(models.Attendance.id == attendance_id).first()
    if not record:
        return False
    db.delete(record)
    db.commit()
    return True

# --- Analytics / Dashboard ---

def get_system_stats(db: Session) -> schemas.StatsOut:
    total_students = db.query(models.Student).count()
    active_students = db.query(models.Student).filter(models.Student.status == "Active").count()
    graduated_students = db.query(models.Student).filter(models.Student.status == "Graduated").count()
    total_departments = db.query(models.Department).count()
    total_courses = db.query(models.Course).count()
    total_enrollments = db.query(models.Enrollment).count()

    # Calculate average GPA across all completed courses
    completed_grades = db.query(func.avg(models.Enrollment.grade_point)).filter(
        models.Enrollment.grade_point.isnot(None)
    ).scalar()
    avg_gpa = round(float(completed_grades), 2) if completed_grades else 0.0

    # Department distribution
    depts = db.query(models.Department).all()
    distribution = []
    for d in depts:
        distribution.append(
            schemas.DeptStat(
                department_id=d.id,
                code=d.code,
                name=d.name,
                student_count=len(d.students)
            )
        )

    return schemas.StatsOut(
        total_students=total_students,
        active_students=active_students,
        graduated_students=graduated_students,
        total_departments=total_departments,
        total_courses=total_courses,
        total_enrollments=total_enrollments,
        average_gpa=avg_gpa,
        department_distribution=distribution
    )

