from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models import (
    UserAccount, Staff, Student, Department, Program, Course, Class,
    Admission, Application, Document, Announcement, RoleEnum,
    AdmissionStatusEnum, DocumentStatusEnum
)
from backend.app.schemas import (
    AdminStatsOut, UserAccountOut, UserAccountCreate, UserAccountUpdate
)
from backend.app.dependencies import require_roles, get_current_user
from backend.app.utils.security import hash_password

router = APIRouter(prefix="/api/admin", tags=["Admin Management"])


@router.get("/stats", response_model=AdminStatsOut, summary="Get Live Admin Dashboard Statistics")
def get_admin_stats(
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(require_roles([RoleEnum.ADMIN]))
):
    """Return aggregated real-time database metrics."""
    total_students = db.query(Student).count()
    total_teachers = db.query(Staff).count()
    total_departments = db.query(Department).count()
    total_programs = db.query(Program).count()
    total_courses = db.query(Course).count()
    total_classes = db.query(Class).count()
    
    pending_applications = db.query(Application).filter(Application.status == "PENDING").count()
    pending_admissions = db.query(Admission).filter(Admission.status == AdmissionStatusEnum.PENDING).count()
    pending_documents = db.query(Document).filter(Document.status == DocumentStatusEnum.PENDING).count()

    recent_apps = db.query(Admission).order_by(Admission.admission_id.desc()).limit(5).all()
    recent_applications = [
        {
            "id": app.admission_id,
            "application_number": app.application_number,
            "applicant_name": app.student.student_name if app.student else app.usn or "N/A",
            "program": app.program.program_name if app.program else "N/A",
            "status": app.status.value if app.status else "PENDING",
            "date": app.admission_date.isoformat() if app.admission_date else ""
        }
        for app in recent_apps
    ]

    recent_ann = db.query(Announcement).order_by(Announcement.announcement_id.desc()).limit(5).all()
    recent_announcements = [
        {
            "id": ann.announcement_id,
            "title": ann.title,
            "target_audience": ann.target_type.value if ann.target_type else "ALL",
            "created_at": ann.created_at.isoformat() if ann.created_at else ""
        }
        for ann in recent_ann
    ]

    return AdminStatsOut(
        total_students=total_students,
        total_teachers=total_teachers,
        total_departments=total_departments,
        total_programs=total_programs,
        total_courses=total_courses,
        total_classes=total_classes,
        pending_applications=pending_applications,
        pending_admissions=pending_admissions,
        pending_documents=pending_documents,
        recent_applications=recent_applications,
        recent_announcements=recent_announcements
    )


@router.get("/users", response_model=List[UserAccountOut], summary="List Users")
def list_users(
    role: Optional[RoleEnum] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(require_roles([RoleEnum.ADMIN]))
):
    query = db.query(UserAccount)
    if role:
        query = query.filter(UserAccount.role == role)
    if search:
        pattern = f"%{search}%"
        query = query.filter(
            (UserAccount.username.like(pattern)) | (UserAccount.email.like(pattern))
        )
    return query.order_by(UserAccount.user_id.desc()).all()


@router.post("/users", response_model=UserAccountOut, status_code=status.HTTP_201_CREATED, summary="Create User")
def create_user(
    data: UserAccountCreate,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(require_roles([RoleEnum.ADMIN]))
):
    existing = db.query(UserAccount).filter(
        (UserAccount.username == data.username) | (UserAccount.email == data.email)
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username or email already exists"
        )

    new_user = UserAccount(
        username=data.username,
        email=data.email,
        password_hash=hash_password(data.password),
        role=data.role,
        status=data.status
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.get("/users/{user_id}", response_model=UserAccountOut, summary="Get User Details")
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(require_roles([RoleEnum.ADMIN]))
):
    user = db.query(UserAccount).filter(UserAccount.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.put("/users/{user_id}", response_model=UserAccountOut, summary="Update User")
def update_user(
    user_id: int,
    data: UserAccountUpdate,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(require_roles([RoleEnum.ADMIN]))
):
    user = db.query(UserAccount).filter(UserAccount.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if data.username and data.username != user.username:
        if db.query(UserAccount).filter(UserAccount.username == data.username).first():
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username taken")
        user.username = data.username

    if data.email and data.email != user.email:
        if db.query(UserAccount).filter(UserAccount.email == data.email).first():
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email taken")
        user.email = data.email

    if data.password:
        user.password_hash = hash_password(data.password)

    if data.role:
        user.role = data.role

    if data.status:
        user.status = data.status

    db.commit()
    db.refresh(user)
    return user


@router.delete("/users/{user_id}", summary="Delete User Account")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(require_roles([RoleEnum.ADMIN]))
):
    if user_id == current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete the currently logged in administrator account"
        )

    user = db.query(UserAccount).filter(UserAccount.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    db.delete(user)
    db.commit()
    return {"message": f"User '{user.username}' deleted successfully"}
