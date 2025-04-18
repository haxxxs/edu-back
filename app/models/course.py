from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_model_creator

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

    # Relationship defined in CourseModule model
    modules: fields.ReverseRelation["models.CourseModule"]

    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        table = "courses"
        ordering = ["id"]

# Pydantic models can be created from Tortoise models, but we'll define them separately
# in app/schemas/ for better control and adherence to API specs. 