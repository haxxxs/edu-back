from tortoise import fields, models
from enum import Enum

class EventType(str, Enum):
    CONFERENCE = "conference"
    WORKSHOP = "workshop"
    WEBINAR = "webinar"
    MEETUP = "meetup"

class Event(models.Model):
    """Event model for educational events"""
    id = fields.IntField(pk=True)
    title = fields.CharField(max_length=200)
    description = fields.TextField(null=True)
    start_date = fields.DatetimeField()
    end_date = fields.DatetimeField()
    location = fields.CharField(max_length=300, null=True)
    max_participants = fields.IntField(null=True)
    current_participants = fields.IntField(default=0)
    type = fields.CharEnumField(EventType, default=EventType.CONFERENCE)
    price = fields.DecimalField(max_digits=10, decimal_places=2, null=True)
    image_url = fields.CharField(max_length=500, null=True)
    is_online = fields.BooleanField(default=False)

    class Meta:
        table = "events"

    def __str__(self):
        return self.title
