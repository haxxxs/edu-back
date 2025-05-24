from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional

class CalendarNoteCreate(BaseModel):
    """Schema for creating a new calendar note"""
    title: str = Field(..., min_length=3, max_length=200)
    description: Optional[str] = None
    date: datetime
    color: Optional[str] = None
    is_important: bool = False

class CalendarNoteUpdate(BaseModel):
    """Schema for updating an existing calendar note"""
    title: Optional[str] = Field(None, min_length=3, max_length=200)
    description: Optional[str] = None
    date: Optional[datetime] = None
    color: Optional[str] = None
    is_important: Optional[bool] = None

class CalendarNoteResponse(CalendarNoteCreate):
    """Schema for returning calendar note details"""
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True) 