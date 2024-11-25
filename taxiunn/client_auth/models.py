from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.db import models


class ClientManager(BaseUserManager):
    """Специфика Django.

    Django требует, чтобы кастомные пользователи определяли свой собственный
    класс Manager.
    """

    def create_user(self, email: str, password: str, full_name: str):
        """Создает и возвращает клиента с имэйлом, паролем."""
        if email is None:
            raise TypeError('Clients must have an email address.')

        if password is None:
            raise TypeError('Clients must have a password.')
        
        if full_name is None:
            raise TypeError('Clients must have a full name.')

        user = self.model(
            email=self.normalize_email(email),
            full_name=full_name,
        )
        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, email: str, password: str, full_name: str):
        """Создает и возвращает клиента с привилегиями суперадмина."""
        user = self.create_user(email, password, full_name)
        user.make_superuser()
        user.save()

        return user


class Client(AbstractBaseUser):
    """Класс клиента."""

    email = models.EmailField(db_index=True, unique=True)
    full_name = models.CharField(null=True, default=None)

    is_active = models.BooleanField(default=True)
    # определяет, кто может войти в административную часть нашего сайта.
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    # Временная метка создания объекта.
    created_at = models.DateTimeField(auto_now_add=True)
    # Временная метка показывающая время последнего обновления объекта.
    updated_at = models.DateTimeField(auto_now=True)

    bank_balance = models.IntegerField(default=1000)

    # USERNAME_FIELD - поле, которое используется для входа в систему.
    USERNAME_FIELD = 'email'

    # класс UserManager должен управлять объектами этого типа.
    objects = ClientManager()

    def __str__(self):
        """Строковое представление модели."""
        return self.email

    def make_superuser(self):
        """Создание суперпользователя."""
        self.is_staff = True
        self.is_superuser = True

    def get_data(self):
        """Выводит набор допустимых данных."""
        return {
            'email': self.email,
            'full_name': self.full_name,
            'bank_balance': self.bank_balance,
        }
