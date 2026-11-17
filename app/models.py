from sqlalchemy import Column, Integer, String, Text, Date, DateTime, Numeric, ForeignKey, Enum as SqlEnum, func
from sqlalchemy.orm import relationship
from app.database import Base
import enum

class GenderEnum(str, enum.Enum):
    Male = "Male"
    Female = "Female"
    Other = "Other"

class StudentStatusEnum(str, enum.Enum):
    Active = "Active"
    Graduated = "Graduated"
    Suspended = "Suspended"
    Inactive = "Inactive"

class EnrollmentStatusEnum(str, enum.Enum):
    Enrolled = "Enrolled"
    Completed = "Completed"
    Dropped = "Dropped"

class AttendanceStatusEnum(str, enum.Enum):
    Present = "Present"
    Absent = "Absent"
    Late = "Late"
    Excused = "Excused"

class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(120), nullable=False)
    head_of_department = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now())

    # Relationships
    students = relationship("Student", back_populates="department", cascade="all, delete-orphan")
    courses = relationship("Course", back_populates="department", cascade="all, delete-orphan")

class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    roll_number = Column(String(30), unique=True, nullable=False, index=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)
    phone = Column(String(25), nullable=True)
    date_of_birth = Column(Date, nullable=True)
    gender = Column(String(15), default="Other")
    address = Column(Text, nullable=True)
    department_id = Column(Integer, ForeignKey("departments.id", ondelete="RESTRICT"), nullable=False, index=True)
    year_of_study = Column(Integer, default=1, nullable=False)
    semester = Column(Integer, default=1, nullable=False)
    status = Column(String(20), default="Active", nullable=False, index=True)
    enrollment_date = Column(Date, nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    department = relationship("Department", back_populates="students")
    enrollments = relationship("Enrollment", back_populates="student", cascade="all, delete-orphan")
    attendance_records = relationship("Attendance", back_populates="student", cascade="all, delete-orphan")

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(120), nullable=False)
    credits = Column(Integer, default=3, nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id", ondelete="CASCADE"), nullable=False, index=True)
    description = Column(Text, nullable=True)
    instructor = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=func.now())

    # Relationships
    department = relationship("Department", back_populates="courses")
    enrollments = relationship("Enrollment", back_populates="course", cascade="all, delete-orphan")
    attendance_records = relationship("Attendance", back_populates="course", cascade="all, delete-orphan")

class Enrollment(Base):
    __tablename__ = "enrollments"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True)
    semester_name = Column(String(30), nullable=False)
    grade = Column(String(5), nullable=True)
    grade_point = Column(Numeric(3, 2), nullable=True)
    status = Column(String(20), default="Enrolled", nullable=False)
    enrolled_date = Column(Date, nullable=False)
    created_at = Column(DateTime, default=func.now())

    # Relationships
    student = relationship("Student", back_populates="enrollments")
    course = relationship("Course", back_populates="enrollments")

class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    status = Column(String(20), default="Present", nullable=False)
    remarks = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=func.now())

    # Relationships
    student = relationship("Student", back_populates="attendance_records")
    course = relationship("Course", back_populates="attendance_records")

