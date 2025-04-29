from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_model_creator
from datetime import datetime
from enum import Enum

class CourseStatus(str, Enum):
    COMPLETED = "completed"
    IN_PROGRESS = "in_progress"

class Course(models.Model):
    """
    Database model for Educational Courses.
    """
    id = fields.IntField(pk=True)
    title = fields.CharField(max_length=255)
    description = fields.TextField()
    level = fields.CharField(max_length=50)  # E.g., "Beginner", "Intermediate", "Advanced"
    duration = fields.CharField(max_length=50) # E.g., "8 weeks"
    image_url = fields.CharField(max_length=512, null=True)
    full_description = fields.TextField(null=True)
    cover_image = fields.CharField(max_length=500, null=True)
    is_active = fields.BooleanField(default=True)

    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        table = "courses"
        ordering = ["id"]

# Pydantic models can be created from Tortoise models, but we'll define them separately
# in app/schemas/ for better control and adherence to API specs. 

class Module(models.Model):
    """Module model for courses"""
    id = fields.IntField(pk=True)
    course = fields.ForeignKeyField('models.Course', related_name='course_modules')
    title = fields.CharField(max_length=200)
    description = fields.TextField(null=True)
    order = fields.IntField(default=0)
    is_required = fields.BooleanField(default=True)
    
    class Meta:
        table = "modules"
    
    def __str__(self):
        return self.title

class UserCourse(models.Model):
    """Model for tracking user progress in courses"""
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField('models.User', related_name='user_courses')
    course = fields.ForeignKeyField('models.Course', related_name='user_courses')
    progress = fields.IntField(default=0)  # 0-100
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
    id = fields.IntField(pk=True)
    user_course = fields.OneToOneField('models.UserCourse', related_name='certificate')
    issued_at = fields.DatetimeField(auto_now_add=True)
    certificate_url = fields.CharField(max_length=500, null=True)
    
    class Meta:
        table = "certificates"
    
    def __str__(self):
        return f"Certificate for {self.user_course}" 