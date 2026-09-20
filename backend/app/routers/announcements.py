from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models import (
    Announcement, Staff, UserAccount, RoleEnum, TargetTypeEnum, Enrollment
)
from backend.app.schemas import (
    AnnouncementOut, AnnouncementCreate, AnnouncementUpdate
)
from backend.app.dependencies import require_roles, get_current_user

router = APIRouter(prefix="/api/announcements", tags=["Announcements Management"])


def _format_announcement(ann: Announcement) -> AnnouncementOut:
    out = AnnouncementOut.model_validate(ann)
    if ann.staff:
        out.author_name = ann.staff.staff_name
    return out


@router.get("", response_model=List[AnnouncementOut], summary="List Announcements")
def list_announcements(
    class_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
):
    query = db.query(Announcement)

    if current_user.role == RoleEnum.STUDENT:
        # Students see ALL, STUDENTS target, or announcements targeted to their enrolled classes
        student_class_ids = []
        if current_user.student_profile:
            enrs = db.query(Enrollment).filter(Enrollment.student_id == current_user.student_profile.student_id).all()
            student_class_ids = [e.class_id for e in enrs]

        query = query.filter(
            (Announcement.target_type == TargetTypeEnum.ALL) |
            (Announcement.target_type == TargetTypeEnum.STUDENTS) |
            ((Announcement.target_type == TargetTypeEnum.CLASS) & (Announcement.class_id.in_(student_class_ids)))
        )
    elif class_id:
        query = query.filter(Announcement.class_id == class_id)

    announcements = query.order_by(Announcement.announcement_id.desc()).all()
    return [_format_announcement(a) for a in announcements]


@router.post("", response_model=AnnouncementOut, status_code=status.HTTP_201_CREATED, summary="Create Announcement")
def create_announcement(
    data: AnnouncementCreate,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(require_roles([RoleEnum.ADMIN, RoleEnum.TEACHER]))
):
    staff_id = None
    if current_user.staff_profile:
        staff_id = current_user.staff_profile.staff_id
    else:
        staff = db.query(Staff).first()
        if not staff:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No staff member exists to assign as author")
        staff_id = staff.staff_id

    ann = Announcement(
        staff_id=staff_id,
        title=data.title,
        content=data.content,
        target_type=data.target_type,
        class_id=data.class_id,
        created_at=datetime.utcnow()
    )
    db.add(ann)
    db.commit()
    db.refresh(ann)
    return _format_announcement(ann)


@router.put("/{ann_id}", response_model=AnnouncementOut, summary="Update Announcement")
def update_announcement(
    ann_id: int,
    data: AnnouncementUpdate,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(require_roles([RoleEnum.ADMIN, RoleEnum.TEACHER]))
):
    ann = db.query(Announcement).filter(Announcement.announcement_id == ann_id).first()
    if not ann:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Announcement not found")

    update_dict = data.model_dump(exclude_unset=True)
    for field, val in update_dict.items():
        setattr(ann, field, val)

    db.commit()
    db.refresh(ann)
    return _format_announcement(ann)


@router.delete("/{ann_id}", summary="Delete Announcement")
def delete_announcement(
    ann_id: int,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(require_roles([RoleEnum.ADMIN, RoleEnum.TEACHER]))
):
    ann = db.query(Announcement).filter(Announcement.announcement_id == ann_id).first()
    if not ann:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Announcement not found")

    db.delete(ann)
    db.commit()
    return {"message": "Announcement deleted successfully"}
