from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema

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