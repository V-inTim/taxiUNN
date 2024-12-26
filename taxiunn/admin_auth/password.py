import string
import secrets

PASSWORD_SIZE = 16


def make_password():
    """Создать пароль."""
    alphabet = string.ascii_letters + string.digits
    password = ''.join(secrets.choice(alphabet) for i in range(PASSWORD_SIZE))
    return password
