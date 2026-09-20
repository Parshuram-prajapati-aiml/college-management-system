import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.app.routers import (
    auth, admin, students, teachers, departments, programs,
    courses, classes, admissions, attendance, marks, documents,
    materials, announcements
)

app = FastAPI(
    title="BLDEA College Management System API",
    description="Backend REST API for BLDEA College of Engineering Management System",
    version="1.0.0"
)

# Enable CORS for frontend web server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount uploaded files directory
upload_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
os.makedirs(upload_path, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=upload_path), name="uploads")

# Register Routers
app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(students.router)
app.include_router(teachers.router)
app.include_router(departments.router)
app.include_router(programs.router)
app.include_router(courses.router)
app.include_router(classes.router)
app.include_router(admissions.router)
app.include_router(attendance.router)
app.include_router(marks.router)
app.include_router(documents.router)
app.include_router(materials.router)
app.include_router(announcements.router)


@app.get("/", tags=["System"])
def root():
    return {
        "system": "BLDEA College Management System API",
        "status": "online",
        "docs_url": "/docs",
        "redoc_url": "/redoc"
    }
