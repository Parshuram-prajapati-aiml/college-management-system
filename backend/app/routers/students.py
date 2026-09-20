from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models import Student, UserAccount, Department, Program, RoleEnum, StudentStatusEnum
from backend.app.schemas import StudentOut, StudentCreate, StudentUpdate
from backend.app.dependencies import require_roles, get_current_user
from backend.app.utils.security import hash_password

router = APIRouter(prefix="/api/students", tags=["Student Management"])


def _format_student(student: Student) -> StudentOut:
    out = StudentOut.model_validate(student)
    out.department_name = student.department.department_name if student.department else None
    out.program_name = student.program.program_name if student.program else None
    return out


@router.get("", response_model=List[StudentOut], summary="List / Search Students")
def list_students(
    search: Optional[str] = None,
    usn: Optional[str] = None,
    department_id: Optional[int] = None,
    program_id: Optional[int] = None,
    semester: Optional[str] = None,
    status_filter: Optional[StudentStatusEnum] = Query(None, alias="status"),
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(require_roles([RoleEnum.ADMIN, RoleEnum.TEACHER, RoleEnum.ADMISSION_OFFICER]))
):
    query = db.query(Student)

    if usn:
        query = query.filter(Student.usn.ilike(f"%{usn}%"))
    if search:
        pat = f"%{search}%"
        query = query.filter(
            (Student.first_name.ilike(pat)) |
            (Student.last_name.ilike(pat)) |
            (Student.email.ilike(pat)) |
            (Student.usn.ilike(pat)) |
            (Student.registration_number.ilike(pat))
        )
    if department_id:
        query = query.filter(Student.department_id == department_id)
    if program_id:
        query = query.filter(Student.program_id == program_id)
    if semester:
        query = query.filter(Student.semester == semester)
    if status_filter:
        query = query.filter(Student.status == status_filter)

    students = query.order_by(Student.student_id.desc()).all()
    return [_format_student(s) for s in students]


@router.post("", response_model=StudentOut, status_code=status.HTTP_201_CREATED, summary="Create Student")
def create_student(
    data: StudentCreate,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(require_roles([RoleEnum.ADMIN, RoleEnum.ADMISSION_OFFICER]))
):
    if db.query(Student).filter((Student.usn == data.usn) | (Student.email == data.email) | (Student.registration_number == data.registration_number)).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Student USN, Email, or Registration Number already registered"
        )

    user_id = None
    if data.username and data.password:
        if db.query(UserAccount).filter((UserAccount.username == data.username) | (UserAccount.email == data.email)).first():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User account username or email already exists"
            )
        new_user = UserAccount(
            username=data.username,
            email=data.email,
            password_hash=hash_password(data.password),
            role=RoleEnum.STUDENT
        )
        db.add(new_user)
        db.flush()
        user_id = new_user.user_id

    student = Student(
        user_id=user_id,
        usn=data.usn,
        registration_number=data.registration_number,
        first_name=data.first_name,
        last_name=data.last_name,
        student_name=f"{data.first_name} {data.last_name}",
        email=data.email,
        phone=data.phone,
        address=data.address,
        date_of_birth=data.date_of_birth,
        gender=data.gender,
        department_id=data.department_id,
        program_id=data.program_id,
        admission_date=data.admission_date,
        enrollment_date=data.enrollment_date,
        academic_year=data.academic_year,
        semester=data.semester,
        gpa=data.gpa,
        status=data.status
    )
    db.add(student)
    db.commit()
    db.refresh(student)
    return _format_student(student)


@router.get("/{student_id}", response_model=StudentOut, summary="Get Student Details")
def get_student(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
):
    student = db.query(Student).filter(Student.student_id == student_id).first()
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
    return _format_student(student)


@router.put("/{student_id}", response_model=StudentOut, summary="Update Student")
def update_student(
    student_id: int,
    data: StudentUpdate,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(require_roles([RoleEnum.ADMIN, RoleEnum.ADMISSION_OFFICER]))
):
    student = db.query(Student).filter(Student.student_id == student_id).first()
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")

    update_dict = data.model_dump(exclude_unset=True)
    for field, val in update_dict.items():
        setattr(student, field, val)

    student.student_name = f"{student.first_name} {student.last_name}"

    db.commit()
    db.refresh(student)
    return _format_student(student)


@router.delete("/{student_id}", summary="Delete Student")
def delete_student(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(require_roles([RoleEnum.ADMIN]))
):
    student = db.query(Student).filter(Student.student_id == student_id).first()
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")

    if student.user_account:
        db.delete(student.user_account)
    db.delete(student)
    db.commit()
    return {"message": "Student record deleted successfully"}
