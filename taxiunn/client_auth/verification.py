import random

from django.core.cache import cache
from django.core.mail import send_mail


def send_verification_code(email: str, verification_code: str):
    """Отправляет на email сообщение с code."""
    send_mail(
        'TaxiUNN Verification Code',
        f'Your verification code is {verification_code}',
        'taxi.unn@mail.ru',
        [email],
        fail_silently=False,
    )


def make_verification_code() -> str:
    """Создает verification code."""
    return str(random.randint(10000, 99999))


class PasswordRecoveryCache:
    """Кеш для методов восстановления пароля."""

    @staticmethod
    def save(email: str, code: str):
        """Сохранение в кеш."""
        cache.set(f'verification_code_{email}', code, timeout=3600)

    @staticmethod
    def verify(email: str, code: str):
        """Сранение хранимого и переданного значений."""
        stored_code = cache.get(f'verification_code_{email}')
        is_code_valid: bool = code == stored_code
        if is_code_valid:
            cache.set(
                key=f'password_recovery_{email}',
                value=True,
                timeout=300,
            )
        return is_code_valid

    @staticmethod
    def check(email: str):
        """Проверка разрешения на изменение пароля."""
        permission = cache.get(f'password_recovery_{email}')
        return bool(permission)
