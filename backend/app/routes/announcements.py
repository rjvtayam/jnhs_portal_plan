from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.announcement import Announcement, Event
from app.models.user import User
from app.models.teacher import Teacher
from app.models.student import Student
from app.models.parent import Parent, ParentStudent
from app.schemas.announcement import (
    AnnouncementCreate, AnnouncementUpdate, AnnouncementResponse,
    EventCreate, EventResponse,
)
from app.utils.auth import get_current_user, require_role
from app.routes.notifications import create_notification
from app.routes.activity import log_activity

router = APIRouter(prefix="/api", tags=["Announcements & Events"])


@router.get("/announcements", response_model=list[AnnouncementResponse])
def list_announcements(
    audience: str = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    query = db.query(Announcement).filter(Announcement.is_active == True)
    if audience:
        query = query.filter(
            (Announcement.target_audience == "all") |
            (Announcement.target_audience == audience)
        )
    return query.order_by(Announcement.created_at.desc()).all()


@router.post("/announcements", response_model=AnnouncementResponse)
def create_announcement(
    announcement: AnnouncementCreate,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("admin", "registrar")),
):
    new_announcement = Announcement(
        **announcement.model_dump(),
        posted_by=user.id,
    )
    db.add(new_announcement)
    db.commit()
    db.refresh(new_announcement)

    # Create notifications for target audience
    audience = announcement.target_audience or "all"
    role_filter = []
    if audience == "all":
        role_filter = ["admin", "principal", "teacher", "student", "parent", "registrar"]
    elif audience == "teachers":
        role_filter = ["teacher"]
    elif audience == "students":
        role_filter = ["student"]
    elif audience == "parents":
        role_filter = ["parent"]

    if role_filter:
        target_users = db.query(User).filter(User.role.in_(role_filter), User.is_active == True).all()
        preview = announcement.content[:100] + ("..." if len(announcement.content) > 100 else "")
        for target_user in target_users:
            create_notification(
                db=db,
                user_id=target_user.id,
                title=f"New Announcement: {announcement.title}",
                message=f"{preview}",
                notif_type="announcement",
                reference_id=new_announcement.id,
                reference_type="announcement",
                link="/pages/{role}/announcements.html".replace("{role}", target_user.role if target_user.role != "super_admin" else "superadmin"),
            )

    log_activity(
        db=db, user_id=user.id, username=user.username, user_role=user.role,
        action="create", category="announcement",
        description=f"Posted announcement: {announcement.title} to {audience}",
        target_type="announcement", target_id=new_announcement.id,
        ip_address=request.client.host if request.client else None,
    )

    return new_announcement


@router.put("/announcements/{announcement_id}", response_model=AnnouncementResponse)
def update_announcement(
    announcement_id: int,
    update: AnnouncementUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("admin", "registrar")),
):
    announcement = db.query(Announcement).filter(Announcement.id == announcement_id).first()
    if not announcement:
        raise HTTPException(status_code=404, detail="Announcement not found")

    update_data = update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(announcement, field, value)

    db.commit()
    db.refresh(announcement)
    return announcement


@router.get("/events", response_model=list[EventResponse])
def list_events(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(Event).filter(Event.is_active == True).order_by(Event.event_date).all()


@router.post("/events", response_model=EventResponse)
def create_event(
    event: EventCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("admin")),
):
    new_event = Event(**event.model_dump(), created_by=user.id)
    db.add(new_event)
    db.commit()
    db.refresh(new_event)
    return new_event
