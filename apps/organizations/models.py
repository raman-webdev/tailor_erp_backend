from django.db import models
from ..common.models import BaseModel
import os
import uuid

# Create your models here.

def organization_logo_upload_path(instance, filename):
    """
    Upload path:
    media/organizations_logo/logos/<organization_id>/logo/<uuid>.<extension>
    """

    extension = os.path.splitext(filename)[1]

    return (
        f"organizations_logo/"
        f"logos/"
        f"{instance.id}/"
        f"logo/"
        f"{uuid.uuid4()}{extension}"
    )


class Organization(BaseModel):

    owner = models.OneToOneField(
        "accounts.User",
        on_delete=models.PROTECT,
        related_name="owned_organization",
    )

    name = models.CharField(max_length=255)

    code = models.CharField(
        max_length=30,
        unique=True,
    )

    email = models.EmailField(unique=True)

    phone = models.CharField(
        max_length=20,
        blank=True,
    )

    logo = models.ImageField(
        upload_to=organization_logo_upload_path,
        blank=True,
        null=True,
    )

    pan_number = models.CharField(
        max_length=20,
        blank=True,
    )

    registration_number = models.CharField(
        max_length=100,
        blank=True,
    )

    province = models.CharField(
    max_length=100
    )

    district = models.CharField(
    max_length=100
    )
    
    local_level = models.CharField(
    max_length=150
    )

    local_level_type = models.CharField(
    max_length=30
    )

    ward = models.PositiveSmallIntegerField()

    postal_code = models.CharField(
    max_length=10
    )

    street = models.CharField(
    max_length=255,
    blank=True
    )

    class Meta:
        db_table = "organizations"

    def __str__(self):
        return self.name
