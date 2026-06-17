from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.models.grade import Grade
from app.models.student import Student
from app.models.subject import Subject
from app.models.user import User
from app.schemas.grade import GradeInput, GradeUpdate, GradeResponse
from app.services.grading_service import compute_quarterly_grade
from app.utils.auth import get_current_user, require_role

router = APIRouter(prefix="/api/grades", tags=["Grades"])


@router.get("/student/{student_id}", response_model=list[GradeResponse])
def get_student_grades(
    student_id: int,
    school_year: Optional[str] = None,
    semester: Optional[str] = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    query = db.query(Grade).filter(Grade.student_id == student_id)
    if school_year:
        query = query.filter(Grade.school_year == school_year)
    if semester:
        query = query.filter(Grade.semester == semester)
    return query.all()


@router.get("/section/{section_id}", response_model=list[GradeResponse])
def get_section_grades(
    section_id: int,
    quarter: Optional[str] = None,
    school_year: Optional[str] = None,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("admin", "registrar", "teacher")),
):
    query = db.query(Grade).filter(Grade.section_id == section_id)
    if quarter:
        query = query.filter(Grade.quarter == quarter)
    if school_year:
        query = query.filter(Grade.school_year == school_year)
    return query.all()


@router.post("/", response_model=GradeResponse)
def create_grade(
    grade_input: GradeInput,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("admin", "teacher")),
):
    subject = db.query(Subject).filter(Subject.id == grade_input.subject_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")

    existing = db.query(Grade).filter(
        Grade.student_id == grade_input.student_id,
        Grade.subject_id == grade_input.subject_id,
        Grade.quarter == grade_input.quarter,
        Grade.school_year == grade_input.school_year,
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Grade already exists for this quarter")

    computed = compute_quarterly_grade(
        ww_score=grade_input.ww_score or 0,
        ww_possible=grade_input.ww_possible or 0,
        pt_score=grade_input.pt_score or 0,
        pt_possible=grade_input.pt_possible or 0,
        qa_score=grade_input.qa_score or 0,
        qa_possible=grade_input.qa_possible or 0,
        subject_code=subject.code,
    )

    new_grade = Grade(
        student_id=grade_input.student_id,
        subject_id=grade_input.subject_id,
        section_id=grade_input.section_id,
        school_year=grade_input.school_year,
        semester=grade_input.semester,
        quarter=grade_input.quarter,
        ww_score=grade_input.ww_score,
        ww_possible=grade_input.ww_possible,
        pt_score=grade_input.pt_score,
        pt_possible=grade_input.pt_possible,
        qa_score=grade_input.qa_score,
        qa_possible=grade_input.qa_possible,
        ww_percentage=computed["ww_percentage"],
        pt_percentage=computed["pt_percentage"],
        qa_percentage=computed["qa_percentage"],
        raw_grade=computed["raw_grade"],
        transmuted_grade=computed["transmuted_grade"],
        encoded_by=user.id,
    )
    db.add(new_grade)
    db.commit()
    db.refresh(new_grade)
    return new_grade


@router.put("/{grade_id}", response_model=GradeResponse)
def update_grade(
    grade_id: int,
    update: GradeUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("admin", "teacher")),
):
    grade = db.query(Grade).filter(Grade.id == grade_id).first()
    if not grade:
        raise HTTPException(status_code=404, detail="Grade not found")

    subject = db.query(Subject).filter(Subject.id == grade.subject_id).first()

    update_data = update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(grade, field, value)

    computed = compute_quarterly_grade(
        ww_score=float(grade.ww_score or 0),
        ww_possible=float(grade.ww_possible or 0),
        pt_score=float(grade.pt_score or 0),
        pt_possible=float(grade.pt_possible or 0),
        qa_score=float(grade.qa_score or 0),
        qa_possible=float(grade.qa_possible or 0),
        subject_code=subject.code if subject else "",
    )

    grade.ww_percentage = computed["ww_percentage"]
    grade.pt_percentage = computed["pt_percentage"]
    grade.qa_percentage = computed["qa_percentage"]
    grade.raw_grade = computed["raw_grade"]
    grade.transmuted_grade = computed["transmuted_grade"]

    db.commit()
    db.refresh(grade)
    return grade
