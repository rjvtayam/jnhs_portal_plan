from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Section(Base):
    __tablename__ = "sections"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    grade_level = Column(String(10), nullable=False)
    track = Column(String(20))
    school_year = Column(String(10), nullable=False)
    adviser_id = Column(Integer, ForeignKey("teachers.id"))
    max_students = Column(Integer, default=50)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    adviser = relationship("Teacher", back_populates="advised_sections")
    enrollments = relationship("Enrollment", back_populates="section")
    section_subjects = relationship("SectionSubject", back_populates="section")
    grades = relationship("Grade", back_populates="section")
    attendances = relationship("Attendance", back_populates="section")


class Subject(Base):
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    grade_level = Column(String(10), nullable=False)
    track = Column(String(20))
    semester = Column(String(10))
    is_specialized = Column(Integer, default=0)
    description = Column(String)

    section_subjects = relationship("SectionSubject", back_populates="subject")
    grades = relationship("Grade", back_populates="subject")


class SectionSubject(Base):
    __tablename__ = "section_subjects"

    id = Column(Integer, primary_key=True, index=True)
    section_id = Column(Integer, ForeignKey("sections.id"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    teacher_id = Column(Integer, ForeignKey("teachers.id"))
    schedule = Column(String(100))
    room = Column(String(50))

    section = relationship("Section", back_populates="section_subjects")
    subject = relationship("Subject", back_populates="section_subjects")
    teacher = relationship("Teacher", back_populates="section_subjects")
