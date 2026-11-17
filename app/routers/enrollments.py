from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app import schemas, crud

router = APIRouter(prefix="/api/enrollments", tags=["Enrollments & Grades"])

@router.get("", response_model=List[schemas.EnrollmentOut])
def list_enrollments(
    student_id: Optional[int] = None,
    course_id: Optional[int] = None,
    semester_name: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List student enrollments and academic grades."""
    return crud.get_enrollments(
        db, student_id=student_id, course_id=course_id, semester_name=semester_name
    )

@router.get("/{enrollment_id}", response_model=schemas.EnrollmentOut)
def get_enrollment(enrollment_id: int, db: Session = Depends(get_db)):
    """Retrieve details for a single enrollment."""
    e = crud.get_enrollment_by_id(db, enrollment_id)
    if not e:
        raise HTTPException(status_code=404, detail="Enrollment record not found")
    return schemas.EnrollmentOut(
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

@router.post("", response_model=schemas.EnrollmentOut, status_code=status.HTTP_201_CREATED)
def create_enrollment(enrollment_in: schemas.EnrollmentCreate, db: Session = Depends(get_db)):
    """Enroll a student in a course."""
    student = crud.get_student_by_id(db, enrollment_in.student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student does not exist.")
    course = crud.get_course_by_id(db, enrollment_in.course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course does not exist.")

    # 1. Validate student is active
    if student.status != "Active":
        raise HTTPException(
            status_code=400,
            detail=f"Cannot enroll student with status '{student.status}'. Only Active students can be enrolled in courses."
        )

    # 2. Validate department alignment
    if student.department_id != course.department_id:
        student_dept = student.department.code if student.department else f"Dept #{student.department_id}"
        course_dept = course.department.code if course.department else f"Dept #{course.department_id}"
        raise HTTPException(
            status_code=400,
            detail=f"Department mismatch: Student '{student.full_name}' belongs to '{student_dept}', but course '{course.code}' belongs to '{course_dept}'."
        )

    # 3. Check for existing duplicate enrollment
    existing = crud.get_enrollments(
        db, student_id=enrollment_in.student_id, course_id=enrollment_in.course_id, semester_name=enrollment_in.semester_name
    )
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Student is already enrolled in this course for this semester."
        )

    e = crud.create_enrollment(db, enrollment_in)
    return schemas.EnrollmentOut(
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

@router.put("/{enrollment_id}", response_model=schemas.EnrollmentOut)
def update_enrollment(enrollment_id: int, enrollment_in: schemas.EnrollmentUpdate, db: Session = Depends(get_db)):
    """Assign/update grade or enrollment status."""
    e = crud.update_enrollment(db, enrollment_id, enrollment_in)
    if not e:
        raise HTTPException(status_code=404, detail="Enrollment record not found")
    return schemas.EnrollmentOut(
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

@router.delete("/{enrollment_id}", response_model=schemas.MessageResponse)
def delete_enrollment(enrollment_id: int, db: Session = Depends(get_db)):
    """Drop/remove an enrollment."""
    success = crud.delete_enrollment(db, enrollment_id)
    if not success:
        raise HTTPException(status_code=404, detail="Enrollment record not found")
    return schemas.MessageResponse(message=f"Enrollment ID {enrollment_id} successfully removed.")
