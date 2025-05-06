from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_model_creator
from enum import Enum
from uuid import UUID

class ContentBlockType(str, Enum):
    HEADING = "heading"
    PARAGRAPH = "paragraph"
    CODE = "code"
    VIDEO = "video"
    IMAGE = "image"
    PRACTICE = "practice"

class ContentBlock(models.Model):
    id = fields.UUIDField(pk=True)
    type = fields.CharEnumField(ContentBlockType)
    lesson = fields.ForeignKeyField('models.Lesson', related_name='content_blocks')
    
    # Heading fields
    level = fields.IntField(null=True)
    text = fields.TextField(null=True)
    
    # Code fields
    language = fields.CharField(max_length=50, null=True)
    code = fields.TextField(null=True)
    
    # Video fields
    video_id = fields.CharField(max_length=100, null=True)
    
    # Image fields
    src = fields.CharField(max_length=255, null=True)
    alt = fields.CharField(max_length=255, null=True)
    
    # Practice fields
    practice_id = fields.UUIDField(null=True)
    description = fields.TextField(null=True)
    task_type = fields.CharField(max_length=50, null=True)
    validation_regex = fields.CharField(max_length=255, null=True)
    placeholder = fields.CharField(max_length=255, null=True)
    
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "content_blocks"

class UserProgress(models.Model):
    id = fields.UUIDField(pk=True)
    user = fields.ForeignKeyField('models.User', related_name='course_progress')
    course = fields.ForeignKeyField('models.Course', related_name='user_progress')
    completed_lessons = fields.JSONField(default=list)  # List of lesson IDs
    completed_practices = fields.JSONField(default=list)  # List of practice IDs
    progress = fields.FloatField(default=0.0)  # Progress percentage
    last_accessed_lesson = fields.ForeignKeyField('models.Lesson', null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "user_progress"
        unique_together = (("user", "course"),)

class UserPracticeAttempt(models.Model):
    id = fields.UUIDField(pk=True)
    user = fields.ForeignKeyField('models.User', related_name='practice_attempts')
    practice = fields.ForeignKeyField('models.ContentBlock', related_name='attempts')
    answer = fields.TextField()
    is_correct = fields.BooleanField()
    feedback = fields.TextField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "user_practice_attempts" 