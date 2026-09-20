from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models import Staff, UserAccount, Department, RoleEnum, StaffTypeEnum
from backend.app.schemas import StaffOut, StaffCreate, StaffUpdate
from backend.app.dependencies import require_roles, get_current_user
from backend.app.utils.security import hash_password

router = APIRouter(prefix="/api/teachers", tags=["Teacher Management"])


def _format_staff(staff: Staff) -> StaffOut:
    out = StaffOut.model_validate(staff)
    out.department_name = staff.department.department_name if staff.department else None
    return out


@router.get("", response_model=List[StaffOut], summary="List Teachers / Staff")
def list_teachers(
    search: Optional[str] = None,
    department_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
):
    query = db.query(Staff)
    if search:
        pat = f"%{search}%"
        query = query.filter(
            (Staff.first_name.ilike(pat)) |
            (Staff.last_name.ilike(pat)) |
            (Staff.email.ilike(pat)) |
            (Staff.staff_name.ilike(pat))
        )
    if department_id:
        query = query.filter(Staff.department_id == department_id)

    staff_list = query.order_by(Staff.staff_id.desc()).all()
    return [_format_staff(s) for s in staff_list]


@router.post("", response_model=StaffOut, status_code=status.HTTP_201_CREATED, summary="Create Teacher/Staff")
def create_teacher(
    data: StaffCreate,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(require_roles([RoleEnum.ADMIN]))
):
    if db.query(Staff).filter(Staff.email == data.email).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Staff email already exists"
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
            role=RoleEnum.TEACHER if data.staff_type == StaffTypeEnum.TEACHER else RoleEnum.ADMISSION_OFFICER
        )
        db.add(new_user)
        db.flush()
        user_id = new_user.user_id

    staff = Staff(
        user_id=user_id,
        first_name=data.first_name,
        last_name=data.last_name,
        staff_name=f"{data.first_name} {data.last_name}",
        email=data.email,
        phone=data.phone,
        department_id=data.department_id,
        designation=data.designation,
        qualification=data.qualification,
        staff_type=data.staff_type,
        joining_date=data.joining_date,
        experience_years=data.experience_years or 0
    )
    db.add(staff)
    db.commit()
    db.refresh(staff)
    return _format_staff(staff)


@router.get("/{teacher_id}", response_model=StaffOut, summary="Get Teacher Details")
def get_teacher(
    teacher_id: int,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
):
    staff = db.query(Staff).filter(Staff.staff_id == teacher_id).first()
    if not staff:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Teacher not found")
    return _format_staff(staff)


@router.put("/{teacher_id}", response_model=StaffOut, summary="Update Teacher")
def update_teacher(
    teacher_id: int,
    data: StaffUpdate,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(require_roles([RoleEnum.ADMIN]))
):
    staff = db.query(Staff).filter(Staff.staff_id == teacher_id).first()
    if not staff:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Teacher not found")

    update_dict = data.model_dump(exclude_unset=True)
    for field, val in update_dict.items():
        setattr(staff, field, val)

    staff.staff_name = f"{staff.first_name} {staff.last_name}"

    db.commit()
    db.refresh(staff)
    return _format_staff(staff)


@router.delete("/{teacher_id}", summary="Delete Teacher")
def delete_teacher(
    teacher_id: int,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(require_roles([RoleEnum.ADMIN]))
):
    staff = db.query(Staff).filter(Staff.staff_id == teacher_id).first()
    if not staff:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Teacher not found")

    if staff.user_account:
        db.delete(staff.user_account)
    db.delete(staff)
    db.commit()
    return {"message": "Teacher record deleted successfully"}
