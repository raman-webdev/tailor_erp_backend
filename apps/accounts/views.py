from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema
from rest_framework.parsers import MultiPartParser, FormParser

from .serializers import (
    RegisterSerializer, LoginSerializer, LogoutSerializer, 
    UserProfileSerializer, UpdateProfileSerializer, ChangePasswordSerializer, 
    ForgotPasswordSerializer, ResetPasswordSerializer, VerifyEmailSerializer,
    ResendVerificationEmailSerializer
)
from .services import PasswordResetService, EmailService, EmailVerificationService

User = get_user_model()


@extend_schema(
    request=RegisterSerializer,
)
class UserRegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()

        verification = EmailVerificationService.create_token(user)

        EmailService.send_verification_email(
            user=user,
            token=verification.token,
        )

        return Response(
            {
                "message": (
                    "Registration successful. "
                    "Please check your email to verify your account."
                ),
                "user_id": str(user.id),
            },
            status=status.HTTP_201_CREATED,
        )
    

@extend_schema(
    request=LoginSerializer,
)
class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        identifier = serializer.validated_data["identifier"]
        password = serializer.validated_data["password"]

        user = authenticate(
            request=request,
            username=identifier,
            password=password,
        )

        if user is None:
            return Response(
                {"detail": "Invalid credentials."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        
        if not user.is_verified:
            return Response(
                {
                    "detail": "Please verify your email first."
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": {
                    "id": str(user.id),
                    "username": user.username,
                    "email": user.email,
                    "full_name": user.full_name,
                },
            },
            status=status.HTTP_200_OK,
        )
    

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            token = RefreshToken(serializer.validated_data["refresh"])
            token.blacklist()
        except Exception:
            return Response(
                {"detail": "Invalid refresh token."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {"message": "Logged out successfully."},
            status=status.HTTP_200_OK,
        )
    


@extend_schema(
    # request=UserProfileSerializer,
    request=UpdateProfileSerializer,
)
class MeView(APIView):
    permission_classes = [IsAuthenticated]

    parser_classes = [
        MultiPartParser,
        FormParser,
    ]

    def get(self, request):
        serializer = UserProfileSerializer(request.user)

        return Response(serializer.data)
    

    def patch(self, request):
        old_picture = request.user.profile_picture

        serializer = UpdateProfileSerializer(
            request.user,
            data=request.data,
            partial=True,
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        if (
            old_picture
            and "profile_picture" in request.FILES
            and old_picture.name != request.user.profile_picture.nam
            ):
            old_picture.delete(save=False)

        return Response(
            {
                "message": "Profile updated successfully.",
                "user": UserProfileSerializer(request.user).data,
            },
            status=status.HTTP_200_OK,
        )


@extend_schema(
    request=ChangePasswordSerializer,
)
class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user

        if not user.check_password(
            serializer.validated_data["old_password"]
        ):
            return Response(
                {
                    "old_password": [
                        "Old password is incorrect."
                    ]
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(
            serializer.validated_data["new_password"]
        )

        user.save(update_fields=["password"])

        return Response(
            {
                "message": "Password changed successfully."
            },
            status=status.HTTP_200_OK,
        )
    
@extend_schema(
    request=ForgotPasswordSerializer,
)
class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]

        user = User.objects.filter(email__iexact=email).first()

        if user:
            token = PasswordResetService.create_token(user)

            EmailService.send_password_reset_email(
              user=user,
              token=token.token,
            )


        return Response(
            {
                "message": (
                    "If an account exists with this email, "
                    "a password reset link has been sent."
                )
            },
            status=status.HTTP_200_OK,
        )
    

class ResetPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ResetPasswordSerializer(
            data=request.data
        )
        serializer.is_valid(raise_exception=True)

        reset_token = PasswordResetService.validate_token(
            serializer.validated_data["token"]
        )

        if reset_token is None:
            return Response(
                {
                    "detail": "Invalid or expired token."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = reset_token.user

        user.set_password(
            serializer.validated_data["new_password"]
        )

        user.save(update_fields=["password"])

        reset_token.is_used = True
        reset_token.save(update_fields=["is_used"])

        return Response(
            {
                "message": "Password has been reset successfully."
            },
            status=status.HTTP_200_OK,
        )
    

class VerifyEmailView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = VerifyEmailSerializer(
            data=request.data,
        )

        serializer.is_valid(raise_exception=True)

        verification = EmailVerificationService.validate_token(
            serializer.validated_data["token"]
        )

        if verification is None:
            return Response(
                {
                    "detail": "Invalid or expired token."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = verification.user

        user.is_verified = True
        user.save(update_fields=["is_verified"])

        verification.is_used = True
        verification.save(update_fields=["is_used"])

        return Response(
            {
                "message": "Email verified successfully."
            },
            status=status.HTTP_200_OK,
        )
    
class ResendVerificationEmailView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ResendVerificationEmailSerializer(
            data=request.data
        )

        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]

        user = User.objects.filter(
            email=email
        ).first()

        if user is None:
            return Response(
                {
                    "message": (
                        "If an account exists with this email, "
                        "a verification email has been sent."
                    )
                },
                status=status.HTTP_200_OK,
            )

        if user.is_verified:
            return Response(
                {
                    "message": "Email is already verified."
                },
                status=status.HTTP_200_OK,
            )

        verification = EmailVerificationService.create_token(
            user
        )

        EmailService.send_verification_email(
            user=user,
            token=verification.token,
        )

        return Response(
            {
                "message": (
                    "Verification email has been sent."
                )
            },
            status=status.HTTP_200_OK,
        )