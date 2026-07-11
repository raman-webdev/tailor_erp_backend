from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db import transaction

from .serializers import OrganizationSerializer

import re

from .models import Organization, Branch


IGNORED_WORDS = {
    "PVT",
    "PRIVATE",
    "LIMITED",
    "LTD",
    "COMPANY",
    "CO",
    "THE",
    "AND",
}


def generate_entity_code(
    model,
    name,
):
    words = re.findall(
        r"[A-Za-z]+",
        name,
    )

    initials = "".join(
        word[0].upper()
        for word in words
        if word.upper() not in IGNORED_WORDS
    )[:5]

    if not initials:
        initials = "GEN"

    last = (
        model.objects
        .filter(code__startswith=initials)
        .order_by("-code")
        .first()
    )

    if last:
        last_number = int(last.code.split("-")[1])
    else:
        last_number = 0

    return f"{initials}-{last_number + 1:04d}"



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

        with transaction.atomic():
            code = generate_entity_code(
                Organization,
                serializer.validated_data["name"],
            )

            organization = serializer.save(
                owner=request.user,
                code=code,
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