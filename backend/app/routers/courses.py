from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models import Course, Department, RoleEnum, UserAccount
from backend.app.schemas import CourseOut, CourseCreate, CourseUpdate
from backend.app.dependencies import require_roles, get_current_user

router = APIRouter(prefix="/api/courses", tags=["Course Management"])


def _format_course(course: Course) -> CourseOut:
    out = CourseOut.model_validate(course)
    out.department_name = course.department.department_name if course.department else None
    return out


@router.get("", response_model=List[CourseOut], summary="List Courses")
def list_courses(
    department_id: Optional[int] = None,
    semester: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
):
    query = db.query(Course)
    if department_id:
        query = query.filter(Course.department_id == department_id)
    if semester:
        query = query.filter(Course.semester == semester)
    courses = query.order_by(Course.course_id.asc()).all()
    return [_format_course(c) for c in courses]


@router.post("", response_model=CourseOut, status_code=status.HTTP_201_CREATED, summary="Create Course")
def create_course(
    data: CourseCreate,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(require_roles([RoleEnum.ADMIN]))
):
    if db.query(Course).filter(Course.course_code == data.course_code).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Course code '{data.course_code}' already exists"
        )

    dept = db.query(Department).filter(Department.department_id == data.department_id).first()
    if not dept:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Department not found")

    course = Course(**data.model_dump())
    db.add(course)
    db.commit()
    db.refresh(course)
    return _format_course(course)


@router.put("/{course_id}", response_model=CourseOut, summary="Update Course")
def update_course(
    course_id: int,
    data: CourseUpdate,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(require_roles([RoleEnum.ADMIN]))
):
    course = db.query(Course).filter(Course.course_id == course_id).first()
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")

    update_data = data.model_dump(exclude_unset=True)
    for field, val in update_data.items():
        setattr(course, field, val)

    db.commit()
    db.refresh(course)
    return _format_course(course)


@router.delete("/{course_id}", summary="Delete Course")
def delete_course(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(require_roles([RoleEnum.ADMIN]))
):
    course = db.query(Course).filter(Course.course_id == course_id).first()
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")

    db.delete(course)
    db.commit()
    return {"message": f"Course '{course.course_name}' deleted successfully"}
