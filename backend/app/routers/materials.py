from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models import (
    StudyMaterial, Course, Class, Staff, UserAccount, RoleEnum, MaterialStatusEnum
)
from backend.app.schemas import (
    StudyMaterialOut, StudyMaterialUpdate
)
from backend.app.dependencies import require_roles, get_current_user
from backend.app.utils.helpers import save_upload_file

router = APIRouter(prefix="/api/materials", tags=["Study Materials Management"])


def _format_material(mat: StudyMaterial) -> StudyMaterialOut:
    out = StudyMaterialOut.model_validate(mat)
    if mat.staff:
        out.teacher_name = mat.staff.staff_name
    if mat.course:
        out.course_name = mat.course.course_name
    return out


@router.get("", response_model=List[StudyMaterialOut], summary="List Study Materials")
def list_materials(
    course_id: Optional[int] = None,
    class_id: Optional[int] = None,
    semester: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
):
    query = db.query(StudyMaterial)

    # Students only see PUBLISHED materials
    if current_user.role == RoleEnum.STUDENT:
        query = query.filter(StudyMaterial.published_status == MaterialStatusEnum.PUBLISHED)
    elif current_user.role == RoleEnum.TEACHER and current_user.staff_profile:
        # Teachers see their own materials (drafts/published/archived) or published from others
        query = query.filter(
            (StudyMaterial.staff_id == current_user.staff_profile.staff_id) |
            (StudyMaterial.published_status == MaterialStatusEnum.PUBLISHED)
        )

    if course_id:
        query = query.filter(StudyMaterial.course_id == course_id)
    if class_id:
        query = query.filter(StudyMaterial.class_id == class_id)
    if semester:
        query = query.filter(StudyMaterial.semester == semester)

    materials = query.order_by(StudyMaterial.material_id.desc()).all()
    return [_format_material(m) for m in materials]


@router.post("", response_model=StudyMaterialOut, status_code=status.HTTP_201_CREATED, summary="Upload Study Material")
def upload_study_material(
    title: str = Form(...),
    course_id: int = Form(...),
    class_id: int = Form(...),
    description: Optional[str] = Form(None),
    academic_year: Optional[str] = Form(None),
    semester: Optional[str] = Form(None),
    published_status: MaterialStatusEnum = Form(MaterialStatusEnum.PUBLISHED),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(require_roles([RoleEnum.TEACHER, RoleEnum.ADMIN]))
):
    staff_id = None
    if current_user.role == RoleEnum.TEACHER:
        if not current_user.staff_profile:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Teacher staff profile not found")
        staff_id = current_user.staff_profile.staff_id
    else:
        staff = db.query(Staff).first()
        if not staff:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No staff member exists to assign as uploader")
        staff_id = staff.staff_id

    course = db.query(Course).filter(Course.course_id == course_id).first()
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")

    cls = db.query(Class).filter(Class.class_id == class_id).first()
    if not cls:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Class section not found")

    safe_name, rel_path = save_upload_file(file, subfolder="study_materials")
    file_type = file.filename.split(".")[-1].upper() if "." in file.filename else "FILE"

    mat = StudyMaterial(
        title=title,
        description=description,
        course_id=course_id,
        class_id=class_id,
        staff_id=staff_id,
        file_path=rel_path,
        file_type=file_type,
        academic_year=academic_year or "2025-2026",
        semester=semester or course.semester,
        upload_date=datetime.utcnow(),
        published_status=published_status
    )
    db.add(mat)
    db.commit()
    db.refresh(mat)
    return _format_material(mat)


@router.put("/{material_id}", response_model=StudyMaterialOut, summary="Update Study Material")
def update_study_material(
    material_id: int,
    data: StudyMaterialUpdate,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(require_roles([RoleEnum.TEACHER, RoleEnum.ADMIN]))
):
    mat = db.query(StudyMaterial).filter(StudyMaterial.material_id == material_id).first()
    if not mat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Study material not found")

    update_dict = data.model_dump(exclude_unset=True)
    for field, val in update_dict.items():
        setattr(mat, field, val)

    db.commit()
    db.refresh(mat)
    return _format_material(mat)


@router.delete("/{material_id}", summary="Delete Study Material")
def delete_study_material(
    material_id: int,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(require_roles([RoleEnum.TEACHER, RoleEnum.ADMIN]))
):
    mat = db.query(StudyMaterial).filter(StudyMaterial.material_id == material_id).first()
    if not mat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Study material not found")

    db.delete(mat)
    db.commit()
    return {"message": "Study material deleted successfully"}
