from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.section import Section, Subject, SectionSubject
from app.models.user import User
from app.schemas.section import (
    SectionCreate, SectionUpdate, SectionResponse,
    SubjectCreate, SubjectResponse,
    SectionSubjectCreate, SectionSubjectResponse,
)
from app.utils.auth import get_current_user, require_role

router = APIRouter(prefix="/api", tags=["Sections & Subjects"])


@router.get("/sections", response_model=list[SectionResponse])
@router.get("/sections/", response_model=list[SectionResponse])
def list_sections(
    school_year: str = None,
    grade_level: str = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    query = db.query(Section)
    if school_year:
        query = query.filter(Section.school_year == school_year)
    if grade_level:
        query = query.filter(Section.grade_level == grade_level)
    return query.all()


@router.get("/sections/{section_id}", response_model=SectionResponse)
def get_section(section_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    section = db.query(Section).filter(Section.id == section_id).first()
    if not section:
        raise HTTPException(status_code=404, detail="Section not found")
    return section


@router.post("/sections", response_model=SectionResponse)
def create_section(
    section: SectionCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("admin")),
):
    new_section = Section(**section.model_dump())
    db.add(new_section)
    db.commit()
    db.refresh(new_section)
    return new_section


@router.put("/sections/{section_id}", response_model=SectionResponse)
def update_section(
    section_id: int,
    update: SectionUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("admin")),
):
    section = db.query(Section).filter(Section.id == section_id).first()
    if not section:
        raise HTTPException(status_code=404, detail="Section not found")

    update_data = update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(section, field, value)

    db.commit()
    db.refresh(section)
    return section


@router.get("/subjects", response_model=list[SubjectResponse])
def list_subjects(
    grade_level: str = None,
    track: str = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    query = db.query(Subject)
    if grade_level:
        query = query.filter(Subject.grade_level == grade_level)
    if track:
        query = query.filter(Subject.track == track)
    return query.all()


@router.post("/subjects", response_model=SubjectResponse)
def create_subject(
    subject: SubjectCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("admin")),
):
    new_subject = Subject(**subject.model_dump())
    db.add(new_subject)
    db.commit()
    db.refresh(new_subject)
    return new_subject


@router.post("/section-subjects", response_model=SectionSubjectResponse)
def assign_subject_to_section(
    assignment: SectionSubjectCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("admin")),
):
    new_assignment = SectionSubject(**assignment.model_dump())
    db.add(new_assignment)
    db.commit()
    db.refresh(new_assignment)
    return new_assignment
