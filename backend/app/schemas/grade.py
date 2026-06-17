from pydantic import BaseModel, Field
from typing import Optional
from datetime import date


class GradeInput(BaseModel):
    student_id: int
    subject_id: int
    section_id: int
    school_year: str
    semester: Optional[str] = None
    quarter: str = Field(..., pattern="^Q[1-4]$")

    # Written Work
    ww_score: Optional[float] = None
    ww_possible: Optional[float] = None

    # Performance Tasks
    pt_score: Optional[float] = None
    pt_possible: Optional[float] = None

    # Quarterly Assessment
    qa_score: Optional[float] = None
    qa_possible: Optional[float] = None


class GradeUpdate(BaseModel):
    ww_score: Optional[float] = None
    ww_possible: Optional[float] = None
    pt_score: Optional[float] = None
    pt_possible: Optional[float] = None
    qa_score: Optional[float] = None
    qa_possible: Optional[float] = None


class GradeResponse(BaseModel):
    id: int
    student_id: int
    subject_id: int
    section_id: int
    school_year: str
    semester: Optional[str] = None
    quarter: str
    ww_score: Optional[float] = None
    ww_possible: Optional[float] = None
    ww_percentage: Optional[float] = None
    pt_score: Optional[float] = None
    pt_possible: Optional[float] = None
    pt_percentage: Optional[float] = None
    qa_score: Optional[float] = None
    qa_possible: Optional[float] = None
    qa_percentage: Optional[float] = None
    raw_grade: Optional[float] = None
    transmuted_grade: Optional[float] = None
    remarks: Optional[str] = None

    class Config:
        from_attributes = True


class GradeBulkUpload(BaseModel):
    grades: list[GradeInput]
