from rest_framework.permissions import BasePermission

from apps.common.services.org_service import (
    get_current_organization,
)

from apps.common.services.permission_services import (
    PermissionService,
)
from apps.organizations.models import (
    OrganizationMember,
)


class HasOrganizationPermission(
    BasePermission,
):
    """
    Checks whether the authenticated user has the
    required permission for the current request.
    """

    message = (
        "You do not have permission to perform this action."
    )

    def has_permission(
        self,
        request,
        view,
    ):
        if not request.user.is_authenticated:
            return False

        organization = get_current_organization(
            request,
        )

        permission_map = getattr(
            view,
            "permission_map",
            {},
        )

        required_permission = permission_map.get(
            request.method,
        )

        # If no permission is defined, allow access.
        if not required_permission:
            return True

        return PermissionService.user_has_permission(
            user=request.user,
            organization=organization,
            permission_code=required_permission,
            )