import os
import uuid
import re
from datetime import datetime
from fastapi import UploadFile, HTTPException, status

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads")
ALLOWED_DOCUMENT_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg", ".doc", ".docx", ".zip"}
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB


def sanitize_filename(filename: str) -> str:
    """Remove unsafe characters and prevent path traversal."""
    filename = os.path.basename(filename)
    filename = re.sub(r'[^a-zA-Z0-9_.-]', '_', filename)
    return filename


def save_upload_file(upload_file: UploadFile, subfolder: str = "general") -> tuple[str, str]:
    """
    Validate and save uploaded file safely.
    Returns tuple of (filename, relative_file_path).
    """
    ext = os.path.splitext(upload_file.filename)[1].lower()
    if ext not in ALLOWED_DOCUMENT_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File extension '{ext}' not allowed. Permitted types: {', '.join(ALLOWED_DOCUMENT_EXTENSIONS)}"
        )

    target_dir = os.path.join(UPLOAD_DIR, subfolder)
    os.makedirs(target_dir, exist_ok=True)

    safe_name = sanitize_filename(upload_file.filename)
    unique_name = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}_{safe_name}"
    file_path = os.path.join(target_dir, unique_name)

    content = upload_file.file.read()
    if len(content) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size exceeds maximum limit of 10 MB"
        )

    with open(file_path, "wb") as f:
        f.write(content)

    rel_path = f"/uploads/{subfolder}/{unique_name}"
    return safe_name, rel_path


def generate_receipt_number() -> str:
    """Generate a unique document receipt number."""
    now_str = datetime.now().strftime("%Y%m%d")
    unique_suffix = uuid.uuid4().hex[:6].upper()
    return f"REC-{now_str}-{unique_suffix}"


def calculate_grade(total_marks: float) -> str:
    """Calculate letter grade based on total score (out of 100)."""
    if total_marks >= 90:
        return "S"
    elif total_marks >= 80:
        return "A"
    elif total_marks >= 70:
        return "B"
    elif total_marks >= 60:
        return "C"
    elif total_marks >= 50:
        return "D"
    elif total_marks >= 40:
        return "E"
    else:
        return "F"
