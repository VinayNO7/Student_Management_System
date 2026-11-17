from fastapi import APIRouter, Depends, HTTPException, Query, status, Response, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
import io
import csv
from datetime import datetime, date

from app.database import get_db
from app import schemas, crud

router = APIRouter(prefix="/api/students", tags=["Students"])

@router.get("", response_model=List[schemas.StudentOut])
def list_students(
    search: Optional[str] = None,
    department_id: Optional[int] = None,
    status: Optional[str] = None,
    semester: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Retrieve students with optional search query, filtering, and pagination."""
    return crud.get_students(
        db, search=search, department_id=department_id, status=status,
        semester=semester, skip=skip, limit=limit
    )

@router.get("/template/csv")
def download_student_csv_template():
    """Download a blank sample CSV template for bulk student import."""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "roll_number", "first_name", "last_name", "email", "phone",
        "date_of_birth", "gender", "department_code", "year_of_study",
        "semester", "status", "enrollment_date", "address"
    ])
    writer.writerow([
        "STU-2025-001", "John", "Doe", "john.doe@example.edu", "+1 555 123 4567",
        "2004-03-15", "Male", "CSE", "1", "1", "Active", "2024-08-01", "123 Campus Way"
    ])
    output.seek(0)
    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=student_import_template.csv"}
    )

@router.post("/import/csv", response_model=schemas.CSVImportResponse)
async def import_students_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Upload a CSV file to register students in bulk."""
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only .csv files are supported.")

    content = await file.read()
    text = content.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text))

    imported = 0
    errors = []

    # Map department codes for fast lookup
    dept_map = {d.code.upper(): d.id for d in crud.get_departments(db)}

    for idx, row in enumerate(reader, start=2):
        roll = row.get("roll_number", "").strip()
        first_name = row.get("first_name", "").strip()
        last_name = row.get("last_name", "").strip()
        email = row.get("email", "").strip()

        if not roll or not first_name or not last_name or not email:
            errors.append(f"Row {idx}: Missing required fields (roll_number, first_name, last_name, email).")
            continue

        if crud.get_student_by_roll(db, roll):
            errors.append(f"Row {idx}: Roll number '{roll}' already exists.")
            continue

        if crud.get_student_by_email(db, email):
            errors.append(f"Row {idx}: Email '{email}' already exists.")
            continue

        dept_code = row.get("department_code", "").strip().upper()
        dept_id = dept_map.get(dept_code)
        if not dept_id:
            try:
                dept_id = int(row.get("department_id", 0))
            except ValueError:
                dept_id = None
        if not dept_id or not crud.get_department_by_id(db, dept_id):
            errors.append(f"Row {idx}: Invalid department code '{dept_code}'.")
            continue

        # Parse date fields
        dob = None
        dob_str = row.get("date_of_birth", "").strip()
        if dob_str:
            try:
                dob = datetime.strptime(dob_str, "%Y-%m-%d").date()
            except ValueError:
                pass

        enr_date = date.today()
        enr_str = row.get("enrollment_date", "").strip()
        if enr_str:
            try:
                enr_date = datetime.strptime(enr_str, "%Y-%m-%d").date()
            except ValueError:
                pass

        try:
            student_in = schemas.StudentCreate(
                roll_number=roll,
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=row.get("phone", "").strip() or None,
                date_of_birth=dob,
                gender=row.get("gender", "Other").strip() or "Other",
                address=row.get("address", "").strip() or None,
                department_id=dept_id,
                year_of_study=int(row.get("year_of_study", 1)),
                semester=int(row.get("semester", 1)),
                status=row.get("status", "Active").strip() or "Active",
                enrollment_date=enr_date
            )
            crud.create_student(db, student_in)
            imported += 1
        except Exception as e:
            errors.append(f"Row {idx}: Failed to create student ({str(e)}).")

    return schemas.CSVImportResponse(
        total_imported=imported,
        errors=errors,
        message=f"Successfully imported {imported} student(s) with {len(errors)} error(s)."
    )

@router.get("/export/csv")
def export_students_csv(db: Session = Depends(get_db)):
    """Export all students as a downloadable CSV file."""
    students = crud.get_students(db, limit=5000)
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "ID", "Roll Number", "First Name", "Last Name", "Email", "Phone",
        "Gender", "Date of Birth", "Department", "Semester", "Year", "Status", "Enrollment Date", "GPA"
    ])
    for s in students:
        writer.writerow([
            s.id, s.roll_number, s.first_name, s.last_name, s.email, s.phone or "",
            s.gender, s.date_of_birth or "", s.department_name or "", s.semester,
            s.year_of_study, s.status, s.enrollment_date, s.gpa or "N/A"
        ])
    output.seek(0)
    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=students_export.csv"}
    )

@router.get("/{student_id}", response_model=schemas.StudentOut)
def get_student(student_id: int, db: Session = Depends(get_db)):
    """Retrieve basic details of a single student."""
    student = crud.get_student_by_id(db, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    return schemas.StudentOut(
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
        gpa=crud.calculate_student_gpa(db, student.id),
        created_at=student.created_at,
        updated_at=student.updated_at
    )

@router.get("/{student_id}/detail", response_model=schemas.StudentDetailOut)
def get_student_detail(student_id: int, db: Session = Depends(get_db)):
    """Retrieve comprehensive profile of a student including courses, grades, and attendance."""
    detail = crud.get_student_detail(db, student_id)
    if not detail:
        raise HTTPException(status_code=404, detail="Student not found")
    return detail

@router.post("", response_model=schemas.StudentOut, status_code=status.HTTP_201_CREATED)
def create_student(student_in: schemas.StudentCreate, db: Session = Depends(get_db)):
    """Register a new student."""
    # Check roll number uniqueness
    if crud.get_student_by_roll(db, student_in.roll_number):
        raise HTTPException(
            status_code=400,
            detail=f"Student with roll number '{student_in.roll_number}' already exists."
        )
    # Check email uniqueness
    if crud.get_student_by_email(db, student_in.email):
        raise HTTPException(
            status_code=400,
            detail=f"Student with email '{student_in.email}' already exists."
        )
    # Validate department exists
    if not crud.get_department_by_id(db, student_in.department_id):
        raise HTTPException(
            status_code=404,
            detail=f"Department with ID {student_in.department_id} does not exist."
        )

    student = crud.create_student(db, student_in)
    return schemas.StudentOut(
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
        gpa=None,
        created_at=student.created_at,
        updated_at=student.updated_at
    )

@router.put("/{student_id}", response_model=schemas.StudentOut)
def update_student(student_id: int, student_in: schemas.StudentUpdate, db: Session = Depends(get_db)):
    """Update student information."""
    existing = crud.get_student_by_id(db, student_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Student not found")

    # If roll number is changing, ensure uniqueness
    if student_in.roll_number and student_in.roll_number != existing.roll_number:
        if crud.get_student_by_roll(db, student_in.roll_number):
            raise HTTPException(status_code=400, detail="Roll number already in use by another student.")

    # If email is changing, ensure uniqueness
    if student_in.email and student_in.email != existing.email:
        if crud.get_student_by_email(db, student_in.email):
            raise HTTPException(status_code=400, detail="Email address already in use by another student.")

    if student_in.department_id:
        if not crud.get_department_by_id(db, student_in.department_id):
            raise HTTPException(status_code=404, detail="Specified Department does not exist.")

    updated = crud.update_student(db, student_id, student_in)
    return schemas.StudentOut(
        id=updated.id,
        roll_number=updated.roll_number,
        first_name=updated.first_name,
        last_name=updated.last_name,
        full_name=updated.full_name,
        email=updated.email,
        phone=updated.phone,
        date_of_birth=updated.date_of_birth,
        gender=updated.gender,
        address=updated.address,
        department_id=updated.department_id,
        department_name=updated.department.name if updated.department else None,
        department_code=updated.department.code if updated.department else None,
        year_of_study=updated.year_of_study,
        semester=updated.semester,
        status=updated.status,
        enrollment_date=updated.enrollment_date,
        gpa=crud.calculate_student_gpa(db, updated.id),
        created_at=updated.created_at,
        updated_at=updated.updated_at
    )

@router.delete("/{student_id}", response_model=schemas.MessageResponse)
def delete_student(student_id: int, db: Session = Depends(get_db)):
    """Delete a student and cascade records."""
    success = crud.delete_student(db, student_id)
    if not success:
        raise HTTPException(status_code=404, detail="Student not found")
    return schemas.MessageResponse(message=f"Student ID {student_id} successfully deleted.")
