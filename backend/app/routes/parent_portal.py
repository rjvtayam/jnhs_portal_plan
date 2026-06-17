from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.student import Student
from app.models.section import Section, Subject, SectionSubject
from app.models.enrollment import Enrollment
from app.models.grade import Grade
from app.models.attendance import Attendance
from app.models.parent import Parent, ParentStudent
from app.utils.auth import get_current_user, require_role

router = APIRouter(prefix="/api/parent", tags=["Parent Portal"])


@router.get("/children")
def list_children(
    db: Session = Depends(get_db),
    user: User = Depends(require_role("parent")),
):
    parent = db.query(Parent).filter(Parent.user_id == user.id).first()
    if not parent:
        raise HTTPException(status_code=404, detail="Parent profile not found")

    links = db.query(ParentStudent).filter(ParentStudent.parent_id == parent.id).all()
    children = []
    for link in links:
        student = db.query(Student).filter(Student.id == link.student_id).first()
        if student:
            enrollment = db.query(Enrollment).filter(
                Enrollment.student_id == student.id,
                Enrollment.status == "enrolled"
            ).first()
            section = None
            if enrollment:
                section = db.query(Section).filter(Section.id == enrollment.section_id).first()
            children.append({
                "id": student.id,
                "lrn": student.lrn,
                "first_name": student.first_name,
                "middle_name": student.middle_name,
                "last_name": student.last_name,
                "section": section.name if section else "Unassigned",
                "grade_level": section.grade_level if section else "-",
                "track": section.track if section else None,
                "relationship": link.rel_type,
            })
    return children


@router.get("/child/{student_id}/dashboard")
def child_dashboard(
    student_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("parent")),
):
    parent = db.query(Parent).filter(Parent.user_id == user.id).first()
    if not parent:
        raise HTTPException(status_code=404, detail="Parent profile not found")

    link = db.query(ParentStudent).filter(
        ParentStudent.parent_id == parent.id,
        ParentStudent.student_id == student_id
    ).first()
    if not link:
        raise HTTPException(status_code=403, detail="Not authorized to view this student")

    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    enrollment = db.query(Enrollment).filter(
        Enrollment.student_id == student_id,
        Enrollment.status == "enrolled"
    ).first()
    section = None
    if enrollment:
        section = db.query(Section).filter(Section.id == enrollment.section_id).first()

    grades = db.query(Grade).filter(
        Grade.student_id == student_id,
        Grade.school_year == "2025-2026"
    ).all()

    total_present = db.query(Attendance).filter(
        Attendance.student_id == student_id,
        Attendance.status == "present"
    ).count() or 0
    total_absent = db.query(Attendance).filter(
        Attendance.student_id == student_id,
        Attendance.status == "absent"
    ).count() or 0
    total_late = db.query(Attendance).filter(
        Attendance.student_id == student_id,
        Attendance.status == "late"
    ).count() or 0

    grade_list = []
    for g in grades:
        subject = db.query(Subject).filter(Subject.id == g.subject_id).first()
        grade_list.append({
            "subject": subject.name if subject else "Unknown",
            "quarter": g.quarter,
            "transmuted_grade": float(g.transmuted_grade) if g.transmuted_grade else None,
        })

    return {
        "student": {
            "id": student.id,
            "lrn": student.lrn,
            "first_name": student.first_name,
            "last_name": student.last_name,
        },
        "section": {
            "name": section.name,
            "grade_level": section.grade_level,
            "track": section.track,
        } if section else None,
        "grades": grade_list,
        "attendance": {
            "present": total_present,
            "absent": total_absent,
            "late": total_late,
        },
    }


@router.get("/child/{student_id}/grades")
def child_grades(
    student_id: int,
    school_year: str = "2025-2026",
    db: Session = Depends(get_db),
    user: User = Depends(require_role("parent")),
):
    parent = db.query(Parent).filter(Parent.user_id == user.id).first()
    if not parent:
        raise HTTPException(status_code=404, detail="Parent profile not found")

    link = db.query(ParentStudent).filter(
        ParentStudent.parent_id == parent.id,
        ParentStudent.student_id == student_id
    ).first()
    if not link:
        raise HTTPException(status_code=403, detail="Not authorized")

    grades = db.query(Grade).filter(
        Grade.student_id == student_id,
        Grade.school_year == school_year
    ).all()

    result = []
    for g in grades:
        subject = db.query(Subject).filter(Subject.id == g.subject_id).first()
        result.append({
            "subject": subject.name if subject else "Unknown",
            "quarter": g.quarter,
            "transmuted_grade": float(g.transmuted_grade) if g.transmuted_grade else None,
        })
    return result
