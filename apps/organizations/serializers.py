from rest_framework import serializers

from .models import Organization

class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = "__all__"
        read_only_fields = (
            "id",
            "owner",
            "code",
            "created_at",
            "updated_at",
            "is_active",
        )