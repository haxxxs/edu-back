from pydantic import BaseModel, Field

class CourseModuleBase(BaseModel):
    title: str
    # Use alias to match the requested API field name 'lessonsCount'
    lessons_count: int = Field(..., alias='lessonsCount')

class CourseModuleResponse(CourseModuleBase):
    # If the API needed to return the module ID, we would add it here
    # id: int

    class Config:
        orm_mode = True
        # Allow population by field name (lessons_count) as well as alias (lessonsCount)
        allow_population_by_field_name = True 