from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.models.student import Student
from app.models.user import User
from app.schemas.student import StudentCreate, StudentUpdate, StudentResponse, StudentListResponse
from app.utils.auth import get_current_user, require_role
from app.routes.activity import log_activity

router = APIRouter(prefix="/api/students", tags=["Students"])


@router.get("/", response_model=list[StudentListResponse])
def list_students(
    search: Optional[str] = None,
    grade_level: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("admin", "registrar")),
):
    query = db.query(Student)
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (Student.first_name.ilike(search_filter)) |
            (Student.last_name.ilike(search_filter)) |
            (Student.lrn.ilike(search_filter))
        )
    return query.offset(skip).limit(limit).all()


@router.get("/{student_id}", response_model=StudentResponse)
def get_student(
    student_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student


@router.post("/", response_model=StudentResponse)
def create_student(
    student: StudentCreate,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("admin", "registrar")),
):
    existing = db.query(Student).filter(Student.lrn == student.lrn).first()
    if existing:
        raise HTTPException(status_code=400, detail="LRN already exists")

    new_student = Student(**student.model_dump())
    db.add(new_student)
    db.commit()
    db.refresh(new_student)

    log_activity(
        db=db, user_id=user.id, username=user.username, user_role=user.role,
        action="create", category="student",
        description=f"Created student: {student.first_name} {student.last_name} (LRN: {student.lrn})",
        target_type="student", target_id=new_student.id,
        ip_address=request.client.host if request.client else None,
    )

    return new_student


@router.put("/{student_id}", response_model=StudentResponse)
def update_student(
    student_id: int,
    update: StudentUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("admin", "registrar")),
):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    update_data = update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(student, field, value)

    db.commit()
    db.refresh(student)
    return student


@router.delete("/{student_id}")
def delete_student(
    student_id: int,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("admin")),
):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    log_activity(
        db=db, user_id=user.id, username=user.username, user_role=user.role,
        action="delete", category="student",
        description=f"Deleted student: {student.first_name} {student.last_name} (LRN: {student.lrn})",
        target_type="student", target_id=student.id,
        ip_address=request.client.host if request.client else None,
    )

    db.delete(student)
    db.commit()
    return {"message": "Student deleted"}
