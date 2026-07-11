from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import OrganizationSerializer

import re

from .models import Organization


def generate_organization_code(name):
    """
    Example:
    Himalayan Life Insurance Pvt. Ltd.
    -> HLI-0001
    """

    ignored_words = {
        "PVT",
        "PRIVATE",
        "LIMITED",
        "LTD",
        "COMPANY",
        "CO",
        "THE",
        "AND",
    }

    words = re.findall(r"[A-Za-z]+", name)

    initials = ""

    for word in words:
        upper = word.upper()

        if upper not in ignored_words:
            initials += upper[0]

    initials = initials[:5]

    count = (
        Organization.objects.filter(
            code__startswith=initials
        ).count()
        + 1
    )

    return f"{initials}-{count:04d}"



@extend_schema(tags=["Organizations"])
class OrganizationListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses=OrganizationSerializer(many=True),
    )
    def get(self, request):
        organizations = (
            Organization.objects
            .filter(owner=request.user)
            .order_by("name")
        )

        serializer = OrganizationSerializer(
            organizations,
            many=True,
        )

        return Response(
            {
                "count": organizations.count(),
                "results": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        request=OrganizationSerializer,
        responses=OrganizationSerializer,
    )
    def post(self, request):
        serializer = OrganizationSerializer(
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)

        organization = serializer.save(
            owner=request.user,
            code=generate_organization_code(
                serializer.validated_data["name"],
            ),
        )

        return Response(
            {
                "message": "Organization created successfully.",
                "organization": OrganizationSerializer(
                    organization
                ).data,
            },
            status=status.HTTP_201_CREATED,
        )