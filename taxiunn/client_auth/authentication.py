from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import BasePermission

from .models import Client


class ClientJWTAuthentication(JWTAuthentication):
    """Переопределение jwt аутентификации под Client."""

    def __init__(self, *args, **kwargs) -> None:
        """Переопределение __init__."""
        super().__init__(*args, **kwargs)
        self.user_model = Client


class IsAuthenticatedClient(BasePermission):
    """Проверяем, авторизован ли администратор."""

    def has_permission(self, request, view):
        """Проверяем, авторизован ли администратор."""
        if not request.user.is_authenticated:
            return False

        return (
            isinstance(request.user, Client) and request.user.is_authenticated
        )
