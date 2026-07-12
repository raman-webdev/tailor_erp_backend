from rest_framework import serializers

from .models import Organization, Branch, Role, OrganizationMember

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


class BranchSerializer(serializers.ModelSerializer):

    class Meta:
        model = Branch

        read_only_fields = (
            "id",
            "code",
            "created_at",
            "updated_at",
            "is_active",
        )

        fields = "__all__"

    def validate_name(self, value):
        organization = self.initial_data.get("organization")

        queryset = Branch.objects.filter(
            organization_id=organization,
            name__iexact=value,
            is_active=True,
        )

        if self.instance:
            queryset = queryset.exclude(
                pk=self.instance.pk,
            )

        if queryset.exists():
            raise serializers.ValidationError(
                "Branch with this name already exists in this organization."
            )

        return value
    

class RoleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Role
        exclude = (
            "id",
            "organization",
            "created_at",
            "updated_at",
            "is_active",
        )


class OrganizationMemberSerializer(
    serializers.ModelSerializer
):

    class Meta:
        model = OrganizationMember

        exclude = (
            "id",
            "organization",
            "created_at",
            "updated_at",
            "is_active",
        )