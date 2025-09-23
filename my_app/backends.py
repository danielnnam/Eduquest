from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()


class InactiveUserBackend(ModelBackend):
    def user_can_authenticate(self, user):
        # Allow even inactive users to authenticate (override default)
        return True


