from pydantic import BaseModel, Field, validator, ConfigDict
from datetime import datetime
from typing import Optional
from enum import Enum

class EventType(str, Enum):
    CONFERENCE = "conference"
    WORKSHOP = "workshop"
    WEBINAR = "webinar"
    MEETUP = "meetup"

class EventCreate(BaseModel):
    """Schema for creating a new event"""
    title: str = Field(..., min_length=3, max_length=200)
    description: Optional[str] = None
    start_date: datetime
    end_date: datetime
    location: Optional[str] = None
    max_participants: Optional[int] = None
    type: EventType = EventType.CONFERENCE
    price: Optional[float] = None
    image_url: Optional[str] = None
    is_online: bool = False

    @validator('end_date')
    def validate_dates(cls, end_date, values):
        if 'start_date' in values and end_date < values['start_date']:
            raise ValueError('End date must be after start date')
        return end_date

class EventResponse(EventCreate):
    """Schema for returning event details"""
    id: int
    current_participants: int = 0

    model_config = ConfigDict(from_attributes=True)
