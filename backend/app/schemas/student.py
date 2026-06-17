from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime


class StudentBase(BaseModel):
    lrn: str = Field(..., min_length=12, max_length=15)
    first_name: str
    middle_name: Optional[str] = None
    last_name: str
    extension_name: Optional[str] = None
    birth_date: Optional[date] = None
    gender: Optional[str] = None
    address: Optional[str] = None
    contact_number: Optional[str] = None
    guardian_name: Optional[str] = None
    guardian_contact: Optional[str] = None


class StudentCreate(StudentBase):
    user_id: Optional[int] = None


class StudentUpdate(BaseModel):
    first_name: Optional[str] = None
    middle_name: Optional[str] = None
    last_name: Optional[str] = None
    extension_name: Optional[str] = None
    birth_date: Optional[date] = None
    gender: Optional[str] = None
    address: Optional[str] = None
    contact_number: Optional[str] = None
    guardian_name: Optional[str] = None
    guardian_contact: Optional[str] = None
    photo_url: Optional[str] = None


class StudentResponse(StudentBase):
    id: int
    user_id: Optional[int] = None
    photo_url: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class StudentListResponse(BaseModel):
    id: int
    lrn: str
    first_name: str
    middle_name: Optional[str] = None
    last_name: str
    gender: Optional[str] = None

    class Config:
        from_attributes = True
