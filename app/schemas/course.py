from pydantic import BaseModel, Field
from typing import List, Optional

from .course_module import CourseModuleResponse # Import the module schema

# Base schema with fields common to both Short and Details views
class CourseBase(BaseModel):
    id: int
    title: str
    description: str
    level: str
    duration: str
    # Use alias to match the requested API field name 'imageUrl'
    image_url: Optional[str] = Field(None, alias='imageUrl')

    class Config:
        orm_mode = True
        # Allow population by field name (image_url) as well as alias (imageUrl)
        allow_population_by_field_name = True

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