from fastapi import APIRouter, Depends, HTTPException, status, Request
from app.core.auth import get_current_admin_user, get_current_user
from app.core.rate_limit import check_rate_limit
from app.schemas.course import CourseCreate, CourseResponse
from app.services.course_service import CourseService
import logging
from typing import List

router = APIRouter()
logger = logging.getLogger(__name__)
course_service = CourseService()

@router.get("/courses", response_model=List[CourseResponse], tags=["Courses"])
async def get_courses(
    request: Request,
    current_user = Depends(get_current_user)
):
    """
    Get all available courses.
    
    Returns:
        List[CourseResponse]: List of all courses with their modules and lessons
    """
    try:
        # Check rate limit
        await check_rate_limit(request)
        
        # Get all courses
        courses = await course_service.get_all_courses()
        return courses
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while fetching courses: {str(e)}"
        )

@router.post(
    "/courses",
    response_model=CourseResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new course",
    description="Create a new course with modules and lessons. Requires admin privileges.",
    tags=["Courses"]
)
async def create_course(
    request: Request,
    course_data: CourseCreate,
    current_user = Depends(get_current_user)
) -> CourseResponse:
    """
    Create a new course with the following features:
    - Input validation for all required fields
    - Unique ID generation for course, modules, and lessons
    - Timestamp tracking for creation and updates
    - Image URL validation
    - Admin-only access
    - Rate limiting
    """
    try:
        # Check rate limit
        await check_rate_limit(request)
        
        # Check if user is admin
        if not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only administrators can create courses"
            )
        
        # Create course
        return await course_service.create_course(course_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error while creating course: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while creating the course: {str(e)}"
        ) 