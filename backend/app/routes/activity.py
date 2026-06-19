from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from datetime import datetime, timedelta
from app.database import get_db
from app.models.user import User
from app.models.activity import ActivityLog
from app.utils.auth import get_current_user, require_role

router = APIRouter(prefix="/api/activity", tags=["Activity Log"])


def log_activity(
    db: Session,
    user_id: int,
    username: str,
    user_role: str,
    action: str,
    category: str,
    description: str,
    target_type: str = None,
    target_id: int = None,
    ip_address: str = None,
    endpoint: str = None,
    method: str = None,
    status_code: int = None,
    details: dict = None,
):
    log = ActivityLog(
        user_id=user_id,
        username=username,
        user_role=user_role,
        action=action,
        category=category,
        description=description,
        target_type=target_type,
        target_id=target_id,
        ip_address=ip_address,
        endpoint=endpoint,
        method=method,
        status_code=status_code,
        details=details,
    )
    db.add(log)
    db.commit()
    return log


@router.get("/")
def get_activity_logs(
    action: Optional[str] = None,
    category: Optional[str] = None,
    user_role: Optional[str] = None,
    user_id: Optional[int] = None,
    days: int = Query(30, le=365),
    limit: int = Query(100, le=500),
    skip: int = 0,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("super_admin")),
):
    since = datetime.utcnow() - timedelta(days=days)
    query = db.query(ActivityLog).filter(ActivityLog.created_at >= since)

    if action:
        query = query.filter(ActivityLog.action == action)
    if category:
        query = query.filter(ActivityLog.category == category)
    if user_role:
        query = query.filter(ActivityLog.user_role == user_role)
    if user_id:
        query = query.filter(ActivityLog.user_id == user_id)

    total = query.count()
    logs = query.order_by(ActivityLog.created_at.desc()).offset(skip).limit(limit).all()

    return {
        "total": total,
        "logs": [
            {
                "id": l.id,
                "user_id": l.user_id,
                "username": l.username,
                "user_role": l.user_role,
                "action": l.action,
                "category": l.category,
                "description": l.description,
                "target_type": l.target_type,
                "target_id": l.target_id,
                "ip_address": l.ip_address,
                "endpoint": l.endpoint,
                "method": l.method,
                "status_code": l.status_code,
                "details": l.details,
                "created_at": l.created_at.isoformat() if l.created_at else None,
            }
            for l in logs
        ],
    }


@router.get("/stats")
def activity_stats(
    days: int = Query(7, le=90),
    db: Session = Depends(get_db),
    user: User = Depends(require_role("super_admin")),
):
    since = datetime.utcnow() - timedelta(days=days)

    total = db.query(func.count(ActivityLog.id)).filter(
        ActivityLog.created_at >= since
    ).scalar() or 0

    by_action = dict(
        db.query(ActivityLog.action, func.count(ActivityLog.id))
        .filter(ActivityLog.created_at >= since)
        .group_by(ActivityLog.action)
        .all()
    )

    by_category = dict(
        db.query(ActivityLog.category, func.count(ActivityLog.id))
        .filter(ActivityLog.created_at >= since)
        .group_by(ActivityLog.category)
        .all()
    )

    by_role = dict(
        db.query(ActivityLog.user_role, func.count(ActivityLog.id))
        .filter(ActivityLog.created_at >= since)
        .group_by(ActivityLog.user_role)
        .all()
    )

    recent_logins = db.query(func.count(ActivityLog.id)).filter(
        ActivityLog.created_at >= since,
        ActivityLog.action == "login",
    ).scalar() or 0

    today = datetime.utcnow().date()
    today_start = datetime.combine(today, datetime.min.time())
    today_count = db.query(func.count(ActivityLog.id)).filter(
        ActivityLog.created_at >= today_start
    ).scalar() or 0

    return {
        "total": total,
        "today": today_count,
        "recent_logins": recent_logins,
        "by_action": by_action,
        "by_category": by_category,
        "by_role": by_role,
    }


@router.delete("/{log_id}")
def delete_activity_log(
    log_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("super_admin")),
):
    log = db.query(ActivityLog).filter(ActivityLog.id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Log not found")
    db.delete(log)
    db.commit()
    return {"message": "Log deleted"}


@router.delete("/")
def clear_activity_logs(
    days: int = Query(30),
    db: Session = Depends(get_db),
    user: User = Depends(require_role("super_admin")),
):
    since = datetime.utcnow() - timedelta(days=days)
    count = db.query(ActivityLog).filter(ActivityLog.created_at <= since).delete()
    db.commit()
    return {"message": f"Deleted {count} logs older than {days} days"}
