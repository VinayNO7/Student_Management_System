from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from app.database import get_db
from app import schemas, crud

router = APIRouter(prefix="/api/attendance", tags=["Attendance"])

@router.get("", response_model=List[schemas.AttendanceOut])
def list_attendance(
    student_id: Optional[int] = None,
    course_id: Optional[int] = None,
    date_val: Optional[date] = None,
    db: Session = Depends(get_db)
):
    """Retrieve attendance logs."""
    return crud.get_attendance_records(db, student_id=student_id, course_id=course_id, date_val=date_val)

@router.post("", response_model=schemas.AttendanceOut, status_code=status.HTTP_200_OK)
def mark_attendance(attendance_in: schemas.AttendanceCreate, db: Session = Depends(get_db)):
    """Mark or update student attendance for a course on a date."""
    student = crud.get_student_by_id(db, attendance_in.student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student does not exist.")
    course = crud.get_course_by_id(db, attendance_in.course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course does not exist.")

    # 1. Validate student is active
    if student.status != "Active":
        raise HTTPException(
            status_code=400,
            detail=f"Cannot mark attendance: Student '{student.full_name}' has status '{student.status}'. Attendance can only be recorded for Active students."
        )

    # 2. Validate student is enrolled in this specific course
    if not crud.is_student_enrolled_in_course(db, attendance_in.student_id, attendance_in.course_id):
        dept_name = student.department.name if student.department else "Unknown Dept"
        raise HTTPException(
            status_code=400,
            detail=f"Cannot mark attendance: Student '{student.full_name}' ({dept_name}) is NOT enrolled in course '{course.code} - {course.name}'."
        )

    # 3. Validate date is not in future
    if attendance_in.date > date.today():
        raise HTTPException(
            status_code=400,
            detail="Cannot mark attendance for a future date."
        )

    rec = crud.mark_attendance(db, attendance_in)
    return schemas.AttendanceOut(
        id=rec.id,
        student_id=rec.student_id,
        student_name=rec.student.full_name if rec.student else None,
        student_roll=rec.student.roll_number if rec.student else None,
        course_id=rec.course_id,
        course_code=rec.course.code if rec.course else None,
        course_name=rec.course.name if rec.course else None,
        date=rec.date,
        status=rec.status,
        remarks=rec.remarks,
        created_at=rec.created_at
    )

@router.post("/batch", response_model=schemas.AttendanceBatchResponse, status_code=status.HTTP_200_OK)
def batch_mark_attendance(batch_in: schemas.AttendanceBatchCreate, db: Session = Depends(get_db)):
    """Mark attendance for a full roster/class in one call."""
    course = crud.get_course_by_id(db, batch_in.course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course does not exist.")
    
    if batch_in.date > date.today():
        raise HTTPException(
            status_code=400,
            detail="Cannot mark attendance for a future date."
        )

    for item in batch_in.records:
        if not crud.is_student_enrolled_in_course(db, item.student_id, batch_in.course_id):
            s = crud.get_student_by_id(db, item.student_id)
            name = s.full_name if s else f"ID {item.student_id}"
            raise HTTPException(
                status_code=400,
                detail=f"Cannot mark batch attendance: Student '{name}' is not enrolled in course '{course.code}'."
            )

    count = crud.batch_mark_attendance(db, batch_in)
    return schemas.AttendanceBatchResponse(
        course_id=batch_in.course_id,
        date=batch_in.date,
        total_marked=count,
        message=f"Successfully logged attendance for {count} students."
    )

@router.delete("/{attendance_id}", response_model=schemas.MessageResponse)
def delete_attendance(attendance_id: int, db: Session = Depends(get_db)):
    """Delete an attendance record."""
    success = crud.delete_attendance(db, attendance_id)
    if not success:
        raise HTTPException(status_code=404, detail="Attendance record not found")
    return schemas.MessageResponse(message=f"Attendance record {attendance_id} deleted successfully.")
