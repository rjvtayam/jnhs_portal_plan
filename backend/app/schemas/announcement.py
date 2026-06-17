from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class AnnouncementBase(BaseModel):
    title: str
    content: str
    target_audience: str = "all"
    target_grade_levels: Optional[str] = None
    priority: str = "normal"


class AnnouncementCreate(AnnouncementBase):
    pass


class AnnouncementUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    target_audience: Optional[str] = None
    target_grade_levels: Optional[str] = None
    priority: Optional[str] = None
    is_active: Optional[bool] = None


class AnnouncementResponse(AnnouncementBase):
    id: int
    is_active: bool
    posted_by: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class EventBase(BaseModel):
    title: str
    description: Optional[str] = None
    event_date: datetime
    event_time: Optional[datetime] = None
    end_date: Optional[datetime] = None
    location: Optional[str] = None


class EventCreate(EventBase):
    pass


class EventResponse(EventBase):
    id: int
    is_active: bool
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
