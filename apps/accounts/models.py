from django.db import models
from django.contrib.auth.models import AbstractUser
from .utils import profile_picture_upload_path
import uuid
from ..common.models import BaseModel
from django.contrib.auth.base_user import BaseUserManager
from django.utils import timezone
from datetime import timedelta

# Create your models here.


class UserManager(BaseUserManager):

    def create_user(self, username, email, password=None, **extra_fields):
        """
        Create and return a regular user.
        """

        if not email:
            raise ValueError("Email is required.")

        email = self.normalize_email(email)

        user = self.model(
            username=username,
            email=email,
            **extra_fields,
        )

        user.set_password(password)

        user.save(using=self._db)

        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        """
        Create and return a superuser.
        """

        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_verified", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(
            username=username,
            email=email,
            password=password,
            **extra_fields,
        )


class User(BaseModel, AbstractUser):

    email = models.EmailField(unique=True)


    phone = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
        null=True
    )

    profile_picture = models.ImageField(
        upload_to=profile_picture_upload_path,
        blank=True,
        null=True,
    )

    is_verified = models.BooleanField(
        default=False
    )


    objects = UserManager()

    class Meta:
        ordering = ['-created_at']


    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
    

    def __str__(self):
        return self.username


class PasswordResetToken(BaseModel):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="password_reset_tokens",
    )

    token = models.CharField(
        max_length=255,
        unique=True,
    )

    expires_at = models.DateTimeField()

    is_used = models.BooleanField(
        default=False,
    )

    def __str__(self):
        return f"{self.user.email}"


class EmailVerificationToken(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="email_verification_tokens",
    )

    token = models.CharField(max_length=255, unique=True)

    expires_at = models.DateTimeField()
    is_used = models.BooleanField(
        default=False,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.user.email
    


