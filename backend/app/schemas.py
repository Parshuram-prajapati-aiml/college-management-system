from datetime import datetime, date
from typing import Optional, List
from decimal import Decimal
from pydantic import BaseModel, EmailStr
from backend.app.models import (
    RoleEnum, UserStatusEnum, StatusEnum, DegreeTypeEnum, GenderEnum,
    StudentStatusEnum, StaffTypeEnum, AdmissionStatusEnum, ApplicationStatusEnum,
    EnrollmentStatusEnum, AttendanceStatusEnum, DocumentStatusEnum,
    MaterialStatusEnum, TargetTypeEnum
)


# Auth Schemas
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    username: str
    role: RoleEnum


class TokenData(BaseModel):
    user_id: Optional[int] = None
    username: Optional[str] = None
    role: Optional[RoleEnum] = None


class LoginRequest(BaseModel):
    username: str  # accepts username or email
    password: str


class UserAccountOut(BaseModel):
    user_id: int
    username: str
    email: str
    role: RoleEnum
    status: UserStatusEnum
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserAccountCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: RoleEnum
    status: UserStatusEnum = UserStatusEnum.ACTIVE


class UserAccountUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    role: Optional[RoleEnum] = None
    status: Optional[UserStatusEnum] = None


# Department Schemas
class DepartmentBase(BaseModel):
    department_name: str
    department_code: str
    building: Optional[str] = None
    hod_name: Optional[str] = None
    hod_email: Optional[EmailStr] = None
    hod_phone: Optional[str] = None


class DepartmentCreate(DepartmentBase):
    pass


class DepartmentUpdate(BaseModel):
    department_name: Optional[str] = None
    department_code: Optional[str] = None
    building: Optional[str] = None
    hod_name: Optional[str] = None
    hod_email: Optional[EmailStr] = None
    hod_phone: Optional[str] = None


class DepartmentOut(DepartmentBase):
    department_id: int
    created_at: Optional[datetime] = None
    programs_count: Optional[int] = 0
    students_count: Optional[int] = 0

    class Config:
        from_attributes = True


# Program Schemas
class ProgramBase(BaseModel):
    program_name: str
    program_code: str
    department_id: int
    description: Optional[str] = None
    degree_type: DegreeTypeEnum = DegreeTypeEnum.UG
    duration_years: int = 4
    capacity: int = 60
    status: StatusEnum = StatusEnum.ACTIVE


class ProgramCreate(ProgramBase):
    pass


class ProgramUpdate(BaseModel):
    program_name: Optional[str] = None
    program_code: Optional[str] = None
    department_id: Optional[int] = None
    description: Optional[str] = None
    degree_type: Optional[DegreeTypeEnum] = None
    duration_years: Optional[int] = None
    capacity: Optional[int] = None
    status: Optional[StatusEnum] = None


class ProgramOut(ProgramBase):
    program_id: int
    department_name: Optional[str] = None

    class Config:
        from_attributes = True


# Staff / Teacher Schemas
class StaffBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: Optional[str] = None
    department_id: Optional[int] = None
    designation: Optional[str] = None
    qualification: Optional[str] = None
    staff_type: StaffTypeEnum = StaffTypeEnum.TEACHER
    joining_date: Optional[date] = None
    experience_years: Optional[int] = 0


class StaffCreate(StaffBase):
    username: Optional[str] = None
    password: Optional[str] = None


class StaffUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    department_id: Optional[int] = None
    designation: Optional[str] = None
    qualification: Optional[str] = None
    staff_type: Optional[StaffTypeEnum] = None
    joining_date: Optional[date] = None
    experience_years: Optional[int] = None


class StaffOut(StaffBase):
    staff_id: int
    user_id: int
    staff_name: str
    department_name: Optional[str] = None

    class Config:
        from_attributes = True


# Student Schemas
class StudentBase(BaseModel):
    usn: str
    registration_number: str
    first_name: str
    last_name: str
    email: EmailStr
    phone: Optional[str] = None
    address: Optional[str] = None
    date_of_birth: date
    gender: Optional[GenderEnum] = GenderEnum.MALE
    department_id: int
    program_id: int
    admission_date: Optional[date] = None
    enrollment_date: Optional[date] = None
    academic_year: str = "2025-2026"
    semester: str = "Semester 1"
    gpa: Optional[Decimal] = 0.00
    status: StudentStatusEnum = StudentStatusEnum.ACTIVE


class StudentCreate(StudentBase):
    username: Optional[str] = None
    password: Optional[str] = None


class StudentUpdate(BaseModel):
    usn: Optional[str] = None
    registration_number: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[GenderEnum] = None
    department_id: Optional[int] = None
    program_id: Optional[int] = None
    academic_year: Optional[str] = None
    semester: Optional[str] = None
    gpa: Optional[Decimal] = None
    status: Optional[StudentStatusEnum] = None


class StudentOut(StudentBase):
    student_id: int
    user_id: int
    student_name: str
    created_at: Optional[datetime] = None
    department_name: Optional[str] = None
    program_name: Optional[str] = None

    class Config:
        from_attributes = True


# Admission Schemas
class AdmissionBase(BaseModel):
    application_number: str
    student_id: Optional[int] = None
    usn: Optional[str] = None
    program_id: Optional[int] = None
    admission_year: Optional[int] = None
    admission_type: Optional[str] = "REGULAR"
    admission_date: Optional[date] = None
    status: AdmissionStatusEnum = AdmissionStatusEnum.PENDING


class AdmissionCreate(AdmissionBase):
    pass


class AdmissionUpdate(BaseModel):
    student_id: Optional[int] = None
    usn: Optional[str] = None
    program_id: Optional[int] = None
    admission_year: Optional[int] = None
    admission_type: Optional[str] = None
    admission_date: Optional[date] = None
    status: Optional[AdmissionStatusEnum] = None


class AdmissionOut(AdmissionBase):
    admission_id: int
    program_name: Optional[str] = None
    student_name: Optional[str] = None

    class Config:
        from_attributes = True


# Course Schemas
class CourseBase(BaseModel):
    course_code: str
    course_name: str
    credits: int = 3
    department_id: int
    semester: str = "Semester 1"


class CourseCreate(CourseBase):
    pass


class CourseUpdate(BaseModel):
    course_code: Optional[str] = None
    course_name: Optional[str] = None
    credits: Optional[int] = None
    department_id: Optional[int] = None
    semester: Optional[str] = None


class CourseOut(CourseBase):
    course_id: int
    department_name: Optional[str] = None

    class Config:
        from_attributes = True


# Class Schemas
class ClassBase(BaseModel):
    course_id: int
    program_id: int
    staff_id: int
    academic_year: str
    semester: str
    schedule: Optional[str] = None
    room: Optional[str] = None
    capacity: int = 60


class ClassCreate(ClassBase):
    pass


class ClassUpdate(BaseModel):
    course_id: Optional[int] = None
    program_id: Optional[int] = None
    staff_id: Optional[int] = None
    academic_year: Optional[str] = None
    semester: Optional[str] = None
    schedule: Optional[str] = None
    room: Optional[str] = None
    capacity: Optional[int] = None


class ClassOut(ClassBase):
    class_id: int
    course_code: Optional[str] = None
    course_name: Optional[str] = None
    program_name: Optional[str] = None
    teacher_name: Optional[str] = None

    class Config:
        from_attributes = True


# Attendance Schemas
class AttendanceBatchItem(BaseModel):
    student_id: int
    status: AttendanceStatusEnum = AttendanceStatusEnum.PRESENT


class AttendanceBatchCreate(BaseModel):
    class_id: int
    date_recorded: date
    records: List[AttendanceBatchItem]


class AttendanceOut(BaseModel):
    attendance_id: int
    student_id: int
    class_id: int
    date_recorded: date
    status: AttendanceStatusEnum
    student_name: Optional[str] = None
    usn: Optional[str] = None

    class Config:
        from_attributes = True


class StudentAttendanceSummary(BaseModel):
    course_code: str
    course_name: str
    total_classes: int
    present_count: int
    absent_count: int
    percentage: float


# Internal Marks Schemas
class InternalMarksCreate(BaseModel):
    student_id: int
    class_id: int
    assessment_name: str
    semester: str
    internal_marks: Decimal = 0.00
    assignment_marks: Decimal = 0.00
    exam_marks: Decimal = 0.00
    remarks: Optional[str] = None


class InternalMarksUpdate(BaseModel):
    internal_marks: Optional[Decimal] = None
    assignment_marks: Optional[Decimal] = None
    exam_marks: Optional[Decimal] = None
    remarks: Optional[str] = None


class InternalMarksOut(BaseModel):
    mark_id: int
    student_id: int
    class_id: int
    assessment_name: str
    semester: str
    internal_marks: Decimal
    assignment_marks: Decimal
    exam_marks: Decimal
    total_marks: Decimal
    grade: str
    remarks: Optional[str] = None
    student_name: Optional[str] = None
    usn: Optional[str] = None
    course_name: Optional[str] = None

    class Config:
        from_attributes = True


# Document Schemas
class DocumentRejectRequest(BaseModel):
    rejection_reason: str


class DocumentReceiptOut(BaseModel):
    receipt_id: int
    document_id: int
    receipt_number: str
    submission_date: Optional[datetime] = None
    remarks: Optional[str] = None

    class Config:
        from_attributes = True


class DocumentOut(BaseModel):
    document_id: int
    student_id: int
    document_type: str
    file_path: str
    original_name: Optional[str] = None
    upload_date: Optional[datetime] = None
    uploaded_by: Optional[int] = None
    status: DocumentStatusEnum
    rejection_reason: Optional[str] = None
    student_name: Optional[str] = None
    usn: Optional[str] = None
    receipt: Optional[DocumentReceiptOut] = None

    class Config:
        from_attributes = True


# Study Material Schemas
class StudyMaterialCreate(BaseModel):
    title: str
    course_id: int
    class_id: int
    description: Optional[str] = None
    academic_year: str
    semester: str
    published_status: MaterialStatusEnum = MaterialStatusEnum.PUBLISHED


class StudyMaterialUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    published_status: Optional[MaterialStatusEnum] = None


class StudyMaterialOut(BaseModel):
    material_id: int
    title: str
    description: Optional[str] = None
    course_id: int
    class_id: int
    staff_id: int
    file_path: str
    file_type: str
    academic_year: str
    semester: str
    upload_date: Optional[datetime] = None
    published_status: MaterialStatusEnum
    teacher_name: Optional[str] = None
    course_name: Optional[str] = None

    class Config:
        from_attributes = True


# Announcement Schemas
class AnnouncementCreate(BaseModel):
    title: str
    content: str
    target_type: TargetTypeEnum = TargetTypeEnum.ALL
    class_id: Optional[int] = None


class AnnouncementUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    target_type: Optional[TargetTypeEnum] = None
    class_id: Optional[int] = None


class AnnouncementOut(BaseModel):
    announcement_id: int
    staff_id: int
    title: str
    content: str
    target_type: TargetTypeEnum
    class_id: Optional[int] = None
    created_at: Optional[datetime] = None
    author_name: Optional[str] = None

    class Config:
        from_attributes = True


# Dashboard Statistics Schema
class AdminStatsOut(BaseModel):
    total_students: int
    total_teachers: int
    total_departments: int
    total_programs: int
    total_courses: int
    total_classes: int
    pending_applications: int
    pending_admissions: int
    pending_documents: int
    recent_applications: List[dict]
    recent_announcements: List[dict]
