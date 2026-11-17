from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app import schemas, crud

router = APIRouter(prefix="/api/departments", tags=["Departments"])

@router.get("", response_model=List[schemas.DepartmentOut])
def list_departments(db: Session = Depends(get_db)):
    """List all departments with student and course counts."""
    return crud.get_departments(db)

@router.get("/{dept_id}", response_model=schemas.DepartmentOut)
def get_department(dept_id: int, db: Session = Depends(get_db)):
    """Retrieve details for a single department."""
    dept = crud.get_department_by_id(db, dept_id)
    if not dept:
        raise HTTPException(status_code=404, detail="Department not found")
    return schemas.DepartmentOut(
        id=dept.id,
        code=dept.code,
        name=dept.name,
        head_of_department=dept.head_of_department,
        description=dept.description,
        created_at=dept.created_at,
        student_count=len(dept.students),
        course_count=len(dept.courses)
    )

@router.post("", response_model=schemas.DepartmentOut, status_code=status.HTTP_201_CREATED)
def create_department(dept_in: schemas.DepartmentCreate, db: Session = Depends(get_db)):
    """Create a new department."""
    if crud.get_department_by_code(db, dept_in.code):
        raise HTTPException(status_code=400, detail=f"Department with code '{dept_in.code}' already exists.")
    dept = crud.create_department(db, dept_in)
    return schemas.DepartmentOut(
        id=dept.id,
        code=dept.code,
        name=dept.name,
        head_of_department=dept.head_of_department,
        description=dept.description,
        created_at=dept.created_at,
        student_count=0,
        course_count=0
    )

@router.put("/{dept_id}", response_model=schemas.DepartmentOut)
def update_department(dept_id: int, dept_in: schemas.DepartmentUpdate, db: Session = Depends(get_db)):
    """Update department info."""
    dept = crud.get_department_by_id(db, dept_id)
    if not dept:
        raise HTTPException(status_code=404, detail="Department not found")
    if dept_in.code and dept_in.code != dept.code:
        if crud.get_department_by_code(db, dept_in.code):
            raise HTTPException(status_code=400, detail="Department code already in use.")
    updated = crud.update_department(db, dept_id, dept_in)
    return schemas.DepartmentOut(
        id=updated.id,
        code=updated.code,
        name=updated.name,
        head_of_department=updated.head_of_department,
        description=updated.description,
        created_at=updated.created_at,
        student_count=len(updated.students),
        course_count=len(updated.courses)
    )

@router.delete("/{dept_id}", response_model=schemas.MessageResponse)
def delete_department(dept_id: int, db: Session = Depends(get_db)):
    """Delete a department (fails if students are attached)."""
    try:
        success = crud.delete_department(db, dept_id)
        if not success:
            raise HTTPException(status_code=404, detail="Department not found")
        return schemas.MessageResponse(message=f"Department ID {dept_id} deleted successfully.")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

