from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import BasePermission

from .models import Admin


class AdminJWTAuthentication(JWTAuthentication):
    """Переопределение jwt аутентификации под Admin."""

    def __init__(self, *args, **kwargs) -> None:
        """Переопределение __init__."""
        super().__init__(*args, **kwargs)
        self.user_model = Admin


class IsAuthenticatedAdmin(BasePermission):
    """Проверяем, авторизован ли администратор."""

    def has_permission(self, request, view):
        """Проверяем, авторизован ли администратор."""
        if not request.user.is_authenticated:
            return False

        return isinstance(request.user, Admin)
