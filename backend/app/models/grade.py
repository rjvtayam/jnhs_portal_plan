from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Grade(Base):
    __tablename__ = "grades"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    section_id = Column(Integer, ForeignKey("sections.id"), nullable=False)
    school_year = Column(String(10), nullable=False)
    semester = Column(String(10))
    quarter = Column(String(5), nullable=False)

    # Written Work
    ww_score = Column(Numeric(5, 2))
    ww_possible = Column(Numeric(5, 2))
    ww_percentage = Column(Numeric(5, 2))

    # Performance Tasks
    pt_score = Column(Numeric(5, 2))
    pt_possible = Column(Numeric(5, 2))
    pt_percentage = Column(Numeric(5, 2))

    # Quarterly Assessment
    qa_score = Column(Numeric(5, 2))
    qa_possible = Column(Numeric(5, 2))
    qa_percentage = Column(Numeric(5, 2))

    # Final Computed Grade
    raw_grade = Column(Numeric(5, 2))
    transmuted_grade = Column(Numeric(5, 2))

    remarks = Column(Text)
    encoded_by = Column(Integer, ForeignKey("users.id"))
    encoded_at = Column(DateTime(timezone=True), server_default=func.now())

    student = relationship("Student", back_populates="grades")
    subject = relationship("Subject", back_populates="grades")
    section = relationship("Section", back_populates="grades")
