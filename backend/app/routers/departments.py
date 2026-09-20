from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models import Department, Program, Student, RoleEnum, UserAccount
from backend.app.schemas import DepartmentOut, DepartmentCreate, DepartmentUpdate
from backend.app.dependencies import require_roles, get_current_user

router = APIRouter(prefix="/api/departments", tags=["Department Management"])


def _format_department(dept: Department, db: Session) -> DepartmentOut:
    out = DepartmentOut.model_validate(dept)
    out.programs_count = db.query(Program).filter(Program.department_id == dept.department_id).count()
    out.students_count = db.query(Student).filter(Student.department_id == dept.department_id).count()
    return out


@router.get("", response_model=List[DepartmentOut], summary="List Departments")
def list_departments(
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
):
    depts = db.query(Department).order_by(Department.department_id.asc()).all()
    return [_format_department(d, db) for d in depts]


@router.post("", response_model=DepartmentOut, status_code=status.HTTP_201_CREATED, summary="Create Department")
def create_department(
    data: DepartmentCreate,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(require_roles([RoleEnum.ADMIN]))
):
    if db.query(Department).filter(Department.department_code == data.department_code).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Department code '{data.department_code}' already exists"
        )

    dept = Department(**data.model_dump())
    db.add(dept)
    db.commit()
    db.refresh(dept)
    return _format_department(dept, db)


@router.put("/{dept_id}", response_model=DepartmentOut, summary="Update Department")
def update_department(
    dept_id: int,
    data: DepartmentUpdate,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(require_roles([RoleEnum.ADMIN]))
):
    dept = db.query(Department).filter(Department.department_id == dept_id).first()
    if not dept:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Department not found")

    update_data = data.model_dump(exclude_unset=True)
    for field, val in update_data.items():
        setattr(dept, field, val)

    db.commit()
    db.refresh(dept)
    return _format_department(dept, db)


@router.delete("/{dept_id}", summary="Delete Department")
def delete_department(
    dept_id: int,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(require_roles([RoleEnum.ADMIN]))
):
    dept = db.query(Department).filter(Department.department_id == dept_id).first()
    if not dept:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Department not found")

    db.delete(dept)
    db.commit()
    return {"message": f"Department '{dept.department_name}' deleted successfully"}
