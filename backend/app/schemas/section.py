from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class SectionBase(BaseModel):
    name: str
    grade_level: str
    track: Optional[str] = None
    school_year: str
    adviser_id: Optional[int] = None
    max_students: int = 50


class SectionCreate(SectionBase):
    pass


class SectionUpdate(BaseModel):
    name: Optional[str] = None
    grade_level: Optional[str] = None
    track: Optional[str] = None
    adviser_id: Optional[int] = None
    max_students: Optional[int] = None


class SectionResponse(SectionBase):
    id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class SubjectBase(BaseModel):
    code: str
    name: str
    grade_level: str
    track: Optional[str] = None
    semester: Optional[str] = None
    is_specialized: bool = False
    description: Optional[str] = None


class SubjectCreate(SubjectBase):
    pass


class SubjectResponse(SubjectBase):
    id: int

    class Config:
        from_attributes = True


class SectionSubjectBase(BaseModel):
    section_id: int
    subject_id: int
    teacher_id: Optional[int] = None
    schedule: Optional[str] = None
    room: Optional[str] = None


class SectionSubjectCreate(SectionSubjectBase):
    pass


class SectionSubjectResponse(SectionSubjectBase):
    id: int

    class Config:
        from_attributes = True
