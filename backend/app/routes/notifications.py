from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func as sqlfunc
from typing import Optional, List
from pydantic import BaseModel
from app.database import get_db
from app.models.notification import Notification
from app.models.user import User
from app.schemas.notification import NotificationResponse
from app.utils.auth import get_current_user

router = APIRouter(prefix="/api/notifications", tags=["Notifications"])


def create_notification(
    db: Session,
    user_id: int,
    title: str,
    message: str,
    notif_type: str,
    reference_id: int = None,
    reference_type: str = None,
    link: str = None,
):
    notif = Notification(
        user_id=user_id,
        title=title,
        message=message,
        type=notif_type,
        reference_id=reference_id,
        reference_type=reference_type,
        link=link,
    )
    db.add(notif)
    db.commit()
    return notif


@router.get("", response_model=list[NotificationResponse])
def list_notifications(
    unread: Optional[bool] = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    query = db.query(Notification).filter(Notification.user_id == user.id)
    if unread is not None:
        query = query.filter(Notification.is_read == (not unread))
    return query.order_by(Notification.created_at.desc()).offset(offset).limit(limit).all()


@router.get("/unread-count")
def unread_count(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    count = db.query(sqlfunc.count(Notification.id)).filter(
        Notification.user_id == user.id,
        Notification.is_read == False,
    ).scalar()
    return {"count": count}


@router.put("/{notification_id}/read")
def mark_read(
    notification_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    notif = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == user.id,
    ).first()
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")
    notif.is_read = True
    db.commit()
    return {"message": "Marked as read"}


@router.put("/read-all")
def mark_all_read(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    db.query(Notification).filter(
        Notification.user_id == user.id,
        Notification.is_read == False,
    ).update({"is_read": True})
    db.commit()
    return {"message": "All notifications marked as read"}


class BulkDeleteRequest(BaseModel):
    ids: List[int]


@router.delete("/{notification_id}")
def delete_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    notif = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == user.id,
    ).first()
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")
    db.delete(notif)
    db.commit()
    return {"message": "Notification deleted"}


@router.post("/bulk-delete")
def bulk_delete_notifications(
    req: BulkDeleteRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    deleted = db.query(Notification).filter(
        Notification.id.in_(req.ids),
        Notification.user_id == user.id,
    ).delete(synchronize_session=False)
    db.commit()
    return {"message": f"{deleted} notifications deleted"}
