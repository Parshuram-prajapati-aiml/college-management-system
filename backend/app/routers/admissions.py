from typing import List, Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models import (
    Admission, Application, Program, Student, UserAccount, RoleEnum, AdmissionStatusEnum
)
from backend.app.schemas import AdmissionOut, AdmissionCreate, AdmissionUpdate
from backend.app.dependencies import require_roles, get_current_user
from backend.app.utils.security import hash_password

router = APIRouter(prefix="/api/admissions", tags=["Admissions Management"])


def _format_admission(adm: Admission) -> AdmissionOut:
    out = AdmissionOut.model_validate(adm)
    out.program_name = adm.program.program_name if adm.program else None
    out.student_name = adm.student.student_name if adm.student else None
    return out


@router.get("", response_model=List[AdmissionOut], summary="List Admissions / Applications")
def list_admissions(
    status_filter: Optional[AdmissionStatusEnum] = Query(None, alias="status"),
    search: Optional[str] = None,
    program_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(require_roles([RoleEnum.ADMIN, RoleEnum.ADMISSION_OFFICER]))
):
    query = db.query(Admission)
    if status_filter:
        query = query.filter(Admission.status == status_filter)
    if program_id:
        query = query.filter(Admission.program_id == program_id)
    if search:
        pat = f"%{search}%"
        query = query.filter(
            (Admission.application_number.ilike(pat)) |
            (Admission.usn.ilike(pat))
        )
    admissions = query.order_by(Admission.admission_id.desc()).all()
    return [_format_admission(a) for a in admissions]


@router.post("", response_model=AdmissionOut, status_code=status.HTTP_201_CREATED, summary="Submit New Admission Application")
def create_admission(
    data: AdmissionCreate,
    db: Session = Depends(get_db)
):
    if db.query(Admission).filter(Admission.application_number == data.application_number).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Application number already exists"
        )

    if data.program_id:
        prog = db.query(Program).filter(Program.program_id == data.program_id).first()
        if not prog:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Program not found")

    adm = Admission(**data.model_dump())
    db.add(adm)
    db.commit()
    db.refresh(adm)
    return _format_admission(adm)


@router.get("/{admission_id}", response_model=AdmissionOut, summary="Get Admission Details")
def get_admission(
    admission_id: int,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(require_roles([RoleEnum.ADMIN, RoleEnum.ADMISSION_OFFICER]))
):
    adm = db.query(Admission).filter(Admission.admission_id == admission_id).first()
    if not adm:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Admission not found")
    return _format_admission(adm)


@router.put("/{admission_id}", response_model=AdmissionOut, summary="Update Admission Status & Workflow")
def update_admission(
    admission_id: int,
    data: AdmissionUpdate,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(require_roles([RoleEnum.ADMIN, RoleEnum.ADMISSION_OFFICER]))
):
    adm = db.query(Admission).filter(Admission.admission_id == admission_id).first()
    if not adm:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Admission not found")

    update_data = data.model_dump(exclude_unset=True)
    for field, val in update_data.items():
        setattr(adm, field, val)

    db.commit()
    db.refresh(adm)
    return _format_admission(adm)


@router.delete("/{admission_id}", summary="Delete Admission Record")
def delete_admission(
    admission_id: int,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(require_roles([RoleEnum.ADMIN]))
):
    adm = db.query(Admission).filter(Admission.admission_id == admission_id).first()
    if not adm:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Admission not found")

    db.delete(adm)
    db.commit()
    return {"message": "Admission record deleted successfully"}
