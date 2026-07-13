from django.db import transaction

from apps.accounts.models import User
from apps.accounts.services import (
    EmailService,
)
from apps.accounts.services import (
    EmailVerificationService,
)

from .models import OrganizationMember


class OrganizationMemberService:

    @staticmethod
    @transaction.atomic
    def create_member(
        organization,
        validated_data,
    ):
        """
        Creates a new organization member.

        Workflow
        --------
        1. Create User
        2. Create OrganizationMember
        3. Generate verification token
        4. Send invitation email
        """

        user = User.objects.create(
            username=validated_data["email"],
            email=validated_data["email"],
            phone=validated_data["phone"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            is_active=False,
        )

        user.set_unusable_password()

        user.save(
            update_fields=[
                "password",
            ]
        )

        member = OrganizationMember.objects.create(
            organization=organization,
            user=user,
            role=validated_data["role"],
            branch=validated_data["branch"],
        )

        verification = (
            EmailVerificationService.create_token(
                user
            )
        )

        EmailService.send_verification_email(
            user=user,
            token=verification.token,
        )

        return member