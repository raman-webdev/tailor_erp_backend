from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404

from .models import Role, OrganizationMember
from .serializers import OrganizationSerializer, BranchSerializer, RoleSerializer, OrganizationMemberSerializer
from apps.common.services.org_service import get_current_organization
from apps.common.permissions import HasOrganizationPermission

import re

from .models import Organization, Branch


IGNORED_WORDS = {
    "PVT",
    "PRIVATE",
    "LIMITED",
    "LTD",
    "COMPANY",
    "CO",
    "THE",
    "AND",
}


def generate_entity_code(
    model,
    name,
):
    words = re.findall(
        r"[A-Za-z]+",
        name,
    )

    initials = "".join(
        word[0].upper()
        for word in words
        if word.upper() not in IGNORED_WORDS
    )[:5]

    if not initials:
        initials = "GEN"

    last = (
        model.objects
        .filter(code__startswith=initials)
        .order_by("-code")
        .first()
    )

    if last:
        last_number = int(last.code.split("-")[1])
    else:
        last_number = 0

    return f"{initials}-{last_number + 1:04d}"



@extend_schema(tags=["Organizations"])
class OrganizationListCreateView(APIView):

    permission_classes = [
        IsAuthenticated,
    ]

    @extend_schema(
        responses=OrganizationSerializer(many=True),
    )
    def get(self, request):

        organizations = (
            Organization.objects
            .filter(
                owner=request.user,
                is_active=True,
            )
            .select_related(
                "owner",
            )
            .order_by(
                "name",
            )
        )

        serializer = OrganizationSerializer(
            organizations,
            many=True,
        )

        return Response(
            {
                "count": organizations.count(),
                "results": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        request=OrganizationSerializer,
        responses=OrganizationSerializer,
    )
    def post(self, request):

        serializer = OrganizationSerializer(
            data=request.data,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        with transaction.atomic():

            code = generate_entity_code(
                Organization,
                serializer.validated_data["name"],
            )

            organization = serializer.save(
                owner=request.user,
                code=code,
            )

        return Response(
            {
                "message": "Organization created successfully.",
                "organization": OrganizationSerializer(
                    organization
                ).data,
            },
            status=status.HTTP_201_CREATED,
        )
    

@extend_schema(tags=["Organizations"])
class OrganizationDetailView(APIView):

    permission_classes = [
        IsAuthenticated,
    ]

    def get_object(
        self,
        request,
        pk,
    ):
        return get_object_or_404(
            Organization.objects.select_related(
                "owner",
            ),
            pk=pk,
            owner=request.user,
            is_active=True,
        )

    @extend_schema(
        responses=OrganizationSerializer,
    )
    def get(
        self,
        request,
        pk,
    ):
        organization = self.get_object(
            request,
            pk,
        )

        serializer = OrganizationSerializer(
            organization,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        request=OrganizationSerializer,
        responses=OrganizationSerializer,
    )
    def patch(
        self,
        request,
        pk,
    ):
        organization = self.get_object(
            request,
            pk,
        )

        serializer = OrganizationSerializer(
            organization,
            data=request.data,
            partial=True,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        serializer.save()

        return Response(
            {
                "message": (
                    "Organization updated successfully."
                ),
                "organization": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        responses=None,
    )
    def delete(
        self,
        request,
        pk,
    ):
        organization = self.get_object(
            request,
            pk,
        )

        organization.is_active = False

        organization.save(
            update_fields=[
                "is_active",
            ],
        )

        return Response(
            {
                "message": (
                    "Organization deleted successfully."
                ),
            },
            status=status.HTTP_204_NO_CONTENT,
        )
    

@extend_schema(
    tags=["Branches"],
)
class BranchListCreateView(APIView):

    permission_classes = [
        IsAuthenticated,
        HasOrganizationPermission,
        ]
    
    permission_map = {
        "GET" : "branch.view",
        "POST" : "branch.create",
    }

    @extend_schema(
        responses=BranchSerializer(many=True),
    )
    def get(self, request):

        organization = get_current_organization(
            request
        )

        queryset = (
            Branch.objects
            .filter(
                organization=organization,
                is_active=True,
            )
            .select_related(
                "organization",
                "manager",
            )
        )

        search = request.query_params.get(
            "search",
        )

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search)
                | Q(code__icontains=search)
                | Q(email__icontains=search)
                | Q(phone__icontains=search)
            )

        queryset = queryset.order_by(
            "-created_at",
        )

        serializer = BranchSerializer(
            queryset,
            many=True,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        request=BranchSerializer,
        responses=BranchSerializer,
    )
    def post(self, request):

        organization = get_current_organization(
            request
        )

        serializer = BranchSerializer(
            data=request.data,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        with transaction.atomic():

            code = generate_entity_code(
                Branch,
                serializer.validated_data["name"],
            )

            branch = serializer.save(
                organization=organization,
                code=code,
            )

        return Response(
            {
                "message": "Branch created successfully.",
                "branch": BranchSerializer(
                    branch
                ).data,
            },
            status=status.HTTP_201_CREATED,
        )
    

@extend_schema(
    tags=["Branches"],
)
class BranchDetailView(APIView):

    permission_classes = [
        IsAuthenticated,
        HasOrganizationPermission,
    ]

    permission_maps = {
        "GET" : "branch.view",
        "PATCH": "branch.update",
        "DELETE" : "branch.delete",
    }

    def get_object(
        self,
        request,
        pk,
    ):
        organization = get_current_organization(
            request,
        )

        return get_object_or_404(
            Branch.objects.select_related(
                "organization",
                "manager",
            ),
            pk=pk,
            organization=organization,
            is_active=True,
        )

    @extend_schema(
        responses=BranchSerializer,
    )
    def get(
        self,
        request,
        pk,
    ):
        branch = self.get_object(
            request,
            pk,
        )

        serializer = BranchSerializer(
            branch,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        request=BranchSerializer,
        responses=BranchSerializer,
    )
    def patch(
        self,
        request,
        pk,
    ):
        branch = self.get_object(
            request,
            pk,
        )

        serializer = BranchSerializer(
            branch,
            data=request.data,
            partial=True,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        serializer.save()

        return Response(
            {
                "message": "Branch updated successfully.",
                "branch": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        responses=None,
    )
    def delete(
        self,
        request,
        pk,
    ):
        branch = self.get_object(
            request,
            pk,
        )

        branch.is_active = False
        branch.save(
            update_fields=[
                "is_active",
            ],
        )

        return Response(
            {
                "message": "Branch deleted successfully.",
            },
            status=status.HTTP_204_NO_CONTENT,
        )
    

class RoleListCreateView(APIView):

    permission_classes = [
        IsAuthenticated,
        HasOrganizationPermission,
    ]

    permission_map = {
        "GET": "role.view",
        "POST": "role.create",
    }

    @extend_schema(
        responses=RoleSerializer(many=True),
        tags=["Roles"],
    )
    def get(self, request):

        organization = get_current_organization(
            request
        )

        roles = (
    Role.objects
    .filter(
        organization=organization,
        is_active=True,
    )
    .select_related(
        "organization",
    )
    .prefetch_related(
        "permissions",
    )
    .order_by("name")
)

        serializer = RoleSerializer(
            roles,
            many=True,
        )

        return Response(serializer.data)

    @extend_schema(
        request=RoleSerializer,
        responses=RoleSerializer,
        tags=["Roles"],
    )
    def post(self, request):

        organization = get_current_organization(
            request
        )

        serializer = RoleSerializer(
            data=request.data,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        role = serializer.save(
            organization=organization,
        )

        return Response(
            {
                "message": "Role created successfully.",
                "role": RoleSerializer(role).data,
            },
            status=status.HTTP_201_CREATED,
        )
    

class RoleDetailView(APIView):

    permission_classes = [
        IsAuthenticated,
        HasOrganizationPermission,
    ]

    permission_map = {
        "GET": "role.view",
        "PATCH": "role.update",
        "DELETE": "role.delete",
    }

    def get_object(
        self,
        request,
        pk,
    ):
        organization = get_current_organization(
            request
        )

        return get_object_or_404(
    Role.objects.select_related(
        "organization",
    ).prefetch_related(
        "permissions",
    ),
    pk=pk,
    organization=organization,
    is_active=True,
)

    @extend_schema(
        responses=RoleSerializer,
        tags=["Roles"],
    )
    def get(
        self,
        request,
        pk,
    ):
        role = self.get_object(
            request,
            pk,
        )

        serializer = RoleSerializer(
            role,
        )

        return Response(
            serializer.data,
        )

    @extend_schema(
        request=RoleSerializer,
        responses=RoleSerializer,
        tags=["Roles"],
    )
    def patch(
        self,
        request,
        pk,
    ):
        role = self.get_object(
            request,
            pk,
        )

        serializer = RoleSerializer(
            role,
            data=request.data,
            partial=True,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        serializer.save()

        return Response(
            {
                "message": "Role updated successfully.",
                "role": serializer.data,
            }
        )

    @extend_schema(
        tags=["Roles"],
    )
    def delete(
        self,
        request,
        pk,
    ):
        role = self.get_object(
            request,
            pk,
        )

        role.is_active = False
        role.save(
            update_fields=[
                "is_active",
            ]
        )

        return Response(
            {
                "message": "Role deleted successfully.",
            },
            status=status.HTTP_204_NO_CONTENT,
        )
    

class OrganizationMemberListCreateView(
    APIView
):

    permission_classes = [
        IsAuthenticated,
        HasOrganizationPermission,
    ]

    permission_map = {
        "GET": "member.view",
        "POST": "member.create",
    }

    def post(self, request):

        organization = (
            get_current_organization(
                request
            )
        )

        serializer = (
            OrganizationMemberSerializer(
                data=request.data,
                context={
                    "organization": organization,
                },
            )
        )

        serializer.is_valid(
            raise_exception=True,
        )

        member = serializer.save()

        return Response(
            {
                "message": (
                    "Organization member created successfully. "
                    "Invitation email sent."
                ),
            },
            status=status.HTTP_201_CREATED,
        )
    

@extend_schema(tags=["Organization Members"])
class OrganizationMemberDetailView(APIView):

    permission_classes = [
        IsAuthenticated,
        HasOrganizationPermission,
    ]

    permission_map = {
        "GET": "branch.view",
        "POST": "branch.create",
    }

    def get_object(
        self,
        request,
        pk,
    ):
        organization = get_current_organization(
            request,
        )

        return get_object_or_404(
            OrganizationMember.objects.select_related(
                "organization",
                "user",
                "role",
                "branch",
            ),
            pk=pk,
            organization=organization,
            is_active=True,
        )

    @extend_schema(
        responses=OrganizationMemberSerializer,
    )
    def get(
        self,
        request,
        pk,
    ):
        member = self.get_object(
            request,
            pk,
        )

        serializer = OrganizationMemberSerializer(
            member,
            context={
                "organization": member.organization,
            },
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        request=OrganizationMemberSerializer,
        responses=OrganizationMemberSerializer,
    )
    def patch(
        self,
        request,
        pk,
    ):
        member = self.get_object(
            request,
            pk,
        )

        serializer = OrganizationMemberSerializer(
            member,
            data=request.data,
            partial=True,
            context={
                "organization": member.organization,
            },
        )

        serializer.is_valid(
            raise_exception=True,
        )

        member = serializer.save()

        return Response(
            {
                "message": (
                    "Organization member updated successfully."
                ),
                "member": OrganizationMemberSerializer(
                    member,
                    context={
                        "organization": member.organization,
                    },
                ).data,
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        responses=None,
    )
    def delete(
        self,
        request,
        pk,
    ):
        member = self.get_object(
            request,
            pk,
        )

        member.is_active = False

        member.save(
            update_fields=[
                "is_active",
            ],
        )

        return Response(
            {
                "message": (
                    "Organization member deleted successfully."
                ),
            },
            status=status.HTTP_204_NO_CONTENT,
        )