from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.enrollment import Enrollment
from app.models.student import Student
from app.models.section import Section
from app.models.user import User
from app.models.parent import Parent, ParentStudent
from app.schemas.enrollment import EnrollmentCreate, EnrollmentUpdate, EnrollmentResponse
from app.utils.auth import get_current_user, require_role
from app.routes.notifications import create_notification

router = APIRouter(prefix="/api/enrollment", tags=["Enrollment"])


@router.get("/", response_model=list[EnrollmentResponse])
def list_enrollments(
    school_year: str = None,
    status: str = None,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("admin", "registrar")),
):
    query = db.query(Enrollment)
    if school_year:
        query = query.filter(Enrollment.school_year == school_year)
    if status:
        query = query.filter(Enrollment.status == status)
    return query.all()


@router.post("/", response_model=EnrollmentResponse)
def enroll_student(
    enrollment: EnrollmentCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("admin", "registrar")),
):
    student = db.query(Student).filter(Student.id == enrollment.student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    section = db.query(Section).filter(Section.id == enrollment.section_id).first()
    if not section:
        raise HTTPException(status_code=404, detail="Section not found")

    existing = db.query(Enrollment).filter(
        Enrollment.student_id == enrollment.student_id,
        Enrollment.school_year == enrollment.school_year,
        Enrollment.status == "enrolled",
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Student is already enrolled for this school year")

    new_enrollment = Enrollment(**enrollment.model_dump())
    db.add(new_enrollment)
    db.commit()
    db.refresh(new_enrollment)

    # Notify student
    if student.user_id:
        create_notification(
            db=db,
            user_id=student.user_id,
            title="Enrollment Confirmation",
            message=f"You have been enrolled in {section.name} for SY {enrollment.school_year}.",
            notif_type="enrollment",
            reference_id=new_enrollment.id,
            reference_type="enrollment",
            link="/pages/student/dashboard.html",
        )

    # Notify linked parents
    parent_links = db.query(ParentStudent).filter(ParentStudent.student_id == student.id).all()
    for pl in parent_links:
        parent = db.query(Parent).filter(Parent.id == pl.parent_id).first()
        if parent and parent.user_id:
            create_notification(
                db=db,
                user_id=parent.user_id,
                title=f"Enrollment: {student.first_name} {student.last_name}",
                message=f"{student.first_name} has been enrolled in {section.name} for SY {enrollment.school_year}.",
                notif_type="enrollment",
                reference_id=new_enrollment.id,
                reference_type="enrollment",
                link="/pages/parent/dashboard.html",
            )

    return new_enrollment


@router.put("/{enrollment_id}", response_model=EnrollmentResponse)
def update_enrollment(
    enrollment_id: int,
    update: EnrollmentUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("admin", "registrar")),
):
    enrollment = db.query(Enrollment).filter(Enrollment.id == enrollment_id).first()
    if not enrollment:
        raise HTTPException(status_code=404, detail="Enrollment not found")

    update_data = update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(enrollment, field, value)

    db.commit()
    db.refresh(enrollment)
    return enrollment


@router.get("/summary")
def enrollment_summary(
    school_year: str,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("admin", "registrar")),
):
    enrollments = db.query(Enrollment).filter(
        Enrollment.school_year == school_year,
        Enrollment.status == "enrolled",
    ).all()

    summary = {}
    for e in enrollments:
        section = db.query(Section).filter(Section.id == e.section_id).first()
        if section:
            key = f"Grade {section.grade_level}"
            summary[key] = summary.get(key, 0) + 1

    return {"school_year": school_year, "total": len(enrollments), "by_grade": summary}
