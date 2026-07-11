from django.contrib import admin
from django.urls import path
from .views import OrganizationCreateView


urlpatterns = [
    path("create/", OrganizationCreateView.as_view(), name="organization-create"),
]