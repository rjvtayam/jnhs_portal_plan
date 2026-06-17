from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Enrollment(Base):
    __tablename__ = "enrollments"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    section_id = Column(Integer, ForeignKey("sections.id"), nullable=False)
    school_year = Column(String(10), nullable=False)
    semester = Column(String(10))
    status = Column(String(20), default="enrolled")
    date_enrolled = Column(DateTime, server_default=func.now())
    date_graduated = Column(DateTime)
    date_transferred = Column(DateTime)
    remarks = Column(String)

    student = relationship("Student", back_populates="enrollments")
    section = relationship("Section", back_populates="enrollments")
