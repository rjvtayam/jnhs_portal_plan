from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date
from pydantic import BaseModel
from app.database import get_db
from app.models.user import User
from app.models.teacher import Teacher
from app.models.student import Student
from app.models.section import Section, Subject, SectionSubject
from app.models.enrollment import Enrollment
from app.models.grade import Grade
from app.models.attendance import Attendance
from app.utils.auth import get_current_user, require_role

router = APIRouter(prefix="/api/teacher", tags=["Teacher Portal"])


class GradeEntry(BaseModel):
    student_id: int
    subject_id: int
    quarter: str
    ww_score: float = 0
    ww_possible: float = 100
    pt_score: float = 0
    pt_possible: float = 100
    qa_score: float = 0
    qa_possible: float = 100
    school_year: str = "2025-2026"


class AttendanceEntry(BaseModel):
    student_id: int
    section_id: int
    subject_id: Optional[int] = None
    date: str
    status: str
    remarks: Optional[str] = None


def get_teacher_profile(user: User, db: Session) -> Teacher:
    teacher = db.query(Teacher).filter(Teacher.user_id == user.id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher profile not found")
    return teacher


@router.get("/dashboard")
def teacher_dashboard(
    db: Session = Depends(get_db),
    user: User = Depends(require_role("teacher")),
):
    teacher = get_teacher_profile(user, db)

    sections = db.query(Section).filter(Section.adviser_id == teacher.id).all()

    section_subjects = db.query(SectionSubject).filter(
        SectionSubject.teacher_id == teacher.id
    ).all()

    subject_ids = list(set([ss.subject_id for ss in section_subjects]))
    section_ids = list(set([ss.section_id for ss in section_subjects]))

    total_students = 0
    for sid in section_ids:
        count = db.query(Enrollment).filter(
            Enrollment.section_id == sid,
            Enrollment.status == "enrolled"
        ).count()
        total_students += count

    return {
        "teacher": {
            "id": teacher.id,
            "name": f"{teacher.first_name} {teacher.last_name}",
            "employee_id": teacher.employee_id,
            "department": teacher.department,
        },
        "advised_sections": len(sections),
        "assigned_subjects": len(subject_ids),
        "total_students": total_students,
        "sections": [
            {
                "id": s.id,
                "name": s.name,
                "grade_level": s.grade_level,
                "track": s.track,
                "student_count": db.query(Enrollment).filter(
                    Enrollment.section_id == s.id,
                    Enrollment.status == "enrolled"
                ).count(),
            }
            for s in sections
        ],
    }


@router.get("/sections")
def my_sections(
    db: Session = Depends(get_db),
    user: User = Depends(require_role("teacher")),
):
    teacher = get_teacher_profile(user, db)

    section_subjects = db.query(SectionSubject).filter(
        SectionSubject.teacher_id == teacher.id
    ).all()

    section_map = {}
    for ss in section_subjects:
        section = db.query(Section).filter(Section.id == ss.section_id).first()
        subject = db.query(Subject).filter(Subject.id == ss.subject_id).first()
        if not section or not subject:
            continue
        if section.id not in section_map:
            section_map[section.id] = {
                "id": section.id,
                "name": section.name,
                "grade_level": section.grade_level,
                "track": section.track,
                "subjects": [],
            }
        section_map[section.id]["subjects"].append({
            "id": subject.id,
            "name": subject.name,
            "code": subject.code,
            "schedule": ss.schedule,
            "room": ss.room,
        })

    return list(section_map.values())


@router.get("/sections/{section_id}/students")
def section_students(
    section_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("teacher")),
):
    teacher = get_teacher_profile(user, db)

    ss = db.query(SectionSubject).filter(
        SectionSubject.section_id == section_id,
        SectionSubject.teacher_id == teacher.id,
    ).first()
    if not ss:
        raise HTTPException(status_code=403, detail="Not assigned to this section")

    enrollments = db.query(Enrollment).filter(
        Enrollment.section_id == section_id,
        Enrollment.status == "enrolled"
    ).all()

    students = []
    for e in enrollments:
        student = db.query(Student).filter(Student.id == e.student_id).first()
        if student:
            students.append({
                "id": student.id,
                "lrn": student.lrn,
                "name": f"{student.last_name}, {student.first_name} {student.middle_name or ''}",
                "first_name": student.first_name,
                "last_name": student.last_name,
                "gender": student.gender,
            })
    return students


@router.get("/sections/{section_id}/subjects")
def section_subjects(
    section_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("teacher")),
):
    teacher = get_teacher_profile(user, db)

    section_subjects = db.query(SectionSubject).filter(
        SectionSubject.section_id == section_id,
        SectionSubject.teacher_id == teacher.id,
    ).all()

    result = []
    for ss in section_subjects:
        subject = db.query(Subject).filter(Subject.id == ss.subject_id).first()
        if subject:
            result.append({
                "id": subject.id,
                "code": subject.code,
                "name": subject.name,
            })
    return result


@router.get("/grades/{section_id}/{subject_id}")
def get_grades(
    section_id: int,
    subject_id: int,
    quarter: str = "Q1",
    school_year: str = "2025-2026",
    db: Session = Depends(get_db),
    user: User = Depends(require_role("teacher")),
):
    teacher = get_teacher_profile(user, db)

    ss = db.query(SectionSubject).filter(
        SectionSubject.section_id == section_id,
        SectionSubject.subject_id == subject_id,
        SectionSubject.teacher_id == teacher.id,
    ).first()
    if not ss:
        raise HTTPException(status_code=403, detail="Not assigned to this subject-section")

    enrollments = db.query(Enrollment).filter(
        Enrollment.section_id == section_id,
        Enrollment.status == "enrolled"
    ).all()

    result = []
    for e in enrollments:
        student = db.query(Student).filter(Student.id == e.student_id).first()
        grade = db.query(Grade).filter(
            Grade.student_id == e.student_id,
            Grade.subject_id == subject_id,
            Grade.section_id == section_id,
            Grade.quarter == quarter,
            Grade.school_year == school_year,
        ).first()

        result.append({
            "student_id": student.id,
            "student_name": f"{student.last_name}, {student.first_name}" if student else "-",
            "lrn": student.lrn if student else "-",
            "grade_id": grade.id if grade else None,
            "ww_score": float(grade.ww_score) if grade and grade.ww_score else None,
            "ww_possible": float(grade.ww_possible) if grade and grade.ww_possible else 100,
            "pt_score": float(grade.pt_score) if grade and grade.pt_score else None,
            "pt_possible": float(grade.pt_possible) if grade and grade.pt_possible else 100,
            "qa_score": float(grade.qa_score) if grade and grade.qa_score else None,
            "qa_possible": float(grade.qa_possible) if grade and grade.qa_possible else 100,
            "raw_grade": float(grade.raw_grade) if grade and grade.raw_grade else None,
            "transmuted_grade": float(grade.transmuted_grade) if grade and grade.transmuted_grade else None,
        })
    return result


@router.post("/grades/save")
def save_grades(
    grades: list[GradeEntry],
    db: Session = Depends(get_db),
    user: User = Depends(require_role("teacher")),
):
    teacher = get_teacher_profile(user, db)

    saved = 0
    for entry in grades:
        ss = db.query(SectionSubject).filter(
            SectionSubject.section_id == entry.student_id,
        ).first()

        section = db.query(Section).filter(Section.id == db.query(Enrollment).filter(
            Enrollment.student_id == entry.student_id, Enrollment.status == "enrolled"
        ).first().section_id).first() if db.query(Enrollment).filter(
            Enrollment.student_id == entry.student_id, Enrollment.status == "enrolled"
        ).first() else None

        if not section:
            continue

        ss = db.query(SectionSubject).filter(
            SectionSubject.section_id == section.id,
            SectionSubject.subject_id == entry.subject_id,
            SectionSubject.teacher_id == teacher.id,
        ).first()
        if not ss:
            continue

        subject = db.query(Subject).filter(Subject.id == entry.subject_id).first()
        subject_code = subject.code if subject else ""

        from app.services.grading_service import compute_percentage, compute_raw_grade, transmute_grade, get_subject_type

        ww_pct = compute_percentage(entry.ww_score, entry.ww_possible)
        pt_pct = compute_percentage(entry.pt_score, entry.pt_possible)
        qa_pct = compute_percentage(entry.qa_score, entry.qa_possible)

        subject_type = get_subject_type(subject_code)
        raw = compute_raw_grade(ww_pct, pt_pct, qa_pct, subject_type)
        transmuted = transmute_grade(raw)

        grade = db.query(Grade).filter(
            Grade.student_id == entry.student_id,
            Grade.subject_id == entry.subject_id,
            Grade.section_id == section.id,
            Grade.quarter == entry.quarter,
            Grade.school_year == entry.school_year,
        ).first()

        if grade:
            grade.ww_score = entry.ww_score
            grade.ww_possible = entry.ww_possible
            grade.ww_percentage = ww_pct
            grade.pt_score = entry.pt_score
            grade.pt_possible = entry.pt_possible
            grade.pt_percentage = pt_pct
            grade.qa_score = entry.qa_score
            grade.qa_possible = entry.qa_possible
            grade.qa_percentage = qa_pct
            grade.raw_grade = raw
            grade.transmuted_grade = transmuted
            grade.encoded_by = user.id
        else:
            new_grade = Grade(
                student_id=entry.student_id,
                subject_id=entry.subject_id,
                section_id=section.id,
                school_year=entry.school_year,
                quarter=entry.quarter,
                ww_score=entry.ww_score,
                ww_possible=entry.ww_possible,
                ww_percentage=ww_pct,
                pt_score=entry.pt_score,
                pt_possible=entry.pt_possible,
                pt_percentage=pt_pct,
                qa_score=entry.qa_score,
                qa_possible=entry.qa_possible,
                qa_percentage=qa_pct,
                raw_grade=raw,
                transmuted_grade=transmuted,
                encoded_by=user.id,
            )
            db.add(new_grade)
        saved += 1

    db.commit()
    return {"message": f"Saved {saved} grade(s)", "saved": saved}


@router.get("/attendance/{section_id}")
def get_attendance(
    section_id: int,
    date_str: Optional[str] = None,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("teacher")),
):
    teacher = get_teacher_profile(user, db)

    ss = db.query(SectionSubject).filter(
        SectionSubject.section_id == section_id,
        SectionSubject.teacher_id == teacher.id,
    ).first()
    if not ss:
        raise HTTPException(status_code=403, detail="Not assigned to this section")

    enrollments = db.query(Enrollment).filter(
        Enrollment.section_id == section_id,
        Enrollment.status == "enrolled"
    ).all()

    result = []
    for e in enrollments:
        student = db.query(Student).filter(Student.id == e.student_id).first()
        if not student:
            continue

        att = None
        if date_str:
            att = db.query(Attendance).filter(
                Attendance.student_id == student.id,
                Attendance.section_id == section_id,
                Attendance.date == date_str,
            ).first()

        result.append({
            "student_id": student.id,
            "student_name": f"{student.last_name}, {student.first_name}" if student else "-",
            "lrn": student.lrn,
            "status": att.status if att else None,
            "remarks": att.remarks if att else None,
            "attendance_id": att.id if att else None,
        })
    return result


@router.post("/attendance/save")
def save_attendance(
    entries: list[AttendanceEntry],
    db: Session = Depends(get_db),
    user: User = Depends(require_role("teacher")),
):
    teacher = get_teacher_profile(user, db)
    saved = 0

    for entry in entries:
        ss = db.query(SectionSubject).filter(
            SectionSubject.section_id == entry.section_id,
            SectionSubject.teacher_id == teacher.id,
        ).first()
        if not ss:
            continue

        att = db.query(Attendance).filter(
            Attendance.student_id == entry.student_id,
            Attendance.section_id == entry.section_id,
            Attendance.date == entry.date,
        ).first()

        if att:
            att.status = entry.status
            att.remarks = entry.remarks
            att.recorded_by = user.id
        else:
            new_att = Attendance(
                student_id=entry.student_id,
                section_id=entry.section_id,
                subject_id=entry.subject_id,
                date=entry.date,
                status=entry.status,
                remarks=entry.remarks,
                recorded_by=user.id,
            )
            db.add(new_att)
        saved += 1

    db.commit()
    return {"message": f"Saved {saved} attendance record(s)", "saved": saved}
