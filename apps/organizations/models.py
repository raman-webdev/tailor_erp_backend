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






