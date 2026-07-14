from django.shortcuts import get_object_or_404

from rest_framework.exceptions import (
    PermissionDenied,
    ValidationError,
)

from apps.organizations.models import (
    Organization,
    OrganizationMember,
)


def get_current_organization(request):
    """
    Returns the current organization selected by the user.

    The frontend must send:

        X-Organization-ID: <organization_uuid>

    The user must either:
        - own the organization
        - or be an active member of it.
    """

    if not request.user.is_authenticated:
        raise PermissionDenied(
            "Authentication required."
        )

    organization_id = request.headers.get(
        "X-Organization-ID",
    )

    if not organization_id:
        raise ValidationError(
            {
                "organization": (
                    "X-Organization-ID header is required."
                )
            }
        )

    organization = get_object_or_404(
        Organization,
        id=organization_id,
        is_active=True,
    )

    is_owner = (
        organization.owner_id == request.user.id
    )

    is_member = OrganizationMember.objects.filter(
        organization=organization,
        user=request.user,
        is_active=True,
    ).exists()

    if not (is_owner or is_member):
        raise PermissionDenied(
            "You do not have access to this organization."
        )

    return organization