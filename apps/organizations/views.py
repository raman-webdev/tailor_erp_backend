from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import OrganizationSerializer



@extend_schema(
    request=OrganizationSerializer,
    tags=["Organizations"],
)
class OrganizationCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = OrganizationSerializer(
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)

        organization = serializer.save(
            owner=request.user,
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