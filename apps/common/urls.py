from django.urls import path

from .views import (
    ProvinceListView,
    DistrictListView,
    LocalLevelListView,
)

urlpatterns = [
    path(
        "provinces/",
        ProvinceListView.as_view(),
        name="province-list",
    ),

    path(
        "provinces/<int:province_id>/districts/",
        DistrictListView.as_view(),
        name="district-list",
    ),

    path(
        "provinces/<int:province_id>/districts/<int:district_id>/local-levels/",
        LocalLevelListView.as_view(),
        name="local-level-list",
    ),
]