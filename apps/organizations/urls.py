from django.contrib import admin
from django.urls import path
from .views import OrganizationListCreateView


urlpatterns = [
    path("", OrganizationListCreateView.as_view(), name="organization-create"),
]