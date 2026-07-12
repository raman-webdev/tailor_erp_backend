from rest_framework.exceptions import PermissionDenied

from apps.organizations.models import Organization


def get_current_organization(request):
    """
    Returns the organization of the authenticated user.

    Later this function can be extended to support
    organization switching using headers, JWT claims,
    or subdomains without changing the views.
    """

    if not request.user.is_authenticated:
        raise PermissionDenied(
            "Authentication required."
        )

    try:
        return Organization.objects.get(
            owner=request.user,
            is_active=True,
        )

    except Organization.DoesNotExist:
        raise PermissionDenied(
            "No organization found."
        )