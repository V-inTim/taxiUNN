from django.contrib.auth.backends import BaseBackend

from .models import Admin


class AdminBackend(BaseBackend):
    """Используется для управления процессом аутентификации администраторов."""

    def authenticate(self, request, email: str = None, password: str = None):
        """Аутентификация."""
        try:
            user = Admin.objects.get(email=email)
        except Admin.DoesNotExist:
            return None

        if user.check_password(password):
            return user
        return None

    def get_user(self, user_id):
        """Получение пользователя."""
        try:
            return Admin.objects.get(pk=user_id)
        except Admin.DoesNotExist:
            return None
