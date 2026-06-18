from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.student import Student
from app.models.teacher import Teacher
from app.models.section import Section, Subject, SectionSubject
from app.models.enrollment import Enrollment
from app.models.grade import Grade
from app.models.attendance import Attendance
from app.utils.auth import get_current_user, require_role

router = APIRouter(prefix="/api/student", tags=["Student Portal"])


@router.get("/dashboard")
def student_dashboard(
    db: Session = Depends(get_db),
    user: User = Depends(require_role("student")),
):
    student = db.query(Student).filter(Student.user_id == user.id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")

    enrollment = db.query(Enrollment).filter(
        Enrollment.student_id == student.id,
        Enrollment.status == "enrolled"
    ).first()
    section = None
    if enrollment:
        section = db.query(Section).filter(Section.id == enrollment.section_id).first()

    grades = db.query(Grade).filter(
        Grade.student_id == student.id,
        Grade.school_year == "2025-2026"
    ).all()

    total_present = db.query(Attendance).filter(
        Attendance.student_id == student.id,
        Attendance.status == "present"
    ).count() or 0
    total_absent = db.query(Attendance).filter(
        Attendance.student_id == student.id,
        Attendance.status == "absent"
    ).count() or 0
    total_late = db.query(Attendance).filter(
        Attendance.student_id == student.id,
        Attendance.status == "late"
    ).count() or 0

    return {
        "student": {
            "id": student.id,
            "lrn": student.lrn,
            "first_name": student.first_name,
            "middle_name": student.middle_name,
            "last_name": student.last_name,
            "extension_name": student.extension_name,
            "gender": student.gender,
            "birth_date": student.birth_date.strftime("%Y-%m-%d") if student.birth_date else None,
            "contact_number": student.contact_number,
            "address": student.address,
            "guardian_name": student.guardian_name,
            "guardian_contact": student.guardian_contact,
            "school_year": enrollment.school_year if enrollment else None,
            "status": "enrolled" if enrollment else "not enrolled",
        },
        "section": {
            "id": section.id,
            "name": section.name,
            "grade_level": section.grade_level,
            "track": section.track,
        } if section else None,
        "grades": [
            {
                "subject_id": g.subject_id,
                "quarter": g.quarter,
                "transmuted_grade": float(g.transmuted_grade) if g.transmuted_grade else None,
            }
            for g in grades
        ],
        "attendance": {
            "present": total_present,
            "absent": total_absent,
            "late": total_late,
        },
    }


@router.get("/grades")
def student_grades(
    school_year: str = "2025-2026",
    db: Session = Depends(get_db),
    user: User = Depends(require_role("student")),
):
    student = db.query(Student).filter(Student.user_id == user.id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")

    grades = db.query(Grade).filter(
        Grade.student_id == student.id,
        Grade.school_year == school_year
    ).all()

    result = []
    for g in grades:
        subject = db.query(Subject).filter(Subject.id == g.subject_id).first()
        result.append({
            "id": g.id,
            "subject": subject.name if subject else "Unknown",
            "subject_code": subject.code if subject else "",
            "quarter": g.quarter,
            "ww_score": float(g.ww_score) if g.ww_score else None,
            "ww_possible": float(g.ww_possible) if g.ww_possible else None,
            "pt_score": float(g.pt_score) if g.pt_score else None,
            "pt_possible": float(g.pt_possible) if g.pt_possible else None,
            "qa_score": float(g.qa_score) if g.qa_score else None,
            "qa_possible": float(g.qa_possible) if g.qa_possible else None,
            "raw_grade": float(g.raw_grade) if g.raw_grade else None,
            "transmuted_grade": float(g.transmuted_grade) if g.transmuted_grade else None,
        })
    return result


@router.get("/attendance")
def student_attendance(
    db: Session = Depends(get_db),
    user: User = Depends(require_role("student")),
):
    student = db.query(Student).filter(Student.user_id == user.id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")

    attendance = db.query(Attendance).filter(
        Attendance.student_id == student.id
    ).order_by(Attendance.date.desc()).limit(30).all()

    present = db.query(Attendance).filter(
        Attendance.student_id == student.id,
        Attendance.status == "present"
    ).count() or 0
    absent = db.query(Attendance).filter(
        Attendance.student_id == student.id,
        Attendance.status == "absent"
    ).count() or 0
    late = db.query(Attendance).filter(
        Attendance.student_id == student.id,
        Attendance.status == "late"
    ).count() or 0

    return {
        "records": [
            {
                "date": a.date.isoformat(),
                "status": a.status,
                "remarks": a.remarks,
            }
            for a in attendance
        ],
        "summary": {
            "present": present,
            "absent": absent,
            "late": late,
        },
    }


@router.get("/schedule")
def student_schedule(
    db: Session = Depends(get_db),
    user: User = Depends(require_role("student")),
):
    student = db.query(Student).filter(Student.user_id == user.id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")

    enrollment = db.query(Enrollment).filter(
        Enrollment.student_id == student.id,
        Enrollment.status == "enrolled"
    ).first()
    if not enrollment:
        return []

    section_subjects = db.query(SectionSubject).filter(
        SectionSubject.section_id == enrollment.section_id
    ).all()

    result = []
    for ss in section_subjects:
        subject = db.query(Subject).filter(Subject.id == ss.subject_id).first()
        teacher = db.query(Teacher).filter(Teacher.id == ss.teacher_id).first()
        result.append({
            "subject": subject.name if subject else "Unknown",
            "subject_code": subject.code if subject else "",
            "teacher": f"{teacher.first_name} {teacher.last_name}" if teacher else "TBA",
            "schedule": ss.schedule,
            "room": ss.room,
        })
    return result
