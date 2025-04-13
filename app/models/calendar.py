from tortoise import fields, models
from datetime import datetime

class CalendarNote(models.Model):
    """Calendar note model for educational platform"""
    id = fields.IntField(pk=True)
    title = fields.CharField(max_length=200)
    description = fields.TextField(null=True)
    date = fields.DatetimeField()
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    color = fields.CharField(max_length=20, null=True)  # For UI customization
    is_important = fields.BooleanField(default=False)
    
    # Optional foreign key to user (commented out for now)
    # user = fields.ForeignKeyField('models.User', related_name='calendar_notes', null=True)

    class Meta:
        table = "calendar_notes"

    def __str__(self):
        return self.title 