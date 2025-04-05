from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional
from app.models.task import TaskStatus

class TaskCreate(BaseModel):
    """Schema for creating a new task"""
    title: str = Field(..., min_length=3, max_length=200)
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.TODO
    due_date: Optional[datetime] = None

class TaskResponse(TaskCreate):
    """Schema for returning task details"""
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
