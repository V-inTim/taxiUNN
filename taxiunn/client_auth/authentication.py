from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import Client


class ClientJWTAuthentication(JWTAuthentication):
    """Переопределение jwt аутентификации под Client."""

    def __init__(self, *args, **kwargs) -> None:
        """Переопределение __init__."""
        super().__init__(*args, **kwargs)
        self.user_model = Client
