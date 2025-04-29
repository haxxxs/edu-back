from tortoise import fields, models
from enum import Enum
from datetime import datetime

class CourseStatus(str, Enum):
    COMPLETED = "completed"
    IN_PROGRESS = "in_progress"

class UserCourse(models.Model):
    """Связь между пользователем и курсом, отслеживание прогресса"""
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField('models.User', related_name='courses')
    course = fields.ForeignKeyField('models.Course', related_name='users')
    progress = fields.IntField(default=0)  # 0-100
    status = fields.CharEnumField(CourseStatus, default=CourseStatus.IN_PROGRESS)
    started_at = fields.DatetimeField(auto_now_add=True)
    last_accessed_at = fields.DatetimeField(auto_now=True)
    completed_at = fields.DatetimeField(null=True)
    certificate_id = fields.CharField(max_length=100, null=True)

    class Meta:
        table = "user_courses"
        unique_together = [("user_id", "course_id")]

    def __str__(self):
        return f"UserCourse {self.id}"

class Certificate(models.Model):
    """Сертификат о прохождении курса"""
    id = fields.IntField(pk=True)
    user_course = fields.OneToOneField('models.UserCourse', related_name='certificate')
    issued_at = fields.DatetimeField(auto_now_add=True)
    certificate_url = fields.CharField(max_length=500, null=True)
    
    class Meta:
        table = "certificates"
    
    def __str__(self):
        return f"Certificate {self.id}" 