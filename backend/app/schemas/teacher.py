from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class TeacherBase(BaseModel):
    employee_id: Optional[str] = None
    first_name: str
    middle_name: Optional[str] = None
    last_name: str
    department: Optional[str] = None
    specialization: Optional[str] = None
    contact_number: Optional[str] = None
    is_adviser: bool = False


class TeacherCreate(TeacherBase):
    user_id: Optional[int] = None


class TeacherUpdate(BaseModel):
    first_name: Optional[str] = None
    middle_name: Optional[str] = None
    last_name: Optional[str] = None
    department: Optional[str] = None
    specialization: Optional[str] = None
    contact_number: Optional[str] = None
    is_adviser: Optional[bool] = None


class TeacherResponse(TeacherBase):
    id: int
    user_id: Optional[int] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
