from tortoise import fields, models
from enum import Enum

class UserRole(str, Enum):
    STUDENT = "student"
    TEACHER = "teacher"
    ADMIN = "admin"

class User(models.Model):
    """User model for the educational platform"""
    id = fields.IntField(pk=True)
    email = fields.CharField(max_length=255, unique=True)
    hashed_password = fields.CharField(max_length=255)
    name = fields.CharField(max_length=100, null=True) # Name to be used in profile
    role = fields.CharEnumField(UserRole, default=UserRole.STUDENT)
    avatar_url = fields.CharField(max_length=512, null=True)
    about = fields.TextField(null=True)
    location = fields.CharField(max_length=100, null=True)
    is_active = fields.BooleanField(default=True) # Keep for enabling/disabling users
    is_admin = fields.BooleanField(default=False)
    telegram_id = fields.CharField(max_length=255, null=True, unique=True) # New field for Telegram ID
    created_at = fields.DatetimeField(auto_now_add=True)
    # Add updated_at for tracking profile updates
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "users"
        ordering = ["id"]

    def __str__(self):
        return self.email # Use email for string representation now
