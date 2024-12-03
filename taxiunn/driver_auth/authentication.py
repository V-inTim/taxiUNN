from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import Driver


class DriverJWTAuthentication(JWTAuthentication):
    """Переопределение JWT аутентификации для Driver."""

    def __init__(self, *args, **kwargs) -> None:
        """Переопределение инициализации JWTAuth для Driver."""
        super().__init__(*args, **kwargs)
        self.user_model = Driver
