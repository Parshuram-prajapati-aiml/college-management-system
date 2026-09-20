from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models import (
    Document, DocumentReceipt, Student, UserAccount, RoleEnum, DocumentStatusEnum
)
from backend.app.schemas import (
    DocumentOut, DocumentRejectRequest, DocumentReceiptOut
)
from backend.app.dependencies import require_roles, get_current_user
from backend.app.utils.helpers import save_upload_file, generate_receipt_number

router = APIRouter(prefix="/api/documents", tags=["Document Management"])


def _format_document(doc: Document) -> DocumentOut:
    out = DocumentOut.model_validate(doc)
    if doc.student:
        out.student_name = doc.student.student_name
        out.usn = doc.student.usn
    if doc.receipt:
        out.receipt = DocumentReceiptOut.model_validate(doc.receipt)
    return out


@router.get("", response_model=List[DocumentOut], summary="List Student Documents")
def list_documents(
    student_id: Optional[int] = None,
    status_filter: Optional[DocumentStatusEnum] = None,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
):
    query = db.query(Document)

    if current_user.role == RoleEnum.STUDENT:
        if not current_user.student_profile:
            return []
        query = query.filter(Document.student_id == current_user.student_profile.student_id)
    elif student_id:
        query = query.filter(Document.student_id == student_id)

    if status_filter:
        query = query.filter(Document.status == status_filter)

    docs = query.order_by(Document.document_id.desc()).all()
    return [_format_document(d) for d in docs]


@router.post("/upload", response_model=DocumentOut, status_code=status.HTTP_201_CREATED, summary="Upload Student Document")
def upload_document(
    document_type: str = Form(...),
    student_id: Optional[int] = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
):
    target_student_id = student_id
    if current_user.role == RoleEnum.STUDENT:
        if not current_user.student_profile:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student profile not found")
        target_student_id = current_user.student_profile.student_id
    elif not target_student_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="student_id is required")

    student = db.query(Student).filter(Student.student_id == target_student_id).first()
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")

    safe_name, rel_path = save_upload_file(file, subfolder="student_documents")

    doc = Document(
        student_id=target_student_id,
        document_type=document_type,
        file_path=rel_path,
        original_name=file.filename,
        upload_date=datetime.utcnow(),
        uploaded_by=current_user.user_id,
        status=DocumentStatusEnum.PENDING
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return _format_document(doc)


@router.put("/{doc_id}/verify", response_model=DocumentOut, summary="Verify Student Document & Generate Receipt")
def verify_document(
    doc_id: int,
    remarks: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(require_roles([RoleEnum.ADMIN, RoleEnum.ADMISSION_OFFICER]))
):
    doc = db.query(Document).filter(Document.document_id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    doc.status = DocumentStatusEnum.VERIFIED
    doc.rejection_reason = None

    if not doc.receipt:
        rcpt = DocumentReceipt(
            document_id=doc.document_id,
            receipt_number=generate_receipt_number(),
            submission_date=datetime.utcnow(),
            remarks=remarks or "Document verified successfully"
        )
        db.add(rcpt)

    db.commit()
    db.refresh(doc)
    return _format_document(doc)


@router.put("/{doc_id}/reject", response_model=DocumentOut, summary="Reject Student Document")
def reject_document(
    doc_id: int,
    body: DocumentRejectRequest,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(require_roles([RoleEnum.ADMIN, RoleEnum.ADMISSION_OFFICER]))
):
    doc = db.query(Document).filter(Document.document_id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    doc.status = DocumentStatusEnum.REJECTED
    doc.rejection_reason = body.rejection_reason

    db.commit()
    db.refresh(doc)
    return _format_document(doc)
