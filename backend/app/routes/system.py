from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from typing import Optional
from datetime import datetime, timedelta
from app.database import get_db
from app.models.user import User
from app.models.system import SystemLog, SystemMetric, ErrorLog
from app.models.student import Student
from app.models.teacher import Teacher
from app.models.enrollment import Enrollment
from app.models.grade import Grade
from app.models.attendance import Attendance
from app.models.section import Section
from app.utils.auth import get_current_user, require_role

router = APIRouter(prefix="/api/system", tags=["System Monitoring"])


@router.get("/health")
def system_health(
    db: Session = Depends(get_db),
    user: User = Depends(require_role("super_admin")),
):
    total_students = db.query(func.count(Student.id)).scalar() or 0
    total_teachers = db.query(func.count(Teacher.id)).scalar() or 0
    total_sections = db.query(func.count(Section.id)).scalar() or 0
    total_enrolled = db.query(func.count(Enrollment.id)).filter(Enrollment.status == "enrolled").scalar() or 0
    total_grades = db.query(func.count(Grade.id)).scalar() or 0
    total_users = db.query(func.count(User.id)).scalar() or 0
    active_users = db.query(func.count(User.id)).filter(User.is_active == True).scalar() or 0

    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "database": "connected",
        "stats": {
            "total_students": total_students,
            "total_teachers": total_teachers,
            "total_sections": total_sections,
            "total_enrolled": total_enrolled,
            "total_grades": total_grades,
            "total_users": total_users,
            "active_users": active_users,
        },
    }


@router.get("/logs")
def get_system_logs(
    level: Optional[str] = None,
    category: Optional[str] = None,
    limit: int = Query(100, le=500),
    skip: int = 0,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("super_admin")),
):
    query = db.query(SystemLog)
    if level:
        query = query.filter(SystemLog.level == level)
    if category:
        query = query.filter(SystemLog.category == category)
    logs = query.order_by(SystemLog.created_at.desc()).offset(skip).limit(limit).all()
    return [
        {
            "id": l.id,
            "level": l.level,
            "category": l.category,
            "message": l.message,
            "details": l.details,
            "ip_address": l.ip_address,
            "user_id": l.user_id,
            "user_role": l.user_role,
            "endpoint": l.endpoint,
            "method": l.method,
            "status_code": l.status_code,
            "response_time_ms": l.response_time_ms,
            "created_at": l.created_at.isoformat() if l.created_at else None,
        }
        for l in logs
    ]


@router.get("/errors")
def get_error_logs(
    resolved: Optional[bool] = None,
    limit: int = Query(100, le=500),
    db: Session = Depends(get_db),
    user: User = Depends(require_role("super_admin")),
):
    query = db.query(ErrorLog)
    if resolved is not None:
        query = query.filter(ErrorLog.resolved == (1 if resolved else 0))
    errors = query.order_by(ErrorLog.created_at.desc()).limit(limit).all()
    return [
        {
            "id": e.id,
            "error_type": e.error_type,
            "error_message": e.error_message,
            "stack_trace": e.stack_trace,
            "endpoint": e.endpoint,
            "method": e.method,
            "user_id": e.user_id,
            "user_role": e.user_role,
            "ip_address": e.ip_address,
            "resolved": bool(e.resolved),
            "resolved_by": e.resolved_by,
            "resolved_at": e.resolved_at.isoformat() if e.resolved_at else None,
            "created_at": e.created_at.isoformat() if e.created_at else None,
        }
        for e in errors
    ]


@router.put("/errors/{error_id}/resolve")
def resolve_error(
    error_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("super_admin")),
):
    error = db.query(ErrorLog).filter(ErrorLog.id == error_id).first()
    if not error:
        raise HTTPException(status_code=404, detail="Error log not found")

    error.resolved = 1
    error.resolved_by = user.id
    error.resolved_at = datetime.utcnow()
    db.commit()
    return {"message": "Error resolved"}


@router.get("/metrics")
def get_metrics(
    hours: int = Query(24, le=168),
    db: Session = Depends(get_db),
    user: User = Depends(require_role("super_admin")),
):
    since = datetime.utcnow() - timedelta(hours=hours)
    metrics = db.query(SystemMetric).filter(
        SystemMetric.recorded_at >= since
    ).order_by(SystemMetric.recorded_at.desc()).all()
    return [
        {
            "id": m.id,
            "metric_name": m.metric_name,
            "metric_value": m.metric_value,
            "metric_unit": m.metric_unit,
            "recorded_at": m.recorded_at.isoformat() if m.recorded_at else None,
        }
        for m in metrics
    ]


@router.get("/stats/overview")
def system_overview(
    db: Session = Depends(get_db),
    user: User = Depends(require_role("super_admin")),
):
    today = datetime.utcnow().date()
    week_ago = today - timedelta(days=7)

    new_users_week = db.query(func.count(User.id)).filter(User.created_at >= week_ago).scalar() or 0
    new_enrollments_week = db.query(func.count(Enrollment.id)).filter(
        Enrollment.date_enrolled >= week_ago
    ).scalar() or 0
    new_grades_week = db.query(func.count(Grade.id)).filter(
        Grade.encoded_at >= week_ago
    ).scalar() or 0

    unresolved_errors = db.query(func.count(ErrorLog.id)).filter(
        ErrorLog.resolved == 0
    ).scalar() or 0
    total_errors = db.query(func.count(ErrorLog.id)).scalar() or 0

    users_by_role = dict(
        db.query(User.role, func.count(User.id)).group_by(User.role).all()
    )

    return {
        "new_users_week": new_users_week,
        "new_enrollments_week": new_enrollments_week,
        "new_grades_week": new_grades_week,
        "unresolved_errors": unresolved_errors,
        "total_errors": total_errors,
        "users_by_role": users_by_role,
    }


@router.post("/logs")
def create_log(
    level: str,
    category: str,
    message: str,
    details: dict = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    log = SystemLog(
        level=level,
        category=category,
        message=message,
        details=details,
        user_id=user.id,
        user_role=user.role,
    )
    db.add(log)
    db.commit()
    return {"message": "Log created"}
