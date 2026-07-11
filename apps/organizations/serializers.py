from rest_framework import serializers

from .models import Organization


class OrganizationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Organization
        exclude = (
            "id",
            "created_at",
            "updated_at",
            "is_active",
            "owner",
        )