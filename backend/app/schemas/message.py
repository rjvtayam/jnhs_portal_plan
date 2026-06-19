from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class MessageCreate(BaseModel):
    recipient_id: int
    subject: str = Field(..., min_length=1, max_length=200)
    body: str = Field(..., min_length=1)


class MessageResponse(BaseModel):
    id: int
    sender_id: Optional[int] = None
    recipient_id: int
    subject: str
    body: str
    is_read: bool
    created_at: Optional[datetime] = None
    sender_username: Optional[str] = None
    recipient_username: Optional[str] = None

    class Config:
        from_attributes = True
