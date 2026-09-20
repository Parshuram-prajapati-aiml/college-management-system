from typing import List, Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models import (
    Attendance, Class, Student, Enrollment, RoleEnum, UserAccount, AttendanceStatusEnum
)
from backend.app.schemas import (
    AttendanceBatchCreate, AttendanceOut, StudentAttendanceSummary
)
from backend.app.dependencies import require_roles, get_current_user

router = APIRouter(prefix="/api/attendance", tags=["Attendance Management"])


def _format_attendance(att: Attendance) -> AttendanceOut:
    out = AttendanceOut.model_validate(att)
    if att.student:
        out.student_name = att.student.student_name
        out.usn = att.student.usn
    return out


@router.post("/batch", response_model=List[AttendanceOut], summary="Batch Record Attendance for Class")
def batch_record_attendance(
    data: AttendanceBatchCreate,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(require_roles([RoleEnum.TEACHER, RoleEnum.ADMIN]))
):
    cls = db.query(Class).filter(Class.class_id == data.class_id).first()
    if not cls:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Class section not found")

    recorded = []
    for item in data.records:
        existing = db.query(Attendance).filter(
            Attendance.student_id == item.student_id,
            Attendance.class_id == data.class_id,
            Attendance.date_recorded == data.date_recorded
        ).first()

        if existing:
            existing.status = item.status
            recorded.append(existing)
        else:
            att = Attendance(
                student_id=item.student_id,
                class_id=data.class_id,
                date_recorded=data.date_recorded,
                status=item.status
            )
            db.add(att)
            recorded.append(att)

    db.commit()
    for r in recorded:
        db.refresh(r)
    return [_format_attendance(r) for r in recorded]


@router.get("/me", response_model=List[StudentAttendanceSummary], summary="Get Current Student Attendance Percentage")
def get_my_attendance(
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(require_roles([RoleEnum.STUDENT]))
):
    if not current_user.student_profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student profile not found")

    student_id = current_user.student_profile.student_id
    enrollments = db.query(Enrollment).filter(Enrollment.student_id == student_id).all()

    summaries = []
    for enr in enrollments:
        cls = enr.class_obj
        if not cls or not cls.course:
            continue

        records = db.query(Attendance).filter(
            Attendance.student_id == student_id,
            Attendance.class_id == cls.class_id
        ).all()

        total = len(records)
        present = sum(1 for r in records if r.status == AttendanceStatusEnum.PRESENT)
        absent = total - present
        pct = round((present / total * 100.0), 2) if total > 0 else 100.0

        summaries.append(StudentAttendanceSummary(
            course_code=cls.course.course_code,
            course_name=cls.course.course_name,
            total_classes=total,
            present_count=present,
            absent_count=absent,
            percentage=pct
        ))

    return summaries


@router.get("", response_model=List[AttendanceOut], summary="Get Attendance Records")
def list_attendance(
    class_id: Optional[int] = None,
    attendance_date: Optional[date] = None,
    student_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
):
    query = db.query(Attendance)
    if class_id:
        query = query.filter(Attendance.class_id == class_id)
    if attendance_date:
        query = query.filter(Attendance.date_recorded == attendance_date)
    if student_id:
        query = query.filter(Attendance.student_id == student_id)

    records = query.order_by(Attendance.date_recorded.desc()).all()
    return [_format_attendance(r) for r in records]
