from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()


class UserEmailAuthentication(ModelBackend):
    def authenticate(self, request, **kwargs):
        email = kwargs['email']
        password = kwargs['password']

        try:
            get_user = User.objects.get(email__iexact=email)
            if get_user.check_password(password) is True:
                return get_user
        except User.DoesNotExist:
            pass
