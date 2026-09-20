from datetime import datetime, date
from enum import Enum as PyEnum
from sqlalchemy import (
    Column, Integer, String, Text, Date, DateTime, Numeric, Enum, ForeignKey, UniqueConstraint, SmallInteger
)
from sqlalchemy.orm import relationship
from backend.app.database import Base


class RoleEnum(str, PyEnum):
    ADMIN = "ADMIN"
    TEACHER = "TEACHER"
    STUDENT = "STUDENT"
    ADMISSION_OFFICER = "ADMISSION_OFFICER"


class UserStatusEnum(str, PyEnum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    LOCKED = "LOCKED"


class StatusEnum(str, PyEnum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


class DegreeTypeEnum(str, PyEnum):
    UG = "UG"
    PG = "PG"


class GenderEnum(str, PyEnum):
    MALE = "MALE"
    FEMALE = "FEMALE"
    OTHER = "OTHER"


class StudentStatusEnum(str, PyEnum):
    ACTIVE = "ACTIVE"
    PROBATION = "PROBATION"
    GRADUATED = "GRADUATED"
    ON_LEAVE = "ON_LEAVE"
    INACTIVE = "INACTIVE"


class StaffTypeEnum(str, PyEnum):
    TEACHER = "TEACHER"
    ADMISSION_OFFICER = "ADMISSION_OFFICER"
    ADMINISTRATOR = "ADMINISTRATOR"
    OTHER = "OTHER"


class AdmissionStatusEnum(str, PyEnum):
    PENDING = "PENDING"
    UNDER_REVIEW = "UNDER_REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"


class ApplicationStatusEnum(str, PyEnum):
    PENDING = "PENDING"
    UNDER_REVIEW = "UNDER_REVIEW"
    DOCUMENTS_REQUIRED = "DOCUMENTS_REQUIRED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class EnrollmentStatusEnum(str, PyEnum):
    ENROLLED = "ENROLLED"
    COMPLETED = "COMPLETED"
    DROPPED = "DROPPED"


class AttendanceStatusEnum(str, PyEnum):
    PRESENT = "PRESENT"
    ABSENT = "ABSENT"


class DocumentStatusEnum(str, PyEnum):
    VERIFIED = "VERIFIED"
    PENDING = "PENDING"
    REJECTED = "REJECTED"


class MaterialStatusEnum(str, PyEnum):
    DRAFT = "DRAFT"
    PUBLISHED = "PUBLISHED"
    ARCHIVED = "ARCHIVED"


class TargetTypeEnum(str, PyEnum):
    ALL = "ALL"
    STUDENTS = "STUDENTS"
    CLASS = "CLASS"


class UserAccount(Base):
    __tablename__ = "user_account"

    user_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(RoleEnum), nullable=False)
    email = Column(String(150), unique=True, nullable=False, index=True)
    status = Column(Enum(UserStatusEnum), default=UserStatusEnum.ACTIVE)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    staff_profile = relationship("Staff", back_populates="user_account", uselist=False)
    student_profile = relationship("Student", back_populates="user_account", uselist=False)


class Department(Base):
    __tablename__ = "departments"

    department_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    department_name = Column(String(150), unique=True, nullable=False)
    department_code = Column(String(30), unique=True, nullable=False)
    building = Column(String(100), nullable=True)
    hod_name = Column(String(150), nullable=True)
    hod_email = Column(String(150), nullable=True)
    hod_phone = Column(String(30), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    programs = relationship("Program", back_populates="department", cascade="all, delete-orphan")
    staff_members = relationship("Staff", back_populates="department")
    students = relationship("Student", back_populates="department", cascade="all, delete-orphan")
    courses = relationship("Course", back_populates="department", cascade="all, delete-orphan")


class Program(Base):
    __tablename__ = "programs"

    program_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    department_id = Column(Integer, ForeignKey("departments.department_id", ondelete="CASCADE"), nullable=False)
    program_name = Column(String(150), unique=True, nullable=False)
    program_code = Column(String(30), unique=True, nullable=False)
    description = Column(String(1000), nullable=True)
    degree_type = Column(Enum(DegreeTypeEnum), default=DegreeTypeEnum.UG)
    duration_years = Column(Integer, nullable=False, default=4)
    capacity = Column(Integer, nullable=False, default=60)
    status = Column(Enum(StatusEnum), default=StatusEnum.ACTIVE)

    department = relationship("Department", back_populates="programs")
    students = relationship("Student", back_populates="program", cascade="all, delete-orphan")
    classes = relationship("Class", back_populates="program", cascade="all, delete-orphan")
    admissions = relationship("Admission", back_populates="program")


class Staff(Base):
    __tablename__ = "staff"

    staff_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user_account.user_id", ondelete="CASCADE"), unique=True, nullable=False)
    department_id = Column(Integer, ForeignKey("departments.department_id", ondelete="SET NULL"), nullable=True)
    first_name = Column(String(80), nullable=False)
    last_name = Column(String(80), nullable=False)
    staff_name = Column(String(170), nullable=False)
    designation = Column(String(100), nullable=True)
    qualification = Column(String(200), nullable=True)
    staff_type = Column(Enum(StaffTypeEnum), default=StaffTypeEnum.TEACHER)
    email = Column(String(150), unique=True, nullable=False)
    phone = Column(String(30), nullable=True)
    joining_date = Column(Date, nullable=True)
    experience_years = Column(Integer, default=0)

    user_account = relationship("UserAccount", back_populates="staff_profile")
    department = relationship("Department", back_populates="staff_members")
    classes = relationship("Class", back_populates="staff", cascade="all, delete-orphan")
    study_materials = relationship("StudyMaterial", back_populates="staff", cascade="all, delete-orphan")
    announcements = relationship("Announcement", back_populates="staff", cascade="all, delete-orphan")


class Student(Base):
    __tablename__ = "students"

    student_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user_account.user_id", ondelete="CASCADE"), unique=True, nullable=False)
    usn = Column(String(30), unique=True, nullable=False, index=True)
    registration_number = Column(String(50), unique=True, nullable=False)
    first_name = Column(String(80), nullable=False)
    last_name = Column(String(80), nullable=False)
    student_name = Column(String(170), nullable=False)
    email = Column(String(150), unique=True, nullable=False)
    phone = Column(String(30), nullable=True)
    address = Column(String(500), nullable=True)
    date_of_birth = Column(Date, nullable=False)
    gender = Column(Enum(GenderEnum), nullable=True)
    department_id = Column(Integer, ForeignKey("departments.department_id", ondelete="CASCADE"), nullable=False)
    program_id = Column(Integer, ForeignKey("programs.program_id", ondelete="CASCADE"), nullable=False)
    admission_date = Column(Date, default=date.today)
    enrollment_date = Column(Date, default=date.today)
    academic_year = Column(String(20), nullable=False)
    semester = Column(String(30), nullable=False)
    gpa = Column(Numeric(3, 2), default=0.00)
    status = Column(Enum(StudentStatusEnum), default=StudentStatusEnum.ACTIVE)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user_account = relationship("UserAccount", back_populates="student_profile")
    department = relationship("Department", back_populates="students")
    program = relationship("Program", back_populates="students")
    enrollments = relationship("Enrollment", back_populates="student", cascade="all, delete-orphan")
    attendance_records = relationship("Attendance", back_populates="student", cascade="all, delete-orphan")
    internal_marks = relationship("InternalMarks", back_populates="student", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="student", cascade="all, delete-orphan")
    admissions = relationship("Admission", back_populates="student")


class Parent(Base):
    __tablename__ = "parents"

    parent_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    parent_name = Column(String(150), nullable=False)
    relationship = Column(String(50), nullable=True)
    phone = Column(String(30), nullable=True)
    email = Column(String(150), nullable=True)
    occupation = Column(String(100), nullable=True)
    address = Column(String(500), nullable=True)


class StudentParent(Base):
    __tablename__ = "student_parent"

    student_id = Column(Integer, ForeignKey("students.student_id", ondelete="CASCADE"), primary_key=True)
    parent_id = Column(Integer, ForeignKey("parents.parent_id", ondelete="CASCADE"), primary_key=True)
    is_primary = Column(SmallInteger, default=0)


class Admission(Base):
    __tablename__ = "admissions"

    admission_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("students.student_id", ondelete="SET NULL"), nullable=True)
    usn = Column(String(30), nullable=True)
    application_number = Column(String(50), unique=True, nullable=False)
    program_id = Column(Integer, ForeignKey("programs.program_id", ondelete="SET NULL"), nullable=True)
    admission_year = Column(Integer, nullable=True)
    admission_type = Column(String(50), nullable=True)
    admission_date = Column(Date, nullable=True)
    status = Column(Enum(AdmissionStatusEnum), default=AdmissionStatusEnum.PENDING)

    student = relationship("Student", back_populates="admissions")
    program = relationship("Program", back_populates="admissions")


class Application(Base):
    __tablename__ = "applications"

    application_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    application_number = Column(String(50), unique=True, nullable=False)
    applicant_name = Column(String(170), nullable=False)
    email = Column(String(150), nullable=False)
    phone = Column(String(30), nullable=True)
    program_id = Column(Integer, ForeignKey("programs.program_id", ondelete="CASCADE"), nullable=False)
    application_date = Column(Date, default=date.today)
    status = Column(Enum(ApplicationStatusEnum), default=ApplicationStatusEnum.PENDING)
    documents_path = Column(String(500), nullable=True)
    notes = Column(String(2000), nullable=True)

    program = relationship("Program")


class Course(Base):
    __tablename__ = "courses"

    course_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    course_code = Column(String(30), unique=True, nullable=False)
    course_name = Column(String(150), nullable=False)
    credits = Column(Integer, default=3)
    department_id = Column(Integer, ForeignKey("departments.department_id", ondelete="CASCADE"), nullable=False)
    semester = Column(String(30), nullable=False)

    department = relationship("Department", back_populates="courses")
    classes = relationship("Class", back_populates="course", cascade="all, delete-orphan")
    study_materials = relationship("StudyMaterial", back_populates="course", cascade="all, delete-orphan")


class Class(Base):
    __tablename__ = "classes"

    class_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    course_id = Column(Integer, ForeignKey("courses.course_id", ondelete="CASCADE"), nullable=False)
    program_id = Column(Integer, ForeignKey("programs.program_id", ondelete="CASCADE"), nullable=False)
    staff_id = Column(Integer, ForeignKey("staff.staff_id", ondelete="CASCADE"), nullable=False)
    academic_year = Column(String(20), nullable=False)
    semester = Column(String(30), nullable=False)
    schedule = Column(String(100), nullable=True)
    room = Column(String(50), nullable=True)
    capacity = Column(Integer, nullable=False)

    course = relationship("Course", back_populates="classes")
    program = relationship("Program", back_populates="classes")
    staff = relationship("Staff", back_populates="classes")
    enrollments = relationship("Enrollment", back_populates="class_obj", cascade="all, delete-orphan")
    attendance_records = relationship("Attendance", back_populates="class_obj", cascade="all, delete-orphan")
    internal_marks = relationship("InternalMarks", back_populates="class_obj", cascade="all, delete-orphan")
    study_materials = relationship("StudyMaterial", back_populates="class_obj", cascade="all, delete-orphan")
    announcements = relationship("Announcement", back_populates="class_obj", cascade="all, delete-orphan")


class Enrollment(Base):
    __tablename__ = "enrollments"

    enrollment_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("students.student_id", ondelete="CASCADE"), nullable=False)
    class_id = Column(Integer, ForeignKey("classes.class_id", ondelete="CASCADE"), nullable=False)
    enrollment_date = Column(Date, default=date.today)
    status = Column(Enum(EnrollmentStatusEnum), default=EnrollmentStatusEnum.ENROLLED)

    student = relationship("Student", back_populates="enrollments")
    class_obj = relationship("Class", back_populates="enrollments")

    __table_args__ = (UniqueConstraint("student_id", "class_id", name="uk_student_class"),)


class Attendance(Base):
    __tablename__ = "attendance"

    attendance_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("students.student_id", ondelete="CASCADE"), nullable=False)
    class_id = Column(Integer, ForeignKey("classes.class_id", ondelete="CASCADE"), nullable=False)
    date_recorded = Column(Date, default=date.today)
    status = Column(Enum(AttendanceStatusEnum), nullable=False)

    student = relationship("Student", back_populates="attendance_records")
    class_obj = relationship("Class", back_populates="attendance_records")

    __table_args__ = (UniqueConstraint("student_id", "class_id", "date_recorded", name="uk_student_class_date"),)


class InternalMarks(Base):
    __tablename__ = "internal_marks"

    mark_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("students.student_id", ondelete="CASCADE"), nullable=False)
    class_id = Column(Integer, ForeignKey("classes.class_id", ondelete="CASCADE"), nullable=False)
    assessment_name = Column(String(100), nullable=False)
    internal_marks = Column(Numeric(5, 2), default=0.00)
    assignment_marks = Column(Numeric(5, 2), default=0.00)
    exam_marks = Column(Numeric(5, 2), default=0.00)
    total_marks = Column(Numeric(5, 2), default=0.00)
    grade = Column(String(5), nullable=False)
    semester = Column(String(30), nullable=False)
    remarks = Column(String(500), nullable=True)

    student = relationship("Student", back_populates="internal_marks")
    class_obj = relationship("Class", back_populates="internal_marks")

    __table_args__ = (UniqueConstraint("student_id", "class_id", "assessment_name", name="uk_student_class_assessment"),)


class Document(Base):
    __tablename__ = "documents"

    document_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("students.student_id", ondelete="CASCADE"), nullable=False)
    document_type = Column(String(100), nullable=False)
    file_path = Column(String(500), nullable=False)
    original_name = Column(String(255), nullable=True)
    upload_date = Column(DateTime, default=datetime.utcnow)
    uploaded_by = Column(Integer, ForeignKey("user_account.user_id", ondelete="SET NULL"), nullable=True)
    status = Column(Enum(DocumentStatusEnum), default=DocumentStatusEnum.PENDING)
    rejection_reason = Column(String(1000), nullable=True)

    student = relationship("Student", back_populates="documents")
    receipt = relationship("DocumentReceipt", back_populates="document", uselist=False, cascade="all, delete-orphan")


class DocumentReceipt(Base):
    __tablename__ = "document_receipts"

    receipt_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    document_id = Column(Integer, ForeignKey("documents.document_id", ondelete="CASCADE"), nullable=False)
    receipt_number = Column(String(100), unique=True, nullable=False)
    submission_date = Column(DateTime, default=datetime.utcnow)
    remarks = Column(String(1000), nullable=True)

    document = relationship("Document", back_populates="receipt")


class StudyMaterial(Base):
    __tablename__ = "study_materials"

    material_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    description = Column(String(2000), nullable=True)
    course_id = Column(Integer, ForeignKey("courses.course_id", ondelete="CASCADE"), nullable=False)
    class_id = Column(Integer, ForeignKey("classes.class_id", ondelete="CASCADE"), nullable=False)
    staff_id = Column(Integer, ForeignKey("staff.staff_id", ondelete="CASCADE"), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(30), nullable=False)
    academic_year = Column(String(20), nullable=False)
    semester = Column(String(30), nullable=False)
    upload_date = Column(DateTime, default=datetime.utcnow)
    published_status = Column(Enum(MaterialStatusEnum), default=MaterialStatusEnum.DRAFT)

    course = relationship("Course", back_populates="study_materials")
    class_obj = relationship("Class", back_populates="study_materials")
    staff = relationship("Staff", back_populates="study_materials")


class Announcement(Base):
    __tablename__ = "announcements"

    announcement_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    staff_id = Column(Integer, ForeignKey("staff.staff_id", ondelete="CASCADE"), nullable=False)
    class_id = Column(Integer, ForeignKey("classes.class_id", ondelete="CASCADE"), nullable=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    target_type = Column(Enum(TargetTypeEnum), default=TargetTypeEnum.CLASS)
    created_at = Column(DateTime, default=datetime.utcnow)

    staff = relationship("Staff", back_populates="announcements")
    class_obj = relationship("Class", back_populates="announcements")
