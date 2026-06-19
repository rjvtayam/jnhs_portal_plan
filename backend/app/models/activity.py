from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.sql import func
from app.database import Base


class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    username = Column(String(50))
    user_role = Column(String(20))
    action = Column(String(50), nullable=False, index=True)
    category = Column(String(50), nullable=False, index=True)
    description = Column(Text, nullable=False)
    target_type = Column(String(50))
    target_id = Column(Integer)
    ip_address = Column(String(50))
    endpoint = Column(String(200))
    method = Column(String(10))
    status_code = Column(Integer)
    details = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
