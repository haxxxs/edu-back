from typing import List, Optional
from fastapi import HTTPException, status
from app.models.course import Course, CourseModule, Lesson, CourseLevel
from app.schemas.course import CourseCreate, CourseResponse
import logging
import traceback
from uuid import UUID

logger = logging.getLogger(__name__)

class CourseService:
    async def get_all_courses(self) -> List[CourseResponse]:
        """
        Get all available courses with their modules and lessons.
        
        Returns:
            List[CourseResponse]: List of all courses with their relationships
        """
        try:
            # Fetch all courses with their relationships
            courses = await Course.all().prefetch_related('modules', 'modules__lessons')
            
            # Convert to response models
            return [
                CourseResponse.model_validate({
                    "id": course.id,
                    "title": course.title,
                    "description": course.description,
                    "fullDescription": course.full_description,
                    "level": course.level,
                    "duration": course.duration,
                    "imageUrl": course.image_url,
                    "cover_image": course.cover_image,
                    "is_active": course.is_active,
                    "created_at": course.created_at,
                    "updated_at": course.updated_at,
                    "modules": [
                        {
                            "id": module.id,
                            "title": module.title,
                            "lessons_count": module.lessons_count,
                            "created_at": module.created_at,
                            "updated_at": module.updated_at,
                            "lessons": [
                                {
                                    "id": lesson.id,
                                    "title": lesson.title,
                                    "type": lesson.type,
                                    "content": lesson.content,
                                    "created_at": lesson.created_at,
                                    "updated_at": lesson.updated_at
                                }
                                for lesson in module.lessons
                            ]
                        }
                        for module in course.modules
                    ]
                })
                for course in courses
            ]
        except Exception as e:
            logger.error(f"Error fetching courses: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"An error occurred while fetching courses: {str(e)}"
            )

    async def create_course(self, course_data: CourseCreate) -> CourseResponse:
        """
        Create a new course with modules and lessons.
        
        Args:
            course_data: CourseCreate - Data for creating a new course
            
        Returns:
            CourseResponse - Created course with all its relationships
            
        Raises:
            HTTPException: If course creation fails
        """
        try:
            # Log incoming data
            logger.info(f"Creating course with data: {course_data.model_dump()}")
            logger.info(f"Number of modules to create: {len(course_data.modules)}")

            # Validate course title uniqueness
            existing_course = await Course.filter(title=course_data.title).first()
            if existing_course:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="A course with this title already exists"
                )

            # Create course
            try:
                course = await Course.create(
                    title=course_data.title,
                    description=course_data.description,
                    full_description=course_data.fullDescription,
                    level=course_data.level,
                    duration=course_data.duration,
                    image_url=str(course_data.imageUrl) if course_data.imageUrl else None,
                    cover_image=course_data.cover_image,
                    is_active=course_data.is_active
                )
                logger.info(f"Created course with ID: {course.id}")

            except Exception as e:
                logger.error(f"Error creating course: {str(e)}")
                logger.error(f"Traceback: {traceback.format_exc()}")
                raise

            # Create modules and lessons
            try:
                for module_data in course_data.modules:
                    logger.info(f"Creating module with title: {module_data.title}")
                    logger.info(f"Number of lessons in module: {len(module_data.lessons)}")
                    
                    # Create module
                    module = await CourseModule.create(
                        title=module_data.title,
                        lessons_count=len(module_data.lessons),
                        course=course  # Pass the course object directly
                    )
                    logger.info(f"Created module with ID: {module.id}")

                    for lesson_data in module_data.lessons:
                        logger.info(f"Creating lesson with title: {lesson_data.title}")
                        lesson = await Lesson.create(
                            title=lesson_data.title,
                            type=lesson_data.type,
                            content=lesson_data.content,
                            module=module  # Pass the module object directly
                        )
                        logger.info(f"Created lesson with ID: {lesson.id} in module {module.id}")
            except Exception as e:
                logger.error(f"Error creating modules/lessons: {str(e)}")
                logger.error(f"Traceback: {traceback.format_exc()}")
                raise

            # Fetch the complete course with relationships
            try:
                course = await Course.get(id=course.id).prefetch_related('modules', 'modules__lessons')
                logger.info(f"Successfully fetched course with relationships: {course.id}")
                logger.info(f"Number of modules fetched: {len(course.modules)}")
                
                # Convert to dictionary with proper structure
                course_dict = {
                    "id": course.id,
                    "title": course.title,
                    "description": course.description,
                    "fullDescription": course.full_description,
                    "level": course.level,
                    "duration": course.duration,
                    "imageUrl": course.image_url,
                    "cover_image": course.cover_image,
                    "is_active": course.is_active,
                    "created_at": course.created_at,
                    "updated_at": course.updated_at,
                    "modules": [
                        {
                            "id": module.id,
                            "title": module.title,
                            "lessons_count": module.lessons_count,
                            "created_at": module.created_at,
                            "updated_at": module.updated_at,
                            "lessons": [
                                {
                                    "id": lesson.id,
                                    "title": lesson.title,
                                    "type": lesson.type,
                                    "content": lesson.content,
                                    "created_at": lesson.created_at,
                                    "updated_at": lesson.updated_at
                                }
                                for lesson in module.lessons
                            ]
                        }
                        for module in course.modules
                    ]
                }
                
                # Convert to Pydantic model
                return CourseResponse.model_validate(course_dict)
            except Exception as e:
                logger.error(f"Error fetching course with relationships: {str(e)}")
                logger.error(f"Traceback: {traceback.format_exc()}")
                raise

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Unexpected error in create_course: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"An error occurred while creating the course: {str(e)}"
            ) 