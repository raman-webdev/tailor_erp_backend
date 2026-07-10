from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q

User = get_user_model()


class EmailUsernamePhoneBackend(ModelBackend):
    """
    Authenticate using email, username, or phone.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        identifier = username

        if identifier is None:
            identifier = kwargs.get("identifier")

        if not identifier or not password:
            return None

        try:
            user = User.objects.get(
                Q(email__iexact=identifier)
                | Q(username__iexact=identifier)
                | Q(phone=identifier)
            )
        except User.DoesNotExist:
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user

        return None
    

