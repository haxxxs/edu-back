from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
from tortoise.expressions import Q

# Import models and schemas
from app.models.course import Course
from app.models.course_module import CourseModule
from app.schemas.course import CourseShort, CourseDetails
from app.schemas.course_module import CourseModuleResponse

# Define the router
router = APIRouter()

@router.get(
    "/", 
    response_model=List[CourseShort],
    summary="Get a list of courses",
    description="Retrieve a list of courses with optional filtering by search term and level."
)
async def list_courses(
    search: Optional[str] = Query(None, description="Search term for course title and description (case-insensitive)"),
    level: Optional[str] = Query(None, description="Filter courses by difficulty level (e.g., Beginner, Intermediate, Advanced)")
):
    """Retrieve a list of courses, optionally filtered by search term and level."""
    query = Course.all()

    if search:
        # Case-insensitive search in title or description
        query = query.filter(Q(title__icontains=search) | Q(description__icontains=search))

    if level:
        # Case-insensitive filter by level
        query = query.filter(level__iexact=level)

    courses = await query.values(
        "id", "title", "description", "level", "duration", "image_url"
    )
    # Manually construct the response to match CourseShort exactly including aliases
    # Pydantic's from_orm might not handle aliases correctly with .values()
    return [
        CourseShort(
            id=c["id"],
            title=c["title"],
            description=c["description"],
            level=c["level"],
            duration=c["duration"],
            imageUrl=c["image_url"] # Use alias directly
        )
        for c in courses
    ]

@router.get(
    "/{course_id}", 
    response_model=CourseDetails,
    summary="Get course details by ID",
    description="Retrieve detailed information about a specific course, including its modules."
)
async def get_course_details(course_id: int):
    """Retrieve details for a specific course by its ID."""
    # Fetch the course and prefetch related modules in one query
    course = await Course.get_or_none(id=course_id).prefetch_related("modules")

    if not course:
        raise HTTPException(status_code=404, detail=f"Course with id {course_id} not found")

    # Convert modules to the response schema
    # We need to map lessons_count to lessonsCount
    modules_response = [
        CourseModuleResponse(
            title=module.title, 
            lessonsCount=module.lessons_count
        ) 
        for module in course.modules # Access prefetched modules
    ]

    # Construct the detailed response using the CourseDetails schema
    # Map ORM fields to schema fields, respecting aliases
    course_details = CourseDetails(
        id=course.id,
        title=course.title,
        description=course.description,
        level=course.level,
        duration=course.duration,
        imageUrl=course.image_url, 
        fullDescription=course.full_description,
        modules=modules_response
    )

    return course_details 