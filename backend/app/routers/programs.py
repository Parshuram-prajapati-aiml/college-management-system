from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models import Program, Department, RoleEnum, UserAccount
from backend.app.schemas import ProgramOut, ProgramCreate, ProgramUpdate
from backend.app.dependencies import require_roles, get_current_user

router = APIRouter(prefix="/api/programs", tags=["Program Management"])


def _format_program(prog: Program) -> ProgramOut:
    out = ProgramOut.model_validate(prog)
    out.department_name = prog.department.department_name if prog.department else None
    return out


@router.get("", response_model=List[ProgramOut], summary="List Programs")
def list_programs(
    department_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
):
    query = db.query(Program)
    if department_id:
        query = query.filter(Program.department_id == department_id)
    progs = query.order_by(Program.program_id.asc()).all()
    return [_format_program(p) for p in progs]


@router.post("", response_model=ProgramOut, status_code=status.HTTP_201_CREATED, summary="Create Program")
def create_program(
    data: ProgramCreate,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(require_roles([RoleEnum.ADMIN]))
):
    if db.query(Program).filter(Program.program_code == data.program_code).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Program code '{data.program_code}' already exists"
        )

    dept = db.query(Department).filter(Department.department_id == data.department_id).first()
    if not dept:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Department not found")

    prog = Program(**data.model_dump())
    db.add(prog)
    db.commit()
    db.refresh(prog)
    return _format_program(prog)


@router.put("/{prog_id}", response_model=ProgramOut, summary="Update Program")
def update_program(
    prog_id: int,
    data: ProgramUpdate,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(require_roles([RoleEnum.ADMIN]))
):
    prog = db.query(Program).filter(Program.program_id == prog_id).first()
    if not prog:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Program not found")

    update_data = data.model_dump(exclude_unset=True)
    for field, val in update_data.items():
        setattr(prog, field, val)

    db.commit()
    db.refresh(prog)
    return _format_program(prog)


@router.delete("/{prog_id}", summary="Delete Program")
def delete_program(
    prog_id: int,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(require_roles([RoleEnum.ADMIN]))
):
    prog = db.query(Program).filter(Program.program_id == prog_id).first()
    if not prog:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Program not found")

    db.delete(prog)
    db.commit()
    return {"message": f"Program '{prog.program_name}' deleted successfully"}
