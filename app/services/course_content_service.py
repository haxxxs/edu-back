from typing import List, Optional
from fastapi import HTTPException, status
from app.models.course import Course, CourseModule, Lesson
from app.models.course_content import ContentBlock, UserProgress, UserPracticeAttempt
from app.models.user import User
from app.schemas.course_content import (
    CourseContent,
    CompleteLessonRequest,
    CompleteLessonResponse,
    ValidatePracticeRequest,
    ValidatePracticeResponse,
    CourseProgress
)
import logging
import traceback
import re
from uuid import UUID

logger = logging.getLogger(__name__)

class CourseContentService:
    async def get_course_content(self, course_id: UUID, user_id: UUID) -> CourseContent:
        """
        Get course content with progress tracking.
        
        Args:
            course_id: UUID of the course
            user_id: UUID of the user
            
        Returns:
            CourseContent: Course content with all modules and lessons
            
        Raises:
            HTTPException: If course not found or user not enrolled
        """
        try:
            # Check if user is enrolled in the course
            user = await User.get_or_none(id=user_id)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            
            # Get course with all relationships
            course = await Course.get_or_none(id=course_id).prefetch_related(
                'modules',
                'modules__lessons',
                'modules__lessons__content_blocks'
            )
            
            if not course:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Course not found"
                )
            
            # Get user progress
            progress = await UserProgress.get_or_none(user=user, course=course)
            
            # Convert to response model
            return CourseContent(
                id=course.id,
                title=course.title,
                modules=[
                    {
                        "id": module.id,
                        "title": module.title,
                        "lessons": [
                            {
                                "id": lesson.id,
                                "title": lesson.title,
                                "content": lesson.content,
                                "content_blocks": [
                                    {
                                        "id": block.id,
                                        "type": block.type,
                                        "level": block.level,
                                        "text": block.text,
                                        "language": block.language,
                                        "code": block.code,
                                        "video_id": block.video_id,
                                        "src": block.src,
                                        "alt": block.alt,
                                        "practice_id": block.practice_id,
                                        "description": block.description,
                                        "task_type": block.task_type,
                                        "validation_regex": block.validation_regex,
                                        "placeholder": block.placeholder,
                                        "created_at": block.created_at,
                                        "updated_at": block.updated_at
                                    }
                                    for block in lesson.content_blocks
                                ]
                            }
                            for lesson in module.lessons
                        ]
                    }
                    for module in course.modules
                ]
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting course content: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"An error occurred while getting course content: {str(e)}"
            )

    async def complete_lesson(
        self,
        course_id: UUID,
        lesson_id: UUID,
        request: CompleteLessonRequest
    ) -> CompleteLessonResponse:
        """
        Mark a lesson as completed for a user.
        
        Args:
            course_id: UUID of the course
            lesson_id: UUID of the lesson
            request: CompleteLessonRequest with user_id
            
        Returns:
            CompleteLessonResponse: Success status and message
            
        Raises:
            HTTPException: If course, lesson or user not found
        """
        try:
            # Get user
            user = await User.get_or_none(id=request.user_id)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            
            # Get course and lesson
            course = await Course.get_or_none(id=course_id)
            if not course:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Course not found"
                )
            
            lesson = await Lesson.get_or_none(id=lesson_id)
            if not lesson:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Lesson not found"
                )
            
            # Get or create user progress
            progress, created = await UserProgress.get_or_create(
                user=user,
                course=course,
                defaults={
                    "completed_lessons": [],
                    "completed_practices": [],
                    "progress": 0.0
                }
            )
            
            # Add lesson to completed lessons if not already there
            if lesson_id not in progress.completed_lessons:
                progress.completed_lessons.append(lesson_id)
                
                # Calculate new progress
                total_lessons = await Lesson.filter(module__course=course).count()
                progress.progress = (len(progress.completed_lessons) / total_lessons) * 100
                
                await progress.save()
            
            return CompleteLessonResponse(
                success=True,
                message="Lesson marked as completed successfully"
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error completing lesson: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"An error occurred while completing lesson: {str(e)}"
            )

    async def validate_practice(
        self,
        course_id: UUID,
        lesson_id: UUID,
        practice_id: UUID,
        request: ValidatePracticeRequest
    ) -> ValidatePracticeResponse:
        """
        Validate a practice answer.
        
        Args:
            course_id: UUID of the course
            lesson_id: UUID of the lesson
            practice_id: UUID of the practice
            request: ValidatePracticeRequest with user_id and answer
            
        Returns:
            ValidatePracticeResponse: Validation result with feedback
            
        Raises:
            HTTPException: If course, lesson, practice or user not found
        """
        try:
            # Get user
            user = await User.get_or_none(id=request.user_id)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            
            # Get course, lesson and practice
            course = await Course.get_or_none(id=course_id)
            if not course:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Course not found"
                )
            
            lesson = await Lesson.get_or_none(id=lesson_id)
            if not lesson:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Lesson not found"
                )
            
            practice = await ContentBlock.get_or_none(
                id=practice_id,
                type="practice",
                lesson=lesson
            )
            if not practice:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Practice not found"
                )
            
            # Validate answer using regex if provided
            is_correct = False
            feedback = None
            
            if practice.validation_regex:
                is_correct = bool(re.match(practice.validation_regex, request.answer))
                feedback = "Correct!" if is_correct else "Incorrect. Please try again."
            
            # Save attempt
            await UserPracticeAttempt.create(
                user=user,
                practice=practice,
                answer=request.answer,
                is_correct=is_correct,
                feedback=feedback
            )
            
            # Update progress if correct
            if is_correct:
                progress = await UserProgress.get_or_none(user=user, course=course)
                if progress and practice_id not in progress.completed_practices:
                    progress.completed_practices.append(practice_id)
                    await progress.save()
            
            return ValidatePracticeResponse(
                success=True,
                message="Practice validated successfully",
                is_correct=is_correct,
                feedback=feedback
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error validating practice: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"An error occurred while validating practice: {str(e)}"
            )

    async def get_course_progress(
        self,
        course_id: UUID,
        user_id: UUID
    ) -> CourseProgress:
        """
        Get user's progress in a course.
        
        Args:
            course_id: UUID of the course
            user_id: UUID of the user
            
        Returns:
            CourseProgress: User's progress in the course
            
        Raises:
            HTTPException: If course or user not found
        """
        try:
            # Get user
            user = await User.get_or_none(id=user_id)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            
            # Get course
            course = await Course.get_or_none(id=course_id)
            if not course:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Course not found"
                )
            
            # Get progress
            progress = await UserProgress.get_or_none(user=user, course=course)
            if not progress:
                # Create new progress record
                progress = await UserProgress.create(
                    user=user,
                    course=course,
                    completed_lessons=[],
                    completed_practices=[],
                    progress=0.0
                )
            
            return CourseProgress(
                completed_lessons=progress.completed_lessons,
                completed_practices=progress.completed_practices,
                progress=progress.progress,
                last_accessed_lesson=progress.last_accessed_lesson.id if progress.last_accessed_lesson else None
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting course progress: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"An error occurred while getting course progress: {str(e)}"
            ) 