from sqlalchemy import Column, Integer, String, Date, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    lrn = Column(String(20), unique=True, nullable=False, index=True)
    first_name = Column(String(50), nullable=False)
    middle_name = Column(String(50))
    last_name = Column(String(50), nullable=False)
    extension_name = Column(String(10))
    birth_date = Column(Date)
    gender = Column(String(10))
    address = Column(String)
    contact_number = Column(String(15))
    guardian_name = Column(String(100))
    guardian_contact = Column(String(15))
    photo_url = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="student")
    enrollments = relationship("Enrollment", back_populates="student")
    grades = relationship("Grade", back_populates="student")
    attendances = relationship("Attendance", back_populates="student")
    parent_links = relationship("ParentStudent", back_populates="student")
