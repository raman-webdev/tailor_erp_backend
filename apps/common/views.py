from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema
from .models import Permission
from .serializers import PermissionSerializer
from rest_framework.permissions import IsAuthenticated

from .services.location_service import LocationService


@extend_schema(tags=["Locations"])
class ProvinceListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response(
            LocationService.get_provinces()
        )


@extend_schema(tags=["Locations"])
class DistrictListView(APIView):
    permission_classes = [AllowAny]

    def get(
        self,
        request,
        province_id,
    ):
        return Response(
            LocationService.get_districts(
                province_id
            )
        )


@extend_schema(tags=["Locations"])
class LocalLevelListView(APIView):
    permission_classes = [AllowAny]

    def get(
        self,
        request,
        province_id,
        district_id,
    ):
        return Response(
            LocationService.get_local_levels(
                province_id,
                district_id,
            )
        )
    

@extend_schema(tags=["Permissions"])
class PermissionListView(APIView):

    permission_classes = [
        IsAuthenticated,
    ]

    @extend_schema(
        responses=PermissionSerializer(
            many=True,
        ),
    )
    def get(
        self,
        request,
    ):
        permissions = (
            Permission.objects.filter(
                is_active=True,
            )
            .order_by(
                "module",
                "name",
            )
        )

        serializer = PermissionSerializer(
            permissions,
            many=True,
        )

        return Response(
            {
                "count": permissions.count(),
                "results": serializer.data,
            },
            status=status.HTTP_200_OK,
        )