from fastapi import APIRouter, Depends, HTTPException, status, Request
from app.core.auth import get_current_user
from app.core.rate_limit import check_rate_limit
from app.schemas.course_content import (
    CourseContent,
    CompleteLessonRequest,
    CompleteLessonResponse,
    ValidatePracticeRequest,
    ValidatePracticeResponse,
    CourseProgress
)
from app.services.course_content_service import CourseContentService
import logging
from uuid import UUID

router = APIRouter()
logger = logging.getLogger(__name__)
content_service = CourseContentService()

@router.get(
    "/courses/{course_id}/content",
    response_model=CourseContent,
    summary="Get course content",
    description="Get course content with all modules, lessons and content blocks. Requires authentication.",
    tags=["Course Content"]
)
async def get_course_content(
    request: Request,
    course_id: UUID,
    current_user = Depends(get_current_user)
):
    """
    Get course content with progress tracking.
    
    Args:
        course_id: UUID of the course
        
    Returns:
        CourseContent: Course content with all modules and lessons
    """
    try:
        # Check rate limit
        await check_rate_limit(request)
        
        # Get course content
        return await content_service.get_course_content(course_id, current_user.id)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while getting course content: {str(e)}"
        )

@router.post(
    "/courses/{course_id}/lessons/{lesson_id}/complete",
    response_model=CompleteLessonResponse,
    summary="Complete lesson",
    description="Mark a lesson as completed for the current user. Requires authentication.",
    tags=["Course Content"]
)
async def complete_lesson(
    request: Request,
    course_id: UUID,
    lesson_id: UUID,
    complete_request: CompleteLessonRequest,
    current_user = Depends(get_current_user)
):
    """
    Mark a lesson as completed.
    
    Args:
        course_id: UUID of the course
        lesson_id: UUID of the lesson
        complete_request: CompleteLessonRequest with user_id
        
    Returns:
        CompleteLessonResponse: Success status and message
    """
    try:
        # Check rate limit
        await check_rate_limit(request)
        
        # Complete lesson
        return await content_service.complete_lesson(
            course_id,
            lesson_id,
            complete_request
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while completing lesson: {str(e)}"
        )

@router.post(
    "/courses/{course_id}/lessons/{lesson_id}/practice/{practice_id}/validate",
    response_model=ValidatePracticeResponse,
    summary="Validate practice",
    description="Validate a practice answer for the current user. Requires authentication.",
    tags=["Course Content"]
)
async def validate_practice(
    request: Request,
    course_id: UUID,
    lesson_id: UUID,
    practice_id: UUID,
    validate_request: ValidatePracticeRequest,
    current_user = Depends(get_current_user)
):
    """
    Validate a practice answer.
    
    Args:
        course_id: UUID of the course
        lesson_id: UUID of the lesson
        practice_id: UUID of the practice
        validate_request: ValidatePracticeRequest with user_id and answer
        
    Returns:
        ValidatePracticeResponse: Validation result with feedback
    """
    try:
        # Check rate limit
        await check_rate_limit(request)
        
        # Validate practice
        return await content_service.validate_practice(
            course_id,
            lesson_id,
            practice_id,
            validate_request
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while validating practice: {str(e)}"
        )

@router.get(
    "/courses/{course_id}/progress",
    response_model=CourseProgress,
    summary="Get course progress",
    description="Get user's progress in a course. Requires authentication.",
    tags=["Course Content"]
)
async def get_course_progress(
    request: Request,
    course_id: UUID,
    current_user = Depends(get_current_user)
):
    """
    Get user's progress in a course.
    
    Args:
        course_id: UUID of the course
        
    Returns:
        CourseProgress: User's progress in the course
    """
    try:
        # Check rate limit
        await check_rate_limit(request)
        
        # Get progress
        return await content_service.get_course_progress(course_id, current_user.id)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while getting course progress: {str(e)}"
        ) 