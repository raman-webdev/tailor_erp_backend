import secrets
from datetime import timedelta
from django.utils import timezone
from django.conf import settings
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from .models import PasswordResetToken, EmailVerificationToken


class PasswordResetService:

    @staticmethod
    def create_token(user):
        PasswordResetToken.objects.filter(
            user=user,
            is_used=False,
        ).delete()

        return PasswordResetToken.objects.create(
            user=user,
            token=secrets.token_urlsafe(64),
            expires_at=timezone.now() + timedelta(minutes=15),
        )
    

    @staticmethod
    def validate_token(token):
        try:
            reset_token = PasswordResetToken.objects.get(
                token=token,
                is_used=False,
            )
        except PasswordResetToken.DoesNotExist:
            return None

        if reset_token.expires_at < timezone.now():
            return None

        return reset_token




# class EmailService:

#     @staticmethod
#     def send_password_reset_email(user, token):
#         reset_link = (
#             f"{settings.FRONTEND_URL}"
#             f"/reset-password?token={token}"
#         )



#         context = {
#             "user": user,
#             "reset_link": reset_link,
#         }

#         html_content = render_to_string(
#             "password_reset.html",
#             context,
#         )

#         email = EmailMultiAlternatives(
#             subject="[Tailor ERP] Reset your password",
#             body="Please use an HTML-supported email client.",
#             from_email=settings.DEFAULT_FROM_EMAIL,
#             to=[user.email],
#         )

#         email.attach_alternative(html_content, "text/html")

#         email.send() 


class EmailService:

    @staticmethod
    def send_password_reset_email(user, token):
        send_mail(
            subject="[Tailor ERP] Reset your password",
            message=f"""
Hello {user.full_name},

Your password reset token is:

{token}

Use this token with the Reset Password API.
""",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )

    @staticmethod
    def send_verification_email(user, token):

        verification_link = (
            f"{settings.FRONTEND_URL}"
            f"/verify-email?token={token}"
        )

        context = {
        "user": user,
        "verification_link": verification_link,
        }


        html_content = render_to_string(
        "email_verification.html",
        context,
        )

        email = EmailMultiAlternatives(
        subject="[Tailor ERP] Verify your email",
        body="Please use an HTML-supported email client.",
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email],
        )

        email.attach_alternative(html_content, "text/html")

        email.send()

        



class EmailVerificationService:

    @staticmethod
    def create_token(user):
        EmailVerificationToken.objects.filter(
            user=user,
            is_used=False
        ).delete()

        return EmailVerificationToken.objects.create(
            user=user,
            token=secrets.token_urlsafe(64),
            expires_at=timezone.now() + timedelta(hours=24),
        )
    
    @staticmethod
    def validate_token(token):
        try:
            verification = EmailVerificationToken.objects.get(
                token=token,
                is_used=False,
            )
        except EmailVerificationToken.DoesNotExist:
            return None
        
        if verification.expires_at < timezone.now():
            return None
        
        return verification
    

    
    



