from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import Admin


class AdminJWTAuthentication(JWTAuthentication):
    """Переопределение jwt аутентификации под Admin."""

    def __init__(self, *args, **kwargs) -> None:
        """Переопределение __init__."""
        super().__init__(*args, **kwargs)
        self.user_model = Admin
