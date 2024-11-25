from typing import Optional
from django.contrib.auth.backends import BaseBackend

from admin_auth.models import Admin


class AdminBackend(BaseBackend):
    """Используется для управления процессом аутентификации администраторов."""

    def authenticate(self, email: str, password: str) -> Optional(Admin):
        """Аутентификация."""
        try:
            user = Admin.objects.get(email=email)
        except Admin.DoesNotExist:
            return None

        if user.check_password(password):
            return user
        return None

    def get_user(self, user_id) -> Optional(Admin):
        """Получение пользователя."""
        try:
            return Admin.objects.get(pk=user_id)
        except Admin.DoesNotExist:
            return None
