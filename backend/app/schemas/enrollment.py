from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime


class EnrollmentBase(BaseModel):
    student_id: int
    section_id: int
    school_year: str
    semester: Optional[str] = None
    status: str = "enrolled"
    remarks: Optional[str] = None


class EnrollmentCreate(EnrollmentBase):
    pass


class EnrollmentUpdate(BaseModel):
    section_id: Optional[int] = None
    status: Optional[str] = None
    remarks: Optional[str] = None


class EnrollmentResponse(EnrollmentBase):
    id: int
    date_enrolled: Optional[datetime] = None
    date_graduated: Optional[datetime] = None
    date_transferred: Optional[datetime] = None

    class Config:
        from_attributes = True
