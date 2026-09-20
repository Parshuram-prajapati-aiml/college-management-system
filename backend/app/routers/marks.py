from typing import List, Optional
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models import (
    InternalMarks, Class, Student, Enrollment, RoleEnum, UserAccount
)
from backend.app.schemas import (
    InternalMarksCreate, InternalMarksUpdate, InternalMarksOut
)
from backend.app.dependencies import require_roles, get_current_user
from backend.app.utils.helpers import calculate_grade

router = APIRouter(prefix="/api/marks", tags=["Internal Marks Management"])


def _format_marks(m: InternalMarks) -> InternalMarksOut:
    out = InternalMarksOut.model_validate(m)
    if m.student:
        out.student_name = m.student.student_name
        out.usn = m.student.usn
    if m.class_obj and m.class_obj.course:
        out.course_name = m.class_obj.course.course_name
    return out


@router.post("", response_model=InternalMarksOut, summary="Enter or Update Internal Marks")
def enter_internal_marks(
    data: InternalMarksCreate,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(require_roles([RoleEnum.TEACHER, RoleEnum.ADMIN]))
):
    cls = db.query(Class).filter(Class.class_id == data.class_id).first()
    if not cls:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Class section not found")
    student = db.query(Student).filter(Student.student_id == data.student_id).first()
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")

    total = Decimal(data.internal_marks or 0) + Decimal(data.assignment_marks or 0) + Decimal(data.exam_marks or 0)
    grade = calculate_grade(float(total))

    existing = db.query(InternalMarks).filter(
        InternalMarks.student_id == data.student_id,
        InternalMarks.class_id == data.class_id,
        InternalMarks.assessment_name == data.assessment_name
    ).first()

    if existing:
        existing.internal_marks = data.internal_marks
        existing.assignment_marks = data.assignment_marks
        existing.exam_marks = data.exam_marks
        existing.total_marks = total
        existing.grade = grade
        existing.semester = data.semester
        existing.remarks = data.remarks
        m_obj = existing
    else:
        m_obj = InternalMarks(
            student_id=data.student_id,
            class_id=data.class_id,
            assessment_name=data.assessment_name,
            internal_marks=data.internal_marks,
            assignment_marks=data.assignment_marks,
            exam_marks=data.exam_marks,
            total_marks=total,
            grade=grade,
            semester=data.semester,
            remarks=data.remarks
        )
        db.add(m_obj)

    db.commit()
    db.refresh(m_obj)
    return _format_marks(m_obj)


@router.get("/me", response_model=List[InternalMarksOut], summary="Get Current Student Marks Report")
def get_my_marks(
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(require_roles([RoleEnum.STUDENT]))
):
    if not current_user.student_profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student profile not found")

    student_id = current_user.student_profile.student_id
    marks_list = db.query(InternalMarks).filter(InternalMarks.student_id == student_id).all()
    return [_format_marks(m) for m in marks_list]


@router.get("", response_model=List[InternalMarksOut], summary="Get Internal Marks List")
def list_marks(
    class_id: Optional[int] = None,
    student_id: Optional[int] = None,
    assessment_name: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
):
    query = db.query(InternalMarks)
    if class_id:
        query = query.filter(InternalMarks.class_id == class_id)
    if student_id:
        query = query.filter(InternalMarks.student_id == student_id)
    if assessment_name:
        query = query.filter(InternalMarks.assessment_name == assessment_name)

    marks_list = query.order_by(InternalMarks.mark_id.desc()).all()
    return [_format_marks(m) for m in marks_list]
