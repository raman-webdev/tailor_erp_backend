from uuid import uuid4
import os


def profile_picture_upload_path(instance, filename):
    ext = filename.split(".")[-1]
    filename = f"{uuid4}.{ext}"
    return os.path.join(
        "users",
        "profile_pictures",
        str(instance.id),
        filename,
    )