from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime


class AttendanceInput(BaseModel):
    student_id: int
    section_id: int
    subject_id: Optional[int] = None
    date: date
    status: str
    remarks: Optional[str] = None


class AttendanceUpdate(BaseModel):
    status: Optional[str] = None
    remarks: Optional[str] = None


class AttendanceResponse(BaseModel):
    id: int
    student_id: int
    section_id: int
    subject_id: Optional[int] = None
    date: date
    status: str
    remarks: Optional[str] = None
    recorded_by: Optional[int] = None
    recorded_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class BulkAttendanceInput(BaseModel):
    section_id: int
    subject_id: Optional[int] = None
    date: date
    records: list[dict]
