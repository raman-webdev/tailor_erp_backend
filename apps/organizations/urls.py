from django.contrib import admin
from django.urls import path
from .views import (
    OrganizationListCreateView,
    OrganizationDetailView,
    BranchListCreateView,
    BranchDetailView,
    RoleListCreateView,
    RoleDetailView,
)


urlpatterns = [
    path("", OrganizationListCreateView.as_view(), name="organization-create"),
    path("organizations/<uuid:pk>/", OrganizationDetailView.as_view(), name="organization-detail"),
    path("branches/", BranchListCreateView.as_view(), name="branches"),
    path("organizations/<uuid:pk>/", OrganizationDetailView.as_view(), name="organization-detail"),
    path("roles/", RoleListCreateView.as_view(), name="role-list-create"),
    path("roles/<uuid:pk>/", RoleDetailView.as_view(), name="role-detail"),
]