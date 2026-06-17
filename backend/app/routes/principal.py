from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.models.user import User
from app.models.student import Student
from app.models.teacher import Teacher
from app.models.section import Section, Subject, SectionSubject
from app.models.enrollment import Enrollment
from app.models.grade import Grade
from app.models.attendance import Attendance
from app.models.announcement import Announcement, Event
from app.utils.auth import get_current_user, require_role

router = APIRouter(prefix="/api/principal", tags=["Principal Portal"])


@router.get("/dashboard")
def principal_dashboard(
    db: Session = Depends(get_db),
    user: User = Depends(require_role("principal", "admin")),
):
    total_students = db.query(Student).count() or 0
    total_teachers = db.query(Teacher).count() or 0
    total_sections = db.query(Section).count() or 0
    total_subjects = db.query(Subject).count() or 0
    total_enrolled = db.query(Enrollment).filter(Enrollment.status == "enrolled").count() or 0

    jhs_students = 0
    shs_students = 0
    for section in db.query(Section).all():
        if section.grade_level in ["7", "8", "9", "10"]:
            enrolled = db.query(Enrollment).filter(
                Enrollment.section_id == section.id,
                Enrollment.status == "enrolled"
            ).count() or 0
            jhs_students += enrolled
        elif section.grade_level in ["11", "12"]:
            enrolled = db.query(Enrollment).filter(
                Enrollment.section_id == section.id,
                Enrollment.status == "enrolled"
            ).count() or 0
            shs_students += enrolled

    return {
        "total_students": total_students,
        "total_teachers": total_teachers,
        "total_sections": total_sections,
        "total_subjects": total_subjects,
        "total_enrolled": total_enrolled,
        "jhs_students": jhs_students,
        "shs_students": shs_students,
    }


@router.get("/teachers")
def list_all_teachers(
    db: Session = Depends(get_db),
    user: User = Depends(require_role("principal", "admin")),
):
    teachers = db.query(Teacher).all()
    result = []
    for t in teachers:
        sections = db.query(Section).filter(Section.adviser_id == t.id).all()
        subjects_taught = db.query(SectionSubject).filter(SectionSubject.teacher_id == t.id).all()
        result.append({
            "id": t.id,
            "employee_id": t.employee_id,
            "first_name": t.first_name,
            "middle_name": t.middle_name,
            "last_name": t.last_name,
            "department": t.department,
            "specialization": t.specialization,
            "contact_number": t.contact_number,
            "is_adviser": t.is_adviser,
            "advised_sections": [{"id": s.id, "name": s.name, "grade_level": s.grade_level} for s in sections],
            "subjects_count": len(subjects_taught),
        })
    return result


@router.get("/students")
def list_all_students(
    grade_level: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("principal", "admin")),
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
        result.append({
            "id": s.id,
            "lrn": s.lrn,
            "first_name": s.first_name,
            "middle_name": s.middle_name,
            "last_name": s.last_name,
            "gender": s.gender,
            "section": section.name if section else "Unassigned",
            "grade_level": section.grade_level if section else "-",
            "track": section.track if section else None,
        })
    return result


@router.get("/subjects")
def list_all_subjects(
    db: Session = Depends(get_db),
    user: User = Depends(require_role("principal", "admin")),
):
    subjects = db.query(Subject).all()
    return [
        {
            "id": s.id,
            "code": s.code,
            "name": s.name,
            "grade_level": s.grade_level,
            "track": s.track,
            "semester": s.semester,
            "is_specialized": s.is_specialized,
        }
        for s in subjects
    ]


@router.get("/sections")
def list_all_sections(
    school_year: Optional[str] = None,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("principal", "admin")),
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


@router.get("/grades/summary")
def grades_summary(
    school_year: str = "2025-2026",
    db: Session = Depends(get_db),
    user: User = Depends(require_role("principal", "admin")),
):
    grades = db.query(Grade).filter(Grade.school_year == school_year).all()

    if not grades:
        return {"average_grade": 0, "passing_rate": 0, "total_grades": 0, "by_subject": {}}

    total = len(grades)
    avg = sum(float(g.transmuted_grade or 0) for g in grades) / total
    passing = sum(1 for g in grades if (g.transmuted_grade or 0) >= 75)
    passing_rate = (passing / total * 100) if total > 0 else 0

    by_subject = {}
    for g in grades:
        subject = db.query(Subject).filter(Subject.id == g.subject_id).first()
        if subject:
            if subject.code not in by_subject:
                by_subject[subject.code] = {"name": subject.name, "grades": []}
            by_subject[subject.code]["grades"].append(float(g.transmuted_grade or 0))

    subject_stats = {}
    for code, data in by_subject.items():
        grades_list = data["grades"]
        subject_stats[code] = {
            "name": data["name"],
            "average": round(sum(grades_list) / len(grades_list), 2),
            "count": len(grades_list),
            "passing": sum(1 for g in grades_list if g >= 75),
        }

    return {
        "average_grade": round(avg, 2),
        "passing_rate": round(passing_rate, 2),
        "total_grades": total,
        "by_subject": subject_stats,
    }


@router.get("/announcements")
def list_announcements_for_principal(
    db: Session = Depends(get_db),
    user: User = Depends(require_role("principal", "admin")),
):
    announcements = db.query(Announcement).order_by(Announcement.created_at.desc()).limit(20).all()
    return [
        {
            "id": a.id,
            "title": a.title,
            "content": a.content,
            "target_audience": a.target_audience,
            "priority": a.priority,
            "is_active": a.is_active,
            "posted_by": a.posted_by,
            "created_at": a.created_at.isoformat() if a.created_at else None,
        }
        for a in announcements
    ]


@router.post("/announcements")
def create_announcement_as_principal(
    title: str,
    content: str,
    target_audience: str = "all",
    priority: str = "normal",
    db: Session = Depends(get_db),
    user: User = Depends(require_role("principal")),
):
    announcement = Announcement(
        title=title,
        content=content,
        target_audience=target_audience,
        priority=priority,
        posted_by=user.id,
    )
    db.add(announcement)
    db.commit()
    return {"message": "Announcement posted"}
