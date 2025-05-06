from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, HttpUrl, validator, ConfigDict
from app.models.course import Course, CourseModule, Lesson, CourseLevel, LessonType
from uuid import UUID

from .course_module import CourseModuleResponse # Import the module schema

# Base schema with fields common to both Short and Details views
class CourseBase(BaseModel):
    id: UUID
    title: str
    description: str
    level: str
    duration: str
    # Use alias to match the requested API field name 'imageUrl'
    image_url: Optional[str] = Field(None, alias='imageUrl')

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )

# Schema for the list view (GET /api/education/courses)
class CourseShort(CourseBase):
    pass # Inherits all fields from CourseBase

# Schema for the detail view (GET /api/education/courses/{id})
class CourseDetails(CourseBase):
    # Use alias to match the requested API field name 'fullDescription'
    full_description: Optional[str] = Field(None, alias='fullDescription')
    # Use the previously defined schema for modules
    modules: List[CourseModuleResponse] = []

# If we needed a schema for creating/updating courses via API:
# class CourseCreate(BaseModel):
#     title: str
#     description: str
#     level: str
#     duration: str
#     imageUrl: Optional[str]
#     fullDescription: Optional[str] 

class LessonBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    type: LessonType
    content: str = Field(..., min_length=1)

    model_config = ConfigDict(from_attributes=True)

class LessonCreate(LessonBase):
    pass

class LessonResponse(LessonBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ModuleBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    lessons: List[LessonCreate]

    model_config = ConfigDict(from_attributes=True)

class ModuleCreate(ModuleBase):
    pass

class ModuleResponse(ModuleBase):
    id: UUID
    lessons_count: int
    lessons: List[LessonResponse]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class CourseCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1, max_length=500)
    fullDescription: str = Field(..., min_length=1, alias='full_description')
    level: CourseLevel
    duration: str = Field(..., min_length=1, max_length=50)
    imageUrl: Optional[HttpUrl] = Field(None, alias='image_url')
    cover_image: Optional[str] = Field(None, max_length=500)
    is_active: bool = Field(default=True)
    modules: List[ModuleCreate]

    @validator('imageUrl')
    def validate_image_url(cls, v):
        if v is not None:
            if not str(v).startswith(('http://', 'https://')):
                raise ValueError('Image URL must start with http:// or https://')
        return v

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "title": "Introduction to Programming",
                "description": "Learn the basics of programming",
                "fullDescription": "A comprehensive course covering programming fundamentals...",
                "level": "beginner",
                "duration": "8 weeks",
                "imageUrl": "https://example.com/course-image.jpg",
                "cover_image": "https://example.com/cover.jpg",
                "is_active": True,
                "modules": [
                    {
                        "title": "Getting Started",
                        "lessons": [
                            {
                                "title": "What is Programming?",
                                "type": "theory",
                                "content": "Programming is the process of creating..."
                            }
                        ]
                    }
                ]
            }
        }
    )

class CourseResponse(CourseBase):
    id: UUID
    modules: List[ModuleResponse]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True, populate_by_name=True) 