"""
Database Seeding Script for BLDEA College Management System.
Safely initializes database tables and inserts initial demo users with Argon2 hashed passwords.
"""
import sys
import os
from datetime import date

# Add workspace root directory to python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app.database import engine, Base, SessionLocal
from backend.app.models import (
    UserAccount, Department, Program, Staff, Student, Course, Class, Enrollment,
    RoleEnum, UserStatusEnum, StatusEnum, DegreeTypeEnum, GenderEnum, StudentStatusEnum, StaffTypeEnum
)
from backend.app.utils.security import hash_password


def seed_database():
    print("Initializing database tables...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        print("Checking existing user accounts...")

        # 1. Admin Account
        admin_user = db.query(UserAccount).filter(UserAccount.username == "admin").first()
        if not admin_user:
            admin_user = UserAccount(
                username="admin",
                email="admin@bldea.edu.in",
                password_hash=hash_password("admin123"),
                role=RoleEnum.ADMIN,
                status=UserStatusEnum.ACTIVE
            )
            db.add(admin_user)
            print(" -> Created demo ADMIN account ('admin')")

        # 2. Admission Officer Account & Staff Profile
        adm_user = db.query(UserAccount).filter(UserAccount.username == "admission1").first()
        if not adm_user:
            adm_user = UserAccount(
                username="admission1",
                email="admissions@bldea.edu.in",
                password_hash=hash_password("admission123"),
                role=RoleEnum.ADMISSION_OFFICER,
                status=UserStatusEnum.ACTIVE
            )
            db.add(adm_user)
            db.flush()
            print(" -> Created demo ADMISSION_OFFICER account ('admission1')")

        # 3. Department
        dept = db.query(Department).filter(Department.department_code == "CSE").first()
        if not dept:
            dept = Department(
                department_name="Computer Science & Engineering",
                department_code="CSE",
                building="Aryabhata Block",
                hod_name="Dr. V. S. Kumar",
                hod_email="hod.cse@bldea.edu.in",
                hod_phone="9876543210"
            )
            db.add(dept)
            db.flush()
            print(" -> Created CSE Department")
        else:
            dept = db.query(Department).first()

        # 4. Program
        prog = db.query(Program).filter(Program.program_code == "BTECH-CSE").first()
        if not prog:
            prog = Program(
                program_name="B.Tech in Computer Science and Engineering",
                program_code="BTECH-CSE",
                department_id=dept.department_id,
                degree_type=DegreeTypeEnum.UG,
                duration_years=4,
                capacity=120,
                status=StatusEnum.ACTIVE,
                description="Comprehensive 4-year undergraduate program in computer science and software engineering."
            )
            db.add(prog)
            db.flush()
            print(" -> Created BTECH-CSE Program")
        else:
            prog = db.query(Program).first()

        # 5. Teacher Account & Staff Profile
        teacher_user = db.query(UserAccount).filter(UserAccount.username == "teacher1").first()
        if not teacher_user:
            teacher_user = UserAccount(
                username="teacher1",
                email="teacher1@bldea.edu.in",
                password_hash=hash_password("teacher123"),
                role=RoleEnum.TEACHER,
                status=UserStatusEnum.ACTIVE
            )
            db.add(teacher_user)
            db.flush()
            print(" -> Created demo TEACHER user ('teacher1')")

        teacher_staff = db.query(Staff).filter(Staff.email == "teacher1@bldea.edu.in").first()
        if not teacher_staff:
            teacher_staff = Staff(
                user_id=teacher_user.user_id,
                first_name="Ramesh",
                last_name="Patil",
                staff_name="Ramesh Patil",
                email="teacher1@bldea.edu.in",
                phone="9123456789",
                department_id=dept.department_id,
                designation="Associate Professor",
                qualification="Ph.D in Computer Networks",
                staff_type=StaffTypeEnum.TEACHER,
                joining_date=date(2018, 6, 1),
                experience_years=8
            )
            db.add(teacher_staff)
            db.flush()
            print(" -> Created demo Teacher Staff profile")

        # 6. Student Account & Student Profile
        student_user = db.query(UserAccount).filter(UserAccount.username == "student1").first()
        if not student_user:
            student_user = UserAccount(
                username="student1",
                email="student1@bldea.edu.in",
                password_hash=hash_password("student123"),
                role=RoleEnum.STUDENT,
                status=UserStatusEnum.ACTIVE
            )
            db.add(student_user)
            db.flush()
            print(" -> Created demo STUDENT user ('student1')")

        student_profile = db.query(Student).filter(Student.usn == "2BL23CS001").first()
        if not student_profile:
            student_profile = Student(
                user_id=student_user.user_id,
                usn="2BL23CS001",
                registration_number="REG2023001",
                first_name="Anand",
                last_name="Kulkarni",
                student_name="Anand Kulkarni",
                email="student1@bldea.edu.in",
                phone="9845012345",
                address="BLDEA Campus Hostel, Vijayapura, Karnataka",
                date_of_birth=date(2004, 5, 14),
                gender=GenderEnum.MALE,
                department_id=dept.department_id,
                program_id=prog.program_id,
                admission_date=date(2023, 8, 1),
                enrollment_date=date(2023, 8, 1),
                academic_year="2025-2026",
                semester="5",
                gpa=3.75,
                status=StudentStatusEnum.ACTIVE
            )
            db.add(student_profile)
            db.flush()
            print(" -> Created demo Student profile ('2BL23CS001')")

        # 7. Course & Class
        course = db.query(Course).filter(Course.course_code == "21CS51").first()
        if not course:
            course = Course(
                course_code="21CS51",
                course_name="Database Management Systems",
                credits=4,
                department_id=dept.department_id,
                semester="5"
            )
            db.add(course)
            db.flush()
            print(" -> Created Course '21CS51'")
        else:
            course = db.query(Course).first()

        class_sec = db.query(Class).filter(Class.course_id == course.course_id).first()
        if not class_sec:
            class_sec = Class(
                course_id=course.course_id,
                program_id=prog.program_id,
                staff_id=teacher_staff.staff_id,
                academic_year="2025-2026",
                semester="5",
                schedule="Mon/Wed/Fri 10:00 AM - 11:00 AM",
                room="Room 302, Aryabhata Block",
                capacity=60
            )
            db.add(class_sec)
            db.flush()
            print(" -> Created Class Section for DBMS")

            # Enroll demo student into class
            enr = Enrollment(
                student_id=student_profile.student_id,
                class_id=class_sec.class_id,
                enrollment_date=date(2025, 8, 1)
            )
            db.add(enr)
            print(" -> Enrolled student into DBMS Class")

        db.commit()
        print("\nDatabase seeding completed successfully!")

    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()

