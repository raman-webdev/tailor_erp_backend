from django.urls import path

from .views import UserRegistrationView, LoginView, LogoutView, MeView, ChangePasswordView, ForgotPasswordView, ResetPasswordView, VerifyEmailView, ResendVerificationEmailView
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView
)

urlpatterns = [
    path("register/", UserRegistrationView.as_view(), name="user_register"),
    path("login/", LoginView.as_view(), name="user_login"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("logout/", LogoutView.as_view(), name="user_logout"),
    path("me/", MeView.as_view(), name="user_profile"),
    path("change-password", ChangePasswordView.as_view(), name="change_password"),
    path("forgot-password/", ForgotPasswordView.as_view(), name="forgot_password"),
    path("password-reset/", ResetPasswordView.as_view(), name="password_reset"),
    path("verify-email/", VerifyEmailView.as_view(), name="verify_email"),
    path("resend-verification-email/", ResendVerificationEmailView.as_view(), name="resend_verification_email"),
]