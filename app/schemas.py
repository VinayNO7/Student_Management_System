from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal

# --- Department Schemas ---
class DepartmentBase(BaseModel):
    code: str = Field(..., max_length=20, examples=["CSE"])
    name: str = Field(..., max_length=120, examples=["Computer Science & Engineering"])
    head_of_department: Optional[str] = Field(None, max_length=100, examples=["Dr. Alan Turing"])
    description: Optional[str] = None

class DepartmentCreate(DepartmentBase):
    pass

class DepartmentUpdate(BaseModel):
    code: Optional[str] = Field(None, max_length=20)
    name: Optional[str] = Field(None, max_length=120)
    head_of_department: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None

class DepartmentOut(DepartmentBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: Optional[datetime] = None
    student_count: Optional[int] = 0
    course_count: Optional[int] = 0

# --- Course Schemas ---
class CourseBase(BaseModel):
    code: str = Field(..., max_length=20, examples=["CS101"])
    name: str = Field(..., max_length=120, examples=["Intro to Programming"])
    credits: int = Field(3, ge=1, le=10)
    department_id: int
    instructor: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None

class CourseCreate(CourseBase):
    pass

class CourseUpdate(BaseModel):
    code: Optional[str] = Field(None, max_length=20)
    name: Optional[str] = Field(None, max_length=120)
    credits: Optional[int] = Field(None, ge=1, le=10)
    department_id: Optional[int] = None
    instructor: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None

class CourseOut(CourseBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: Optional[datetime] = None
    department_name: Optional[str] = None

# --- Student Schemas ---
class StudentBase(BaseModel):
    roll_number: str = Field(..., max_length=30, examples=["STU-2024-001"])
    first_name: str = Field(..., max_length=50)
    last_name: str = Field(..., max_length=50)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=25)
    date_of_birth: Optional[date] = None
    gender: str = Field("Other", examples=["Male", "Female", "Other"])
    address: Optional[str] = None
    department_id: int
    year_of_study: int = Field(1, ge=1, le=6)
    semester: int = Field(1, ge=1, le=12)
    status: str = Field("Active", examples=["Active", "Graduated", "Suspended", "Inactive"])
    enrollment_date: date

class StudentCreate(StudentBase):
    pass

class StudentUpdate(BaseModel):
    roll_number: Optional[str] = Field(None, max_length=30)
    first_name: Optional[str] = Field(None, max_length=50)
    last_name: Optional[str] = Field(None, max_length=50)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=25)
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    address: Optional[str] = None
    department_id: Optional[int] = None
    year_of_study: Optional[int] = Field(None, ge=1, le=6)
    semester: Optional[int] = Field(None, ge=1, le=12)
    status: Optional[str] = None
    enrollment_date: Optional[date] = None

class StudentOut(StudentBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str
    department_name: Optional[str] = None
    department_code: Optional[str] = None
    gpa: Optional[float] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

# --- Enrollment Schemas ---
class EnrollmentBase(BaseModel):
    student_id: int
    course_id: int
    semester_name: str = Field(..., max_length=30, examples=["Fall 2024"])
    grade: Optional[str] = Field(None, max_length=5, examples=["A", "B+", "C", "F"])
    grade_point: Optional[Decimal] = Field(None, ge=0.0, le=4.0)
    status: str = Field("Enrolled", examples=["Enrolled", "Completed", "Dropped"])
    enrolled_date: date

class EnrollmentCreate(EnrollmentBase):
    pass

class EnrollmentUpdate(BaseModel):
    semester_name: Optional[str] = None
    grade: Optional[str] = None
    grade_point: Optional[Decimal] = None
    status: Optional[str] = None

class EnrollmentOut(EnrollmentBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    student_name: Optional[str] = None
    student_roll: Optional[str] = None
    course_code: Optional[str] = None
    course_name: Optional[str] = None
    course_credits: Optional[int] = None
    created_at: Optional[datetime] = None

# --- Attendance Schemas ---
class AttendanceBase(BaseModel):
    student_id: int
    course_id: int
    date: date
    status: str = Field("Present", examples=["Present", "Absent", "Late", "Excused"])
    remarks: Optional[str] = None

class AttendanceCreate(AttendanceBase):
    pass

class AttendanceUpdate(BaseModel):
    status: Optional[str] = None
    remarks: Optional[str] = None

class AttendanceOut(AttendanceBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    student_name: Optional[str] = None
    student_roll: Optional[str] = None
    course_code: Optional[str] = None
    course_name: Optional[str] = None
    created_at: Optional[datetime] = None

class AttendanceBatchItem(BaseModel):
    student_id: int
    status: str = Field("Present", examples=["Present", "Absent", "Late", "Excused"])
    remarks: Optional[str] = None

class AttendanceBatchCreate(BaseModel):
    course_id: int
    date: date
    records: List[AttendanceBatchItem]

class AttendanceBatchResponse(BaseModel):
    course_id: int
    date: date
    total_marked: int
    message: str

class CSVImportResponse(BaseModel):
    total_imported: int
    errors: List[str] = []
    message: str

# --- Detailed Student Profile Schema ---
class StudentDetailOut(StudentOut):
    enrollments: List[EnrollmentOut] = []
    attendance_records: List[AttendanceOut] = []
    attendance_percentage: Optional[float] = None

# --- Analytics / Dashboard Schemas ---
class DeptStat(BaseModel):
    department_id: int
    code: str
    name: str
    student_count: int

class StatsOut(BaseModel):
    total_students: int
    active_students: int
    graduated_students: int
    total_departments: int
    total_courses: int
    total_enrollments: int
    average_gpa: float
    department_distribution: List[DeptStat]

class MessageResponse(BaseModel):
    message: str
    success: bool = True
    detail: Optional[str] = None

class DBStatusResponse(BaseModel):
    engine: str
    connected: bool
    host: str
    port: int
    database: str
    message: str
