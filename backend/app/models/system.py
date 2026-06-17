from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.sql import func
from app.database import Base


class SystemLog(Base):
    __tablename__ = "system_logs"

    id = Column(Integer, primary_key=True, index=True)
    level = Column(String(10), nullable=False, index=True)
    category = Column(String(50), nullable=False, index=True)
    message = Column(Text, nullable=False)
    details = Column(JSON)
    ip_address = Column(String(50))
    user_id = Column(Integer)
    user_role = Column(String(20))
    endpoint = Column(String(200))
    method = Column(String(10))
    status_code = Column(Integer)
    response_time_ms = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)


class SystemMetric(Base):
    __tablename__ = "system_metrics"

    id = Column(Integer, primary_key=True, index=True)
    metric_name = Column(String(100), nullable=False, index=True)
    metric_value = Column(Integer, nullable=False)
    metric_unit = Column(String(20))
    recorded_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)


class ErrorLog(Base):
    __tablename__ = "error_logs"

    id = Column(Integer, primary_key=True, index=True)
    error_type = Column(String(100), nullable=False)
    error_message = Column(Text, nullable=False)
    stack_trace = Column(Text)
    endpoint = Column(String(200))
    method = Column(String(10))
    user_id = Column(Integer)
    user_role = Column(String(20))
    ip_address = Column(String(50))
    resolved = Column(Integer, default=0)
    resolved_by = Column(Integer)
    resolved_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
