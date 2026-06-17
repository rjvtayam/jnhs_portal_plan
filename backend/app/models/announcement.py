from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from app.database import Base


class Announcement(Base):
    __tablename__ = "announcements"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    target_audience = Column(String(50), default="all")
    target_grade_levels = Column(String(100))
    priority = Column(String(10), default="normal")
    is_active = Column(Boolean, default=True)
    posted_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True))


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    event_date = Column(DateTime, nullable=False)
    event_time = Column(DateTime)
    end_date = Column(DateTime)
    location = Column(String(100))
    is_active = Column(Boolean, default=True)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    document_type = Column(String(50))
    school_year = Column(String(10))
    semester = Column(String(10))
    file_path = Column(String(255))
    generated_by = Column(Integer, ForeignKey("users.id"))
    generated_at = Column(DateTime(timezone=True), server_default=func.now())


class SchoolSettings(Base):
    __tablename__ = "school_settings"

    id = Column(Integer, primary_key=True, index=True)
    school_year = Column(String(10), nullable=False)
    semester = Column(String(10))
    current_quarter = Column(String(5))
    is_active = Column(Boolean, default=False)
    grading_weights = Column(Text)
    updated_at = Column(DateTime(timezone=True))
