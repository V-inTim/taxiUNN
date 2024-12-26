from django.core.mail import send_mail


def send_password(email: str, password: str):
    """Отправляет пользователю пароль на почту."""
    send_mail(
        'TaxiUNN Admin Registration',
        f'You are registered as Admin.\n Your password: {password}',
        'taxi.unn@mail.ru',
        [email],
        fail_silently=False,
    )
