from django.db import models
import uuid

# Create your models here.

class BaseModel(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(
    auto_now_add=True
    )

    updated_at = models.DateTimeField(
    auto_now=True
    )


    class Meta:
        abstract = True


class Permission(BaseModel):

    module = models.CharField(
        max_length=100,
    )

    name = models.CharField(
        max_length=150,
    )

    code = models.CharField(
        max_length=150,
        unique=True,
    )

    description = models.TextField(
        blank=True,
    )

    class Meta:
        db_table = "permissions"

        ordering = [
            "module",
            "name",
        ]

        indexes = [
            models.Index(
                fields=[
                    "module",
                ]
            ),
            models.Index(
                fields=[
                    "code",
                ]
            ),
        ]

    def __str__(self):
        return self.code
