from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from app.database import get_db
from app.models.user import User
from app.models.student import Student
from app.models.teacher import Teacher
from app.models.section import Section, Subject
from app.models.enrollment import Enrollment
from app.models.grade import Grade
from app.models.attendance import Attendance
from app.models.parent import Parent, ParentStudent
from app.utils.auth import get_current_user, require_role
from app.utils.auth import hash_password

router = APIRouter(prefix="/api/registrar", tags=["Registrar Portal"])


@router.get("/dashboard")
def registrar_dashboard(
    db: Session = Depends(get_db),
    user: User = Depends(require_role("registrar", "admin")),
):
    total_students = db.query(Student).count() or 0
    total_teachers = db.query(Teacher).count() or 0
    total_sections = db.query(Section).count() or 0
    total_enrolled = db.query(Enrollment).filter(Enrollment.status == "enrolled").count() or 0
    total_users = db.query(User).count() or 0
    students_with_accounts = db.query(User).filter(User.role == "student").count() or 0

    school_year = "2025-2026"
    enrolled_this_sy = db.query(Enrollment).filter(
        Enrollment.school_year == school_year,
        Enrollment.status == "enrolled"
    ).count() or 0

    by_grade = {}
    enrollments = db.query(Enrollment).filter(
        Enrollment.school_year == school_year,
        Enrollment.status == "enrolled"
    ).all()
    for e in enrollments:
        section = db.query(Section).filter(Section.id == e.section_id).first()
        if section:
            key = f"Grade {section.grade_level}"
            by_grade[key] = by_grade.get(key, 0) + 1

    return {
        "total_students": total_students,
        "total_teachers": total_teachers,
        "total_sections": total_sections,
        "total_enrolled": total_enrolled,
        "enrolled_this_sy": enrolled_this_sy,
        "total_users": total_users,
        "students_with_accounts": students_with_accounts,
        "by_grade": by_grade,
    }


@router.get("/students")
def list_students(
    search: Optional[str] = None,
    grade_level: Optional[str] = None,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("registrar", "admin")),
):
    query = db.query(Student)
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (Student.first_name.ilike(search_filter)) |
            (Student.last_name.ilike(search_filter)) |
            (Student.lrn.ilike(search_filter))
        )
    students = query.all()
    result = []
    for s in students:
        enrollment = db.query(Enrollment).filter(
            Enrollment.student_id == s.id,
            Enrollment.status == "enrolled"
        ).first()
        section = None
        if enrollment:
            section = db.query(Section).filter(Section.id == enrollment.section_id).first()
        if grade_level and section and str(section.grade_level) != grade_level:
            continue
        has_account = db.query(User).filter(User.role == "student", User.username == s.lrn).first() is not None
        result.append({
            "id": s.id,
            "lrn": s.lrn,
            "first_name": s.first_name,
            "middle_name": s.middle_name,
            "last_name": s.last_name,
            "extension_name": s.extension_name,
            "gender": s.gender,
            "birth_date": s.birth_date.isoformat() if s.birth_date else None,
            "address": s.address,
            "contact_number": s.contact_number,
            "guardian_name": s.guardian_name,
            "guardian_contact": s.guardian_contact,
            "section": section.name if section else "Unassigned",
            "grade_level": section.grade_level if section else "-",
            "has_account": has_account,
        })
    return result


@router.post("/students")
def create_student(
    lrn: str,
    first_name: str,
    last_name: str,
    middle_name: Optional[str] = None,
    extension_name: Optional[str] = None,
    birth_date: Optional[str] = None,
    gender: Optional[str] = None,
    address: Optional[str] = None,
    contact_number: Optional[str] = None,
    guardian_name: Optional[str] = None,
    guardian_contact: Optional[str] = None,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("registrar", "admin")),
):
    existing = db.query(Student).filter(Student.lrn == lrn).first()
    if existing:
        raise HTTPException(status_code=400, detail="LRN already exists")

    new_student = Student(
        lrn=lrn,
        first_name=first_name,
        last_name=last_name,
        middle_name=middle_name,
        extension_name=extension_name,
        birth_date=birth_date,
        gender=gender,
        address=address,
        contact_number=contact_number,
        guardian_name=guardian_name,
        guardian_contact=guardian_contact,
    )
    db.add(new_student)
    db.commit()
    db.refresh(new_student)
    return {"message": "Student created", "student_id": new_student.id}


@router.get("/sections")
def list_sections(
    school_year: Optional[str] = None,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("registrar", "admin")),
):
    query = db.query(Section)
    if school_year:
        query = query.filter(Section.school_year == school_year)
    sections = query.all()
    result = []
    for s in sections:
        adviser = db.query(Teacher).filter(Teacher.id == s.adviser_id).first()
        enrolled = db.query(Enrollment).filter(
            Enrollment.section_id == s.id,
            Enrollment.status == "enrolled"
        ).count() or 0
        result.append({
            "id": s.id,
            "name": s.name,
            "grade_level": s.grade_level,
            "track": s.track,
            "school_year": s.school_year,
            "adviser": f"{adviser.first_name} {adviser.last_name}" if adviser else "Unassigned",
            "enrolled_count": enrolled,
            "max_students": s.max_students,
        })
    return result


@router.get("/sections/{section_id}/students")
def list_section_students(
    section_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("registrar", "admin")),
):
    enrollments = db.query(Enrollment).filter(
        Enrollment.section_id == section_id,
        Enrollment.status == "enrolled"
    ).all()
    result = []
    for e in enrollments:
        student = db.query(Student).filter(Student.id == e.student_id).first()
        if student:
            result.append({
                "id": student.id,
                "lrn": student.lrn,
                "first_name": student.first_name,
                "last_name": student.last_name,
                "gender": student.gender,
                "enrollment_id": e.id,
            })
    return result


@router.post("/enrollment")
def enroll_student(
    student_id: int,
    section_id: int,
    school_year: str = "2025-2026",
    semester: Optional[str] = None,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("registrar", "admin")),
):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    section = db.query(Section).filter(Section.id == section_id).first()
    if not section:
        raise HTTPException(status_code=404, detail="Section not found")

    existing = db.query(Enrollment).filter(
        Enrollment.student_id == student_id,
        Enrollment.school_year == school_year,
        Enrollment.status == "enrolled",
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Student already enrolled for this school year")

    new_enrollment = Enrollment(
        student_id=student_id,
        section_id=section_id,
        school_year=school_year,
        semester=semester,
        status="enrolled",
    )
    db.add(new_enrollment)
    db.commit()
    db.refresh(new_enrollment)
    return {"message": "Student enrolled", "enrollment_id": new_enrollment.id}


@router.put("/enrollment/{enrollment_id}/status")
def update_enrollment_status(
    enrollment_id: int,
    status: str,
    remarks: Optional[str] = None,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("registrar", "admin")),
):
    enrollment = db.query(Enrollment).filter(Enrollment.id == enrollment_id).first()
    if not enrollment:
        raise HTTPException(status_code=404, detail="Enrollment not found")

    enrollment.status = status
    if remarks:
        enrollment.remarks = remarks
    if status == "dropped":
        enrollment.date_transferred = datetime.utcnow()
    elif status == "transferred":
        enrollment.date_transferred = datetime.utcnow()
    elif status == "graduated":
        enrollment.date_graduated = datetime.utcnow()

    db.commit()
    return {"message": f"Enrollment status updated to {status}"}


@router.post("/accounts/create-student")
def create_student_account(
    student_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("registrar", "admin")),
):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    existing = db.query(User).filter(User.username == student.lrn).first()
    if existing:
        raise HTTPException(status_code=400, detail="Account already exists for this LRN")

    new_user = User(
        username=student.lrn,
        password_hash=hash_password(student.lrn),
        role="student",
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    student.user_id = new_user.id
    db.commit()

    return {"message": "Student account created", "username": student.lrn, "password": student.lrn}


@router.post("/accounts/create-parent")
def create_parent_account(
    student_id: int,
    parent_email: str,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("registrar", "admin")),
):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    existing = db.query(User).filter(User.username == parent_email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Account already exists for this email")

    new_user = User(
        username=parent_email,
        password_hash=hash_password(student.lrn),
        role="parent",
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    parent = Parent(
        user_id=new_user.id,
        first_name=student.guardian_name.split()[-1] if student.guardian_name else "Parent",
        last_name=student.guardian_name.split()[-1] if student.guardian_name else "Unknown",
        contact_number=student.guardian_contact,
        email=parent_email,
    )
    db.add(parent)
    db.commit()
    db.refresh(parent)

    link = ParentStudent(
        parent_id=parent.id,
        student_id=student.id,
        relationship="Guardian",
    )
    db.add(link)
    db.commit()

    return {"message": "Parent account created", "username": parent_email, "password": student.lrn}


@router.post("/accounts/create-teacher")
def create_teacher_account(
    teacher_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("admin")),
):
    teacher = db.query(Teacher).filter(Teacher.id == teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")

    if not teacher.employee_id:
        raise HTTPException(status_code=400, detail="Teacher has no employee ID")

    existing = db.query(User).filter(User.username == teacher.employee_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Account already exists for this employee ID")

    new_user = User(
        username=teacher.employee_id,
        password_hash=hash_password(teacher.employee_id),
        role="teacher",
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    teacher.user_id = new_user.id
    db.commit()

    return {"message": "Teacher account created", "username": teacher.employee_id, "password": teacher.employee_id}


@router.get("/reports/students")
def list_students_for_reports(
    grade_level: Optional[str] = None,
    school_year: str = "2025-2026",
    db: Session = Depends(get_db),
    user: User = Depends(require_role("registrar", "admin")),
):
    enrollments = db.query(Enrollment).filter(
        Enrollment.school_year == school_year,
        Enrollment.status == "enrolled"
    ).all()
    result = []
    for e in enrollments:
        student = db.query(Student).filter(Student.id == e.student_id).first()
        section = db.query(Section).filter(Section.id == e.section_id).first()
        if student and section:
            if grade_level and str(section.grade_level) != grade_level:
                continue
            result.append({
                "student_id": student.id,
                "lrn": student.lrn,
                "name": f"{student.last_name}, {student.first_name} {student.middle_name or ''}",
                "section": section.name,
                "grade_level": section.grade_level,
                "section_id": section.id,
            })
    return result


@router.get("/reports/sf9/{student_id}")
def download_sf9(
    student_id: int,
    school_year: str = "2025-2026",
    db: Session = Depends(get_db),
    user: User = Depends(require_role("registrar", "admin")),
):
    from app.services.report_service import generate_sf9
    try:
        filepath = generate_sf9(student_id, school_year, db)
        filename = filepath.split("/")[-1]
        return FileResponse(filepath, media_type="application/pdf", filename=filename)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/reports/sf10/{student_id}")
def download_sf10(
    student_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("registrar", "admin")),
):
    from app.services.report_service import generate_sf10
    try:
        filepath = generate_sf10(student_id, db)
        filename = filepath.split("/")[-1]
        return FileResponse(filepath, media_type="application/pdf", filename=filename)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
