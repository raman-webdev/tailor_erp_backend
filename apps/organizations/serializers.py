from rest_framework import serializers
from ..accounts.models import User
from .models import Organization, Branch, Role, OrganizationMember
from .services import OrganizationMemberService

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
    serializers.ModelSerializer,
):

    first_name = serializers.CharField(
        max_length=100,
        required=True,
    )

    last_name = serializers.CharField(
        max_length=100,
        required=True,
    )

    email = serializers.EmailField(
        required=True,
    )

    phone = serializers.CharField(
        max_length=20,
        required=True,
    )

    role = serializers.PrimaryKeyRelatedField(
        queryset=Role.objects.none(),
    )

    branch = serializers.PrimaryKeyRelatedField(
        queryset=Branch.objects.none(),
        allow_null=True,
        required=False,
    )

    class Meta:
        model = OrganizationMember

        exclude = (
            "organization",
            "user",
        )

        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
            "is_active",
        )

    def __init__(
        self,
        *args,
        **kwargs,
    ):
        super().__init__(
            *args,
            **kwargs,
        )

        organization = self.context.get(
            "organization",
        )

        if organization:
            self.fields["role"].queryset = (
                Role.objects.filter(
                    organization=organization,
                    is_active=True,
                )
            )

            self.fields["branch"].queryset = (
                Branch.objects.filter(
                    organization=organization,
                    is_active=True,
                )
            )

    def validate_email(
        self,
        value,
    ):
        queryset = User.objects.filter(
            email=value,
        )

        if self.instance:
            queryset = queryset.exclude(
                pk=self.instance.user.pk,
            )

        if queryset.exists():
            raise serializers.ValidationError(
                "A user with this email already exists."
            )

        return value

    def create(
        self,
        validated_data,
    ):
        organization = self.context[
            "organization"
        ]

        return (
            OrganizationMemberService.create_member(
                organization=organization,
                validated_data=validated_data,
            )
        )

    def update(
        self,
        instance,
        validated_data,
    ):
        return (
            OrganizationMemberService.update_member(
                member=instance,
                validated_data=validated_data,
            )
        )

    def to_representation(
        self,
        instance,
    ):
        return {
            "id": str(instance.id),
            "first_name": instance.user.first_name,
            "last_name": instance.user.last_name,
            "email": instance.user.email,
            "phone": instance.user.phone,
            "role": {
                "id": str(instance.role.id),
                "name": instance.role.name,
            },
            "branch": (
                {
                    "id": str(instance.branch.id),
                    "name": instance.branch.name,
                }
                if instance.branch
                else None
            ),
            "is_active": instance.is_active,
            "created_at": instance.created_at,
            "updated_at": instance.updated_at,
        }