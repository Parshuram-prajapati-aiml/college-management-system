from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models import Class, Course, Program, Staff, RoleEnum, UserAccount
from backend.app.schemas import ClassOut, ClassCreate, ClassUpdate
from backend.app.dependencies import require_roles, get_current_user

router = APIRouter(prefix="/api/classes", tags=["Class Management"])


def _format_class(cls: Class) -> ClassOut:
    out = ClassOut.model_validate(cls)
    out.course_code = cls.course.course_code if cls.course else None
    out.course_name = cls.course.course_name if cls.course else None
    out.program_name = cls.program.program_name if cls.program else None
    if cls.staff:
        out.teacher_name = cls.staff.staff_name
    return out


@router.get("", response_model=List[ClassOut], summary="List Classes")
def list_classes(
    staff_id: Optional[int] = None,
    program_id: Optional[int] = None,
    academic_year: Optional[str] = None,
    semester: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
):
    query = db.query(Class)

    # If logged in user is a TEACHER, scope to their assigned classes
    if current_user.role == RoleEnum.TEACHER and current_user.staff_profile:
        query = query.filter(Class.staff_id == current_user.staff_profile.staff_id)
    elif staff_id:
        query = query.filter(Class.staff_id == staff_id)

    if program_id:
        query = query.filter(Class.program_id == program_id)
    if academic_year:
        query = query.filter(Class.academic_year == academic_year)
    if semester:
        query = query.filter(Class.semester == semester)

    classes_list = query.order_by(Class.class_id.asc()).all()
    return [_format_class(c) for c in classes_list]


@router.post("", response_model=ClassOut, status_code=status.HTTP_201_CREATED, summary="Create Class Section")
def create_class(
    data: ClassCreate,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(require_roles([RoleEnum.ADMIN]))
):
    course = db.query(Course).filter(Course.course_id == data.course_id).first()
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    program = db.query(Program).filter(Program.program_id == data.program_id).first()
    if not program:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Program not found")
    staff = db.query(Staff).filter(Staff.staff_id == data.staff_id).first()
    if not staff:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Staff teacher not found")

    new_class = Class(**data.model_dump())
    db.add(new_class)
    db.commit()
    db.refresh(new_class)
    return _format_class(new_class)


@router.put("/{class_id}", response_model=ClassOut, summary="Update Class Section")
def update_class(
    class_id: int,
    data: ClassUpdate,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(require_roles([RoleEnum.ADMIN]))
):
    cls = db.query(Class).filter(Class.class_id == class_id).first()
    if not cls:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Class not found")

    update_data = data.model_dump(exclude_unset=True)
    for field, val in update_data.items():
        setattr(cls, field, val)

    db.commit()
    db.refresh(cls)
    return _format_class(cls)


@router.delete("/{class_id}", summary="Delete Class Section")
def delete_class(
    class_id: int,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(require_roles([RoleEnum.ADMIN]))
):
    cls = db.query(Class).filter(Class.class_id == class_id).first()
    if not cls:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Class not found")

    db.delete(cls)
    db.commit()
    return {"message": "Class section deleted successfully"}
