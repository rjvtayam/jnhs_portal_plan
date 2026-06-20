import os
import uuid
import shutil
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel
from app.database import get_db
from app.models.user import User
from app.models.student import Student
from app.models.teacher import Teacher
from app.models.parent import Parent
from app.utils.auth import get_current_user, require_role, hash_password, verify_password

router = APIRouter(prefix="/api/profile", tags=["Profile"])

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "backend", "uploads", "profiles")
ALLOWED_TYPES = {"image/jpeg", "image/jpg", "image/png", "image/webp"}
MAX_SIZE = 2 * 1024 * 1024  # 2MB


class ProfileUpdate(BaseModel):
    email: Optional[str] = None
    contact_number: Optional[str] = None
    address: Optional[str] = None
    first_name: Optional[str] = None
    middle_name: Optional[str] = None
    last_name: Optional[str] = None
    department: Optional[str] = None
    specialization: Optional[str] = None
    guardian_name: Optional[str] = None
    guardian_contact: Optional[str] = None


@router.get("/")
def get_profile(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    result = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role,
        "is_active": user.is_active,
        "profile_picture": user.profile_picture,
        "created_at": user.created_at.isoformat() if user.created_at else None,
        "last_login": user.last_login.isoformat() if user.last_login else None,
    }

    if user.role == "student" and user.student:
        s = user.student
        enrollment = None
        if s.enrollments:
            from app.models.enrollment import Enrollment
            from app.models.section import Section
            active = [e for e in s.enrollments if e.status == "enrolled"]
            if active:
                enrollment = active[0]
                section = db.query(Section).filter(Section.id == enrollment.section_id).first()
                result["academic"] = {
                    "lrn": s.lrn,
                    "first_name": s.first_name,
                    "middle_name": s.middle_name,
                    "last_name": s.last_name,
                    "extension_name": s.extension_name,
                    "birth_date": s.birth_date.isoformat() if s.birth_date else None,
                    "gender": s.gender,
                    "contact_number": s.contact_number,
                    "address": s.address,
                    "guardian_name": s.guardian_name,
                    "guardian_contact": s.guardian_contact,
                    "grade_level": section.grade_level if section else None,
                    "section_name": section.name if section else None,
                    "school_year": enrollment.school_year,
                    "track": section.track if section else None,
                }
        if "academic" not in result:
            result["academic"] = {
                "lrn": s.lrn,
                "first_name": s.first_name,
                "middle_name": s.middle_name,
                "last_name": s.last_name,
                "extension_name": s.extension_name,
                "birth_date": s.birth_date.isoformat() if s.birth_date else None,
                "gender": s.gender,
                "contact_number": s.contact_number,
                "address": s.address,
                "guardian_name": s.guardian_name,
                "guardian_contact": s.guardian_contact,
            }

    elif user.role == "teacher" and user.teacher:
        t = user.teacher
        result["academic"] = {
            "employee_id": t.employee_id,
            "first_name": t.first_name,
            "middle_name": t.middle_name,
            "last_name": t.last_name,
            "department": t.department,
            "specialization": t.specialization,
            "contact_number": t.contact_number,
            "is_adviser": t.is_adviser,
        }

    elif user.role == "parent" and user.parent:
        p = user.parent
        from app.models.parent import ParentStudent
        from app.models.student import Student as StudentModel
        links = db.query(ParentStudent).filter(ParentStudent.parent_id == p.id).all()
        linked_students = []
        for link in links:
            st = db.query(StudentModel).filter(StudentModel.id == link.student_id).first()
            if st:
                linked_students.append({
                    "student_id": st.id,
                    "name": f"{st.first_name} {st.last_name}",
                    "lrn": st.lrn,
                    "relationship": link.rel_type,
                })
        result["academic"] = {
            "first_name": p.first_name,
            "last_name": p.last_name,
            "contact_number": p.contact_number,
            "address": p.address,
            "linked_students": linked_students,
        }

    elif user.role in ("admin", "registrar", "principal"):
        result["academic"] = {
            "email": user.email,
        }

    return result


@router.put("/")
def update_profile(
    update: ProfileUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if user.role == "student" and user.student:
        s = user.student
        if update.first_name is not None:
            s.first_name = update.first_name
        if update.middle_name is not None:
            s.middle_name = update.middle_name
        if update.last_name is not None:
            s.last_name = update.last_name
        if update.contact_number is not None:
            s.contact_number = update.contact_number
        if update.address is not None:
            s.address = update.address
        if update.guardian_name is not None:
            s.guardian_name = update.guardian_name
        if update.guardian_contact is not None:
            s.guardian_contact = update.guardian_contact

    elif user.role == "teacher" and user.teacher:
        t = user.teacher
        if update.first_name is not None:
            t.first_name = update.first_name
        if update.middle_name is not None:
            t.middle_name = update.middle_name
        if update.last_name is not None:
            t.last_name = update.last_name
        if update.department is not None:
            t.department = update.department
        if update.specialization is not None:
            t.specialization = update.specialization
        if update.contact_number is not None:
            t.contact_number = update.contact_number

    elif user.role == "parent" and user.parent:
        p = user.parent
        if update.first_name is not None:
            p.first_name = update.first_name
        if update.last_name is not None:
            p.last_name = update.last_name
        if update.contact_number is not None:
            p.contact_number = update.contact_number
        if update.address is not None:
            p.address = update.address

    if update.email is not None:
        user.email = update.email

    db.commit()
    db.refresh(user)
    return {"message": "Profile updated successfully"}


@router.post("/picture")
async def upload_profile_picture(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="Only JPG, PNG, and WebP images are allowed")

    contents = await file.read()
    if len(contents) > MAX_SIZE:
        raise HTTPException(status_code=400, detail="Image must be smaller than 2MB")

    os.makedirs(UPLOAD_DIR, exist_ok=True)

    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else "jpg"
    filename = f"{user.id}_{uuid.uuid4().hex[:8]}.{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)

    with open(filepath, "wb") as f:
        f.write(contents)

    if user.profile_picture:
        old_path = os.path.join(UPLOAD_DIR, user.profile_picture)
        if os.path.exists(old_path):
            os.remove(old_path)

    user.profile_picture = filename
    db.commit()

    return {"profile_picture": f"/uploads/profiles/{filename}"}


@router.delete("/picture")
def delete_profile_picture(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if user.profile_picture:
        filepath = os.path.join(UPLOAD_DIR, user.profile_picture)
        if os.path.exists(filepath):
            os.remove(filepath)
        user.profile_picture = None
        db.commit()
    return {"message": "Profile picture removed"}
