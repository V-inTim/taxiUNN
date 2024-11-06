from django.core.mail import send_mail
from django.core.cache import cache
import random


def send_verification_code(email: str, verification_code: str):
    """ Отправляет на email сообщение с code."""

    send_mail(
        'TaxiUNN Verification Code',
        f'Your verification code is {verification_code}',
        'taxi.unn@mail.ru',
        [email],
        fail_silently=False,
    )


def make_verification_code():
    """ Создает verification code."""

    return random.randint(10000, 99999)


class PasswordRecoveryCache:
    """ Кеш для методов восстановления пароля."""

    @staticmethod
    def save(email, code):
        """ Сохранение в кеш."""
        cache.set(f'verification_code_{email}', code, timeout=3600)

    @staticmethod
    def verify(email, code):
        """ Сранение хранимого и переданного значений."""
        stored_code = cache.get(f'verification_code_{email}')
        if str(code) == str(stored_code):
            cache.set(f'password_recovery_{email}', True, timeout=300)
        return str(code) == str(stored_code)

    @staticmethod
    def check(email):
        """ Проверка разрешения на изменение пароля."""
        permission = cache.get(f'password_recovery_{email}')
        return bool(permission)
