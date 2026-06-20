from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.teacher import Teacher
from app.models.user import User
from app.schemas.teacher import TeacherCreate, TeacherUpdate, TeacherResponse
from app.utils.auth import get_current_user, require_role
from app.routes.activity import log_activity

router = APIRouter(prefix="/api/teachers", tags=["Teachers"])


@router.get("/", response_model=list[TeacherResponse])
def list_teachers(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("admin", "registrar")),
):
    return db.query(Teacher).offset(skip).limit(limit).all()


@router.get("/{teacher_id}", response_model=TeacherResponse)
def get_teacher(
    teacher_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    teacher = db.query(Teacher).filter(Teacher.id == teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    return teacher


@router.post("/", response_model=TeacherResponse)
def create_teacher(
    teacher: TeacherCreate,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("admin")),
):
    new_teacher = Teacher(**teacher.model_dump())
    db.add(new_teacher)
    db.commit()
    db.refresh(new_teacher)

    log_activity(
        db=db, user_id=user.id, username=user.username, user_role=user.role,
        action="create", category="teacher",
        description=f"Created teacher: {teacher.first_name} {teacher.last_name}",
        target_type="teacher", target_id=new_teacher.id,
        ip_address=request.client.host if request.client else None,
    )

    return new_teacher


@router.put("/{teacher_id}", response_model=TeacherResponse)
def update_teacher(
    teacher_id: int,
    update: TeacherUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("admin")),
):
    teacher = db.query(Teacher).filter(Teacher.id == teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")

    update_data = update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(teacher, field, value)

    db.commit()
    db.refresh(teacher)
    return teacher


@router.post("/{teacher_id}/toggle-active")
def toggle_teacher_active(
    teacher_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("admin")),
):
    teacher = db.query(Teacher).filter(Teacher.id == teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    if not teacher.user_id:
        raise HTTPException(status_code=400, detail="Teacher has no linked user account")

    target_user = db.query(User).filter(User.id == teacher.user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="Linked user account not found")

    target_user.is_active = not target_user.is_active
    db.commit()
    return {"is_active": target_user.is_active, "message": f"Account {'activated' if target_user.is_active else 'deactivated'}"}
