from apps.organizations.models import (
    OrganizationMember,
)


class PermissionService:

    @staticmethod
    def user_has_permission(
        user,
        organization,
        permission_code,
    ):
        try:
            member = (
                OrganizationMember.objects
                .select_related(
                    "role",
                )
                .prefetch_related(
                    "role__permissions",
                )
                .get(
                    user=user,
                    organization=organization,
                    is_active=True,
                )
            )

        except OrganizationMember.DoesNotExist:
            return False

        return (
            member.role.permissions.filter(
                code=permission_code,
                is_active=True,
            ).exists()
        )