from django.db import models
from ..common.models import BaseModel
import os
import uuid
from django.conf import settings

# Create your models here.

def organization_logo_upload_path(
    instance,
    filename,
):
    """
    media/organizations_logo/logos/organizations/<organization_id>/logo/<uuid>.<extension>
    """

    extension = os.path.splitext(filename)[1]

    return (
        f"organizations_logo/"
        f"logos/"
        f"organizations/"
        f"{instance.id}/"
        f"logo/"
        f"{uuid.uuid4()}{extension}"
    )


def branch_logo_upload_path(
    instance,
    filename,
):
    """
    media/organizations_logo/logos/branches/<branch_id>/logo/<uuid>.<extension>
    """

    extension = os.path.splitext(filename)[1]

    return (
        f"organizations_logo/"
        f"logos/"
        f"branches/"
        f"{instance.id}/"
        f"logo/"
        f"{uuid.uuid4()}{extension}"
    )


class Organization(BaseModel):

    owner = models.ForeignKey(
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
    




class BranchType(models.TextChoices):
    HEADQUARTERS = (
        "HEADQUARTERS",
        "Headquarters",
    )

    REGIONAL = (
        "REGIONAL",
        "Regional Office",
    )

    SITE = (
        "SITE",
        "Site Office",
    )

    WAREHOUSE = (
        "WAREHOUSE",
        "Warehouse",
    )


class Branch(BaseModel):
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="branches",
    )

    name = models.CharField(
        max_length=255,
    )

    code = models.CharField(
        max_length=20,
        unique=True,
        editable=False,
    )

    branch_type = models.CharField(
        max_length=20,
        choices=BranchType.choices,
        default=BranchType.REGIONAL,
    )

    email = models.EmailField(
        blank=True,
    )

    phone = models.CharField(
        max_length=20,
        blank=True,
    )

    logo = models.ImageField(
        upload_to=branch_logo_upload_path,
        blank=True,
        null=True,
    )

    province = models.CharField(
        max_length=100,
    )

    district = models.CharField(
        max_length=100,
    )

    local_level = models.CharField(
        max_length=150,
    )

    local_level_type = models.CharField(
        max_length=50,
    )

    ward = models.PositiveSmallIntegerField()

    postal_code = models.CharField(
        max_length=20,
        blank=True,
    )

    street = models.CharField(
        max_length=255,
        blank=True,
    )

    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="managed_branches",
    )

    remarks = models.TextField(
        blank=True,
    )

    class Meta:
        db_table = "branches"

        ordering = [
            "name",
        ]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "organization",
                    "name",
                ],
                name="unique_branch_name_per_organization",
            )
        ]

        indexes = [
            models.Index(
                fields=[
                    "organization",
                ]
            ),
            models.Index(
                fields=[
                    "code",
                ]
            ),
            models.Index(
                fields=[
                    "branch_type",
                ]
            ),
            models.Index(
                fields=[
                    "is_active",
                ]
            ),
        ]

    def __str__(self):
        return (
            f"{self.organization.name}"
            f" - "
            f"{self.name}"
        )



