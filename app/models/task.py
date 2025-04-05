from tortoise import fields, models
from enum import Enum

class TaskStatus(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class Task(models.Model):
    """Task model for the educational platform"""
    id = fields.IntField(pk=True)
    title = fields.CharField(max_length=200)
    description = fields.TextField(null=True)
    status = fields.CharEnumField(TaskStatus, default=TaskStatus.TODO)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    due_date = fields.DatetimeField(null=True)
    
    # Optional foreign key to user (commented out for now)
    # user = fields.ForeignKeyField('models.User', related_name='tasks', null=True)

    class Meta:
        table = "tasks"

    def __str__(self):
        return self.title
