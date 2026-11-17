from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app import schemas, crud

router = APIRouter(prefix="/api/courses", tags=["Courses"])

@router.get("", response_model=List[schemas.CourseOut])
def list_courses(
    department_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Retrieve courses with optional department filter."""
    return crud.get_courses(db, department_id=department_id)

@router.get("/{course_id}", response_model=schemas.CourseOut)
def get_course(course_id: int, db: Session = Depends(get_db)):
    """Retrieve details for a single course."""
    course = crud.get_course_by_id(db, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return schemas.CourseOut(
        id=course.id,
        code=course.code,
        name=course.name,
        credits=course.credits,
        department_id=course.department_id,
        department_name=course.department.name if course.department else None,
        instructor=course.instructor,
        description=course.description,
        created_at=course.created_at
    )

@router.get("/{course_id}/enrolled-students", response_model=List[schemas.StudentOut])
def get_course_enrolled_students(course_id: int, db: Session = Depends(get_db)):
    """Retrieve all students currently enrolled in this course."""
    course = crud.get_course_by_id(db, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return crud.get_enrolled_students_for_course(db, course_id)

@router.post("", response_model=schemas.CourseOut, status_code=status.HTTP_201_CREATED)
def create_course(course_in: schemas.CourseCreate, db: Session = Depends(get_db)):
    """Create a new course offering."""
    if crud.get_course_by_code(db, course_in.code):
        raise HTTPException(status_code=400, detail=f"Course with code '{course_in.code}' already exists.")
    if not crud.get_department_by_id(db, course_in.department_id):
        raise HTTPException(status_code=404, detail="Department does not exist.")
    
    course = crud.create_course(db, course_in)
    return schemas.CourseOut(
        id=course.id,
        code=course.code,
        name=course.name,
        credits=course.credits,
        department_id=course.department_id,
        department_name=course.department.name if course.department else None,
        instructor=course.instructor,
        description=course.description,
        created_at=course.created_at
    )

@router.put("/{course_id}", response_model=schemas.CourseOut)
def update_course(course_id: int, course_in: schemas.CourseUpdate, db: Session = Depends(get_db)):
    """Update course attributes."""
    course = crud.get_course_by_id(db, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    if course_in.code and course_in.code != course.code:
        if crud.get_course_by_code(db, course_in.code):
            raise HTTPException(status_code=400, detail="Course code already in use.")
    if course_in.department_id:
        if not crud.get_department_by_id(db, course_in.department_id):
            raise HTTPException(status_code=404, detail="Specified Department does not exist.")

    updated = crud.update_course(db, course_id, course_in)
    return schemas.CourseOut(
        id=updated.id,
        code=updated.code,
        name=updated.name,
        credits=updated.credits,
        department_id=updated.department_id,
        department_name=updated.department.name if updated.department else None,
        instructor=updated.instructor,
        description=updated.description,
        created_at=updated.created_at
    )

@router.delete("/{course_id}", response_model=schemas.MessageResponse)
def delete_course(course_id: int, db: Session = Depends(get_db)):
    """Delete a course."""
    success = crud.delete_course(db, course_id)
    if not success:
        raise HTTPException(status_code=404, detail="Course not found")
    return schemas.MessageResponse(message=f"Course ID {course_id} deleted successfully.")
