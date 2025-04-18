from tortoise import fields, models

class CourseModule(models.Model):
    """
    Database model for Modules within an Educational Course.
    """
    id = fields.IntField(pk=True)
    title = fields.CharField(max_length=255)
    lessons_count = fields.IntField(description="Number of lessons in the module")
    course: fields.ForeignKeyRelation["models.Course"] = fields.ForeignKeyField(
        "models.Course", related_name="modules", description="The course this module belongs to"
    )

    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        table = "course_modules"
        ordering = ["id"] # Or maybe order based on creation or a specific order field later 