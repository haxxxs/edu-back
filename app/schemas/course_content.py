from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional, Union
from datetime import datetime
from enum import Enum
from uuid import UUID

class ContentBlockType(str, Enum):
    HEADING = "heading"
    PARAGRAPH = "paragraph"
    CODE = "code"
    VIDEO = "video"
    IMAGE = "image"
    PRACTICE = "practice"

class ContentBlockBase(BaseModel):
    type: ContentBlockType
    level: Optional[int] = None
    text: Optional[str] = None
    language: Optional[str] = None
    code: Optional[str] = None
    video_id: Optional[str] = None
    src: Optional[HttpUrl] = None
    alt: Optional[str] = None
    practice_id: Optional[UUID] = None
    description: Optional[str] = None
    task_type: Optional[str] = None
    validation_regex: Optional[str] = None
    placeholder: Optional[str] = None

class ContentBlockResponse(ContentBlockBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }

class LessonContent(BaseModel):
    id: UUID
    title: str
    content_blocks: List[ContentBlockResponse]

    model_config = {
        "from_attributes": True
    }

class ModuleContent(BaseModel):
    id: UUID
    title: str
    lessons: List[LessonContent]

    model_config = {
        "from_attributes": True
    }

class CourseContent(BaseModel):
    id: UUID
    title: str
    modules: List[ModuleContent]

    model_config = {
        "from_attributes": True
    }

class CompleteLessonRequest(BaseModel):
    user_id: UUID

class CompleteLessonResponse(BaseModel):
    success: bool
    message: str

class ValidatePracticeRequest(BaseModel):
    user_id: UUID
    answer: str

class ValidatePracticeResponse(BaseModel):
    success: bool
    message: str
    is_correct: bool
    feedback: Optional[str] = None

class CourseProgress(BaseModel):
    completed_lessons: List[UUID]
    completed_practices: List[UUID]
    progress: float
    last_accessed_lesson: Optional[UUID] = None

    model_config = {
        "from_attributes": True
    } 