from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from typing import Optional, List
from pydantic import BaseModel
from app.database import get_db
from app.models.message import Message
from app.models.user import User
from app.models.student import Student
from app.models.teacher import Teacher
from app.models.parent import Parent
from app.schemas.message import MessageCreate, MessageResponse
from app.utils.auth import get_current_user, require_role
from app.routes.notifications import create_notification

router = APIRouter(prefix="/api/messages", tags=["Messages"])

# Role-based messaging rules
MESSAGING_RULES = {
    "super_admin": ["admin", "registrar"],
    "admin": ["teacher"],
    "registrar": ["student", "parent"],
    "principal": ["teacher", "admin", "registrar"],
    "teacher": [],
    "student": [],
    "parent": [],
}


def get_allowed_recipient_roles(sender_role):
    return MESSAGING_RULES.get(sender_role, [])


def serialize_message(msg, current_user_id):
    data = {
        "id": msg.id,
        "sender_id": msg.sender_id,
        "recipient_id": msg.recipient_id,
        "subject": msg.subject,
        "body": msg.body,
        "is_read": msg.is_read,
        "created_at": msg.created_at.isoformat() if msg.created_at else None,
        "sender_username": msg.sender.username if msg.sender else None,
        "recipient_username": msg.recipient.username if msg.recipient else None,
    }
    return data


@router.get("", response_model=list[MessageResponse])
def list_messages(
    folder: str = Query("inbox", regex="^(inbox|sent)$"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if folder == "inbox":
        query = db.query(Message).filter(Message.recipient_id == user.id)
    else:
        query = db.query(Message).filter(Message.sender_id == user.id)

    messages = query.order_by(Message.created_at.desc()).offset(offset).limit(limit).all()
    return [serialize_message(m, user.id) for m in messages]


@router.get("/unread-count")
def unread_count(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    from sqlalchemy import func as sqlfunc
    count = db.query(sqlfunc.count(Message.id)).filter(
        Message.recipient_id == user.id,
        Message.is_read == False,
    ).scalar()
    return {"count": count}


@router.get("/recipients")
def list_recipients(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    allowed_roles = get_allowed_recipient_roles(user.role)
    if not allowed_roles:
        return []

    users = db.query(User).filter(
        User.role.in_(allowed_roles),
        User.is_active == True,
        User.id != user.id,
    ).all()

    result = []
    for u in users:
        display_name = u.username
        if u.role == "teacher":
            teacher = db.query(Teacher).filter(Teacher.user_id == u.id).first()
            if teacher:
                display_name = f"{teacher.first_name} {teacher.last_name}"
        elif u.role == "student":
            student = db.query(Student).filter(Student.user_id == u.id).first()
            if student:
                display_name = f"{student.first_name} {student.last_name}"
        elif u.role == "parent":
            parent = db.query(Parent).filter(Parent.user_id == u.id).first()
            if parent:
                display_name = f"{parent.first_name} {parent.last_name}"

        result.append({
            "id": u.id,
            "username": u.username,
            "role": u.role,
            "display_name": display_name,
        })

    return result


@router.post("", response_model=MessageResponse)
def send_message(
    message: MessageCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    # Verify recipient exists
    recipient = db.query(User).filter(User.id == message.recipient_id).first()
    if not recipient:
        raise HTTPException(status_code=404, detail="Recipient not found")

    # Verify role-based permission
    allowed_roles = get_allowed_recipient_roles(user.role)
    if allowed_roles and recipient.role not in allowed_roles:
        raise HTTPException(
            status_code=403,
            detail=f"You can only message users with roles: {', '.join(allowed_roles)}",
        )

    if recipient.id == user.id:
        raise HTTPException(status_code=400, detail="Cannot send message to yourself")

    new_msg = Message(
        sender_id=user.id,
        recipient_id=message.recipient_id,
        subject=message.subject,
        body=message.body,
    )
    db.add(new_msg)
    db.commit()
    db.refresh(new_msg)

    # Create notification for recipient
    create_notification(
        db=db,
        user_id=recipient.id,
        title=f"New Message: {message.subject}",
        message=f"From {user.username}: {message.body[:100]}{'...' if len(message.body) > 100 else ''}",
        notif_type="message",
        reference_id=new_msg.id,
        reference_type="message",
        link="/pages/{role}/messages.html".replace("{role}", recipient.role if recipient.role != "super_admin" else "superadmin"),
    )

    return serialize_message(new_msg, user.id)


@router.put("/{message_id}/read")
def mark_read(
    message_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    msg = db.query(Message).filter(
        Message.id == message_id,
        Message.recipient_id == user.id,
    ).first()
    if not msg:
        raise HTTPException(status_code=404, detail="Message not found")
    msg.is_read = True
    db.commit()
    return {"message": "Marked as read"}


@router.put("/read-all")
def mark_all_read(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    db.query(Message).filter(
        Message.recipient_id == user.id,
        Message.is_read == False,
    ).update({"is_read": True})
    db.commit()
    return {"message": "All messages marked as read"}


@router.delete("/{message_id}")
def delete_message(
    message_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    msg = db.query(Message).filter(Message.id == message_id).first()
    if not msg:
        raise HTTPException(status_code=404, detail="Message not found")
    if msg.sender_id != user.id and msg.recipient_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this message")
    db.delete(msg)
    db.commit()
    return {"message": "Message deleted"}


class BulkDeleteRequest(BaseModel):
    ids: List[int]


@router.post("/bulk-delete")
def bulk_delete_messages(
    req: BulkDeleteRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    deleted = db.query(Message).filter(
        Message.id.in_(req.ids),
        (Message.sender_id == user.id) | (Message.recipient_id == user.id),
    ).delete(synchronize_session=False)
    db.commit()
    return {"message": f"{deleted} messages deleted"}
