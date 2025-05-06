from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_model_creator
from datetime import datetime
from enum import Enum
from typing import List, Optional

class CourseStatus(str, Enum):
    COMPLETED = "completed"
    IN_PROGRESS = "in_progress"

class CourseLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

class LessonType(str, Enum):
    THEORY = "theory"
    PRACTICE = "practice"
    VIDEO = "video"

class Course(models.Model):
    """
    Database model for Educational Courses.
    """
    id = fields.UUIDField(pk=True)
    title = fields.CharField(max_length=255, unique=True)
    description = fields.CharField(max_length=500)
    full_description = fields.TextField()
    level = fields.CharEnumField(CourseLevel)
    duration = fields.CharField(max_length=50) # E.g., "8 weeks"
    image_url = fields.CharField(max_length=500, null=True)
    cover_image = fields.CharField(max_length=500, null=True)
    is_active = fields.BooleanField(default=True)

    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    # Relationships
    modules: fields.ReverseRelation["CourseModule"]

    def __str__(self):
        return self.title

    class Meta:
        table = "courses"
        ordering = ["id"]

class CourseModule(models.Model):
    """Module model for courses"""
    id = fields.UUIDField(pk=True)
    title = fields.CharField(max_length=255)
    lessons_count = fields.IntField(default=0)
    course = fields.ForeignKeyField('models.Course', related_name='modules', on_delete=fields.CASCADE)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    
    # Relationships
    lessons: fields.ReverseRelation["Lesson"]

    def __str__(self):
        return self.title

    class Meta:
        table = "course_modules"
        ordering = ["id"]

class Lesson(models.Model):
    """Lesson model for modules"""
    id = fields.UUIDField(pk=True)
    title = fields.CharField(max_length=255)
    type = fields.CharEnumField(LessonType)
    content = fields.TextField()
    module = fields.ForeignKeyField('models.CourseModule', related_name='lessons', on_delete=fields.CASCADE)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        table = "lessons"
        ordering = ["id"]

class UserCourse(models.Model):
    """Model for tracking user progress in courses"""
    id = fields.UUIDField(pk=True)
    user = fields.ForeignKeyField('models.User', related_name='user_courses')
    course = fields.ForeignKeyField('models.Course', related_name='user_courses')
    progress = fields.FloatField(default=0.0)
    status = fields.CharEnumField(CourseStatus, default=CourseStatus.IN_PROGRESS)
    started_at = fields.DatetimeField(auto_now_add=True)
    last_accessed_at = fields.DatetimeField(auto_now=True)
    completed_at = fields.DatetimeField(null=True)
    certificate_id = fields.CharField(max_length=100, null=True)
    
    class Meta:
        table = "user_courses"
        unique_together = ("user", "course")
    
    def __str__(self):
        return f"{self.user.username} - {self.course.title}"

class Certificate(models.Model):
    """Certificate model for completed courses"""
    id = fields.UUIDField(pk=True)
    user_course = fields.OneToOneField('models.UserCourse', related_name='certificate')
    issued_at = fields.DatetimeField(auto_now_add=True)
    certificate_url = fields.CharField(max_length=500, null=True)
    
    class Meta:
        table = "certificates"
    
    def __str__(self):
        return f"Certificate for {self.user_course}" 