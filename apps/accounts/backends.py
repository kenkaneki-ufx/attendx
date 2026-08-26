from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

Faculty = get_user_model()


class FacultyBackend(ModelBackend):
    """Custom authentication backend for Faculty."""

    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = Faculty.objects.get(username=username)
            if user.check_password(password):
                return user
        except Faculty.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return Faculty.objects.get(pk=user_id)
        except Faculty.DoesNotExist:
            return None
